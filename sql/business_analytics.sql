-- ==================================================
-- BUSINESS QUESTION 1:
-- What is the distribution of payment statuses?
-- ==================================================

SELECT
    payment_status,
    COUNT(*) AS total_payments,
    ROUND(SUM(payment_amount), 2) AS recorded_payment_amount,
    ROUND(AVG(days_late), 2) AS average_days_late
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_PAYMENT
GROUP BY payment_status
ORDER BY total_payments DESC;


-- ==================================================
-- BUSINESS QUESTION 2:
-- What percentage of payment records are late?
-- Late is defined as days_late > 0.
-- ==================================================

SELECT
    COUNT(*) AS total_payments,
    COUNT_IF(days_late > 0) AS late_payments,
    ROUND(
        100.0 * COUNT_IF(days_late > 0)
        / NULLIF(COUNT(*), 0),
        2
    ) AS late_payment_percentage
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_PAYMENT;


-- Business Question 3 — Loan portfolio by province
-- Which Canadian provinces have the highest number and dollar value of originated loans?

SELECT
    c.province,
    COUNT(*) AS total_loans,
    ROUND(SUM(l.loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(l.loan_amount), 2) AS average_loan_amount
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_LOAN l
JOIN CLOUD_FINANCIAL_DB.MARTS.DIM_CUSTOMER c
    ON l.customer_id = c.customer_id
GROUP BY c.province
ORDER BY total_loan_amount DESC;


-- Business Question 4 — Dealer loan origination performance
-- Which dealers originated the largest loan portfolios?

SELECT
    d.dealer_id,
    d.dealer_name,
    COUNT(l.loan_id) AS total_loans,
    ROUND(SUM(l.loan_amount), 2) AS total_loan_amount,
    ROUND(AVG(l.loan_amount), 2) AS average_loan_amount
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_LOAN l
JOIN CLOUD_FINANCIAL_DB.MARTS.DIM_DEALER d
    ON l.dealer_id = d.dealer_id
GROUP BY
    d.dealer_id,
    d.dealer_name
ORDER BY total_loan_amount DESC
LIMIT 10;


-- ==================================================
-- BUSINESS QUESTION 5:
-- Reconcile loan counts and amounts after joins
-- ==================================================

SELECT
    'FACT_LOAN' AS source,
    COUNT(*) AS total_loans,
    ROUND(SUM(loan_amount), 2) AS total_amount
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_LOAN

UNION ALL

SELECT
    'JOIN_CUSTOMERS',
    COUNT(*),
    ROUND(SUM(l.loan_amount), 2)
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_LOAN l
JOIN CLOUD_FINANCIAL_DB.MARTS.DIM_CUSTOMER c
    ON l.customer_id = c.customer_id

UNION ALL

SELECT
    'JOIN_DEALERS',
    COUNT(*),
    ROUND(SUM(l.loan_amount), 2)
FROM CLOUD_FINANCIAL_DB.MARTS.FACT_LOAN l
JOIN CLOUD_FINANCIAL_DB.MARTS.DIM_DEALER d
    ON l.dealer_id = d.dealer_id;