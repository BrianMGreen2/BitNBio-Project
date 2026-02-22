# Context Engineering for AI Systems: A Case Study in Lifecycle Design

> *Who Gives a Fly as a worked example of how to design the information architecture an AI system needs to be trustworthy — not just today, but as knowledge accumulates over time.*

---

## What this document is

This repository was built as a one-day competition entry. That context matters for understanding what it demonstrates and what it doesn't.

What it doesn't demonstrate is a finished system. The knowledge base is sparse, most scoring dimensions are inferred rather than evidenced, the AI-assisted content generation layer described in `AI_ASSISTED_CONTENT.md` hasn't been implemented, and the curation backlog identified by `prioritise.py` is 190 items long.

What it does demonstrate — and what was the actual design challenge — is how to build the *information architecture* that would make an AI system trustworthy across the full lifecycle of a knowledge-intensive domain. The biology is real, the scoring criteria are defensible, and the validation infrastructure is functional. But the deeper work was figuring out what context an AI system would need at each stage of this domain's development, and building the structures that would supply that context reliably.

That is context engineering. This document explains what it is, why it matters, and what the design decisions in this project illustrate about how to do it.

---

## The problem context engineering addresses

Most discussions of AI capability focus on what models can do given a prompt. Context engineering focuses on a different question: what information does a model need to have available — in what form, at what granularity, with what provenance — for its outputs to be trustworthy for a specific purpose?

This is a harder question than it looks, for three reasons.

**The form matters as much as the content.** An AI model given a 50-page PDF of literature on cross-species Rb pathway biology and asked to assess translational risk will produce an output. Whether that output is trustworthy depends entirely on whether the model correctly extracted, weighted, and synthesised the relevant information from the document — which is not reliably verifiable. The same information represented as structured, scored, sourced JSON with explicit evidence tiers produces outputs that *can* be verified, because the source is queryable and the claims are checkable. The content is the same; the context engineering is different; the trustworthiness is categorically different.

**The context requirements change as knowledge accumulates.** A system in month one, when everything is inferred, needs different context structures than the same system in month twelve, when evidence entries have been curated and validated. If the context architecture is designed only for the mature state, the system is unusable at the start. If it's designed only for the sparse state, it can't take advantage of richer data as it accumulates. Good context engineering designs for the full lifecycle — including the transition between states.

**Different uses of the same knowledge require different context.** A translational scientist, a clinical trialist, and a regulatory specialist all need knowledge about cross-species pathway conservation — but they need different aspects of it, framed differently, with different uncertainty representations. A context architecture that serves one audience well will not automatically serve the others. This is not a limitation to work around; it is a design requirement to plan for.

These three pressures — form, lifecycle, and audience — define the context engineering problem. The Who Gives a Fly system was designed to address all three, and the design decisions that address them are visible throughout the codebase and documentation.

---

## The five layers of context engineering in this project

### Layer 1: The knowledge schema — deciding what exists and what is first-class

The first context engineering decision is what counts as knowledge in this domain and how it is represented. This decision is made in `config/pathways.json`, `config/evidence_schema.json`, and `config/translational_risk_rubric_data.json`, and it is much more consequential than it appears.

Every field in the evidence schema is a decision about what an AI system will be able to reason about. Fields that exist can be queried, validated, scored, and passed as context. Fields that don't exist create gaps that get filled by inference — which means the AI model draws on its training distribution rather than on curated domain knowledge. The gap between what the schema captures and what the domain requires is the gap between what the system knows and what it is guessing.

The schema design decisions in this project were made against that standard. `evidence_tier` exists as a first-class field because an AI system generating a document needs to know how much confidence to place in each piece of evidence — and that judgment cannot be left to the model's interpretation of narrative text. `supports_validity` and `concordance` exist as explicit booleans rather than being inferred from description text because the scientific review gates that catch bad scoring (`W-N02`: `phenotype_match: "different"` with `supports_validity: true`) depend on them being machine-readable. The `pmid` field is required at specific score levels not because the system cares about citation format but because a claim without a primary source is qualitatively different from a claim with one, and that difference needs to be structurally represented so downstream systems can act on it.

**The generalisation:** In any domain where AI systems will be used for high-stakes decisions, the first context engineering question is: what are the minimum schema fields required to make AI outputs verifiable? Not what would be nice to capture — what is load-bearing for the difference between a trustworthy and an untrustworthy output?

