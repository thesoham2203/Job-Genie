"""
Enhanced Resume Matcher - Additional Rendering Methods
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any

class EnhancedResumeMatcherAppMethods:
    """Additional rendering methods for the Enhanced Resume Matcher App."""
    
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
                        'category': enhanced_keywords['category_keywords'].get(kw, 'General')
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
                    category = enhanced_keywords['category_keywords'].get(kw, 'General')
                    
                    if importance > 2:
                        st.markdown(f"🚨 **{kw}** ({category})")
                    elif importance > 1.5:
                        st.markdown(f"⚠️ **{kw}** ({category})")
                    else:
                        st.markdown(f"• {kw} ({category})")
            else:
                st.success("All important keywords are present!")
        
        # Keyword density analysis
        st.markdown("#### 📊 Keyword Density Analysis")
        
        if keyword_analysis['keyword_frequency']:
            density_data = []
            total_words = sum(keyword_analysis['keyword_frequency'].values())
            
            for kw, freq in keyword_analysis['keyword_frequency'].items():
                density = (freq / max(total_words, 1)) * 100
                density_data.append({
                    'keyword': kw,
                    'frequency': freq,
                    'density': density,
                    'importance': enhanced_keywords['keyword_weights'].get(kw, 1)
                })
            
            density_df = pd.DataFrame(density_data)
            density_df = density_df.sort_values('density', ascending=False)
            
            # Show top 10 by density
            st.dataframe(
                density_df.head(10)[['keyword', 'frequency', 'density', 'importance']],
                use_container_width=True
            )
    
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
        if format_analysis['improvements']:
            st.markdown("#### 💡 Format Improvements")
            
            for improvement in format_analysis['improvements']:
                st.markdown(f"""
                <div class="improvement-suggestion">
                    <strong>Suggestion:</strong> {improvement}
                </div>
                """, unsafe_allow_html=True)
        
        # Format best practices
        st.markdown("#### 📋 ATS Format Best Practices")
        
        best_practices = [
            "Use standard section headers (Experience, Education, Skills)",
            "Avoid tables, text boxes, and complex formatting",
            "Use bullet points for listing achievements",
            "Stick to common fonts (Arial, Calibri, Times)",
            "Save as .docx or .pdf format",
            "Avoid headers/footers with important information",
            "Use consistent date formats (MM/YYYY)",
            "Keep file size under 2MB"
        ]
        
        for practice in best_practices:
            st.markdown(f"• {practice}")
    
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
        
        # Section breakdown if available
        if 'section_breakdown' in length_analysis:
            st.markdown("#### 📊 Section Breakdown")
            
            section_data = []
            for section, words in length_analysis['section_breakdown'].items():
                section_data.append({
                    'Section': section.title(),
                    'Words': words,
                    'Percentage': (words / max(word_count, 1)) * 100
                })
            
            section_df = pd.DataFrame(section_data)
            
            fig = px.pie(
                section_df,
                values='Words',
                names='Section',
                title="Word Distribution by Section",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show section table
            st.dataframe(section_df, use_container_width=True)
        
        # Length recommendations by experience level
        st.markdown("#### 💼 Length Guidelines by Experience")
        
        guidelines = {
            "Entry Level (0-2 years)": "1 page (300-500 words)",
            "Mid Level (3-7 years)": "1-2 pages (500-700 words)",
            "Senior Level (8+ years)": "2 pages (700-900 words)",
            "Executive Level": "2-3 pages (800-1200 words)"
        }
        
        for level, guideline in guidelines.items():
            st.markdown(f"• **{level}**: {guideline}")
    
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
        
        # Action plan
        st.markdown("#### 📋 Action Plan")
        
        action_steps = [
            "1. **Update Keywords**: Add missing high-priority keywords to relevant sections",
            "2. **Quantify Achievements**: Add specific numbers and metrics to your accomplishments",
            "3. **Optimize Format**: Ensure ATS-friendly formatting throughout",
            "4. **Enhance Content**: Expand on experiences that match job requirements",
            "5. **Review & Refine**: Proofread and ensure consistency across all sections"
        ]
        
        for step in action_steps:
            st.markdown(step)
        
        # Download improved resume template
        if st.button("📥 Download Resume Template"):
            st.info("💡 Feature coming soon: AI-generated optimized resume template")
    
    def render_advanced_insights(self, nlp_analysis: Dict[str, Any]):
        """Render advanced NLP insights."""
        
        st.markdown("#### 🧠 Advanced AI Insights")
        
        # Semantic similarity breakdown
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("##### 🎯 Semantic Alignment")
            
            semantic_scores = {
                'Skills Match': nlp_analysis['skills_similarity'],
                'Experience Relevance': nlp_analysis['experience_match'],
                'Domain Expertise': nlp_analysis['domain_similarity'],
                'Role Fit': nlp_analysis['role_alignment']
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
        
        # Skill gap analysis
        if 'skill_gaps' in nlp_analysis:
            st.markdown("##### 🎯 Skill Gap Analysis")
            
            skill_gaps = nlp_analysis['skill_gaps']
            
            if skill_gaps:
                gaps_df = pd.DataFrame([
                    {'Skill': skill, 'Gap Level': level}
                    for skill, level in skill_gaps.items()
                ])
                
                st.dataframe(gaps_df, use_container_width=True)
            else:
                st.success("No significant skill gaps detected!")

# Export the methods to be added to the main class
def extend_main_app_class():
    """Extend the main app class with additional methods."""
    # This would be used to add methods to the main class
    pass
