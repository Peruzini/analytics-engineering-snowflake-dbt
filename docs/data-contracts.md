# Contratos de Dados — MVP-01

| Source | Grão | Chave | Principal regra |
| --- | --- | --- | --- |
| raw_customers | cliente | customer_id | email único, cadastro com data |
| raw_products | produto | product_id | preço de lista não nulo |
| raw_campaigns | campanha | campaign_id | canal conhecido |
| raw_orders | pedido | order_id | cliente existente, campanha opcional, status conhecido |
| raw_order_items | item de pedido | order_item_id | pedido e produto existentes, quantidade e valores não nulos |
| raw_payments | pagamento | payment_id | pedido existente e método/status conhecido |

## Estados de pedido

- `completed`: pedido concluído, com pagamento `paid` na amostra;
- `refunded`: pedido reembolsado, com evento `refunded`;
- `pending`: pedido pendente, sem pagamento;
- `cancelled`: pedido cancelado, sem pagamento.

## Regras financeiras da amostra

Valor bruto de item: `quantity * unit_price`.

Valor líquido de item: `quantity * unit_price - discount_amount`.

Valor do pagamento sintético: soma dos valores líquidos dos itens do pedido.

**Importante:** valor transacionado não equivale automaticamente a receita contábil. Os marts deverão documentar tratamento de pedidos reembolsados/cancelados e conciliar as duas camadas.

## Testes

- dbt: `not_null`, `unique`, `relationships`, `accepted_values`;
- Python: comparação byte a byte dos CSVs, chaves de negócio, referências e reconciliação do valor do pagamento.

A execução de testes dbt no warehouse requer Snowflake configurado. O CI do MVP-01 só valida parse e testes Python.
