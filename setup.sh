#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
cd fastapi-backend
python -m venv venv
source venv/bin/activate  # For Unix
# venv\Scripts\activate  # For Windows (uncomment this line and comment the above if using Windows)

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Initialize pre-commit
echo "Setting up pre-commit hooks..."
cd ..
pre-commit install

echo "Setup complete! The pre-commit hooks are now installed."
echo "Before each commit, tests and linting will be automatically run." 