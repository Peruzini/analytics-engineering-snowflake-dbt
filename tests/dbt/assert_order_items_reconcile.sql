-- Two facts at different grains must reconcile by order.
with expected as (
    select order_id, gross_item_amount, discount_amount, net_item_amount,
        recognized_revenue
    from {{ ref('fct_orders') }}
), actual as (
    select order_id, sum(gross_item_amount) as gross_item_amount,
        sum(discount_amount) as discount_amount,
        sum(net_item_amount) as net_item_amount,
        sum(recognized_item_revenue) as recognized_revenue
    from {{ ref('fct_order_items') }}
    group by order_id
)
select coalesce(e.order_id, a.order_id) as order_id
from expected e
full outer join actual a on e.order_id = a.order_id
where e.order_id is null or a.order_id is null
   or abs(e.gross_item_amount - a.gross_item_amount) > 0.01
   or abs(e.discount_amount - a.discount_amount) > 0.01
   or abs(e.net_item_amount - a.net_item_amount) > 0.01
   or abs(e.recognized_revenue - a.recognized_revenue) > 0.01
