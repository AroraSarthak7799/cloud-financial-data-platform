SELECT
    customer_id,
    customer_name,
    email,
    phone_number,
    city,
    province,
    postal_code,
    created_date
FROM {{ ref('stg_customers') }}