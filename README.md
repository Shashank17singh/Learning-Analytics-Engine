<div align="center">

# Learning Analytics Engine

**An end-to-end Python assessment platform and Data Science Analytics dashboard for educational insights.**

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)

</div>

---

## Overview

Built an unsupervised K-Means clustering pipeline to segment student learning patterns and performance metrics. Designed the architecture to scale via SQLite, leveraging Seaborn for deep exploratory data analysis and deploying the interactive analytics engine via Streamlit.

---

### System Architecture

```mermaid
graph TD
    subgraph "Application Layer"
    A[Admin Portal] -->|Manage| B(SQLite Database)
    C[Student Portal] -->|Take Assessment| B
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
    
    class A,C,H io;
    class B,E core;
    class D,F,G logic;
```

## Features

| Capability | Description |
|---|---|
| **Assessment Engine** | A secure platform supporting candidate registration, timed assessmentzes, reviews, and leaderboard rankings. |
| **Exploratory Data Analysis** | Automated descriptive statistics, competency segmentation, and statistical correlations (e.g., reviews requested vs. final score). |
| **Machine Learning** | Implements Binary Classification (Pass/Fail), Regression (Score Prediction), and K-Means Clustering (Learner Segmentation). |
| **Interactive Dashboard** | Provides a modern, reactive interface to interact with real-time cohort analytics, histograms, and correlation heatmaps. |

---

## Tech Stack

**Machine Learning & Analytics** - Scikit-Learn · Pandas · NumPy
**Software Engineering** - Python · SQLite3 
**Visualizations** - Matplotlib · Seaborn · Streamlit
**Environment** - Jupyter Notebooks · Git

---

## Directory Structure

```
Learning-Analytics-Engine/
│
├── app.py                              # Modern Streamlit Web Application (Main Web Dashboard)
├── main.py                             # Main CLI Entry Point & Menu Router
├── admin.py                            # Secure Admin Authentication & Role Management
├── assessment_mgmt.py                         # Assessment Question CRUD & Robust CSV Loader
├── assessment_engine.py                             # Interactive Assessment Taking Engine (Timing & Reviews)
├── leaderboard.py                      # Real-Time Ranked Leaderboard Module
├── analytics.py                        # EDA & Descriptive Statistics (Pandas, NumPy)
├── visualizer.py                       # Visual Dashboards & Charts (Matplotlib, Seaborn)
├── ml_models.py                        # Scikit-learn Modeling Pipelines
│
├── Learning_Analytics_EDA.ipynb    # Complete Interactive Jupyter Notebook
├── assessment_engine.csv                            # Bulk Question Bank (100+ Curated Questions)
├── qms.db                              # SQLite3 Database
└── README.md                           # You are here
```

---

## Setup and Installation

### Prerequisites

- Python 3.11+

### 1. Clone the Repository

```bash
git clone https://github.com/Shashank17singh/Learning-Analytics-Engine.git
cd Learning-Analytics-Engine
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Launch the Dashboard

Once the dependencies are installed, launch the Streamlit app to interact with the assessment engine and analytics platform.

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## Key Analytics Workflows

1. **End-to-End Tracking:** User actions (reviews taken, time elapsed) are captured in SQLite and analyzed dynamically using Pandas and Seaborn.
2. **Statistical Rigor:** Computes standard deviation, IQR, and Pearson correlation coefficients to identify conceptual bottlenecks.
3. **Predictive Modeling:** Trains Random Forest and Logistic Regression models on-the-fly to predict student success based on behavioral telemetry.


---

## Deployment
- **Dashboard URL:** https://learning-analytics-engine.streamlit.app/
