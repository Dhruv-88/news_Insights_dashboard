# Import components

"""
    News Data Pipeline - Main Orchestration Script

    This script coordinates the entire ETL pipeline for news data:
    1. Extract data from NewsAPI
    2. Transform and process the data
    3. Analyze sentiment of news content
    4. Load data to BigQuery

    Usage:
        python main.py
"""

import os
import logging
import argparse
from dotenv import load_dotenv
import pandas as pd 
import os
import argparse
from dotenv import load_dotenv
from newsapi import NewsApiClient
# Set up logging first



try:
    # If main.py is in the root directory
    from components.extract_content import extract_data
    from components.transform_content import transform_data
    from components.analyse_sentiment import analyze_sentiment
    from components.load_content import load_data_to_bigquery
    from components.logging_config import setup_logging, get_logger
except ImportError:
    # If main.py is somewhere else
    import sys
    import os
    # Get the absolute path to the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(project_root)
    
    # Try again with the updated path
    from components.extract_content import extract_data
    from components.transform_content import transform_data
    from components.analyse_sentiment import analyze_sentiment
    from components.load_content import load_data_to_bigquery
    from components.logging_config import setup_logging, get_logger




setup_logging()  # Initialize logging system
logger = get_logger(__name__)

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


def main():
    """
    Execute the complete news data pipeline.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="News Data Pipeline")
    parser.add_argument('--service_account', type=str, default='./service_account.json',
                        help='Path to Google Cloud service account JSON file')
    parser.add_argument('--load_method', type=str, default='append', choices=['fail', 'replace', 'append'],
                        help='Method to use when loading data to BigQuery')
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Step 1: Extract data from NewsAPI
        logger.info("Step 1: Extracting news data...")
        articles = extract_data()
        logger.info(f"Extracted {len(articles)} articles")
        
        # Step 2: Transform the data
        logger.info("Step 2: Transforming news data...")
        transformed_df = transform_data(articles)
        logger.info(f"Transformed data: {len(transformed_df)} articles")
        
        # Step 3: Analyze sentiment
        logger.info("Step 3: Analyzing sentiment...")
        final_df = analyze_sentiment(transformed_df)
        logger.info("Sentiment analysis complete")
        
        # Step 4: Load data to BigQuery
        logger.info("Step 4: Loading data to BigQuery...")
        rows_loaded = load_data_to_bigquery(
            final_df,
            service_account_path=args.service_account,
            method=args.load_method
        )
        logger.info(f"Successfully loaded {rows_loaded} rows to BigQuery")
        
        # Pipeline complete
        logger.info("News data pipeline completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()