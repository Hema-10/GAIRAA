# OTP Generator using Apache Airflow

## Project Overview
Automatically generates a secure six-digit OTP and sends it through Gmail SMTP every five minutes.

## Technologies
- Python
- Apache Airflow 3.1.2
- Docker Compose
- PostgreSQL
- Redis
- Gmail SMTP

## Project Structure
- dags/otp_generator.py
- docker-compose.yaml
- .env.example
- .gitignore
- README.md

## Airflow Variables
- OTP_RECEIVER_EMAIL
- OTP_SENDER_EMAIL

## SMTP Connection
Configure an Airflow connection with ID: gmail_smtp.
Use Gmail SMTP credentials and an app password.

## Run
1. Copy .env.example to .env.
2. Configure your local environment.
3. Run docker compose up airflow-init.
4. Run docker compose up -d.
5. Open http://localhost:8080.
6. Configure the SMTP connection and Airflow Variables.
7. Enable the otp_generator DAG.

## Security
- Uses Python secrets for OTP generation.
- Does not print OTP values in logs.
- Keeps email addresses in Airflow Variables.
- Never commit real credentials.

## Limitation
The DAG sends an OTP and displays a five-minute validity message. OTP verification and actual expiry enforcement are not implemented.
