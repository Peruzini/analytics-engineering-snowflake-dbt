# MVP-04D — Auditoria estática de entrega (GitHub)

**Tipo de evidência:** leitura e validações realizadas diretamente sobre os artefatos versionados em `main`. **Não equivale a testes dbt em execução, schema validation nativa do Power BI ou round-trip no Desktop.**

## Resultado da conferência

| Controle | Conferência | Resultado |
| --- | --- | --- |
| Arquivos de visuais PBIR | 4 páginas; 12 + 12 + 13 + 13 arquivos = **50 visuais** | Sem arquivo ausente na amostra integral |
| Projeções dos 50 visuais | Todas as referências de coluna/medida confrontadas com `model.bim` | **Zero referências ausentes** |
| Dimensões do layout | 50 retângulos no canvas 1280×960, sem interseção geométrica dentro de cada página | **Zero colisões/out-of-bounds** |
| Modelo semântico | **9 tabelas, 5 relacionamentos, 39 medidas DAX** presentes no Git | Inventário conferido |
| CSVs de Power BI | 420 clientes, 40 produtos, 4.200 pedidos, 8.400 itens, 365 dias, 420 resumos de clientes, 5 canais | Contagens conferidas |
| Chaves e integridade | Duplicidade de chaves, cliente/produto/pedido dos itens, contagem e valores líquidos por pedido | **Zero divergências** |
| Reconciliação financeira | Pedido, item, dia, cliente, canal = **269.998.155 centavos** = **R$ 2.699.981,55** | **Cinco grãos conciliados** |
| Regras de status | 3.588 completed; 254 cancelled; 197 refunded; 161 pending; receita reconhecida somente em completed | **Consistente nos CSVs** |

Essas conferências foram realizadas sobre a versão mais recente do repositório no momento da auditoria. **A comparação CSV versus saída dbt verdadeira permanece pendente.** A equivalência contábil entre arquivos gerados não substitui teste dos modelos SQL.

## Limites

- JSON parseável e referência existente **não significam** que o motor Power BI aceitará o visual, carregará a consulta M ou executará as medidas.
- Ausência de colisão por bounding boxes **não comprova** fonte legível, ausência de truncamento, legibilidade dos gráficos ou correta interação.
- O dataset é **deliberadamente sintético**; 98,57% de recompra e sazonalidade não são fatos comerciais.
- Esta auditoria não executou `unittest` Python, `dbt seed/run/test/snapshot` nem `export_powerbi.py`; os gates G1–G3 continuam pendentes.
- O baseline de 88 testes Snowflake já aprovado é de outra versão de dados.

## Próximo gate obrigatório

No clone atualizado, com ambiente Python ativado: `python scripts/local_ci.py --full`. A versão MVP-04D desse comando integra testes Python/YAML, dbt DuckDB e comparação dos 7 CSVs no mesmo banco temporário. Exigir `POWERBI_EXPORT_MATCH`, etapa `duckdb-powerbi-parity` PASS e `LOCAL_FULL_PASS` antes de abrir o Desktop.

[Checklist de homologação](MVP04D_RELEASE.md) · [Case de recrutamento](PORTFOLIO_CASE_STUDY.md).
