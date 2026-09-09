#  Quiz Management System (Python for Data Science & Analytics)

[![Python 3.x](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![Data Science](https://img.shields.io/badge/Domain-Python%20for%20Data%20Science-orange.svg)]()
[![Data Analytics](https://img.shields.io/badge/Analytics-Pandas%20%7C%20NumPy-brightgreen.svg)]()
[![Visualizations](https://img.shields.io/badge/Visuals-Seaborn%20%7C%20Matplotlib-blueviolet.svg)]()
[![Web App](https://img.shields.io/badge/UI-Streamlit-red.svg)]()
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)]()

> **Certification Context:**  
> Developed as part of the **Summer Training & Internship Program** on **"Python for Data Science"** conducted by **E & ICT Academy, IIT Kanpur** (A Joint Initiative of MeitY & IIT Kanpur).  
> **Student:** Shashank Singh.

---

##  Executive Summary

The **Quiz Management System** is an end-to-end Python project showcasing both **Software Engineering / Database Management** and **Applied Data Science & Business Intelligence Analytics**.

It features a dual-layer architecture:
1. **Interactive Assessment Engine (Application Layer):** A secure assessment platform supporting candidate registration, timed quiz taking with hints, instant score evaluation, leaderboard rankings, and administrator question repository management (CRUD & CSV bulk loading).
2. **Data Analytics & BI Dashboard (Data Science Layer):** A professional analytics dashboard powered by **Pandas, NumPy, Matplotlib, Seaborn, and Streamlit** that transforms raw relational assessment logs into actionable pedagogical insights, engagement correlations, score distributions, and performance segmentation.

---

##  System Architecture

```
                               +------------------------------------------+
                               |        Quiz Management System            |
                               |    (Web Dashboard & CLI Interface)       |
                               +------------------------------------------+
                                      /             |            \
                                     /              |             \
            +-----------------------+   +-------------------+   +----------------------------+
            | Admin Portal          |   | Quiz & Leaderboard|   | Data Science & Analytics   |
            | (admin.py, quizmgmt)  |   | (quiz.py, lboard) |   | Dashboard (app.py, anlyt.) |
            +-----------------------+   +-------------------+   +----------------------------+
                        \                     /                                |
                         \                   /                                 |
                     +---------------------------+            +------------------------------+
                     |   SQLite3 Database Engine |            |  Data Science Analytics Stack|
                     |         (qms.db)          |            |  - Pandas: DataFrames & Stats|
                     | - login (auth)            |----------->|  - NumPy: Numerical Metrics  |
                     | - questions (assessment)  |            |  - Matplotlib & Seaborn      |
                     | - leaderboard (ranks)     |            +------------------------------+
                     | - attempts (time & hints) |                             |
                     +---------------------------+                             v
                                                              +------------------------------+
                                                              | Visual Dashboards & Reports  |
                                                              | - Streamlit Web UI (:8501)   |
                                                              | - charts/*.png               |
                                                              | - Jupyter Notebook (.ipynb)  |
                                                              +------------------------------+
```

---

##  Data Science & Analytics Capabilities

This project implements all core competencies required in professional Data Science and Analytics roles:

### 1. Data Ingestion & Preprocessing (SQL & Pandas)
- Automatic extraction of relational attempt logs from SQLite into **Pandas DataFrames**.
- Automated type conversions, datetime parsing, and null-safety verification.

### 2. Exploratory Data Analysis (EDA) & Summary Statistics
- **Descriptive Statistics:** Mean (66.56%), Median (70.00%), Standard Deviation (21.95%), Interquartile Range (IQR = 30.00%), Minimum/Maximum scores.
- **Statistical Correlations (Pearson's $r$):**
  - Hints Requested vs. Final Score ($r \approx -0.81$): Identifies cognitive difficulty patterns.
  - Completion Duration vs. Final Score ($r \approx -0.75$): Analyzes pacing and conceptual struggle.
  - Hints Requested vs. Duration ($r \approx +0.35$): Measures active engagement duration added by hints.
- **Competency Segmentation:** Automatic categorical binning into *Distinction (75-100%)*, *Competent (50-74%)*, and *Needs Improvement (<50%)*.

### 3. Publication-Grade Visual Analytics (Matplotlib & Seaborn)
The interactive dashboard provides real-time visualization of:
- **Score Distribution (KDE & Histogram):** Visualizes performance variance with Mean and Median reference thresholds.
- **Completion Time vs. Score Percentage:** Multi-class scatter plot with linear regression trendline indicating pass/fail boundaries.
- **Hint Usage Impact (Boxplot):** Statistical boxplot demonstrating how hint frequency affects score spread.
- **Competency Tier Breakdown (Donut Chart):** Proportional breakdown of learner classifications.
- **Correlation Heatmap:** Complete matrix quantifying engagement behavior vs. outcome.

---

##  Project Structure

```
Shashank Singh Quiz_Management_System_Final (1)/
│
├── app.py                              # Modern Streamlit Web Application (Main Web Dashboard)
├── main.py                             # Main CLI Entry Point & Menu Router
├── admin.py                            # Secure Admin Authentication & Role Management
├── quizmgmt.py                         # Quiz Question CRUD & Robust CSV Loader
├── quiz.py                             # Interactive Quiz Taking Engine (Timing & Hints)
├── leaderboard.py                      # Real-Time Ranked Leaderboard Module
├── analytics.py                        # EDA & Descriptive Statistics (Pandas, NumPy)
├── visualizer.py                       # Visual Dashboards & Charts (Matplotlib, Seaborn)
├── ds_dashboard.py                     # Data Science CLI Dashboard
│
├── Quiz_Data_Science_Analysis.ipynb    # Complete Interactive Jupyter Notebook
├── quiz.csv                            # Bulk Question Bank (100+ Curated Questions)
├── qms.db                              # SQLite3 Database (Schema: login, questions, leaderboard, attempts)
├── charts/                             # Exported High-Resolution Analytics Figures
├── requirements.txt                    # Cloud Deployment Dependencies
├── .gitignore                          # Clean Version Control Rules
└── README.md                           # Comprehensive Technical Documentation
```

---

##  How to Run the Project

### 1. Launch the Modern Web Dashboard (Recommended)
```bash
streamlit run app.py
```
Open your browser at **`http://localhost:8501`**.

The Web App features 4 dedicated tabs:
1.  **Data Science & Analytics Dashboard:** Real-time KPI cards, interactive tier filters, name search, Seaborn charts, correlation heatmap, and CSV export.
2.  **Play Quiz:** Interactive candidate assessment with timer, hint expander, and instant balloons result.
3.  **Live Leaderboard:** Real-time ranks (, , ) with progress bars.
4.  **Admin Portal:** Secure management (Username: `admin`, Password: `admin123`) for question editing and CSV bulk uploads.

### 2. Launch the Terminal Console Interface
```bash
python main.py
```

### 3. Open the Interactive Jupyter Notebook
```bash
jupyter notebook Quiz_Data_Science_Analysis.ipynb
```

---

##  1-Click Free Cloud Deployment (Streamlit Cloud)

To get a live public portfolio link for your resume and LinkedIn:
1. Push this repository to **GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Quiz Management System - Python for Data Science"
   git branch -M main
   git remote add origin https://github.com/<YOUR_USERNAME>/quiz-management-datascience.git
   git push -u origin main
   ```
2. Visit **[share.streamlit.io](https://share.streamlit.io/)**, sign in with GitHub, select your repository, specify `app.py`, and click **Deploy**.
3. You will receive a permanent live URL (e.g. `https://shashank-quiz-management.streamlit.app`).

---

##  Key Talking Points for Technical Interviews

When explaining this project in an interview or viva:
1. **End-to-End Ownership:** *"I developed both the operational data collection application and the downstream analytics pipeline. User actions like hints taken and time elapsed are captured in SQLite and analyzed using Pandas and Seaborn."*
2. **Statistical Rigor:** *"Rather than looking at simple averages, I computed standard deviation, IQR, and Pearson correlation coefficients ($r \approx -0.81$ between hints and score) to identify where students experience conceptual bottlenecks."*
3. **Business & Educational Impact:** *"The analytics dashboard allows course coordinators to identify challenging questions and segment learners into competency tiers for targeted intervention."*
