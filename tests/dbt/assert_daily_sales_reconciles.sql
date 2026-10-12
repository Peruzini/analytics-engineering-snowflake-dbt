-- Reconcile every order day, including missing or extra dates.
with expected as (
    select order_date, count(*) as order_count,
        sum(completed_order_flag) as completed_orders,
        sum(recognized_revenue) as revenue
    from {{ ref('fct_orders') }}
    group by order_date
), actual as (
    select order_date, order_count, completed_orders,
        recognized_revenue as revenue
    from {{ ref('mart_daily_sales') }}
)
select coalesce(e.order_date, a.order_date) as order_date,
    e.order_count as expected_orders, a.order_count as actual_orders,
    e.revenue as expected_revenue, a.revenue as actual_revenue
from expected e
full outer join actual a on e.order_date = a.order_date
where e.order_date is null or a.order_date is null
   or e.order_count <> a.order_count
   or e.completed_orders <> a.completed_orders
   or abs(e.revenue - a.revenue) > 0.01