### Layer 2: The evidence lifecycle — designing for how knowledge actually enters the system

The second context engineering decision is how knowledge gets into the schema — and this is where most systems fail. A schema that is beautifully designed but never populated with reliable data produces a system that generates confident-sounding outputs from an empty knowledge base, which is worse than no system at all.

The curation workflow in `validate_evidence.py` was built around a specific theory of how knowledge should enter this system: through a sequence of gates that progressively increase the trustworthiness of each piece of evidence before it is committed to the knowledge base. The template generates a structured blank that forces the curator to address every required field. The `--entry` command checks structural validity. The `--review` command checks scientific consistency — the score-evidence gates that prevent inflation of uncertain findings into confident scores. The `--approve` command stamps provenance and upgrades the evidence tier.

Each gate is a context engineering decision: it determines what an AI model will see when it draws on a particular piece of evidence. An entry that passes all gates is not just structurally valid — it has been checked against the domain's evidence standards, and its tier accurately reflects its quality. When the AI generation layer uses it as context, it can propagate that confidence level into the generated document.

The alternative — accepting evidence entries without gates, trusting curators to self-assess quality — produces a knowledge base where high-quality and low-quality evidence are indistinguishable to downstream systems. The AI model cannot tell the difference between a score of 4 backed by two independent in vivo studies and a score of 4 backed by a single unpublished cell line observation, because the schema doesn't represent that distinction unless the gates enforce it.

**The generalisation:** The context engineering question at this layer is: what gates does knowledge need to pass before it can be used as AI context without explicit qualification? What is the minimum evidence standard for an unqualified assertion in a generated document? The answer to this question determines the curation workflow — and the curation workflow determines the quality ceiling of everything the AI system produces.

### Layer 3: The scoring system — structured uncertainty representation

The third context engineering decision is how the system represents what it doesn't know. This is addressed by the five-dimension scoring system in `risk_scorer.py` and the `evidence_tier` field that threads through every output.

The conventional approach to uncertainty in AI systems is to add a disclaimer. "This information may be incomplete." "Consult an expert before acting." These are true and useless. They treat uncertainty as a uniform property of the entire output rather than as something that varies by dimension, by component, and by evidence source.

The scoring system in this project represents uncertainty structurally. D1 and D2 scores, once Ensembl data is available, carry `scored_by: "enriched"` — they are derived from authoritative API data and can be treated with corresponding confidence. D3, D4, and D5 scores carry `scored_by: "inferred"` until evidence entries are curated — they are estimated from keyword patterns in free-text annotations, and the rationale string is prefixed with `[INFERRED]`. The record-level `evidence_tier` summarises the overall state: `"validated"`, `"partial"`, or `"inferred"` depending on the mix.

This structured uncertainty representation does two things for downstream AI use. First, it enables appropriate hedging: a generation prompt that includes `evidence_tier: "inferred"` for D3 and D4 can instruct the model to qualify those dimensions specifically, rather than applying a blanket disclaimer to the entire document. Second, it makes the confidence level of each claim auditable: the validation module can check whether the generated document's register of certainty for each claim matches the evidence tier of the data it was generated from.

The override and modifier rules serve the same function at a different level. They represent structured expert judgment about which conditions are serious enough to override the composite score — knowledge that cannot be captured in the weighted sum but must be represented explicitly for downstream systems to act on it correctly. OR-01 (no homolog → Critical regardless of composite) is not a rule that emerges from the math; it is a domain expert's judgment encoded in a form an AI system can use without having to rediscover it from first principles.

**The generalisation:** The context engineering question at this layer is: what is the finest-grained representation of uncertainty the domain requires? At what granularity do confidence levels need to vary? A blanket disclaimer is a failure of context engineering, not a solution to it.

### Layer 4: The prioritisation system — directing human attention to where it matters most for AI context quality

The fourth context engineering decision is how the system manages its own knowledge gaps. This is addressed by `prioritise.py` and the coverage report in `validate_evidence.py --report`.

A knowledge base that has gaps is normal and expected. The question is whether those gaps are in the places that matter most for the system's primary purpose, or whether they are randomly distributed. An AI system whose knowledge is deep in areas that rarely come up and thin in the areas that determine 80% of its outputs is worse than useless — it is confidently wrong where it matters.

