-- Grain: one product; list price is not booked transaction price.
select product_id, product_name, category, list_price
from {{ ref('stg_products') }}
