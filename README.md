# PitchSight Analyzer 🚀

A professional VC pitch deck analyzer that provides AI-powered feedback with coordinate-based annotations directly on PDF slides.

## Features

- 📊 **AI-Powered Analysis**: Analyzes pitch decks using advanced language models
- 🎯 **Coordinate-Based Feedback**: Visual markers directly on PDF slides
- 📱 **Professional UI**: Split-screen design optimized for VC professionals
- ⚡ **Real-Time Processing**: Fast analysis with live feedback display
- 🔍 **Multi-Agent Analysis**: Team assessment, market analysis, and critical issue detection

## Architecture

- **Backend**: FastAPI with LangGraph multi-agent system
- **Frontend**: React + TypeScript with PDF.js integration
- **AI Models**: Claude 3.5 Sonnet for analysis
- **Search**: Tavily for market research

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <your-repo-url>
cd vc_deck_analyser
```

### 2. Environment Setup
Create a `.env` file in the root directory:
```bash
# Required API Keys
ANTHROPIC_API_KEY=your_anthropic_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional: Custom API URLs
VITE_API_URL=http://localhost:8000
```

### 3. Backend Setup (Python/FastAPI)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Frontend Setup (React/TypeScript)
```bash
# Navigate to frontend directory
cd pitchsight-analyzer

# Install Node.js dependencies
npm install
```

## Running the Application

### Method 1: Run Both Servers Simultaneously

**Terminal 1 - Backend Server:**
```bash
# From project root directory
python api.py
```
Backend will start on: http://localhost:8000

**Terminal 2 - Frontend Server:**
```bash
# From pitchsight-analyzer directory
cd pitchsight-analyzer
npm run dev
```
Frontend will start on: http://localhost:8080

### Method 2: Quick Start Script
Create a `start.sh` file in the root directory:
```bash
#!/bin/bash
echo "Starting PitchSight Analyzer..."

# Start backend in background
echo "Starting backend server..."
python api.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd pitchsight-analyzer
npm run dev &
FRONTEND_PID=$!

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:8080"
echo "Press Ctrl+C to stop both servers"

# Wait for user interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

Make it executable and run:
```bash
chmod +x start.sh
./start.sh
```

## Usage Instructions

### 1. Access the Application
Open your browser and navigate to: http://localhost:8080

### 2. Upload a Pitch Deck
- Click "Upload PDF" or drag and drop a PDF file
- Supported format: PDF files only
- Maximum recommended size: 50MB

### 3. Review Analysis Results
- **Left Panel**: PDF viewer with interactive feedback markers
- **Right Panel**: Detailed analysis with tabs:
  - **Critical**: Issues that need immediate attention (red markers)
  - **Market**: TAM/SAM analysis and market insights
  - **Team**: Founder and team assessment
  - **Overview**: General context and key topics

### 4. Interact with Feedback
- Click on red/orange markers on the PDF to see detailed feedback
- Use the feedback panel to navigate between issues
- Zoom and navigate through slides using the PDF controls

## API Endpoints

### Backend API (http://localhost:8000)

- `GET /health` - Health check endpoint
- `POST /analyze-pitch-deck` - Upload and analyze pitch deck
  - Body: `multipart/form-data` with `file` field
  - Response: Analysis results with feedback coordinates

### Example API Usage
```bash
# Health check
curl http://localhost:8000/health

# Analyze pitch deck
curl -X POST http://localhost:8000/analyze-pitch-deck \
  -F "file=@your-pitch-deck.pdf"
```

## Project Structure

```
vc_deck_analyser/
├── agents/                     # AI analysis agents
│   ├── final_summary_agent.py  # Coordinates feedback generation
│   ├── tam_sam_agent.py        # Market analysis
│   ├── team_slide_agent.py     # Team assessment
│   └── topic_extract.py        # Topic extraction
├── utils/                      # Utility functions
│   ├── parse_pdf.py           # PDF processing
│   └── llm.py                 # LLM utilities
├── pitchsight-analyzer/        # React frontend
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/          # API services
│   │   └── pages/             # Page components
│   └── package.json
├── api.py                     # FastAPI backend server
├── graph_flow.py             # LangGraph workflow
├── state_types.py            # Type definitions
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

**Frontend won't start:**
```bash
# Check if port 8080 is in use
lsof -i :8080

# Clear npm cache if needed
npm cache clean --force
```

**Analysis fails:**
- Verify API keys are set in `.env` file
- Check internet connection for Tavily search
- Ensure PDF file is not corrupted or password-protected

### Environment Variables
```bash
# Check if environment variables are loaded
python -c "import os; print('ANTHROPIC_API_KEY:', bool(os.getenv('ANTHROPIC_API_KEY')))"
```

## Development

### Adding New Analysis Agents
1. Create agent in `agents/` directory
2. Add to workflow in `graph_flow.py`
3. Update state types in `state_types.py`

### Frontend Development
```bash
cd pitchsight-analyzer
npm run dev      # Development server
npm run build    # Production build
npm run preview  # Preview production build
```

### Backend Development
```bash
# Run with auto-reload
uvicorn api:app --reload --port 8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary. Please contact the author for licensing information.

## Support

For support and questions, please contact the development team or create an issue in the repository.
