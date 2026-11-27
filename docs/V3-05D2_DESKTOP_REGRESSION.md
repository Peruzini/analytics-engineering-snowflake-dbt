# V3-05D2 — Refinamento e regressão E-commerce

Candidato final: 8050234934c6b82c8716ef6ea046bf0038adb65b; candidato intermediário 2145352bf5ae0339b23292e7c8c4fe07ae55d1b7. Power BI Desktop Windows 2.160.1151.0, worktrees isoladas, 26/11/2026 BRT.

- Tema com unidades de exibição explícitas, cartões de pedidos inteiros. Inspeção intermediária detectou truncamento de receita após desabreviação; cinco cartões monetários ajustados para 18D no candidato final.
- Execução real de `python -m unittest discover -s tests`: 46/46 PASS em ambos os candidatos; exit 0. DAX nativo no intermediário: 4.200 pedidos, 3.588 concluídos, receita 2699981.55, 420 compradores, 414 recorrentes; quatro status e taxas 0/1; accessories × BA 60/54 e 52606.47.
- Candidato final aberto e atualizado; quatro capturas reais inspecionadas. Receita completa R$ 2.699.981,55, reembolso R$ 156.410,28, 3.588 e 4.200 pedidos, 420/414 clientes, cinco séries de canal; nenhum truncamento de KPI monetário observado. Uma tentativa de captura falhou por janela minimizada, corrigida restaurando a janela e repetindo.
- Modelo semântico/CSV e pipeline dbt não alterados. Evidência do ciclo dbt V3-05C3 (91 testes e paridade 7/7) permanece no candidato anterior; dbt completo não repetido nesta etapa de apresentação.

Capturas locais em inspection-d2, não publicadas. Rótulos/rodapés pequenos a 60% de zoom; capturas editoriais com painéis ocultos no V3-05E. Acessibilidade/mobile e novo round-trip do candidato D2 não foram testados; D1 comprovado no baseline anterior. Sem merge.
