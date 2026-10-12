# MVP-03 — Execução e validação Snowflake

## O que foi publicado

1. **fct_orders incremental:** estratégia MERGE com chave `order_id`. Para não perder atualizações antigas, compara todos os campos de interesse e envia apenas pedidos novos ou modificados. Sem `updated_at` confiável nos dados sintéticos, ainda lê toda a pequena origem. Não trata exclusões físicas de pedidos.
2. **snap_customers:** snapshot dbt 1.9+ com `check` em `email` e `region`, grão `customer_id`. Executar novamente depois de modificar uma dessas colunas produz nova versão histórica.
3. **5 testes SQL singulares:** receita por status/pagamento, conciliação diária, pedidos x itens, clientes x LTV e canais. dbt considera sucesso quando cada teste retorna zero linhas.
4. **Workflow manual:** `.github/workflows/snowflake-integration.yml` — não roda em push/PR e exige escolha explícita `yes`.

## Requisitos para integração

Criar uma conta Snowflake própria e um usuário/role com permissões mínimas para criar e atualizar objetos somente em database/schema dedicados ao portfólio.

Em GitHub Settings > Secrets and variables > Actions > Repository secrets, definir:

| Secret | Exemplo de escopo |
| --- | --- |
| DBT_SNOWFLAKE_ACCOUNT | Identificador da conta Snowflake |
| DBT_SNOWFLAKE_USER | Usuário específico do portfólio |
| DBT_SNOWFLAKE_PASSWORD | Senha do usuário (não commitar) |
| DBT_SNOWFLAKE_ROLE | Role limitada |
| DBT_SNOWFLAKE_DATABASE | Database sandbox |
| DBT_SNOWFLAKE_WAREHOUSE | Warehouse pequeno, com auto-suspend |
| DBT_SNOWFLAKE_SCHEMA | Schema dedicado; não usar PUBLIC |

O dbt cria, por padrão, os schemas derivados `<SCHEMA>_raw`, `<SCHEMA>_staging`, `<SCHEMA>_intermediate`, `<SCHEMA>_analytics` e `<SCHEMA>_snapshots`. O papel precisa ter permissões para criá-los; não usar role de produção.

## Como executar

1. Configurar secrets e acesso Snowflake; não passar credenciais por chat.
2. Abrir Actions > **Snowflake Integration (Manual)** > Run workflow.
3. Selecionar `confirm=yes`.
4. Inspecionar `dbt debug`, `dbt seed`, `dbt run`, `dbt snapshot` e `dbt test`.
5. Registrar SHA, run URL, status, quantidades e testes. Se falhar, **não** divulgar integração validada.

**Custos:** executar manualmente pode consumir créditos do Snowflake e minutos do GitHub Actions. Não há agendamento.

## Verificação do incremental

Após uma execução verde inicial, fazer nova run sem mudar seeds: nenhum registro deve mudar semanticamente, e não deve haver multiplicação de `order_id`. Um teste mais forte requer atualizar o status de um pedido em ambiente de demonstração, reexecutar seed e dbt run, e comprovar o merge; restaurar a fixture original e reexecutar depois. Não alterar dados ou disparar novas runs automaticamente.

O `merge` compara dados existentes com a origem e ignora linhas idênticas; ele não propaga exclusões físicas. `dbt --full-refresh` é caminho manual para reconstrução quando necessário.

## Verificação do snapshot

A primeira run captura clientes correntes. Uma mudança posterior em `email` ou `region` seguida de `dbt snapshot` cria versão histórica, com `dbt_valid_from`/`dbt_valid_to`. O projeto não usa `created_at` como timestamp de modificação.

## Distinção importante

A CI normal executa somente testes Python, validação YAML e `dbt parse`. Isso confirma configuração e dependências, **não** execução SQL real no Snowflake. O workflow manual somente pode ser considerado comprovado após uma run real verde.
