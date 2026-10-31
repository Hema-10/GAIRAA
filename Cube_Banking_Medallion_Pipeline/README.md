# Banking Analytics Pipeline — MySQL Version

This educational project uses **MySQL 8**, Python, synthetic banking data, Medallion architecture (Bronze/Silver/Gold), an Airflow DAG, logging, retries, error handling, tests, and 15 business-insight queries.

## Windows setup
1. Install MySQL Server 8 and create a database:
   ```sql
   CREATE DATABASE banking_analytics;
   ```
2. Extract this ZIP and open the folder in VS Code.
3. Create a virtual environment and install dependencies:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and set your MySQL username/password.
5. Generate synthetic CSV data:
   ```powershell
   python -m src.generate_data
   ```
6. Create tables and run the pipeline:
   ```powershell
   python main.py
   ```
7. Run business insight queries:
   ```powershell
   python -m src.insights
   ```
8. Run tests:
   ```powershell
   pytest -v
   ```

## Airflow
The DAG is in `dags/banking_analytics_dag.py`. Airflow must be installed/configured separately and the project root must be on `PYTHONPATH`. The DAG retries failed runs three times.

## Medallion layers
- Bronze: ingestion batch audit table and raw synthetic CSV files in `data/`.
- Silver: cleaned relational banking tables.
- Gold: daily branch/channel KPIs, monthly loan KPIs, and fraud-alert KPIs.

All records are synthetic. This is a learning/demo pipeline, not core banking software. Rule-based alerts are review signals, not proof of fraud.

## Cube analytics API

Cube exposes a semantic analytics layer over the banking MySQL tables. Its model files are in `cube/schema/` and include transactions, accounts, branches, customers, loans, and loan payments. Transaction measures include counts, successful/failed counts, total value, and average value; loan and payment measures cover principal and repayments.

### Start Cube

Make sure MySQL is running and that `.env` contains the same connection settings used by the Python pipeline. Docker Desktop on Windows provides `host.docker.internal` so Cube can connect to the MySQL server on your machine.

```powershell
docker compose up -d cube
docker compose logs -f cube
```

Open **http://localhost:4000** for Cube Playground. Use `banking-cube` as the model and inspect the measures and dimensions. The Cube API uses the `CUBEJS_API_SECRET` value from Compose (default: `local-dev-secret-change-me`). Set a private value in `.env` before using beyond local learning.

Example: successful transaction value grouped by channel:

```powershell
$body = @{
  query = @{
    measures = @('Transactions.successfulAmount')
    dimensions = @('Transactions.channel')
  }
} | ConvertTo-Json -Depth 5
Invoke-RestMethod -Method Post -Uri 'http://localhost:4000/cubejs-api/v1/load' `
  -Headers @{ Authorization = 'Bearer local-dev-secret-change-me' } `
  -ContentType 'application/json' -Body $body
```

Stop the analytics service with `docker compose stop cube`. Cube is an additional analytics API; it reads the relational tables created and populated by the existing Python/Airflow pipeline.
