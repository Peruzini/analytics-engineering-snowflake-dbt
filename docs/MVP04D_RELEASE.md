# MVP-04D — Validação, homologação e evidências

**Status atual: PRÉ-RELEASE, não homologado.** O conteúdo está no Git, mas os testes da nova fixture e o round-trip no Desktop ainda não foram executados. Não reutilizar o PASS de **88 testes Snowflake** do baseline anterior como evidência da versão atual.

## Gates

| Gate | Critério | Estado |
| --- | --- | --- |
| G0 Git | Arquivos do pipeline, CSVs, 4 páginas, 50 visuais, 39 medidas presentes | Versionado; auditoria estática de fases anteriores |
| G1 Python | Seeds determinísticas, testes unitários, YAML e estrutura PBIR | Pendente de execução atual |
| G2 dbt DuckDB | seed, run, incremental, snapshot, test e parse Snowflake offline | Pendente de execução atual |
| G3 CSV × dbt | 7 CSVs iguais às saídas reais dos marts DuckDB | Pendente de execução atual |
| G4 Desktop | Abrir PBIP, refresh, verificar DAX, filtros, relações e renderização | Pendente |
| G5 Portfólio | Capturas reais das quatro páginas e evidência referenciada por commit | Pendente |

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
