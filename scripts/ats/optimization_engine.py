"""
ATS-specific optimization engine that mimics real ATS systems.
"""
from typing import Dict, List, Tuple
import re
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ATSSystemType(Enum):
    """Different ATS systems with specific requirements."""
    WORKDAY = "workday"
    TALEO = "taleo"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    BAMBOO_HR = "bamboo_hr"
    GENERIC = "generic"

@dataclass
class ATSCriteria:
    """ATS-specific criteria and weights."""
    keyword_weight: float
    format_weight: float
    length_weight: float
    section_weight: float
    file_format_weight: float

class ATSOptimizationEngine:
    """Engine that optimizes resumes for specific ATS systems."""
    
    def __init__(self):
        self.ats_criteria = {
            ATSSystemType.WORKDAY: ATSCriteria(0.4, 0.2, 0.15, 0.15, 0.1),
            ATSSystemType.TALEO: ATSCriteria(0.45, 0.25, 0.1, 0.15, 0.05),
            ATSSystemType.GREENHOUSE: ATSCriteria(0.35, 0.2, 0.2, 0.2, 0.05),
            ATSSystemType.GENERIC: ATSCriteria(0.4, 0.2, 0.15, 0.15, 0.1)
        }
        
        # ATS-specific parsing patterns
        self.section_patterns = {
            'contact': [r'contact\s*information', r'personal\s*details'],
            'summary': [r'professional\s*summary', r'objective', r'profile'],
            'experience': [r'work\s*experience', r'professional\s*experience', r'employment'],
            'education': [r'education', r'academic\s*background'],
            'skills': [r'skills', r'technical\s*skills', r'competencies'],
            'certifications': [r'certifications', r'licenses', r'credentials']
        }
    
    def analyze_ats_compatibility(self, resume_text: str, job_description: str, 
                                ats_type: ATSSystemType = ATSSystemType.GENERIC) -> Dict:
        """Comprehensive ATS compatibility analysis."""
        
        analysis = {
            'overall_score': 0.0,
            'keyword_analysis': self._analyze_keywords(resume_text, job_description),
            'format_analysis': self._analyze_format(resume_text),
            'length_analysis': self._analyze_length(resume_text),
            'section_analysis': self._analyze_sections(resume_text),
            'recommendations': [],
            'missing_keywords': [],
            'optimization_suggestions': []
        }
        
        # Calculate weighted score based on ATS type
        criteria = self.ats_criteria[ats_type]
        
        keyword_score = analysis['keyword_analysis']['score']
        format_score = analysis['format_analysis']['score']
        length_score = analysis['length_analysis']['score']
        section_score = analysis['section_analysis']['score']
        
        analysis['overall_score'] = (
            keyword_score * criteria.keyword_weight +
            format_score * criteria.format_weight +
            length_score * criteria.length_weight +
            section_score * criteria.section_weight
        )
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis, ats_type)
        
        return analysis
    
    def _analyze_keywords(self, resume_text: str, job_description: str) -> Dict:
        """Analyze keyword matching for ATS systems."""
        # Extract keywords from job description
        job_keywords = self._extract_job_keywords(job_description)
        
        # Check which keywords appear in resume
        resume_lower = resume_text.lower()
        matched_keywords = []
        missing_keywords = []
        
        for keyword in job_keywords:
            if keyword.lower() in resume_lower:
                # Check for exact match vs partial match
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\b', resume_lower):
                    matched_keywords.append({
                        'keyword': keyword,
                        'match_type': 'exact',
                        'frequency': len(re.findall(r'\b' + re.escape(keyword.lower()) + r'\b', resume_lower))
                    })
                else:
                    matched_keywords.append({
                        'keyword': keyword,
                        'match_type': 'partial',
                        'frequency': resume_lower.count(keyword.lower())
                    })
            else:
                missing_keywords.append(keyword)
        
        keyword_coverage = len(matched_keywords) / len(job_keywords) if job_keywords else 0
        
        return {
            'score': min(keyword_coverage * 1.2, 1.0),  # Slight boost for good coverage
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords,
            'total_job_keywords': len(job_keywords),
            'keyword_density': self._calculate_keyword_density(resume_text, matched_keywords)
        }
    
    def _extract_job_keywords(self, job_description: str) -> List[str]:
        """Extract important keywords from job description."""
        # Remove common stop words and extract meaningful terms
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        
        try:
            stop_words = set(stopwords.words('english'))
        except LookupError:
            nltk.download('stopwords')
            nltk.download('punkt')
            stop_words = set(stopwords.words('english'))
        
        # Add job-specific stop words
        job_stop_words = {'experience', 'skills', 'requirements', 'qualifications', 
                         'preferred', 'required', 'must', 'should', 'years', 'degree'}
        stop_words.update(job_stop_words)
        
        words = word_tokenize(job_description.lower())
        
        # Extract multi-word technical terms
        keywords = []
        
        # Single words (3+ chars, not stop words, alphanumeric)
        for word in words:
            if (len(word) >= 3 and 
                word not in stop_words and 
                word.isalnum() and 
                not word.isdigit()):
                keywords.append(word)
        
        # Extract common technical phrases
        technical_phrases = [
            r'\b(?:machine learning|data science|artificial intelligence)\b',
            r'\b(?:full stack|front end|back end)\b',
            r'\b(?:project management|agile development)\b',
            r'\b(?:cloud computing|database design)\b',
            r'\b(?:user experience|user interface)\b'
        ]
        
        for pattern in technical_phrases:
            matches = re.findall(pattern, job_description.lower())
            keywords.extend(matches)
        
        # Remove duplicates and return most frequent/important
        from collections import Counter
        keyword_counts = Counter(keywords)
        
        # Return top keywords (limit to prevent keyword stuffing)
        return [word for word, count in keyword_counts.most_common(50)]
    
    def _analyze_format(self, resume_text: str) -> Dict:
        """Analyze resume format for ATS compatibility."""
        issues = []
        score = 1.0
        
        # Check for problematic formatting
        if len(re.findall(r'\t', resume_text)) > 10:
            issues.append("Excessive use of tabs - use spaces instead")
            score -= 0.1
        
        # Check for special characters that might confuse ATS
        problematic_chars = ['•', '→', '★', '◆', '▪', '▫']
        for char in problematic_chars:
            if char in resume_text:
                issues.append(f"Contains special character '{char}' - use standard bullets")
                score -= 0.05
        
        # Check section headers
        section_headers_found = 0
        for section_type, patterns in self.section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, resume_text, re.IGNORECASE):
                    section_headers_found += 1
                    break
        
        if section_headers_found < 4:
            issues.append("Missing standard section headers")
            score -= 0.2
        
        # Check for consistent formatting
        lines = resume_text.split('\n')
        inconsistent_spacing = sum(1 for line in lines if line.strip() == '') / len(lines)
        if inconsistent_spacing > 0.3:
            issues.append("Inconsistent spacing between sections")
            score -= 0.1
        
        return {
            'score': max(score, 0.0),
            'issues': issues,
            'section_headers_found': section_headers_found
        }
    
    def _analyze_length(self, resume_text: str) -> Dict:
        """Analyze resume length for ATS optimization."""
        word_count = len(resume_text.split())
        char_count = len(resume_text)
        
        # Optimal ranges for different experience levels
        optimal_ranges = {
            'entry_level': (300, 500),
            'mid_level': (400, 700),
            'senior_level': (500, 800),
            'executive': (600, 1000)
        }
        
        # Determine experience level from content
        experience_level = self._estimate_experience_level(resume_text)
        optimal_min, optimal_max = optimal_ranges[experience_level]
        
        score = 1.0
        issues = []
        
        if word_count < optimal_min:
            score = word_count / optimal_min
            issues.append(f"Resume too short ({word_count} words). Add more details about experience and achievements.")
        elif word_count > optimal_max:
            score = optimal_max / word_count
            issues.append(f"Resume too long ({word_count} words). Consider condensing to {optimal_max} words or less.")
        
        return {
            'score': score,
            'word_count': word_count,
            'char_count': char_count,
            'estimated_experience_level': experience_level,
            'optimal_range': optimal_ranges[experience_level],
            'issues': issues
        }
    
    def _generate_recommendations(self, analysis: Dict, ats_type: ATSSystemType) -> List[str]:
        """Generate specific recommendations for ATS optimization."""
        recommendations = []
        
        # Keyword recommendations
        if analysis['keyword_analysis']['score'] < 0.6:
            missing = analysis['keyword_analysis']['missing_keywords'][:5]
            recommendations.append(
                f"Add these missing keywords naturally throughout your resume: {', '.join(missing)}"
            )
        
        # Format recommendations
        if analysis['format_analysis']['score'] < 0.8:
            recommendations.extend([
                "Use standard section headers: Summary, Experience, Education, Skills",
                "Use simple bullet points (•) instead of special characters",
                "Ensure consistent spacing between sections"
            ])
        
        # Length recommendations
        if analysis['length_analysis']['score'] < 0.8:
            recommendations.append(analysis['length_analysis']['issues'][0])
        
        # ATS-specific recommendations
        if ats_type == ATSSystemType.TALEO:
            recommendations.append("For Taleo systems: Place keywords in the first 1/3 of your resume")
        elif ats_type == ATSSystemType.WORKDAY:
            recommendations.append("For Workday systems: Use exact keyword matches from job description")
        
        return recommendations
    
    def _analyze_sections(self, resume_text: str) -> Dict:
        """Analyze presence and organization of resume sections."""
        sections_found = {}
        score = 0.0
        
        for section_type, patterns in self.section_patterns.items():
            found = False
            for pattern in patterns:
                if re.search(pattern, resume_text, re.IGNORECASE):
                    found = True
                    break
            sections_found[section_type] = found
            if found:
                score += 1
        
        score = score / len(self.section_patterns)
        
        return {
            'score': score,
            'sections_found': sections_found,
            'missing_sections': [k for k, v in sections_found.items() if not v]
        }
    
    def _calculate_keyword_density(self, resume_text: str, matched_keywords: List[Dict]) -> float:
        """Calculate keyword density (keywords per 100 words)."""
        total_words = len(resume_text.split())
        if total_words == 0:
            return 0.0
        
        total_keyword_frequency = sum(kw['frequency'] for kw in matched_keywords)
        return (total_keyword_frequency / total_words) * 100
    
    def _estimate_experience_level(self, resume_text: str) -> str:
        """Estimate experience level from resume content."""
        # Look for years of experience
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience'
        ]
        
        years = []
        for pattern in year_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            years.extend([int(m) for m in matches])
        
        if years:
            max_years = max(years)
            if max_years <= 2:
                return 'entry_level'
            elif max_years <= 5:
                return 'mid_level'
            elif max_years <= 10:
                return 'senior_level'
            else:
                return 'executive'
        
        # Fallback: estimate from content complexity and roles
        text_lower = resume_text.lower()
        senior_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
        executive_indicators = ['ceo', 'cto', 'vp', 'vice president', 'executive']
        
        if any(indicator in text_lower for indicator in executive_indicators):
            return 'executive'
        elif any(indicator in text_lower for indicator in senior_indicators):
            return 'senior_level'
        else:
            # Check word count as proxy for experience
            word_count = len(resume_text.split())
            if word_count > 600:
                return 'senior_level'
            elif word_count > 400:
                return 'mid_level'
            else:
                return 'entry_level'
