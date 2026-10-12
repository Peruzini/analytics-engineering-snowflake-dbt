with source as (
    select * from {{ source('raw', 'raw_payments') }}
)
select
    trim(cast(payment_id as varchar)) as payment_id,
    trim(cast(order_id as varchar)) as order_id,
    try_to_date(cast(payment_date as varchar)) as payment_date,
    try_to_decimal(cast(amount as varchar), 18, 2) as amount,
    lower(trim(cast(payment_status as varchar))) as payment_status,
    lower(trim(cast(payment_method as varchar))) as payment_method
from source
