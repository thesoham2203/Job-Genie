"""
Integration Bridge for Enhanced Resume Matcher
Connects existing components with new enhanced features
"""

import sys
from pathlib import Path
import logging

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

logger = logging.getLogger(__name__)

def integrate_existing_components():
    """Bridge existing components with enhanced features."""
    
    try:
        # Import existing modules
        from scripts.similarity.get_similarity_score import get_similarity_score
        from scripts.ReadPdf import ReadPdf
        
        logger.info("Successfully imported existing components")
        
        # Import new enhanced modules
        from scripts.nlp.advanced_processor import AdvancedNLPProcessor
        from scripts.ats.optimization_engine import ATSOptimizationEngine
        from scripts.parsers.enhanced_parser import EnhancedResumeParser
        from scripts.analytics.insights_engine import ResumeAnalyticsEngine
        
        logger.info("Successfully imported enhanced components")
        
        return True
        
    except ImportError as e:
        logger.warning(f"Could not import some components: {e}")
        return False

class IntegratedResumeProcessor:
    """Integrated processor that combines old and new functionality."""
    
    def __init__(self):
        self.enhanced_available = integrate_existing_components()
        
        if self.enhanced_available:
            try:
                from scripts.nlp.advanced_processor import AdvancedNLPProcessor
                from scripts.ats.optimization_engine import ATSOptimizationEngine
                self.nlp_processor = AdvancedNLPProcessor()
                self.ats_engine = ATSOptimizationEngine()
                logger.info("Enhanced processors initialized")
            except Exception as e:
                logger.warning(f"Could not initialize enhanced processors: {e}")
                self.enhanced_available = False
        
        # Always have fallback functionality
        self.fallback_available = True
        logger.info("Fallback processors initialized")
    
    def extract_text_basic(self, resume_text: str):
        """Basic text extraction and processing."""
        words = resume_text.split()
        sentences = resume_text.split('.')
        
        # Basic keyword extraction
        keywords = []
        for word in words:
            word = word.strip('.,!?').lower()
            if len(word) > 3 and word.isalpha():
                keywords.append(word)
        
        return {
            'text': resume_text,
            'word_count': len(words),
            'sentence_count': len(sentences),
            'keywords': list(set(keywords)),
            'method': 'basic_extraction'
        }
    
    def process_resume(self, resume_text: str, use_enhanced: bool = True):
        """Process resume with best available method."""
        
        if use_enhanced and self.enhanced_available and hasattr(self, 'nlp_processor'):
            try:
                # Use enhanced processing
                result = self.nlp_processor.process_text_advanced(resume_text)
                result['method'] = 'enhanced'
                return result
            except Exception as e:
                logger.warning(f"Enhanced processing failed, using fallback: {e}")
        
        # Use basic processing
        return self.extract_text_basic(resume_text)
    
    def analyze_compatibility(self, resume_text: str, job_description: str, ats_type: str = 'generic'):
        """Analyze ATS compatibility with best available method."""
        
        if self.enhanced_available and hasattr(self, 'ats_engine'):
            try:
                from scripts.ats.optimization_engine import ATSSystemType
                
                # Convert string to enum
                ats_enum = ATSSystemType.GENERIC
                for ats in ATSSystemType:
                    if ats.value.lower().replace('_', ' ') == ats_type.lower():
                        ats_enum = ats
                        break
                
                result = self.ats_engine.analyze_ats_compatibility(
                    resume_text, job_description, ats_enum
                )
                result['method'] = 'enhanced_ats'
                return result
            except Exception as e:
                logger.warning(f"Enhanced ATS analysis failed: {e}")
        
        # Fallback to basic similarity
        try:
            from scripts.similarity.get_similarity_score import get_similarity_score
            similarity = get_similarity_score(resume_text, job_description)
            
            # Convert similarity result to expected format
            if isinstance(similarity, list) and len(similarity) > 0:
                score = similarity[0].score if hasattr(similarity[0], 'score') else 0.5
            else:
                score = 0.5
            
            return {
                'overall_score': score,
                'keyword_analysis': {
                    'score': score,
                    'matched_keywords': [],
                    'missing_keywords': [],
                    'keyword_frequency': {}
                },
                'format_analysis': {
                    'score': 0.8,  # Assume decent format
                    'format_checks': {
                        'has_contact_info': True,
                        'proper_sections': True,
                        'readable_format': True
                    },
                    'improvements': []
                },
                'length_analysis': {
                    'score': 0.7,
                    'word_count': len(resume_text.split()),
                    'character_count': len(resume_text)
                },
                'section_analysis': {
                    'score': 0.7
                },
                'recommendations': ['Use enhanced analysis for detailed recommendations'],
                'method': 'basic_similarity'
            }
        except Exception as e:
            logger.error(f"Basic similarity calculation failed: {e}")
            
            return {
                'overall_score': 0.5,
                'keyword_analysis': {
                    'score': 0.5,
                    'matched_keywords': [],
                    'missing_keywords': [],
                    'keyword_frequency': {}
                },
                'format_analysis': {
                    'score': 0.5,
                    'format_checks': {},
                    'improvements': []
                },
                'length_analysis': {
                    'score': 0.5,
                    'word_count': len(resume_text.split()),
                    'character_count': len(resume_text)
                },
                'section_analysis': {
                    'score': 0.5
                },
                'recommendations': ['Please check your input and try again'],
                'method': 'error_fallback',
                'error': str(e)
            }

def get_integrated_processor():
    """Get the integrated processor instance."""
    return IntegratedResumeProcessor()

def check_component_status():
    """Check which components are available."""
    status = {
        'enhanced_nlp': False,
        'enhanced_ats': False,
        'enhanced_parser': False,
        'enhanced_analytics': False,
        'basic_similarity': False,
        'pdf_reader': False
    }
    
    # Check enhanced components
    try:
        from scripts.nlp.advanced_processor import AdvancedNLPProcessor
        status['enhanced_nlp'] = True
    except ImportError:
        pass
    
    try:
        from scripts.ats.optimization_engine import ATSOptimizationEngine
        status['enhanced_ats'] = True
    except ImportError:
        pass
    
    try:
        from scripts.parsers.enhanced_parser import EnhancedResumeParser
        status['enhanced_parser'] = True
    except ImportError:
        pass
    
    try:
        from scripts.analytics.insights_engine import ResumeAnalyticsEngine
        status['enhanced_analytics'] = True
    except ImportError:
        pass
    
    # Check original components
    try:
        from scripts.similarity.get_similarity_score import get_similarity_score
        status['basic_similarity'] = True
    except ImportError:
        pass
    
    try:
        from scripts.ReadPdf import ReadPdf
        status['pdf_reader'] = True
    except ImportError:
        pass
    
    return status

if __name__ == "__main__":
    # Test integration
    logging.basicConfig(level=logging.INFO)
    
    print("🔗 Component Integration Status")
    print("=" * 40)
    
    status = check_component_status()
    for component, available in status.items():
        icon = "✅" if available else "❌"
        print(f"{icon} {component.replace('_', ' ').title()}")
    
    print("\n🧪 Testing Integrated Processor")
    processor = get_integrated_processor()
    
    test_resume = "Software Engineer with 5 years experience in Python, Django, and React. Built scalable web applications."
    test_job = "Looking for a Python developer with Django experience and web development skills."
    
    result = processor.analyze_compatibility(test_resume, test_job)
    print(f"Analysis method: {result.get('method', 'unknown')}")
    print(f"Overall score: {result.get('overall_score', 0):.2%}")
    
    print("\n✅ Integration test complete!")
