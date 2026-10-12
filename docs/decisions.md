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

## ADR-008 — Incremental por comparação de alterações
Sem campo confiável de atualização nos dados originais, `fct_orders` compara toda a pequena origem a cada run e envia ao MERGE apenas os pedidos novos ou modificados. Esse desenho evita perder mudanças antigas, mas não realiza CDC nem captura exclusões físicas; é uma escolha consciente para o portfólio, não o padrão ideal para grandes volumes.

## ADR-009 — Snapshot por comparação de atributos
O snapshot de clientes usa check strategy em e-mail e região (não `created_at`, que representa cadastro). A execução do snapshot é distinta do modelo corrente de clientes.

## ADR-010 — Integração isolada e manual
Nenhuma conexão Snowflake é acionada por push. O workflow de integração exige confirmação `yes`, secrets configurados e role restrita. CI comum permanece offline.

## Backlog
Executar e evidenciar teste real no Snowflake quando houver conta configurada. MVP-04: Power BI.
