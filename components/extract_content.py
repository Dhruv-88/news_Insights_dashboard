"""
News Data Pipeline - Extract and Transform news articles from NewsAPI

This module provides functionality to extract news articles from NewsAPI.
"""

import datetime
import os
import logging
from typing import List, Dict, Any

import pandas as pd
from newsapi import NewsApiClient
from dotenv import load_dotenv

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