# E-commerce Analytics — Commercial Decision Center

V3-05D3C: quatro páginas (receita, pedidos, clientes/mix e canais) com 14 gráficos SVG. Design system reaproveitado do Fleet (commit 3a6b471). Quatro CSVs versionados, sem duplicação; hashes iguais ao manifesto V3-05C1. Os três marts adicionais não são somados aos fatos.

## Executar na raiz do repositório
```bash
node labs/ecommerce-analytics/tests/dashboard.mjs
python -m http.server 8081 --bind 127.0.0.1
```
Abrir http://127.0.0.1:8081/labs/ecommerce-analytics/ (servidor na raiz; não usar file://). Sem npm, CDN ou API. Filtros compartilhados de data, região e status. Canal nas páginas de pedidos; categoria na página de itens; filtro não aplicável é ocultado e desabilitado. Seleções preservadas ao retornar à página. Seleção por gráficos, alternativas tabulares, exportação CSV dos resumos e PNG 2× por gráfico implementadas. Valores monetários do motor e CSV em centavos; BRL na interface.

## Contratos
Recompra por dois pedidos distintos; compradores não aditivos. Participação canal remove somente filtro de canal. Média móvel 7d cruza início da seleção, acumulado reinicia na seleção. Receita por dia usa dias de calendário selecionados. Pareto top 10 acumula sobre todos produtos filtrados. Não há ROAS, CAC ou funil de status. Dados sintéticos. Sem ECharts por opção de SVG nativo como Fleet.

## Evidência
56/56 verificações executadas em JS sobre os módulos recuperados do GitHub e CSVs completos, incluindo 28 combinações de página e filtro na geração HTML/SVG. Veja evidence/dashboard.json. Sintaxe do app conferida com substituição de import.meta.url para compilação isolada; não execução DOM. Wrapper Node e navegador não executados, Desktop Commander offline. Homologação de interação, PNG, responsividade, legibilidade e acessibilidade no D3D. Sem alteração PBIP, CSV, dbt, merge ou deploy.
