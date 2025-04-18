"""
News Data Pipeline - Transform news articles data

This module provides functionality to transform news articles data,
extract content from URLs, and prepare the data for analysis.
"""

import ast
import logging
from typing import List, Dict, Any, Union

import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("news_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def extract_source_name(source: Union[Dict[str, str], str]) -> str:
    """
    Extract the name from a source object which can be either a dictionary or string.
    
    Args:
        source: Source object from NewsAPI (can be dict or string)
        
    Returns:
        str: Extracted source name or 'Unknown' if not found
    """
    if isinstance(source, dict):
        return source.get('name', 'Unknown')
    elif isinstance(source, str):
        try:
            dict_data = ast.literal_eval(source)  # Attempt to parse it as a dictionary
            if isinstance(dict_data, dict):
                return dict_data.get('name', 'Unknown')
        except (SyntaxError, ValueError):
            # If source is a plain string, return it directly
            return source
    return 'Unknown'


def extract_content(url: str) -> str:
    """
    Extract the main content from a webpage given its URL.
    
    Args:
        url: URL of the article
        
    Returns:
        str: Extracted text content or error message
    """
    if not url or not isinstance(url, str):
        return "Error: Invalid URL"
        
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract meaningful text from paragraphs
        paragraphs = soup.find_all("p")
        content = " ".join(p.text.strip() for p in paragraphs if p.text.strip())
        
        # If no paragraphs found, try with article or div tags
        if not content:
            article_content = soup.find('article')
            if article_content:
                content = article_content.get_text(strip=True)
            else:
                # As a fallback, get text from the main part of the page
                main_content = soup.find('main') or soup.find('div', class_=['content', 'article'])
                if main_content:
                    content = main_content.get_text(strip=True)
        
        # Truncate to avoid excessively large content
        max_length = 1000
        if content:
            return content[:max_length] + ("..." if len(content) > max_length else "")
        else:
            return "No content extracted"
            
    except requests.exceptions.RequestException as e:
        return f"Request error: {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def transform_data(combined_articles: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Transform the combined articles into a cleaned and structured DataFrame.
    
    Args:
        combined_articles: List of article dictionaries from NewsAPI
        
    Returns:
        pd.DataFrame: Transformed and cleaned DataFrame
        
    Raises:
        ValueError: If the input data is invalid
    """
    logger.info("Transforming data...")
    
    if not combined_articles:
        raise ValueError("No articles provided for transformation")
    
    # Convert to DataFrame
    combined_articles_df = pd.DataFrame(combined_articles)
    
    # Check if we have the necessary columns
    required_columns = ['title', 'description', 'url', 'publishedAt']
    missing_columns = [col for col in required_columns if col not in combined_articles_df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Drop the urlToImage column if it exists
    if 'urlToImage' in combined_articles_df.columns:
        combined_articles_df = combined_articles_df.drop('urlToImage', axis=1)
    
    # Remove duplicates based on description
    final_df = combined_articles_df.drop_duplicates(subset=["description"], keep='first')
    logger.info(f"After removing duplicates: {len(final_df)} articles")
    
    # Format dates
    try:
        final_df['publishedAt'] = pd.to_datetime(final_df['publishedAt']).dt.strftime('%Y-%m-%d')
    except Exception as e:
        logger.warning(f"Error formatting dates: {str(e)}")
        # Continue without formatting if there's an error
    
    # Apply source name extraction
    final_df.loc[:, 'source'] = final_df['source'].apply(extract_source_name)
    
    # Extract full content from each article URL
    logger.info("Extracting full content from URLs (this may take a while)...")
    final_df['full_content'] = [extract_content(url) for url in tqdm(final_df['url'])]
    
    return final_df