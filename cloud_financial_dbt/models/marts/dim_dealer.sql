SELECT
    dealer_id,
    dealer_name,
    dealer_type,
    city,
    province,
    postal_code,
    phone_number,
    onboarding_date,
    active_flag
FROM {{ ref('stg_dealers') }}