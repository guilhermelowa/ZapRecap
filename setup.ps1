# Create and activate virtual environment
Write-Host "Creating virtual environment..."
cd fastapi-backend
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements.txt

# Initialize pre-commit
Write-Host "Setting up pre-commit hooks..."
cd ..
pre-commit install

Write-Host "Setup complete! The pre-commit hooks are now installed."
Write-Host "Before each commit, tests and linting will be automatically run." 