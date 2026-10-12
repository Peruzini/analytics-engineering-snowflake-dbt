-- Grain: one customer.
select customer_id, email, region, created_at
from {{ ref('stg_customers') }}
