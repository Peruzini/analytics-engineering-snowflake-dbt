# V3-05C1 — Contrato de filtros, grãos e snapshot

## Regras
- Status: numerador e denominador respeitam a seleção; contagens de status usam KEEPFILTERS e retornam zero quando há pedidos mas nenhum daquele status. Sem pedidos, taxas ficam vazias. Um único status pode produzir 0% ou 100%; não interpretar como taxa global.
- Categoria: compradores e recompra derivam de FatoItens concluídos. Recompra = dois ou mais order_id distintos com itens selecionados, não quantidade de itens. Receita por região nessa página e receita por comprador usam receita de itens; pedidos mistos não duplicam receita. As medidas de receita/pedidos do grão pedido mantêm sua semântica; não usar para analisar categoria sem adaptação.
- Relacionamentos existentes preservados, sem bidirecionais. Resumos históricos preservados e não somados aos fatos.
- Canais: legenda proposta na série temporal; participação mantém denominador de todos os canais com os demais filtros vigentes. Notas estáticas identificadas.
- Média móvel atravessa limites mensais; acumulado respeita a seleção externa do calendário. Homologar contexto DAX real.
- Sete consultas M fixadas em SHA de origem: b1c285cfd54564b2849f9e7a9c61f42c2e782b91. A referência JSON lista os blobs e resultados. Para mudar fixture, primeiro comprovar paridade dbt/CSV; publicar nova revisão e atualizar simultaneamente sete URLs, manifesto e teste de snapshot. Não usar main flutuante.
- 39 medidas, 9 tabelas, 5 relações e 50 visuais preservados; somente cinco visuais alterados. Sem reforma estética nesta etapa.

## Evidência
[Snapshot e reconciliação independente](V3-05C1_CSV_REFERENCE.json). Treze verificações em CSVs integrais passaram; receita de 269998155 centavos em cinco grãos. Categoria e região foram recalculadas independentemente. Não houve execução dos testes Python, dbt, Power Query, DAX, schemas oficiais ou Desktop. A legenda Series proposta, notas e comportamento real dos filtros requerem homologação. V3-05C2 é layout, C3 é execução/paridade dbt, D é Desktop.
