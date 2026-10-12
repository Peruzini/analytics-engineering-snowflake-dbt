# Catálogo DAX — Ecommerce Analytics (MVP-04B)

**Fonte de execução:** [model.bim](../EcommerceAnalytics.SemanticModel/model.bim). Este arquivo serve para revisão; não duplicar as medidas manualmente no Desktop.

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
| Receita Mês Anterior | `VAR DataAtual = MIN(DimData[Data]) VAR InicioAnterior = EOMONTH(DataAtual, -2) + 1 VAR FimAnterior = EOMONTH(DataAtual, -1) RETURN IF(HASONEVALUE(DimData[AnoMes]), CALCULATE([Receita Reconhecida], REMOVEFILTERS(DimData), DATESBETWEEN(DimData[Data], InicioAnterior, FimAnterior)))` | R$ #,0.00 |
| Variação Receita MoM % | `VAR Anterior = [Receita Mês Anterior] RETURN DIVIDE([Receita Reconhecida] - Anterior, Anterior)` | 0.0% |
| Receita Média Móvel 7d | `VAR Fim = MAX(DimData[Data]) VAR Primeira = MINX(ALL(DimData[Data]), DimData[Data]) VAR Inicio = MAX(Primeira, Fim - 6) RETURN DIVIDE(CALCULATE([Receita Reconhecida], REMOVEFILTERS(DimData), DATESBETWEEN(DimData[Data], Inicio, Fim)), Fim - Inicio + 1)` | R$ #,0.00 |
| Taxa Cancelamento % | `DIVIDE([Pedidos Cancelados], [Pedidos Totais])` | 0.0% |
| Desconto Concluídos | `CALCULATE(SUM(FatoItens[discount_amount]), FatoItens[order_status] = "completed")` | R$ #,0.00 |
| Bruto Concluídos | `CALCULATE(SUM(FatoItens[gross_item_amount]), FatoItens[order_status] = "completed")` | R$ #,0.00 |
| Taxa Desconto Concluídos % | `DIVIDE([Desconto Concluídos], [Bruto Concluídos])` | 0.0% |
| Clientes Recorrentes (2+) | `COUNTROWS(FILTER(VALUES(DimClientes[customer_id]), CALCULATE([Pedidos Concluídos]) >= 2))` | #,0 |
| Taxa Recompra Período % | `DIVIDE([Clientes Recorrentes (2+)], [Clientes Compradores])` | 0.0% |
| Participação Receita Canal % | `DIVIDE([Receita Reconhecida], CALCULATE([Receita Reconhecida], REMOVEFILTERS(FatoPedidos[channel])))` | 0.0% |
| Participação Receita Produto % | `DIVIDE([Receita Itens], CALCULATE([Receita Itens], ALLSELECTED(DimProdutos)))` | 0.0% |

**Importante:** métricas com *Histórico* e orçamento planejado vêm de `ResumoCanais`, sem filtro temporal. A página de canais do MVP-04B utiliza `FatoPedidos[channel]` para análise por período/região; nunca combinar valores agregados históricos com métricas filtradas como se tivessem o mesmo contexto. A recompra mede 2+ pedidos `completed` na seleção, não retenção de coorte. `Variação Receita MoM %` requer seleção de um único mês e não deve ser usada como taxa YoY. Produtos usam o grão de itens; não usar receita de pedidos para filtrar por produto sem relação reversa.
