# MVP-04C — UX e storytelling | Ecommerce Analytics

**Implementação versionada no Git.** O relatório PBIP/PBIR foi reorganizado seguindo o padrão Fleet, preservando os contratos do MVP-04B: **4 páginas, 9 tabelas, 5 relacionamentos, 39 medidas DAX, 7 CSVs e agora 50 visuais**. Não houve abertura no Power BI Desktop ou validação visual renderizada nesta etapa.

## Objetivo para recrutadores

Em 30–60 segundos, permitir que alguém identifique o problema de negócio, a evidência mais importante de cada página e o aprofundamento disponível. A estética reforça a leitura; a qualidade de dados e as regras de receita são a sustentação da narrativa.

## Sistema de design

- Tela fixa 1280 × 960, formato `FitToPage`; margens laterais de 24.
- Tema coerente: marinho escuro (`#12283F`) nos títulos, fundo claro (`#F4F7FB`), azul/teal nos resultados, superfícies brancas e bordas discretas.
- Hierarquia uniforme: **título numerado → pergunta → quatro cartões KPI → dois filtros → nota de leitura → gráfico(s) → tabela de detalhe → ressalva de dado sintético**.
- Fontes Segoe UI. Cores usadas como apoio visual, não como único sinal de significado.
- Gráficos ordenados e rótulos específicos; nenhum painel exige interpretação de dezenas de barras para encontrar o nível de categoria.
- Cabeçalhos `01 / 04` a `04 / 04` orientam navegação e deixam claro que as páginas formam uma história.
- Cada observação com números de referência é **estática** e identificada como tal; o usuário pode alterar os KPIs e gráficos com filtros sem confundir a anotação como cálculo dinâmico.

## Sequência narrativa

| Página | Pergunta do decisor | Evidência principal | Próxima investigação |
| --- | --- | --- | --- |
| 01 · Receita & Performance | Como o resultado evoluiu? | Receita, pedidos concluídos, ticket e série mensal versus mês anterior | Quais regiões sustentam a receita? |
| 02 · Pedidos & Eficiência | Quanto dos pedidos se transforma em receita reconhecida? | Receita, reembolsos, descontos dos concluídos e cancelamentos; evolução diária/7d | Como comparar meses com duração diferente e status distintos? |
| 03 · Clientes & Mix | O que foi vendido e quem volta a comprar? | Compradores, 2+ compras, taxa de recompra e receita dos itens | Quais categorias/regiões contribuem; quais produtos compõem o mix? |
| 04 · Canais & Atribuição | Como variam receita e qualidade dos pedidos por canal/mês? | Receita, conclusão, reembolso, linha mensal e barras por canal | Analisar participações e ticket por canal, com `unattributed` explícito |

## Destaques orientados por evidência

As notas vêm das análises do [MVP-04B](MVP04B_ANALISE.md) e são **exclusivas do cenário sintético completo**:

- Nov/25: receita **+42,06%** vs out/25, pedidos concluídos **+47,06%**, ticket médio **−3,40%**. O efeito é de volume, não de maior ticket.
- Fev/26: **28 dias**, receita média de **R$ 5.651,73/dia**. Normalizar dias corrige comparação de meses de comprimentos diferentes.
- **414 de 420** compradores com 2+ compras concluídas (**98,57%**) — resultado induzido, não indicador crível de retenção externa.
- Conclusão por canal: **email 91,45%** contra **social 80,47%**. Taxas definidas pelo gerador, não efeito causal.
- Orçamento continua **planejado**; não criar CAC, ROAS ou margem sem custos reais.

## Melhoria de UX específica

A página de produtos deixa de mostrar até **40 nomes individuais num gráfico de 244px de altura**. O gráfico agora usa `DimProdutos[category]`; cada SKU continua disponível na tabela de detalhe da página. A página de canais mantém filtros `FatoPedidos[channel]` e `DimData[AnoMes]` na mesma linha e reflete ambos nos gráficos e nas medidas. Os visuais foram redistribuídos dentro do canvas sem sobreposição na validação geométrica do layout.

## Escopo técnico e testes

- Arquivos editáveis em `powerbi/EcommerceAnalytics.Report/definition/pages/*` e tema em `StaticResources/RegisteredResources/EcommercePortfolio.json`.
- Qualidade estática codificada em `tests/test_mvp04c_ux.py`: inventário 50, geometria, cabeçalhos, legendas, presença de ressalvas, filtros e grão de produto.
- Os testes PBIR prévios permanecem ativos. `tests/test_mvp04b_structure.py` tem contagem de visuais revisada para 13 na quarta página.
- A revisão de geometria durante a geração não encontrou conflitos; o teste Python foi versionado mas ainda **precisa de execução**.
- **Não comprovado:** renderização correta, suportabilidade de todos os formatos JSON pela versão do Desktop, carregamento M, relações e resultados DAX no motor Tabular.
- **Pendente:** `python scripts/generate_data.py --check`, `python -m unittest discover -s tests -v`, `python scripts/local_ci.py --full` e `python scripts/export_powerbi.py --check`. Essas verificações não consomem Snowflake nem GitHub Actions e devem ser executadas antes do round-trip no Power BI Desktop.

## Critérios de aprovação visual no Desktop (etapa posterior)

1. Abrir `powerbi/EcommerceAnalytics.pbip` com todas as pastas adjacentes, sem erros de esquema ou importação.
2. Refresh completo dos sete CSVs do GitHub; conferir R$ 2.699.981,55 para a base integral e quantidade de pedidos concluídos.
3. Revisar ortografia, tipografia, quebra de linhas, eixos, tabelas e legibilidade dos 50 visuais em 1280 × 960.
4. Testar slicers em múltiplos meses, região e canal, comparando totais com o case documentado. Os avisos estáticos não devem ser confundidos com KPIs reativos.
5. Verificar que receita de itens não multiplica a receita por pedido e que os históricos desconectados não são somados aos fatos.
6. Salvar o PBIP após inspeção; versionar correções e produzir screenshots reais. Sem declarar visual aprovado antes disso.

**Próximo marco:** gates locais de integridade + paridade dbt; depois inspeção no Power BI Desktop e empacotamento do portfólio.
