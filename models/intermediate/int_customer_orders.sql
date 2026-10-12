-- Grain: every order; completed only is recognized revenue (case-study rule).
with orders as (select * from {{ ref('stg_orders') }}),
financials as (select * from {{ ref('int_order_financials') }}),
campaigns as (select * from {{ ref('stg_campaigns') }})
select o.order_id, o.customer_id, o.campaign_id,
    coalesce(c.channel, 'unattributed') as channel, o.order_date, o.order_status,
    f.item_count, f.unit_count, f.gross_item_amount, f.discount_amount,
    f.net_item_amount, f.payment_count, f.payment_amount,
    case when o.order_status = 'completed' then f.net_item_amount else 0 end as recognized_revenue,
    case when o.order_status = 'refunded' then f.net_item_amount else 0 end as refunded_amount,
    case when o.order_status = 'completed' then 1 else 0 end as completed_order_flag
from orders o
left join financials f on o.order_id = f.order_id
left join campaigns c on o.campaign_id = c.campaign_id
