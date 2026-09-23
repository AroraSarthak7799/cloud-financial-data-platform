SELECT
    loan_id,
    customer_id,
    vehicle_id,
    dealer_id,
    loan_start_date,
    maturity_date,
    original_price,
    down_payment,
    loan_amount,
    annual_interest_rate,
    term_months,
    monthly_payment,
    loan_status
FROM {{ ref('stg_loans') }}