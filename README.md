# Analytics Engineering — Snowflake + dbt

[![CI](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml/badge.svg)](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/workflows/ci.yml)

**Portfólio técnico de Analytics Engineering:** dados sintéticos de e-commerce, transformações SQL com dbt, contratos, testes de qualidade e CI. O projeto foi desenhado para execução no Snowflake, com verificações offline reproduzíveis.

> **Status: MVP-01 — infraestrutura, dados sintéticos e staging.** A existência de modelos, testes e CI não implica que um pipeline Snowflake já tenha sido executado. Camadas intermediate, marts, incremental, snapshots e dashboard são etapas posteriores.

## Problema de negócio

Uma operação de e-commerce recebe dados de clientes, produtos, campanhas, pedidos, itens e pagamentos. Antes de calcular receita, margem, ticket médio, recompra ou aquisição, é necessário padronizar chaves, estados, datas e valores e garantir integridade referencial.

O MVP-01 entrega uma camada `staging` validável para as seis entidades.

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
dbt tests + documentation
             |
             v
MVP-02: intermediate / marts (not yet implemented)
MVP-03: reconciliation / incremental / snapshots / BI
```

O padrão `target_schema_<custom_schema>` é o comportamento padrão de schema customizado do dbt. Não há necessidade de credenciais para gerar dados sintéticos nem para validar sintaxe localmente.

## Evidências do MVP-01

- **6 fontes CSV sintéticas** e gerador determinístico com Python (stdlib).
- **6 modelos staging SQL/dbt** com `source()`, aliases, tipos e contratos de colunas.
- **Testes dbt** para unicidade, obrigatoriedade, integridade referencial e domínios.
- **Testes Python** para integridade dos CSVs e reprodutibilidade.
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
dbt run --select staging --profiles-dir .
dbt test --select staging --profiles-dir .
dbt docs generate --profiles-dir .
```

Esses comandos **não foram executados no Snowflake como parte deste MVP**. `profiles.yml` é ignorado no Git e não deve ser commitado.

## Estrutura

- `seeds/` — dados sintéticos controlados;
- `scripts/` — geração determinística;
- `models/staging/` — 6 modelos de staging;
- `models/staging/_sources.yml` — definições das seis fontes;
- `models/staging/_models.yml` — testes e documentação;
- `tests/` — testes Python de qualidade e reprodução;
- `docs/` — arquitetura, contratos e decisões;
- `.github/workflows/ci.yml` — validação offline.

## Próximos marcos

1. **MVP-02:** intermediate, dimensões, fatos e marts analíticos.
2. **MVP-03:** testes de reconciliação, snapshots, incremental e execução Snowflake.
3. **MVP-04:** Power BI consumindo a camada analítica.

Dados e marcas são fictícios. Este repositório não inclui informações de clientes ou empregadores.
