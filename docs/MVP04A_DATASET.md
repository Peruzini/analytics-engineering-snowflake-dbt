# MVP-04A — Dataset comercial de 12 meses

## Objetivo
Substituir a antiga base sintética pequena por um **cenário analítico longitudinal**, útil para sazonalidade, recompra, análise de produtos e canais. O caso **continua sendo simulação** e não representa operação ou receitas reais.

## Resultado versionado
- Período: **2025-10-01 a 2026-09-30**, 365 dias com pedidos.
- 420 clientes sintéticos, sete UFs; 40 produtos, seis categorias; 12 campanhas planejadas em quatro canais.
- 4.200 pedidos, 8.400 itens, 3.785 pagamentos.
- Status: 3.588 completed, 254 cancelled, 197 refunded, 161 pending.
- Recompra: **420 clientes com mais de um pedido** (fenômeno **deliberadamente induzido** pelo cenário, não estimativa real).
- Receita reconhecida **R$ 2.699.981,55** — total fictício reconciliado por grão no gerador.
- Perfil sazonal sintético: outubro/2025 357 pedidos, novembro 525, dezembro 450, janeiro/2026 297, fevereiro 240, março 314, abril 313, maio 330, junho 303, julho 345, agosto 392, setembro 334.
- Ajustes por dia útil/fim de semana e incremento nas datas finais de novembro. Não usar estes números para inferir comportamento de consumidores reais.

## Fonte única e determinismo
- Cenário parametrizado em `scripts/market_config.json`.
- Gerador canônico das **seis seeds** em `scripts/generate_data.py` (Python stdlib, operações financeiras em centavos inteiros, sem aleatoriedade).
- Outputs em `seeds/raw_*.csv`, com **mesmas colunas, chaves e status** do MVP-03.
- Os sete CSVs em `powerbi/data/*.csv` foram construídos aplicando as mesmas regras SQL publicadas e conciliados na geração. **Não foram exportados pela execução dbt** nesta etapa; a verificação canônica `python scripts/export_powerbi.py --check` é gate obrigatório.
- No fechamento do **MVP-04A**, o modelo mantinha 9 tabelas, 5 relacionamentos, 27 medidas e 4 páginas; o **MVP-04B** adicionou 12 medidas (total 39), canal no fato e dois visuais. `DimData` abrange os 365 dias.

## Regras de negócio
- **Receita reconhecida:** apenas pedidos `completed`; `refunded`, `cancelled` e `pending` geram receita reconhecida zero (regra didática, não norma contábil geral).
- **Refunds:** valor separado de `recognized_revenue`, não abater duas vezes.
- **Itens:** 1–3 por pedido, sem duplicação por pagamentos. Preços transacionais vêm dos itens, `list_price` é apenas catálogo.
- **Desconto:** 0–15% por item mais promoção limitada em novembro; preço líquido e pagamento são conciliados em centavos.
- **Pagamentos:** exatamente um pagamento para cada pedido `completed` ou `refunded`, zero para demais, com métodos Pix/cartão.
- **Canais:** `organic`, `paid_search`, `social`, `email`, mais `unattributed`. O budget é **planejado**; sem ROAS, CAC ou margem.
- **Campanhas e status:** diferenças determinísticas nos percentuais por canal permitem comparação exploratória, mas **não** causam qualquer efeito real de marketing.
- **Cliente recorrente:** há pedidos repetidos; não confundir participação no período com taxa de retenção/coortes de clientes reais.

## Ruptura de fixture em relação ao MVP-03
Esta mudança é um **reset controlado de dados sintéticos**, não atualização incremental dos 36 pedidos antigos:
- IDs antigos `O001` foram substituídos por `O000001`. O incremental `fct_orders` não remove linhas excluídas da origem; **não executar MERGE em tabela antiga esperando substituição completa**.
- Se uma integração Snowflake excepcional for autorizada futuramente, planejar o `dbt seed --full-refresh` e `dbt run --full-refresh` (ou recriação isolada do schema), com validação de snapshot e destino antes de qualquer run. **Nenhum refresh Snowflake foi executado aqui**.
- Evidências de 12/10/2026, incluindo 88 dbt tests green, pertencem **ao dataset anterior**; não transferir o PASS para o novo cenário.
- Auditoria prévia de R$ 14.250,40 permanece como [histórico](AUDITORIA_MVP04_2026-10-12.md), não representa os números atuais.

Atualização posterior: [MVP-04B — Análise e indicadores](MVP04B_ANALISE.md).

## Qualidade / gates
1. **Git:** 13 CSVs versionados e totais reconciliados na geração.
2. **Python:** `python scripts/generate_data.py --check` e `python -m unittest discover -s tests -v` — **ainda exigem execução independente** após esta revisão.
3. **dbt local:** `python scripts/local_ci.py --full` — precisa repetir após reset; aprovação do dataset anterior não se transfere.
4. **Exportação:** `python scripts/export_powerbi.py --check` — conferir 7 CSVs contra saída canônica de dbt DuckDB, inclusive arredondamentos.
5. **Power BI Desktop:** abrir o PBIP e realizar refresh/round-trip somente depois de aprovar os gates anteriores.

Sem GitHub Actions, Snowflake ou dependência de Power BI Desktop para gerar os dados.
