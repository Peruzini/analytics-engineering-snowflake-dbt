# Arquitetura — MVP-02

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

- Todos os 36 pedidos sintéticos continuam em `fct_orders`, independentemente de status.
- Os 72 itens sintéticos são preservados em `fct_order_items`.
- Pagamentos são agregados antes de juntar aos pedidos; isso evita fanout.
- A receita reconhecida só conta pedidos completed (regra didática documentada).
- `mart_channel_performance` preserva pedidos sem campanha como `unattributed`.
- `planned_budget_amount` não é gasto real de mídia.

## Validação e limites

`profiles.yml` local permanece ignorado. A GitHub Actions executa testes Python/YAML e `dbt parse`, sem acessar Snowflake. Não foram executados `dbt seed/run/test` no warehouse, tampouco incremental ou snapshot nesta etapa.

Consulte [grãos e métricas](model-lineage.md) e [contratos](data-contracts.md).
