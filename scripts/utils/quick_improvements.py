"""
Quick improvements script - immediate enhancements to existing code.
"""

# 1. Better keyword extraction
def extract_job_keywords_improved(job_description: str) -> List[Dict[str, Any]]:
    """Improved keyword extraction with weights and categories."""
    import re
    from collections import Counter
    
    # Define keyword categories with weights
    keyword_categories = {
        'must_have': {
            'weight': 1.0,
            'patterns': [r'required?:?\s*([^.]+)', r'must\s+have:?\s*([^.]+)']
        },
        'preferred': {
            'weight': 0.7,
            'patterns': [r'preferred?:?\s*([^.]+)', r'nice\s+to\s+have:?\s*([^.]+)']
        },
        'technical': {
            'weight': 0.9,
            'patterns': [r'\b(python|java|javascript|react|angular|aws|docker)\b']
        }
    }
    
    extracted_keywords = []
    
    for category, config in keyword_categories.items():
        for pattern in config['patterns']:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            for match in matches:
                keywords = [kw.strip() for kw in match.split(',') if kw.strip()]
                for keyword in keywords:
                    extracted_keywords.append({
                        'keyword': keyword,
                        'category': category,
                        'weight': config['weight'],
                        'importance': 'high' if config['weight'] > 0.8 else 'medium'
                    })
    
    return extracted_keywords

# 2. Better similarity calculation
def calculate_weighted_similarity(resume_text: str, job_keywords: List[Dict]) -> float:
    """Calculate similarity with keyword weights and positions."""
    total_weight = sum(kw['weight'] for kw in job_keywords)
    matched_weight = 0
    
    resume_lower = resume_text.lower()
    
    for keyword_data in job_keywords:
        keyword = keyword_data['keyword'].lower()
        weight = keyword_data['weight']
        
        # Check for keyword presence
        if keyword in resume_lower:
            # Bonus for early appearance (first 1/3 of resume)
            early_position = len(resume_text) // 3
            if keyword in resume_text[:early_position].lower():
                weight *= 1.2
            
            # Bonus for exact match vs partial
            if re.search(r'\b' + re.escape(keyword) + r'\b', resume_lower):
                weight *= 1.1
            
            matched_weight += weight
    
    return min(matched_weight / total_weight, 1.0) if total_weight > 0 else 0

# 3. Better section detection
def detect_resume_sections(text: str) -> Dict[str, str]:
    """Improved section detection with better patterns."""
    sections = {}
    
    section_patterns = {
        'summary': [
            r'(?:professional\s+)?summary',
            r'profile',
            r'objective',
            r'about\s+me'
        ],
        'experience': [
            r'(?:work\s+|professional\s+)?experience',
            r'employment\s+history',
            r'career\s+history'
        ],
        'education': [
            r'education',
            r'academic\s+background',
            r'qualifications'
        ],
        'skills': [
            r'(?:technical\s+)?skills',
            r'competencies',
            r'technologies',
            r'expertise'
        ]
    }
    
    text_lines = text.split('\n')
    current_section = None
    section_content = []
    
    for line in text_lines:
        line_lower = line.lower().strip()
        
        # Check if line is a section header
        found_section = None
        for section_name, patterns in section_patterns.items():
            for pattern in patterns:
                if re.match(f'^{pattern}\\s*:?\\s*$', line_lower):
                    found_section = section_name
                    break
            if found_section:
                break
        
        if found_section:
            # Save previous section
            if current_section and section_content:
                sections[current_section] = '\n'.join(section_content)
            
            # Start new section
            current_section = found_section
            section_content = []
        elif current_section:
            section_content.append(line)
    
    # Save last section
    if current_section and section_content:
        sections[current_section] = '\n'.join(section_content)
    
    return sections

# 4. Better achievements extraction
def extract_achievements(experience_text: str) -> List[Dict[str, Any]]:
    """Extract quantified achievements from experience descriptions."""
    achievement_patterns = [
        r'(?:increased|improved|enhanced|boosted|grew)\s+([^.]+?)(?:by\s+)?(\d+(?:\.\d+)?%)',
        r'(?:reduced|decreased|cut|lowered)\s+([^.]+?)(?:by\s+)?(\d+(?:\.\d+)?%)',
        r'(?:managed|led|supervised)\s+(?:a\s+)?(?:team\s+of\s+)?(\d+)\s+(?:people|developers|engineers)',
        r'(?:generated|created|delivered)\s+\$?(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:million|billion|k|m)?',
        r'(?:processed|handled)\s+(\d+(?:,\d+)*)\s+(?:requests|transactions|users)'
    ]
    
    achievements = []
    
    for pattern in achievement_patterns:
        matches = re.finditer(pattern, experience_text, re.IGNORECASE)
        for match in matches:
            achievement = {
                'text': match.group(0),
                'metric': match.groups()[-1],  # Last group is usually the number
                'context': match.groups()[0] if len(match.groups()) > 1 else '',
                'type': 'quantified'
            }
            achievements.append(achievement)
    
    return achievements

# 5. Quick UI improvements for existing Streamlit app
def add_progress_indicators():
    """Add progress indicators to show optimization progress."""
    
    progress_areas = {
        'Keywords': 0.7,
        'Format': 0.9,
        'Length': 0.8,
        'ATS Compatibility': 0.75
    }
    
    st.subheader("📊 Optimization Progress")
    
    for area, score in progress_areas.items():
        color = "green" if score >= 0.8 else "orange" if score >= 0.6 else "red"
        st.metric(
            area,
            f"{score:.1%}",
            delta=f"+{(score-0.6):.1%}" if score > 0.6 else None,
            help=f"Target: 80%+ for optimal ATS performance"
        )
        
        # Progress bar
        st.progress(score)

# 6. Better error messages and user guidance
def provide_specific_feedback(analysis_results: Dict) -> List[str]:
    """Provide specific, actionable feedback instead of generic messages."""
    
    feedback = []
    
    keyword_score = analysis_results.get('keyword_score', 0)
    if keyword_score < 0.6:
        missing_keywords = analysis_results.get('missing_keywords', [])[:3]
        feedback.append(
            f"❗ Add these key terms from the job posting: {', '.join(missing_keywords)}. "
            f"Try including them in your skills section or experience descriptions."
        )
    
    format_score = analysis_results.get('format_score', 0)
    if format_score < 0.8:
        feedback.append(
            "📝 Format improvements needed: Use clear section headers like 'EXPERIENCE', "
            "'EDUCATION', 'SKILLS'. Avoid fancy formatting, tables, or graphics."
        )
    
    length = analysis_results.get('word_count', 0)
    if length < 300:
        feedback.append(
            "📏 Your resume is too short. Add more details about your achievements, "
            "responsibilities, and technical projects. Aim for 400-600 words."
        )
    elif length > 800:
        feedback.append(
            "📏 Your resume is too long. Focus on the most relevant experiences and "
            "achievements. Remove older or less relevant positions."
        )
    
    return feedback

print("Quick improvements ready! These can be integrated into existing code for immediate better results.")
