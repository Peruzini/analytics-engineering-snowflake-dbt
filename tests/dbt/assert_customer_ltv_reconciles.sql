-- Reconcile at customer grain, including customers with zero orders.
with expected as (
    select c.customer_id,
        count(o.order_id) as total_orders,
        coalesce(sum(o.recognized_revenue), 0) as revenue
    from {{ ref('dim_customers') }} c
    left join {{ ref('fct_orders') }} o on o.customer_id = c.customer_id
    group by c.customer_id
), actual as (
    select customer_id, lifetime_orders as total_orders,
        lifetime_recognized_revenue as revenue
    from {{ ref('mart_customer_ltv') }}
)
select coalesce(e.customer_id, a.customer_id) as customer_id
from expected e
full outer join actual a on e.customer_id = a.customer_id
where e.customer_id is null or a.customer_id is null
   or e.total_orders <> a.total_orders
   or abs(e.revenue - a.revenue) > 0.01
