import os
import json
import streamlit as st
import requests

# Set page config
st.set_page_config(page_title="Resume Matching", layout="wide")
st.title("📄 Resume Matching with Job Description (Batch)")

# Upload Job Description
job_file = st.file_uploader("📄 Upload Job Description File", type=["txt", "pdf"])

# Function to read file content
def read_file(file):
    if file is not None:
        return file.read().decode("utf-8", errors="ignore")
    return ""

# Function to run Llama3 request
def match_resume_with_job(resume_text, job_text):
    prompt = f"""

You are an AI assistant designed to evaluate how well a candidate fits a specific job role based on their resume and a structured job description. The job description includes multiple requirement categories, each with an importance weight. Your task is to extract claims about how well the candidate meets each requirement and present them in a structured JSON format.

## Instructions:

1. Analyze the **Resume Data** and the **Job Description Data** provided below.
2. For each requirement (skill, education, experience, soft skill, etc.) in the job description, evaluate the degree to which the candidate meets the requirement based on the resume.
3. For each requirement, extract and return the following fields:
   - **requirement**: the original job requirement or skill.
   - **match**: choose one of the following: "FULL", "PARTIAL","NEAR FULL" or "NONE".
   - **evidence**: a short explanation or quote from the resume that supports your evaluation.
   - **source**: "RESUME" if the evidence is explicitly present in the resume or "Inference"
   - **importance**: put the corresponding weight from the job description file
PLEASE MAKE SURE TO PUT ONLY THINGS THAT OCCUR IN THE RESUME DATA and Be very critical in your assessment.
4. Output the result in this JSON format:
[
  {{
    "requirement": "",
    "match": "",
    "evidence": "",
    "source": "",
    "importance": 0.0
  }},
  ...
]
PLEASE MAKE SURE TO GIVE THE EXACT JSON FORMAT IN THE OUTPUT .
MAKE SURE to evaluate the candidate's fit for ALL requirements, including soft skills and penalties.
Mention the penalties that should be applied according to the job description penalties and the match with the resume
## Resume Data:
{resume_text}

## Job Description Data:
{job_text}

"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "Llama3:latest",
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"❌ Error: {response.status_code}"
    except Exception as e:
        return f"❌ Exception: {str(e)}"

# On button click
if st.button("🔍 Run Matching for All Resumes"):
    job_text = read_file(job_file)
    if not job_text:
        st.error("🚫 Please upload a job description file.")
    else:
        st.info("📂 Loading resumes from 'parsed_json' directory...")
        if not os.path.exists("parsed_json"):
            st.error("🚫 'parsed_json' directory not found.")
        else:
            resume_files = [f for f in os.listdir("parsed_json") if f.endswith(".json")]
            if not resume_files:
                st.warning("⚠️ No resumes found in 'parsed_json'.")
            else:
                os.makedirs("matching_results", exist_ok=True)
                with st.spinner("⏳ Matching in progress..."):
                    for file in resume_files:
                        resume_path = os.path.join("parsed_json", file)
                        with open(resume_path, "r", encoding="utf-8") as f:
                            resume_json = json.load(f)
                        resume_text = json.dumps(resume_json, indent=2, ensure_ascii=False)
                        result = match_resume_with_job(resume_text, job_text)

                        # Save result to file
                        result_filename = file.replace(".json", "_match.json")
                        result_path = os.path.join("matching_results", result_filename)
                        with open(result_path, "w", encoding="utf-8") as out_file:
                            out_file.write(result)

                        st.success(f"✅ Match complete for: {file}")
                        with st.expander(f"📄 {file} Match Result"):
                            st.text_area("🔍 Output", result, height=300)

                st.success("🎉 All resume matches complete!")
