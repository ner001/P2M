import streamlit as st
import http.client
import json
import urllib.parse
import pandas as pd
import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
# Try to get GitHub token from environment, or use a placeholder
GITHUB_ACCESS_TOKEN = os.environ.get("GITHUB_ACCESS_TOKEN", "YOUR_GITHUB_TOKEN")

# App configuration
st.set_page_config(
    page_title="Profile Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Initialize session state for page navigation if not exists
if 'page' not in st.session_state:
    st.session_state.page = 'linkedin'  # Default to LinkedIn page

# GitHub API base URL
GITHUB_API_URL = "https://api.github.com"
github_headers = {
    'Authorization': f'token {GITHUB_ACCESS_TOKEN}'
}

# Function definitions for LinkedIn analysis
def fully_encode_url(url):
    """Fully encode a URL for the API request"""
    replacements = {
        '://': '%3A%2F%2F',
        '/': '%2F',
        ':': '%3A',
        '?': '%3F',
        '=': '%3D',
        '&': '%26',
        ' ': '%20'
    }
    for char, encoded in replacements.items():
        url = url.replace(char, encoded)
    return url
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
def fetch_linkedin_data(linkedin_url, RAPIDAPI_KEY):
    """Fetch LinkedIn profile data from RapidAPI"""
    try:
        encoded_url = fully_encode_url(linkedin_url)
        conn = http.client.HTTPSConnection("linkedin-profile-data.p.rapidapi.com")
        
        headers = {
            'x-rapidapi-key': "RAPIDAPI_KEY",
            'x-rapidapi-host': "linkedin-data-api.p.rapidapi.com"
        }

        conn.request("GET", "/?url=https://www.linkedin.com/in/mohammed-arbi-nsibi-584a43241/", headers=headers)
        res = conn.getresponse()
        data = res.read()
        
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}

# Function definitions for GitHub analysis
def search_github_profiles(keyword, max_profiles, country=None):
    search_url = f"{GITHUB_API_URL}/search/users"
    query = f'{keyword}'
    
    if country:
        query += f' location:{country}'

    params = {
        'q': query,
        'per_page': max_profiles,
        'sort': 'repositories',
        'order': 'desc'
    }

    response = requests.get(search_url, headers=github_headers, params=params)

    if response.status_code == 200:
        return response.json()['items']
    elif response.status_code == 403:
        st.write("Rate limit exceeded. Waiting...")
        reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
        time_to_wait = max(0, reset_time - time.time())
        time.sleep(time_to_wait)
        return search_github_profiles(keyword, max_profiles, country)
    else:
        st.write(f"Failed to search for profiles: {response.status_code}")
        return []

def fetch_profile_and_repositories(username):
    profile_url = f"{GITHUB_API_URL}/users/{username}"
    repos_url = f"{GITHUB_API_URL}/users/{username}/repos"

    profile_response = requests.get(profile_url, headers=github_headers)
    repos_response = requests.get(repos_url, headers=github_headers)

    if profile_response.status_code == 200:
        profile_data = profile_response.json()
    else:
        st.write(f"Failed to fetch profile data for {username}: {profile_response.status_code}")
        return None, []

    if repos_response.status_code == 200:
        repos_data = repos_response.json()
    else:
        st.write(f"Failed to fetch repositories for {username}: {repos_response.status_code}")
        repos_data = []

    return profile_data, repos_data

def analyze_profiles(profiles):
    profile_analysis = []

    for profile in profiles:
        username = profile['login']
        profile_data, repos_data = fetch_profile_and_repositories(username)

        if profile_data:
            analysis = {
                'Username': profile_data['login'],
                'Name': profile_data.get('name', 'N/A'),
                'Company': profile_data.get('company', 'N/A'),
                'Location': profile_data.get('location', 'N/A'),
                'Public Repos': profile_data['public_repos'],
                'Followers': profile_data['followers'],
                'Following': profile_data['following'],
                'Profile URL': profile_data['html_url'],
                'Repo Count': len(repos_data),
                'Top Repositories': [repo['name'] for repo in repos_data[:5]]
            }
            profile_analysis.append(analysis)

    return profile_analysis

