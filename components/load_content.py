"""
News Data Pipeline - Load data to BigQuery

This module provides functionality to load the processed news data
into Google BigQuery for storage and analysis.
"""

import os
import logging
import pandas as pd
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account

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


def load_data_to_bigquery(dataframe, service_account_path='./service_account.json', method='append'):
    """
    Load a pandas DataFrame to BigQuery.
    
    Parameters:
    -----------
    dataframe : pandas.DataFrame
        The DataFrame to be loaded to BigQuery
    service_account_path : str, default='./service_account.json'
        Path to the Google Cloud service account JSON file
    method : str, default='replace'
        What to do if the table exists. Options: 'fail', 'replace', or 'append'
        
    Returns:
    --------
    int
        Number of rows loaded to BigQuery
    """
    # Load environment variables
    load_dotenv()
    
    # Get BigQuery project, dataset, and table details from environment variables
    project_id = os.getenv("project_id")
    dataset_id = os.getenv("dataset_id")
    table_id = os.getenv("table_id")
    
    if not all([project_id, dataset_id, table_id]):
        raise ValueError("Missing environment variables. Make sure project_id, dataset_id, and table_id are set.")
    
    # Full table reference
    table_ref = f"{dataset_id}.{table_id}"
    
    # Set up credentials
    credentials = service_account.Credentials.from_service_account_file(service_account_path)
    
    # Check if publishedAt is in datetime format
    if 'publishedAt' in dataframe.columns and dataframe['publishedAt'].dtype == 'object':
        dataframe['publishedAt'] = pd.to_datetime(dataframe['publishedAt'])
    
    # Upload to BigQuery with error handling
    try:
        dataframe.to_gbq(
            destination_table=table_ref,
            project_id=project_id,
            if_exists=method,
            credentials=credentials
        )
        logger.info(f"Successfully loaded {len(dataframe)} rows to {table_ref}")
        return len(dataframe)
    except Exception as e:
        logger.error(f"Error loading data to BigQuery: {str(e)}")
        raise