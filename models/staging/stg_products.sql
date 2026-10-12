with source as (
    select * from {{ source('raw', 'raw_products') }}
)
select
    trim(cast(product_id as varchar)) as product_id,
    trim(cast(product_name as varchar)) as product_name,
    trim(cast(category as varchar)) as category,
    try_cast(cast(list_price as varchar) as decimal(18, 2)) as list_price
from source
