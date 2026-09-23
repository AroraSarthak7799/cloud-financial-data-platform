SELECT
    payment_id,
    loan_id,
    payment_number,
    scheduled_payment_date,
    actual_payment_date,
    scheduled_amount,
    payment_amount,
    payment_status,
    days_late
FROM {{ ref('stg_payments') }}