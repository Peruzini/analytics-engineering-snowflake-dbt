-- Grain: one item; joining order context does not multiply item rows.
with items as (select * from {{ ref('stg_order_items') }}),
orders as (select * from {{ ref('fct_orders') }})
select i.order_item_id, i.order_id, i.product_id, o.customer_id, o.campaign_id,
    o.order_date, o.order_status, i.quantity, i.unit_price, i.discount_amount,
    i.quantity * i.unit_price as gross_item_amount,
    i.quantity * i.unit_price - i.discount_amount as net_item_amount,
    case when o.order_status = 'completed'
        then i.quantity * i.unit_price - i.discount_amount else 0
    end as recognized_item_revenue
from items i
left join orders o on i.order_id = o.order_id
