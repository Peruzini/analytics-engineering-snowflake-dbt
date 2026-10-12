-- Grain: customer including customers with zero orders.
-- Lifetime here means observed historical revenue, not predicted future value.
with customers as (select * from {{ ref('dim_customers') }}),
orders as (select * from {{ ref('fct_orders') }})
select c.customer_id, c.region, c.created_at,
    count(o.order_id) as lifetime_orders,
    coalesce(sum(o.completed_order_flag), 0) as completed_orders,
    min(o.order_date) as first_order_date,
    max(o.order_date) as last_order_date,
    coalesce(sum(o.recognized_revenue), 0) as lifetime_recognized_revenue,
    coalesce(sum(o.refunded_amount), 0) as lifetime_refunded_amount,
    sum(o.recognized_revenue) / nullif(sum(o.completed_order_flag), 0) as avg_completed_ticket
from customers c
left join orders o on c.customer_id = o.customer_id
group by c.customer_id, c.region, c.created_at
