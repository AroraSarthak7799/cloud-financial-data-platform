WITH source AS (

    SELECT *
    FROM {{ source('raw', 'loans') }}

),

cleaned AS (

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
        TRIM(loan_status) AS loan_status
    FROM source

)

SELECT *
FROM cleaned