The prioritisation system in this project scores gaps by a combination of three signals: the current risk level of the component (which determines how consequential a wrong assessment would be), the dimension weight in the composite score (which determines how much the gap affects the output), and the inference uncertainty of the affected dimension (which determines how unreliable the current estimate is). This combination produces a ranked backlog that directs curation effort to exactly the places where AI context quality is lowest relative to the importance of getting it right.

This is context quality management — the ongoing process of identifying where the gap between what the AI system needs to produce trustworthy outputs and what it currently has in context is largest, and prioritising the work that closes those gaps. It is a continuous process, not a one-time setup. As the knowledge base grows, the prioritisation changes. As new components are added, new gaps appear. As evidence is curated, the gaps close and new ones become the highest priority.

**The generalisation:** The context engineering question at this layer is: given that you cannot curate everything at once, what is the right order? What metric correctly captures "where the AI system most needs better context for its outputs to be trustworthy"? The answer depends on the domain and the use case — but there is always an answer, and building a system without one means curation effort goes wherever curators happen to look, not where the system most needs it.

### Layer 5: The lifecycle update architecture — context that stays current

The fifth context engineering decision is how the system maintains context quality over time. This is partially addressed in the current implementation (the `--approve` workflow stamps provenance and evidence tier), and partially described as future work in `AI_ASSISTED_CONTENT.md` (the runtime update trigger and document registry).

This is the hardest layer, and the one most commonly neglected. Knowledge domains evolve. New studies are published. Old findings are revised. The regulatory landscape changes. Patient populations are refined. A context architecture that was correctly calibrated at the time of initial curation drifts out of calibration as the domain evolves — and AI systems built on stale context produce outputs that were once trustworthy but are no longer.

The design decisions in this project that address this problem are: the explicit version tracking in `rubric_metadata`, the curator provenance stamps and dates on every evidence entry, the `evidence_tier` as a signal that must be re-validated rather than assumed, and the `prioritise.py` tool that can be re-run at any point to identify which gaps have grown in priority as the rest of the knowledge base has been filled in. These create the infrastructure for lifecycle-aware context management, even though the automated update trigger hasn't been built yet.

The competition context is directly relevant here. A one-day build cannot produce a mature knowledge base. What it can produce — and did — is a context architecture with the right lifecycle properties: it knows what it doesn't know, it labels its inferences as inferences, it prioritises its own gaps correctly, and it is designed to improve gracefully as evidence accumulates. That is more valuable than a mature knowledge base built on an architecture that doesn't handle uncertainty, doesn't prioritise gaps, and treats its initial curation as permanent ground truth.

**The generalisation:** The context engineering question at this layer is: how does this system know when its context has gone stale, and what does it do about it? A system that doesn't answer this question is a snapshot, not a system. The context engineering investment that makes it a system is understanding the update triggers, the re-validation requirements, and the feedback loops that keep context quality calibrated over time.

---

## What "one day" actually demonstrates

The competition constraint — one day to build a system that demonstrates something real — forced a specific set of design choices that are worth examining as a design philosophy.

A one-day build cannot be comprehensive. It must be architecturally sound. If the architecture is wrong, more time makes it worse — it fills the wrong structure with more data, writes more code against incorrect abstractions, and produces more documentation of a design that will need to be thrown away. If the architecture is right, more time simply fills it in — more evidence entries, more pathways, more species comparisons, more generated documents. The value of a correctly designed architecture scales with time; the value of an incorrectly designed architecture does not.

The context engineering choices in this project were made with that constraint in mind. The evidence schema was designed to be sparse but correct — capturing the minimum fields that make AI outputs verifiable rather than the maximum fields that might eventually be useful. The scoring system was designed to be explicit about inference rather than pretending the scores are more confident than they are. The curation workflow was designed to enforce quality on entry rather than relying on post-hoc review. The prioritisation system was designed to direct future effort rather than being built after the knowledge base is mature.

Each of these choices was also a deliberate demonstration. The point is not that Who Gives a Fly is a production system. The point is that these five layers — knowledge schema, evidence lifecycle, scoring/uncertainty representation, gap prioritisation, lifecycle update architecture — are the correct layers to design, in that order, for any knowledge-intensive domain where AI systems will be used for high-stakes decisions. The Rb pathway is the worked example. The architecture is the claim.

---

## Where this pattern applies

