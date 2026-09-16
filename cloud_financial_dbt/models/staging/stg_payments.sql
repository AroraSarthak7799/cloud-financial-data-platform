WITH source AS (

    SELECT *
    FROM {{ source('raw', 'payments') }}

),

cleaned AS (

    SELECT
        payment_id,
        loan_id,
        payment_number,
        scheduled_payment_date,
        actual_payment_date,
        scheduled_amount,
        payment_amount,
        TRIM(payment_status) AS payment_status,
        days_late
    FROM source

)

SELECT *
FROM cleaned