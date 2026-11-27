# V3-05D1 — Homologação nativa E-commerce Analytics

Candidato: `9266fdd9d847bf065403fd3c9979ea224dd07be4`. Power BI Desktop Windows 2.160.1151.0; 26/11/2026 BRT (27/11 UTC). Abertura, refresh, navegação, salvamento e reabertura reais em worktree isolada. O Desktop reserializou BIM para TMDL localmente; 39 medidas, 52 visuais, 8 sortDefinition e 36 altText preservados. No gráfico de canais, a única diferença de queryRef observada foi a ordem das propriedades Category/Series/Y, sem troca de campos. Reabertura em novo processo com KPIs populados.

## Evidência nativa DAX
- 365 dias, 420 clientes, 40 produtos, 4.200 pedidos, 8.400 itens, 365 resumos diários, 420 resumos de clientes, 5 canais e uma linha na tabela Medidas; contagens reconfirmadas após reabertura.
- Receita reconhecida R$ 2.699.981,55, 3.588 concluídos, ticket 752,503219063545, taxa conclusão 0,854285714285714, 420 compradores e 414 recorrentes.
- Seis categorias, quatro status e cinco canais coincidentes com V3-05C1; Accessories × BA: 60 compradores, 54 recorrentes, R$ 52.606,47. As taxas de cancelamento/reembolso sob seleção individual produziram 0/1 conforme contrato.
- O aviso anterior de tabelas incompletas não reapareceu na inspeção das páginas reabertas; nenhuma tabela vazia. Sua causa exata não foi estabelecida.

## Inspeção visual real (quatro páginas)
Capturas reais das janelas a 60% de zoom foram inspecionadas. KPIs, tabelas e gráficos renderizados; cinco séries da evolução mensal de receita por canal visíveis. Sem erros de visual observados. Ajuste necessário: cartões de pedidos concluídos (3.588) e totais (4.200) exibem ambos “4 Mil”; configurar unidades sem abreviação e inteiros. Aprimorar legibilidade dos rótulos, rodapé e ocupação de tabela antes das capturas editoriais; ocultar painéis e tooltips.

Capturas locais reais, ainda não publicadas:
- EcommerceAnalytics-1.png: `1060fe40ea8178ae2ae228e2c6a2c444f6c845c2e515bccdfc083f6cfa78b371`
- EcommerceAnalytics-2.png: `1dea2adc4575c65d05cb593868620fd3fd4699ea5131466160f11f7d2ee28659`
- EcommerceAnalytics-3.png: `cff9fc7aa4b911231b292f05336287068fbf5bca8a3f1cf072855a16a0eeab10`
- EcommerceAnalytics-4.png: `b30de219547d97af71991b9293d694aa95b999430bd52b45296a08c8f25a9f55`

Status: G4 com abertura, refresh, salvamento/reabertura, navegação, KPIs e renderização desktop aprovados, acabamento pendente. G5 capturas editoriais pendentes. Filtros testados por consultas DAX, não matriz exaustiva de interação por mouse/teclado, leitor de tela ou mobile. Sem merge, sem migração TMDL no Git, sem publicação no Power BI Service. A evidência dbt V3-05C3 permanece vinculada ao candidato testado.
