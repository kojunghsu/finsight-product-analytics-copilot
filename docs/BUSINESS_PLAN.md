# FinSight productization plan

## Executive summary

FinSight is an LLM-powered product analytics copilot for digital-banking onboarding teams. It translates natural-language product questions into four governed workflows—KPI definition, funnel analysis, customer segmentation, and A/B experiment evaluation—while deterministic Python owns every calculation and statistical test.

The product hypothesis is that a narrow, auditable copilot can reduce the time between a product manager asking a question and an analyst reviewing a statistically grounded first-pass answer. FinSight is not positioned as a replacement for analysts or as a general-purpose data-science platform.

## Business problem

Digital-banking product teams repeatedly ask questions such as:

- What should count as successful onboarding?
- At which stage are customers leaving?
- Which customer groups experience the most friction?
- Did a redesigned flow improve activation without harming engagement?

Answering these questions often requires translating business language into metric definitions, locating approved fields, choosing an analytical method, calculating results, and communicating limitations. The bottleneck is not only computation; it is the handoff between business intent and governed analysis.

## Target users and jobs to be done

| Persona | Job to be done | Current friction | FinSight outcome |
|---|---|---|---|
| Digital-banking product manager | Diagnose onboarding performance and prepare a decision | Must translate a broad question into an analyst request | Receives a reviewable first-pass answer and next step |
| Product analyst | Standardize recurring funnel and experiment work | Repeats metric setup and stakeholder explanation | Reuses governed calculations and an audit trail |
| Growth or onboarding lead | Understand friction and evaluate a redesign | Results are split across dashboards, notebooks, and messages | Follows one Measure → Diagnose → Experiment → Decide flow |

## Value proposition

> Reduce time from a product question to a validated first-pass insight while keeping metric definitions, calculations, statistical assumptions, and limitations reviewable by a human analyst.

### Expected benefits to validate in a pilot

- Shorter turnaround time for bounded onboarding questions
- More consistent KPI and experiment definitions
- Fewer unsupported numerical claims from LLM-generated answers
- A visible handoff between automated first-pass analysis and human approval

These are product hypotheses. The prototype does not claim measured commercial impact.

## Why an LLM is necessary

A conventional dashboard works well when the user already knows the metric, filter, and visualization. FinSight addresses the earlier translation step. A product manager can ask, “Where are customers getting stuck?” without specifying a funnel query or statistical test.

The LLM is responsible for:

- mapping business language to one approved workflow;
- grounding the request in an allowlisted schema;
- selecting the metric, dimension, and explicit filters;
- explaining immutable Python results in product language;
- stating limitations and one bounded next step.

The LLM is not allowed to calculate metrics, execute arbitrary code, invent fields, or approve a rollout. This separation is the central product design, not an implementation detail.

## Product design

### Core journey

```text
Measure → Diagnose → Experiment → Decide
```

1. **Measure:** define activation and supporting onboarding KPIs.
2. **Diagnose:** locate funnel loss and compare approved customer dimensions.
3. **Experiment:** compare Control and Treatment using deterministic statistics.
4. **Decide:** interpret evidence, guardrails, assumptions, and human checks.

### MVP workflows

| Workflow | Example question | Deterministic output | LLM contribution |
|---|---|---|---|
| KPI definition | What should we measure? | Definitions and current values | Map business objective to primary/supporting metrics |
| Funnel analysis | Where are customers dropping off? | Stage counts, conversion, drop-off | Route the question and explain the largest loss |
| Segmentation | Which channel has the lowest activation? | Counts and rates for one approved dimension | Select the dimension and communicate descriptive limits |
| A/B experiment | Did the redesign improve activation? | Group rates, lift, CI, p-value, guardrail | Explain estimated effect and bounded rollout conditions |

Detailed requirements, error states, non-goals, and acceptance criteria are documented in [PRODUCT_SPEC.md](PRODUCT_SPEC.md).

## Market landscape

Market review checked **August 13, 2026** using official vendor product and pricing pages. Products and prices may change.

| Product | Current positioning relevant to FinSight | Pricing signal | Gap FinSight explores |
|---|---|---|---|
| Amplitude | Broad digital/product analytics platform with AI agents, product analytics, feature experimentation, session replay, and activation | Free tier; higher tiers scale by volume and enterprise requirements | FinSight is narrower: banking onboarding, four governed decisions, transparent Python calculations |
| Mixpanel | Product analytics with funnels, retention, flows, session replay, Mixpanel Agent, and enterprise experimentation/security capabilities | First 1M monthly events free; Growth usage pricing and custom Enterprise | FinSight emphasizes statistical auditability and domain-specific decision language rather than broad self-service analytics |
| Statsig | Integrated experimentation, feature management, product analytics, and session replay | Developer tier is free; Pro is listed at $150/month with included events | FinSight does not manage feature flags or experimentation infrastructure; it focuses on interpreting uploaded onboarding data |
| ThoughtSpot Spotter | Enterprise AI analytics and natural-language data exploration with governed data integration | Developer pricing begins at $25/user/month; enterprise is custom | FinSight is a small local prototype with a constrained analytics contract rather than a general enterprise BI agent |

