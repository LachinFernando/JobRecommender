import streamlit as st
import os
from db_utils import get_record
from llm import career_recommendation

# Set page config
st.set_page_config(
    page_title="Career Recommendations - FutureFrameXR",
    page_icon="💼",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    .career-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5em;
        margin-bottom: 1.5em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1E88E5;
    }
    .skills-badge {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1565c0;
        padding: 4px 12px;
        border-radius: 15px;
        margin: 3px;
        font-size: 0.85em;
    }
    .section-title {
        color: #1E88E5;
        margin-top: 1em;
        margin-bottom: 0.5em;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "generated" not in st.session_state:
    st.session_state.generated = False

# dynamodb table name
os.environ["ENV"] = st.secrets["aws"]["ENV"]
TABLE_NAME = os.getenv("ENV") + "_user_info"

# Authentication check
if not st.user.is_logged_in:
    st.error("🔒 Please login to view your career recommendations", icon="🚨")
    st.stop()

if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# Fetch user data if not in session
if not st.session_state.user_info:
    db_fetch = get_record(TABLE_NAME, str(st.user.sub))
    if not db_fetch:
        st.error("📝 Please complete your profile first to get career recommendations", icon="🚨")
        st.stop()
    st.session_state.user_info = db_fetch

# Main content
st.title("🚀 Your Career Recommendations")
st.markdown("Discover exciting career paths tailored to your skills and interests.")
st.markdown("---")

# User info sidebar
with st.sidebar:
    st.markdown("### 👤 Your Profile")
    if st.user.picture:
        st.image(st.user.picture, width=100)
    st.write(f"**Name:** {st.user.name}")
    st.write(f"**Education:** {st.session_state.user_info.get('education_level', 'Not specified')} in {st.session_state.user_info.get('field_of_study', 'Not specified')}")
    
    if st.session_state.user_info.get('interests'):
        st.markdown("**Interests:**")
        interests = st.session_state.user_info['interests'].split(', ') if isinstance(st.session_state.user_info['interests'], str) else st.session_state.user_info['interests']
        for interest in interests[:5]:
            st.markdown(f"- {interest.strip()}")
    
    if st.button("🔄 Refresh Recommendations"):
        st.session_state.generated = False
        st.rerun()

# Generate recommendations
if not st.session_state.generated:
    if st.button("✨ Generate Career Recommendations", type="primary", use_container_width=True):
        with st.spinner("🔍 Analyzing your profile and finding the best career matches..."):
            try:
                career_recommendations = career_recommendation(
                    st.session_state.user_info["education_level"],
                    st.session_state.user_info["field_of_study"],
                    st.session_state.user_info["career_goals"],
                    st.session_state.user_info["interests"],
                    st.session_state.user_info["skills"]
                )
                
                st.session_state.career_dict = {}
                for job_type in career_recommendations.careers:
                    st.session_state.career_dict[job_type.title] = {
                        "description": job_type.description,
                        "skills": job_type.skills,
                        "daily_duties": job_type.daily_duties
                    }
                st.session_state.generated = True
                st.rerun()
                
            except Exception as e:
                st.error("❌ An error occurred while generating recommendations. Please try again.")
                st.error(str(e))
    
    # Show some loading tips
    st.markdown("### 💡 Tips for Better Recommendations")
    st.markdown("""
    - Make sure your profile is complete and up-to-date
    - Be specific about your career goals and interests
    - Include all relevant skills and experiences
    - The more detailed your profile, the better the recommendations
    """)

# Display career recommendations
if st.session_state.get('career_dict'):
    st.markdown("### 🎯 Recommended Career Paths")
    st.markdown("Based on your profile, here are some career options that might interest you:")
    
    for career, details in st.session_state.career_dict.items():
        with st.container():
            #st.markdown(f"<div class='career-card'>", unsafe_allow_html=True)
            
            # Career title with icon
            st.markdown(f"#### 🎯 {career}")
            
            # Description
            st.markdown("<div class='section-title'>About This Role</div>", unsafe_allow_html=True)
            st.markdown(details["description"])
            
            # Skills
            st.markdown("<div class='section-title'>Key Skills Required</div>", unsafe_allow_html=True)
            skills = details["skills"].split(",") if isinstance(details["skills"], str) else details["skills"]
            cols = st.columns(3)
            for i, skill in enumerate(skills[:6]):  # Show max 6 skills
                with cols[i % 3]:
                    st.markdown(f"<span class='skills-badge'>{skill.strip()}</span>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Daily Duties
            st.markdown("<div class='section-title'>Daily Duties</div>", unsafe_allow_html=True)
            st.markdown(details["daily_duties"])
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add some space between cards
            st.markdown("<br>", unsafe_allow_html=True)
