# MVP-04B — Análise e indicadores para portfólio

**Natureza:** case sintético, 2025-10-01 a 2026-09-30. Análise descritiva dos sete CSVs versionados, **não de uma operação real**. Os indicadores abaixo foram calculados dos arquivos de marts do Git; não são evidência de execução no Power BI Desktop ou paridade com dbt.

## Perguntas de negócio, indicadores e decisões possíveis

| Pergunta | Indicadores | Análise/decisão que o dashboard permite |
| --- | --- | --- |
| A receita cresceu? Por quê? | Receita, pedidos concluídos, ticket médio, receita mês anterior, MoM, receita/dia | Separar efeito de volume, valor por pedido e duração do mês |
| Onde se concentram as falhas do funil de pedidos? | Taxas de conclusão, cancelamento, reembolso; valor reembolsado | Comparar status por período/canal; investigar categorias de pedidos, não declarar perdas realizadas |
| Quais produtos explicam a receita? | Receita reconhecida de itens, unidades concluídas, participação por produto | Priorizar mix e concentração, sem alegar margem (não há custos) |
| Quantos clientes compram repetidamente? | Compradores, clientes com 2+ pedidos concluídos, taxa de recompra no período | Medir frequência *na seleção*; **não é retenção de coorte** |
| Quais canais têm melhor desempenho? | Receita reconhecida, participação de receita, ticket, taxa de conclusão/reembolso filtrados por mês | Comparar padrões simulados; sem afirmar causalidade ou calcular ROAS/CAC |

## Descobertas observadas nos CSVs

1. **Novembro simulado cresce principalmente em volume.** Receita passa de **R$ 238.223,92 (out/25)** a **R$ 338.418,72 (nov/25)** (**+42,06%**). Pedidos concluídos sobem de 306 a 450 (**+47,06%**), enquanto o ticket médio cai de R$ 778,51 a R$ 752,04 (aprox. **−3,40%**). Interpretação: a elevação de receita coincide com maior volume, não com ticket maior. O padrão foi programado no gerador.
2. **Comparação mensal exige normalização por dia.** Fevereiro/26 registra receita de **R$ 158.248,51** em 28 dias (**R$ 5.651,73/dia**); novembro/25 tem **R$ 11.280,62/dia** em 30 dias. A leitura só por total mistura sazonalidade e duração do mês.
3. **Status por canal variam na simulação.** Taxa de pedidos concluídos: **email 91,45%**, **organic 89,23%**, **paid_search 82,16%**, **social 80,47%** e **unattributed 81,76%**. As probabilidades foram definidas pelo código do cenário; diferenças **não demonstram qualidade causal** de canais.
4. **Recompra aparece artificialmente elevada.** Dos 420 compradores, 414 têm ao menos 2 pedidos `completed` (**98,57%**). É uma propriedade gerada, não evidência de fidelização, cohort retention ou LTV futuro.
5. **Checagem de viés de atribuição.** `unattributed` reúne 466 de 4.200 pedidos (**11,10%**) mas apenas **2,86% da receita reconhecida**. Como os dados são determinísticos, diferenças na seleção de itens/pedidos podem resultar da própria função geradora. Tratar como **alerta de qualidade/simulação**, não interpretação de marketing real.

Valor total do case: **R$ 2.699.981,55 de receita reconhecida**, conciliada entre pedido, item, dia, cliente e canal na construção da fixture.

## Alterações concretas no modelo

- **Canal no grão de pedido:** `int_customer_orders` mapeia `stg_campaigns` para `channel`, com fallback `unattributed`. `fct_orders` preserva esse campo e a lógica incremental; o CSV e `FatoPedidos[channel]` correspondem à mesma informação.
- **Canais agora respeitam período:** a quarta página usa `FatoPedidos[channel]` e `DimData[AnoMes]`, evitando a limitação dos agregados históricos desconectados de data.
- **39 medidas DAX** no modelo: 27 anteriores + 12 novas relacionadas a tendência mensal, média diária/móvel, status, descontos em completed, recompra no período e participação de receita por canal/produto.
- **4 páginas e 43 visuais ao concluir 04B**, incluindo série mensal por canal, resumo mensal com MoM e revenue/day, análise de recompra e ranking por produto.
- **Separação de grãos:** produto se calcula no fato de itens. Receita agregada histórica de `ResumoCanais` não é combinada com métricas filtradas do fato detalhado.
- **Primeiro mês sem comparação anterior:** a medida de MoM retorna BLANK sem mês anterior válido. Não há comparação YoY confiável com apenas 12 meses.
- **Budget planejado** continua documentado no agregado, mas **não** é spend real; não há ROAS, CAC ou margem.

## Reprodução
- Medidas: [catálogo DAX](../powerbi/dax/CATALOGO.md).
- Auditoria descritiva: `python scripts/analyze_business.py` (stdlib, somente leitura).
- Testes de referência: `python -m unittest discover -s tests -v`.
- Teste dbt real, ainda pendente após mudança de schema: `python scripts/local_ci.py --full`.
- Equivalência de CSVs com SQL/dbt, ainda pendente: `python scripts/export_powerbi.py --check`.
- Round-trip no Desktop e checagem visual: pendente.

A integração Snowflake de 88 testes PASS foi feita **antes** do dataset MVP-04A e da nova coluna `channel`. Não reaproveitar essa evidência como aprovação do MVP-04B.

## Próximo marco
**MVP-04C — UX e storytelling:** a etapa seguinte reorganizou a narrativa e ampliou de 43 para 50 visuais editáveis (ver [documentação](MVP04C_UX_STORYTELLING.md)). Permanecem os gates locais e a validação visual real do Desktop.
