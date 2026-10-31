CREATE DATABASE IF NOT EXISTS banking_analytics;
USE banking_analytics;

CREATE TABLE IF NOT EXISTS ingestion_batches (
    batch_id VARCHAR(40) PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    started_at DATETIME NOT NULL,
    completed_at DATETIME NULL,
    status VARCHAR(20) NOT NULL,
    row_count INT NOT NULL DEFAULT 0,
    error_message TEXT NULL
);

CREATE TABLE IF NOT EXISTS branches (
    branch_id INT PRIMARY KEY,
    branch_name VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL
);
CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT PRIMARY KEY,
    home_branch_id INT,
    full_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL,
    CONSTRAINT fk_customers_branch FOREIGN KEY (home_branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE IF NOT EXISTS accounts (
    account_id BIGINT PRIMARY KEY,
    branch_id INT NOT NULL,
    account_type VARCHAR(30) NOT NULL,
    current_balance DECIMAL(18,2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    opened_at DATE NOT NULL,
    CONSTRAINT chk_account_balance CHECK (current_balance >= 0),
    CONSTRAINT fk_accounts_branch FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE IF NOT EXISTS account_holders (
    customer_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,
    holder_role VARCHAR(30) NOT NULL DEFAULT 'PRIMARY',
    PRIMARY KEY (customer_id, account_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE IF NOT EXISTS bank_transactions (
    transaction_id BIGINT PRIMARY KEY,
    account_id BIGINT NOT NULL,
    transaction_time DATETIME NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    amount DECIMAL(18,2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'INR',
    status ENUM('SUCCESS','FAILED','PENDING') NOT NULL,
    channel VARCHAR(20) NOT NULL,
    merchant_category VARCHAR(50),
    source_updated_at DATETIME NOT NULL,
    CONSTRAINT chk_transaction_amount CHECK (amount > 0),
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    INDEX idx_tx_account_time (account_id, transaction_time),
    INDEX idx_tx_time_status (transaction_time, status)
);
CREATE TABLE IF NOT EXISTS loans (
    loan_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    branch_id INT NOT NULL,
    principal_amount DECIMAL(18,2) NOT NULL,
    interest_rate DECIMAL(6,3) NOT NULL,
    loan_status VARCHAR(30) NOT NULL,
    issued_date DATE NOT NULL,
    due_date DATE NULL,
    CONSTRAINT chk_loan_principal CHECK (principal_amount > 0),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id),
    INDEX idx_loans_customer (customer_id)
);
CREATE TABLE IF NOT EXISTS loan_payments (
    payment_id BIGINT PRIMARY KEY,
    loan_id BIGINT NOT NULL,
    payment_date DATE NOT NULL,
    amount_paid DECIMAL(18,2) NOT NULL,
    payment_status VARCHAR(20) NOT NULL,
    CONSTRAINT chk_payment_amount CHECK (amount_paid >= 0),
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id),
    INDEX idx_payment_loan_date (loan_id, payment_date)
);
CREATE TABLE IF NOT EXISTS fraud_alerts (
    alert_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    transaction_id BIGINT NOT NULL,
    alert_reason VARCHAR(200) NOT NULL,
    risk_score DECIMAL(5,2) NOT NULL,
    review_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_alert_transaction_reason (transaction_id, alert_reason),
    FOREIGN KEY (transaction_id) REFERENCES bank_transactions(transaction_id)
);

CREATE TABLE IF NOT EXISTS gold_daily_branch_kpis (
    transaction_date DATE NOT NULL,
    branch_id INT NOT NULL,
    transaction_count BIGINT NOT NULL,
    successful_count BIGINT NOT NULL,
    failed_count BIGINT NOT NULL,
    successful_value DECIMAL(20,2) NOT NULL,
    failure_rate_pct DECIMAL(7,2),
    PRIMARY KEY (transaction_date, branch_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE IF NOT EXISTS gold_daily_channel_kpis (
    transaction_date DATE NOT NULL,
    channel VARCHAR(20) NOT NULL,
    transaction_count BIGINT NOT NULL,
    successful_value DECIMAL(20,2) NOT NULL,
    PRIMARY KEY (transaction_date, channel)
);
CREATE TABLE IF NOT EXISTS gold_monthly_loan_kpis (
    payment_month DATE NOT NULL,
    branch_id INT NOT NULL,
    payment_count BIGINT NOT NULL,
    successful_amount DECIMAL(20,2) NOT NULL,
    PRIMARY KEY (payment_month, branch_id),
    FOREIGN KEY (branch_id) REFERENCES branches(branch_id)
);
CREATE TABLE IF NOT EXISTS gold_daily_fraud_kpis (
    alert_date DATE PRIMARY KEY,
    alert_count BIGINT NOT NULL,
    pending_count BIGINT NOT NULL,
    high_risk_count BIGINT NOT NULL
);
