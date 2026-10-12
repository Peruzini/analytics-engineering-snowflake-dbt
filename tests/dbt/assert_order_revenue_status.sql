-- Returns orders violating the portfolio revenue convention.
select
    order_id, order_status, net_item_amount, payment_amount,
    recognized_revenue, refunded_amount
from {{ ref('fct_orders') }}
where net_item_amount is null
   or recognized_revenue is null
   or refunded_amount is null
   or abs(recognized_revenue -
        case when order_status = 'completed' then net_item_amount else 0 end) > 0.01
   or abs(refunded_amount -
        case when order_status = 'refunded' then net_item_amount else 0 end) > 0.01
   or abs(coalesce(payment_amount, 0) -
        case when order_status in ('completed', 'refunded') then net_item_amount else 0 end) > 0.01
