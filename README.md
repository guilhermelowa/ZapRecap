# ZapRecap

A WhatsApp chat analyzer built with FastAPI and React.

## Features

- 📊 Message activity heatmap visualization
- 📈 Detailed conversation statistics
- 🔤 Word usage analysis and metrics
- 🤖 AI-powered conversation theme analysis (Premium)
- 🎭 Message simulation based on participant styles (Premium)
- 🌐 Multi-language support (English and Portuguese)

## Development Setup

### Prerequisites
- Python 3.8 or higher
- Git
- Node.js and npm (for the frontend)

### Backend Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd ZapRecap
```

2. Run the setup script:

For Unix/Linux/Mac:
```bash
chmod +x setup.sh
./setup.sh
```

For Windows (PowerShell):
```powershell
.\setup.ps1
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up pre-commit hooks for testing and linting

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. Before each commit:
- All tests will be run
- Python code will be linted with flake8

If any tests fail or linting issues are found, the commit will be aborted.

### Manual Testing

To run tests manually:

```bash
cd fastapi-backend
python -m pytest tests/
```

To run linting manually:

```bash
cd fastapi-backend
python -m flake8
```

### Running the Application

1. Start the backend:
```bash
cd fastapi-backend
uvicorn app.main:app --reload
```

2. Start the frontend (in a separate terminal):
```bash
cd client
npm install
npm run dev
```

The application will be available at http://localhost:5173

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **AI Integration**: OpenAI GPT models
- **Data Analysis**: NLTK, Pandas, NumPy

## Project Structure

- `client/`: Vite-powered React frontend
- `fastapi-backend/`: FastAPI backend
- `README.md`: This file

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.

