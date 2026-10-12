> **AUDITORIA HISTÓRICA (dataset anterior).** Este documento registra o commit-base `b516f40` com 36 pedidos e não corresponde ao novo cenário MVP-04A (4.200 pedidos). Consulte [MVP-04A](MVP04A_DATASET.md) para os dados vigentes.

# Auditoria estática MVP-04 — 12/10/2026

## Escopo e referência

Repositório: [Peruzini/analytics-engineering-snowflake-dbt](https://github.com/Peruzini/analytics-engineering-snowflake-dbt)

Commit-base auditado: `b516f40a4bca3a1577705cabf2c1ac6840152515`. Auditoria via leitura direta dos artefatos versionados no GitHub, **sem Power BI Desktop, dbt, GitHub Actions ou acesso ao Snowflake**.

## Resultado comprovado na leitura estática

| Controle | Evidência | Parecer |
| --- | --- | --- |
| PBIP / projeto Git | Entrada `EcommerceAnalytics.pbip`, pastas `.Report` e `.SemanticModel` presentes | Estrutura presente |
| Conteúdo do relatório | 4 páginas, 41 `visual.json` encontrados | Estrutura presente |
| Referências PBIR | Todos os 41 visuais lidos; colunas e medidas referenciadas existem no modelo | Sem referências ausentes |
| Modelo semântico | 9 tabelas, 5 relacionamentos, 27 medidas | Inventário confirmado |
| DAX (dependências) | Referências qualificadas `Tabela[Coluna]` e dependências `[Medida]` presentes no catálogo do modelo | Sem referências ausentes |
| Dados CSV | 7 tabelas, 36 pedidos, 72 itens, 28 dias, 12 clientes, 8 produtos e 5 canais | Inventário confirmado |
| Chaves / relações | Sem chaves duplicadas em 7 tabelas; pedidos com cliente válido, itens com pedidos, clientes e produtos válidos | Sem erro observado |
| Reconciliação de receita | Pedidos = Itens = Dia = Cliente = Canal = **R$ 14.250,40** | Valores conciliados ao centavo |
| Status financeiro | Pedidos diferentes de `completed` têm receita reconhecida zero; pedidos concluídos conciliam com itens líquidos | Consistente com a regra didática |

A auditoria foi adicionada aos testes estáticos do repositório. A verificação aqui relatada é de **conteúdo e referências**, não de renderização nem execução nativa do motor Tabular.

## Limites e pendências

1. **Execução dos testes Python nesta revisão:** não realizada; a existência do teste versionado não representa PASS.
2. **Paridade canônica CSV ↔ dbt DuckDB:** ainda não executada neste commit. Usar `python scripts/export_powerbi.py --check` depois de atualizar o clone. Se houver DRIFT, não declarar aptidão para o Desktop antes de corrigir as saídas.
3. **Power BI Desktop (PBIP, Power Query M, DAX e visuais):** ainda não aberto nem submetido a round-trip. Só esse gate verifica renderização, compatibilidade da versão instalada e refresh.
4. **Snowflake:** integração anterior foi aprovada no baseline próprio; não foi acionado nesta auditoria.

## Próximo gate

**Validar CSVs contra dbt no PC usando DuckDB; sem Snowflake nem GitHub Actions.** Com PASS, abrir e inspecionar o PBIP completo no Power BI Desktop. Não é necessário produzir novo software de infraestrutura.

Detalhes do plano: [MVP04_POWERBI.md](MVP04_POWERBI.md).
