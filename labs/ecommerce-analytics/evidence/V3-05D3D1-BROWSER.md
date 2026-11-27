# V3-05D3D1 — Browser acceptance (real)

Candidato `73037de16f4efc9a25b1bf6e6426a768b369dedb`, 27/11/2026, Windows, Google Chrome 158.0.8127.37, Python 3.11.9, Playwright 1.61.0 em venv isolado, Node 26.13.1. Testes Node reais: 56/56, exit 0. Browser gate: 115/117, exit 1. 16 capturas em 4 resoluções, hashes em browser-validation.json. O arquivo JSON é a saída real do gate, recuperada do computador, não reconstruída. Inspeção visual direta das quatro páginas desktop 1440 e quatro mobile 390. Tablet e 320 testados automaticamente, sem inspeção editorial individual. Capturas locais em portfolio-v3-05d/ecommerce-browser-results; não publicadas. 

## Achados
Exportação PNG da página pedidos falhou no primeiro gráfico: diagnóstico DOM confirmou dois elementos id=status, querySelector retorna SPAN e nenhum SVG; demais testes interativos/exports dessa página foram interrompidos pelo timeout, não aprovados. Servidor local confirmou GET /favicon.ico 404. Visual desktop: eixo recompra chega a 103,53%; marcadores excessivos na receita diária e acumulada, heatmap 9/42 células abaixo de contraste 4,5:1 (auditoria anterior), rótulos de categorias/canais em inglês nas dispersões, pequenos múltiplos sem escala numérica visível, comparação MoM ausente. Mobile 390px: rolagem horizontal interna exigida, parte dos valores invisível inicialmente; DOM confirmou áreas 340px e conteúdo 550px em pedidos.

## Resultado
Gate não aprovado integralmente. Corrigir falhas e refinamentos no D3D2, repetir os gates e inspeção antes de transpor para Power BI. Sem alterações no código da aplicação, PBIP ou fontes, sem merge ou deploy. 
