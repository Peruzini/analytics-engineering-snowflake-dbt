# MVP-04D — Validação, homologação e evidências

**Status atual: PRÉ-RELEASE, G1–G3 aprovados no ambiente local; Desktop ainda não homologado.** Não reutilizar o PASS de **88 testes Snowflake** do baseline anterior como evidência da versão atual.

## Gates

| Gate | Critério | Estado |
| --- | --- | --- |
| G0 Git | Arquivos do pipeline, CSVs, 4 páginas, 52 visuais, 39 medidas presentes | Versionado; auditoria estática de fases anteriores |
| G1 Python | Seeds determinísticas, testes unitários, YAML e estrutura PBIR | PASS local (V3-05C3) |
| G2 dbt DuckDB | seed, run, incremental, snapshot, test e parse Snowflake offline | PASS local (V3-05C3) |
| G3 CSV × dbt | 7 CSVs iguais às saídas reais dos marts DuckDB | PASS local (V3-05C3) |
| G4 Desktop | Abrir PBIP, refresh, verificar DAX, filtros, relações e renderização | Pendente |
| G5 Portfólio | Capturas reais das quatro páginas e evidência referenciada por commit | Pendente |

[Auditoria estática G0 do GitHub](MVP04D_AUDITORIA_ESTATICA.md): 50 visuais e sete CSVs revisados sem problemas de referências, geometria ou conciliação; isso não substitui G1–G4.

## Fluxo local simplificado

Apenas quando o desenvolvimento no Git estiver pronto, no Git Bash, dentro do clone atualizado:

1. `git pull`
2. Ativar ambiente, se necessário: `source .venv/Scripts/activate`
3. `python scripts/local_ci.py --full`

O comando do item 3 integra G1, G2 e G3, **reutilizando o mesmo banco DuckDB**, sem gastar créditos Snowflake ou minutos do GitHub Actions. Para aprovar, o terminal precisa mostrar **POWERBI_EXPORT_MATCH** e **LOCAL_FULL_PASS**; em `.local-evidence/latest.json` a etapa `duckdb-powerbi-parity` deve estar PASS.

Se mostrar `POWERBI_EXPORT_DRIFT`, corrigir a primeira diferença relatada entre CSV comprometido e resultado do dbt. Não sobrescrever cegamente os dados. O comando `python scripts/export_powerbi.py --check` continua disponível separadamente, mas reexecuta dbt e não é necessário após o gate completo.

Após PASS, pode-se registrar evidência versionada com `python scripts/local_ci.py --full --publish` (segunda execução opcional); não subir chaves, credenciais, `profiles.yml` ou cache.

## Aceite do Power BI Desktop

Abrir `powerbi/EcommerceAnalytics.pbip` preservando as pastas `.Report` e `.SemanticModel`; usar acesso **Anônimo** aos CSVs públicos do GitHub, sem conectar Snowflake.

- **Abertura e refresh:** nenhum erro PBIP/PBIR/TMSL/Power Query; contagens 420/40/4200/8400/365/420/5 nas sete tabelas.
- **KPIs globais sem filtros:** receita R$ 2.699.981,55; 3.588 concluídos; taxa 85,43%; ticket R$ 752,50.
- **Quatro páginas:** sem cortes relevantes, sobreposição ou textos ilegíveis; notas fixas identificadas como referência à base integral.
- **Filtros:** testar mês (novembro/25, fevereiro/26), região, categoria e canal; a seleção de `unattributed` deve funcionar.
- **Grãos:** não duplicar receita na análise por produto e não somar resumos históricos desconectados.
- **Round-trip:** salvar como projeto no Desktop e revisar os arquivos alterados no Git, sem incluir `.pbi` e caches.

Se houver erro de abertura, registrar versão do Desktop e a mensagem de erro, corrigir no Git e repetir. JSON sintaticamente válido **não comprova** compatibilidade real.

## Evidências finais

Após aprovação G4, salvar capturas autênticas em `docs/screenshots/`:

- `01-visao-executiva.png`
- `02-receita-pedidos.png`
- `03-clientes-produtos.png`
- `04-canais-pedidos.png`

Conferir privacidade/legibilidade, indicar versão do Desktop, commit testado e resultados G1–G4. Atualizar [estudo de caso](PORTFOLIO_CASE_STUDY.md) com essas imagens somente após existirem.

O título **MVP-04D VALIDADO** só será aplicado quando todos os gates estiverem comprovados. O case permanece sintético e não demonstra impacto em operação real.


## Complemento V3-05C1

A fonte de sete CSVs está fixada no commit `b1c285cfd54564b2849f9e7a9c61f42c2e782b91`. Ver [contrato e evidências](V3-05C1_FILTER_CONTRACT.md). G1–G5 continuam pendentes até execução comprovada; a conciliação dos CSVs publicados não equivale à saída dbt atual.


## Complemento V3-05C2

O candidato possui 52 visuais, com os 50 IDs anteriores preservados; a auditoria histórica de G0 com 50 visuais refere-se ao baseline. A nova auditoria estática encontra-se em [V3-05C2](V3-05C2_LAYOUT.md). G1–G5 permanecem pendentes.


## Complemento V3-05C3 — Execução local comprovada

Candidato `6c247a7d2935ccbbd6b8ca4e631e00e30c616fbe`: Windows, Python 3.11.9, dbt-core 1.12.5, DuckDB adapter 1.10.1, Snowflake adapter 1.10.8 (parse fictício). 46 testes Python, 91 testes dbt, 6 seeds, 15 modelos, reexecução incremental e snapshot PASS. `POWERBI_EXPORT_MATCH` nos sete CSVs; `LOCAL_FULL_PASS`; 123 hashes SHA-256 conferidos no ambiente local. [Evidência gerada pelo script](evidence/local-validation/6c247a7d2935.json). Primeira falha: comparação textual sensível a caixa; segunda: empate decimal no ticket de C0169 (695,405), corrigido por serialização half-even com checagem da média SQL. Nenhuma fixture alterada. 19 ocorrências de aviso de depreciação dos argumentos de testes genéricos, sem falhas. G4–G5 pendentes; sem consultas Snowflake ou runner hospedado. Clone original com mudanças locais preservado por worktree isolada. Evidência publicada via conector GitHub porque o Git local não possui identidade de commit configurada.