Cross-species drug development is one domain with this structure. The general pattern — a knowledge domain where AI assistance is valuable, where the knowledge base is incomplete and growing, where different professional communities need different renderings of the same underlying knowledge, and where the consequences of AI error are serious enough to require structured context rather than training-prior generation — describes many others.

**Clinical guideline development** has the same structure. The knowledge base (clinical trial evidence) accumulates over time. Different stakeholders (guideline committees, clinicians, patients) need different renderings. Uncertainty representation (evidence quality grades like GRADE) is already structured but not yet used systematically as AI context. The context engineering question is whether existing evidence quality frameworks can be mapped to AI context structures that enable appropriate uncertainty propagation.

**Regulatory scientific advice** has the same structure. The relevant knowledge (prior regulatory decisions, applicable guidance documents, precedent cases) is complex, unevenly distributed across sources, and needs to be synthesised for different purposes at different points in the development timeline. Context engineering for regulatory AI systems would mean building structured, versioned, provenance-tracked knowledge bases of regulatory precedent, with evidence tier equivalents that reflect the strength and applicability of each precedent to the current case.

**Precision medicine biomarker development** has the same structure. The knowledge base (genomic associations, functional studies, clinical correlations) accumulates in parallel with patient data. Different team members (molecular pathologists, oncologists, genetic counsellors, patients) need different renderings of the same underlying knowledge. The consequences of wrong outputs are immediate patient harm. The context engineering requirements are the most stringent of any of these domains.

**Environmental risk assessment** has the same structure. The knowledge base (toxicological studies, epidemiological data, mechanistic models) accumulates over decades. Different stakeholders (regulators, industry, communities) need different content. Uncertainty representation is central to regulatory credibility.

In each case, the same five-layer architecture applies. The specific choices within each layer — what the schema captures, what gates knowledge passes through, how uncertainty is represented, how gaps are prioritised, how context is kept current — depend on the domain. But the questions that need to be answered at each layer are the same questions.

---

## The meta-lesson: context engineering is infrastructure, not configuration

The most common mistake in deploying AI systems for high-stakes domains is treating context as configuration — something you set up once, check off, and move past. "We gave the model the relevant documents. We wrote a good system prompt. We did RAG." These are not wrong, but they are insufficient. They treat context as a static input to a static system.

Context engineering, properly understood, is infrastructure. It has the same lifecycle properties as any other critical infrastructure: it requires maintenance as the domain evolves, it degrades if not maintained, it has failure modes that need to be understood and designed around, and its quality determines the quality ceiling of everything built on top of it.

The Who Gives a Fly project was designed as a demonstration of what it looks like to treat context engineering as infrastructure rather than configuration. The schema is versioned. The evidence entries are provenance-stamped. The inference flags are first-class outputs, not footnotes. The gap prioritisation tool runs at any point to assess the current state of context quality. The lifecycle update architecture is designed, even if not fully implemented.

None of this was necessary to produce a working demo for a one-day competition. A working demo only required generating plausible-looking reports. The context engineering infrastructure was built because the point of the competition entry was not to demonstrate that a demo is possible — it is to demonstrate that a trustworthy system is designable. That is a harder thing to show, and it requires actually designing it.

---

## Reading guide for this repository

The five context engineering layers map to the repository documentation as follows:

| Layer | Primary document | Supporting documents |
|-------|-----------------|---------------------|
| 1. Knowledge schema | `config/evidence_schema.json` | `README.md` → Config Files section |
| 2. Evidence lifecycle | `CURATOR_REVIEW_GUIDE.md` | `README_curator_review_section.md` |
| 3. Scoring / uncertainty | `config/translational_risk_rubric_data.json` | `README_risk_scoring_section.md`, `README_inference_and_enrichment_section.md` |
| 4. Gap prioritisation | `prioritise.py` | `README_complete_update.md` → Content Prioritisation |
| 5. Lifecycle architecture | `AI_ASSISTED_CONTENT.md` | `README_enrichment_tools_section.md` |

The biological context that motivates all of this is in `BACKGROUND.md`. The argument for why AI-assisted content generation specifically requires this infrastructure is in `AI_ASSISTED_CONTENT.md`. This document is the meta-level argument about why the infrastructure was designed the way it was, and what that design demonstrates beyond the specific domain.

---

*See also: [BACKGROUND.md](BACKGROUND.md) · [AI_ASSISTED_CONTENT.md](AI_ASSISTED_CONTENT.md) · [README.md](README.md)*
