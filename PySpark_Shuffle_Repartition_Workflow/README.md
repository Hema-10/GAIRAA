# PySpark Shuffle and Repartition Workflow

A beginner-friendly local PySpark example that demonstrates **repartitioning**, **shuffle during joins**, **window functions**, and **grouped aggregation**.

## Requirements

- Python 3.9+
- Java (a compatible JDK; Java 17 is a good choice)
- PySpark

Install dependency:

```bash
python -m pip install -r requirements.txt
```

Run:

```bash
python main.py
```

## Workflow

```text
Create DataFrame
      |
      v
repartition(4, "city")
      |   wide transformation; normally causes shuffle
      v
Join customer information
      |   Spark may shuffle join data by customer key
      v
Window function
      |   partition by city and order by amount
      v
GroupBy city + sum(amount)
      |   aggregation may require shuffle
      v
Show results + explain("formatted")
```

## Key concepts

- **Partition:** A chunk of data processed by a Spark task.
- **Shuffle:** Data is redistributed between executors/partitions, often across the network. It is more expensive than a narrow transformation.
- **repartition():** Changes the number/distribution of partitions. It causes a shuffle.
- **coalesce():** Usually reduces partitions with less data movement; it does not normally cause a full shuffle unless shuffle is explicitly enabled.
- **Exchange:** In Spark's physical plan, `Exchange` is a common indicator of data redistribution/shuffle.
- **Window function:** Computes values across rows in a defined window. `Window.partitionBy(...).orderBy(...)` may require shuffle and sorting.

Spark can optimize the physical plan. The exact number and placement of shuffle stages can vary by Spark version, input size, adaptive query execution, and join strategy. Use `explain("formatted")` and the Spark UI to inspect what actually happened.

## Project structure

```text
pyspark_shuffle_repartition_workflow/
├── main.py
├── README.md
└── requirements.txt
```
