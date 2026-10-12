# Evidência real — dbt + Snowflake (baseline anterior à execução local)

## Identificação
- Data: **2026-10-12**.
- Workflow: `Snowflake Integration (Manual)`; execução explícita por `workflow_dispatch`.
- [GitHub Actions Run #38315794938](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/runs/38315794938).
- Commit executado: `1007ddaa9f06e6a9bcb2ce08c912ee71941535f5`, **anterior** à migração para DuckDB e self-hosted.
- Job: `dbt seed/run/snapshot/test (key pair)`, ID `115031986096`.
- Resultado do job: **SUCCESS**.

## Validação realizada
| Etapa | Resultado | WARN | ERROR |
| --- | ---: | ---: | ---: |
| Autenticação e `dbt debug` | PASS | — | — |
| `dbt seed` | 6/6 PASS | 0 | 0 |
| `dbt run` | 15/15 PASS | 0 | 0 |
| `dbt snapshot` | 1/1 PASS | 0 | 0 |
| `dbt test` | 88/88 PASS | 0 | 0 |

Entre os testes aprovados estão cinco reconciliações SQL singulares: `assert_channel_revenue_reconciles`, `assert_customer_ltv_reconciles`, `assert_daily_sales_reconciles`, `assert_order_items_reconcile` e `assert_order_revenue_status`.

## Escopo e limites
**Está provado:** o baseline `1007ddaa` conseguiu autenticar via key pair, criar os seeds/modelos, executar um snapshot e concluir 88 testes no Snowflake.

**Ainda não está provado:** idempotência de uma segunda run Snowflake, histórico SCD2 após alterar atributos, atualização retroativa em MERGE, paridade da nova versão SQL com TRY_CAST, funcionamento do novo runner Windows ou execução local DuckDB.

Apenas conservar a evidência. Não repetir uma Run paga apenas para produzir outro resultado verde. Qualquer nova execução exige objetivo e autorização explícitos.

## Proveniência
Dados extraídos dos jobs e logs da [Run #38315794938](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/runs/38315794938). Nenhuma senha, chave privada ou token é incluído neste documento.
