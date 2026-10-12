{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge' if target.type == 'snowflake' else 'delete+insert',
    on_schema_change='fail'
) }}

-- Grain: one order, including cancelled, pending and refunded orders.
-- In absence of reliable updated_at, scan the small source and MERGE only
-- new/changed rows. No date watermark means late updates are not silently lost.
-- Hard-deleted source orders are not removed automatically.
with incoming as (
    select
        order_id, customer_id, campaign_id, order_date, order_status,
        item_count, unit_count, gross_item_amount, discount_amount,
        net_item_amount, payment_count, payment_amount,
        recognized_revenue, refunded_amount, completed_order_flag
    from {{ ref('int_customer_orders') }}
)
select incoming.*
from incoming
{% if is_incremental() %}
where not exists (
    select 1
    from {{ this }} existing
    where existing.order_id = incoming.order_id
        and             existing.order_id is not distinct from incoming.order_id
        and             existing.customer_id is not distinct from incoming.customer_id
        and             existing.campaign_id is not distinct from incoming.campaign_id
        and             existing.order_date is not distinct from incoming.order_date
        and             existing.order_status is not distinct from incoming.order_status
        and             existing.item_count is not distinct from incoming.item_count
        and             existing.unit_count is not distinct from incoming.unit_count
        and             existing.gross_item_amount is not distinct from incoming.gross_item_amount
        and             existing.discount_amount is not distinct from incoming.discount_amount
        and             existing.net_item_amount is not distinct from incoming.net_item_amount
        and             existing.payment_count is not distinct from incoming.payment_count
        and             existing.payment_amount is not distinct from incoming.payment_amount
        and             existing.recognized_revenue is not distinct from incoming.recognized_revenue
        and             existing.refunded_amount is not distinct from incoming.refunded_amount
        and             existing.completed_order_flag is not distinct from incoming.completed_order_flag
)
{% endif %}
