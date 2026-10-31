# DummyJSON API to PySpark DAG Project (Windows)

This project fetches live product records from DummyJSON and processes them with local Apache Spark. Spark automatically builds the execution DAG from the DataFrame transformations and actions in `main.py`.

## API used

- All products: https://dummyjson.com/products?limit=0
- API documentation: https://dummyjson.com/docs/products

The program fetches the API response at runtime. It does not use manually typed sample product records. The API request is made with Python `requests`; the returned product records are then loaded into a Spark DataFrame.

## Requirements

- Windows 10/11
- Python 3.9–3.11 recommended
- JDK 17 (the project uses PySpark 3.5.9)
- Internet connection for the API request and package installation

## 1. Check Java and Python

Open a new PowerShell terminal:

```powershell
java -version
python --version
$env:JAVA_HOME
```

Confirm Java 17 is active and `JAVA_HOME` points to your JDK 17 folder. Reopen the terminal after changing Windows environment variables.

## 2. Extract and open the project

Extract the ZIP and open the `Spark_DAG_Project` folder in VS Code. Open the integrated PowerShell terminal in that folder.

## 3. Create and activate the virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt instead:

```cmd
venv\Scripts\activate.bat
```

## 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Run

```powershell
python main.py
```

The program will:

1. Fetch product records from DummyJSON.
2. Create a Spark DataFrame from the API response.
3. Filter out products with zero stock.
4. Select and transform columns; calculate inventory value (`price * stock`) and discounted price.
5. Group by category and brand to calculate inventory summaries.
6. Print the Spark execution plan using `explain(extended=True)`.
7. Write CSV output folders under `output/`.

## 6. View the DAG execution in Spark UI

While the program is waiting at `Press Enter to stop Spark`, open the Spark UI URL printed in the terminal (usually http://localhost:4040).

Inspect:

- **Jobs**: actions such as `show`, `count`, and `write` trigger jobs.
- **Stages**: shuffle operations such as `groupBy` can create stage boundaries.
- **SQL/DataFrame**: inspect query plans and execution details.

Do not press Enter until you finish inspecting the UI. Then return to the terminal and press Enter to stop Spark.

## Output folders

- `output/cleaned_products/`
- `output/category_inventory/`
- `output/brand_inventory/`

Each output is a Spark CSV directory and contains one or more `part-*.csv` files plus metadata. It is not a single CSV file.

## Understanding the DAG

- `filter`, `select`, and `withColumn` are transformations. They are lazily evaluated.
- `groupBy` and aggregations are wide transformations that generally require a shuffle.
- `show`, `count`, and `write` are actions that trigger execution.
- Spark constructs the DAG automatically; this project does not manually define a DAG.
- The DAG Scheduler divides jobs into stages, and stages into tasks.

**Note:** This project uses `inventory_value = price * stock`, not actual sales revenue. DummyJSON's products endpoint provides product/catalog data, not order transaction history.

## Windows Python worker fix

The project sets `PYSPARK_PYTHON` and `PYSPARK_DRIVER_PYTHON` to the active Python interpreter at the top of `main.py`. This addresses the Windows error where Spark tries to launch a missing `python3` executable.

## Troubleshooting

### `JAVA_HOME is not set` or wrong Java version

Set `JAVA_HOME` to the JDK 17 installation directory, add `%JAVA_HOME%\bin` to Windows Path, and open a fresh terminal.

### API request fails

Check your internet connection and try opening the API endpoint in a browser. The API must be reachable when the program runs.

### `ModuleNotFoundError: No module named 'requests'`

Activate the project's virtual environment and run `pip install -r requirements.txt`.

### Spark UI does not open

Keep `main.py` running and use the exact Spark UI URL printed in the terminal. If port 4040 is occupied, Spark may select another port.
