SELECT
    vehicle_id,
    vin,
    dealer_id,
    make,
    model,
    vehicle_type,
    model_year,
    original_price,
    estimated_value
FROM {{ ref('stg_vehicles') }}