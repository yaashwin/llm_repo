#!/bin/bash

echo "Setting up Multimodal Transcription & Local LLM Application..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check for Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
else
    print_status "Python 3 found: $(python3 --version)"
fi

# Check for Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js is required but not installed. Please install Node.js 14 or higher."
    exit 1
else
    print_status "Node.js found: $(node --version)"
fi

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    print_error "FFmpeg is required but not installed."
    echo "Please install FFmpeg:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install ffmpeg"
    echo "  macOS: brew install ffmpeg"
    echo "  Windows: Download from https://ffmpeg.org/download.html"
    exit 1
else
    print_status "FFmpeg found"
fi

# Create project structure
print_status "Creating project directories..."
mkdir -p backend/uploads
mkdir -p backend/outputs
touch backend/uploads/.gitkeep
touch backend/outputs/.gitkeep

# Backend setup
print_status "Setting up backend..."
cd backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_status "Creating .env file..."
    cat > .env << EOL
# LLM Provider API Keys
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Default LLM Provider (gemini, openai, claude, ollama)
DEFAULT_LLM_PROVIDER=gemini

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
EOL
    print_warning "Please add your API keys to backend/.env file"
fi

# Create virtual environment
python3 -m venv venv
print_status "Virtual environment created."

# Activate virtual environment
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Install additional YouTube download dependencies
print_status "Installing YouTube download dependencies..."
pip install -U yt-dlp pytubefix

# Download Whisper model
print_status "Downloading Whisper model..."
python -c "import whisper; whisper.load_model('base')" || print_warning "Whisper model download failed - will download on first use"

# Create empty cookies file
touch cookies.txt

# Check CUDA availability
python -c "import torch; print('CUDA available' if torch.cuda.is_available() else 'CPU mode')"

cd ..

# Frontend setup
print_status "Setting up frontend..."
cd frontend

# Check if package.json exists
if [ ! -f package.json ]; then
    print_error "package.json not found in frontend directory"
    exit 1
fi

# Install Node dependencies
print_status "Installing Node dependencies..."
npm install

# Create .env.local for frontend if needed
if [ ! -f .env.local ]; then
    cat > .env.local << EOL
REACT_APP_API_URL=http://localhost:8000
EOL
fi

cd ..

# Install Ollama
print_status "Checking for Ollama..."
if ! command -v ollama &> /dev/null; then
    print_status "Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    else
        print_warning "Please install Ollama manually from https://ollama.ai"
        print_warning "After installation, run: ollama pull tinyllama"
    fi
else
    print_status "Ollama is already installed."
fi

# Pull recommended models
if command -v ollama &> /dev/null; then
    print_status "Pulling recommended Ollama models..."
    ollama pull tinyllama:latest || print_warning "Failed to pull tinyllama"
    print_status "You can also try these models:"
    echo "  - ollama pull qwen:0.5b (very small, 394MB)"
    echo "  - ollama pull gemma:2b (good quality, 1.4GB)"
fi

# Create run scripts
print_status "Creating run scripts..."

# Create run_backend.sh
cat > run_backend.sh << 'EOL'
#!/bin/bash
cd backend
source venv/bin/activate
python app.py
EOL
chmod +x run_backend.sh

# Create run_frontend.sh
cat > run_frontend.sh << 'EOL'
#!/bin/bash
cd frontend
npm start
EOL
chmod +x run_frontend.sh

# Create run_ollama.sh
cat > run_ollama.sh << 'EOL'
#!/bin/bash
ollama serve
EOL
chmod +x run_ollama.sh

echo ""
print_status "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Add your API keys to backend/.env file (optional, for meeting summaries)"
echo "2. Start the services:"
echo "   Terminal 1: ./run_ollama.sh    (Local LLM)"
echo "   Terminal 2: ./run_backend.sh   (Backend API)"
echo "   Terminal 3: ./run_frontend.sh  (Frontend UI)"
echo ""
echo "The application will be available at http://localhost:3000"
echo ""
print_warning "Troubleshooting:"
echo "- YouTube downloads: If you encounter issues, export cookies from your browser to backend/cookies.txt"
echo "- Memory issues with Ollama: Try smaller models like 'ollama pull qwen:0.5b'"
echo "- GPU support: Install CUDA toolkit for faster transcription"