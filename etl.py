#!/usr/bin/env python3
"""
News Data Pipeline - Extract and Transform news articles from NewsAPI

This module provides functionality to extract news articles from NewsAPI,
transform the data, analyze sentiment, and prepare it for further analysis.
"""

import datetime
import os
import ast
import logging
from typing import List, Dict, Any, Optional, Union

import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
from newsapi import NewsApiClient
from bs4 import BeautifulSoup
from tqdm import tqdm
from transformers import pipeline


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


class NewsAPIError(Exception):
    """Custom exception for NewsAPI related errors."""
    pass


def extract_data() -> List[Dict[str, Any]]:
    """
    Extract news articles from NewsAPI for multiple topics and combine them.
    
    Returns:
        List[Dict[str, Any]]: Combined list of articles from different topics
        
    Raises:
        NewsAPIError: If there's an issue with the NewsAPI
        EnvironmentError: If required environment variables are missing
    """
    try:
        # Get current date and date from 7 days ago
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        logger.info(f"Current date: {current_date}")
        
        seven_days_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y-%m-%d')
        logger.info(f"7 days ago: {seven_days_ago}")
        
        # Load API key from .env file
        load_dotenv()
        news_api = os.getenv("NEWS_API")
        
        if not news_api:
            raise EnvironmentError("NEWS_API environment variable not found. Please check your .env file.")
        
        # Initialize NewsAPI client
        newsapi = NewsApiClient(news_api)
        
        # Define topics to search for
        topics = ['GenAI', 'AI', 'Technology']
        combined_articles = []
        
        # Fetch articles for each topic
        for topic in topics:
            logger.info(f"Fetching articles for topic: {topic}...")
            try:
                articles = newsapi.get_everything(
                    q=topic,
                    from_param=seven_days_ago,
                    to=current_date,
                    language='en',
                    sort_by='relevancy',
                    page=2
                )
                
                if 'articles' not in articles:
                    logger.warning(f"No articles found for topic: {topic}")
                    continue
                    
                logger.info(f"Fetched {len(articles['articles'])} articles for topic: {topic}")
                combined_articles.extend(articles['articles'])
                
            except Exception as e:
                logger.error(f"Error fetching articles for topic {topic}: {str(e)}")
                # Continue with other topics rather than failing completely
        
        if not combined_articles:
            raise NewsAPIError("No articles were fetched from any topic")
        
        # Remove duplicate articles (same URL)
        seen_urls = set()
        unique_articles = []
        
        for article in combined_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        logger.info(f"Total unique articles fetched: {len(unique_articles)}")
        return unique_articles
        
    except Exception as e:
        logger.error(f"Error in extract_data: {str(e)}")
        raise


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


