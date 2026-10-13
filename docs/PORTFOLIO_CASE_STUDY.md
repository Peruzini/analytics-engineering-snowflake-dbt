# E-commerce Analytics — Case de Analytics Engineering + Power BI

**Estudo de caso com dados 100% sintéticos e versionados.**
[Projeto PBIP](../powerbi/EcommerceAnalytics.pbip) · [Catálogo DAX](../powerbi/dax/CATALOGO.md) · [Status de validação](MVP04D_RELEASE.md)

## Problema de negócio

Um e-commerce fictício possui seis fontes: clientes, produtos, campanhas, pedidos, itens e pagamentos. Os estados dos pedidos e a diferença de granularidade entre fatos dificultam obter uma receita confiável. O objetivo é construir uma camada analítica reproduzível e comunicar o desempenho sem duplicidades.

## Solução implementada

| Camada | Entrega |
| --- | --- |
| Dados | 6 seeds CSV sintéticas e gerador Python determinístico |
| Transformação | 6 staging, 2 intermediate, 7 marts dbt |
| Qualidade | Testes Python e SQL, chaves, reconciliação por grão, reprocessamento incremental e snapshot SCD2 |
| Plataforma | DuckDB local; Snowflake utilizado em baseline anterior |
| BI | 9 tabelas, 5 relacionamentos, 39 medidas DAX, 4 páginas e 50 visuais PBIP/PBIR |
| Consumo | 7 CSVs analíticos via Power Query M; sem conexão Snowflake necessária |

**Linhagem:** Python/seeds → dbt staging → intermediate → marts DuckDB → CSV → Power Query → modelo semântico/DAX → relatório PBIR.

## Escala e indicadores do cenário

| Indicador | Valor |
| --- | ---: |
| Período | 01/10/2025 a 30/09/2026 |
| Clientes | 420 |
| Produtos | 40 |
| Pedidos / itens | 4.200 / 8.400 |
| Pedidos concluídos | 3.588 |
| Receita reconhecida | R$ 2.699.981,55 |
| Ticket médio concluídos | R$ 752,50 |
| Taxa de conclusão | 85,43% |

Esses números foram reconciliados na geração dos arquivos sintéticos. **A nova execução real dbt e a validação do Desktop ainda são pendentes**. Apenas pedidos `completed` entram em receita; os demais status têm receita reconhecida zero por uma simplificação didática documentada.

## As quatro perguntas de negócio

1. **Visão Executiva:** a evolução vem de volume ou ticket? Comparar receita mensal, mês anterior e região.
2. **Receita e Pedidos:** quanto foi concluído, reembolsado ou cancelado? Comparar receita por dia e média móvel.
3. **Clientes e Produtos:** como se distribuem recompra, categorias e contribuição por produto?
4. **Canais e Pedidos:** como variam receita, conclusão e reembolso por canal e mês, preservando pedidos sem atribuição?

## Achados da base simulada

- **Novembro/2025:** receita +42,06% vs. outubro, pedidos concluídos +47,06%, ticket −3,40%: crescimento associado sobretudo ao volume gerado.
- **Fevereiro/2026:** R$ 5.651,73/dia no cenário, com 28 dias. Não confundir duração do mês com eficiência comercial.
- **Recompra:** 414/420 compradores (98,57%) têm 2+ pedidos concluídos. Isso foi induzido pelo algoritmo, não representa retenção ou LTV futuro.
- **Canais:** diferenças de conclusão foram parametrizadas; não atribuir causalidade real a campanhas.

Não há custo de mercadoria nem gasto efetivo de mídia; **ROAS, CAC e margem não são calculáveis**. O orçamento disponível é apenas planejado.

## Decisões técnicas relevantes

**Separação de grãos** (pedido/item) evita fanout; os pagamentos são agregados antes do join. A receita é conciliada entre fato de pedidos, fato de itens e resumos de dia, cliente e canal. O campo `channel` foi incorporado ao pedido para possibilitar filtros temporais. O relatório foi criado no Git para facilitar revisão dos contratos e do DAX antes do Desktop.

## Artefatos para avaliação

[SQL e modelos dbt](../models/marts) · [Testes SQL](../tests/dbt) · [Modelo semântico](../powerbi/EcommerceAnalytics.SemanticModel/model.bim) · [PBIR](../powerbi/EcommerceAnalytics.Report) · [MVP-04B — Análise](MVP04B_ANALISE.md) · [MVP-04C — UX](MVP04C_UX_STORYTELLING.md)

**Estado:** pré-release. O pipeline atualizado, paridade CSV e abertura/renderização no Power BI ainda precisam de evidência; ver [MVP-04D](MVP04D_RELEASE.md). Capturas reais só serão anexadas após essa validação.

*Stack: Python, SQL, dbt, DuckDB, Snowflake, Power BI, Power Query M, DAX, PBIP/PBIR, Git.*
