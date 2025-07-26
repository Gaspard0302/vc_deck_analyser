#!/bin/bash
echo "Starting PitchSight Analyzer..."

# Check if required dependencies are installed
echo "Checking dependencies..."

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.11+"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with your API keys."
    echo "See README.md for details."
    exit 1
fi

# Check if Python dependencies are installed
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv venv
fi

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "🔧 Installing Python dependencies..."
pip install -r requirements.txt

# Check if Node dependencies are installed
if [ ! -d "pitchsight-analyzer/node_modules" ]; then
    echo "🔧 Installing Node.js dependencies..."
    cd pitchsight-analyzer
    npm install
    cd ..
fi

echo "🚀 Starting servers..."

# Start backend in background
echo "🔧 Starting backend server..."
python api.py &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend started successfully on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🔧 Starting frontend server..."
cd pitchsight-analyzer
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 3

echo ""
echo "🎉 PitchSight Analyzer is running!"
echo "📊 Backend:  http://localhost:8000"
echo "🌐 Frontend: http://localhost:8080"
echo ""
echo "📋 Open http://localhost:8080 in your browser to start analyzing pitch decks"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Wait for user interrupt
trap cleanup INT
wait