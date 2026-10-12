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

CI offline executa testes Python sobre os datasets, valida YAML, modelos existentes e `dbt parse`. Os testes genéricos dbt (`unique`, `not_null`, `relationships`, `accepted_values`) ficam declarados para execução futura em Snowflake. A execução real de `dbt seed/run/test` e a conciliação SQL serão validadas separadamente no MVP-03.
