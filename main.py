"""
    News Data Pipeline - Cloud Function
    
    This script coordinates the entire ETL pipeline for news data:
    1. Extract data from NewsAPI
    2. Transform and process the data
    3. Analyze sentiment of news content
    4. Load data to BigQuery
    
    Adapted to run as a Google Cloud Function.
"""

import os
import logging
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import functions_framework

# Import components
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

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Configure logging for cloud environment (avoid file handlers in Cloud Functions)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

@functions_framework.http
def news_etl_pipeline(request):
    """
    HTTP Cloud Function entry point.
    
    Args:
        request (flask.Request): HTTP request object.
        
    Returns:
        Response with execution status
    """
    # Log function start
    logger.info(f"News ETL pipeline triggered at {datetime.now().isoformat()}")
    
    try:
        # Get configuration from environment variables
        service_account_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        load_method = os.environ.get("LOAD_METHOD", "append")
        
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
            service_account_path=service_account_path,
            method=load_method
        )
        logger.info(f"Successfully loaded {rows_loaded} rows to BigQuery")
        
        # Pipeline complete
        logger.info("News data pipeline completed successfully")
        
        return {"success": True, "message": f"Pipeline successfully processed {rows_loaded} articles", "timestamp": datetime.now().isoformat()}
        
    except Exception as e:
        error_message = f"Pipeline failed: {str(e)}"
        logger.error(error_message)
        
        # Return error response
        return {"success": False, "error": error_message, "timestamp": datetime.now().isoformat()}, 500