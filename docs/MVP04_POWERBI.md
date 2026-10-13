# MVP-04 — Power BI | Ecommerce Analytics

**Status 12/10/2026:** projeto PBIP/TMSL/PBIR versionado no Git; dataset ampliado no [MVP-04A](MVP04A_DATASET.md). A antiga auditoria de 36 pedidos é histórica; os novos CSVs possuem 4.200 pedidos, 8.400 itens, 420 clientes e 365 dias. Testes dbt e equivalência com o exportador ainda pendentes. **Ainda não foi aberto, carregado ou salvo pelo Power BI Desktop**. A paridade do CSV contra execução local dbt e o teste real no Desktop são gates pendentes.

## Regra operacional: Git antes do Desktop

Reproduzir o processo do [Fleet Analytics](https://github.com/Peruzini/bi-analytics-portfolio/tree/main/powerbi/fleet):
1. Construir e revisar fontes, dados sintéticos, modelo semântico, DAX, PBIR, tema e documentação **no Git**.
2. Validar sintaxe e integridade das referências via `python -m unittest discover -s tests -v`.
3. Executar `python scripts/local_ci.py --full` (dbt DuckDB + comparação byte a byte dos 7 CSVs **no mesmo banco temporário**). Em caso de drift, investigar a primeira diferença antes de atualizar os CSVs. O comando `python scripts/export_powerbi.py --check` continua disponível, porém refaz dbt.
4. Somente após ambos os gates PASS, clonar/atualizar o projeto completo no PC, abrir `powerbi/EcommerceAnalytics.pbip`, atualizar dados, conferir relacionamentos/DAX, avaliar visualmente as 4 páginas e salvar no Desktop. Esse round-trip não está comprovado.
5. Versionar eventuais correções do round-trip; não publicar capturas ou resultados fictícios.

Nenhuma etapa rotineira precisa de Snowflake ou runner GitHub Actions.

## Entrega no Git

| Artefato | Caminho | Conteúdo |
| --- | --- | --- |
| PBIP | `powerbi/EcommerceAnalytics.pbip` | Atalho do projeto editável |
| Report PBIR | `powerbi/EcommerceAnalytics.Report/definition/` | 4 páginas, 50 visuais, tema e layout |
| Modelo tabular | `powerbi/EcommerceAnalytics.SemanticModel/model.bim` | 9 tabelas, 5 relacionamentos, 39 medidas DAX |
| Dados | `powerbi/data/` | 7 CSV sintéticos de marts/dimensões |
| Exportação | `scripts/export_powerbi.py` | Gerador/checker dos 7 CSV diretamente dos dbt marts via DuckDB |
| Validação | `tests/test_powerbi_data.py` + `tests/test_powerbi_structure.py` | Reconciliação por grão, esquema, paths, refs |
| Catálogo | `powerbi/dax/CATALOGO.md` | Medidas com DAX e formatação |

### Linhagem
`seeds/ (6 fontes) → dbt seed/staging/intermediate/marts no DuckDB → 7 CSV → Power Query M (GitHub raw/main) → modelo Tabular Power BI → visuais.`

As sete saídas do cenário MVP-04A foram produzidas de forma determinística a partir das seeds e regras SQL documentadas, sem execução dbt nesta atualização. **Ainda precisam ser comparadas byte a byte com o exportador dbt em execução real no PC**. Uma divergência requer correção, não ajuste oculto do teste.

### Modelo relacional principal

`DimData[Data]` → `FatoPedidos[order_date]` (1:N)

`DimClientes[customer_id]` → `FatoPedidos[customer_id]` (1:N)

`FatoPedidos[order_id]` → `FatoItens[order_id]` (1:N)

`DimProdutos[product_id]` → `FatoItens[product_id]` (1:N)

`DimClientes[customer_id]` → `ResumoClientes[customer_id]` (1:1 na fixture)

**ResumoCanais e ResumoDiario são agregados independentes**. Não conectá-los também às tabelas-fato: isso poderia introduzir caminhos ambíguos/duplicidade de receita. **MVP-04B:** `fct_orders` passa a conter `channel` por pedido, alimentando `FatoPedidos[channel]`. A página Canais e Pedidos agora usa o fato detalhado e filtros de data; `ResumoCanais` permanece apenas como histórico de referência (budget planejado). Não somar os dois grãos.

**MVP-04C:** as quatro páginas receberam uma identidade visual única, leitura guiada, notas estáticas explicitamente rotuladas e rodapé de dados sintéticos. A página de produtos mostra categorias no gráfico e SKUs no detalhe. Ver [MVP-04C — UX e storytelling](MVP04C_UX_STORYTELLING.md).

### Dashboard: quatro páginas

| Página | Questão | Visuais |
| --- | --- | --- |
| Visão Executiva | Receita reconhecida, volume e ticket | Cartões, filtro período/região, receita mensal vs mês anterior, tabela região |
| Receita e Pedidos | Efeito dos status e reembolsos | Cartões, filtros status/período, receita diária vs média móvel 7d, tabela **mensal** de MoM, receita/dia e taxas |
| Clientes e Produtos | Quem e o quê geram receita | Recompra no período (induzida pelo cenário), receita de itens por produto, participação e unidades |
| Canais e Pedidos | Como receita e status variam por canal/mês? | Cartões, slicers de canal/mês, série mensal, barras e tabela analítica de fatos |

### Definições que não podem ser alteradas silenciosamente
- Receita reconhecida = apenas pedidos `completed`.
- `refunded` tem receita reconhecida zero e reembolso segregado.
- Receita de itens usa somente `recognized_item_revenue`, consistente com FatoPedidos.
- Ticket médio = receita reconhecida / pedidos concluídos.
- Budget = `planned_budget_amount`, não desembolso. Sem ROAS/CAC.
- LTV = `lifetime_recognized_revenue` observada; não predição. Custos/margem não disponíveis.
- Não somar receita de fato de pedidos + fato de itens + marts, pois representaria a mesma receita em diferentes grãos.

**Interpretação:** as diferenças entre canais, recompra elevada e sazonalidade são programadas no gerador, não descobertas causais de comércio real. Veja [análise e indicadores MVP-04B](MVP04B_ANALISE.md).

### Importação final
O PBIP importa os CSVs por Power Query M via `Web.Contents` em URL público no GitHub. Isso requer internet e autenticação **Anônima** no primeiro refresh, mas nenhum secret ou conta Snowflake. Manter pastas `.Report` e `.SemanticModel` ao lado de `.pbip`; o Desktop não abre corretamente um `.pbip` isolado.

### Gates para encerramento
- [x] Dataset 04A ampliado e reconciliado na geração: 4.200 pedidos, 8.400 itens, 365 dias.
- [x] Código de exportação DuckDB e testes no Git.
- [x] PBIP, modelo, 39 medidas, 4 páginas/50 visuais em formato editável; canal por pedido adicionado no MVP-04B.
- [ ] `python scripts/generate_data.py --check` e `python -m unittest discover -s tests -v` após atualização do clone.
- [ ] `python scripts/local_ci.py --full` no dataset atual, incluindo a etapa `duckdb-powerbi-parity` e `LOCAL_FULL_PASS`.
- [ ] Round-trip abrir → atualizar → conferir → salvar no Power BI Desktop.
- [ ] Evidência final de screenshots e documentação do case.

- [ ] Auditar geometria/layout com `tests/test_mvp04c_ux.py` e inspecionar o resultado renderizado no Desktop.

## Homologação do MVP-04D

[Checklist e evidências de validação](MVP04D_RELEASE.md) · [Estudo de caso profissional](PORTFOLIO_CASE_STUDY.md).

## Referências
- Fleet: https://github.com/Peruzini/bi-analytics-portfolio/tree/main/powerbi/fleet
- PBIP: https://learn.microsoft.com/power-bi/developer/projects/projects-overview
- Política de custos: [LOCAL_EXECUTION_POLICY.md](LOCAL_EXECUTION_POLICY.md)
