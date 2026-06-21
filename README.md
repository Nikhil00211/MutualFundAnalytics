Mutual Fund Analytics

A Python-based data analytics project exploring the Indian mutual fund industry through data ingestion, validation, live NAV integration, and exploratory analysis across fund-level, investor-level, and market-level datasets.

Table of Contents

- Overview
- Features
- Datasets
- Project Structure
- Technologies Used
- Setup
- Usage
- Completed Tasks
- Future Work
- Author

Overview

This project analyzes mutual fund industry data using Python and Pandas. It covers the complete data pipeline from raw data ingestion and validation to profiling and live NAV integration using the MFAPI API.

The objective is to build a reliable and validated analytical foundation that can be used for exploratory data analysis, performance evaluation, investor behavior analysis, and future dashboard development.

Features

- Automated data ingestion and profiling of multiple CSV datasets
- Missing value detection and duplicate record analysis
- Data type validation and summary statistics generation
- AMFI code referential integrity validation across datasets
- Categorical consistency analysis for fund houses, categories, plans, and risk classifications
- Live NAV data integration through MFAPI
- Historical NAV tracking for multiple mutual fund schemes
- Foundation for exploratory data analysis and dashboard development

Datasets

All datasets are stored in "data/raw/".

File| Description
01_fund_master.csv| Scheme-level master data including fund house, category, expense ratio, fund manager, and risk classification
02_nav_history.csv| Historical daily NAV data for mutual fund schemes
03_aum_by_fund_house.csv| Assets Under Management trends across fund houses
04_monthly_sip_inflows.csv| Monthly SIP inflow trends across the industry
05_category_inflows.csv| Mutual fund category-wise inflow data
06_industry_folio_count.csv| Industry-wide investor folio statistics
07_scheme_performance.csv| Returns, alpha, beta, Sharpe ratio, drawdown, and ratings
08_investor_transactions.csv| Investor-level transaction records
09_portfolio_holdings.csv| Portfolio composition and stock holdings
10_benchmark_indices.csv| Benchmark index history including market indices

Project Structure

MutualFundAnalytics/
│
├── data/
│   └── raw/
│
├── data_ingestion.py
├── live_nav_fetch.py
├── amfi_validation.py
├── fund_master_analysis.py
│
├── requirements.txt
└── README.md

Technologies Used

- Python 3
- Pandas
- Requests
- Git
- GitHub
- Visual Studio Code

Setup

git clone https://github.com/Nikhil00211/MutualFundAnalytics.git
cd MutualFundAnalytics

python -m venv venv

venv\Scripts\activate
# Windows

source venv/bin/activate
# Linux / macOS

pip install -r requirements.txt

Usage

Run Data Ingestion

python data_ingestion.py --folder data/raw

Fetch Live NAV Data

python live_nav_fetch.py

Validate AMFI Code Integrity

python amfi_validation.py

Run Categorical Consistency Analysis

python fund_master_analysis.py

Completed Tasks

- Project setup and repository configuration
- Data ingestion and profiling
- Missing value analysis
- Duplicate record validation
- Data type verification
- AMFI code referential integrity validation
- Categorical consistency analysis
- Live NAV integration through MFAPI
- Git version control and GitHub deployment

Future Work

- Exploratory Data Analysis (EDA)
- Fund performance benchmarking
- SIP trend analysis
- Investor demographic analysis
- Data visualization using Matplotlib and Plotly
- Interactive Streamlit dashboard
- Mutual fund recommendation engine
- Portfolio analytics and risk evaluation

Author

Nikhil

Bachelor of Engineering in Computer Science and Engineering (Cybersecurity)

GitHub: https://github.com/Nikhil00211
