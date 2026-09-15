# The Architects 👨‍💻

## Team Members

| Name | Email |
|---|---|
| Dorcase Lesly Nana Tounda | d.nanatoun@alustudent.com |
| Migisha Olivier | o.migisha@alustudent.com |
| Stephane Tchatchum Chassem | stephanetchatchum@gmail.com / t.stephane@alustudent.com |

## Project Description

This project processes Mobile Money (MoMo) SMS transaction data provided in XML format. The system parses the raw messages, cleans and normalizes the data (phone numbers, amounts, dates), categorizes each transaction (deposit, withdrawal, payment, airtime purchase, failed transaction, etc.), and loads it into a MySQL database. A frontend dashboard then displays the processed data through charts and tables, allowing users to analyze transaction patterns such as total volume per category or most common transaction types.

## System Architecture

Diagram: https://drive.google.com/file/d/1S9XQpp4Zy9GHpasJ5rH_kUblvPkCtMb0/view?usp=drive_link

Flow: XML file → ETL pipeline (parse, clean, categorize) → MySQL database → API (optional) → Frontend dashboard

## Database Design (Week 2)

Our database is built around five tables: `Users`, `Transactions`, `Transaction_Categories`, `Transaction_Map` (a junction table), and `System_Logs`.

- **Users** stores anyone who sends or receives money. A single unified table is used (rather than separate Sender/Receiver tables) since the same person can act as either role across different transactions.
- **Transactions** is the core table, referencing `Users` twice via `senderId` and `receiverId` foreign keys, capturing both roles in one transaction record without duplicating personal data.
- **Transaction_Categories** holds the fixed list of transaction types (e.g. Deposit, Withdrawal, Payment, Airtime).
- **Transaction_Map** is a junction table resolving the many-to-many relationship between `Transactions` and `Transaction_Categories`, since a transaction may reasonably carry more than one category tag.
- **System_Logs** tracks our own ETL pipeline's processing events (successes, warnings, errors) independently of the financial data. Its `transactionId` foreign key is nullable, since some log entries (e.g. parsing failures on malformed SMS text) occur before any transaction record exists.

The full ERD, design rationale, data dictionary, sample queries, and constraint documentation are available in the **Database Design Document** and in [`docs/erd_diagram.png`](docs/erd_diagram.png).

Database Design Document (PDF): https://github.com/TCStephane/SMS-Team/blob/main/Database_Design_Document_The_Architects.pdf

### Security & Accuracy Rules

Our schema enforces data integrity through: Primary Key constraints (unique record identity), NOT NULL constraints (required fields), UNIQUE constraints (e.g. one phone number per user), CHECK constraints (preventing negative financial values), Foreign Key constraints (referential integrity between tables), and `ON DELETE CASCADE` / `ON DELETE SET NULL` rules to handle dependent records safely when a parent record is removed.

## Project Structure

```
├── README.md               # Setup, run, overview
├── .env.example             # DATABASE_URL or path to SQLite
├── requirements.txt         # Python dependencies
├── index.html                # Dashboard entry (static)
├── web/                      # Dashboard styling and JS
├── data/
│   ├── raw/                  # Provided XML input
│   ├── processed/            # Cleaned/derived outputs
│   ├── db.sqlite3            # SQLite DB file
│   └── logs/                 # ETL logs
├── etl/                      # Parsing, cleaning, categorizing, loading scripts
├── api/
├── database/
│   └── database_setup.sql    # Database schema, constraints, and sample data
├── docs/
│   ├── erd_diagram.png       # Entity Relationship Diagram
│   └── architechture.png     # System architecture diagram
├── examples/
│   └── json_schemas.json     # JSON representations of database entities
├── scripts/                  # Shell scripts to run ETL / serve frontend
└── tests/                    # Unit tests
```

## Getting Started

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up the database: run the SQL script in `database/database_setup.sql` against a MySQL instance
4. Place the raw XML file in `data/raw/`
5. Run the ETL pipeline: `bash scripts/run_etl.sh`
6. Serve the frontend: `bash scripts/serve_frontend.sh`

## Team Task Sheet

Team Task Sheet: https://docs.google.com/spreadsheets/d/1uXz-sH-oNDaBkWZBpQvr6HRq_AZWBfH5yAPg-5yXXqA/edit?gid=0#gid=0

## Scrum Board

Board: https://github.com/users/Edenoliver19/projects/1
