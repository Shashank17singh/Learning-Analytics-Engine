# Learning Analytics Engine

A student assessment platform that generates exams with AI, tracks behavior telemetry, and runs statistical analysis and predictive modeling.

> **Live Deployments:**
> * **Interactive Streamlit App:** [learning-analytics-engine.streamlit.app](https://learning-analytics-engine.streamlit.app/)

---

## Overview

The **Learning Analytics Engine** combines real-time exam delivery with educational data science and generative AI. Students participate in adaptive, syllabus-grounded quizzes while administrators monitor cohort mastery through descriptive statistics, psychometric telemetry, and machine learning models.

The platform uses Retrieval-Augmented Generation (RAG) across multiple LLM providers (Google Gemini, OpenAI, Groq, Anthropic) to extract questions from uploaded PDF course material, storing event telemetry and answer timings in a serverless Supabase PostgreSQL backend.

---

## Architecture Overview

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

| Feature | Description |
| ------- | ----------- |
| **Multi-Provider AI Engine** | Dynamically synthesizes single-choice, multiple-choice, and numerical questions across varying difficulty levels (Easy, Medium, Hard) and target competitive formats (GATE, CAT, UPSC) using Gemini, OpenAI, Groq, or Anthropic |
| **RAG PDF Ingestion** | Extracts and indexes uploaded course syllabi (PDFs) to anchor generated questions directly to official course documents |
| **Cloud PostgreSQL Telemetry** | Serverless Supabase PostgreSQL backend tracking per-question response times, completion percentages, and user sessions |
| **Structured Placement Rounds** | Aptitude, technical MCQ, coding, system design, HR, and mock rounds with format enforcement and AI rubric scoring |
| **Cohort Leaderboards** | Dynamic hall of fame ranking top performers filtered across domains, subjects, and difficulty tiers |
| **Descriptive Analytics** | Score distributions, duration vs. accuracy curves, and competency breakdowns visualized via Seaborn and Matplotlib |
| **Predictive Modeling** | Built-in Scikit-learn pipelines implementing Binary Classification (Pass/Fail) and K-Means clustering (Learner Segmentation) |

---

## Technology Stack

| Component | Technology |
| --------- | ---------- |
| Application Framework | Streamlit, Python 3.11+ |
| Machine Learning | Scikit-Learn, Pandas, NumPy |
| Database & Storage | Supabase (PostgreSQL 15+), Psycopg2 |
| Generative AI Providers | Google Gemini, OpenAI, Groq, Anthropic |
| Data Visualizations | Matplotlib, Seaborn |
| Document Parsing | PyPDF |
| Testing & Quality | pytest, ruff |
| Containerization | Docker |

---

## Project Structure

```
Learning-Analytics-Engine/
├── app.py                      # Main Streamlit web application and routing
├── pages/
│   ├── Student_Portal.py       # Assessment engine and student telemetry dashboard
│   └── Admin_Portal.py         # Cohort analytics, user management, and ML reports
├── auth_utils.py               # Authentication and password hashing routines
├── auth_rules.py               # RBAC permission rules
├── db_utils.py                 # PostgreSQL connection pool and table migrations
├── llm_utils.py                # Multi-LLM provider client and RAG prompt logic
├── analytics.py                # Statistical aggregations and plot generators
├── ml_models.py                # Scikit-learn classification and clustering models
├── placement.py                # Mock interview rounds and rubric evaluation
├── domains_catalog.json        # Pre-configured assessment taxonomies
├── tests/                      # Automated test suite
├── Dockerfile                  # Container definition
├── requirements.txt            # Python dependencies
└── README.md
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+
- A [Supabase Account](https://supabase.com/) with an active PostgreSQL project
- API keys for at least one supported AI provider (Gemini, OpenAI, Groq, or Anthropic)

### 1. Clone the repository

```bash
git clone https://github.com/Shashank17singh/Learning-Analytics-Engine.git
cd Learning-Analytics-Engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure secrets

Create `.streamlit/secrets.toml` in the repository root:

```toml
# Database Connection (Required)
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.your-supabase-url.supabase.co:5432/postgres"

# Administrator Account Setup
ADMIN_PASSWORD="your-secure-admin-password"

# AI Provider Configurations (At least one required)
GEMINI_API_KEY="your-gemini-api-key"
OPENAI_API_KEY="your-openai-api-key"
GROQ_API_KEY="your-groq-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

### 4. Run the application

```bash
streamlit run app.py
```

The application opens locally at `http://localhost:8501`.

---

## Running the Tests

Execute automated tests:

```bash
pytest tests/
```

Run static code analysis and linting:

```bash
ruff check .
```

---

## Deployment

The platform is containerized and deployable to any standard container service:

```bash
docker build -t learning-analytics-engine .
docker run -p 8501:8501 learning-analytics-engine
```

Live deployment is hosted on Streamlit Community Cloud at [learning-analytics-engine.streamlit.app](https://learning-analytics-engine.streamlit.app/).

---

## Known Limitations

- RAG PDF chunking utilizes standard sliding window text splits; complex tables or equations in scanned PDF syllabi require explicit text conversion.
- Code submissions in mock technical rounds are evaluated against rubric criteria via LLM analysis rather than sandboxed runtime execution.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
