import csv, uuid
from datetime import datetime, date
from decimal import Decimal
from src.config import DATA_DIR
from src.db import connection
from src.logging_config import get_logger

log=get_logger(__name__)
TABLES={
"branches":("branches.csv",["branch_id","branch_name","city"],["branch_id"]),
"customers":("customers.csv",["customer_id","home_branch_id","full_name","customer_segment","created_at"],["customer_id"]),
"accounts":("accounts.csv",["account_id","branch_id","account_type","current_balance","status","opened_at"],["account_id"]),
"account_holders":("account_holders.csv",["customer_id","account_id","holder_role"],["customer_id","account_id"]),
"bank_transactions":("bank_transactions.csv",["transaction_id","account_id","transaction_time","transaction_type","amount","currency","status","channel","merchant_category","source_updated_at"],["transaction_id"]),
"loans":("loans.csv",["loan_id","customer_id","branch_id","principal_amount","interest_rate","loan_status","issued_date","due_date"],["loan_id"]),
"loan_payments":("loan_payments.csv",["payment_id","loan_id","payment_date","amount_paid","payment_status"],["payment_id"])}
INTS={"branch_id","customer_id","home_branch_id","account_id","transaction_id","loan_id","payment_id"}
DECS={"current_balance","amount","principal_amount","interest_rate","amount_paid"}
DATES={"opened_at","issued_date","due_date","payment_date"}
TIMES={"created_at","transaction_time","source_updated_at"}

def read_rows(filename):
    path=DATA_DIR/filename
    if not path.exists(): raise FileNotFoundError(f"{path} missing; run python -m src.generate_data first")
    with path.open(newline="",encoding="utf-8") as f: return list(csv.DictReader(f))

def convert(row):
    result={}
    for k,v in row.items():
        if v=="": result[k]=None
        elif k in INTS: result[k]=int(v)
        elif k in DECS: result[k]=Decimal(v)
        elif k in TIMES: result[k]=datetime.fromisoformat(v)
        elif k in DATES: result[k]=date.fromisoformat(v)
        else: result[k]=v
    return result

def load_table(cursor, table, filename, cols, pks):
    rows=read_rows(filename)
    updates=[c for c in cols if c not in pks]
    sql=f"INSERT INTO `{table}` ({','.join('`'+c+'`' for c in cols)}) VALUES ({','.join(['%s']*len(cols))})"
    if updates:
        # MySQL 8 compatible upsert; VALUES(col) remains supported in MySQL 8 (deprecated in newer releases).
        sql += " ON DUPLICATE KEY UPDATE " + ",".join(f"`{c}`=VALUES(`{c}`)" for c in updates)
    else:
        sql += " ON DUPLICATE KEY UPDATE " + ",".join(f"`{c}`=`{c}`" for c in pks)
    for raw in rows:
        item=convert(raw)
        cursor.execute(sql,[item[c] for c in cols])
    return len(rows)

