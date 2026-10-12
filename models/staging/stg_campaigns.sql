with source as (
    select * from {{ source('raw', 'raw_campaigns') }}
)
select
    trim(cast(campaign_id as varchar)) as campaign_id,
    trim(cast(channel as varchar)) as channel,
    try_to_decimal(cast(budget_amount as varchar), 18, 2) as budget_amount
from source
