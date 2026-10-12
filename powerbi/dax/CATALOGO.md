# Catálogo DAX — Ecommerce Analytics

O código executável das medidas está no arquivo `powerbi/EcommerceAnalytics.SemanticModel/model.bim`.

| Medida | Expressão DAX | Formato |
| --- | --- | --- |
| Receita Reconhecida | `SUM(FatoPedidos[recognized_revenue])` | R$ #,0.00 |
| Pedidos Totais | `DISTINCTCOUNT(FatoPedidos[order_id])` | #,0 |
| Pedidos Concluídos | `SUM(FatoPedidos[completed_order_flag])` | #,0 |
| Pedidos Pendentes | `CALCULATE([Pedidos Totais], FatoPedidos[order_status] = "pending")` | #,0 |
| Pedidos Cancelados | `CALCULATE([Pedidos Totais], FatoPedidos[order_status] = "cancelled")` | #,0 |
| Pedidos Reembolsados | `CALCULATE([Pedidos Totais], FatoPedidos[order_status] = "refunded")` | #,0 |
| Ticket Médio | `DIVIDE([Receita Reconhecida], [Pedidos Concluídos])` | R$ #,0.00 |
| Taxa Conclusão % | `DIVIDE([Pedidos Concluídos], [Pedidos Totais])` | 0.0% |
| Taxa Reembolso % | `DIVIDE([Pedidos Reembolsados], [Pedidos Totais])` | 0.0% |
| Valor Bruto Itens | `SUM(FatoItens[gross_item_amount])` | R$ #,0.00 |
| Descontos Itens | `SUM(FatoItens[discount_amount])` | R$ #,0.00 |
| Reembolsos Valor | `SUM(FatoPedidos[refunded_amount])` | R$ #,0.00 |
| Receita Itens | `SUM(FatoItens[recognized_item_revenue])` | R$ #,0.00 |
| Unidades Pedidos Concluídos | `CALCULATE(SUM(FatoItens[quantity]), FatoItens[order_status] = "completed")` | #,0 |
| Clientes Cadastrados | `DISTINCTCOUNT(DimClientes[customer_id])` | #,0 |
| Clientes Compradores | `CALCULATE(DISTINCTCOUNT(FatoPedidos[customer_id]), FatoPedidos[order_status] = "completed")` | #,0 |
| Receita por Cliente Comprador | `DIVIDE([Receita Reconhecida], [Clientes Compradores])` | R$ #,0.00 |
| Receita Acumulada | `VAR UltimaData = MAX(DimData[Data]) RETURN CALCULATE([Receita Reconhecida], FILTER(ALLSELECTED(DimData[Data]), DimData[Data] <= UltimaData))` | R$ #,0.00 |
| Receita Rolling 7d | `CALCULATE([Receita Reconhecida], DATESINPERIOD(DimData[Data], MAX(DimData[Data]), -7, DAY))` | R$ #,0.00 |
| Receita por Canal - Histórico | `SUM(ResumoCanais[recognized_revenue])` | R$ #,0.00 |
| Budget Planejado - Total | `SUM(ResumoCanais[planned_budget_amount])` | R$ #,0.00 |
| Pedidos por Canal - Histórico | `SUM(ResumoCanais[order_count])` | #,0 |
| Pedidos Concluídos por Canal | `SUM(ResumoCanais[completed_orders])` | #,0 |
| Ticket Médio por Canal | `DIVIDE([Receita por Canal - Histórico], [Pedidos Concluídos por Canal])` | R$ #,0.00 |
| Receita Histórica Clientes | `SUM(ResumoClientes[lifetime_recognized_revenue])` | R$ #,0.00 |
| Pedidos Históricos Clientes | `SUM(ResumoClientes[lifetime_orders])` | #,0 |
| Descontos sobre Bruto % | `DIVIDE([Descontos Itens], [Valor Bruto Itens])` | 0.0% |

Nota: medidas de ResumoCanais são históricas e não respondem a filtros de data. Orçamento planejado não é gasto nem autoriza ROAS/CAC.
