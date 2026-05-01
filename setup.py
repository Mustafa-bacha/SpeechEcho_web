#!/usr/bin/env python3
"""
SpeechEcho - Cross-platform Automated Setup Script
This script works on Linux, macOS, and Windows
Usage: python setup.py
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class Colors:
    """ANSI color codes for terminal output"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^80}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'='*80}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def run_command(command, shell=False, cwd=None):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            command if shell else command.split(),
            shell=shell,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)

def get_command_output(command):
    """Get output from a command"""
    try:
        result = subprocess.run(
            command.split() if isinstance(command, str) else command,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except:
        return None

def check_prerequisites():
    """Check if all prerequisites are installed"""
    print_header("Step 1/5: Checking Prerequisites")

    # Check Python
    if not command_exists("python") and not command_exists("python3"):
        print_error("Python 3 is required but not installed")
        print("Visit: https://www.python.org/downloads/")
        return False

    python_version = get_command_output("python --version") or \
                     get_command_output("python3 --version")
    print_success(f"Python found ({python_version})")

    # Check Node.js
    if not command_exists("node"):
        print_error("Node.js is required but not installed")
        print("Visit: https://nodejs.org/")
        return False

    node_version = get_command_output("node --version")
    print_success(f"Node.js found ({node_version})")

    # Check npm
    if not command_exists("npm"):
        print_error("npm is required but not installed")
        return False

    npm_version = get_command_output("npm --version")
    print_success(f"npm found ({npm_version})")

    # Check Git (optional)
    if command_exists("git"):
        git_version = get_command_output("git --version")
        print_success(f"Git found ({git_version})")
    else:
        print_warning("Git not found (optional)")

    return True

def setup_backend():
    """Setup backend with virtual environment and dependencies"""
    print_header("Step 2/5: Setting Up Backend")

    backend_path = Path("backend")
    if not backend_path.exists():
        print_error("backend/ directory not found")
        return False

    os.chdir(backend_path)

    # Create virtual environment
    venv_path = Path("venv")
    if not venv_path.exists():
        print_info("Creating Python virtual environment...")
        success, _, _ = run_command("python -m venv venv")
        if not success:
            success, _, _ = run_command("python3 -m venv venv")
        if not success:
            print_error("Failed to create virtual environment")
            return False
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment already exists")

    # Determine pip command
    if os.name == 'nt':  # Windows
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:  # Linux/macOS
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"

    # Upgrade pip
    print_info("Upgrading pip, setuptools, wheel...")
    run_command(f"{pip_cmd} install --upgrade pip setuptools wheel")
    print_success("pip upgraded")

    # Install requirements
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print_info("Installing backend dependencies (this may take 5-15 minutes)...")
        success, stdout, stderr = run_command(f"{pip_cmd} install -r requirements.txt")
        if not success:
            print_error("Failed to install backend dependencies")
            print(f"Error: {stderr}")
            return False
        print_success("Backend dependencies installed")
    else:
        print_error("requirements.txt not found")
        return False

    # Create .env
    env_file = Path(".env")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Backend .env created from template")
        print_warning("Please edit backend/.env with your settings")
    elif env_file.exists():
        print_success("Backend .env already exists")

    # Initialize database
    print_info("Initializing database...")
    success, stdout, stderr = run_command(
        f'{python_cmd} -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"'
    )
    if success:
        print_success("Database initialized")

    os.chdir("..")
    return True

def setup_frontend():
    """Setup frontend with Node.js dependencies"""
    print_header("Step 3/5: Setting Up Frontend")

    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print_error("frontend/ directory not found")
        return False

    os.chdir(frontend_path)

    # Clear npm cache
    print_info("Clearing npm cache...")
    run_command("npm cache clean --force")

    # Install dependencies
    print_info("Installing frontend dependencies (this may take 2-5 minutes)...")
    success, stdout, stderr = run_command("npm install")
    if not success:
        print_error("Failed to install frontend dependencies")
        print(f"Error: {stderr}")
        return False
    print_success("Frontend dependencies installed")

    # Create .env.local
    env_file = Path(".env.local")
    env_example = Path(".env.example")
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("Frontend .env.local created from template")
    elif env_file.exists():
        print_success("Frontend .env.local already exists")

    os.chdir("..")
    return True

def check_chatterbox():
    """Check Chatterbox TTS directory"""
    print_header("Step 4/5: Checking Chatterbox TTS")

    chatterbox_path = Path("chatterbox-streaming")
    if chatterbox_path.exists():
        print_success("Chatterbox TTS directory found")
        print_info("Models will be downloaded automatically on first use")
    else:
        print_warning("chatterbox-streaming/ directory not found (optional)")

    return True

def print_summary():
    """Print setup summary and next steps"""
    print_header("Setup Complete! ✅")

    print(f"{Colors.GREEN}{Colors.BOLD}All dependencies installed successfully!{Colors.ENDC}")
    print()
    print(f"{Colors.BOLD}📁 Project Structure:{Colors.ENDC}")
    print("   backend/          - FastAPI backend server")
    print("   frontend/         - React frontend application")
    print("   chatterbox-streaming/ - TTS model (optional)")
    print()
    print(f"{Colors.BOLD}⚙️  Configuration Files:{Colors.ENDC}")
    print("   backend/.env      - Backend configuration (EDIT THIS!)")
    print("   frontend/.env.local - Frontend configuration")
    print()
    print(f"{Colors.BOLD}🚀 To start the application:{Colors.ENDC}")
    print()
    print("   Terminal 1 (Backend):")
    print("     cd backend")
    if os.name == 'nt':  # Windows
        print("     venv\\Scripts\\activate")
    else:
        print("     source venv/bin/activate")
    print("     uvicorn app.main:app --reload --port 8000")
    print()
    print("   Terminal 2 (Frontend):")
    print("     cd frontend")
    print("     npm run dev")
    print()
    print(f"{Colors.BOLD}🌐 Access the application:{Colors.ENDC}")
    print("   Frontend:   http://localhost:5173")
    print("   API Docs:   http://localhost:8000/api/docs")
    print("   ReDoc:      http://localhost:8000/api/redoc")
    print()
    print(f"{Colors.BOLD}⚡ Remember to:{Colors.ENDC}")
    print("   1. Edit backend/.env with your configuration")
    print("   2. Add API keys if needed (GEMINI_API_KEY, etc.)")
    print("   3. Update CORS_ORIGINS if hosting on different domain")
    print()
    print(f"{Colors.BOLD}📚 For more information:{Colors.ENDC}")
    print("   - SETUP.md - Complete setup guide")
    print("   - README.md - Project overview")
    print("   - MODEL_DOCUMENTATION.md - Model details")
    print()

def main():
    """Main setup function"""
    try:
        # Change to project root if not already there
        if not Path("backend").exists():
            print_error("Not in project root directory")
            print("Please run this script from the SpeechEcho_web directory")
            sys.exit(1)

        # Run setup steps
        if not check_prerequisites():
            sys.exit(1)

        if not setup_backend():
            sys.exit(1)

        if not setup_frontend():
            sys.exit(1)

        if not check_chatterbox():
            sys.exit(1)

        print_summary()
        print_success("Setup completed successfully!")
        return 0

    except KeyboardInterrupt:
        print_warning("\nSetup interrupted by user")
        return 1
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
