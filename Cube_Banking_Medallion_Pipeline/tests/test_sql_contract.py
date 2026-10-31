from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def test_medallion_layers_exist():
    sql=(ROOT/"sql"/"schema.sql").read_text(encoding="utf-8").lower()
    assert "create database if not exists banking_analytics" in sql
    assert "create table if not exists bank_transactions" in sql
    assert "create table if not exists gold_daily_branch_kpis" in sql

def test_mysql_upsert_present():
    code=(ROOT/"src"/"pipeline.py").read_text(encoding="utf-8").lower()
    assert "on duplicate key update" in code
