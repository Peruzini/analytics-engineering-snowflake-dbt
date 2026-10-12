# Execução local — Windows e Git Bash

Usar Python 3.11 e Git Bash. Nenhuma chave Snowflake é necessária para testes offline.

## Instalação (uma vez)
```bash
git clone https://github.com/Peruzini/analytics-engineering-snowflake-dbt.git
cd analytics-engineering-snowflake-dbt
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Se existir Python 3.11 sob o comando `py -3.11`, pode usar `py -3.11 -m venv .venv` no lugar de `python -m venv .venv`.

## Validação sem custos de nuvem
```bash
python scripts/local_ci.py --quick
python scripts/local_ci.py --full
```

O script full usa Snowflake apenas para parse com placeholders e executa todos os modelos, incremental, snapshot e testes sobre DuckDB temporário. Saída: `.local-evidence/latest.json`. Confirmar `LOCAL_FULL_PASS` antes de prosseguir; se falhar, não declarar sucesso.

## Publicação de evidência
Com modificações de código já commitadas e worktree limpa:
```bash
python scripts/local_ci.py --full --publish
git status --short
```

Revisar o JSON em `docs/evidence/local-validation/` e commitar/push manualmente. Nenhuma Action ou Artifact envolvida.

## Runner self-hosted (opcional, não configurado automaticamente)
O botão Actions depende de cadastrar novo runner Windows para ESTE repositório em Settings > Actions > Runners, com label adicional `ae-local`. O runner do VTT não atende aqui automaticamente. Nunca permitir execução de PRs externos no runner de um repositório público.

## Integração Snowflake
Somente depois de autorização: workflow `Snowflake Integration (Manual Self-Hosted)`, confirmação `yes`, runner preparado e Secrets já cadastrados. Usa créditos do Snowflake apesar de rodar no PC. Ver [operação Snowflake](mvp03-operations.md).
