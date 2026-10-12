# MVP-02 — Linhagem e modelo dimensional

```text
raw_customers -> stg_customers -> dim_customers -> mart_customer_ltv
raw_products  -> stg_products  -> dim_products
raw_orders    -> stg_orders -----+
raw_order_items -> stg_order_items -> int_order_financials
raw_payments -> stg_payments ------+             |
                                  +-> int_customer_orders -> fct_orders
raw_order_items -> stg_order_items -------------------------> fct_order_items
fct_orders -> fct_order_items / mart_daily_sales / mart_customer_ltv /
              mart_channel_performance
raw_campaigns -> stg_campaigns -> mart_channel_performance
```

Consulte a linhagem real no `dbt docs generate` quando houver ambiente Snowflake.

| Modelo | Grão | Chave |
| --- | --- | --- |
| int_order_financials | pedido com itens | order_id |
| int_customer_orders | todos os pedidos | order_id |
| dim_customers | cliente | customer_id |
| dim_products | produto | product_id |
| fct_orders | pedido | order_id |
| fct_order_items | item | order_item_id |
| mart_daily_sales | dia com pedido | order_date |
| mart_customer_ltv | cliente com ou sem pedidos | customer_id |
| mart_channel_performance | canal incluindo unattributed | channel |

## Fórmulas

- Valor bruto: `quantity * unit_price`.
- Valor líquido transacional: valor bruto menos `discount_amount`, independentemente do status.
- Receita reconhecida neste estudo: valor líquido de pedidos `completed`; nos demais status, zero.
- Valor reembolsado: valor líquido dos pedidos `refunded`, mantido à parte da receita.
- Ticket médio: receita reconhecida / número de pedidos completed (NULL quando zero).
- LTV histórico: soma de receita reconhecida dos pedidos da janela observada, não previsão.
- Canal de aquisição: `stg_campaigns.channel`; pedidos sem campanha entram como `unattributed`.
- Orçamento: budget **planejado** das campanhas. Não representa mídia paga. Não calcular ROAS ou CAC sem custos reais.
- Margem não é calculada porque não existem custos de produto.

**Limite:** testes Python comprovam regras sobre a fixture; `dbt parse` valida dependências SQL/Jinja, mas não executa queries Snowflake. Testes de conciliação SQL e execução de integração virão no MVP-03.