def analyze_sentiment(df: pd.DataFrame, text_column: str = 'full_content') -> pd.DataFrame:
    """
    Apply sentiment analysis to the specified text column in the DataFrame.
    
    Args:
        df: DataFrame containing the text to analyze
        text_column: Column name containing the text to analyze
        
    Returns:
        pd.DataFrame: DataFrame with sentiment analysis results added
        
    Raises:
        ValueError: If the text column doesn't exist
    """
    logger.info("Initializing sentiment analysis pipeline...")
    
    if text_column not in df.columns:
        raise ValueError(f"Text column '{text_column}' not found in DataFrame")
    
    # Initialize sentiment analysis pipeline
    try:
        sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        logger.info("Sentiment analysis pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing sentiment analysis pipeline: {str(e)}")
        raise
    
    # Helper function to analyze a single text
    def analyze_single_text(text):
        if pd.isna(text) or text == "" or not isinstance(text, str):
            return {"label": "NEUTRAL", "score": 0.5}  # Default for empty content
        try:
            # DistilBERT has a max token limit, so truncate if needed
            truncated_text = text[:512]  # Simple truncation approach
            result = sentiment_pipeline(truncated_text)[0]
            return result
        except Exception as e:
            logger.warning(f"Error processing text: {str(e)}")
            return {"label": "NEUTRAL", "score": 0.5}  # Default for errors
    
    # Apply sentiment analysis in batches to avoid memory issues
    logger.info(f"Applying sentiment analysis to {len(df)} articles...")
    batch_size = 32
    results = []
    
    # Process in batches with progress bar
    for i in tqdm(range(0, len(df), batch_size)):
        batch = df[text_column].iloc[i:i+batch_size].fillna("").tolist()
        # Filter out empty strings
        valid_texts = []
        valid_indices = []
        
        for j, text in enumerate(batch):
            if isinstance(text, str) and text.strip():
                valid_texts.append(text)
                valid_indices.append(j)
        
        if valid_texts:
            try:
                batch_results = sentiment_pipeline(valid_texts)
                
                # Place results in the correct positions
                for idx, result in zip(valid_indices, batch_results):
                    while len(results) < i + idx:
                        results.append({"label": "NEUTRAL", "score": 0.5})
                    results.append(result)
            except Exception as e:
                logger.error(f"Error in batch sentiment analysis: {str(e)}")
                # Add neutral results for this batch
                results.extend([{"label": "NEUTRAL", "score": 0.5} for _ in valid_texts])
        
        # Fill in missing results for empty strings
        while len(results) < min(i + batch_size, len(df)):
            results.append({"label": "NEUTRAL", "score": 0.5})
    
    # Ensure we have exactly the right number of results
    if len(results) != len(df):
        logger.warning(f"Results length mismatch: {len(results)} vs {len(df)}. Adjusting...")
        if len(results) < len(df):
            results.extend([{"label": "NEUTRAL", "score": 0.5} for _ in range(len(df) - len(results))])
        else:
            results = results[:len(df)]
    
    # Add sentiment results to the dataframe
    df.loc[:, 'sentiment_label'] = [result['label'] for result in results]
    df.loc[:, 'sentiment_score'] = [result['score'] for result in results]
    df.loc[:, 'sentiment_value'] = df['sentiment_label'].map({'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0})
    
    logger.info("Sentiment analysis completed successfully")
    return df


def save_data(df: pd.DataFrame, filename: str = 'transformed_news_data.csv') -> None:
    """
    Save the DataFrame to a CSV file.
    
    Args:
        df: DataFrame to save
        filename: Name of the output file
        
    Returns:
        None
    """
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Data successfully saved to {filename}")
    except Exception as e:
        logger.error(f"Error saving data to {filename}: {str(e)}")


def main() -> Optional[pd.DataFrame]:
    """
    Main function to run the extract, transform, and sentiment analysis pipeline.
    
    Returns:
        Optional[pd.DataFrame]: Processed DataFrame or None if an error occurred
    """
    logger.info("Starting news extraction, transformation and sentiment analysis pipeline...")
    
    try:
        # Set pandas display options to show all content
        pd.set_option('display.max_columns', None)  # Show all columns
        pd.set_option('display.width', None)  # Auto-detect terminal width
        pd.set_option('display.max_colwidth', 100)  # Set a reasonable column width
        
        # Extract data
        articles = extract_data()
        
        # Transform data
        transformed_df = transform_data(articles)
        
        # Apply sentiment analysis
        results_df = analyze_sentiment(transformed_df)
        
        # Print top 5 rows
        logger.info("\nProcessed Data - Top 5 Rows:")
        print(results_df[['title', 'source', 'publishedAt', 'sentiment_label', 'sentiment_score']].head())
        
        # Display sentiment distribution
        sentiment_counts = results_df['sentiment_label'].value_counts()
        logger.info("\nSentiment Distribution:")
        print(sentiment_counts)
        
        # Calculate average sentiment by source
        source_sentiment = results_df.groupby('source')['sentiment_value'].agg(['mean', 'count']).sort_values(by='mean', ascending=False)
        logger.info("\nAverage Sentiment by Source (with article count):")
        print(source_sentiment)
        
        # Save to CSV
        save_data(results_df, 'news_with_sentiment.csv')
        logger.info("Pipeline completed successfully!")
        
        return results_df
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        return None


if __name__ == "__main__":
    main()