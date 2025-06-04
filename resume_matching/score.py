import os
import json
import pandas as pd
import streamlit as st
from io import StringIO

st.set_page_config(page_title="Candidate Matching Scores", layout="wide")
st.title("📊 Candidate Matching Scores Generator")

# Folder containing JSON files
directory = "matching_results"

# Match value mapping
match_mapping = {
    "FULL": 1.0,
    "NEAR FULL": 0.7,
    "PARTIAL": 0.4,
    "NONE": 0.0,
    "MISSING": 0.0,
    "None": 0.0
}

# Collect results
results = []

for filename in os.listdir(directory):
    if filename.endswith("_match.json"):
        filepath = os.path.join(directory, filename)
        candidate_name = filename.replace("_match.json", "")
        
        with open(filepath, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                st.warning(f"⚠️ Invalid JSON in file: {filename}")
                continue

        numerator = 0.0
        denominator = 0.0

        for item in data:
            match_str = item.get("match", "MISSING")
            importance = item.get("importance", 0.0)
            if importance is None:  # <-- Correction ici
                importance = 0.0
            match_val = match_mapping.get(match_str, 0.0)

            numerator += match_val * importance
            denominator += importance

        score = (numerator / denominator) * 100 if denominator > 0 else 0
        results.append({"Name": candidate_name, "Score": round(score, 2)})

# Create DataFrame
df = pd.DataFrame(results)

# Display the table
st.subheader("📋 Calculated Scores")
st.dataframe(df)

# Use StringIO to ensure proper text-based CSV download
csv_buffer = StringIO()
df.to_csv(csv_buffer, index=False)
csv_content = csv_buffer.getvalue()

# Download button
st.download_button(
    label="💾 Download Matching Scores as CSV",
    data=csv_content,
    file_name="matching_scores.csv",
    mime="text/csv"
)

st.success("✅ Matching scores generated successfully.")
