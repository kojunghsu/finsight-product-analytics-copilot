# FinSight productization plan

## Business problem

Digital-banking product managers often depend on analysts to translate broad questions into metrics, funnel cuts, and statistically defensible experiment readouts. This creates a slow loop between noticing an onboarding problem and deciding what to do next.

## Product

FinSight is a narrow product-analytics copilot for onboarding. It converts business language into four governed workflows: KPI definition, onboarding funnel diagnosis, customer segmentation, and A/B experiment evaluation. It is not a general data-science automation platform.

## Target users and jobs to be done

- Product managers: get a statistically grounded first-pass answer without specifying a test.
- Product analysts: standardize recurring analysis and preserve an auditable calculation trail.
- Growth and onboarding teams: identify friction, evaluate redesigns, and prepare rollout decisions.

## Value proposition

Reduce time from business question to a validated first-pass insight while keeping calculation logic governed, reproducible, and reviewable.

## Positioning and landscape

FinSight sits between general-purpose chat assistants, BI monitoring tools, product analytics suites, and experimentation platforms. Its differentiation is a domain-specific decision flow—Measure → Diagnose → Experiment → Decide—with strict separation between language reasoning and statistical computation. A real commercialization study would validate this positioning with current competitor and customer research.

## Pricing hypothesis

| Tier | Customer | Illustrative model |
|---|---|---|
| Analyst | Individual analyst or PM | Monthly per seat |
| Team | Product squad | Per-seat plus governed data connections |
| Enterprise | Regulated financial institution | Annual contract, SSO, audit, private deployment, support |

Pricing is a testable hypothesis, not a validated willingness-to-pay claim.

## Go-to-market

Start with onboarding and growth teams at digital banks and fintechs. Lead with a bounded proof of value: reduce turnaround time for recurring funnel and experiment questions, then quantify adoption, answer accuracy, analyst review time, and decision-cycle time.

## Success metrics

- Median time from question to reviewed first-pass insight
- Percentage of questions routed correctly
- Numerical agreement with analyst-authored reference results
- Analyst acceptance or correction rate
- Weekly active users and repeated workflows
- Unsupported-claim and schema-hallucination rate

## Risks and human role

Humans remain accountable for KPI-strategy alignment, data quality, experiment validity, regulatory and fairness review, operational constraints, and rollout approval. Synthetic results do not demonstrate real customer impact. LLM explanations must be evaluated for faithfulness to deterministic outputs.

## Roadmap

1. MVP: local synthetic-data prototype and four workflows.
2. Pilot: governed warehouse connection, saved analyses, evaluation harness, and analyst approval.
3. Enterprise: permissions, audit logs, private deployment, PII controls, monitoring, and integrations.
