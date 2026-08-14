# FinSight productization plan

## Executive summary

FinSight is an LLM-powered product analytics copilot for credit-card product teams. It first determines which of four lifecycle use cases an uploaded customer-level dataset can support—Acquisition & Onboarding, Activation & Early Use, Engagement & Spend, and Retention & Inactivity—then routes natural-language questions to governed deterministic analyses. A/B experiment evaluation is available when the required experiment fields are present.

The product hypothesis is that a narrow, auditable copilot can reduce the time between a product manager asking a question and an analyst reviewing a statistically grounded first-pass answer. FinSight is not positioned as a replacement for analysts or as a general-purpose data-science platform.

## Product positioning

> **For credit-card product managers and product analysts who need faster answers to recurring lifecycle questions, FinSight is a governed product analytics copilot that converts natural-language questions and customer-level CSV data into reviewable first-pass evidence. Unlike broad self-service analytics agents, FinSight uses a credit-card-specific metric contract, deterministic Python calculations, explicit dataset-compatibility checks, and human approval before decisions are acted upon.**

FinSight occupies the decision-preparation layer between a business question and deeper analyst investigation. It does not replace the data warehouse, event-tracking platform, experimentation infrastructure, or product analyst. Its initial wedge is a recurring set of credit-card lifecycle decisions where speed, consistent definitions, and statistical traceability matter more than unlimited analytical flexibility.

### Initial customer, user, and buyer

- **Beachhead customer:** a digital bank or fintech with a credit-card product team and recurring onboarding, activation, engagement, retention, and experiment questions.
- **Primary daily users:** product managers, product analysts, and growth or onboarding leads.
- **Likely economic buyer for a pilot:** a Head of Product Analytics, Growth, Data, or Digital Product who owns analyst capacity and decision quality.
- **Human value retained:** analysts validate schema meaning, data quality, assumptions, and recommendations; product and risk leaders retain final decision authority.

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

### Customer value by category

| Value category | Current workflow problem | FinSight value hypothesis |
|---|---|---|
| Speed | A bounded question waits for metric clarification and analyst setup | Produce a reviewable first pass in one governed workflow |
| Consistency | KPI definitions and denominators vary across dashboards or notebooks | Reuse an explicit credit-card metric contract and deterministic calculations |
| Trust | Open-ended AI answers may invent fields, numbers, or causal explanations | Separate LLM planning from Python computation and expose limitations and an audit trail |
| Analyst leverage | Analysts repeatedly rebuild routine funnel and experiment summaries | Automate first-pass preparation while preserving analyst review for higher-value investigation |
| Decision safety | Teams may analyze unsupported data or overstate descriptive results | Gate workflows by confirmed fields and refuse unsupported or causal claims |

The commercial value is therefore not “more analytics features.” It is a shorter and more controlled path from a recurring product question to evidence that an analyst can review, correct, and communicate.

## Why an LLM is necessary

A conventional dashboard works well when the user already knows the metric, filter, and visualization. FinSight addresses the earlier translation step. A product manager can ask, “Where are customers getting stuck?” without specifying a funnel query or statistical test.

The LLM is responsible for:

- mapping business language to one approved workflow;
- grounding the request in an allowlisted schema;
- selecting the metric, dimension, and explicit filters;
- explaining immutable Python results in product language;
- stating limitations and one bounded next step.

The LLM is not allowed to calculate metrics, execute arbitrary code, invent fields, or approve a rollout. This separation is the central product design, not an implementation detail.

### Human-reviewed schema mapping

Different banks may describe equivalent lifecycle events with different names—for example, `kyc_completed` instead of `identity_verified`. FinSight proposes mappings only from an explicit approved alias list; it does not use fuzzy similarity or silently reinterpret an event. The user reviews source-to-target mappings before a deterministic compatibility engine enables only the use cases supported by the normalized dataset.

This reduces setup friction without pretending that a similar-looking name proves business equivalence. Confirmed mappings and file-level provenance appear in the audit trail, preserving accountability for the analytical definition.

## Product design

### Core journey

```text
Measure → Diagnose → Experiment → Decide
```

1. **Measure:** define activation and supporting onboarding KPIs.
2. **Diagnose:** locate funnel loss and compare approved customer dimensions.
3. **Experiment:** compare Control and Treatment using deterministic statistics.
4. **Decide:** interpret evidence, guardrails, assumptions, and human checks.

### MVP lifecycle use cases

1. Acquisition & Onboarding
2. Activation & Early Use
3. Engagement & Spend
4. Retention & Inactivity

KPI, funnel, segmentation, and A/B evaluation are governed analytical capabilities applied only when their required fields are present.

| Workflow | Example question | Deterministic output | LLM contribution |
|---|---|---|---|
| KPI definition | What should we measure? | Definitions and current values | Map business objective to primary/supporting metrics |
| Funnel analysis | Where are customers dropping off? | Stage counts, conversion, drop-off | Route the question and explain the largest loss |
| Segmentation | Which channel has the lowest activation? | Counts and rates for one approved dimension | Select the dimension and communicate descriptive limits |
| Engagement & Spend | How are customers using and spending on the card? | 30-day active rate, transaction frequency, average spend, and spend among active customers | Explain usage depth and keep the result descriptive |
| Retention & Inactivity | How do 30-day and 90-day activity compare? | Separate activity-window rates and reactivation when available | Explain that the windows are not a monotonic survival curve |
| A/B experiment | Did the redesign improve activation? | Data-quality gates, group rates, lift, CI, p-value, SRM, guardrail, approximate MDE, directional segment consistency | Explain estimated effect and bounded phased-rollout conditions |

