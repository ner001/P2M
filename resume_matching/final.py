import streamlit as st
import pandas as pd

st.set_page_config(page_title="Candidate Matcher", layout="wide")

st.title("📊 Candidate Score Merger")

# Step 1: Upload both files
col1, col2 = st.columns(2)
with col1:
    candidate_info_file = st.file_uploader("📂 Upload Candidate Info CSV", type=["csv"], key="candidate_info")
with col2:
    score_file = st.file_uploader("📂 Upload Matching Score CSV", type=["csv"], key="score_file")

if candidate_info_file and score_file:
    try:
        # Load CSVs
        candidate_info_df = pd.read_csv(candidate_info_file)
        scores_df = pd.read_csv(score_file)

        # Create merge keys: normalize names by removing spaces and lowercasing
        candidate_info_df["merge_key"] = candidate_info_df["Name"].str.replace(" ", "", regex=False).str.lower()
        scores_df["merge_key"] = scores_df["Name"].str.replace("_", "", regex=False).str.lower()

        # Merge on merge_key
        merged_df = pd.merge(candidate_info_df, scores_df[["merge_key", "Score"]], on="merge_key", how="left")

        # Drop helper column
        merged_df.drop(columns=["merge_key"], inplace=True)

        # Sort by score descending
        merged_df = merged_df.sort_values(by="Score", ascending=False)

        st.success("✅ Files uploaded and merged successfully!")

        # Display full merged table
        st.subheader("🔍 Merged Candidate Table (Sorted by Score ↓)")
        st.dataframe(merged_df, use_container_width=True)

        # Download merged table
        csv = merged_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Merged Table as CSV",
            data=csv,
            file_name="merged_candidates_scores.csv",
            mime="text/csv"
        )

        # --- NEW FEATURE: Select Top N Candidates ---
        st.subheader("🔢 Select Number of Top Candidates")
        num_top = st.number_input(
            "Enter the number of top candidates to display:",
            min_value=1,
            max_value=len(merged_df),
            value=min(5, len(merged_df)),
            step=1
        )

        top_candidates = merged_df.head(num_top).sort_values(by="Score", ascending=False)

        st.subheader(f"🏆 Top {num_top} Candidates")
        st.dataframe(top_candidates, use_container_width=True)

        # Download top candidates
        top_csv = top_candidates.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"📥 Download Top {num_top} Candidates as CSV",
            data=top_csv,
            file_name=f"top_{num_top}_candidates.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"❌ Error while processing files: {e}")
else:
    st.info("📄 Please upload both files to proceed.")
