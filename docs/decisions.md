# Decisões Técnicas

## ADR-001 — Dados sintéticos versionados

**Decisão:** utilizar fixtures determinísticas geradas apenas com a biblioteca padrão do Python.

**Motivo:** recrutadores e colaboradores podem reproduzir os mesmos dados sem acesso a empresas, APIs ou credenciais.

## ADR-002 — dbt + Snowflake em camadas

**Decisão:** carregar seeds em `<target.schema>_raw` e modelos em `<target.schema>_staging` pelo comportamento padrão de schema do dbt.

**Motivo:** manter isolamento de ambientes e evitar macros de override prematuras.

## ADR-003 — CI offline primeiro

**Decisão:** GitHub Actions verifica CSVs, testes Python, sintaxe YAML e `dbt parse` com placeholders.

**Motivo:** CI não deve exigir conta Snowflake nem consumir créditos para verificações sintáticas. Testes de integração serão adicionados separadamente.

## ADR-004 — Preservar dados inválidos para observabilidade

**Decisão:** no MVP-01, staging não remove registros por status nem faz deduplicação oculta.

**Motivo:** a camada de transformação deve ser auditável; dados fora de contrato devem falhar em testes, não desaparecer silenciosamente.

## Backlog

- MVP-02: intermediate e dimensional marts;
- MVP-03: conciliação, incremental, snapshot e Snowflake integrado;
- MVP-04: dashboard Power BI.
