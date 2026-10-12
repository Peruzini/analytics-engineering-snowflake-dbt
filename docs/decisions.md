# Decisões Técnicas

## ADR-001 — Dados sintéticos versionados
Fixtures determinísticas em Python puro, sem segredos, terceiros ou dados reais.

## ADR-002 — dbt + Snowflake em camadas
Schemas no formato `<target.schema>_<custom_schema>`, preservando isolamento por ambiente.

## ADR-003 — CI offline primeiro (histórico; substituído pela ADR-011)
GitHub Actions valida testes Python, YAML e parse dbt sem se conectar ao warehouse.

## ADR-004 — Preservação dos dados de origem
Staging não filtra status e não executa deduplicação silenciosa. Violações de contrato são descobertas por testes.

## ADR-005 — Receita por status
Neste case, somente pedidos `completed` geram receita reconhecida. Pedidos `refunded` geram receita zero e valor de reembolso separado; `pending` e `cancelled` preservados. É uma simplificação didática, não uma regra contábil universal.

## ADR-006 — Budget planejado não é gasto
`mart_channel_performance` agrega budget planejado. Não calcula ROAS/CAC sem custo efetivo ou dados de tráfego.

## ADR-007 — Contratos de grão
Itens e pagamentos são agregados separadamente antes do join por pedido. Fatos preservam grãos distintos de pedidos e itens para não multiplicar valores.

## ADR-008 — Incremental por comparação de alterações
Sem campo confiável de atualização nos dados originais, `fct_orders` compara toda a pequena origem a cada run e envia ao MERGE apenas os pedidos novos ou modificados. Esse desenho evita perder mudanças antigas, mas não realiza CDC nem captura exclusões físicas; é uma escolha consciente para o portfólio, não o padrão ideal para grandes volumes.

## ADR-009 — Snapshot por comparação de atributos
O snapshot de clientes usa check strategy em e-mail e região (não `created_at`, que representa cadastro). A execução do snapshot é distinta do modelo corrente de clientes.

## ADR-010 — Integração isolada e manual
Nenhuma conexão Snowflake é acionada por push. O workflow de integração exige confirmação `yes`, secrets configurados e role restrita. CI comum permanece offline.

## ADR-011 — Local-first, sem Actions automáticas (12/10/2026)
Gates no PC, workflows apenas manuais self-hosted, sem uso de Actions Artifact. Evidência JSON local, publicação revisada em Git. [Política](LOCAL_EXECUTION_POLICY.md).

## ADR-012 — Teste SQL real em DuckDB
Para validar dados/modelos localmente sem Snowflake, usar TRY_CAST compatível nos staging e incremental delete+insert no DuckDB, preservando merge no Snowflake. DuckDB PASS não substitui integração Snowflake.

## ADR-013 — Evidência de integração Snowflake anterior à migração
A [Run #38315794938](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/runs/38315794938) executou de fato no Snowflake o commit `1007ddaa`: 6 seeds, 15 modelos, 1 snapshot e 88 testes PASS. Essa evidência não valida o SQL modificado na migração local. [Relatório](SNOWFLAKE_INTEGRATION_BASELINE_2026-10-12.md).

## Backlog
Validar localmente no PC o commit pós-migração (`LOCAL_FULL_PASS`), sem repetir a Run Snowflake por padrão. MVP-04: Power BI.

## ADR-014 — Fleet-first para Power BI
Construir o PBIP com modelo tabular, PBIR, DAX e dados primeiro em Git. O Desktop fica reservado para validação final. Fontes Power Query M usam GitHub raw público para evitar Snowflake e paths absolutos. [MVP-04](MVP04_POWERBI.md).
