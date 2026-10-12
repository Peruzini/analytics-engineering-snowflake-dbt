# Contratos de Dados — MVP-02

## Sources e staging

| Source | Grão | Chave |
| --- | --- | --- |
| raw_customers | cliente | customer_id |
| raw_products | produto | product_id |
| raw_campaigns | campanha | campaign_id |
| raw_orders | pedido | order_id |
| raw_order_items | item de pedido | order_item_id |
| raw_payments | pagamento | payment_id |

## Contratos de marts

| Modelo | Grão | Uso |
| --- | --- | --- |
| dim_customers | cliente | segmentação por região |
| dim_products | produto | categoria, catálogo |
| fct_orders | pedido | receitas, descontos, status e quantidade de pedidos |
| fct_order_items | item | análise por produto |
| mart_daily_sales | dia com pedidos | evolução e ticket médio |
| mart_customer_ltv | cliente | histórico de pedidos e LTV observada |
| mart_channel_performance | canal incluindo unattributed | atribuição e orçamento planejado |

## Regras financeiras

- `completed`: somente este status contribui para `recognized_revenue`.
- `refunded`: receita zero neste case e valor separado em `refunded_amount`.
- `pending` / `cancelled`: receita zero e status preservado.
- `net_item_amount` não equivale a receita, pois abrange todos os status.
- `planned_budget_amount` não equivale a despesa realizada.
- `lifetime_recognized_revenue` é receita reconhecida acumulada, não LTV predita.
- A regra é uma simplificação didática, não política contábil universal.

Leia [modelo e linhagem](model-lineage.md).

## Verificação

Python, YAML, DuckDB e dbt são validados localmente. Já houve execução Snowflake real anterior à migração, com 6 seeds, 15 modelos, 1 snapshot e 88 testes PASS ([evidência](SNOWFLAKE_INTEGRATION_BASELINE_2026-10-12.md)). Para MVP-04, o script `scripts/export_powerbi.py --check` deve comparar os 7 CSVs com saídas canônicas dbt DuckDB, antes de abrir o Power BI.

## Implementação MVP-03

- `fct_orders` usa `materialized='incremental'` e `incremental_strategy='merge'`, com `unique_key='order_id'`. Comparação NULL-safe identifica novas linhas ou mudanças em todos os 15 campos; exclusões físicas não são propagadas.
- `snap_customers` usa estratégia `check` em `email` e `region`, preservando versões históricas a cada execução com mudanças de dados.
- Cinco testes SQL em `tests/dbt/` retornam linhas de divergência; todos tiveram PASS na execução Snowflake baseline de 12/10/2026.

[Protocolo operacional](mvp03-operations.md).
