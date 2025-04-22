#!/bin/bash
# improved-deploy.sh - Deploy News ETL Pipeline to Cloud Functions with enhanced env var handling
# Usage: ./improved-deploy.sh

# Exit on any error
set -e

# Load environment variables from .env file
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found"
  exit 1
fi

# Check for required variables
REQUIRED_VARS=("NEWS_API" "project_id" "dataset_id" "table_id" "service_account")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!var}" ]; then
    MISSING_VARS+=("$var")
  fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
  echo "Error: The following required variables are missing or empty:"
  for var in "${MISSING_VARS[@]}"; do
    echo "  - $var"
  done
  exit 1
fi

# Configuration
REGION=${REGION:-"us-central1"}
FUNCTION_NAME=${FUNCTION_NAME:-"news_etl_pipeline"}
SERVICE_ACCOUNT=${service_account}

# Log all environment variables being used for deployment
echo "Using the following configuration:"
echo "-------------------------"
echo "FUNCTION_NAME: $FUNCTION_NAME"
echo "REGION: $REGION"
echo "PROJECT_ID: $project_id"
echo "DATASET_ID: $dataset_id"
echo "TABLE_ID: $table_id"
echo "SERVICE_ACCOUNT: $SERVICE_ACCOUNT"
echo "NEWS_API: ${NEWS_API:0:5}... (masked for security)"
echo "-------------------------"

# Verify with user
read -p "Does this configuration look correct? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
  echo "Deployment cancelled by user"
  exit 0
fi

# Build environment variables string for the function
# Do NOT add quotes around values as gcloud will handle this
ENV_VARS=""
ENV_VARS+="NEWS_API=${NEWS_API},"
ENV_VARS+="project_id=${project_id},"
ENV_VARS+="dataset_id=${dataset_id},"
ENV_VARS+="table_id=${table_id}"

echo "Environment variables string: $ENV_VARS"

# Deploy the function
echo "Deploying Cloud Function..."
gcloud functions deploy "$FUNCTION_NAME" \
  --gen2 \
  --runtime=python311 \
  --region="$REGION" \
  --source=. \
  --entry-point="$FUNCTION_NAME" \
  --trigger-http \
  --timeout=540s \
  --memory=2048MB \
  --service-account="$SERVICE_ACCOUNT" \
  --set-env-vars="$ENV_VARS"

DEPLOY_STATUS=$?
if [ $DEPLOY_STATUS -eq 0 ]; then
  echo "✅ Deployment complete!"
  echo "Function is available at: https://$REGION-$project_id.cloudfunctions.net/$FUNCTION_NAME"
  echo 
  echo "To view logs, run:"
  echo "gcloud logging read \"resource.type=cloud_function AND resource.labels.function_name=$FUNCTION_NAME\" --limit=20"
else
  echo "❌ Deployment failed with status code $DEPLOY_STATUS"
  echo "Check the error message above for details."
fi