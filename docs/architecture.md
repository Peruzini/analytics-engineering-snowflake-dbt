# Arquitetura — MVP-01

## Entrada e saída

O projeto usa exclusivamente seis datasets sintéticos. São carregados como seeds do dbt, no schema padrão `<target.schema>_raw`. As seis views `stg_*` são publicadas em `<target.schema>_staging`.

O naming padrão do dbt é intencional, pois preserva isolamento entre ambientes sem sobrescrever tabelas de outros usuários.

```text
raw_customers  -> stg_customers
raw_products   -> stg_products
raw_campaigns  -> stg_campaigns
raw_orders     -> stg_orders
raw_order_items-> stg_order_items
raw_payments   -> stg_payments
```

## Grão e regras

- Clientes: uma linha por `customer_id`.
- Produtos: uma linha por `product_id`.
- Campanhas: uma linha por `campaign_id`.
- Pedidos: uma linha por `order_id`, inclusive cancelados/pendentes/reembolsados.
- Itens: uma linha por `order_item_id` e relacionamento N:1 com pedidos e produtos.
- Pagamentos: uma linha por `payment_id`. Apenas pedidos completed/refunded possuem pagamento na amostra.

O valor de pagamento reembolsado é um **montante de transação** e não receita reconhecida. A regra de receita será definida e validada nos marts, sem misturar cancelamento, estorno e reconhecimento.

## Qualidade

A camada staging apenas padroniza nomenclatura, tipos e strings. Não faz deduplicação silenciosa nem remove pedidos por status. Contratos testam unicidade, não nulos, referências e domínios.

## Segurança e ambiente

Credenciais são recebidas por variáveis de ambiente. `profiles.yml` local não é versionado. O CI usa placeholders e `dbt parse` sem abrir conexão com Snowflake.

## Etapas futuras

MVP-02 implementará intermediate, fatos e dimensões; MVP-03 implementará testes de conciliação, snapshots, incremental e execução de integração real.
