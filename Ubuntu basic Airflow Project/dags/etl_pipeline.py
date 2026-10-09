from datetime import datetime
import pandas as pd

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


def load_data():
    import os

    input_folder = "/home/hema/airflow/data/input"

    csv_files = [
        file for file in os.listdir(input_folder)
        if file.endswith(".csv")
    ]

    if not csv_files:
        raise FileNotFoundError("No CSV file found in input folder")

    input_file = os.path.join(input_folder, csv_files[0])

    df = pd.read_csv(input_file)

    print(f"Loaded file: {csv_files[0]}")
    print("Data loaded successfully!")
    print(df)


def transform_data():
    input_file = "/home/hema/airflow/data/employees.csv"
    output_file = "/home/hema/airflow/data/transformed_employees.csv"

    df = pd.read_csv(input_file)

    # Convert employee names to uppercase
    df["name"] = df["name"].str.upper()

    # Save transformed data
    df.to_csv(output_file, index=False)

    print("Data transformed and saved successfully!")
    print(df)


def data_quality_check():
    file_path = "/home/hema/airflow/data/transformed_employees.csv"

    df = pd.read_csv(file_path)

    # Check for missing values
    assert df.isnull().sum().sum() == 0, "Data contains missing values"

    # Check age
    assert (df["age"] > 0).all(), "Invalid age found"

    # Check salary
    assert (df["salary"] > 0).all(), "Invalid salary found"

    print("Data quality check passed successfully!")

with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
) as dag:

    load = PythonOperator(
        task_id="load_data",
        python_callable=load_data,
    )

    transform = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data,
    )
    
    quality = PythonOperator(
        task_id="data_quality",
        python_callable=data_quality_check,
    )

    load >> transform >> quality