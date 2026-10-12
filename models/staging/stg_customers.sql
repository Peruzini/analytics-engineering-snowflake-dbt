with source as (
    select * from {{ source('raw', 'raw_customers') }}
)
select
    trim(cast(customer_id as varchar)) as customer_id,
    lower(trim(cast(email as varchar))) as email,
    trim(cast(region as varchar)) as region,
    try_to_date(cast(created_at as varchar)) as created_at
from source
