<div align="center">

# Learning Analytics Engine

**An intelligent student assessment platform that dynamically generates AI-driven exams, tracks user behavior telemetry, and performs statistical analysis and predictive modeling.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Backend-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Generative AI](https://img.shields.io/badge/Multi--LLM-Gemini%20|%20OpenAI%20|%20Groq%20|%20Anthropic-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)](https://aistudio.google.com/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

</div>

---

## Overview

The **Learning Analytics Engine** is a comprehensive educational platform that merges real-time assessment delivery with advanced data science and generative AI. It allows students to take AI-generated, customized quizzes while administrators gain deep insights into cohort performance through interactive, predictive analytics. 

The platform leverages **Retrieval-Augmented Generation (RAG)** via multiple LLM providers (Google Gemini, OpenAI, Groq, Anthropic) to synthesize quiz questions from user-uploaded PDF study materials, and relies on a persistent **Supabase PostgreSQL** backend for seamless behavioral telemetry.

---

### System Architecture

```mermaid
graph TD
    subgraph "Generative AI / LLM Layer"
    I[Gemini / OpenAI / Groq / Anthropic]
    end

    subgraph "Application Layer"
    A[Admin Portal] -->|Manage Data| B[(Supabase PostgreSQL)]
    C[Student Portal] -->|Telemetry & Results| B
    C <-->|RAG PDF Chunking & Prompting| I
    end
    
    subgraph "Data Science & Analytics Layer"
    B --> D{Data Ingestion & Cleaning}
    D --> E[Pandas DataFrames]
    E --> F[Exploratory Data Analysis]
    E --> G[Scikit-Learn ML Models]
    end
    
    subgraph "Presentation Layer"
    F --> H[Streamlit UI Visualizations]
    G --> H
    end
    
    classDef io fill:#f9f0ff,stroke:#8a2be2,stroke-width:2px,color:#000;
    classDef core fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#000;
    classDef logic fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#000;
    classDef ext fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000;
    
    class A,C,H io;
    class B,E core;
    class D,F,G logic;
    class I ext;
```

---

## Features

| Capability | Description |
|---|---|
| **Multi-Provider AI Engine** | Dynamically generates custom, on-the-fly multiple-choice questions tailored to the user's selected difficulty. Supports **Google Gemini, OpenAI, Groq, and Anthropic** APIs. |
| **RAG PDF Ingestion** | Upload your own course material (PDFs) and let the engine extract context, synthesize data, and generate high-quality examination questions based strictly on the syllabus provided. |
| **Cloud PostgreSQL Backend** | Integrated with **Supabase Serverless PostgreSQL** for permanent, robust data persistence of user logins, telemetry, and analytics records. |
| **Dynamic Leaderboards** | Real-time, grouped hall of fame with explicit ranking. Filter top performers dynamically across specific Domains, Subjects, or Difficulty levels (Easy, Medium, Hard). |
| **Personalized Analytics** | Students have access to a dedicated analytics tab showcasing their own personal seaborn charts (Score Distribution, Duration vs. Score, and Competency Breakdown). |
| **Machine Learning** | Implements Binary Classification (Pass/Fail), Regression (Score Prediction), and K-Means Clustering (Learner Segmentation). |

---

## Tech Stack

- **Machine Learning & Analytics:** Scikit-Learn · Pandas · NumPy
- **Software Engineering:** Python · Psycopg2 · PostgreSQL (Supabase)
- **Generative AI (LLMs):** Google Gemini · OpenAI · Groq · Anthropic
- **Visualizations:** Matplotlib · Seaborn · Streamlit
- **Document Processing:** PyPDF (RAG Ingestion)

---

## Directory Structure

```
Learning-Analytics-Engine/
│
├── app.py                              # Main Streamlit Web Application (Authentication & Routing)
├── pages/                              # Streamlit Multi-Page Components
│   ├── 1_Student_Portal.py             # Interactive Assessment Engine & Student Dashboard
│   └── 2_Admin_Portal.py               # Secure Admin Auth, User Management & Analytics
├── auth_utils.py                       # Secure Authentication & Password Hashing
├── db_utils.py                         # Supabase PostgreSQL Connection & Schema Setup
├── llm_utils.py                        # Multi-LLM Provider API Integrations & RAG Logic
├── analytics.py                        # EDA & Descriptive Statistics Logic
├── ml_models.py                        # Scikit-learn Modeling Pipelines (Clustering, Regression)
│
├── Learning_Analytics_EDA.ipynb        # Comprehensive Jupyter Notebook for offline EDA
├── domains_catalog.json                # Pre-defined assessment domains & subjects catalog
└── README.md                           # Project Documentation
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- A [Supabase Account](https://supabase.com/) with a running PostgreSQL project
- API Keys for one or more supported providers (Gemini, OpenAI, Groq, Anthropic)

### 1. Clone the Repository

```bash
git clone https://github.com/Shashank17singh/Learning-Analytics-Engine.git
cd Learning-Analytics-Engine
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys & Database URL

The app requires a PostgreSQL database URL for telemetry, and API keys for generating AI-powered assessment questions. Create a `.streamlit/secrets.toml` file in the project root:

```toml
# Database Connection (Required)
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.your-supabase-url.supabase.co:5432/postgres"

# AI Provider Configurations
# Note: You only need the key for the provider(s) you intend to use. 
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
GROQ_API_KEY="your-groq-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 4. Launch the Dashboard

Once the dependencies are installed and the secrets are configured, launch the Streamlit app:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Key Workflows

1. **Dynamic RAG Generation:** Generates real-time, context-aware assessments via external LLM APIs based on student uploaded PDFs or categorized domains.
2. **Immediate Feedback Loop:** Submitting an assessment provides students with instant grading and transparent AI-generated explanations for incorrect answers.
3. **End-to-End Tracking:** Student actions (time taken, accuracy, domain chosen) are captured in PostgreSQL, rendered cleanly with standardized dates/times, and analyzed dynamically using Pandas.
4. **Statistical Rigor & Visualization:** Computes standard deviation, IQR, and Pearson correlation coefficients to identify conceptual bottlenecks. Visualized cleanly via Matplotlib and Seaborn for both students and admins.
5. **Predictive Modeling:** Trains Random Forest and Logistic Regression models on-the-fly to predict student success based on behavioral telemetry.

---

## Deployment

- **Dashboard URL:** [https://learning-analytics-engine.streamlit.app/](https://learning-analytics-engine.streamlit.app/)
