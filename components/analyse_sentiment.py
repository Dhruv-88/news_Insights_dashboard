"""
News Data Pipeline - Sentiment Analysis

This module provides functionality to analyze sentiment of news article content
using transformers-based models.
"""

import logging
import pandas as pd
from typing import Dict, Any
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