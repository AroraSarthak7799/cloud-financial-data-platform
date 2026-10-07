{% snapshot customer_history %}

{{
    config(
        target_schema='HISTORY',
        unique_key='customer_id',
        strategy='check',
        check_cols=[
            'customer_name',
            'email',
            'phone_number',
            'city',
            'province',
            'postal_code'
        ]
    )
}}

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

{% endsnapshot %}