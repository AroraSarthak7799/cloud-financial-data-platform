WITH source AS (

    SELECT *
    FROM {{ source('raw', 'dealers') }}

),

cleaned AS (

    SELECT
        dealer_id,
        TRIM(dealer_name) AS dealer_name,
        TRIM(dealer_type) AS dealer_type,
        TRIM(city) AS city,
        TRIM(province) AS province,
        UPPER(TRIM(postal_code)) AS postal_code,
        phone_number,
        onboarding_date,
        UPPER(TRIM(active_flag)) AS active_flag
    FROM source

)

SELECT *
FROM cleaned