Official references: [Amplitude pricing and platform](https://amplitude.com/pricing), [Mixpanel pricing](https://mixpanel.com/pricing/), [Statsig pricing](https://statsig.com/pricing), [ThoughtSpot pricing](https://www.thoughtspot.com/pricing), and [ThoughtSpot Spotter](https://www.thoughtspot.com/product/agents/spotter).

### Competitive position

FinSight should not claim feature superiority over established platforms. Its testable differentiation is:

- one high-context use case: digital-banking onboarding;
- a small allowlisted workflow surface instead of open-ended analysis;
- deterministic calculations separated from LLM reasoning;
- an exposed plan/result audit trail;
- explicit human responsibility for strategy, data quality, compliance, and rollout.

The commercial question is whether this narrower experience creates enough speed, trust, or workflow fit to justify a standalone product or vertical add-on. That requires customer discovery and pilot evidence.

## Pricing hypothesis

The following figures are **illustrative hypotheses for customer interviews**, not validated willingness-to-pay or a launch commitment.

| Tier | Illustrative price | Intended customer | Included hypothesis |
|---|---:|---|---|
| Free demo | $0 | Students and evaluators | Synthetic data, four workflows, limited LLM questions |
| Individual | $12/user/month | Individual PM or analyst | CSV upload, complete analyses, audit export |
| Team | $99/month | One product squad, up to 10 users | Shared analyses, metric definitions, and review workflow |
| Enterprise pilot | Custom; target $5,000–$10,000/year | Regulated financial institution testing one use case | Private pilot, onboarding support, and one governed data connection |

### Pricing logic

- A free demo makes the prototype easy to evaluate without implying production readiness.
- A low individual price reduces trial friction but must eventually cover model and support costs.
- Team pricing aligns value with a product squad rather than charging for every query.
- The enterprise offer is framed as a limited pilot because the MVP does not yet include full SSO, RBAC, private deployment, or production support.
- A production model would test seat-based, event-volume, and annual platform pricing against customer preferences.

## Go-to-market hypothesis

### Beachhead

Start with onboarding and growth teams at digital banks and fintechs that already run controlled product experiments but experience delays in routine analysis.

### Pilot motion

1. Connect one approved onboarding dataset.
2. Define a reference set of 20–30 recurring product questions.
3. Compare FinSight answers with analyst-authored results.
4. Measure routing accuracy, numerical agreement, review time, and correction rate.
5. Expand only if the pilot demonstrates both accuracy and useful time savings.

### Channels

- Founder-led outreach to product analytics leaders
- Partnerships with analytics consultancies serving fintech
- A portfolio/demo version for practitioner feedback
- Content showing audited product-analysis workflows rather than generic AI claims

## Success metrics

### Product quality

- Correct workflow-routing rate
- Numerical agreement with analyst-authored reference results
- Unsupported-field and unsupported-claim rate
- Analyst acceptance, correction, and rejection rates
- Percentage of answers with an accurate limitation and actionable next step

### Business value

- Median time from question to reviewed first-pass insight
- Weekly active users and repeated workflows
- Reduction in routine analyst turnaround time
- Pilot-to-paid conversion and team expansion

## Risks and human role

| Risk | MVP mitigation | Human responsibility |
|---|---|---|
| Schema or metric hallucination | Allowlisted structured plan | Approve the semantic layer and metric definitions |
| Incorrect numerical claims | Deterministic Python calculations | Review data quality and analytical assumptions |
| Overstated causal or rollout language | Experiment-specific prompt rules and limitations | Validate randomization, SRM, operational, legal, and compliance constraints |
| Sensitive financial data exposure | Synthetic data in the prototype | Approve production hosting, access, retention, and PII controls |
| Automation bias | Visible audit trail and bounded next step | Make the final product and rollout decision |

Synthetic results do not demonstrate real customer impact. A production pilot would require privacy, security, model-risk, fairness, and regulatory review.

## Roadmap

1. **MVP:** local synthetic-data prototype with four governed workflows.
2. **Pilot:** warehouse connection, saved analyses, evaluation harness, SRM checks, and analyst approval.
3. **Team product:** shared metric catalog, permissions, comments, and decision history.
4. **Enterprise:** SSO, RBAC, private deployment, PII controls, monitoring, and audit retention.

## Assumptions to validate

- Product teams have enough recurring questions for a constrained copilot to be useful.
- Analysts prefer reviewing a governed first pass over answering every question from scratch.
- Banking-specific language and controls produce meaningfully more trust than a general analytics agent.
- Customers will pay for workflow speed and governance rather than only for additional dashboards.
