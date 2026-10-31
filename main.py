"""Fetch live product data from DummyJSON and demonstrate a PySpark execution DAG."""

# On Windows, make Spark workers use the same Python interpreter as this project.
import os
import sys
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, round as spark_round, sum as spark_sum, avg
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType, DoubleType
)

API_URL = "https://dummyjson.com/products?limit=0"

PRODUCT_SCHEMA = StructType([
    StructField("id", IntegerType(), False),
    StructField("title", StringType(), True),
    StructField("category", StringType(), True),
    StructField("brand", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("stock", IntegerType(), True),
    StructField("rating", DoubleType(), True),
    StructField("discountPercentage", DoubleType(), True),
])


def fetch_products():
    """Fetch product records from DummyJSON and keep the fields used in analysis."""
    print("\nFetching product data from DummyJSON...")
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    payload = response.json()
    products = payload.get("products", [])
    if not products:
        raise RuntimeError("The API returned no product records.")

    rows = []
    for product in products:
        rows.append({
            "id": int(product["id"]),
            "title": str(product.get("title") or "Unknown"),
            "category": str(product.get("category") or "Unknown"),
            "brand": str(product.get("brand") or "Unknown"),
            "price": float(product.get("price") or 0),
            "stock": int(product.get("stock") or 0),
            "rating": float(product.get("rating") or 0),
            "discountPercentage": float(product.get("discountPercentage") or 0),
        })

    print(f"Fetched {len(rows)} products from the API.")
    return rows


def main():
    products = fetch_products()

    spark = (
        SparkSession.builder
        .appName("DummyJSON_Product_DAG")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")

    try:
        print("\nSPARK STARTED")
        print("Spark version:", spark.version)
        print("Spark UI:", spark.sparkContext.uiWebUrl)

        # API records become the source DataFrame for the Spark DAG.
        source_df = spark.createDataFrame(products, schema=PRODUCT_SCHEMA)
        print("\n1. API SOURCE DATA")
        source_df.show(10, truncate=False)
        print("Total API records:", source_df.count())

        # Narrow transformations: filter, select, and derived columns.
        available_df = source_df.filter(col("stock") > 0)
        selected_df = available_df.select(
            "id", "title", "category", "brand", "price", "stock",
            "rating", "discountPercentage"
        )
        enriched_df = (
            selected_df
            .withColumn("inventory_value", spark_round(col("price") * col("stock"), 2))
            .withColumn("discounted_price", spark_round(
                col("price") * (1 - col("discountPercentage") / 100), 2
            ))
        )

        # Wide transformations: groupBy causes shuffle and helps demonstrate stages.
        category_summary = enriched_df.groupBy("category").agg(
            spark_sum("stock").alias("total_stock"),
            spark_round(spark_sum("inventory_value"), 2).alias("total_inventory_value"),
            spark_round(avg("rating"), 2).alias("average_rating"),
            spark_sum("id").alias("_sort_helper"),
        ).drop("_sort_helper")

        brand_summary = enriched_df.groupBy("brand").agg(
            spark_sum("stock").alias("total_stock"),
            spark_round(spark_sum("inventory_value"), 2).alias("total_inventory_value"),
        )

        print("\n2. CLEANED AND ENRICHED PRODUCTS")
        enriched_df.orderBy("id").show(15, truncate=False)

        print("\n3. CATEGORY-WISE INVENTORY ANALYSIS")
        category_summary.orderBy(col("total_inventory_value").desc()).show(20, truncate=False)

        print("\n4. BRAND-WISE INVENTORY ANALYSIS")
        brand_summary.orderBy(col("total_inventory_value").desc()).show(20, truncate=False)

        # explain() displays Spark's logical and physical execution plans.
        print("\n5. EXECUTION PLAN / DAG FOR CATEGORY SUMMARY")
        category_summary.explain(extended=True)

        # Spark writes each result as a folder containing part-*.csv files.
        (enriched_df.write.mode("overwrite").option("header", True)
         .csv("output/cleaned_products"))
        (category_summary.write.mode("overwrite").option("header", True)
         .csv("output/category_inventory"))
        (brand_summary.write.mode("overwrite").option("header", True)
         .csv("output/brand_inventory"))

        print("\n6. OUTPUT SAVED")
        print("output/cleaned_products/")
        print("output/category_inventory/")
        print("output/brand_inventory/")
        print("\nPROJECT COMPLETED")
        print("Keep this program running while you inspect Spark UI Jobs and Stages.")
        print("Spark UI:", spark.sparkContext.uiWebUrl)
        input("\nPress Enter to stop Spark and exit...")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()