# Sidebar navigation
st.sidebar.title("Professional Profile Analyzer")
st.sidebar.markdown("---")
st.sidebar.title("Navigation")
if st.sidebar.button("LinkedIn Analyzer", use_container_width=True):
    st.session_state.page = 'linkedin'
    st.rerun()
if st.sidebar.button("GitHub Analyzer", use_container_width=True):
    st.session_state.page = 'github'
    st.rerun()

# Display appropriate page based on selection
if st.session_state.page == 'linkedin':
    st.title("LinkedIn Profile Analyzer")
    st.markdown("""
    This tool fetches and displays detailed information from LinkedIn profiles using the RapidAPI LinkedIn Profile Data API.
    Enter a LinkedIn profile URL and your RapidAPI key to analyze the profile.
    """)

    # Input fields
    col1, col2 = st.columns(2)
    with col1:
        linkedin_url = st.text_input("LinkedIn Profile URL")
    api_key = st.text_input("RapidAPI Key", type="password")
    with col2: 
        st.markdown("**Note:** You can get your RapidAPI key from [RapidAPI](https://rapidapi.com/).")  
    st.markdown("---")

    # Fetch data button
    if st.button("Analyze LinkedIn Profile", type="primary"):
        if not linkedin_url or not api_key:
            st.error("Please provide both a LinkedIn URL and RapidAPI key")
        else:
            with st.spinner("Fetching profile data..."):
                profile_data = fetch_linkedin_data(linkedin_url, api_key)
                
                if "error" in profile_data:
                    st.error(f"Error fetching profile data: {profile_data['error']}")
                else:
                    # Display profile information
                    st.success("Profile data retrieved successfully!")
                    
                    # Profile header section
                    if "profile" in profile_data:
                        profile = profile_data["profile"]
                        
                        # Create a two-column layout for the profile header
                        header_col1, header_col2 = st.columns([1, 3])
                        
                        with header_col1:
                            if "photo" in profile:
                                st.image(profile.get("photo", ""), width=150)
                            else:
                                st.image("https://via.placeholder.com/150", width=150)
                        
                        with header_col2:
                            st.markdown(f"## {profile.get('name', 'N/A')}")
                            st.markdown(f"**{profile.get('title', 'N/A')}**")
                            st.markdown(f"🌍 {profile.get('location', 'N/A')}")
                            
                            if "connections" in profile:
                                st.markdown(f"🔗 {profile.get('connections', 'N/A')} connections")
                            
                            if "url" in profile:
                                st.markdown(f"[View LinkedIn Profile]({profile.get('url', '#')})")
                    
                    # About section
                    if "profile" in profile_data and "about" in profile_data["profile"]:
                        st.markdown("### About")
                        st.markdown(profile_data["profile"]["about"])
                    
                    # Tabs for different sections
                    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Experience", "Education", "Skills", "Projects", "Raw Data"])
                    
                    # Experience tab
                    with tab1:
                        if "experience" in profile_data:
                            st.markdown("### Work Experience")
                            
                            for job in profile_data.get("experience", []):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**{job.get('title', 'N/A')}** at **{job.get('company', 'N/A')}**")
                                    if "description" in job and job["description"]:
                                        st.markdown(job["description"])
                                
                                with col2:
                                    st.markdown(f"{job.get('date_range', 'N/A')}")
                                    if "location" in job:
                                        st.markdown(f"📍 {job.get('location', '')}")
                                
                                st.divider()
                        else:
                            st.info("No experience data available")
                    
                    # Education tab
                    with tab2:
                        if "education" in profile_data:
                            st.markdown("### Education")
                            
                            for edu in profile_data.get("education", []):
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"**{edu.get('school', 'N/A')}**")
                                    st.markdown(f"*{edu.get('degree', 'N/A')}*")
                                    if "description" in edu and edu["description"]:
                                        st.markdown(edu["description"])
                                
                                with col2:
                                    st.markdown(f"{edu.get('date_range', 'N/A')}")
                                
                                st.divider()
                        else:
                            st.info("No education data available")
                    
                    # Skills tab
                    with tab3:
                        if "skills" in profile_data:
                            st.markdown("### Skills")
                            
                            skills = profile_data.get("skills", [])
                            # Create a DataFrame for skills
                            if skills:
                                # Create multiple columns for skills display
                                cols = st.columns(3)
                                for i, skill in enumerate(skills):
                                    cols[i % 3].markdown(f"- {skill}")
                        else:
                            st.info("No skills data available")
                    
                    # Projects tab
                    with tab4:
                        if "projects" in profile_data:
                            st.markdown("### Projects")
                            
                            for project in profile_data.get("projects", []):
                                st.markdown(f"**{project.get('title', 'N/A')}**")
                                st.markdown(f"*{project.get('date_range', 'N/A')}*")
                                if "description" in project and project["description"]:
                                    st.markdown(project["description"])
                                st.divider()
                        else:
                            st.info("No project data available")
                    
                    # Raw data tab
                    with tab5:
                        st.markdown("### Raw Profile Data")
                        st.json(profile_data)
                        # Convert the dictionary to a JSON string
                        json_data = json.dumps(profile_data, indent=4)

                        # Add a download button
                        st.download_button(
                            label="📥 Download Profile Data as JSON",
                            data=json_data,
                            file_name="profile_data.json",
                            mime="application/json"
                        )

