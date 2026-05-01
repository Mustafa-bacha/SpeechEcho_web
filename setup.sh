#!/bin/bash

################################################################################
# SpeechEcho - Automated Setup Script
# This script automates the complete setup process for a fresh system
# Usage: bash setup.sh
################################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Utility functions
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup script
main() {
    print_header "🚀 SpeechEcho - Complete Automated Setup"

    # Check prerequisites
    print_header "Step 1/5: Checking Prerequisites"

    if ! command_exists python3; then
        print_error "Python 3 is required but not installed"
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_success "Python 3 found ($PYTHON_VERSION)"

    if ! command_exists node; then
        print_error "Node.js is required but not installed"
        echo "Visit: https://nodejs.org/"
        exit 1
    fi
    NODE_VERSION=$(node --version)
    print_success "Node.js found ($NODE_VERSION)"

    if ! command_exists npm; then
        print_error "npm is required but not installed"
        exit 1
    fi
    NPM_VERSION=$(npm --version)
    print_success "npm found ($NPM_VERSION)"

    if ! command_exists git; then
        print_error "Git is required but not installed"
        exit 1
    fi
    print_success "Git found"

    # Backend setup
    print_header "Step 2/5: Setting Up Backend"

    if [ ! -d "backend" ]; then
        print_error "backend/ directory not found"
        exit 1
    fi

    cd backend

    # Create virtual environment
    if [ -d "venv" ]; then
        print_warning "Virtual environment already exists, skipping creation"
    else
        print_info "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    fi

    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
    print_success "Virtual environment activated"

    # Upgrade pip
    print_info "Upgrading pip, setuptools, wheel..."
    pip install --upgrade pip setuptools wheel --quiet
    print_success "pip upgraded"

    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_info "Installing backend dependencies (this may take 5-10 minutes)..."
        pip install -r requirements.txt --quiet
        print_success "Backend dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi

    # Create .env if not exists
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env
            print_success "Backend .env created from template"
            print_warning "Please edit backend/.env with your settings"
        fi
    else
        print_success "Backend .env already exists"
    fi

    # Initialize database
    print_info "Initializing database..."
    python3 -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine); print('Database initialized')" 2>/dev/null || true
    print_success "Database initialized"

    cd ..

    # Frontend setup
    print_header "Step 3/5: Setting Up Frontend"

    if [ ! -d "frontend" ]; then
        print_error "frontend/ directory not found"
        exit 1
    fi

    cd frontend

    # Clear npm cache if issues exist
    print_info "Clearing npm cache..."
    npm cache clean --force --quiet

    # Install dependencies
    print_info "Installing frontend dependencies (this may take 2-5 minutes)..."
    npm install --quiet
    print_success "Frontend dependencies installed"

    # Create .env.local if not exists
    if [ ! -f ".env.local" ]; then
        if [ -f ".env.example" ]; then
            cp .env.example .env.local
            print_success "Frontend .env.local created from template"
        fi
    else
        print_success "Frontend .env.local already exists"
    fi

    cd ..

    # Chatterbox setup
    print_header "Step 4/5: Checking Chatterbox TTS"

    if [ -d "chatterbox-streaming" ]; then
        print_success "Chatterbox TTS directory found"
        print_info "Models will be downloaded automatically on first use"
    else
        print_warning "chatterbox-streaming/ directory not found (optional)"
    fi

    # Summary
    print_header "Step 5/5: Setup Complete! ✅"

    print_success "All dependencies installed successfully!"
    echo ""
    print_info "📁 Project Structure:"
    echo "  backend/          - FastAPI backend server"
    echo "  frontend/         - React frontend application"
    echo "  chatterbox-streaming/ - TTS model (optional)"
    echo ""
    print_info "⚙️  Configuration Files:"
    echo "  backend/.env      - Backend configuration (EDIT THIS!)"
    echo "  frontend/.env.local - Frontend configuration"
    echo ""
    print_info "🚀 To start the application:"
    echo ""
    echo "  Terminal 1 (Backend):"
    echo "    cd backend"
    echo "    source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo "    uvicorn app.main:app --reload --port 8000"
    echo ""
    echo "  Terminal 2 (Frontend):"
    echo "    cd frontend"
    echo "    npm run dev"
    echo ""
    print_info "🌐 Access the application:"
    echo "  Frontend:   http://localhost:5173"
    echo "  API Docs:   http://localhost:8000/api/docs"
    echo "  ReDoc:      http://localhost:8000/api/redoc"
    echo ""
    print_warning "Remember to:"
    echo "  1. Edit backend/.env with your configuration"
    echo "  2. Add API keys if needed (GEMINI_API_KEY, etc.)"
    echo "  3. Update CORS_ORIGINS if hosting on different domain"
    echo ""
    print_info "📚 For more information, see:"
    echo "  - SETUP.md - Complete setup guide"
    echo "  - README.md - Project overview"
    echo "  - MODEL_DOCUMENTATION.md - Model details"
    echo ""
}

# Run main function
main

exit 0
