import pytest
import tempfile
import os
from pathlib import Path
from scripts.utils.security import SecurityValidator, FileValidationError

class TestSecurityValidator:
    """Test cases for security validation functionality."""
    
    def test_validate_file_path_valid_file(self):
        """Test validation of a valid file."""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(b'%PDF-1.4 test content')
            tmp_path = tmp.name
        
        try:
            # Should not raise an exception for valid file
            result = SecurityValidator.validate_file_path(tmp_path)
            assert isinstance(result, Path)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_path_nonexistent_file(self):
        """Test validation of non-existent file."""
        with pytest.raises(FileValidationError, match="File does not exist"):
            SecurityValidator.validate_file_path("nonexistent_file.pdf")
    
    def test_validate_file_path_blocked_extension(self):
        """Test validation of blocked file extensions."""
        with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
        
        try:
            with pytest.raises(FileValidationError, match="File type not allowed"):
                SecurityValidator.validate_file_path(tmp_path)
        finally:
            os.unlink(tmp_path)
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        dangerous_filename = "file<>:\"|?*\\/.pdf"
        result = SecurityValidator.sanitize_filename(dangerous_filename)
        assert "<" not in result
        assert ">" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
        
    def test_sanitize_filename_long_name(self):
        """Test sanitization of very long filenames."""
        long_name = "a" * 300 + ".pdf"
        result = SecurityValidator.sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".pdf")

class TestResumeProcessor:
    """Test cases for ResumeProcessor functionality."""
    
    def test_processor_initialization(self):
        """Test ResumeProcessor initialization."""
        from scripts.ResumeProcessor import ResumeProcessor
        
        processor = ResumeProcessor("test_resume.pdf")
        assert processor.input_file == "test_resume.pdf"
        assert "Data/Resumes/test_resume.pdf" in processor.input_file_name

if __name__ == "__main__":
    pytest.main([__file__])
