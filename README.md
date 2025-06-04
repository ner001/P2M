#Intelligent Multi-Agent HR Automation System

> **Conception et développement d'un système multi-agent intelligent pour l'automatisation des processus RH**

A comprehensive AI-powered solution for automating HR recruitment processes, featuring intelligent CV filtering, automated email generation, and candidate profile discovery from professional platforms.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [System Components](#system-components)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

This project addresses the critical challenges faced by HR departments in modern recruitment processes. Traditional manual candidate screening, subjective profile evaluation, and interview coordination are time-consuming and error-prone. Our solution leverages advanced AI technologies to automate these processes, improving efficiency, reducing bias, and enhancing recruitment quality.

### Key Benefits
- ⚡ **Automated CV Screening**: Intelligent scoring system based on customizable criteria
- 📧 **Smart Email Automation**: Personalized communications based on candidate status
- 🔍 **Candidate Discovery**: Intelligent profile suggestions from LinkedIn and GitHub
- 📊 **Objective Evaluation**: Data-driven candidate ranking and comparison
- 🎯 **Customizable Workflows**: Adaptable to different recruitment needs

## 🚀 Features

### 1. Intelligent CV Processing
- **Automated Data Extraction**: Extracts key information from PDF resumes using LlamaExtract
- **Smart Scoring System**: Compares candidate profiles against job requirements
- **Weighted Evaluation**: Customizable criteria importance for different positions
- **Candidate Ranking**: Automatic sorting based on compatibility scores

### 2. Email Automation
- **Multi-Status Support**: Handles schedule, reschedule, follow-up, and rejection emails
- **Personalized Content**: Generates tailored messages based on candidate profiles
- **Collaborative Agents**: Uses CrewAI for intelligent email orchestration
- **Batch Processing**: Processes multiple candidates simultaneously via CSV input

### 3. Candidate Discovery
- **LinkedIn Integration**: Extracts professional profiles via RapidAPI
- **GitHub Analysis**: Evaluates technical skills through repository analysis
- **Keyword-Based Search**: Targeted candidate discovery based on specific requirements
- **Cross-Platform Insights**: Combines professional and technical profile data

## 🏗️ Architecture

![Flowchart (1)](https://github.com/user-attachments/assets/5d58ed66-b85e-41f4-998e-d5c2af34b4ec)

## 🛠️ Technologies

### Frontend & Interface
- **Streamlit**: Interactive web interface for HR managers
- **Python**: Core programming language

### AI & Machine Learning
- **LlamaExtract**: PDF data extraction and structuring
- **LLaMA 3**: Natural language processing for CV analysis and comparison
- **CrewAI**: Multi-agent orchestration platform

### APIs & Integration
- **LinkedIn API**: Professional profile data extraction (via RapidAPI)
- **GitHub API**: Technical profile analysis and repository evaluation

### Data Processing
- **JSON**: Structured data format for CV information
- **CSV**: Batch processing for candidate management

## 📦 Installation

### Prerequisites
- Python 3.8+
- GitHub Access Token
- RapidAPI Account (for LinkedIn integration)
- LlamaExtract API Key

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/ner001/P2M.git
cd P2M
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file in the root directory
GITHUB_ACCESS_TOKEN=your_github_token
RAPIDAPI_KEY=your_rapidapi_key
LLAMA_EXTRACT_API_KEY=your_llamaextract_key
```

5. **Run the application**
```bash
# For CV matching system
streamlit run resume_matching/app.py

# For email automation
python mail_automation/interview.py

# For profile scraping
python scrapping/linkedin_github.py
```

## 🎯 Usage

### 1. CV Processing & Matching (`resume_matching/`)

```bash
streamlit run resume_matching/app.py
```

**Main Components:**
- `app.py`: Main Streamlit interface for CV processing
- `job_requirements.py`: Generates job descriptions and requirements
- `match.py`: Performs CV-to-job matching analysis
- `score.py`: Calculates compatibility scores
- `final.py`: Generates final reports and rankings
- `cvs.db`: Database storing processed CV data

**Workflow:**
1. **Generate Job Description** - Enter job title, system creates requirements
2. **Upload CVs** - Batch upload PDF resumes for processing
3. **Review Results** - View candidate rankings and compatibility scores
4. **Select Candidates** - Choose top candidates for next steps

### 2. Email Automation (`mail_automation/`)

```bash
python mail_automation/interview.py
```

**Components:**
- `interview.py`: Main email automation script using CrewAI
- `mail.csv`: Template CSV file (name, email, status columns)

**Supported Statuses:**
- `schedule`: Interview scheduling emails
- `reschedule`: Interview rescheduling notifications
- `follow-up`: Follow-up communications
- `rejection`: Polite rejection emails

**Usage:**
1. Prepare CSV file with candidate data
2. Configure email settings and templates
3. Run automated email generation and sending

### 3. Profile Discovery (`scrapping/`)

```bash
python scrapping/linkedin_github.py
```

**Features:**
- **LinkedIn Integration**: Extract profiles from URLs via RapidAPI
- **GitHub Search**: Find technical talent by keywords and location
- **Repository Analysis**: Evaluate coding skills and project contributions
- **Profile Comparison**: Cross-platform talent assessment

## 📁 Project Structure

```
P2M/
├── csv/                     # CSV data files
├── mail_automation/         # Email automation module
│   ├── interview.py        # CrewAI email automation
│   └── mail.csv           # Candidate data template
├── matching_results/        # CV matching outputs
├── parsed_json/            # Structured CV data
├── resume_matching/        # Main CV processing module
│   ├── app.py             # Streamlit web interface
│   ├── cvs.db             # Candidate database
│   ├── final.py           # Report generation
│   ├── job_requirements.py # Job description generator
│   ├── match.py           # CV-job matching engine
│   └── score.py           # Scoring algorithm
├── scrapping/              # Profile discovery module
│   └── linkedin_github.py  # Social media scraping
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
├── README.md              # Project documentation
└── requirements.txt        # Python dependencies
```

## 🔧 System Components

### CV Processing Pipeline
```
CV Upload → Data Extraction → Job Matching → Scoring → Ranking
```
<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/dc923aae-d585-4aed-b439-526e6be23418" width="400"/>
</div>

### Email Automation Agents
- **csv_extractor**: Processes candidate data files
- **email_creator**: Generates personalized email drafts
- **output_formatter**: Formats emails for delivery

<div style="text-align: center;">
  <img src="https://github.com/user-attachments/assets/cbcff207-297f-4145-ae2a-96a57f313a30" width="300"/>
</div>


## 📸 Screenshots

### CV Processing Interface
![Screenshot 2025-06-04 152108](https://github.com/user-attachments/assets/77232807-20cb-4dd7-a108-a150c01b79f9)

### Email Automation Interface
![mail1](https://github.com/user-attachments/assets/000cef84-d879-46ef-bbb1-4e39afe9c5e1)

### Profile Discovery Tools
![linkedin1](https://github.com/user-attachments/assets/550828cf-b720-4d4f-8ca0-eeaac07a1daa)
![github](https://github.com/user-attachments/assets/a15c9898-e2ab-4f92-b50f-3416c8594c21)


