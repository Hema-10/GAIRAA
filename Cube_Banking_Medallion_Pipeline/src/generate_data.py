import csv, random
from datetime import date, datetime, timedelta
from src.config import DATA_DIR
random.seed(42)

def save(name, rows):
    with (DATA_DIR / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def main():
    branches = [
        {"branch_id":1,"branch_name":"Chennai Central","city":"Chennai"},
        {"branch_id":2,"branch_name":"Coimbatore Main","city":"Coimbatore"},
        {"branch_id":3,"branch_name":"Madurai South","city":"Madurai"}]
    save("branches.csv", branches)
    customers=[]; accounts=[]; holders=[]; txns=[]; loans=[]; payments=[]
    now=datetime.now().replace(microsecond=0)
    for cid in range(1,31):
        bid=random.choice([1,2,3]); aid=10000+cid
        customers.append({"customer_id":cid,"home_branch_id":bid,"full_name":f"Demo Customer {cid:03d}","customer_segment":random.choice(["RETAIL","PREMIUM","SME"]),"created_at":(now-timedelta(days=random.randint(30,900))).isoformat(sep=" ")})
        accounts.append({"account_id":aid,"branch_id":bid,"account_type":random.choice(["SAVINGS","CURRENT","SALARY"]),"current_balance":f"{random.uniform(1000,250000):.2f}","status":"ACTIVE","opened_at":(date.today()-timedelta(days=random.randint(30,1000))).isoformat()})
        holders.append({"customer_id":cid,"account_id":aid,"holder_role":"PRIMARY"})
        if cid<=15:
            lid=50000+cid
            loans.append({"loan_id":lid,"customer_id":cid,"branch_id":bid,"principal_amount":f"{random.uniform(50000,900000):.2f}","interest_rate":f"{random.uniform(7,14.5):.3f}","loan_status":random.choice(["ACTIVE","ACTIVE","CLOSED"]),"issued_date":(date.today()-timedelta(days=random.randint(90,900))).isoformat(),"due_date":(date.today()+timedelta(days=random.randint(-60,365))).isoformat()})
            for p in range(random.randint(1,4)):
                payments.append({"payment_id":lid*10+p,"loan_id":lid,"payment_date":(date.today()-timedelta(days=random.randint(0,180))).isoformat(),"amount_paid":f"{random.uniform(1000,30000):.2f}","payment_status":random.choice(["SUCCESS","SUCCESS","FAILED"])})
    for tid in range(1,301):
        cid=random.randint(1,30); stamp=now-timedelta(days=random.randint(0,89),minutes=random.randint(0,1440))
        txns.append({"transaction_id":tid,"account_id":10000+cid,"transaction_time":stamp.isoformat(sep=" "),"transaction_type":random.choice(["DEBIT","CREDIT","TRANSFER"]),"amount":f"{random.uniform(50,75000):.2f}","currency":"INR","status":random.choice(["SUCCESS","SUCCESS","SUCCESS","FAILED","PENDING"]),"channel":random.choice(["UPI","CARD","ATM","ONLINE"]),"merchant_category":random.choice(["GROCERY","FUEL","BILLS","RETAIL","OTHER"]),"source_updated_at":stamp.isoformat(sep=" ")})
    for name,rows in [("customers.csv",customers),("accounts.csv",accounts),("account_holders.csv",holders),("bank_transactions.csv",txns),("loans.csv",loans),("loan_payments.csv",payments)]:
        save(name,rows)
    print("Synthetic banking CSV files generated in", DATA_DIR)

if __name__=="__main__": main()
