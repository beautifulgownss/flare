.PHONY: help install demo test lint format pipeline dashboard dashboard-test

help:  ## Show available commands
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

install:  ## Install Python dev dependencies
	python -m pip install -r requirements-dev.txt

demo:  ## Run the zero-key offline demo (writes demo/output/)
	python src/demo.py

test:  ## Run the Python test suite
	python -m pytest

lint:  ## Lint Python code
	ruff check src tests

format:  ## Auto-fix lint issues
	ruff check src tests --fix

pipeline:  ## Run the full live pipeline (requires API keys in .env)
	python src/run_pipeline.py

dashboard:  ## Start the React dashboard on localhost:3000
	cd dashboard && npm install && npm start

dashboard-test:  ## Run dashboard tests
	cd dashboard && CI=true npm test -- --watchAll=false
