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
logger = logging.getLogger(__name__)

def load_data_to_bigquery(dataframe, service_account_path=None, method='append'):
    """
    Load a pandas DataFrame to BigQuery.
    
    Parameters:
    -----------
    dataframe : pandas.DataFrame
        The DataFrame to be loaded to BigQuery
    service_account_path : str, optional
        Path to the Google Cloud service account JSON file. If None, use default credentials.
    method : str, default='append'
        What to do if the table exists. Options: 'fail', 'replace', or 'append'
        
    Returns:
    --------
    int
        Number of rows loaded to BigQuery
    """
    # Load environment variables
    load_dotenv()
    
    # Get BigQuery project, dataset, and table details from environment variables
    # Check both lowercase and uppercase versions for compatibility
    project_id = os.getenv("project_id") 
    dataset_id = os.getenv("dataset_id") 
    table_id = os.getenv("table_id") 
    
    # Log the configuration values for debugging
    logger.info(f"BigQuery Configuration - Project: {project_id}, Dataset: {dataset_id}, Table: {table_id}")
    
    if not all([project_id, dataset_id, table_id]):
        error_msg = "Missing environment variables. Make sure project_id, dataset_id, and table_id are set."
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    # Full table reference
    table_ref = f"{dataset_id}.{table_id}"
    
    # Set up credentials - handle both local and cloud environments
    credentials = None
    if service_account_path and os.path.exists(service_account_path):
        # Local environment with service account file
        logger.info(f"Using service account credentials from: {service_account_path}")
        credentials = service_account.Credentials.from_service_account_file(service_account_path)
    else:
        # Cloud environment - use default credentials
        logger.info("Service account file not found or not specified. Using default credentials.")
        # When running in GCP, default credentials will be used automatically
    
    # Check if publishedAt is in datetime format
    if 'publishedAt' in dataframe.columns and dataframe['publishedAt'].dtype == 'object':
        dataframe['publishedAt'] = pd.to_datetime(dataframe['publishedAt'])
    
    # Upload to BigQuery with error handling
    try:
        dataframe.to_gbq(
            destination_table=table_ref,
            project_id=project_id,
            if_exists=method,
            credentials=credentials  # Will be None in Cloud Function, which is correct
        )
        logger.info(f"Successfully loaded {len(dataframe)} rows to {table_ref}")
        return len(dataframe)
    except Exception as e:
        logger.error(f"Error loading data to BigQuery: {str(e)}")
        raise