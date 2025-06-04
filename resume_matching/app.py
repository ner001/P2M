import os
import json
import io
import sqlite3
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from llama_cloud_services import LlamaExtract
from pydantic import BaseModel
from typing import List, Optional
from llama_cloud.core.api_error import ApiError
import os
import tempfile
import json
import re
from pathlib import Path

# Load environment variables
load_dotenv()
api_key = os.environ["LLAMA_CLOUD_API_KEY"]
llama_extract = LlamaExtract()

# -------------------- Data Schema --------------------
class TechnicalSkills(BaseModel):
    programming_languages: List[str]
    frameworks: List[str]
    skills: List[str]

class Experience(BaseModel):
    company: str
    title: str
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]

class Education(BaseModel):
    institution: str
    degree: str
    start_date: Optional[str]
    end_date: Optional[str]

class Resume(BaseModel):
    name: str
    phone: str
    email: str
    links: List[str]
    experience: List[Experience]
    education: List[Education]
    technical_skills: TechnicalSkills
    key_accomplishments: str
    certifications: List[str]
    projects: List[str]
    languages: List[str]
    interests: List[str]
    hobbies: List[str]
    awards: List[str]
    volunteer_experience: List[str]
    references: List[str]
    summary: str
    location: str

# -------------------- Database Functions --------------------
def create_database():
    conn = sqlite3.connect("cvs.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            json_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_database(name, email, phone, json_data):
    conn = sqlite3.connect("cvs.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO candidates (name, email, phone, json_data) VALUES (?, ?, ?, ?)",
                  (name, email, phone, json_data))
    except sqlite3.IntegrityError:
        st.warning(f"⚠️ Le candidat avec l'email {email} existe déjà.")
    conn.commit()
    conn.close()

def get_all_candidates():
    conn = sqlite3.connect("cvs.db")
    c = conn.cursor()
    c.execute("SELECT name, email, phone, json_data FROM candidates")
    rows = c.fetchall()
    conn.close()
    return rows

def delete_candidate_by_email(email):
    conn = sqlite3.connect("cvs.db")
    c = conn.cursor()
    c.execute("DELETE FROM candidates WHERE email = ?", (email,))
    conn.commit()
    conn.close()

# -------------------- Llama Agent --------------------
def initialize_agent():
    try:
        existing_agent = llama_extract.get_agent(name="resume-screening")
        if existing_agent:
            llama_extract.delete_agent(existing_agent.id)
    except ApiError as e:
        if e.status_code != 404:
            raise
    return llama_extract.create_agent(name="resume-screening", data_schema=Resume)

# -------------------- Streamlit App --------------------
def main():
    st.set_page_config(page_title="CV Parser", layout="wide")
    st.title("📄 CV Parser")

    create_database()
    agent = initialize_agent()

    st.subheader("📂 Charger un dossier contenant des CVs (PDF)")

    # Étape 1 : Upload multiple de fichiers
    uploaded_files = st.file_uploader("Téléverser les fichiers PDF des CVs", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.success(f"{len(uploaded_files)} fichier(s) prêt(s) à être analysé(s).")

        # Étape 2 : Bouton de lancement du parsing
        if st.button("🔍 Lancer le parsing"):

            # Créer un dossier temporaire pour stocker les fichiers
            with tempfile.TemporaryDirectory() as temp_dir:
                os.makedirs("parsed_json", exist_ok=True)

                # Sauvegarder les fichiers localement pour traitement
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                pdf_files = list(Path(temp_dir).glob("*.pdf"))

                if not pdf_files:
                    st.warning("Aucun fichier PDF valide trouvé.")
                else:
                    with st.spinner("⏳ Traitement des fichiers..."):
                        for pdf_path in pdf_files:
                            try:
                                result = agent.extract(str(pdf_path))
                                data = Resume(**result.data)

                                # Sauvegarde en base de données
                                save_to_database(data.name, data.email, data.phone, json.dumps(result.data))

                                # Sauvegarde au format JSON
                                clean_name = re.sub(r'[^\w\-_.]', '_', data.name)
                                json_filename = clean_name + ".json"
                                json_path = os.path.join("parsed_json", json_filename)

                                with open(json_path, "w", encoding="utf-8") as f:
                                    json.dump(result.data, f, indent=2, ensure_ascii=False)

                                st.success(f"✅ {pdf_path.name} traité avec succès.")

                            except Exception as e:
                                st.warning(f"❌ Erreur avec {pdf_path.name} : {str(e)}")

                    st.success("🎉 Extraction terminée pour tous les fichiers.")

    st.subheader("📋 Liste des candidats")
    candidates = get_all_candidates()
    search = st.text_input("🔎 Rechercher par nom ou email")

    if candidates:
        for i, (name, email, phone, json_data) in enumerate(candidates):
            if search.lower() in name.lower() or search.lower() in email.lower() or search == "":
                try:
                    resume_dict = json.loads(json_data)
                    with st.expander(f"👤 {name} | 📧 {email}"):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"- **Téléphone** : {phone}")
                            st.markdown(f"- **Localisation** : {resume_dict.get('location', '')}")
                            st.markdown(f"- **Résumé** : {resume_dict.get('summary', '')}")
                            st.markdown(f"- **Compétences** : {', '.join(resume_dict.get('technical_skills', {}).get('skills', []))}")
                        with col2:
                            if st.button(f"🗑️ Supprimer", key=f"delete_{i}"):
                                delete_candidate_by_email(email)
                                st.experimental_rerun()
                except:
                    continue

        # Export CSV
        filtered_data = [
            {
                "Name": name,
                "Email": email,
                "Phone": phone,
                "Location": json.loads(json_data).get("location", ""),
                "Summary": json.loads(json_data).get("summary", ""),
                "Skills": ", ".join(json.loads(json_data).get("technical_skills", {}).get("skills", [])),
            }
            for name, email, phone, json_data in candidates
            if search.lower() in name.lower() or search.lower() in email.lower() or search == ""
        ]
        df = pd.DataFrame(filtered_data)

        if not df.empty:
            st.subheader("📤 Exporter les résultats")
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("⬇️ Télécharger CSV", csv_buffer.getvalue(), "candidats.csv", "text/csv")

            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Candidats')
            excel_buffer.seek(0)
            st.download_button(
                "⬇️ Télécharger Excel",
                excel_buffer,
                "candidats.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.info("ℹ️ Aucun CV trouvé.")

if __name__ == "__main__":
    main()