# V3-05D3F1-R2 - Ecommerce visual refinement

27/11/2026. Candidate 7718e7516a0ec635c77d17a93f6e1190d9da4dbd. Base a5c94e5 (PR #5). 66 native visuals across four pages. 44 previous measures preserved exactly, six auxiliary measures and four calculated display columns added; source CSV, original keys, partitions, relationships and prior semantic definitions unchanged.

## Visual acceptance
- Executive: MoM last complete months -7.97%, verified natively; daily revenue remains chart and table. Full 12 monthly rows plus total visible.
- Orders: four status labels in Portuguese with percentages; daily revenue and seven-day moving average differentiated; 12 monthly rows plus total visible.
- Customers/products: six categories and seven regions in 42-cell heatmap; native scatter reference lines R$ 449,996.925 (mean category revenue) and 98.5714% (global repurchase rate). Distinct customers across categories are not additive. Top 10 Pareto uses percentage axis 0-100%, final cumulative share 59.0575% of all selected products, not renormalized. Product detail enlarged; intentional scroll for catalogue.
- Channels: five native small multiples with common scale; localized channel labels; weighted global ticket R$ 752.50 and completion 85.43% visible on scatter. Share denominator removes channel filters while preserving other filters. No ROAS, CAC or margin claimed.
- Localization follows approved HTML labels, including Office/Lifestyle and original product names. Display columns map source values one-to-one with fallback to raw value. Separate presentation measures preserve original business measure definitions and denominator semantics. Source keys remain unchanged.
- Four native loaded screenshots inspected, hashes and paths recorded in V3-05D3F1_R2_NATIVE_CHECKS.json. No simulated images.

## Validation
316/316 historical DAX values, 218/218 additional value comparisons for translated axes, heatmap cells, share calculations, selected statuses/channels/category-region filters and reference measures; tolerance 1e-7 absolute. 49/49 unittest including three new tests. Static bounds, overlap, tabOrder and field references PASS. 4200 orders, 8400 items, 12 months; no divergence. Initial system Python lacked duckdb; project venv already contained dependency and full suite passed. Native query was retried after refresh until actual order count reached 4200.

One Power BI instance only. Closed the disposable validation process after normal close attempt did not complete; 0 Desktop and 0 new Analysis Services processes at end. No edits in UI other than refresh, no saved round-trip committed. No merge, deploy, paid service or Snowflake credit usage. Visual refinement PASS, not full functional homologation: cross-filter interactions, synchronized filters, broader filtered regressions, mobile, accessibility and save/reopen are D3F2 gates.
