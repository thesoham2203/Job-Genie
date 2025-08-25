"""
Enhanced NLP Pipeline for better resume-job matching accuracy.
"""
import spacy
import torch
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class AdvancedNLPProcessor:
    """Advanced NLP processor for better semantic understanding."""
    
    def __init__(self):
        # Load multiple models for different aspects
        self.nlp = spacy.load("en_core_web_trf")  # Transformer model for better accuracy
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.domain_model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        
        # Domain-specific skill embeddings
        self.skill_embeddings = self._load_skill_embeddings()
        
    def extract_skills_advanced(self, text: str) -> List[Dict]:
        """Extract skills with confidence scores and categorization."""
        doc = self.nlp(text)
        
        skills = []
        
        # Technical skills extraction
        tech_patterns = [
            # Programming languages
            r'\b(?:Python|Java|JavaScript|C\+\+|C#|Ruby|Go|Rust|Kotlin|Swift)\b',
            # Frameworks
            r'\b(?:React|Angular|Vue|Django|Flask|Spring|Laravel|Express)\b',
            # Databases
            r'\b(?:MySQL|PostgreSQL|MongoDB|Redis|Elasticsearch|Oracle)\b',
            # Cloud platforms
            r'\b(?:AWS|Azure|GCP|Docker|Kubernetes|Terraform)\b',
            # Tools
            r'\b(?:Git|Jenkins|JIRA|Confluence|Slack|Figma)\b'
        ]
        
        # Extract named entities and categorize
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PRODUCT', 'GPE']:  # Organizations, products, locations
                skills.append({
                    'text': ent.text,
                    'category': self._categorize_skill(ent.text),
                    'confidence': ent._.confidence if hasattr(ent._, 'confidence') else 0.8,
                    'context': self._get_context(doc, ent.start, ent.end)
                })
        
        # Extract skills using pattern matching
        import re
        for pattern in tech_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                skills.append({
                    'text': match.group(),
                    'category': 'technical',
                    'confidence': 0.9,
                    'context': self._get_context_around_match(text, match)
                })
        
        return self._deduplicate_skills(skills)
    
    def extract_experience_metrics(self, text: str) -> Dict:
        """Extract quantifiable experience metrics."""
        doc = self.nlp(text)
        
        metrics = {
            'years_experience': [],
            'team_size': [],
            'project_impact': [],
            'certifications': [],
            'education_level': None
        }
        
        # Years of experience patterns
        import re
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in\s*\w+',
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics['years_experience'].extend([int(m) for m in matches])
        
        # Team size patterns
        team_patterns = [
            r'(?:led|managed|supervised)\s*(?:a\s*)?team\s*of\s*(\d+)',
            r'(\d+)\s*(?:person|member|developer)s?\s*team',
        ]
        
        for pattern in team_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics['team_size'].extend([int(m) for m in matches])
        
        # Project impact (numbers, percentages, monetary values)
        impact_patterns = [
            r'(\d+(?:\.\d+)?%)\s*(?:increase|improvement|reduction)',
            r'\$(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|billion|k|m|b)?',
            r'(\d+(?:,\d+)*)\s*(?:users|customers|clients)',
        ]
        
        for pattern in impact_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics['project_impact'].extend(matches)
        
        return metrics
    
    def semantic_similarity_advanced(self, resume_text: str, job_text: str) -> Dict:
        """Calculate advanced semantic similarity with multiple dimensions."""
        
        # 1. Overall semantic similarity
        resume_embedding = self.sentence_model.encode([resume_text])
        job_embedding = self.sentence_model.encode([job_text])
        overall_similarity = np.dot(resume_embedding, job_embedding.T)[0][0]
        
        # 2. Skills-specific similarity
        resume_skills = self.extract_skills_advanced(resume_text)
        job_skills = self.extract_skills_advanced(job_text)
        skills_similarity = self._calculate_skills_similarity(resume_skills, job_skills)
        
        # 3. Experience level matching
        resume_metrics = self.extract_experience_metrics(resume_text)
        job_metrics = self.extract_experience_metrics(job_text)
        experience_match = self._calculate_experience_match(resume_metrics, job_metrics)
        
        # 4. Industry/domain similarity
        domain_similarity = self._calculate_domain_similarity(resume_text, job_text)
        
        # 5. Role responsibility matching
        responsibility_match = self._calculate_responsibility_match(resume_text, job_text)
        
        return {
            'overall_similarity': float(overall_similarity),
            'skills_similarity': skills_similarity,
            'experience_match': experience_match,
            'domain_similarity': domain_similarity,
            'responsibility_match': responsibility_match,
            'composite_score': self._calculate_composite_score({
                'overall': overall_similarity,
                'skills': skills_similarity,
                'experience': experience_match,
                'domain': domain_similarity,
                'responsibility': responsibility_match
            })
        }
    
    def _categorize_skill(self, skill: str) -> str:
        """Categorize skills into technical, soft, domain-specific, etc."""
        skill_categories = {
            'technical': ['python', 'java', 'javascript', 'react', 'angular', 'sql', 'aws'],
            'soft': ['leadership', 'communication', 'teamwork', 'problem-solving'],
            'domain': ['finance', 'healthcare', 'retail', 'manufacturing'],
            'tools': ['git', 'jira', 'confluence', 'slack', 'figma'],
            'methodologies': ['agile', 'scrum', 'kanban', 'devops', 'ci/cd']
        }
        
        skill_lower = skill.lower()
        for category, keywords in skill_categories.items():
            if any(keyword in skill_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _calculate_skills_similarity(self, resume_skills: List[Dict], job_skills: List[Dict]) -> float:
        """Calculate similarity between skill sets."""
        if not resume_skills or not job_skills:
            return 0.0
        
        resume_skill_texts = [skill['text'].lower() for skill in resume_skills]
        job_skill_texts = [skill['text'].lower() for skill in job_skills]
        
        # Exact matches
        exact_matches = len(set(resume_skill_texts) & set(job_skill_texts))
        
        # Semantic matches using embeddings
        semantic_matches = 0
        for job_skill in job_skill_texts:
            job_embedding = self.sentence_model.encode([job_skill])
            for resume_skill in resume_skill_texts:
                resume_embedding = self.sentence_model.encode([resume_skill])
                similarity = np.dot(job_embedding, resume_embedding.T)[0][0]
                if similarity > 0.8:  # High semantic similarity threshold
                    semantic_matches += 1
                    break
        
        total_job_skills = len(job_skill_texts)
        skill_coverage = (exact_matches + semantic_matches) / total_job_skills
        
        return min(skill_coverage, 1.0)
    
    def _calculate_composite_score(self, scores: Dict) -> float:
        """Calculate weighted composite score."""
        weights = {
            'overall': 0.2,
            'skills': 0.35,      # Most important for ATS
            'experience': 0.25,   # Important for role fit
            'domain': 0.1,
            'responsibility': 0.1
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in weights)
        return min(weighted_score, 1.0)
