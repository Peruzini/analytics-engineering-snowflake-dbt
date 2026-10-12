-- Grain: one order, preserving every order status.
select order_id, customer_id, campaign_id, order_date, order_status,
    item_count, unit_count, gross_item_amount, discount_amount, net_item_amount,
    payment_count, payment_amount, recognized_revenue, refunded_amount,
    completed_order_flag
from {{ ref('int_customer_orders') }}
