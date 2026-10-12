# Arquitetura — MVP-03

## Pipeline

O projeto usa seis CSVs sintéticos gerados de forma determinística e versionados.

```text
6 CSVs -> dbt seed (RAW)
            |
            v
       6 staging views
            |
            v
       2 intermediate views
            |
            v
       2 dimensions + 2 facts + 3 aggregated marts
            |
            +--> fct_orders incremental MERGE
            +--> snap_customers (SCD2)
            +--> 5 SQL reconciliation tests
            |
            v
       Power BI (MVP-04)
```

## Esquemas por ambiente

O dbt usa o padrão `<target.schema>_<custom_schema>`; isso separa o ambiente de cada usuário.

| Layer | Schema esperado se target.schema=DBT_DEV |
| --- | --- |
| Seeds | DBT_DEV_raw |
| Staging | DBT_DEV_staging |
| Intermediate | DBT_DEV_intermediate |
| Marts | DBT_DEV_analytics |

## Cuidados na modelagem

- Todos os **4.200** pedidos sintéticos continuam em `fct_orders`, independentemente de status.
- Os **8.400** itens sintéticos são preservados em `fct_order_items`.
- Pagamentos são agregados antes de juntar aos pedidos; isso evita fanout.
- A receita reconhecida só conta pedidos completed (regra didática documentada).
- `mart_channel_performance` preserva pedidos sem campanha como `unattributed`.
- **MVP-04B:** `fct_orders.channel` também registra o canal no grão de pedido, permitindo análises por data/canal no Power BI sem somar o mart agregado.
- `planned_budget_amount` não é gasto real de mídia.

## Validação e limites

`profiles.yml` local permanece ignorado. O pipeline Snowflake **foi executado com sucesso no baseline anterior à migração** (6 seeds, 15 modelos, 1 snapshot e 88 testes), evidenciado em [relatório](SNOWFLAKE_INTEGRATION_BASELINE_2026-10-12.md). Na arquitetura atual, testes rotineiros usam dbt + DuckDB no PC; Actions apenas manual self-hosted. O MVP-04A ampliou a fixture sintética para 12 meses e exportou 7 CSVs versionados, ainda pendentes da paridade dbt. A aprovação Snowflake é do dataset anterior, não do atual. [Cenário MVP-04A](MVP04A_DATASET.md) · [Plano Power BI](MVP04_POWERBI.md).

Consulte [grãos e métricas](model-lineage.md), [contratos](data-contracts.md) e [análise MVP-04B](MVP04B_ANALISE.md).
