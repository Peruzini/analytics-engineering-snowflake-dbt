# Decisões Técnicas

## ADR-001 — Dados sintéticos versionados
Fixtures determinísticas em Python puro, sem segredos, terceiros ou dados reais.

## ADR-002 — dbt + Snowflake em camadas
Schemas no formato `<target.schema>_<custom_schema>`, preservando isolamento por ambiente.

## ADR-003 — CI offline primeiro
GitHub Actions valida testes Python, YAML e parse dbt sem se conectar ao warehouse.

## ADR-004 — Preservação dos dados de origem
Staging não filtra status e não executa deduplicação silenciosa. Violações de contrato são descobertas por testes.

## ADR-005 — Receita por status
Neste case, somente pedidos `completed` geram receita reconhecida. Pedidos `refunded` geram receita zero e valor de reembolso separado; `pending` e `cancelled` preservados. É uma simplificação didática, não uma regra contábil universal.

## ADR-006 — Budget planejado não é gasto
`mart_channel_performance` agrega budget planejado. Não calcula ROAS/CAC sem custo efetivo ou dados de tráfego.

## ADR-007 — Contratos de grão
Itens e pagamentos são agregados separadamente antes do join por pedido. Fatos preservam grãos distintos de pedidos e itens para não multiplicar valores.

## Backlog
MVP-03: testes de conciliação SQL, snapshots, incremental e integração Snowflake. MVP-04: Power BI.
