import json
import logging
import os.path
import pathlib
from typing import Dict, Any

from .parsers import ParseJobDesc, ParseResume
from .ReadPdf import read_single_pdf
from .utils.security import SecurityValidator, FileValidationError, sanitize_text_input

# Configure logging
logger = logging.getLogger(__name__)

READ_RESUME_FROM = "Data/Resumes/"
SAVE_DIRECTORY = "Data/Processed/Resumes"


class ResumeProcessor:
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.input_file_name = os.path.join(READ_RESUME_FROM + self.input_file)

    def process(self) -> bool:
        """
        Process a resume file with enhanced error handling and security validation.
        
        Returns:
            bool: True if processing successful, False otherwise
        """
        try:
            # Validate file security before processing
            SecurityValidator.validate_file_path(self.input_file_name)
            
            logger.info(f"Starting processing of resume: {self.input_file}")
            
            resume_dict = self._read_resumes()
            
            if not resume_dict:
                logger.error(f"Failed to extract data from resume: {self.input_file}")
                return False
                
            self._write_json_file(resume_dict)
            
            logger.info(f"Successfully processed resume: {self.input_file}")
            return True
            
        except FileValidationError as e:
            logger.error(f"File validation failed for {self.input_file}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"An error occurred processing {self.input_file}: {str(e)}", exc_info=True)
            return False

    def _read_resumes(self) -> Dict[str, Any]:
        """
        Read and parse resume with enhanced error handling.
        
        Returns:
            dict: Parsed resume data
            
        Raises:
            Exception: If PDF reading or parsing fails
        """
        try:
            data = read_single_pdf(self.input_file_name)
            
            if not data or not data.strip():
                raise ValueError("No text extracted from PDF")
            
            # Sanitize extracted text
            sanitized_data = sanitize_text_input(data)
            
            output = ParseResume(sanitized_data).get_JSON()
            
            if not output:
                raise ValueError("Failed to parse resume data")
                
            return output
            
        except Exception as e:
            logger.error(f"Failed to read resume {self.input_file_name}: {str(e)}")
            raise

    def _read_job_desc(self) -> Dict[str, Any]:
        """
        Read and parse job description with enhanced error handling.
        
        Returns:
            dict: Parsed job description data
            
        Raises:
            Exception: If PDF reading or parsing fails
        """
        try:
            data = read_single_pdf(self.input_file_name)
            
            if not data or not data.strip():
                raise ValueError("No text extracted from PDF")
            
            # Sanitize extracted text
            sanitized_data = sanitize_text_input(data)
            
            output = ParseJobDesc(sanitized_data).get_JSON()
            
            if not output:
                raise ValueError("Failed to parse job description data")
                
            return output
            
        except Exception as e:
            logger.error(f"Failed to read job description {self.input_file_name}: {str(e)}")
            raise

    def _write_json_file(self, resume_dictionary: Dict[str, Any]) -> None:
        """
        Write resume data to JSON file with enhanced error handling.
        
        Args:
            resume_dictionary: Resume data to save
            
        Raises:
            Exception: If file writing fails
        """
        try:
            # Validate required fields
            if 'unique_id' not in resume_dictionary:
                raise ValueError("Resume data missing unique_id field")
            
            # Sanitize filename
            sanitized_filename = SecurityValidator.sanitize_filename(self.input_file)
            
            file_name = f"Resume-{sanitized_filename}{resume_dictionary['unique_id']}.json"
            save_directory_name = pathlib.Path(SAVE_DIRECTORY) / file_name
            
            # Ensure directory exists
            save_directory_name.parent.mkdir(parents=True, exist_ok=True)
            
            # Validate save directory
            SecurityValidator.validate_directory_path(SAVE_DIRECTORY)
            
            json_object = json.dumps(resume_dictionary, sort_keys=True, indent=2, ensure_ascii=False)
            
            with open(save_directory_name, "w+", encoding='utf-8') as outfile:
                outfile.write(json_object)
                
            logger.info(f"Successfully saved resume data to: {save_directory_name}")
            
        except Exception as e:
            logger.error(f"Failed to write JSON file for {self.input_file}: {str(e)}")
            raise
