with source as (
    select * from {{ source('raw', 'raw_order_items') }}
)
select
    trim(cast(order_item_id as varchar)) as order_item_id,
    trim(cast(order_id as varchar)) as order_id,
    trim(cast(product_id as varchar)) as product_id,
    try_cast(cast(quantity as varchar) as decimal(18, 0)) as quantity,
    try_cast(cast(unit_price as varchar) as decimal(18, 2)) as unit_price,
    try_cast(cast(discount_amount as varchar) as decimal(18, 2)) as discount_amount
from source
