# Analytics Engineering — Snowflake + dbt

[![CI](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml/badge.svg)](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml)

**Portfólio técnico de Analytics Engineering:** dados sintéticos de e-commerce, transformações SQL com dbt, contratos, testes de qualidade e CI. O projeto foi desenhado para execução no Snowflake, com verificações offline reproduzíveis.

> **Status: MVP-03 — incremental, snapshot, testes SQL de reconciliação e integração manual configurados.** CI offline não equivale à execução dos modelos no Snowflake. O workflow real depende de secrets e de disparo manual explícito.

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
- **CI offline** com validação Python, YAML e `dbt parse`, sem acesso ao Snowflake.
- Documentação de arquitetura, dicionário de dados e decisões técnicas.

## Como executar

### 1. Dados e testes offline

```bash
python scripts/generate_data.py --output-dir seeds
python -m unittest discover -s tests -v
```

### 2. Dependências

```bash
python -m pip install -r requirements.txt
```

### 3. Parse do projeto sem conectar ao Snowflake

O arquivo `profiles.yml.example` é apenas um modelo, sem segredos. Crie um `profiles.yml` local a partir dele e defina variáveis de ambiente (`DBT_SNOWFLAKE_ACCOUNT`, `DBT_SNOWFLAKE_USER`, `DBT_SNOWFLAKE_PASSWORD`). Para testar somente o parse, podem ser placeholders, pois não há execução de consultas:

```bash
cp profiles.yml.example profiles.yml
dbt parse --profiles-dir .
```

No CI, esse arquivo é criado no runner com valores fictícios. O workflow não roda `dbt seed/run/test` remotamente.

### 4. Rodar de fato no Snowflake (opcional e com credenciais próprias)

Configure o perfil Snowflake com conta, usuário, credencial, `warehouse`, `database`, `role` e `schema` válidos. Depois:

```bash
dbt seed --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
dbt docs generate --profiles-dir .
```

A execução SQL real depende de conta e credenciais configuradas. O workflow manual também inclui `dbt snapshot`. **Não afirmar validação Snowflake sem uma run de integração verde.** `profiles.yml` não deve ser commitado. Veja [como configurar e validar o MVP-03](docs/mvp03-operations.md).

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
- `.github/workflows/ci.yml` — validação offline;
- `.github/workflows/snowflake-integration.yml` — integração Snowflake exclusivamente manual.

## Próximos marcos

1. **Validação externa do MVP-03:** configurar acesso Snowflake e executar o workflow manual, registrando evidências de `dbt seed/run/snapshot/test`.
2. **MVP-04:** Power BI consumindo os marts.

Importante: o orçamento de campanhas é **planejado**, não gasto real. Não há base suficiente para calcular ROAS, CAC ou margem.

Dados e marcas são fictícios. Este repositório não inclui informações de clientes ou empregadores.
