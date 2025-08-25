"""
Enhanced Resume Matcher - Main Application with Integrated Features
"""
import json
import os
import logging
from typing import List, Dict, Any, Optional
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

# Import our enhanced modules
try:
    from scripts.integration_bridge import get_integrated_processor, check_component_status
    from scripts.utils.quick_improvements import (
        extract_job_keywords_improved, 
        calculate_weighted_similarity,
        provide_specific_feedback
    )
    from scripts.utils.security import SecurityValidator, sanitize_text_input
    from scripts.utils.config import config
    
    # Check what components are available
    component_status = check_component_status()
    
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedResumeMatcherApp:
    """Enhanced Resume Matcher Application with all new features integrated."""
    
    def __init__(self):
        self.setup_page_config()
        self.nlp_processor = None
        self.ats_engine = None
        self.parser = None
        self.analytics_engine = None
        self.initialize_components()
    
    def setup_page_config(self):
        """Setup Streamlit page configuration."""
        st.set_page_config(
            page_title="Job Genie - AI Resume Optimizer",
            page_icon="🎯",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Custom CSS to maintain theme while enhancing UI
        st.markdown("""
        <style>
        /* Main theme colors */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
        }
        
        .improvement-suggestion {
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #28a745;
        }
        
        .warning-card {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #f39c12;
        }
        
        .error-card {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #e74c3c;
        }
        
        .success-card {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #28a745;
        }
        
        /* Score indicators */
        .score-excellent { color: #28a745; font-weight: bold; }
        .score-good { color: #ffc107; font-weight: bold; }
        .score-poor { color: #dc3545; font-weight: bold; }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Custom buttons */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Progress bars */
        .stProgress .st-bo {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: #f8f9fa;
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1rem;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_components(self):
        """Initialize all processing components."""
        try:
            if 'components_initialized' not in st.session_state:
                with st.spinner("🚀 Initializing AI components..."):
                    self.nlp_processor = AdvancedNLPProcessor()
                    self.ats_engine = ATSOptimizationEngine()
                    self.parser = EnhancedResumeParser()
                    self.analytics_engine = ResumeAnalyticsEngine()
                st.session_state.components_initialized = True
                st.success("✅ All components loaded successfully!")
            else:
                self.nlp_processor = AdvancedNLPProcessor()
                self.ats_engine = ATSOptimizationEngine()
                self.parser = EnhancedResumeParser()
                self.analytics_engine = ResumeAnalyticsEngine()
        except Exception as e:
            st.error(f"❌ Failed to initialize components: {str(e)}")
            st.info("💡 Using fallback mode with basic functionality")
    
    def render_main_header(self):
        """Render the main application header."""
        st.markdown("""
        <div class="main-header">
            <h1>🎯 Job Genie - AI Resume Optimizer</h1>
            <p>Transform your resume with AI-powered optimization for ATS systems</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render enhanced sidebar with configuration options."""
        with st.sidebar:
            st.markdown("### ⚙️ Configuration")
            
            # ATS System Selection
            ats_type = st.selectbox(
                "🤖 Target ATS System",
                options=[ats.value.replace('_', ' ').title() for ats in ATSSystemType],
                help="Select the ATS system if known for optimized results"
            )
            
            # Analysis Depth
            analysis_depth = st.radio(
                "🔍 Analysis Depth",
                ["Quick Scan (30s)", "Deep Analysis (2-3 min)"],
                help="Deep analysis provides more comprehensive insights"
            )
            
            # File Upload Method
            upload_method = st.radio(
                "📄 Input Method",
                ["Text Input", "File Upload"],
                help="Choose how to provide your resume"
            )
            
            st.markdown("---")
            
            # Quick Tips
            st.markdown("### 💡 Quick Tips")
            tips = [
                "Use keywords from the job description",
                "Quantify your achievements with numbers",
                "Keep formatting simple and clean",
                "Save as .docx or .pdf format",
                "Proofread for spelling and grammar"
            ]
            
            for tip in tips:
                st.markdown(f"• {tip}")
            
            st.markdown("---")
            
            # Help & Support
            st.markdown("### 📞 Support")
            if st.button("🆘 Get Help"):
                st.info("📧 Contact: support@jobgenie.ai")
            
            if st.button("📊 View Analytics Dashboard"):
                st.session_state.show_analytics = True
            
            return ats_type, analysis_depth, upload_method
    
    def render_input_section(self, upload_method: str):
        """Render the input section for resume and job description."""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📄 Your Resume")
            
            resume_text = ""
            resume_file = None
            
            if upload_method == "File Upload":
                resume_file = st.file_uploader(
                    "Upload your resume",
                    type=['pdf', 'docx', 'txt'],
                    help="Supported formats: PDF, DOCX, TXT"
                )
                
                if resume_file:
                    try:
                        # Use enhanced parser
                        with st.spinner("📖 Parsing your resume..."):
                            parsed_data = self.parser.parse_resume(
                                resume_file, 
                                resume_file.type.split('/')[-1]
                            )
                            resume_text = parsed_data.get('raw_text', '')
                            
                            # Show parsing success
                            st.success(f"✅ Parsed {len(resume_text.split())} words from your resume")
                            
                            # Store parsed data for later use
                            st.session_state.parsed_resume_data = parsed_data
                    
                    except Exception as e:
                        st.error(f"❌ Failed to parse resume: {str(e)}")
                        st.info("💡 Try using text input instead")
            
            else:  # Text Input
                resume_text = st.text_area(
                    "Paste your resume text here:",
                    height=300,
                    placeholder="Copy and paste your complete resume here...",
                    help="Include all sections: contact info, summary, experience, education, skills"
                )
            
            # Resume preview
            if resume_text:
                with st.expander("👀 Resume Preview", expanded=False):
                    st.text(resume_text[:500] + "..." if len(resume_text) > 500 else resume_text)
        
        with col2:
            st.markdown("### 💼 Job Description")
            
            job_description = st.text_area(
                "Paste the job description here:",
                height=300,
                placeholder="Copy and paste the complete job description here...",
                help="Include requirements, responsibilities, and preferred qualifications"
            )
            
            # Job description preview
            if job_description:
                with st.expander("👀 Job Description Preview", expanded=False):
                    st.text(job_description[:500] + "..." if len(job_description) > 500 else job_description)
        
        return resume_text, job_description, resume_file
    
    def perform_analysis(self, resume_text: str, job_description: str, 
                        ats_type: str, analysis_depth: str):
        """Perform comprehensive resume analysis."""
        
        if not resume_text or not job_description:
            st.warning("⚠️ Please provide both resume text and job description")
            return None
        
        # Sanitize inputs
        resume_text = sanitize_text_input(resume_text)
        job_description = sanitize_text_input(job_description)
        
        # Convert ATS type
        ats_enum = ATSSystemType.GENERIC
        for ats in ATSSystemType:
            if ats.value.replace('_', ' ').title() == ats_type:
                ats_enum = ats
                break
        
        analysis_results = {}
        
        with st.spinner("🔍 Analyzing your resume..."):
            # Progress bar for user feedback
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: ATS Analysis (40%)
            status_text.text("Analyzing ATS compatibility...")
            progress_bar.progress(0.2)
            
            ats_analysis = self.ats_engine.analyze_ats_compatibility(
                resume_text, job_description, ats_enum
            )
            progress_bar.progress(0.4)
            
            # Step 2: Advanced NLP Analysis (60% - only for deep analysis)
            if "Deep Analysis" in analysis_depth:
                status_text.text("Performing semantic analysis...")
                nlp_analysis = self.nlp_processor.semantic_similarity_advanced(
                    resume_text, job_description
                )
                progress_bar.progress(0.7)
            else:
                nlp_analysis = None
            
            # Step 3: Enhanced keyword analysis (80%)
            status_text.text("Extracting keywords...")
            enhanced_keywords = extract_job_keywords_improved(job_description)
            weighted_similarity = calculate_weighted_similarity(resume_text, enhanced_keywords)
            progress_bar.progress(0.9)
            
            # Step 4: Generate recommendations (100%)
            status_text.text("Generating recommendations...")
            specific_feedback = provide_specific_feedback({
                'keyword_score': ats_analysis['keyword_analysis']['score'],
                'format_score': ats_analysis['format_analysis']['score'],
                'word_count': ats_analysis['length_analysis']['word_count'],
                'missing_keywords': ats_analysis['keyword_analysis']['missing_keywords']
            })
            progress_bar.progress(1.0)
            
            status_text.text("✅ Analysis complete!")
        
        # Compile results
        analysis_results = {
            'ats_analysis': ats_analysis,
            'nlp_analysis': nlp_analysis,
            'enhanced_keywords': enhanced_keywords,
            'weighted_similarity': weighted_similarity,
            'specific_feedback': specific_feedback,
            'ats_type': ats_type
        }
        
        # Track analytics
        if self.analytics_engine:
            self.analytics_engine.track_analysis({
                'overall_score': ats_analysis['overall_score'],
                'keyword_score': ats_analysis['keyword_analysis']['score'],
                'format_score': ats_analysis['format_analysis']['score'],
                'length_score': ats_analysis['length_analysis']['score'],
                'ats_type': ats_type.lower()
            })
        
        return analysis_results
    
    def render_results_dashboard(self, analysis_results: Dict[str, Any]):
        """Render comprehensive results dashboard."""
        
        ats_analysis = analysis_results['ats_analysis']
        nlp_analysis = analysis_results.get('nlp_analysis')
        
        # Overall Score Header
        st.markdown("## 📊 Analysis Results")
        
        # Score metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            overall_score = ats_analysis['overall_score']
            score_class = self.get_score_class(overall_score)
            delta = f"+{(overall_score - 0.7):.1%}" if overall_score > 0.7 else None
            st.metric(
                "🎯 Overall Score",
                f"{overall_score:.1%}",
                delta=delta,
                help="Combined ATS compatibility score"
            )
        
        with col2:
            keyword_score = ats_analysis['keyword_analysis']['score']
            st.metric(
                "🔑 Keyword Match",
                f"{keyword_score:.1%}",
                delta=f"{(keyword_score - 0.6):.1%}" if keyword_score > 0.6 else None,
                help="How well your resume matches job keywords"
            )
        
        with col3:
            format_score = ats_analysis['format_analysis']['score']
            st.metric(
                "📝 Format Score",
                f"{format_score:.1%}",
                delta=f"{(format_score - 0.8):.1%}" if format_score > 0.8 else None,
                help="ATS-friendly formatting score"
            )
        
        with col4:
            if nlp_analysis:
                semantic_score = nlp_analysis['composite_score']
                st.metric(
                    "🧠 Semantic Match",
                    f"{semantic_score:.1%}",
                    delta=f"{(semantic_score - 0.7):.1%}" if semantic_score > 0.7 else None,
                    help="AI-powered semantic similarity"
                )
            else:
                weighted_sim = analysis_results['weighted_similarity']
                st.metric(
                    "⚖️ Weighted Match",
                    f"{weighted_sim:.1%}",
                    help="Importance-weighted keyword matching"
                )
        
        # Score visualization
        self.render_score_breakdown(analysis_results)
        
        # Detailed analysis tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🎯 Keywords", "📝 Format", "📏 Length", "💡 Recommendations", "📈 Insights"
        ])
        
        with tab1:
            self.render_keyword_analysis(ats_analysis['keyword_analysis'], analysis_results['enhanced_keywords'])
        
        with tab2:
            self.render_format_analysis(ats_analysis['format_analysis'])
        
        with tab3:
            self.render_length_analysis(ats_analysis['length_analysis'])
        
        with tab4:
            self.render_recommendations(analysis_results['specific_feedback'], ats_analysis['recommendations'])
        
        with tab5:
            if nlp_analysis:
                self.render_advanced_insights(nlp_analysis)
            else:
                st.info("💡 Enable 'Deep Analysis' for advanced semantic insights")
    
    def render_score_breakdown(self, analysis_results: Dict[str, Any]):
        """Render interactive score breakdown visualization."""
        
        st.markdown("### 📈 Score Breakdown")
        
        ats_analysis = analysis_results['ats_analysis']
        nlp_analysis = analysis_results.get('nlp_analysis')
        
        # Prepare data for radar chart
        categories = ['Keywords', 'Format', 'Length', 'Sections']
        scores = [
            ats_analysis['keyword_analysis']['score'],
            ats_analysis['format_analysis']['score'],
            ats_analysis['length_analysis']['score'],
            ats_analysis['section_analysis']['score']
        ]
        
        if nlp_analysis:
            categories.extend(['Skills Match', 'Experience', 'Domain Fit'])
            scores.extend([
                nlp_analysis['skills_similarity'],
                nlp_analysis['experience_match'],
                nlp_analysis['domain_similarity']
            ])
        
        # Create radar chart
        fig = go.Figure()
        
        # Add current scores
        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=categories,
            fill='toself',
            name='Your Resume',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.2)'
        ))
        
        # Add target line
        target_scores = [0.8] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=target_scores,
            theta=categories,
            fill='toself',
            name='Target Score',
            line=dict(color='rgba(231, 76, 60, 0.8)', dash='dash'),
            fillcolor='rgba(231, 76, 60, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickformat='.0%'
                )
            ),
            showlegend=True,
            title="Resume Optimization Radar",
            font=dict(size=12),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def get_score_class(self, score: float) -> str:
        """Get CSS class for score styling."""
        if score >= 0.8:
            return "score-excellent"
        elif score >= 0.6:
            return "score-good"
        else:
            return "score-poor"
    
    def render_keyword_analysis(self, keyword_analysis: Dict[str, Any], enhanced_keywords: Dict[str, Any]):
        """Render detailed keyword analysis."""
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ✅ Matched Keywords")
            
            if keyword_analysis['matched_keywords']:
                # Create keyword importance chart
                matched_df = pd.DataFrame([
                    {
                        'keyword': kw,
                        'importance': enhanced_keywords['keyword_weights'].get(kw, 1),
                        'frequency': keyword_analysis['keyword_frequency'].get(kw, 0)
                    }
                    for kw in keyword_analysis['matched_keywords']
                ])
                
                # Sort by importance
                matched_df = matched_df.sort_values('importance', ascending=True)
                
                fig = px.bar(
                    matched_df,
                    x='importance',
                    y='keyword',
                    color='frequency',
                    orientation='h',
                    title="Matched Keywords by Importance",
                    color_continuous_scale='Viridis',
                    height=300
                )
                
                fig.update_layout(
                    xaxis_title="Importance Weight",
                    yaxis_title="Keywords",
                    font=dict(size=10)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show keyword list with context
                for kw in keyword_analysis['matched_keywords'][:10]:
                    importance = enhanced_keywords['keyword_weights'].get(kw, 1)
                    freq = keyword_analysis['keyword_frequency'].get(kw, 0)
                    
                    if importance > 2:
                        st.markdown(f"🔥 **{kw}** (Critical - appears {freq}x)")
                    elif importance > 1.5:
                        st.markdown(f"⭐ **{kw}** (Important - appears {freq}x)")
                    else:
                        st.markdown(f"✓ {kw} (appears {freq}x)")
            else:
                st.warning("No matching keywords found!")
        
        with col2:
            st.markdown("#### ❌ Missing Keywords")
            
            if keyword_analysis['missing_keywords']:
                missing_df = pd.DataFrame([
                    {
                        'keyword': kw,
                        'importance': enhanced_keywords['keyword_weights'].get(kw, 1),
                        'category': enhanced_keywords.get('category_keywords', {}).get(kw, 'General')
                    }
                    for kw in keyword_analysis['missing_keywords'][:20]
                ])
                
                # Group by category
                category_counts = missing_df['category'].value_counts()
                
                fig = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Missing Keywords by Category",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show top missing keywords
                missing_sorted = sorted(
                    keyword_analysis['missing_keywords'][:15],
                    key=lambda x: enhanced_keywords['keyword_weights'].get(x, 1),
                    reverse=True
                )
                
                for kw in missing_sorted:
                    importance = enhanced_keywords['keyword_weights'].get(kw, 1)
                    category = enhanced_keywords.get('category_keywords', {}).get(kw, 'General')
                    
                    if importance > 2:
                        st.markdown(f"🚨 **{kw}** ({category})")
                    elif importance > 1.5:
                        st.markdown(f"⚠️ **{kw}** ({category})")
                    else:
                        st.markdown(f"• {kw} ({category})")
            else:
                st.success("All important keywords are present!")
    
    def render_format_analysis(self, format_analysis: Dict[str, Any]):
        """Render format analysis results."""
        
        # ATS Format Score Card
        score = format_analysis['score']
        score_class = self.get_score_class(score)
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📝 ATS Format Compatibility</h4>
            <p class="{score_class}">Score: {score:.1%}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Format check results
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### ✅ Format Strengths")
            
            for check, passed in format_analysis['format_checks'].items():
                if passed:
                    check_name = check.replace('_', ' ').title()
                    st.markdown(f"✅ {check_name}")
        
        with col2:
            st.markdown("#### ⚠️ Format Issues")
            
            issues_found = False
            for check, passed in format_analysis['format_checks'].items():
                if not passed:
                    check_name = check.replace('_', ' ').title()
                    st.markdown(f"❌ {check_name}")
                    issues_found = True
            
            if not issues_found:
                st.success("No format issues detected!")
        
        # Detailed format recommendations
        if format_analysis.get('improvements'):
            st.markdown("#### 💡 Format Improvements")
            
            for improvement in format_analysis['improvements']:
                st.markdown(f"""
                <div class="improvement-suggestion">
                    <strong>Suggestion:</strong> {improvement}
                </div>
                """, unsafe_allow_html=True)
    
    def render_length_analysis(self, length_analysis: Dict[str, Any]):
        """Render length and structure analysis."""
        
        # Length metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            word_count = length_analysis['word_count']
            st.metric("📄 Word Count", f"{word_count:,}")
        
        with col2:
            char_count = length_analysis['character_count']
            st.metric("🔤 Characters", f"{char_count:,}")
        
        with col3:
            page_estimate = max(1, round(word_count / 300))
            st.metric("📋 Est. Pages", page_estimate)
        
        with col4:
            reading_time = max(1, round(word_count / 200))
            st.metric("⏱️ Reading Time", f"{reading_time} min")
        
        # Length recommendations
        st.markdown("#### 📏 Length Analysis")
        
        if word_count < 300:
            st.markdown("""
            <div class="warning-card">
                <strong>⚠️ Resume Too Short</strong><br>
                Your resume appears to be too brief. Consider adding more details about your experience and achievements.
            </div>
            """, unsafe_allow_html=True)
        
        elif word_count > 800:
            st.markdown("""
            <div class="warning-card">
                <strong>⚠️ Resume Too Long</strong><br>
                Your resume might be too lengthy. Consider condensing information and focusing on most relevant experiences.
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.markdown("""
            <div class="success-card">
                <strong>✅ Good Length</strong><br>
                Your resume length is appropriate for most positions.
            </div>
            """, unsafe_allow_html=True)
    
    def render_recommendations(self, specific_feedback: List[str], ats_recommendations: List[str]):
        """Render comprehensive recommendations."""
        
        st.markdown("#### 🎯 Priority Recommendations")
        
        all_recommendations = specific_feedback + ats_recommendations
        
        # Categorize recommendations
        priority_high = []
        priority_medium = []
        priority_low = []
        
        for rec in all_recommendations:
            if any(word in rec.lower() for word in ['critical', 'important', 'missing', 'must']):
                priority_high.append(rec)
            elif any(word in rec.lower() for word in ['improve', 'consider', 'enhance']):
                priority_medium.append(rec)
            else:
                priority_low.append(rec)
        
        # High priority recommendations
        if priority_high:
            st.markdown("##### 🔴 High Priority")
            for rec in priority_high[:5]:
                st.markdown(f"""
                <div class="error-card">
                    <strong>Critical:</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
        
        # Medium priority recommendations
        if priority_medium:
            st.markdown("##### 🟡 Medium Priority")
            for rec in priority_medium[:5]:
                st.markdown(f"""
                <div class="warning-card">
                    <strong>Improvement:</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
        
        # Low priority recommendations
        if priority_low:
            st.markdown("##### 🟢 Enhancement Opportunities")
            for rec in priority_low[:3]:
                st.markdown(f"""
                <div class="improvement-suggestion">
                    <strong>Enhancement:</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
    
    def render_advanced_insights(self, nlp_analysis: Dict[str, Any]):
        """Render advanced NLP insights."""
        
        st.markdown("#### 🧠 Advanced AI Insights")
        
        # Semantic similarity breakdown
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("##### 🎯 Semantic Alignment")
            
            semantic_scores = {
                'Skills Match': nlp_analysis.get('skills_similarity', 0),
                'Experience Relevance': nlp_analysis.get('experience_match', 0),
                'Domain Expertise': nlp_analysis.get('domain_similarity', 0),
                'Role Fit': nlp_analysis.get('role_alignment', 0)
            }
            
            for metric, score in semantic_scores.items():
                score_class = self.get_score_class(score)
                st.markdown(f"{metric}: <span class='{score_class}'>{score:.1%}</span>", 
                           unsafe_allow_html=True)
        
        with col2:
            st.markdown("##### 📊 Confidence Levels")
            
            # Create confidence visualization
            confidence_data = pd.DataFrame([
                {'Metric': k.replace('_', ' ').title(), 'Score': v}
                for k, v in semantic_scores.items()
            ])
            
            fig = px.bar(
                confidence_data,
                x='Score',
                y='Metric',
                orientation='h',
                color='Score',
                color_continuous_scale='RdYlGn',
                title="Semantic Analysis Confidence"
            )
            
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        if 'insights' in nlp_analysis:
            st.markdown("##### 💡 Key Insights")
            
            for insight in nlp_analysis['insights']:
                st.markdown(f"""
                <div class="improvement-suggestion">
                    {insight}
                </div>
                """, unsafe_allow_html=True)

    def run(self):
        """Main application runner."""
        
        # Render header
        self.render_main_header()
        
        # Check if analytics dashboard should be shown
        if st.session_state.get('show_analytics', False):
            if st.button("← Back to Resume Analyzer"):
                st.session_state.show_analytics = False
                st.experimental_rerun()
            
            if self.analytics_engine:
                self.analytics_engine.create_analytics_dashboard()
            return
        
        # Render sidebar and get configuration
        ats_type, analysis_depth, upload_method = self.render_sidebar()
        
        # Render input section
        resume_text, job_description, resume_file = self.render_input_section(upload_method)
        
        # Analysis button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            analyze_button = st.button(
                "🚀 Analyze Resume", 
                type="primary",
                use_container_width=True,
                help="Click to start comprehensive resume analysis"
            )
        
        # Perform analysis
        if analyze_button:
            analysis_results = self.perform_analysis(
                resume_text, job_description, ats_type, analysis_depth
            )
            
            if analysis_results:
                st.session_state.analysis_results = analysis_results
        
        # Display results if available
        if 'analysis_results' in st.session_state:
            self.render_results_dashboard(st.session_state.analysis_results)

def main():
    """Main application entry point."""
    app = EnhancedResumeMatcherApp()
    app.run()

if __name__ == "__main__":
    main()
