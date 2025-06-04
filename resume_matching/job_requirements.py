import streamlit as st
import requests
import re
import json
import time

def generate_job_requirements(job_title, model="llama3:latest"):
    url = "http://localhost:11434/api/generate"
    prompt = f"""    -Goal-  
            You are a job description parser. Your task is to extract and structure the requirements from a job description.
            Given a job description for a {job_title} position, extract and structure the requirements into the following JSON format with weights (0-1) .  
            -Output Requirements-  
            1. **Job Type**: Use the provided `{job_title}`.  
            2. **Categories**: Organize requirements into:  
            - `Core skills` (critical for the role)  
            - `Technical skills` (tools/frameworks)  
            - `Experience requirements` (years/projects)  
            - `Education requirements` (degrees/certifications)  
            - `Soft skills` (communication, teamwork)  
            3. **Weights**: Assign each item a weight between 0 (least important) and 1 (most important).   

            -Important Instructions-
            - Be COMPREHENSIVE: Include ALL possible skills and keywords that might appear on resumes for this role
            - For technical roles, list specific technologies, frameworks, and tools (e.g., for AI Engineer, include TensorFlow, PyTorch, Keras, scikit-learn, etc.)
            - For all roles, include industry-specific terminology and certifications
            - Create an IDEAL requirements profile that can be used as a benchmark for evaluating candidate resumes
            - Assign realistic weights that reflect actual industry priorities for this role

            Output must follow this exact format:
            ```json
            {{
            "job_type": "{job_title}",
            "importance_weights": {{
                "Core skills": [
                {{
                    "skill": "<exact_skill_name>",
                    "weight": <0.0-1.0>
                }}
                ],
                "Technical skills": [
                {{
                    "skill": "<exact_skill_name>",
                    "weight": <0.0-1.0>
                }}
                ],
                "Experience requirements": [
                {{
                    "requirement": "<exact_experience>",
                    "weight": <0.0-1.0>
                }}
                ],
                "Education requirements": [
                {{
                    "requirement": "<exact_education>",
                    "weight": <0.0-1.0>
                }}
                ],
                "Soft skills": [
                {{
                    "skill": "<exact_soft_skill>",
                    "weight": <0.0-1.0>
                }}
                ]
            }},
            }}
            ```
            
            Rules:
            - Return ONLY the JSON block
            - No explanations or comments
            - Weights must be between 0.0 and 1.0
            - Ensure valid JSON format with proper quotes and commas
            - This output will be used directly for resume screening, so be thorough and precise"""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        raw_output = data.get("response", "")

        # Extract the JSON block using regex
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if not json_match:
            raise ValueError("No JSON object found in the model response.")

        json_str = json_match.group(0)
        return json.loads(json_str)

    except Exception as e:
        st.error(f"Error parsing job requirements: {e}")
        return None

def display_job_requirements(requirements):
    """Display the job requirements in a structured format."""
    if not requirements:
        st.error("No requirements to display.")
        return

    job_type = requirements.get('job_type', 'Unknown Position')
    st.subheader(f"Job Requirements for: {job_type}")

    st.header("Importance Weights")
    weights = requirements.get("importance_weights", {})

    for category, items in weights.items():
        with st.expander(f"📌 {category}", expanded=False):
            if not items:
                st.write("No items in this category.")
                continue

            for item in items:
                # Ensure item is a dictionary
                if isinstance(item, dict):
                    skill_or_req = item.get("skill") or item.get("requirement", "Unknown")
                    weight = item.get("weight", 0.0)
                    col1, col2 = st.columns([3, 7])
                    with col1:
                        st.write(f"**{skill_or_req}**")
                    with col2:
                        st.progress(min(max(weight, 0.0), 1.0))  # ensure 0.0 <= weight <= 1.0
                        st.caption(f"Weight: {weight:.2f}")
                else:
                    st.warning(f"Unexpected format: {item}")

    with st.expander("📄 View Raw JSON"):
        st.code(json.dumps(requirements, indent=2), language="json")

