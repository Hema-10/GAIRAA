from src.db import connection

QUERIES = {
"1 Daily transaction trends": "SELECT DATE(transaction_time) day,COUNT(*) attempts,SUM(CASE WHEN status='SUCCESS' THEN amount ELSE 0 END) successful_value FROM bank_transactions GROUP BY DATE(transaction_time) ORDER BY day DESC",
"2 Branch transaction performance": "SELECT b.branch_name,SUM(g.transaction_count) transactions,SUM(g.successful_value) successful_value FROM gold_daily_branch_kpis g JOIN branches b USING(branch_id) GROUP BY b.branch_name ORDER BY successful_value DESC",
"3 Failed transaction rate": "SELECT DATE(transaction_time) day,ROUND(100*SUM(status='FAILED')/NULLIF(COUNT(*),0),2) failure_rate_pct FROM bank_transactions GROUP BY DATE(transaction_time) ORDER BY day DESC",
"4 Channel usage": "SELECT channel,COUNT(*) attempts,SUM(CASE WHEN status='SUCCESS' THEN amount ELSE 0 END) successful_value FROM bank_transactions GROUP BY channel ORDER BY attempts DESC",
"5 Average transaction by customer segment": "SELECT c.customer_segment,ROUND(AVG(t.amount),2) avg_amount FROM bank_transactions t JOIN accounts a USING(account_id) JOIN account_holders h USING(account_id) JOIN customers c USING(customer_id) WHERE t.status='SUCCESS' GROUP BY c.customer_segment ORDER BY avg_amount DESC",
"6 Customers with no successful transaction in 30 days": "SELECT c.customer_id,c.full_name FROM customers c WHERE NOT EXISTS(SELECT 1 FROM account_holders h JOIN bank_transactions t USING(account_id) WHERE h.customer_id=c.customer_id AND t.status='SUCCESS' AND t.transaction_time>=NOW()-INTERVAL 30 DAY)",
"7 Customer acquisition by month": "SELECT DATE_FORMAT(created_at,'%Y-%m') AS month, COUNT(*) AS new_customers FROM customers GROUP BY DATE_FORMAT(created_at,'%Y-%m') ORDER BY month",
"8 Balance by account type": "SELECT account_type,COUNT(*) accounts,SUM(current_balance) total_balance,ROUND(AVG(current_balance),2) average_balance FROM accounts GROUP BY account_type ORDER BY total_balance DESC",
"9 Branch account balances": "SELECT b.branch_name,SUM(a.current_balance) total_balance FROM accounts a JOIN branches b USING(branch_id) GROUP BY b.branch_name ORDER BY total_balance DESC",
"10 Loans by status": "SELECT loan_status,COUNT(*) loan_count,SUM(principal_amount) principal_total FROM loans GROUP BY loan_status",
"11 Successful repayments by month": "SELECT DATE_FORMAT(payment_date,'%Y-%m') month,SUM(amount_paid) paid_amount FROM loan_payments WHERE payment_status='SUCCESS' GROUP BY DATE_FORMAT(payment_date,'%Y-%m') ORDER BY month",
"12 Loan payments by branch": "SELECT b.branch_name,COUNT(*) payments,SUM(CASE WHEN p.payment_status='SUCCESS' THEN p.amount_paid ELSE 0 END) paid_amount FROM loan_payments p JOIN loans l USING(loan_id) JOIN branches b USING(branch_id) GROUP BY b.branch_name ORDER BY paid_amount DESC",
"13 Pending fraud alerts": "SELECT alert_reason,COUNT(*) pending_alerts FROM fraud_alerts WHERE review_status='PENDING' GROUP BY alert_reason ORDER BY pending_alerts DESC",
"14 Alert review outcomes": "SELECT review_status,COUNT(*) alerts FROM fraud_alerts GROUP BY review_status",
"15 Pipeline run history": "SELECT batch_id,started_at,completed_at,status,row_count FROM ingestion_batches ORDER BY started_at DESC LIMIT 20",
}

def main():
    with connection() as conn:
        cur=conn.cursor(dictionary=True,buffered=True)
        for title,sql in QUERIES.items():
            print("\n"+"="*68+"\n"+title+"\n"+"="*68)
            cur.execute(sql)
            rows=cur.fetchall()[:20]
            if not rows: print("(no rows)")
            else:
                print(" | ".join(rows[0].keys()))
                for row in rows: print(" | ".join(str(v) for v in row.values()))
        cur.close()
if __name__=="__main__": main()