elif st.session_state.page == 'github':
    st.title("GitHub Profile Analyzer")

    # GitHub API key warning/input
    if GITHUB_ACCESS_TOKEN == "YOUR_GITHUB_TOKEN":
        st.warning("GitHub access token not found in environment variables. You may need to set up a .env file with your GitHub token.")
        github_token = st.text_input("Enter GitHub Access Token (optional)", type="password")
        if github_token:
            github_headers['Authorization'] = f'token {github_token}'

    keyword = st.text_input("🔍 Enter a keyword to search for profiles:")
    max_profiles = st.text_input("📊 Max Profiles to Fetch")
    
    # Country Dropdown
    country = st.selectbox(
        "Select a Country (optional)",
        options=["", "Tunisia", "United States", "Canada", "India", "France", "Germany", "Brazil", "United Kingdom"]
    )

    if st.button("Search GitHub Profiles", type="primary"):
        if not keyword:
            st.error("Please enter a keyword to search for GitHub profiles")
        else:
            if max_profiles.isdigit():
                max_profiles = int(max_profiles)
                
                with st.spinner("Searching for GitHub profiles..."):
                    profiles = search_github_profiles(keyword, max_profiles=max_profiles, country=country)
                    profile_data = analyze_profiles(profiles)

                    if profile_data:
                        st.success(f"Found {len(profile_data)} profiles matching your criteria")
                        st.subheader("📈 GitHub Profile Analysis")
                        for person in profile_data:
                            with st.expander(f"{person['Name']} (@{person['Username']})"):
                                # Create a two-column layout for profile display
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    st.markdown(f"""
                                    **👤 Username:** [{person['Username']}]({person['Profile URL']})  
                                    **📛 Name:** {person['Name']}  
                                    **🏢 Company:** {person['Company']}  
                                    **📍 Location:** {person['Location']}  
                                    **⭐ Top Repositories:** {', '.join(person['Top Repositories']) if person['Top Repositories'] else 'None'}
                                    """)
                                
                                with col2:
                                    st.markdown(f"""
                                    **📦 Public Repos:** {person['Public Repos']}  
                                    **👥 Followers:** {person['Followers']}  
                                    **👣 Following:** {person['Following']}  
                                    """)
                    else:
                        st.warning("No profiles found matching your criteria")
            else:
                st.error("Please enter a valid number for Max Profiles")
    st.markdown("---")