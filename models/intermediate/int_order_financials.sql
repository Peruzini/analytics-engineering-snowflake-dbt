-- Grain: one row per order with items. Aggregate items and payments separately.
with items as (
    select order_id, count(*) as item_count, sum(quantity) as unit_count,
        sum(quantity * unit_price) as gross_item_amount,
        sum(discount_amount) as discount_amount,
        sum(quantity * unit_price - discount_amount) as net_item_amount
    from {{ ref('stg_order_items') }}
    group by order_id
),
payments as (
    select order_id, count(*) as payment_count, sum(amount) as payment_amount
    from {{ ref('stg_payments') }}
    group by order_id
)
select i.order_id, i.item_count, i.unit_count, i.gross_item_amount,
    i.discount_amount, i.net_item_amount,
    coalesce(p.payment_count, 0) as payment_count,
    coalesce(p.payment_amount, 0) as payment_amount
from items i
left join payments p on i.order_id = p.order_id
