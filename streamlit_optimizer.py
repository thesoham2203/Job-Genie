"""
Interactive dashboard for real-time resume optimization feedback.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List
import numpy as np

from scripts.nlp.advanced_processor import AdvancedNLPProcessor
from scripts.ats.optimization_engine import ATSOptimizationEngine, ATSSystemType

class ResumeOptimizationDashboard:
    """Interactive dashboard for resume optimization."""
    
    def __init__(self):
        self.nlp_processor = AdvancedNLPProcessor()
        self.ats_engine = ATSOptimizationEngine()
    
    def render_dashboard(self):
        """Render the complete optimization dashboard."""
        st.set_page_config(
            page_title="Resume Optimizer Pro",
            page_icon="📄",
            layout="wide"
        )
        
        st.title("🎯 Resume Optimizer Pro")
        st.markdown("### Get real-time feedback to optimize your resume for ATS systems")
        
        # Sidebar for configuration
        with st.sidebar:
            st.header("Configuration")
            ats_type = st.selectbox(
                "Target ATS System",
                options=[ats.value for ats in ATSSystemType],
                help="Select the ATS system the company uses (if known)"
            )
            
            analysis_depth = st.radio(
                "Analysis Depth",
                ["Quick Scan", "Deep Analysis"],
                help="Deep analysis provides more detailed feedback but takes longer"
            )
        
        # Main content area
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📄 Resume Text")
            resume_text = st.text_area(
                "Paste your resume text here:",
                height=300,
                placeholder="Copy and paste your resume content here..."
            )
            
            st.header("💼 Job Description")
            job_description = st.text_area(
                "Paste the job description:",
                height=200,
                placeholder="Copy and paste the job description here..."
            )
            
            analyze_button = st.button("🔍 Analyze Resume", type="primary")
        
        with col2:
            if analyze_button and resume_text and job_description:
                with st.spinner("Analyzing your resume..."):
                    self._perform_analysis(resume_text, job_description, ats_type, analysis_depth)
            elif analyze_button:
                st.warning("Please provide both resume text and job description.")
            else:
                st.info("👈 Enter your resume and job description, then click 'Analyze Resume'")
    
    def _perform_analysis(self, resume_text: str, job_description: str, 
                         ats_type: str, analysis_depth: str):
        """Perform comprehensive resume analysis."""
        
        # Convert string to enum
        ats_enum = ATSSystemType(ats_type)
        
        # Basic ATS analysis
        ats_analysis = self.ats_engine.analyze_ats_compatibility(
            resume_text, job_description, ats_enum
        )
        
        # Advanced NLP analysis (if deep analysis selected)
        if analysis_depth == "Deep Analysis":
            nlp_analysis = self.nlp_processor.semantic_similarity_advanced(
                resume_text, job_description
            )
        else:
            nlp_analysis = None
        
        # Render results
        self._render_analysis_results(ats_analysis, nlp_analysis, ats_type)
    
    def _render_analysis_results(self, ats_analysis: Dict, nlp_analysis: Dict, ats_type: str):
        """Render comprehensive analysis results."""
        
        # Overall score at the top
        st.header("📊 Overall Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            overall_score = ats_analysis['overall_score']
            color = self._get_score_color(overall_score)
            st.metric(
                "ATS Compatibility Score",
                f"{overall_score:.1%}",
                delta=f"{(overall_score - 0.7):.1%}" if overall_score > 0.7 else None
            )
        
        with col2:
            keyword_score = ats_analysis['keyword_analysis']['score']
            st.metric(
                "Keyword Match",
                f"{keyword_score:.1%}",
                delta=f"{(keyword_score - 0.6):.1%}" if keyword_score > 0.6 else None
            )
        
        with col3:
            if nlp_analysis:
                semantic_score = nlp_analysis['composite_score']
                st.metric(
                    "Semantic Match",
                    f"{semantic_score:.1%}",
                    delta=f"{(semantic_score - 0.7):.1%}" if semantic_score > 0.7 else None
                )
        
        # Score breakdown visualization
        st.subheader("📈 Score Breakdown")
        self._render_score_breakdown(ats_analysis, nlp_analysis)
        
        # Detailed analysis tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎯 Keywords", "📝 Format", "📏 Length", "💡 Recommendations"
        ])
        
        with tab1:
            self._render_keyword_analysis(ats_analysis['keyword_analysis'])
        
        with tab2:
            self._render_format_analysis(ats_analysis['format_analysis'])
        
        with tab3:
            self._render_length_analysis(ats_analysis['length_analysis'])
        
        with tab4:
            self._render_recommendations(ats_analysis['recommendations'], ats_type)
    
    def _render_score_breakdown(self, ats_analysis: Dict, nlp_analysis: Dict):
        """Render interactive score breakdown chart."""
        
        # ATS scores
        categories = ['Keywords', 'Format', 'Length', 'Sections']
        ats_scores = [
            ats_analysis['keyword_analysis']['score'],
            ats_analysis['format_analysis']['score'],
            ats_analysis['length_analysis']['score'],
            ats_analysis['section_analysis']['score']
        ]
        
        if nlp_analysis:
            categories.extend(['Skills Match', 'Experience', 'Domain Fit'])
            ats_scores.extend([
                nlp_analysis['skills_similarity'],
                nlp_analysis['experience_match'],
                nlp_analysis['domain_similarity']
            ])
        
        # Create radar chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=ats_scores,
            theta=categories,
            fill='toself',
            name='Your Resume'
        ))
        
        # Add target line
        target_scores = [0.8] * len(categories)
        fig.add_trace(go.Scatterpolar(
            r=target_scores,
            theta=categories,
            fill='toself',
            name='Target Score',
            line=dict(color='rgba(255, 0, 0, 0.5)'),
            fillcolor='rgba(255, 0, 0, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title="Resume Score Breakdown"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _render_keyword_analysis(self, keyword_analysis: Dict):
        """Render detailed keyword analysis."""
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("✅ Matched Keywords")
            matched = keyword_analysis['matched_keywords']
            if matched:
                df = pd.DataFrame(matched)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No keywords matched. Add relevant keywords from the job description.")
        
        with col2:
            st.subheader("❌ Missing Keywords")
            missing = keyword_analysis['missing_keywords']
            if missing:
                for i, keyword in enumerate(missing[:10], 1):
                    st.write(f"{i}. **{keyword}**")
                if len(missing) > 10:
                    st.info(f"... and {len(missing) - 10} more keywords")
            else:
                st.success("Great! All important keywords are included.")
        
        # Keyword density chart
        if matched:
            st.subheader("📊 Keyword Frequency")
            freq_data = [(kw['keyword'], kw['frequency']) for kw in matched]
            freq_df = pd.DataFrame(freq_data, columns=['Keyword', 'Frequency'])
            freq_df = freq_df.sort_values('Frequency', ascending=True)
            
            fig = px.bar(freq_df, x='Frequency', y='Keyword', orientation='h')
            fig.update_layout(title="Keyword Frequency in Your Resume")
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_format_analysis(self, format_analysis: Dict):
        """Render format analysis with specific issues."""
        
        score = format_analysis['score']
        issues = format_analysis['issues']
        
        if score >= 0.8:
            st.success(f"✅ Great formatting! Score: {score:.1%}")
        elif score >= 0.6:
            st.warning(f"⚠️ Good formatting with room for improvement. Score: {score:.1%}")
        else:
            st.error(f"❌ Formatting needs attention. Score: {score:.1%}")
        
        if issues:
            st.subheader("🔧 Formatting Issues to Fix:")
            for i, issue in enumerate(issues, 1):
                st.write(f"{i}. {issue}")
        
        # Formatting checklist
        st.subheader("📋 ATS-Friendly Formatting Checklist")
        checklist = [
            "Use standard section headers (Summary, Experience, Education, Skills)",
            "Use simple bullet points (• or -)",
            "Avoid special characters and symbols",
            "Use consistent spacing between sections",
            "Save as .docx or .pdf format",
            "Use standard fonts (Arial, Calibri, Times New Roman)"
        ]
        
        for item in checklist:
            st.write(f"☐ {item}")
    
    def _render_length_analysis(self, length_analysis: Dict):
        """Render length analysis with recommendations."""
        
        word_count = length_analysis['word_count']
        optimal_range = length_analysis['optimal_range']
        experience_level = length_analysis['estimated_experience_level']
        
        st.subheader(f"📏 Resume Length Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Word Count", word_count)
        
        with col2:
            st.metric("Experience Level", experience_level.replace('_', ' ').title())
        
        with col3:
            st.metric("Optimal Range", f"{optimal_range[0]}-{optimal_range[1]} words")
        
        # Visual representation
        fig = go.Figure()
        
        # Add optimal range
        fig.add_shape(
            type="rect",
            x0=optimal_range[0], x1=optimal_range[1],
            y0=-0.5, y1=0.5,
            fillcolor="green", opacity=0.3,
            line=dict(color="green", width=2)
        )
        
        # Add current length
        fig.add_trace(go.Scatter(
            x=[word_count], y=[0],
            mode="markers+text",
            marker=dict(size=15, color="blue"),
            text=["Your Resume"],
            textposition="top center",
            name="Current Length"
        ))
        
        fig.update_layout(
            title="Resume Length vs Optimal Range",
            xaxis_title="Word Count",
            yaxis=dict(visible=False),
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        if length_analysis['issues']:
            st.warning("⚠️ " + length_analysis['issues'][0])
    
    def _render_recommendations(self, recommendations: List[str], ats_type: str):
        """Render actionable recommendations."""
        
        st.subheader(f"💡 Optimization Recommendations for {ats_type.title()}")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                st.write(f"**{i}.** {rec}")
        else:
            st.success("🎉 Your resume looks great! No major improvements needed.")
        
        # Additional pro tips
        st.subheader("🚀 Pro Tips for ATS Success")
        pro_tips = [
            "**Mirror the job description language**: Use the exact terms and phrases from the job posting",
            "**Quantify achievements**: Include numbers, percentages, and specific metrics",
            "**Use action verbs**: Start bullet points with strong action verbs (Led, Developed, Increased)",
            "**Include relevant certifications**: Add any certifications mentioned in the job description",
            "**Tailor for each application**: Customize your resume for each specific job application"
        ]
        
        for tip in pro_tips:
            st.markdown(f"• {tip}")
    
    def _get_score_color(self, score: float) -> str:
        """Get color based on score."""
        if score >= 0.8:
            return "green"
        elif score >= 0.6:
            return "orange"
        else:
            return "red"

# Usage example
if __name__ == "__main__":
    dashboard = ResumeOptimizationDashboard()
    dashboard.render_dashboard()
