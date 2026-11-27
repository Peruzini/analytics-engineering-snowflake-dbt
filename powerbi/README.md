# Ecommerce Analytics — PBIP

**Abra só depois da validação do repositório no Git.**

Entrypoint: [EcommerceAnalytics.pbip](EcommerceAnalytics.pbip). O projeto precisa ser baixado com as pastas `EcommerceAnalytics.Report` e `EcommerceAnalytics.SemanticModel` preservadas.

## Fonte
`data/*.csv` é versionado; as consultas M do modelo leem os arquivos pelo `raw.githubusercontent.com/Peruzini/analytics-engineering-snowflake-dbt/b1c285cfd54564b2849f9e7a9c61f42c2e782b91`. O projeto é público; configure autenticação Anônima no Power BI Desktop. Nenhuma chave Snowflake ou token GitHub é necessário.

## Antes de abrir
1. `python scripts/local_ci.py --full` — sementes, testes Python/YAML, dbt DuckDB, incremental, snapshot e paridade dos 7 CSVs em um único banco.
2. Conferir `POWERBI_EXPORT_MATCH`, `LOCAL_FULL_PASS` e `duckdb-powerbi-parity` PASS em `.local-evidence/latest.json`; se houver drift, investigar antes de atualizar arquivos.
3. Abrir no Power BI Desktop e revisar conforme [checklist MVP-04D](../docs/MVP04D_RELEASE.md).

## Critérios do case
Receita = completed. Budget = planejado. Reembolso separado. Agregados `ResumoCanais` e `ResumoDiario` não são fatos detalhados; medidas não somam grãos diferentes. Quatro páginas, 52 visuais e 39 medidas DAX estão versionadas no Git. A página de canais usa `FatoPedidos[channel]` com filtros temporais; veja [MVP-04B](../docs/MVP04B_ANALISE.md).

UX e storytelling: [MVP04C_UX_STORYTELLING.md](../docs/MVP04C_UX_STORYTELLING.md).

Documentação completa: [MVP04_POWERBI.md](../docs/MVP04_POWERBI.md) · [Case de portfólio](../docs/PORTFOLIO_CASE_STUDY.md).


## V3-05C1

[Contrato de filtros, grãos e atualização do snapshot](../docs/V3-05C1_FILTER_CONTRACT.md). A revisão dos CSVs é fixa; para adotar novos dados, reexecutar paridade e atualizar explicitamente as sete URLs e o manifesto. A publicação de CSVs em main não muda a fonte deste PBIP.


## V3-05C2 — Identidade visual

[Layout, evidência e limitações](../docs/V3-05C2_LAYOUT.md). Quatro páginas, 52 visuais e duas análises gráficas por página; 39 medidas e snapshot do V3-05C1 preservados.
