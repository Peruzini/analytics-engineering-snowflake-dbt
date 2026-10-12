# Política de execução local — Analytics Engineering

**12/10/2026. Estado: código versionado; validação operacional no computador pendente.**

## Objetivo
Economizar a franquia GitHub Actions e créditos Snowflake reaproveitando do VTT o processamento self-hosted, a evidência pequena persistida em Git e disparos explícitos. Não replicar matrizes, retries, checkpoints ou infraestrutura pesada sem necessidade.

## Regras
1. **PC é o ambiente padrão.** Usar `python scripts/local_ci.py --quick` para dados/testes Python/YAML; `python scripts/local_ci.py --full` para parse Snowflake fictício e execução real de dbt sobre DuckDB.
2. **Zero Actions automáticas.** Workflows somente `workflow_dispatch`, `runs-on: [self-hosted, Windows, X64, ae-local]`; sem triggers `push`/`pull_request`, `ubuntu-latest` ou `upload-artifact`.
3. **Runner é opcional.** A execução direta via Git Bash funciona sem runner. O runner `vtt-heavy` de outro repositório não é automaticamente compartilhado. Um runner Windows deste repositório com label `ae-local` precisa ser registrado separadamente para habilitar o botão Actions.
4. **Sem Snowflake na rotina.** O teste DuckDB executa seed, marts, incremental, snapshot e testes dbt; `dbt parse` com perfil Snowflake fictício não faz consultas. Não equivale a uma integração Snowflake aprovada.
5. **Snowflake real apenas sob autorização.** Workflow separado requer `confirm=yes`, usuário de serviço, chave privada criptografada, role restrita. Mesmo em runner local, Snowflake consome créditos de warehouse.
6. **Evidências em Git, não Actions Artifact.** Cada execução registra `.local-evidence/latest.json` (ignorado no Git). Depois de `LOCAL_FULL_PASS` e com worktree limpa, `--full --publish` prepara `docs/evidence/local-validation/<sha>.json` para revisão e commit manual. Nunca escrever Secrets em JSON.
7. **Proteção de dados.** Ignorar `profiles.yml`, `*.p8`, `*.key` e bancos DuckDB. Não copiar chave ou senha para chat, logs, Git ou arquivos de evidência.
8. **Sem autorun ou polling.** Uma execução por autorização, auditar PASS/FAIL e hashes antes de avançar. Não rotular falha operacional como falha de regra de negócio.
9. **Estados distintos.** `LOCAL_QUICK_PASS` verifica fixtures/Python/YAML. `LOCAL_FULL_PASS` inclui SQL DuckDB e parse offline. `SNOWFLAKE_INTEGRATION_PASS` só após executar consultas reais e auditar os resultados.
10. **Runner público exige cuidado.** Não habilitar PRs de terceiros em runner self-hosted deste repositório público. Deixá-lo offline quando não estiver em uso.

## Referências VTT
- [CI Cost Policy](https://github.com/Peruzini/vtt-scene-compiler/blob/poc-2.4.3-dataset-v2-training-baseline/docs/CI_COST_POLICY.md)
- [Git Evidence Bridge](https://github.com/Peruzini/vtt-scene-compiler/blob/poc-2.4.3-dataset-v2-training-baseline/benchmark/vtt_native/scripts/poc23_g18_git_evidence_bridge.py)

O VTT usa GitHub Contents API e staging por run em paralelo. Aqui a evidência é gerada localmente e commitada manualmente: mais simples, sem GitHub API token adicional.

## Critério de conclusão
Mudanças de repositório implementadas ≠ validação do ambiente do usuário. A transição só é operacionalmente validada com `LOCAL_FULL_PASS` executado no Windows, evidência auditada e nenhuma Run hospedada disparada. Sem executar Snowflake até liberação específica.