def edit_job_requirements(requirements: dict) -> dict:
    st.header("Edit Job Requirements")

    # Editable Job Type
    job_type = st.text_input("Job Type", value=requirements.get("job_type", ""))

    # Editable Importance Weights
    st.subheader("Edit Importance Weights")
    weights = requirements.get("importance_weights", {})

    # Temporarily store the changes to apply only on button click
    temp_weights = {}
    temp_job_type = job_type

    for category, items in weights.items():
        st.markdown(f"#### 📌 {category}")
        updated_items = []
        for i, item in enumerate(items):
            if isinstance(item, dict):
                skill = item.get("skill", "")
                requirement = item.get("requirement", "")
                weight = item.get("weight", 0.0)

                col1, col2, col3 = st.columns([4, 4, 2])
                with col1:
                    updated_skill = st.text_input(
                        f"{category} - Item {i+1}", 
                        value=skill or requirement, 
                        key=f"{category}_{i}_skill"
                    )
                with col2:
                    updated_weight = st.slider(
                        f"{category} - Weight {i+1}", 
                        0.0, 1.0, float(weight), 
                        0.01, 
                        key=f"{category}_{i}_weight"
                    )
                with col3:
                    delete = st.checkbox("Delete", key=f"{category}_{i}_delete")

                if not delete:
                    new_item = {"weight": updated_weight}
                    if skill:
                        new_item["skill"] = updated_skill
                    if requirement:
                        new_item["requirement"] = updated_skill
                    updated_items.append(new_item)

        # Add new item option
        with st.expander(f"➕ Add new to {category}"):
            new_label = st.text_input(f"New {category} item", key=f"new_{category}_label")
            new_weight = st.slider(
                f"New {category} weight", 
                0.0, 1.0, 0.5, 0.01, 
                key=f"new_{category}_weight"
            )
            if new_label:
                new_item = {"weight": new_weight}
                if "skill" in category.lower():
                    new_item["skill"] = new_label
                else:
                    new_item["requirement"] = new_label
                updated_items.append(new_item)

        temp_weights[category] = updated_items

    # Button to apply updates
    if st.button("✅ Update Requirements"):
        requirements["job_type"] = temp_job_type
        requirements["importance_weights"] = temp_weights
        st.success("Job requirements updated successfully!")

    return requirements


def main():
    """Main application logic."""
    st.set_page_config(
        page_title="Job Requirements Generator",
        page_icon="💼",
        layout="wide",
    )

    st.title("💼 Job Requirements Generator")

    with st.sidebar:
        st.header("Configuration")
        st.subheader("Model Selection")
        model_options = {
            "llama3:latest": "Llama 3 (Best quality)",
            "gemma:2b": "Gemma 2B (Faster)",
            "mistral:latest": "Mistral (Balanced)"
        }
        model_type = st.selectbox(
            "Choose Model",
            list(model_options.keys()),
            format_func=lambda x: model_options[x],
            index=0
        )

        st.info("Ensure you have Ollama running locally with these models installed.")

        with st.expander("ℹ️ About this app"):
            st.markdown("""
            This app helps recruiters to:
            - Generate structured job requirements
            - Assign importance weights to skills
            - Edit and download the requirements
            """)

    col1, col2 = st.columns([3, 1])
    with col1:
        job_title = st.text_input("Enter Job Title", placeholder="e.g. Data Scientist")
    with col2:
        generate_button = st.button("🚀 Generate Requirements", disabled=not job_title)

    if generate_button:
        with st.spinner(f"Generating requirements for '{job_title}' using {model_type}..."):
            start_time = time.time()
            requirements = generate_job_requirements(job_title, model=model_type)
            duration = time.time() - start_time

            if requirements:
                st.success(f"✅ Generated in {duration:.2f} seconds using {model_type}")
                st.session_state.requirements = requirements
            else:
                st.error("❌ Failed to generate valid requirements.")

    if "requirements" in st.session_state:
        view_mode = st.radio(
            "Select Mode", 
            ["View Requirements", "Edit Requirements"], 
            horizontal=True,
            key="view_mode"
        )

        if view_mode == "View Requirements":
            display_job_requirements(st.session_state.requirements)

        elif view_mode == "Edit Requirements":
            st.session_state.requirements = edit_job_requirements(st.session_state.requirements)
            st.success("Modifications saved. Switch to 'View Requirements' to preview.")

            # Download updated JSON
            st.download_button(
                label="📥 Download Modified Requirements",
                data=json.dumps(st.session_state.requirements, indent=2),
                file_name=f"{st.session_state.requirements['job_type'].replace(' ', '_')}_requirements.json",
                mime="application/json"
            )


if __name__ == "__main__":
    main()