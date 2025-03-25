# news_Insights_dashboard

## Project Overview
This project involves building a Live Business Intelligence (BI) Dashboard using Looker Studio for visualizing real-time news data fetched via the News API. The project uses Apache Airflow for managing the ETL (Extract, Transform, Load) process and schedules data updates every 6 hours. Additionally, sentiment analysis is performed on news articles using a pre-trained NLP model to classify articles as positive, negative, or neutral. The goal is to automate the data flow and create a dynamic, insightful dashboard for news analytics, while storing and querying the data in Google BigQuery.

### Key Objectives:
- Build a BI dashboard that highlights key insights from live news data, including sentiment-based metrics.
- Use News API to extract real-time news data every 6 hours.
- Perform data transformation and sentiment analysis using Apache Airflow.
- Store data in Google BigQuery for efficient querying and analysis.
- Visualize the data using Looker Studio for insightful reporting, incorporating sentiment trends.
- Showcase ETL, NLP, and business intelligence skills by creating automated data flows and interactive visualizations.

## Tech Stack
- **Cloud Platform**: Google Cloud Platform (GCP), using Google Cloud Composer (managed Apache Airflow service).
- **ETL Tool**: Apache Airflow for orchestrating the ETL pipeline.
- **News API**: For extracting live news data in JSON format.
- **Business Intelligence**: Looker Studio for creating the dashboard and data visualizations.
- **Data Storage**: Google BigQuery for storing structured, queried data.
- **Data Staging**: Google Cloud Storage (GCS) for raw or intermediate data storage, if necessary.
- **NLP Model**: Pre-trained Sentiment Analysis model (such as DistilBERT or VADER) deployed via Google Cloud AI or Google Cloud Functions for real-time predictions.

## Project Stages

### 1. Requirement Gathering and Planning
- Define the types of news data to be collected (e.g., technology, business, health, etc.).  
- Determine key metrics for visualization, including sentiment-based metrics (e.g., overall sentiment, sentiment per category).  
- Set up the schedule for data extraction (every 6 hours).  
- Define the sentiment analysis model to use (e.g., DistilBERT, VADER, or a custom model fine-tuned on news data).  

### 2. Setting Up the Environment
#### Set up Google Cloud Platform:
- Create a new project in GCP.  
- Enable Google Cloud Composer and configure the environment.  

#### Set up Looker Studio:
- Connect Looker Studio to Google BigQuery for data access.  

#### Set up NLP Model:
- Deploy the sentiment analysis model using Google Cloud AI or Google Cloud Functions.  
- Ensure the model can process news articles and return sentiment labels (positive, negative, neutral).  

### 3. ETL Pipeline Development
#### Extract:
- Use the News API to extract news data in JSON format every 6 hours.  
- Define filters like keywords, locations, and languages.  

#### Transform:
- Write Python scripts in Airflow to clean and structure the raw data.  
- Use the sentiment analysis model to process each news article and assign a sentiment label (positive, negative, neutral).  
- Extract key fields like article title, date, content, categories, and sentiment.  

#### Load:
- Load the transformed data (including sentiment labels) into Google BigQuery for querying and analysis.  

### 4. Apache Airflow Setup
- Set up Apache Airflow in Google Cloud Composer for managing the ETL pipeline.  
- Create DAGs in Airflow for task orchestration.  
- Schedule the DAG to run every 6 hours to fetch and process new data.  
- Tasks in the DAG will include:
   - Data extraction from the News API.
   - Data transformation using Python code in Airflow (including sentiment analysis).
   - Data loading into Google BigQuery.  
- Ensure that each article's sentiment is processed by the NLP model and stored in BigQuery.  

### 5. Data Visualization with Looker Studio
- Connect Looker Studio to Google BigQuery.  
- Create visualizations and dashboards in Looker Studio to display:
   - News frequency over time.
   - Popular news categories or topics.
   - Geographical distribution of news stories.
   - Sentiment distribution (positive, negative, neutral) of news articles.
   - Sentiment trends over time for various categories or topics.  
- Design interactive dashboards to explore data trends dynamically.  

### 6. Testing and Validation
- Unit test the ETL process to ensure the data is correctly extracted, transformed, and loaded.  
- End-to-End testing to validate the entire workflow from extraction to sentiment analysis and visualization.  
- Monitor Airflow logs to ensure tasks complete successfully.  
- Review Looker Studio visualizations for accuracy and performance.  
- Validate that the sentiment labels are correctly applied and displayed in the dashboard.  

### 7. Deployment and Monitoring
- Deploy the DAGs to Google Cloud Composer to automate the extraction, sentiment analysis, and transformation every 6 hours.  
- Set up Airflow monitoring to track task success and failures.  
- Ensure the Looker Studio dashboard is updated correctly after each data run, including sentiment-based visualizations.  

## Task List
1. **Requirement Gathering and Planning**
    - 👨‍💻 Define types of news data to collect (e.g., technology, business, health, etc.).
    - 👨‍💻 Identify key metrics for visualization (e.g., news frequency, sentiment).
    - 👨‍💻 Set schedule for data extraction (every 6 hours).
    - 👨‍💻 Choose sentiment analysis model (e.g., DistilBERT, VADER).

2. **Set Up the Environment**
    - 👨‍💻 Set up Google Cloud Platform (GCP) project.
    - 👨‍💻 Enable Google Cloud Composer and configure environment.
    - 👨‍💻 Set up Looker Studio and connect to Google BigQuery.
    - 👨‍💻 Set up NLP sentiment analysis model (DistilBERT or VADER) via Google Cloud AI or Google Cloud Functions.

3. **ETL Pipeline Development**
    - **Extract**:
        - 👨‍💻 Set up API call to News API to fetch real-time news data.
        - 👨‍💻 Define filters for data (e.g., keywords, locations, languages).
    - **Transform**:
        - 👨‍💻 Write Python scripts in Apache Airflow to clean and structure data.
        - 👨‍💻 Integrate sentiment analysis to classify articles as positive, negative, or neutral.
        - 👨‍💻 Extract key fields: article title, date, content, category, and sentiment.
    - **Load**:
        - 👨‍💻 Load data into Google BigQuery for querying and analysis.

4. **Apache Airflow Setup**
    - 👨‍💻 Set up Apache Airflow in Google Cloud Composer.
    - 👨‍💻 Create DAGs to manage the ETL pipeline.
    - 👨‍💻 Schedule DAG to run every 6 hours.
    - 👨‍💻 Ensure tasks are created for:
        - Data extraction from News API.
        - Sentiment analysis processing.
        - Data loading into Google BigQuery.

5. **Data Visualization with Looker Studio**
    - 👨‍💻 Connect Looker Studio to Google BigQuery.
    - 👨‍💻 Create visualizations for:
        - News frequency over time.
        - Popular news categories/topics.
        - Geographical distribution of news stories.
        - Sentiment distribution (positive, negative, neutral).
        - Sentiment trends over time.
    - 👨‍💻 Design interactive dashboards for data exploration.

6. **Testing and Validation**
    - 👨‍💻 Unit test ETL pipeline to verify data extraction, transformation, and loading.
    - 👨‍💻 Perform end-to-end testing for data flow (from API call to Looker Studio visualization).
    - 👨‍💻 Monitor Airflow logs for successful task execution.
    - 👨‍💻 Validate Looker Studio visualizations for accuracy and performance.

7. **Deployment and Monitoring**
    - 👨‍💻 Deploy DAGs to Google Cloud Composer for automated execution.
    - 👨‍💻 Set up monitoring for Airflow task success and failures.
    - 👨‍💻 Ensure Looker Studio dashboard updates correctly after each data run.
