-- Grain: date with at least one order.
select
    order_date,
    count(*) as order_count,
    sum(completed_order_flag) as completed_orders,
    sum(case when order_status = 'pending' then 1 else 0 end) as pending_orders,
    sum(case when order_status = 'cancelled' then 1 else 0 end) as cancelled_orders,
    sum(case when order_status = 'refunded' then 1 else 0 end) as refunded_orders,
    sum(gross_item_amount) as gross_order_amount,
    sum(discount_amount) as discount_amount,
    sum(net_item_amount) as net_order_amount_all_statuses,
    sum(recognized_revenue) as recognized_revenue,
    sum(refunded_amount) as refunded_amount,
    sum(recognized_revenue) / nullif(sum(completed_order_flag), 0) as avg_completed_ticket
from {{ ref('fct_orders') }}
group by order_date
