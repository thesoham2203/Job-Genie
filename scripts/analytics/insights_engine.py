"""
Advanced analytics engine for resume performance insights.
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Tuple
import streamlit as st
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path

class ResumeAnalyticsEngine:
    """Advanced analytics engine for tracking resume performance and optimization trends."""
    
    def __init__(self, db_path: str = "resume_analytics.db"):
        self.db_path = db_path
        self._setup_database()
    
    def _setup_database(self):
        """Set up SQLite database for analytics tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables for analytics
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            overall_score REAL,
            keyword_score REAL,
            format_score REAL,
            length_score REAL,
            ats_type TEXT,
            job_title TEXT,
            industry TEXT,
            experience_level TEXT,
            improvements_made TEXT,
            user_id TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS skill_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            skill_name TEXT,
            skill_category TEXT,
            demand_score REAL,
            market_trend TEXT,
            job_postings_count INTEGER
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS optimization_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            before_score REAL,
            after_score REAL,
            improvement_percentage REAL,
            optimization_type TEXT,
            user_id TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def track_analysis(self, analysis_data: Dict[str, Any], user_id: str = "anonymous"):
        """Track resume analysis for trend analysis."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO resume_analysis 
        (overall_score, keyword_score, format_score, length_score, ats_type, 
         job_title, industry, experience_level, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            analysis_data.get('overall_score', 0),
            analysis_data.get('keyword_score', 0),
            analysis_data.get('format_score', 0),
            analysis_data.get('length_score', 0),
            analysis_data.get('ats_type', 'generic'),
            analysis_data.get('job_title', ''),
            analysis_data.get('industry', ''),
            analysis_data.get('experience_level', ''),
            user_id
        ))
        
        conn.commit()
        conn.close()
    
    def generate_market_insights(self) -> Dict[str, Any]:
        """Generate market insights based on job posting analysis."""
        
        # Simulated market data (in real implementation, this would pull from job APIs)
        market_data = self._get_market_data()
        
        insights = {
            'trending_skills': self._analyze_trending_skills(market_data),
            'salary_ranges': self._analyze_salary_ranges(market_data),
            'location_trends': self._analyze_location_trends(market_data),
            'industry_growth': self._analyze_industry_growth(market_data),
            'ats_adoption': self._analyze_ats_adoption(market_data),
            'keyword_importance': self._analyze_keyword_importance(market_data)
        }
        
        return insights
    
    def generate_personalized_recommendations(self, user_profile: Dict[str, Any], 
                                           market_insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized career and optimization recommendations."""
        
        recommendations = []
        
        # Skill gap analysis
        user_skills = set(user_profile.get('skills', []))
        trending_skills = set(market_insights['trending_skills'][:10])
        skill_gaps = trending_skills - user_skills
        
        if skill_gaps:
            recommendations.append({
                'type': 'skill_development',
                'priority': 'high',
                'title': 'Develop In-Demand Skills',
                'description': f"Consider learning these trending skills: {', '.join(list(skill_gaps)[:3])}",
                'action_items': [
                    f"Take online courses in {skill}" for skill in list(skill_gaps)[:3]
                ],
                'impact': 'Could increase interview chances by 40-60%'
            })
        
        # Industry transition opportunities
        current_industry = user_profile.get('industry', '')
        growing_industries = market_insights['industry_growth'][:3]
        
        if current_industry not in [ind['name'] for ind in growing_industries]:
            recommendations.append({
                'type': 'industry_transition',
                'priority': 'medium',
                'title': 'Consider High-Growth Industries',
                'description': f"These industries are showing strong growth: {', '.join([ind['name'] for ind in growing_industries])}",
                'action_items': [
                    "Research transferable skills for target industry",
                    "Network with professionals in growing industries",
                    "Highlight relevant experience for new industry"
                ],
                'impact': 'Potential 20-30% salary increase'
            })
        
        # Location optimization
        user_location = user_profile.get('location', '')
        top_locations = market_insights['location_trends'][:5]
        
        recommendations.append({
            'type': 'location_optimization',
            'priority': 'low',
            'title': 'Consider Remote or Relocation Opportunities',
            'description': f"Top job markets: {', '.join([loc['city'] for loc in top_locations])}",
            'action_items': [
                "Apply for remote positions",
                "Consider relocation to high-opportunity markets",
                "Highlight remote work experience"
            ],
            'impact': 'Access to 3x more job opportunities'
        })
        
        return recommendations
    
    def create_analytics_dashboard(self) -> None:
        """Create comprehensive analytics dashboard."""
        
        st.header("📊 Resume Analytics & Market Insights")
        
        # Generate insights
        market_insights = self.generate_market_insights()
        
        # Tabs for different analytics views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Market Trends", 
            "🎯 Skill Analysis", 
            "💰 Salary Insights", 
            "🏢 Industry Reports"
        ])
        
        with tab1:
            self._render_market_trends(market_insights)
        
        with tab2:
            self._render_skill_analysis(market_insights)
        
        with tab3:
            self._render_salary_insights(market_insights)
        
        with tab4:
            self._render_industry_reports(market_insights)
    
    def _render_market_trends(self, insights: Dict[str, Any]):
        """Render market trends analysis."""
        
        st.subheader("🔥 Trending Skills This Month")
        
        trending_skills = insights['trending_skills']
        
        # Create trending skills chart
        skills_df = pd.DataFrame(trending_skills[:15])
        
        fig = px.bar(
            skills_df, 
            x='demand_score', 
            y='skill_name',
            orientation='h',
            title="Most In-Demand Skills",
            color='demand_score',
            color_continuous_scale='viridis'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # ATS adoption trends
        st.subheader("🤖 ATS System Adoption Rates")
        
        ats_data = insights['ats_adoption']
        ats_df = pd.DataFrame(ats_data)
        
        fig = px.pie(
            ats_df, 
            values='adoption_rate', 
            names='ats_system',
            title="ATS Market Share"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Location trends
        st.subheader("🌍 Top Job Markets")
        
        location_data = insights['location_trends'][:10]
        loc_df = pd.DataFrame(location_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                loc_df, 
                x='job_count', 
                y='city',
                orientation='h',
                title="Job Opportunities by City"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.scatter(
                loc_df, 
                x='avg_salary', 
                y='job_count',
                size='growth_rate',
                hover_name='city',
                title="Salary vs Job Opportunities"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _render_skill_analysis(self, insights: Dict[str, Any]):
        """Render detailed skill analysis."""
        
        st.subheader("🎯 Skill Demand Analysis")
        
        # Skill category breakdown
        trending_skills = insights['trending_skills']
        
        # Group by category
        category_counts = {}
        for skill in trending_skills:
            category = skill['category']
            if category not in category_counts:
                category_counts[category] = []
            category_counts[category].append(skill)
        
        # Create category analysis
        for category, skills in category_counts.items():
            st.write(f"**{category.title()} Skills:**")
            
            skills_df = pd.DataFrame(skills[:10])
            
            fig = px.bar(
                skills_df,
                x='skill_name',
                y='demand_score',
                title=f"Top {category.title()} Skills",
                color='growth_rate',
                color_continuous_scale='RdYlGn'
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Skill correlation matrix
        st.subheader("🔗 Skill Combinations")
        st.info("Skills often appearing together in job postings:")
        
        # Simulated correlation data
        common_combinations = [
            ["Python", "Machine Learning", "Data Science"],
            ["React", "JavaScript", "Node.js"],
            ["AWS", "Docker", "Kubernetes"],
            ["SQL", "Python", "Tableau"],
            ["Java", "Spring Boot", "Microservices"]
        ]
        
        for i, combo in enumerate(common_combinations, 1):
            st.write(f"{i}. {' + '.join(combo)}")
    
    def _render_salary_insights(self, insights: Dict[str, Any]):
        """Render salary analysis and insights."""
        
        st.subheader("💰 Salary Insights")
        
        salary_data = insights['salary_ranges']
        
        # Salary by experience level
        exp_levels = ['Entry Level', 'Mid Level', 'Senior Level', 'Lead/Principal']
        salary_ranges = [
            [45000, 75000], [70000, 110000], [100000, 160000], [140000, 220000]
        ]
        
        salary_df = pd.DataFrame({
            'Experience Level': exp_levels,
            'Min Salary': [r[0] for r in salary_ranges],
            'Max Salary': [r[1] for r in salary_ranges],
            'Avg Salary': [(r[0] + r[1]) / 2 for r in salary_ranges]
        })
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Min Salary',
            x=salary_df['Experience Level'],
            y=salary_df['Min Salary'],
            text=salary_df['Min Salary'],
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='Max Salary',
            x=salary_df['Experience Level'],
            y=salary_df['Max Salary'],
            text=salary_df['Max Salary'],
            textposition='auto',
        ))
        
        fig.update_layout(
            title='Salary Ranges by Experience Level',
            xaxis_title='Experience Level',
            yaxis_title='Salary ($)',
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Salary by skills
        st.subheader("💎 High-Value Skills")
        
        high_value_skills = [
            {'skill': 'Machine Learning', 'salary_premium': 25000, 'demand': 'Very High'},
            {'skill': 'DevOps', 'salary_premium': 20000, 'demand': 'High'},
            {'skill': 'Cloud Architecture', 'salary_premium': 30000, 'demand': 'Very High'},
            {'skill': 'Data Science', 'salary_premium': 22000, 'demand': 'High'},
            {'skill': 'Cybersecurity', 'salary_premium': 28000, 'demand': 'Very High'}
        ]
        
        skills_df = pd.DataFrame(high_value_skills)
        
        fig = px.bar(
            skills_df,
            x='skill',
            y='salary_premium',
            color='demand',
            title='Salary Premium by Skill',
            color_discrete_map={
                'Very High': '#00CC96',
                'High': '#FFA15A',
                'Medium': '#FF6692'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_market_data(self) -> Dict[str, Any]:
        """Simulate market data (in real implementation, pull from job APIs)."""
        return {
            'job_postings': 50000,
            'trending_skills': [
                {'skill_name': 'Python', 'demand_score': 95, 'category': 'programming', 'growth_rate': 15},
                {'skill_name': 'JavaScript', 'demand_score': 92, 'category': 'programming', 'growth_rate': 12},
                {'skill_name': 'React', 'demand_score': 88, 'category': 'framework', 'growth_rate': 20},
                {'skill_name': 'AWS', 'demand_score': 85, 'category': 'cloud', 'growth_rate': 25},
                {'skill_name': 'Machine Learning', 'demand_score': 82, 'category': 'ai', 'growth_rate': 30},
                {'skill_name': 'Docker', 'demand_score': 78, 'category': 'devops', 'growth_rate': 18},
                {'skill_name': 'Kubernetes', 'demand_score': 75, 'category': 'devops', 'growth_rate': 22},
                {'skill_name': 'SQL', 'demand_score': 90, 'category': 'database', 'growth_rate': 8},
                {'skill_name': 'Node.js', 'demand_score': 73, 'category': 'framework', 'growth_rate': 14},
                {'skill_name': 'Terraform', 'demand_score': 70, 'category': 'devops', 'growth_rate': 35}
            ]
        }
    
    def _analyze_trending_skills(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze trending skills from market data."""
        return sorted(market_data['trending_skills'], key=lambda x: x['demand_score'], reverse=True)
