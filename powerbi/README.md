# Ecommerce Analytics — PBIP

**Abra só depois da validação do repositório no Git.**

Entrypoint: [EcommerceAnalytics.pbip](EcommerceAnalytics.pbip). O projeto precisa ser baixado com as pastas `EcommerceAnalytics.Report` e `EcommerceAnalytics.SemanticModel` preservadas.

## Fonte
`data/*.csv` é versionado; as consultas M do modelo leem os arquivos pelo `raw.githubusercontent.com/Peruzini/analytics-engineering-snowflake-dbt/main`. O projeto é público; configure autenticação Anônima no Power BI Desktop. Nenhuma chave Snowflake ou token GitHub é necessário.

## Antes de abrir
1. `python -m unittest discover -s tests -v`
2. `python scripts/export_powerbi.py --check`
3. Conferir os relatórios PASS; se houver drift, executar `python scripts/export_powerbi.py`, revisar e commitar novas saídas.

## Critérios do case
Receita = completed. Budget = planejado. Reembolso separado. Agregados `ResumoCanais` e `ResumoDiario` não são fatos detalhados; medidas não somam grãos diferentes. Quatro páginas, 43 visuais e 39 medidas DAX estão versionadas no Git. A página de canais usa `FatoPedidos[channel]` com filtros temporais; veja [MVP-04B](../docs/MVP04B_ANALISE.md).

Documentação completa: [MVP04_POWERBI.md](../docs/MVP04_POWERBI.md).
