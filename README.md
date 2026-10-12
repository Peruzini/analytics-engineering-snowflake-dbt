# Analytics Engineering — Snowflake + dbt

[![CI](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml/badge.svg)](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml)

**Portfólio técnico de Analytics Engineering:** dados sintéticos de e-commerce, transformações SQL com dbt, contratos, testes de qualidade e CI. O projeto foi desenhado para execução no Snowflake, com verificações offline reproduzíveis.

> **Status: MVP-02 — staging, intermediate e marts publicados.** A CI offline valida código, modelo e dados sintéticos; o projeto ainda não foi executado contra um Snowflake real. Incremental, snapshots e dashboard ficam para etapas seguintes.

## Problema de negócio

Uma operação de e-commerce recebe dados de clientes, produtos, campanhas, pedidos, itens e pagamentos. Antes de calcular receita, margem, ticket médio, recompra ou aquisição, é necessário padronizar chaves, estados, datas e valores e garantir integridade referencial.

O MVP-01 entregou a camada staging. O **MVP-02 acrescenta 2 modelos intermediate e 7 modelos de analytics**, incluindo dimensões, fatos e marts, com receita reconhecida apenas em pedidos concluídos.

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
MVP-03: SQL reconciliation, incremental and snapshots
MVP-04: Power BI on analytics marts
```

O padrão `target_schema_<custom_schema>` é o comportamento padrão de schema customizado do dbt. Não há necessidade de credenciais para gerar dados sintéticos nem para validar sintaxe localmente.

## Evidências dos MVPs 01–02

- **6 fontes CSV sintéticas** e gerador determinístico com Python (stdlib).
- **6 modelos staging, 2 intermediate e 7 modelos analíticos**, usando `source()`, `ref()`, contratos, grãos explícitos e status preservados.
- **Testes dbt** para unicidade, obrigatoriedade, integridade referencial e domínios.
- **Testes Python** para integridade dos CSVs, reprodutibilidade e reconciliação matemática offline de receita entre dia, cliente e canal.
- **CI** com validação Python, YAML e `dbt parse`, sem acesso a dados privados nem conexão real ao Snowflake.
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

Esses comandos **não foram executados no Snowflake como parte deste MVP**. `profiles.yml` é ignorado no Git e não deve ser commitado.

## Estrutura

- `seeds/` — dados sintéticos controlados;
- `scripts/` — geração determinística;
- `models/staging/` — 6 modelos staging;
- `models/intermediate/` — agregações financeiras por pedido e regra de receita;
- `models/marts/` — 2 dimensões, 2 fatos e 3 marts analíticos;
- `models/staging/_sources.yml` — definições das seis fontes;
- `models/staging/_models.yml` — testes e documentação;
- `tests/` — testes Python de qualidade e reprodução;
- `docs/` — arquitetura, contratos, linhagem e decisões;
- `.github/workflows/ci.yml` — validação offline.

## Próximos marcos

1. **MVP-03:** reconciliação SQL no warehouse, snapshots, incremental e execução Snowflake.
2. **MVP-04:** Power BI consumindo os marts.

Importante: o orçamento de campanhas é **planejado**, não gasto real. Não há base suficiente para calcular ROAS, CAC ou margem.

Dados e marcas são fictícios. Este repositório não inclui informações de clientes ou empregadores.
