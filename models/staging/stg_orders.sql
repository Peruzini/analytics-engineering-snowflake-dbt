with source as (
    select * from {{ source('raw', 'raw_orders') }}
)
select
    trim(cast(order_id as varchar)) as order_id,
    trim(cast(customer_id as varchar)) as customer_id,
    nullif(trim(cast(campaign_id as varchar)), '') as campaign_id,
    try_to_date(cast(order_date as varchar)) as order_date,
    lower(trim(cast(order_status as varchar))) as order_status
from source
