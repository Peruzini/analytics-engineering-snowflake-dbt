# V3-05D3D3 — E-commerce: aprovação visual do laboratório HTML

27/11/2026. Candidato final de aplicação `8a03da87503314ec1ff1f35a7c3ddbcb1f728b8f`, Windows, Chrome 158.0.8127.37, Playwright 1.61.0, Node 26.13.1. Node 56/56 e browser 198/198, exit 0. D3D3 inicial: 115/115 verificações adicionais (emulação por toque e hashes). A inspeção de 16 capturas revelou quebra do último dígito de R$ 2.699.981,55 em 320px nas páginas executiva, clientes e canais. Corrigido CSS exclusivamente para <=360px, primeiro/último KPIs em largura integral, valores sem quebra. Novo gate verifica todos os KPIs em linha única.

## Regressão final
16/16 hashes das novas capturas verificados. 99/99 verificações de interação/console na emulação por toque em 390, 320, 1024 (96 página × resolução × teste + 3 consoles). Comparação de igualdade binária com 12 capturas anteriores acima de 360px: 11/12 idênticas. A exceção 1440x900-clientes.png foi inspecionada novamente e comparada pixel a pixel no computador: 1440×1393, somente 13 pixels alterados, bbox x=966 y=1038–1050, diferença RGB máxima 1/255. Aceita como variação visual desprezível, não igualdade binária; a saída bruta permanece 126/127 e exit 1, sem reclassificação artificial. As quatro novas imagens de 320px foram inspecionadas, valores monetários íntegros. Nenhum problema visual material nessa comparação. Resultado JSON do browser e mobile brutos preservados.

## Inspeção editorial
| Página | 1440 | 1024 | 390 | 320 | Observação |
|---|---|---|---|---|---|
| Receita | Aprovada | Aprovada | Aprovada | Aprovada | MoM condicionado a meses completos, precisão monetária preservada. |
| Pedidos | Aprovada | Aprovada | Aprovada | Aprovada | Status não é funil, série diária sem excesso de marcadores, média móvel enfatizada. |
| Clientes | Aprovada | Aprovada | Aprovada | Aprovada com ressalva | Heatmap mínimo 4,913:1, eixo recompra <=100%; rótulos do Pareto top 10 pequenos em 320, alternativa tabular. |
| Canais | Aprovada | Aprovada | Aprovada | Aprovada | Small multiples em escala compartilhada, sem ROAS/CAC sem gasto. |

Aprovado editorialmente como referência de Data Viz para Power BI. Tabelas mantêm rolagem interna e telas compactas exigem rolagem vertical. Não é teste físico de smartphone/tablet, WCAG integral ou leitor de tela. Capturas em %USERPROFILE%/portfolio-v3-05d/ecommerce-browser-d3d3-final. Sem alteração dos motores analíticos, bases, dbt, PBIP ou main; sem merge/deploy.

## Transposição D3D E
Priorizar receita mensal com MoM válido, composição de status, taxas e média móvel; heatmap categoria×região, dispersão de recompra e Pareto top 10 com denominador integral; pequenos múltiplos por canal e comparação ticket/conclusão. Preservar grãos e semântica de filtros. Adaptar ao canvas e equivalentes nativos Power BI; não instalar visuais pagos. Novas medidas exigem paridade e homologação Desktop.
