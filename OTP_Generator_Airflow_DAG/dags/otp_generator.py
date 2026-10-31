from datetime import datetime
import secrets

from airflow.sdk import DAG, Variable
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.smtp.hooks.smtp import SmtpHook


def generate_and_send_otp():
    # Generate a secure six-digit OTP
    otp = f"{secrets.randbelow(1_000_000):06d}"

    # Read email addresses from Airflow Variables
    receiver = Variable.get("OTP_RECEIVER_EMAIL")
    sender = Variable.get("OTP_SENDER_EMAIL")

    subject = "Your OTP"

    html_content = f"""
    <h2>Your OTP is: {otp}</h2>
    <p>Please use this OTP to verify your request.</p>
    <p>This OTP is valid for 5 minutes.</p>
    """

    # Send OTP using the configured Gmail SMTP connection
    hook = SmtpHook(
        smtp_conn_id="gmail_smtp",
        auth_type="basic"
    )

    with hook:
        hook.send_email_smtp(
            to=receiver,
            subject=subject,
            html_content=html_content,
            from_email=sender,
        )

    # Never log the generated OTP
    print("OTP email sent successfully.")


with DAG(
    dag_id="otp_generator",
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
) as dag:

    generate_otp_task = PythonOperator(
        task_id="generate_and_send_otp",
        python_callable=generate_and_send_otp,
    )
