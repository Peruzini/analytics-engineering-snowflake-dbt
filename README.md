# Analytics Engineering — Snowflake + dbt


**Portfólio técnico de Analytics Engineering:** dados sintéticos, dbt, testes SQL, Snowflake como integração final e DuckDB para execução local sem créditos.

> **Status: MVP-03 — incremental, snapshot, testes SQL de reconciliação e integração manual configurados.** A transição local foi versionada; o primeiro LOCAL_FULL_PASS no PC ainda precisa ser comprovado. CI offline não equivale à execução dos modelos no Snowflake. O workflow real usa autenticação por **chave privada**, com usuário de serviço, secrets e disparo manual explícito.

## Problema de negócio

Uma operação de e-commerce recebe dados de clientes, produtos, campanhas, pedidos, itens e pagamentos. Antes de calcular receita, margem, ticket médio, recompra ou aquisição, é necessário padronizar chaves, estados, datas e valores e garantir integridade referencial.

O MVP-01 entregou staging; o **MVP-02** acrescentou 2 modelos intermediate e 7 modelos analíticos. O **MVP-03** acrescenta controle incremental, histórico de clientes, testes SQL e execução Snowflake manual, preservando a regra de receita de pedidos concluídos.

## Arquitetura

```text
Synthetic CSV data (versioned seeds)
             |
             v
dbt seed -> Snowflake target_schema_raw
             |
             v
dbt staging -> Snowflake target_schema_staging
             |
             v
2 intermediate models (target_schema_intermediate)
             |
             v
7 dimensions, facts and marts (target_schema_analytics)
             |
             v
MVP-03: MERGE incremental + customer snapshot + SQL reconciliation
             |
             v
Optional manual Snowflake integration (no automatic run)
             |
             v
MVP-04: Power BI on analytics marts
```

O padrão `target_schema_<custom_schema>` é o comportamento padrão de schema customizado do dbt. Não há necessidade de credenciais para gerar dados sintéticos nem para validar sintaxe localmente.

## Evidências dos MVPs 01–03

- **6 fontes CSV sintéticas** e gerador determinístico com Python (stdlib).
- **6 modelos staging, 2 intermediate e 7 modelos analíticos**, usando `source()`, `ref()`, contratos, grãos explícitos e status preservados.
- **Testes dbt** para unicidade, obrigatoriedade, integridade referencial e domínios, além de **5 testes SQL singulares** para conciliação de métricas.
- **Testes Python** para integridade dos CSVs, reprodutibilidade e reconciliação matemática offline de receita entre dia, cliente e canal.
- **MVP-03:** MERGE incremental de `fct_orders`, snapshot SCD2 de clientes e workflow manual `dbt seed/run/snapshot/test` (não executado automaticamente).
- **Validação no PC** com Python, YAML, `dbt parse` offline e execução SQL completa no DuckDB (pendente de PASS no Windows).
- Documentação de arquitetura, dicionário de dados e decisões técnicas.

## Como executar no seu PC (Git Bash)

```bash
git clone https://github.com/Peruzini/analytics-engineering-snowflake-dbt.git
cd analytics-engineering-snowflake-dbt
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
python scripts/local_ci.py --quick
python scripts/local_ci.py --full
```

O modo `--full` executa dbt com DuckDB local temporário (seed, run, incremental, snapshot, test) e faz parse de Snowflake offline com placeholders. **Sem consumo de Actions hospedado nem consultas Snowflake.** O resultado verificável fica em `.local-evidence/latest.json`. Para preparar evidência revisável no Git, após commitar o código: `python scripts/local_ci.py --full --publish`.

**Execução GitHub Actions:** ambos workflows agora são somente manuais e usam runner Windows self-hosted `ae-local`, que ainda precisa ser registrado neste repositório. A execução direta via Git Bash dispensa esse runner. O Snowflake real permanece uma validação excepcional, confirmada, com créditos.

Veja [política de execução local](docs/LOCAL_EXECUTION_POLICY.md), [guia Windows](docs/LOCAL_SETUP_WINDOWS.md) e [Snowflake operações](docs/mvp03-operations.md).


## Estrutura

- `seeds/` — dados sintéticos controlados;
- `scripts/` — geração determinística;
- `models/staging/` — 6 modelos staging;
- `models/intermediate/` — agregações financeiras por pedido e regra de receita;
- `models/marts/` — 2 dimensões, 2 fatos e 3 marts analíticos, com `fct_orders` incremental;
- `models/staging/_sources.yml` — definições das seis fontes;
- `models/staging/_models.yml` — testes e documentação;
- `snapshots/` — snapshot SCD2 de clientes;
- `tests/dbt/` — cinco testes de reconciliação SQL;
- `tests/` — testes Python de qualidade e reprodução;
- `docs/` — arquitetura, contratos, linhagem e decisões;
- `.github/workflows/ci.yml` — execução somente manual em runner próprio;
- `.github/workflows/snowflake-integration.yml` — integração Snowflake manual no runner próprio, ainda não validada.

## Próximos marcos

1. **Validar a execução local no Windows:** obter `LOCAL_FULL_PASS` e registrar a evidência. Só então autorizar integração real Snowflake.
2. **MVP-04:** Power BI consumindo os marts.

Importante: o orçamento de campanhas é **planejado**, não gasto real. Não há base suficiente para calcular ROAS, CAC ou margem.

Dados e marcas são fictícios. Este repositório não inclui informações de clientes ou empregadores.
