WITH source AS (

    SELECT *
    FROM {{ source('raw', 'customers') }}

),

cleaned AS (

    SELECT
        customer_id,
        TRIM(customer_name) AS customer_name,
        LOWER(TRIM(email)) AS email,
        phone_number,
        TRIM(city) AS city,
        TRIM(province) AS province,
        UPPER(TRIM(postal_code)) AS postal_code,
        created_date
    FROM source

)

SELECT *
FROM cleaned