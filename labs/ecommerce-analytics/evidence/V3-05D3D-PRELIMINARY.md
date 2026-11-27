# V3-05D3D — Gate browser / auditoria preliminar

Candidato `2391dec0d5aac4c8ccaaa6e0f38508da0625e61e`, 27/11/2026. 56/56 verificações JS reexecutadas nesta sessão a partir dos módulos recuperados; 14 gráficos / 4 páginas gerados. Não equivalem a renderização de browser. Desktop Commander offline e ambiente isolado sem DNS para GitHub; não houve execução da aplicação integral nem capturas de página. Sem merge/deploy.

## Achados
- Ambos: verificar rótulos SVG longos, sobreposição em dispersões, escala percentual e datas, uso de espaço acima da dobra, seleção por mouse/teclado e rolagem horizontal no mobile. O preenchimento #789BB5 contra branco tem contraste 2,94:1, inferior a 3:1 para elementos gráficos informativos; a legenda textual ajuda, mas recomenda-se escurecer a cor e testar.
- Heatmap: 9/42 células na seleção integral com contraste de texto <4,5:1 (mínimo 3,42:1). Office BA/MG/PR/RS/SP e Peripherals PR/RJ/RS/SP. Calcular cor de texto por luminância do fundo efetivo, não limiar de opacidade.
- Gráfico de composição de pedidos isolado: SVG real gerado pelo código e transferido para Chromium 144.0.7559.96. Quatro segmentos alcançados por Tab; bbox 720×125, labels presentes. Conversão via clone/serialize/Image/canvas produziu PNG 1440×250, 27.905 bytes. Não testado o botão/export download na aplicação integral.
- Comparação MoM da receita ainda ausente; incluir delta mensal com comparação válida ou explicitar indisponibilidade em períodos parciais.

## Roteiro automatizado preparado (não executado)
`tests/browser_gate.py`: 4 viewports (1440×900, 1024×768, 390×844, 320×720), navegação, 4 KPIs/página, inventário SVG, overflow e recorte geométrico de texto, screenshots e hashes, exportações PNG/CSV, seleção teclado/mouse, persistência de filtro, contexto vazio, console. Revisão humana das capturas, contraste dinâmico e leitor de tela permanecem separados. O script depende de Python Playwright e Chromium locais, não altera app ou PBIP; saídas fora do clone. Não foi executado/validado nesta etapa. Para ambiente já equipado, executar na raiz:

```powershell
python labs/ecommerce-analytics/tests/browser_gate.py --output "$env:TEMP/portfolio-v3-05d3d-ecommerce-analytics"
```

Se o ambiente não tiver Playwright, preparar dependência local isolada e navegador, mediante autorização; opcionalmente indicar Chrome/Chromium instalado com --executable. Gate D3D permanece PENDENTE; não transpor design para Power BI antes de homologar páginas e corrigir achados.
