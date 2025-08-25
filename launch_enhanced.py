#!/usr/bin/env python3
"""
Job Genie - Enhanced Resume Matcher Launch Script
Integrates all Phase 1-2 components with improved UI
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        logger.error("Python 3.8+ is required. Current version: %s.%s.%s", 
                    version.major, version.minor, version.micro)
        return False
    
    logger.info("Python version: %s.%s.%s ✓", version.major, version.minor, version.micro)
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'streamlit',
        'pandas',
        'numpy',
        'plotly',
        'spacy',
        'transformers',
        'PyPDF2',
        'python-docx',
        'requests',
        'pydantic'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            logger.info("%s ✓", package)
        except ImportError:
            missing_packages.append(package)
            logger.warning("%s ✗", package)
    
    if missing_packages:
        logger.error("Missing packages: %s", ', '.join(missing_packages))
        logger.info("Run: pip install -r requirements-production.txt")
        return False
    
    return True

def setup_environment():
    """Setup environment variables and configuration."""
    env_example_path = Path('.env.example')
    env_path = Path('.env')
    
    if env_example_path.exists() and not env_path.exists():
        logger.info("Creating .env file from template...")
        try:
            with open(env_example_path, 'r') as f:
                content = f.read()
            
            with open(env_path, 'w') as f:
                f.write(content)
            
            logger.info(".env file created. Please configure your API keys.")
        except Exception as e:
            logger.warning("Could not create .env file: %s", e)
    
    # Set default environment variables
    os.environ.setdefault('STREAMLIT_THEME_PRIMARYCOLOR', '#667eea')
    os.environ.setdefault('STREAMLIT_THEME_BACKGROUNDCOLOR', '#ffffff')
    os.environ.setdefault('STREAMLIT_THEME_SECONDARYBACKGROUNDCOLOR', '#f0f2f6')
    os.environ.setdefault('STREAMLIT_THEME_TEXTCOLOR', '#262730')
    
    logger.info("Environment setup complete ✓")

def create_data_directories():
    """Create necessary data directories."""
    directories = [
        'Data/JobDescription',
        'Data/Resumes',
        'Data/Processed/JobDescription',
        'Data/Processed/Resumes',
        'logs',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("Data directories created ✓")

def download_spacy_model():
    """Download required spaCy model if not present."""
    try:
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model en_core_web_sm ✓")
        except OSError:
            logger.info("Downloading spaCy model en_core_web_sm...")
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], 
                         check=True)
            logger.info("spaCy model downloaded ✓")
    except ImportError:
        logger.warning("spaCy not installed, skipping model download")
    except Exception as e:
        logger.warning("Could not download spaCy model: %s", e)

def run_streamlit():
    """Launch the Streamlit application."""
    logger.info("Launching Job Genie - Enhanced Resume Matcher...")
    
    # Set Streamlit configuration
    config_args = [
        "--server.headless", "true",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--theme.primaryColor", "#667eea",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
        "--theme.textColor", "#262730",
        "--runner.magicEnabled", "false"
    ]
    
    # Choose the enhanced app
    app_file = "streamlit_enhanced.py"
    if not Path(app_file).exists():
        app_file = "streamlit_app.py"  # Fallback to original
        logger.warning("Enhanced app not found, using original streamlit_app.py")
    
    cmd = [sys.executable, "-m", "streamlit", "run", app_file] + config_args
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except subprocess.CalledProcessError as e:
        logger.error("Failed to start Streamlit: %s", e)
        return False
    
    return True

def main():
    """Main launch function."""
    print("🎯 Job Genie - Enhanced Resume Matcher")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    create_data_directories()
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Please install missing dependencies first:")
        logger.error("pip install -r requirements-production.txt")
        sys.exit(1)
    
    # Download required models
    download_spacy_model()
    
    # Launch application
    logger.info("🚀 Starting application...")
    print("\n🌐 Opening browser at: http://localhost:8501")
    print("💡 Press Ctrl+C to stop the application\n")
    
    success = run_streamlit()
    
    if not success:
        logger.error("Failed to start application")
        sys.exit(1)

if __name__ == "__main__":
    main()
