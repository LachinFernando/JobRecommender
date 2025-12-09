import streamlit as st
import os

from db_utils import add_user_info, get_record


# Load environment variables from secrets
os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY"]
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_KEY"]
os.environ["AWS_REGION"] = st.secrets["aws"]["REGION_NAME"]
os.environ["ENV"] = st.secrets["aws"]["ENV"]

# dynamodb table name
TABLE_NAME = os.getenv("ENV") + "_user_info"

# check if user info is in session state
if "user_info" not in st.session_state:
    st.session_state.user_info = {}
    

# Page configuration
st.set_page_config(
    page_title="Your Profile - FutureFrameXR",
    page_icon="👤",
    layout="centered"
)

if not st.user.is_logged_in:
    # ask the user to login
    # add the message "Please login to continue" and an icon
    st.error("Please login to continue", icon="🚨")
    st.stop()

user_available = False
if not st.session_state.user_info:
    # get user info from dynamodb
    user_info = get_record(TABLE_NAME, str(st.user.sub))
    if user_info:
        user_available = True
        # set the user info to session state
        st.session_state.user_info = user_info
    else:
        user_available = False
    
# display the user info in sidebar
if user_available:
    with st.sidebar:
        # latest user info
        if st.user.picture:
            st.image(st.user.picture)
        st.write("Name: " + st.user.name)
        st.write("Email: " + st.user.email)
        st.write("Education Level: " + st.session_state.user_info["education_level"])
        st.write("Field of Study: " + st.session_state.user_info["field_of_study"])
        st.write("Skills: ", ", ".join(st.session_state.user_info["skills"]) if isinstance(st.session_state.user_info["skills"], list) else st.session_state.user_info["skills"])
        st.write("Interests: ",  ", ".join(st.session_state.user_info["interests"]) if isinstance(st.session_state.user_info["interests"], list) else st.session_state.user_info["interests"])
        st.write("Career Goals: " + st.session_state.user_info["career_goals"])

st.title("👤 Your Profile")
st.markdown("Tell us about yourself to get personalized career recommendations.")

# User Information Form
with st.form("user_info_form"):
    st.markdown("### Basic Information")
    col1, col2 = st.columns(2)
    
    with col1:
        first_name = st.text_input("First Name", placeholder="John")
    with col2:
        last_name = st.text_input("Last Name", placeholder="Doe")
    
    email = st.text_input("Email", placeholder="john.doe@example.com")
    
    st.markdown("### Academic Information")
    education_level = st.selectbox(
        "Current Education Level",
        ["High School", "Associate's Degree", "Bachelor's Degree", "Master's Degree", "PhD", "Other"]
    )
    
    field_of_study = st.text_input("Field of Study/Major", placeholder="e.g., Computer Science, Business, etc.")
    
    st.markdown("### Career Interests")
    interests = st.multiselect(
        "Select your areas of interest (select up to 3)",
        ["Technology", "Business", "Healthcare", "Arts & Design", "Engineering", 
         "Education", "Science & Research", "Marketing", "Finance", "Other"],
        max_selections=5
    )
    
    skills = st.text_area("Current Skills (comma-separated)", 
                         placeholder="e.g., Python, Data Analysis, Project Management, etc.")
    
    career_goals = st.text_area("What are your career goals? (Optional)", 
                               placeholder="Where do you see yourself in 5 years?")
    
    submitted = st.form_submit_button("Save Profile")
    if submitted:
        if not all([first_name, last_name, email, education_level, field_of_study, interests]):
            st.error("Please fill in all required fields.")
        else:
            # Here you would typically save this information to a database
            st.session_state.user_info = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "education_level": education_level,
                "field_of_study": field_of_study,
                "interests": ", ".join(interests),
                "skills": ", ".join([s.strip() for s in skills.split(",") if s.strip()]),
                "career_goals": career_goals
            }
            # save the data to dynamodb
            db_response = add_user_info(
                TABLE_NAME,
                str(st.user.sub),
                first_name,
                last_name,
                email,
                education_level,
                field_of_study,
                ", ".join(interests),
                ", ".join([s.strip() for s in skills.split(",") if s.strip()]),
                career_goals
            )
            if db_response['success']:
                st.success("Profile saved successfully!")
                st.balloons()
            else:
                st.error("Failed to save profile.")
            
            # redirect to another page after saving
            st.switch_page("pages/01_Career_Recommendations.py")