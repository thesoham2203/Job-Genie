import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    def __init__(self):
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.qdrant_api_key = os.getenv('QDRANT_API_KEY')
        self.qdrant_url = os.getenv('QDRANT_URL')
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.max_file_size_mb = int(os.getenv('MAX_FILE_SIZE_MB', '10'))
        self.allowed_file_types = os.getenv('ALLOWED_FILE_TYPES', 'pdf').split(',')
        self.secret_key = os.getenv('SECRET_KEY')
        
    def validate(self) -> bool:
        """Validate that required configuration is present."""
        required_keys = [
            'cohere_api_key', 'qdrant_api_key', 'qdrant_url', 'secret_key'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(self, key):
                missing_keys.append(key.upper())
        
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary (excluding sensitive data)."""
        return {
            'debug': self.debug,
            'log_level': self.log_level,
            'max_file_size_mb': self.max_file_size_mb,
            'allowed_file_types': self.allowed_file_types
        }

def load_legacy_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from legacy YAML file.
    This function maintains backward compatibility.
    """
    if config_path is None:
        config_path = Path("scripts/similarity/config.yml")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Global config instance
config = Config()
