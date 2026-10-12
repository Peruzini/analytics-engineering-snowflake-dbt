# MVP-03 — Execução e validação no Snowflake

## Status

CI offline verde: a instalação e o parse do projeto são verificados sem conexão ao Snowflake. O workflow de integração **não foi executado** com credenciais reais.

## Autenticação sem senha do Google

O GitHub Actions usa um **usuário Snowflake de serviço** (`TYPE = SERVICE`) com chave privada criptografada PKCS8. Seu login Google/SSO permanece exclusivo para uso pessoal. Não use senha do Google em Secrets.

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

Não cadastrar `DBT_SNOWFLAKE_PASSWORD`. O runner grava a chave privada em arquivo temporário com permissões `0600` e o dbt usa `private_key_path` + `private_key_passphrase`.

### Criar a chave no Windows (OpenSSL)

No Git Bash ou PowerShell com OpenSSL instalado, na pasta **fora do repositório**:

```bash
openssl genrsa 3072 | openssl pkcs8 -topk8 -v2 aes-256-cbc -out snowflake_ci_key.p8
openssl pkey -in snowflake_ci_key.p8 -pubout -out snowflake_ci_key.pub
```

A ferramenta solicitará uma passphrase para proteger a chave. Guarde-a em gerenciador de senhas.

No Snowflake, `RSA_PUBLIC_KEY` recebe apenas o texto base64 da chave pública, excluindo `-----BEGIN PUBLIC KEY-----`, `-----END PUBLIC KEY-----` e quebras de linha.

**Nunca** commitar o arquivo `.p8`, colar chave privada ou passphrase no chat, nem publicar logs com seus conteúdos.

## Execução

1. Concluir usuário de serviço, role e os **oito** Secrets.
2. Abrir `Actions > Snowflake Integration (Manual) > Run workflow`.
3. Selecionar `confirm=yes`; isso pode consumir créditos Snowflake.
4. Verificar `dbt debug`, `dbt seed`, `dbt run`, `dbt snapshot` e `dbt test`.
5. Guardar link/commit da run e evidências. Uma CI offline verde não substitui essa integração.

## Validações funcionais pendentes

- Provar idempotência do MERGE e atualização de pedido alterado.
- Provar histórico SCD2 após mudança simulada de email/região.
- Confirmar todas as cinco reconciliações SQL e os testes genéricos.
- Validar o isolamento de schema e registrar consumo aproximado.

Consulte a documentação oficial: https://docs.snowflake.com/en/user-guide/key-pair-auth
