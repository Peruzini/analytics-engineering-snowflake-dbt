-- Grain: channel including unattributed orders. Budget is planned, not actual spend.
with campaign_budget as (
    select channel, sum(budget_amount) as planned_budget_amount
    from {{ ref('stg_campaigns') }}
    group by channel
),
attributed_orders as (
    select coalesce(c.channel, 'unattributed') as channel,
        count(*) as order_count,
        sum(o.completed_order_flag) as completed_orders,
        sum(o.recognized_revenue) as recognized_revenue,
        sum(o.refunded_amount) as refunded_amount
    from {{ ref('fct_orders') }} o
    left join {{ ref('stg_campaigns') }} c on o.campaign_id = c.campaign_id
    group by coalesce(c.channel, 'unattributed')
)
select coalesce(b.channel, a.channel) as channel,
    coalesce(b.planned_budget_amount, 0) as planned_budget_amount,
    coalesce(a.order_count, 0) as order_count,
    coalesce(a.completed_orders, 0) as completed_orders,
    coalesce(a.recognized_revenue, 0) as recognized_revenue,
    coalesce(a.refunded_amount, 0) as refunded_amount
from campaign_budget b
full outer join attributed_orders a on b.channel = a.channel
