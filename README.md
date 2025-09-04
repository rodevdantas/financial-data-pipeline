# 📊 ETL Pipeline and Interactive Stock Dashboard

This project was developed with the goal of practicing and integrating knowledge in **data engineering**, **cloud automation**, and **interactive visualization**, creating an end-to-end solution for stock market analysis.

## Project Objective

- Build an automated ETL pipeline hosted in the cloud, which collects, transforms, and loads data daily.  
- Create a layered architecture (Bronze, Silver, Gold) for data organization.  
- Make the data available in a low-cost solution (Google Sheets).  
- Connect the processed data to an interactive dashboard in Looker Studio, providing insights into performance and volatility of major market companies.  
- Practice a full-stack data approach, combining data collection, processing, storage, and visualization in a single project.  

## Technologies Used

### 🔹 Google Cloud Platform (GCP)
- **Cloud Functions** → serverless execution of Python code.  
- **Cloud Scheduler** → schedule daily execution of the pipeline.  

### 🔹 Python
- **pandas** → manipulation, cleaning, and transformation of tabular data.  
- **yfinance** → extraction of stock market quotes and information.  
- **logging** → monitoring and traceability of pipeline execution.  

### 🔹 Visualization and Storage
- **Google Sheets** → storage of processed data, acting as a low-cost data lake.  
- **Looker Studio** → creation of an interactive and dynamic dashboard.  

## Solution Architecture

The project follows a layered data architecture:

- **Bronze** → raw data extracted from the Yahoo Finance API.  
- **Silver** → cleaned, standardized, and enriched data.  
- **Gold** → final table with consolidated metrics for analysis.  

**Pipeline flow**:  
`Cloud Scheduler → Cloud Function (ETL in Python) → Google Sheets → Looker Studio`  

## How to Explore

You can simply explore the project by viewing the code or accessing the public links:  

- **Dashboard:** [Looker Studio Dashboard](https://lookerstudio.google.com/u/0/reporting/b1fd8ae3-8545-458c-b6e4-0d2d236d86e5/page/bAjWF)  
- **Processed Data:** [Google Sheets](https://docs.google.com/spreadsheets/d/1H779bzHVLrPaaHEuLEIRsJt1OdSXKBu02GmlhST2EjI/)  

To review the code:  
```
git clone https://github.com/your-username/financial-data-pipeline.git
cd financial-data-pipeline
```

The dashboard shows:  
- **Closing price** → daily and consolidated values per stock.  
- **Total trading volume** → total traded per asset.  
- **Average daily variation** → a measure of volatility.  
- **Company comparison** → trend charts and comparative bar charts.  

**Analyzed companies (tickers):**  
AAPL (Apple), MSFT (Microsoft), GOOGL (Google), AMZN (Amazon), TSLA (Tesla), META (Meta), NVDA (NVIDIA), BRK-B (Berkshire Hathaway), JPM (JPMorgan Chase), JNJ (Johnson & Johnson)

## Project Structure

📂 financial-data-pipeline/  
│  
├── main.py # ETL and execution in Cloud Functions  
├── requirements.txt # List of dependencies  
├── README.md # Project documentation  

## Skills

- **Data Engineering** → ETL, layered modeling, best practices in Python.  
- **Cloud Computing** → use of serverless services and automation with GCP.  
- **Data Analysis** → volatility calculations, financial metrics, and indicators.  
- **Visualization** → building an interactive dashboard in Looker Studio, applying Data Storytelling principles.  
- **End-to-end integration** → automated pipeline combining extraction, transformation, storage, and visual presentation.  

## Notes

This project simulates a real market solution, focusing on **automation, scalability, and UI**.  
More than just extracting data, the goal was to **build a complete data journey**, from back-end to front-end.

