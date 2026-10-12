-- Reconcile attribution at channel grain, including budget-only zero-order channels.
with expected as (
    select coalesce(c.channel, 'unattributed') as channel,
        count(*) as order_count,
        sum(o.recognized_revenue) as revenue
    from {{ ref('fct_orders') }} o
    left join {{ ref('stg_campaigns') }} c on o.campaign_id = c.campaign_id
    group by coalesce(c.channel, 'unattributed')
), actual as (
    select channel, order_count, recognized_revenue as revenue
    from {{ ref('mart_channel_performance') }}
)
select coalesce(e.channel, a.channel) as channel
from expected e
full outer join actual a on e.channel = a.channel
where a.channel is null
   or coalesce(e.order_count, 0) <> a.order_count
   or abs(coalesce(e.revenue, 0) - a.revenue) > 0.01
