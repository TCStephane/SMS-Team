# The Architects 👨‍💻

## Team Members
| Name | Email |
|---|---|
| Dorcase Lesly Nana Tounda | d.nanatoun@alustudent.com |
| Migisha Olivier | o.migisha@alustudent.com |
| Stephane Tchatchum Chassem | stephanetchatchum@gmail.com/t.stephane@alustudent.com |

## Project Description
This project processes Mobile Money (MoMo) SMS transaction data provided in XML format. The system parses the raw messages, cleans and normalizes the data (phone numbers, amounts, dates), categorizes each transaction (deposit, withdrawal, payment, airtime purchase, failed transaction, etc.), and loads it into a SQLite database. A frontend dashboard then displays the processed data through charts and tables, allowing users to analyze transaction patterns such as total volume per category or most common transaction types.

## System Architecture
Diagram: [Add draw.io / Miro link here]

Flow: XML file → ETL pipeline (parse, clean, categorize) → SQLite database → API (optional) → Frontend dashboard

## Scrum Board
Board: [Add Trello / GitHub Projects / Jira link here]

## Project Structure
```
├── README.md            # Setup, run, overview
├── .env.example          # DATABASE_URL or path to SQLite
├── requirements.txt      # Python dependencies
├── index.html             # Dashboard entry (static)
├── web/                   # Dashboard styling and JS
├── data/
│   ├── raw/               # Provided XML input
│   ├── processed/         # Cleaned/derived outputs
│   ├── db.sqlite3         # SQLite DB file
│   └── logs/              # ETL logs
├── etl/                   # Parsing, cleaning, categorizing, loading scripts
├── api/                   
├── scripts/               # Shell scripts to run ETL / serve frontend
└── tests/                 # Unit tests
```

## Getting Started
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Place the raw XML file in `data/raw/`
4. Run the ETL pipeline: `bash scripts/run_etl.sh`
5. Serve the frontend: `bash scripts/serve_frontend.sh`
