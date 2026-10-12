-- Ensure order-grain channel attribution agrees with campaign staging.
-- Unattributed means no campaign; tests the Power BI time-filterable channel.
with expected as (
    select o.order_id, coalesce(c.channel, 'unattributed') as expected_channel
    from {{ ref('fct_orders') }} o
    left join {{ ref('stg_campaigns') }} c on o.campaign_id = c.campaign_id
)
select o.order_id
from {{ ref('fct_orders') }} o
join expected e on o.order_id = e.order_id
where o.channel is distinct from e.expected_channel
