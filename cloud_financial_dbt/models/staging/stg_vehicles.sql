WITH source AS (

    SELECT *
    FROM {{ source('raw', 'vehicles') }}

),

cleaned AS (

    SELECT
        vehicle_id,
        UPPER(TRIM(vin)) AS vin,
        dealer_id,
        TRIM(make) AS make,
        TRIM(model) AS model,
        TRIM(vehicle_type) AS vehicle_type,
        model_year,
        original_price,
        estimated_value
    FROM source

)

SELECT *
FROM cleaned