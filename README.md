# The Architects 👨‍💻
 
## Team Members
 
| Name | Email |
|---|---|
| Dorcase Lesly Nana Tounda | d.nanatoun@alustudent.com |
| Migisha Olivier | o.migisha@alustudent.com |
| Stephane Tchatchum Chassem | stephanetchatchum@gmail.com / t.stephane@alustudent.com |
 
## Project Description
 
This project processes Mobile Money (MoMo) SMS transaction data provided in XML format. The system parses the raw messages, cleans and normalizes the data (phone numbers, amounts, dates), categorizes each transaction (deposit, withdrawal, payment, airtime purchase, failed transaction, etc.), and loads it into a MySQL database. A frontend dashboard then displays the processed data through charts and tables, allowing users to analyze transaction patterns such as total volume per category or most common transaction types.
 
The project also exposes the processed transactions through a secure REST API built in plain Python (`http.server`) and compares search strategies (linear search, dictionary lookup, binary search) on the transaction data.
 
## System Architecture
 
Diagram: https://drive.google.com/file/d/1S9XQpp4Zy9GHpasJ5rH_kUblvPkCtMb0/view?usp=drive_link
 
Flow: XML file → ETL pipeline (parse, clean, categorize) → MySQL database → REST API (Basic Auth, CRUD) → Frontend dashboard
 
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
 
## XML Parsing & DSA (Week 3)
 
`dsa/parse_xml_file.py` parses `modified_sms_v2.xml` into a list of JSON objects saved to `data/processed/transactions.json` (1,691 records). The XML stores transaction details only inside the free-text SMS `body`, so transaction type, amount, sender, receiver, fee, balance and transaction ID are extracted with regular expressions.
 
`dsa/dsa_compare.py` compares three ways of finding a transaction by ID, on the first 20 records and on the full dataset:
 
- **Linear search:** scans the list record by record, O(n).
- **Dictionary lookup:** `id -> transaction` hash map, O(1) on average.
- **Binary search:** halves a sorted list at each step, O(log n).
On the full dataset, dictionary lookup was about two orders of magnitude faster than linear search. Exact timings vary by machine; the recorded run is in [`docs/dsa_results.txt`](docs/dsa_results.txt).
 
## REST API & Security (Week 3)
 
The API (in `api/`) is built with Python's `http.server` and serves the parsed transactions on `http://localhost:8000`.
 
| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions` | List all transactions |
| GET | `/transactions/{id}` | View one transaction |
| POST | `/transactions` | Add a new transaction |
| PUT | `/transactions/{id}` | Update an existing transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |
 
Required fields for POST and PUT: `transaction_type`, `amount` (must be a number), `sender`, `receiver`.
 
**Authentication:** every endpoint is protected with HTTP Basic Auth. Missing or invalid credentials return `401 Unauthorized` with the header `WWW-Authenticate: Basic realm="MoMo API"`. The credentials are read from the environment variables `API_USERNAME` and `API_PASSWORD` (development defaults: `admin` / `secret`).
 
**Validation:** invalid IDs and bad request bodies return `400`, unknown IDs return `404`, and all errors are JSON in the form `{"error": "..."}`.
 
Full requests, responses and error codes are in [`docs/api_docs.md`](docs/api_docs.md). Screenshots of the curl tests (successful GET, 401, POST, PUT, DELETE) are in [`screenshots/`](screenshots/).
 
Basic Auth only base64-encodes credentials (it does not encrypt them) and has no expiry, revocation or roles, so it should only be used over HTTPS. Stronger alternatives (JWT, OAuth 2.0) are discussed in the project report.
 
## Project Structure
 
```
├── README.md               # Setup, run, overview
├── .env.example             # DATABASE_URL or path to SQLite
├── requirements.txt         # Python dependencies
├── index.html                # Dashboard entry (static)
├── web/                      # Dashboard styling and JS
├── data/
│   ├── raw/                  # Provided XML input
│   ├── processed/            # Cleaned/derived outputs (incl. transactions.json)
│   ├── db.sqlite3            # SQLite DB file
│   └── logs/                 # ETL logs
├── etl/                      # Parsing, cleaning, categorizing, loading scripts
├── api/                      # REST API server (http.server, Basic Auth, CRUD)
├── dsa/
│   ├── parse_xml_file.py     # XML -> JSON parser
│   └── dsa_compare.py        # Linear vs dictionary vs binary search benchmark
├── database/
│   └── database_setup.sql    # Database schema, constraints, and sample data
├── docs/
│   ├── erd_diagram.png       # Entity Relationship Diagram
│   ├── architechture.png     # System architecture diagram
│   ├── api_docs.md           # REST API endpoint documentation
│   └── dsa_results.txt       # DSA benchmark output
├── screenshots/              # curl test evidence for the API
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
### Running the REST API and DSA comparison
 
Run these from the repository root (on Windows, use `py` if `python` is not recognized).
 
1. Parse the XML into JSON:
```bash
   python dsa/parse_xml_file.py data/raw/modified_sms_v2.xml
```
   Expected output: `Parsed 1691 records -> .../data/processed/transactions.json (unclassified: 0)`
2. Run the DSA comparison (prints the tables and saves them to `docs/dsa_results.txt`):
```bash
   python dsa/dsa_compare.py
```
3. (Optional) Set your own API credentials:
```bash
   # macOS / Linux / Git Bash
   export API_USERNAME=myuser
   export API_PASSWORD=mypassword
 
   # Windows PowerShell
   $env:API_USERNAME="myuser"; $env:API_PASSWORD="mypassword"
```
4. Start the API server (replace `server.py` with the actual file name in `api/`):
```bash
   python api/server.py
```
5. Test it with curl (in PowerShell use `curl.exe`):
```bash
   # List all transactions
   curl -u admin:secret http://localhost:8000/transactions
 
   # Wrong credentials -> 401
   curl -i -u admin:wrong http://localhost:8000/transactions
 
   # Create
   curl -u admin:secret -X POST -H "Content-Type: application/json" \
     -d '{"transaction_type":"payment","amount":500,"sender":"You","receiver":"Test"}' \
     http://localhost:8000/transactions
 
   # Update
   curl -u admin:secret -X PUT -H "Content-Type: application/json" \
     -d '{"transaction_type":"payment","amount":999,"sender":"You","receiver":"Updated"}' \
     http://localhost:8000/transactions/1
 
   # Delete
   curl -u admin:secret -X DELETE http://localhost:8000/transactions/1
```
 
## Team Task Sheet
 
Team Task Sheet week 2: https://docs.google.com/spreadsheets/d/1uXz-sH-oNDaBkWZBpQvr6HRq_AZWBfH5yAPg-5yXXqA/edit?gid=0#gid=0
 
Team Task Sheet week 3: https://docs.google.com/spreadsheets/d/1cA_YjZg5WW1m2F5SEw1XdaNt5yW8OGGPCeXsBfc6p0c/edit?gid=0#gid=0
 
## Scrum Board
 
Board: https://github.com/users/Edenoliver19/projects/1