def build_gold(cursor):
    cursor.execute("""INSERT INTO gold_daily_branch_kpis
    (transaction_date,branch_id,transaction_count,successful_count,failed_count,successful_value,failure_rate_pct)
    SELECT DATE(t.transaction_time),a.branch_id,COUNT(*),
      SUM(t.status='SUCCESS'),SUM(t.status='FAILED'),
      COALESCE(SUM(CASE WHEN t.status='SUCCESS' THEN t.amount ELSE 0 END),0),
      ROUND(100.0*SUM(t.status='FAILED')/NULLIF(COUNT(*),0),2)
    FROM bank_transactions t JOIN accounts a USING(account_id)
    GROUP BY DATE(t.transaction_time),a.branch_id
    ON DUPLICATE KEY UPDATE transaction_count=VALUES(transaction_count),
      successful_count=VALUES(successful_count),failed_count=VALUES(failed_count),
      successful_value=VALUES(successful_value),failure_rate_pct=VALUES(failure_rate_pct)""")
    cursor.execute("""INSERT INTO gold_daily_channel_kpis
    (transaction_date,channel,transaction_count,successful_value)
    SELECT DATE(transaction_time),channel,COUNT(*),
      COALESCE(SUM(CASE WHEN status='SUCCESS' THEN amount ELSE 0 END),0)
    FROM bank_transactions GROUP BY DATE(transaction_time),channel
    ON DUPLICATE KEY UPDATE transaction_count=VALUES(transaction_count),
      successful_value=VALUES(successful_value)""")
    cursor.execute("""INSERT INTO gold_monthly_loan_kpis
    (payment_month,branch_id,payment_count,successful_amount)
    SELECT STR_TO_DATE(DATE_FORMAT(p.payment_date,'%Y-%m-01'),'%Y-%m-%d'),l.branch_id,COUNT(*),
      COALESCE(SUM(CASE WHEN p.payment_status='SUCCESS' THEN p.amount_paid ELSE 0 END),0)
    FROM loan_payments p JOIN loans l USING(loan_id)
    GROUP BY STR_TO_DATE(DATE_FORMAT(p.payment_date,'%Y-%m-01'),'%Y-%m-%d'),l.branch_id
    ON DUPLICATE KEY UPDATE payment_count=VALUES(payment_count),successful_amount=VALUES(successful_amount)""")
    cursor.execute("""INSERT INTO gold_daily_fraud_kpis(alert_date,alert_count,pending_count,high_risk_count)
    SELECT DATE(created_at),COUNT(*),SUM(review_status='PENDING'),SUM(risk_score>=80)
    FROM fraud_alerts GROUP BY DATE(created_at)
    ON DUPLICATE KEY UPDATE alert_count=VALUES(alert_count),pending_count=VALUES(pending_count),
      high_risk_count=VALUES(high_risk_count)""")

def run_pipeline():
    batch=str(uuid.uuid4()); started=datetime.now(); total=0
    log.info("Starting batch_id=%s",batch)
    try:
        with connection() as conn:
            cursor=conn.cursor()
            cursor.execute("INSERT INTO ingestion_batches(batch_id,source_name,started_at,status) VALUES(%s,%s,%s,%s)",(batch,"synthetic_csv",started,"RUNNING"))
            for table,(filename,cols,pks) in TABLES.items():
                count=load_table(cursor,table,filename,cols,pks); total+=count
                log.info("Loaded table=%s rows=%s batch_id=%s",table,count,batch)
            cursor.execute("""INSERT INTO fraud_alerts(transaction_id,alert_reason,risk_score,review_status)
            SELECT transaction_id,'Large transaction over INR 50000',85,'PENDING'
            FROM bank_transactions WHERE amount>=50000
            ON DUPLICATE KEY UPDATE alert_reason=VALUES(alert_reason)""")
            build_gold(cursor)
            cursor.execute("UPDATE ingestion_batches SET completed_at=%s,status='SUCCESS',row_count=%s WHERE batch_id=%s",(datetime.now(),total,batch))
            cursor.close()
    except Exception:
        log.exception("Pipeline failed batch_id=%s",batch)
        # Failure is logged and the transaction rolled back; re-raise for Airflow retries.
        raise
    log.info("Completed batch_id=%s rows=%s",batch,total)
    return {"batch_id":batch,"rows_loaded":total}

def counts():
    with connection() as conn:
        cur=conn.cursor(dictionary=True)
        cur.execute("SELECT (SELECT COUNT(*) FROM customers) customers,(SELECT COUNT(*) FROM accounts) accounts,(SELECT COUNT(*) FROM bank_transactions) transactions,(SELECT COUNT(*) FROM loans) loans,(SELECT COUNT(*) FROM loan_payments) loan_payments,(SELECT COUNT(*) FROM fraud_alerts) fraud_alerts")
        row=cur.fetchone(); cur.close()
    return row
