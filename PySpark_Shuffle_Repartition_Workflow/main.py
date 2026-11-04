"""
PySpark Shuffle + Repartition Workflow
--------------------------------------
Demonstrates:
1. Creating a DataFrame
2. repartition() - increases/rebalances partitions and causes a shuffle
3. A join - commonly causes a shuffle when Spark must align join keys
4. A window function - uses partition/order information and may cause a shuffle
5. explain("formatted") - inspect the physical execution plan
"""

from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, sum as spark_sum, row_number, desc


def main():
    spark = (
        SparkSession.builder
        .appName("ShuffleRepartitionWorkflow")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    # Sample transaction data
    transactions = [
        (1, "Asha", "Chennai", 500),
        (2, "Bala", "Erode", 800),
        (3, "Asha", "Chennai", 250),
        (4, "Dinesh", "Erode", 1200),
        (5, "Bala", "Coimbatore", 400),
        (6, "Asha", "Coimbatore", 700),
        (7, "Dinesh", "Chennai", 300),
        (8, "Bala", "Erode", 600),
    ]
    tx_schema = ["transaction_id", "customer", "city", "amount"]
    tx = spark.createDataFrame(transactions, tx_schema)

    customer_info = [
        ("Asha", "Premium"),
        ("Bala", "Regular"),
        ("Dinesh", "Premium"),
    ]
    customer_schema = ["customer", "customer_type"]
    customers = spark.createDataFrame(customer_info, customer_schema)

    print("\\n--- Initial DataFrame ---")
    tx.show()
    print("Initial partitions:", tx.rdd.getNumPartitions())

    # REPARTITION: redistributes rows by key across partitions.
    # This is a wide transformation and normally introduces a shuffle.
    print("\\n--- Repartition by city ---")
    repartitioned = tx.repartition(4, "city")
    print("Partitions after repartition:", repartitioned.rdd.getNumPartitions())
    repartitioned.show()

    # JOIN: Spark may shuffle one or both sides to place matching keys together.
    print("\\n--- Join transactions with customer information ---")
    joined = repartitioned.join(customers, on="customer", how="inner")
    joined.show()

    # WINDOW: compute a row number per city, ordered by transaction amount.
    # Window partitioning/order may trigger exchange (shuffle) in the plan.
    print("\\n--- Window function: rank transactions within each city ---")
    window_spec = Window.partitionBy("city").orderBy(desc("amount"))
    ranked = joined.withColumn("rank_in_city", row_number().over(window_spec))
    ranked.show()

    # Aggregation also commonly requires data to be shuffled by grouping key.
    print("\\n--- Aggregate total transaction amount by city ---")
    totals = ranked.groupBy("city").agg(
        spark_sum("amount").alias("total_amount")
    )
    totals.show()

    print("\\n--- Physical plan: look for Exchange / shuffle operations ---")
    ranked.explain("formatted")

    spark.stop()


if __name__ == "__main__":
    main()