Detailed requirements, error states, non-goals, and acceptance criteria are documented in [PRODUCT_SPEC.md](PRODUCT_SPEC.md).

## Market landscape

Market review checked **August 13, 2026** using official vendor product and pricing pages. Products and prices may change.

| Product | Current market positioning | Pricing signal | FinSight's differentiated focus |
|---|---|---|---|
| Amplitude | Broad product analytics platform covering behavioral analytics, experimentation, session replay, activation, and AI-assisted analysis | Free tier; higher tiers scale by volume and enterprise requirements | Credit-card-specific lifecycle metrics, dataset-compatibility checks, deterministic Python calculations, and human review |
| Mixpanel | Self-service product analytics for funnels, retention, flows, segmentation, and AI-assisted exploration | First 1M monthly events free; Growth usage pricing and custom Enterprise | Governed metric definitions, schema confirmation, statistical auditability, and credit-card decision language rather than broad event exploration |
| Statsig | Experimentation and feature-delivery platform combining feature flags, product analytics, and session replay | Developer tier is free; Pro is listed at $150/month with included events | Evaluation of uploaded experiment outcomes through CI, significance, SRM, MDE, guardrails, and bounded decision gates—not experiment delivery infrastructure |
| ThoughtSpot Spotter | Enterprise AI analytics and natural-language data exploration integrated with governed business data | Developer pricing begins at $25/user/month; enterprise is custom | A constrained analytics contract for recurring credit-card lifecycle decisions, with LLM interpretation separated from deterministic computation |

Official references: [Amplitude pricing and platform](https://amplitude.com/pricing), [Mixpanel pricing](https://mixpanel.com/pricing/), [Statsig pricing](https://statsig.com/pricing), [ThoughtSpot pricing](https://www.thoughtspot.com/pricing), and [ThoughtSpot Spotter](https://www.thoughtspot.com/product/agents/spotter).

### Competitive position

FinSight is complementary to established analytics platforms, not a feature-for-feature replacement. A data warehouse or product analytics platform stores and exposes the underlying data; FinSight tests whether a governed, domain-specific decision layer can make recurring credit-card questions faster and safer to answer.

Its testable differentiation is:

- four bounded, related use cases across the credit-card customer lifecycle plus experiment evaluation when compatible fields are present;
- a small allowlisted workflow surface instead of open-ended analysis;
- deterministic calculations separated from LLM reasoning;
- an exposed plan/result audit trail;
- explicit human responsibility for strategy, data quality, compliance, and rollout.

The commercial question is whether this narrower experience creates enough speed, trust, or workflow fit to justify a standalone product or vertical add-on. That requires customer discovery and pilot evidence.

The credit-card focus is a deliberate beachhead rather than the final market boundary. If customers validate the architecture and workflow, the same governed pattern could expand to deposit onboarding, consumer lending, digital wallets, BNPL, and other regulated financial-product journeys. Expansion would require a separately approved metric and schema contract for each product; FinSight would not assume that credit-card definitions transfer automatically.

## Pricing hypothesis

The following figures are **illustrative hypotheses for customer interviews**, not validated willingness-to-pay or a launch commitment.

| Tier | Illustrative price | Intended customer | Included hypothesis |
|---|---:|---|---|
| Free demo | $0 | Evaluators and individual practitioners | Synthetic data, sample files, and bounded lifecycle demonstrations |
| Individual | $9–$15/user/month | Individual PM or analyst | CSV upload, supported lifecycle analyses, and audit export |
| Team | $49–$79/month | One small product squad | Shared analyses, metric definitions, and review workflow |
| Enterprise pilot | Custom; target $2,500–$5,000 for three months | Regulated financial institution testing one bounded use case | Private pilot, schema and KPI setup, evaluation support, and one governed data connection |

### Pricing logic

- A free demo makes the prototype easy to evaluate without implying production readiness.
- A low individual price reflects the deliberately constrained MVP and reduces trial friction while testing willingness to pay.
- Team pricing aligns value with one product squad instead of competing with the breadth of an enterprise analytics platform.
- Enterprise pilot pricing covers schema validation, KPI configuration, evaluation, security review preparation, and onboarding support—not software feature breadth alone.
- The enterprise offer remains a time-boxed pilot because the MVP does not yet include full SSO, RBAC, private deployment, or production support.
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
| Overstated causal or rollout language | Experiment-specific prompt rules, SRM alert, and limitations | Validate randomization, operational, legal, and compliance constraints |
| Sensitive financial data exposure | Synthetic data in the prototype | Approve production hosting, access, retention, and PII controls |
| Automation bias | Visible audit trail and bounded next step | Make the final product and rollout decision |

Synthetic results do not demonstrate real customer impact. A production pilot would require privacy, security, model-risk, fairness, and regulatory review.

## Roadmap

1. **MVP:** local synthetic-data prototype spanning four credit-card lifecycle use cases, governed analytical workflows, schema mapping, SRM, approximate MDE, and analyst-facing decision gates.
2. **Pilot:** warehouse connection, saved analyses, evaluation harness, configurable experiment-allocation ratios, exposure-window validation, and analyst approval.
3. **Team product:** shared metric catalog, permissions, comments, and decision history.
4. **Enterprise:** SSO, RBAC, private deployment, PII controls, monitoring, and audit retention.

## Assumptions to validate

- Product teams have enough recurring questions for a constrained copilot to be useful.
- Analysts prefer reviewing a governed first pass over answering every question from scratch.
- Banking-specific language and controls produce meaningfully more trust than a general analytics agent.
- Customers will pay for workflow speed and governance rather than only for additional dashboards.
