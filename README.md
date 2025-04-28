# News Insights Dashboard

## Project Overview
This project involves building a Live Business Intelligence (BI) Dashboard using Looker Studio for visualizing real-time news data fetched via the News API. The project uses Google Cloud Functions for managing the ETL (Extract, Transform, Load) process and schedules data updates every 12 hours. Additionally, sentiment analysis is performed on news articles using a pre-trained NLP model to classify articles as positive, negative, or neutral. The goal is to automate the data flow and create a dynamic, insightful dashboard for news analytics, while storing and querying the data in Google BigQuery.

Project Link : https://lookerstudio.google.com/reporting/a2b5dcc8-c710-447f-890d-68267f51d3e2 
### Key Objectives:
- Build a BI dashboard that highlights key insights from live news data, including sentiment-based metrics.
- Use News API to extract real-time news data every 12 hours.
- Perform data transformation and sentiment analysis using Google Cloud Functions.
- Store data in Google BigQuery for efficient querying and analysis.
- Visualize the data using Looker Studio for insightful reporting, incorporating sentiment trends.
- Showcase ETL, NLP, and business intelligence skills by creating automated data flows and interactive visualizations.

## Tech Stack
- **Cloud Platform**: Google Cloud Platform (GCP)
- **ETL Tool**: Google Cloud Functions for orchestrating the ETL pipeline.
- **Scheduler**: Google Cloud Scheduler for triggering ETL runs every 12 hours.
- **News API**: For extracting live news data in JSON format.
- **Business Intelligence**: Looker Studio for creating the dashboard and data visualizations.
- **Data Storage**: Google BigQuery for storing structured, queried data.
- **NLP Model**: Pre-trained Sentiment Analysis model integrated directly into the Cloud Function.

## Initial Setup

### Clone the repository:

`
git clone https://github.com/Dhruv-88/news_Insights_dashboard
`
<br />
<br />
`
cd news_insights_dashboard
`

### Create and activate the conda environment:

`
make create-env 
`
<br />
<br />
`
conda activate news_env
`

### Install dependencies using Poetry:
`
make check-poetry
`
<br />
<br />
`
make install-deps-poetry   
`
- paste the correct value in .env file , variable names should be exact qual to .env_templet.txt


## Project Stages

### 1. Requirement Gathering and Planning
- Define the types of news data to be collected (e.g., technology, business, health, etc.).  
- Determine key metrics for visualization, including sentiment-based metrics (e.g., overall sentiment, sentiment per category).  
- Set up the schedule for data extraction (every 12 hours).  
- Define the sentiment analysis model to use (e.g., TextBlob or NLTK).  

### 2. Setting Up the Environment
#### Set up Google Cloud Platform:
- Create a new project in GCP.  
- Enable Google Cloud Functions and Cloud Scheduler.  

#### Set up Looker Studio:
- Connect Looker Studio to Google BigQuery for data access.  

#### Set up NLP Model:
- Integrate the sentiment analysis model into the ETL Cloud Function.
- Ensure the model can process news articles and return sentiment labels (positive, negative, neutral).  

### 3. ETL Pipeline Development
#### Extract:
- Use the News API to extract news data in JSON format every 12 hours.  
- Define filters like keywords, locations, and languages.  

#### Transform:
- Write Python code to clean and structure the raw data.  
- Use the sentiment analysis model to process each news article and assign a sentiment label (positive, negative, neutral).  
- Extract key fields like article title, date, content, categories, and sentiment.  

#### Load:
- Load the transformed data (including sentiment labels) into Google BigQuery for querying and analysis.  

### 4. Google Cloud Functions Setup
- Develop a Cloud Function that handles the entire ETL pipeline:
  - Data extraction from the News API
  - Data transformation (including sentiment analysis)
  - Data loading into Google BigQuery
- Deploy the function to Google Cloud Functions.
- Use Cloud Scheduler to trigger the function every 12 hours.

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
- Monitor Cloud Function logs to ensure successful execution.  
- Review Looker Studio visualizations for accuracy and performance.  
- Validate that the sentiment labels are correctly applied and displayed in the dashboard.  

### 7. Deployment and Monitoring
- Deploy the ETL function to Google Cloud Functions.
- Set up Cloud Scheduler to trigger the function every 12 hours.
- Monitor Cloud Function logs for execution success and failures.
- Ensure the Looker Studio dashboard is updated correctly after each data run, including sentiment-based visualizations.  

## Task List
1. **Requirement Gathering and Planning**
    - ✅ Define types of news data to collect (e.g., technology, business, health, etc.).
    - ✅ Identify key metrics for visualization (e.g., news frequency, sentiment).
    - ✅ Set schedule for data extraction (every 12 hours).
    - ✅ Choose sentiment analysis approach (TextBlob, NLTK).

2. **Set Up the Environment**
    - ✅ Set up Google Cloud Platform (GCP) project.
    - ✅ Enable Google Cloud Functions and Cloud Scheduler.
    - ✅ Set up Looker Studio and connect to Google BigQuery.
    - ✅ Set up sentiment analysis functionality within the ETL pipeline.

3. **ETL Pipeline Development**
    - **Extract**:
        - ✅ Set up API call to News API to fetch real-time news data.
        - ✅ Define filters for data (e.g., keywords, locations, languages).
    - **Transform**:
        - ✅ Write Python scripts to clean and structure data.
        - ✅ Integrate sentiment analysis to classify articles as positive, negative, or neutral.
        - ✅ Extract key fields: article title, date, content, category, and sentiment.
    - **Load**:
        - ✅ Load data into Google BigQuery for querying and analysis.

4. **Google Cloud Functions Setup**
    - ✅ Develop Cloud Function for the ETL pipeline.
    - ✅ Deploy function to Google Cloud Functions.
    - ✅ Set up Cloud Scheduler to trigger function every 12 hours.
    - ✅ Ensure function handles:
        - Data extraction from News API.
        - Sentiment analysis processing.
        - Data loading into Google BigQuery.

5. **Data Visualization with Looker Studio**
    - ✅ Connect Looker Studio to Google BigQuery.
    - ✅ Create visualizations for:
        - News frequency over time.
        - Popular news categories/topics.
        - Geographical distribution of news stories.
        - Sentiment distribution (positive, negative, neutral).
        - Sentiment trends over time.
    - ✅ Design interactive dashboards for data exploration.

6. **Testing and Validation**
    - ✅ Test ETL pipeline to verify data extraction, transformation, and loading.
    - ✅ Perform end-to-end testing for data flow (from API call to Looker Studio visualization).
    - ✅ Monitor Cloud Function logs for successful execution.
    - ✅ Validate Looker Studio visualizations for accuracy and performance.

7. **Deployment and Monitoring**
    - ✅ Deploy ETL function to Google Cloud Functions.
    - ✅ Set up Cloud Scheduler for 12-hour execution.
    - ✅ Ensure Looker Studio dashboard updates correctly after each data run.
