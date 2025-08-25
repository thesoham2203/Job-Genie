import os
import logging
from pathlib import Path
from typing import Union, List, Optional
import mimetypes
import magic

logger = logging.getLogger(__name__)

class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass

class SecurityValidator:
    """Security validation utilities for file processing."""
    
    # Allowed MIME types for security
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'application/json'
    }
    
    # Maximum file size in bytes (default 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    # Dangerous file extensions to block
    BLOCKED_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', 
        '.js', '.jar', '.dll', '.sys', '.bin'
    }
    
    @classmethod
    def validate_file_path(cls, file_path: Union[str, Path]) -> Path:
        """
        Validate file path for security issues.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            FileValidationError: If path is invalid or insecure
        """
        path = Path(file_path).resolve()
        
        # Check if file exists
        if not path.exists():
            raise FileValidationError(f"File does not exist: {path}")
        
        # Check if it's actually a file
        if not path.is_file():
            raise FileValidationError(f"Path is not a file: {path}")
        
        # Check file size
        file_size = path.stat().st_size
        if file_size > cls.MAX_FILE_SIZE:
            raise FileValidationError(
                f"File size ({file_size} bytes) exceeds maximum allowed "
                f"size ({cls.MAX_FILE_SIZE} bytes)"
            )
        
        # Check file extension
        if path.suffix.lower() in cls.BLOCKED_EXTENSIONS:
            raise FileValidationError(f"File type not allowed: {path.suffix}")
        
        # Validate MIME type using python-magic
        try:
            mime_type = magic.from_file(str(path), mime=True)
            if mime_type not in cls.ALLOWED_MIME_TYPES:
                raise FileValidationError(f"MIME type not allowed: {mime_type}")
        except Exception as e:
            logger.warning(f"Could not determine MIME type for {path}: {e}")
        
        return path
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = os.path.basename(filename)
        
        # Remove or replace dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Limit filename length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @classmethod
    def validate_directory_path(cls, dir_path: Union[str, Path]) -> Path:
        """
        Validate directory path for security.
        
        Args:
            dir_path: Directory path to validate
            
        Returns:
            Validated Path object
            
        Raises:
            FileValidationError: If directory is invalid
        """
        path = Path(dir_path).resolve()
        
        # Check if directory exists
        if not path.exists():
            raise FileValidationError(f"Directory does not exist: {path}")
        
        # Check if it's actually a directory
        if not path.is_dir():
            raise FileValidationError(f"Path is not a directory: {path}")
        
        # Check write permissions
        if not os.access(path, os.W_OK):
            raise FileValidationError(f"No write permission for directory: {path}")
        
        return path

def validate_json_structure(data: dict, required_fields: List[str]) -> bool:
    """
    Validate that JSON data contains required fields.
    
    Args:
        data: JSON data to validate
        required_fields: List of required field names
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If required fields are missing
    """
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    return True

def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input to prevent injection attacks.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Limit text length
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes and other control characters
    text = text.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')
    
    # Basic HTML/script tag removal (basic protection)
    import re
    text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)
    
    return text.strip()
