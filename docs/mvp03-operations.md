# MVP-03 — Execução e validação no Snowflake

## Status

**Integração Snowflake real PASS em 12/10/2026 no commit `1007ddaa`**, antes da transição: [Run #38315794938](https://github.com/Peruzini/analytics-engineering-snowflake-dbt/actions/runs/38315794938) executou `dbt debug`, 6 seeds, 15 modelos, 1 snapshot e 88 testes sem falhas. Veja [evidência de baseline](SNOWFLAKE_INTEGRATION_BASELINE_2026-10-12.md). A transição local posterior ainda aguarda `LOCAL_FULL_PASS` no Windows; o SQL pós-migração não foi reexecutado no Snowflake.

## Autenticação sem senha do Google

A integração manual self-hosted usa um **usuário Snowflake de serviço** (`TYPE = SERVICE`) com chave privada criptografada PKCS8. Seu login Google/SSO permanece exclusivo para uso pessoal. Não use senha do Google em Secrets.

### Preparar usuário de serviço

1. Gerar em máquina local uma chave RSA privada **criptografada PKCS8** e uma chave pública. Guardar a chave privada em local seguro, fora do repositório.
2. No Snowflake, usando uma role que possa criar usuários, criar `AE_PORTFOLIO_CI` com `TYPE = SERVICE` e `RSA_PUBLIC_KEY` igual ao conteúdo base64 da chave pública (sem cabeçalho/rodapé).
3. Com `SECURITYADMIN`, executar `GRANT ROLE AE_PORTFOLIO_ROLE TO USER AE_PORTFOLIO_CI;`.
4. Assegurar que `AE_PORTFOLIO_ROLE` possua permissões de USAGE e CREATE SCHEMA na database e USAGE no warehouse de testes.

O usuário de serviço precisa permanecer limitado a ambientes de teste. Não fornecer papéis administrativos ao workflow.

### Secrets obrigatórios do GitHub

Configurar em `Settings > Secrets and variables > Actions` no repositório:

| Secret | Conteúdo |
| --- | --- |
| `DBT_SNOWFLAKE_ACCOUNT` | Identificador organização-conta |
| `DBT_SNOWFLAKE_USER` | `AE_PORTFOLIO_CI` (usuário de serviço) |
| `DBT_SNOWFLAKE_PRIVATE_KEY` | Texto inteiro do arquivo privado criptografado `.p8`, incluindo BEGIN/END |
| `DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE` | Frase secreta usada para criptografar a chave |
| `DBT_SNOWFLAKE_ROLE` | `AE_PORTFOLIO_ROLE` |
| `DBT_SNOWFLAKE_DATABASE` | `AE_PORTFOLIO_DB` |
| `DBT_SNOWFLAKE_WAREHOUSE` | `AE_PORTFOLIO_WH` |
| `DBT_SNOWFLAKE_SCHEMA` | `AE_PORTFOLIO` |

Não cadastrar `DBT_SNOWFLAKE_PASSWORD`. O workflow Linux anterior usava permissões `0600`. O novo runner Windows grava a chave em arquivo temporário sob o usuário do runner e remove ao final; recomenda-se execução com conta Windows dedicada e ACL restrita. O dbt usa `private_key_path` + `private_key_passphrase`.

### Criar a chave no Windows (OpenSSL)

No Git Bash ou PowerShell com OpenSSL instalado, na pasta **fora do repositório**:

```bash
openssl genrsa 3072 | openssl pkcs8 -topk8 -v2 aes-256-cbc -out snowflake_ci_key.p8
openssl pkey -in snowflake_ci_key.p8 -pubout -out snowflake_ci_key.pub
```

A ferramenta solicitará uma passphrase para proteger a chave. Guarde-a em gerenciador de senhas.

No Snowflake, `RSA_PUBLIC_KEY` recebe apenas o texto base64 da chave pública, excluindo `-----BEGIN PUBLIC KEY-----`, `-----END PUBLIC KEY-----` e quebras de linha.

**Nunca** commitar o arquivo `.p8`, colar chave privada ou passphrase no chat, nem publicar logs com seus conteúdos.

## Execução local antes da integração

Executar `python scripts/local_ci.py --full` no PC; valida modelos com DuckDB, não consulta Snowflake. Ver [política local](LOCAL_EXECUTION_POLICY.md) e [setup Windows](LOCAL_SETUP_WINDOWS.md).

## Integração excepcional no Snowflake

Uma integração real já foi aprovada no baseline. Para **nova** validação após a migração, obter autorização explícita, registrar runner Windows `ae-local` neste repositório e abrir `Actions > Snowflake Integration (Manual Self-Hosted) > Run workflow` com `confirm=yes`. Mesmo com execução no PC, Snowflake consome créditos. Confirmar `dbt debug/seed/run/snapshot/test` e guardar evidência; não declarar PASS antes.

## Validações funcionais pendentes

- Provar idempotência do MERGE e atualização de pedido alterado.
- Provar histórico SCD2 após mudança simulada de email/região.
- As cinco reconciliações SQL e os testes genéricos **passaram no baseline**; reexecutar apenas se for necessário validar a versão pós-migração.
- Validar o isolamento de schema e registrar consumo aproximado.

Consulte a documentação oficial: https://docs.snowflake.com/en/user-guide/key-pair-auth
