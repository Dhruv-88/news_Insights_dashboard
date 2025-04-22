# Set the conda environment name
CONDA_ENV_NAME = news_env

## Set up commands
# Set the conda command
CONDA_CMD = conda

# Set the activate command based on the operating system
ifeq ($(OS),Windows_NT)
	ACTIVATE_CMD = $(CONDA_CMD) activate
else ifeq ($(shell uname -s),Darwin)
	ACTIVATE_CMD = $(CONDA_CMD) activate
else
	ACTIVATE_CMD = source activate
endif

# Set the poetry command
POETRY_CMD = poetry

# Set the default target
.DEFAULT_GOAL := run

# Create the conda environment
create-env:
	$(CONDA_CMD) create --name $(CONDA_ENV_NAME) python=3.12

# Install dependencies in the conda environment using conda
install-deps-conda:
	$(CONDA_CMD) install --name $(CONDA_ENV_NAME) < requirements.txt

# Install dependencies in the conda environment using poetry
install-deps-poetry:
	$(POETRY_CMD) install --no-root

# Check for Poetry and install if not found
check-poetry:
	@echo "Checking for Poetry..."
	@which poetry || (echo "Poetry not found, installing..." && conda install -c conda-forge poetry)

# Initialize a new Poetry project
init-project: check-poetry
	@echo "Initializing new Poetry project..."
	@poetry init --no-interaction

# Run the program in the conda environment
run: activate-env
	python your_program.py

# Clean up the conda environment
clean:
	$(CONDA_CMD) env remove --name $(CONDA_ENV_NAME)

# Update requirements file from poetry dependencies
update-requirements:
	poetry export -f requirements.txt --output requirements.txt --without-hashes

# Run tests using poetry
test:
	PYTHONPATH=$(PWD) pytest firebase/test/auth/test_*.py -v
	PYTHONPATH=$(PWD) pytest firebase/test/user/test_*.py -v

# Run tests using poetry with coverage
test-coverage:
	PYTHONPATH=. pytest firebase/test/auth/test_*.py -v --cov=firebase/functions --cov-report=term-missing

# Remove all __pycache__ directories
clean-pycache:
	find . -type d -name '__pycache__' -exec rm -rf {} +


# Docker commands 
build-docker:
	docker build -t briefly_env .

run-docker:
	@if [ "$(ENABLE_FLASK_APP)" = "true" ] && [ "$(ENABLE_LAMBDA_FUNCTION)" = "true" ]; then \
		echo "Starting Flask and Lambda..."; \
		docker run -e ENABLE_FLASK_APP=true -e ENABLE_LAMBDA_FUNCTION=true -p 1000:1000 -p 9000:8080  briefly_env; \
	elif [ "$(ENABLE_FLASK_APP)" = "true" ]; then \
		echo "Starting Flask only..."; \
		docker run -e ENABLE_FLASK_APP=true -e ENABLE_LAMBDA_FUNCTION=false -p 1000:1000  briefly_env; \
	elif [ "$(ENABLE_LAMBDA_FUNCTION)" = "true" ]; then \
		echo "Starting Lambda only..."; \
		docker run -e ENABLE_FLASK_APP=false -e ENABLE_LAMBDA_FUNCTION=true -p 9000:8080  briefly_env; \
	else \
		echo "Neither Flask nor Lambda is enabled."; \
	fi

.PHONY: run-signup run-login install clean-all

install:
	poetry install

clean-all:
	pkill -f functions-framework || true
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run tests in watch mode (useful during development)
test-watch:
	PYTHONPATH=. pytest-watch firebase/test/auth/test_*.py -v

# Clean test cache
test-clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Add these new targets
install-requirements:
	pip install -r requirements.txt




chmod-deploy-script:
	chmod +x ./scripts/deployment.sh 

deploy-gcp: chmod-deploy-script
	./scripts/deployment.sh 

run-pipline-cloud: 
	gcloud functions call news-etl-pipeline \
	--gen2 \
	--region=us-central1 \
	--project=upheld-quanta-455417-m4


# curl -X POST https://us-central1-upheld-quanta-455417-m4.cloudfunctions.net/news_etl_pipeline \
  -H "Authorization: bearer $(gcloud auth print-identity-token)" 

  gcloud scheduler jobs create http news_etl_scheduler \
  --schedule="0 */12 * * *" \
  --uri="https://us-central1-upheld-quanta-455417-m4.cloudfunctions.net/news_etl_pipeline" \
  --http-method=POST \
  --oidc-service-account-email="news-service-account@upheld-quanta-455417-m4.iam.gserviceaccount.com" \
  --oidc-token-audience="https://us-central1-upheld-quanta-455417-m4.cloudfunctions.net/news_etl_pipeline" \
  --location=us-central1