# WhatsApp Conversation Analyzer

A web application that helps you analyze your WhatsApp conversations with detailed metrics, statistics, and AI-powered insights.

## Features

- 📊 Message activity heatmap visualization
- 📈 Detailed conversation statistics
- 🔤 Word usage analysis and metrics
- 🤖 AI-powered conversation theme analysis (Premium)
- 🎭 Message simulation based on participant styles (Premium)
- 🌐 Multi-language support (English and Portuguese)

## Tech Stack

- **Frontend**: React + TypeScript + Vite
- **Backend**: FastAPI + Python
- **AI Integration**: OpenAI GPT models
- **Data Analysis**: NLTK, Pandas, NumPy

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python (v3.12+)
- pip
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/whatsapp-conversation-analyzer.git
cd whatsapp-conversation-analyzer
```

2. Set up the frontend:

```bash
cd client
npm install
npm run dev
```

3. Set up the backend (preferably use a virtual environment):

```bash
cd fastapi-backend
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app/main.py
```

### Running the application

1. Run the backend:

```bash
cd fastapi-backend
source venv/bin/activate # On Windows: venv\Scripts\activate
uvicorn app.main:app --reload
```

2. Run the frontend:

```bash
cd client
npm run dev
```

3. Access the application at `http://localhost:5173`

## Project Structure

- `client/`: Vite-powered React frontend
- `fastapi-backend/`: FastAPI backend
- `README.md`: This file


## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.

