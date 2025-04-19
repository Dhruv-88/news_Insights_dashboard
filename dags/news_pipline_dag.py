"""
Apache Airflow DAG for News Data Pipeline

This DAG orchestrates the full news data pipeline to run every 12 hours.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Import pipeline components
import sys
import os
# Add project root to path - adjust based on your deployment structure
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

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
    # Get the absolute path to the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    sys.path.append(project_root)
    
    # Try again with the updated path
    from components.extract_content import extract_data
    from components.transform_content import transform_data
    from components.analyse_sentiment import analyze_sentiment
    from components.load_content import load_data_to_bigquery
    from components.logging_config import setup_logging, get_logger

# Initialize logger
setup_logging()
logger = get_logger(__name__)

# Default arguments for DAG
default_args = {
    'owner': 'Dhruv Patel',
    'depends_on_past': False,
    'email': ['dhruvrpatel3011@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'news_data_pipeline',
    default_args=default_args,
    description='ETL pipeline for news data with sentiment analysis',
    schedule_interval=timedelta(hours=12),  # Run every 12 hours
    start_date=days_ago(1),
    catchup=False,
     tags=['news', 'etl', 'sentiment', 'load'],
)

# Task functions with Airflow context
def extract_task(**context):
    """Extract news data"""
    logger.info("Starting extraction task")
    articles = extract_data()
    # Push result to XCom for next task
    context['ti'].xcom_push(key='extracted_articles', value=articles)
    return len(articles)

def transform_task(**context):
    """Transform extracted news data"""
    logger.info("Starting transformation task")
    # Pull articles from previous task
    articles = context['ti'].xcom_pull(task_ids='extract', key='extracted_articles')
    transformed_df = transform_data(articles)
    # Store DataFrame as a file for the next task
    file_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/tmp'), 'transformed_articles.pkl')
    transformed_df.to_pickle(file_path)
    return len(transformed_df)

def sentiment_task(**context):
    """Analyze sentiment of news content"""
    logger.info("Starting sentiment analysis task")
    # Load DataFrame from file
    file_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/tmp'), 'transformed_articles.pkl')
    transformed_df = pd.read_pickle(file_path)
    final_df = analyze_sentiment(transformed_df)
    # Store updated DataFrame
    file_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/tmp'), 'final_articles.pkl')
    final_df.to_pickle(file_path)
    return len(final_df)

def load_task(**context):
    """Load data to BigQuery"""
    logger.info("Starting BigQuery load task")
    # Load DataFrame from file
    file_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/tmp'), 'final_articles.pkl')
    final_df = pd.read_pickle(file_path)
    # Get service account path from Airflow connection or environment
    service_account_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', './service_account.json')
    rows_loaded = load_data_to_bigquery(
        final_df,
        service_account_path=service_account_path,
        method='append'  # Use append for incremental loads
    )
    # Clean up temporary files
    for file_name in ['transformed_articles.pkl', 'final_articles.pkl']:
        file_path = os.path.join(os.environ.get('AIRFLOW_HOME', '/tmp'), file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
    return rows_loaded

# Define tasks
extract = PythonOperator(
    task_id='extract',
    python_callable=extract_task,
    provide_context=True,
    dag=dag,
)

transform = PythonOperator(
    task_id='transform',
    python_callable=transform_task,
    provide_context=True,
    dag=dag,
)

analyze_sentiment_task = PythonOperator(
    task_id='analyze_sentiment',
    python_callable=sentiment_task,
    provide_context=True,
    dag=dag,
)

load = PythonOperator(
    task_id='load',
    python_callable=load_task,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
extract >> transform >> analyze_sentiment_task >> load