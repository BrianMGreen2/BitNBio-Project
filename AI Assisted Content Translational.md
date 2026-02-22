# AI-Assisted Content for Multidisciplinary Translational Teams

> *Why bridging the preclinical-to-clinical gap requires custom-synthesised content, not just better data — and what makes AI assistance trustworthy enough to use in that context.*
>
> READ THIS FIRST: [CONTEXT_ENGINEERING.md](CONTEXT_ENGINEERING.md) for a discussion on how to design architecture correctly for a domain where the knowledge base is always incomplete and always growing.
---

## The content problem that precedes the biology problem

BACKGROUND.md describes why the translational gap exists at the biological level: species-specific pathway divergences that are predictable, mappable, and consequential — but not systematically characterised as part of the current drug development process.

There is a second problem that sits upstream of the biology. Even when the divergences are characterised, the people who need to act on them cannot easily use the information. This is not a failure of intelligence or expertise. It is a structural mismatch between how biological knowledge is produced and what different members of a drug development team actually need to read and act on.

A translational scientist working in fly genetics and a clinical trial physician designing an oncology protocol are not reading the same literature, using the same vocabulary, asking the same questions, or making the same kinds of decisions. The cross-species pathway analysis this system produces is scientifically rigorous and carefully sourced — but a JSON risk assessment record, a conservation heatmap, or even a well-structured Markdown report is not what a clinical pharmacologist needs when they are deciding whether the preclinical efficacy data supports a particular patient selection biomarker. It is not what a regulatory affairs specialist needs when they are drafting the pharmacology section of an IND. It is not what a clinical operations team needs when they are designing inclusion criteria for a Phase I dose escalation study.

The content that actually bridges these communities does not yet exist in any systematic way. It has to be synthesised — from the scientific record, the risk assessment, the pathway data, and an understanding of what each audience needs to know and in what form. That synthesis has historically required either a rare individual who can operate fluently across all these domains, or a committee of specialists who meet repeatedly to translate between them. Both approaches are slow, expensive, and do not scale.

This is where AI-assisted content generation becomes genuinely useful — not as a replacement for domain expertise, but as the synthesis layer that takes structured, validated, scored biological knowledge and renders it into the specific content each member of a multidisciplinary team needs.

---

## What multidisciplinary teams actually need — and why it differs by role

The preclinical-to-clinical transition involves at minimum six distinct professional communities, each with different questions, different decision authorities, and different tolerances for uncertainty.

**Basic scientists and translational researchers** need to understand which aspects of their model organism findings are likely to hold in humans and which are model-specific artefacts. They need this framed in molecular terms: which pathway connections transfer, which do not, and what bridging experiments would close the gap. They are comfortable with biological complexity and uncertainty — they need precision, not simplification.

**Clinical pharmacologists** need to know how target pathway biology in the model organism predicts PK/PD relationships in patients. They need to understand whether the biomarkers used to assess drug effect in the preclinical model are likely to function as equivalent PD markers in humans — whether the same proteins are expressed in the right tissues, whether the same feedback loops are engaged, whether the dose-response relationship is likely to be similar. They think in terms of mechanism, exposure, and effect.

**Clinical trial physicians and investigators** need to understand which patient populations the preclinical data actually supports enrolling, what the biological rationale for inclusion and exclusion criteria is, and what to watch for as evidence of on-target versus off-target toxicity. They need the biology translated into clinical terms: what does a D3 regulatory context mismatch mean for the expected safety profile? What does a High Risk D4 score mean for which tumour subtypes to prioritise in the dose escalation cohort?

**Regulatory affairs specialists** need to understand the scientific rationale well enough to draft and defend it in IND submissions and FDA meetings. They need content that is precise, evidenced, and structured around regulatory expectations — not narrative science writing, but defensible scientific argument in the format regulators expect. They need to know what the preclinical package demonstrates, what it does not demonstrate, and how to characterise the gap honestly without undermining the programme.

**Clinical operations and data management teams** need to understand the biological basis of the protocol well enough to design data collection instruments, define endpoints, and build the operational infrastructure around the trial. They are often the least scientifically specialised and the most operationally sophisticated — they need the biology translated into decision rules, not mechanisms.

**Biostatisticians and data scientists** need to understand the biological hypotheses well enough to design the analysis plan. They need to know which comparisons are primary versus exploratory, which biomarkers are pre-specified versus post-hoc, and what the power assumptions are based on — which in turn requires understanding the quality of evidence underlying the preclinical effect sizes.

None of these audiences can simply be handed the same document. Each needs a different synthesis of the same underlying biological knowledge. And because the underlying knowledge is structured, scored, and sourced — as it is in this system — that synthesis can be performed systematically rather than ad hoc.

---

## Why AI is specifically suited to this problem — and what it requires to be trusted

Large language models have a genuine capability that is directly relevant here: they can take structured information in one form and render it in another form appropriate for a different audience, at scale, without losing the substance. This is exactly the synthesis problem described above. Given a risk assessment record, a pathway annotation, a set of evidence entries, and a specification of the target audience and decision context, a capable model can produce a biologically accurate, appropriately framed, audience-specific document.

This capability is real. But it is also, without constraints, dangerous in a drug development context. The consequences of a plausible-sounding but scientifically incorrect document in a regulatory submission or a clinical protocol are serious. The constraints that make AI-assisted content generation trustworthy in this domain are not peripheral — they are the core design requirement.

There are three of them.

### 1. The right context: grounding every output in structured, validated knowledge

An AI model generating content about cross-species pathway biology without access to curated, scored, sourced knowledge will draw on its training data — which is a mixture of high-quality literature, lower-quality secondary sources, outdated reviews, and knowledge that ends at a training cutoff. It will produce content that sounds authoritative but may be wrong in specific ways that are difficult for a non-specialist to detect.

The solution is not to avoid AI generation. It is to ground every generation call in a specific, validated, structured knowledge base. In this system, that knowledge base is `pathways.json` augmented by validated evidence entries — data that has been curated by domain experts, checked against primary sources with PMIDs, scored against explicit criteria, and approved through a structured review workflow. The AI model's role is to synthesise and render this information, not to supply it.

This distinction matters enormously. A document generated by an AI model that has been given the validated regulatory context entry for RB1/Drosophila, the phenotypic evidence entries with their scores and caveats, the pharmacological evidence entries with their concordance assessments, and the relevant risk score with its override and modifier flags — and asked to produce a clinical pharmacologist's briefing on what the Drosophila data does and does not support — is doing something categorically different from a model that is simply asked "what does fly biology tell us about RB1 inhibition?". The first is synthesis of validated information. The second is generation from training priors, which may be outdated, incomplete, or wrong.

The infrastructure built in this project — the structured evidence schema, the curation workflow, the evidence tiers, the PMID requirements — is not incidental scaffolding. It is what makes AI-assisted content generation trustworthy. Every evidence entry that makes it through `validate_evidence.py --review` and `--approve` becomes part of the grounding context that can be passed to a generation step. The quality of the generated content is bounded by the quality of the curated knowledge base.

### 2. Runtime validation: checking generated content against the structured record

The second constraint is that generated content must be checkable against the structured record it was generated from, and that checking must happen automatically rather than relying on human review alone.

The specific failure mode this addresses is confabulation — where a model generates plausible-sounding text that is inconsistent with the source material, either by adding claims not present in the source, modifying quantitative values, or omitting caveats that are present in the source. In a clinical document, each of these failures is consequential.

Runtime validation works by treating the structured evidence record as the authority and checking every quantitative claim, every risk level, every scored assessment, and every caveat flag in generated content against the source. This is technically straightforward when the source is structured: a generated document that says "CDK4/6 inhibitor response is concordant between mouse and human" can be checked against the `concordance` field in the pharmacological evidence entries. A generated document that says "the INK4 family is moderately conserved in Drosophila" can be checked against the D1 score of 0 and the OR-01 override. A generated document that omits the caveat about Rb1 knockout lethality can be detected by checking whether the `caveats` field from the corresponding phenotypic evidence entry was included.

What this requires from the system is that the structured record is specific enough to make these checks possible. Vague annotations — "some divergence exists" — cannot be validated against generated text. The precision requirements in the evidence schema, the mandatory `caveats` fields, the score-PMID consistency rules in the scientific review — these are not bureaucratic overhead. They are what enables runtime validation of generated content.

The practical implementation is a generation-validation loop: the AI model generates a document, a validation function checks it against the structured record, discrepancies are flagged and either corrected automatically or surfaced for human review, and the validated document is the output. The validation function does not need to understand biology — it needs to match structured fields to generated text, flag numerical inconsistencies, and verify that required caveats are present. That is an engineering problem, not a biological one.

### 3. Appropriate scoring criteria: knowing when a generated document is good enough

The third constraint is the most subtle. "Good enough" means different things for different audiences and different decisions. A document used to brief a clinical investigator on patient selection rationale does not need to meet the same standard as a document used in an IND submission. A document that synthesises three validated evidence entries and one inferred score should be labelled differently than a document that synthesises ten validated entries with no inference. The confidence level of the underlying evidence should propagate into the generated content and be visible to the reader.

This is the direct connection to the `evidence_tier` system built into `risk_scorer.py`. When a generated document draws on assessments where all five dimensions are ground-truth scored (`evidence_tier: "validated"`), the document can assert those scores with confidence and the generated text should reflect that. When it draws on assessments where three dimensions are inferred (`evidence_tier: "partial"` or `"inferred"`), the generated text should communicate that uncertainty explicitly — not as a disclaimer buried in a footnote, but as a substantive qualification of the claims being made.

The scoring criteria for generated content, then, are not just about whether the text is accurate to the source — they are about whether the text correctly represents the confidence level of the source. A document that says "RBF1 is a reliable model for human RB1 biology" when the underlying D4 score is inferred and the D3 score flags regulatory rewiring is inaccurate to the source even if every individual claim it makes could be found somewhere in the literature. It has promoted an uncertain inference to a confident assertion.

The validation function needs to check not just factual accuracy but confidence propagation: does the generated document's register of certainty match the evidence tier of the data it was generated from?

---

## What AI-assisted content generation looks like in practice

Given these three constraints, the workflow for generating a multidisciplinary briefing document looks like this:

**Step 1: Select the target audience and decision context.** Who is reading this? What decision are they making? What information do they need and what level of biological detail is appropriate? This selection maps to the `education_level` settings already present in `settings.json` (undergraduate / graduate / clinical), but for multidisciplinary team content it extends further: a clinical trial physician needs a different rendering than a graduate-level researcher even within the "clinical" education level.

**Step 2: Assemble the grounding context.** For the pathway, component, and species pair in question, collect: the validated evidence entries from `pathways.json`, the risk assessment record from `risk_scorer.py` including all dimension scores, applied overrides and modifiers, and raised flags, and the `evidence_tier` for each dimension. This is the structured knowledge base the AI model will synthesise from. Nothing beyond this structured record should enter the generation step as a factual claim.

**Step 3: Generate with explicit constraints.** The prompt to the AI model specifies the target audience, the decision context, the content structure expected, and — critically — the instructions for handling uncertainty: inferred dimensions must be labelled as estimates, override flags must be surfaced and explained, caveats must be included where the evidence record includes them, and the confidence register of the generated text must match the `evidence_tier` of the underlying data.

**Step 4: Validate against the structured record.** Check every quantitative claim, risk level, and caveat against the source. Flag discrepancies. Verify that the overall confidence register of the document matches the evidence tiers. Return any failed checks for correction before the document is released.

**Step 5: Label and version the output.** Every generated document should carry: the date of generation, the evidence tier of the underlying data, the version of the rubric used for scoring, and a note of which dimensions were ground-truth scored versus inferred. This is the audit trail that makes the document defensible in a regulatory context and trustworthy to a clinical reviewer.

---

## The documents that can be generated from this system today

Even at the current state of evidence curation — all D3/D4/D5 dimensions inferred, D1/D2 enriched from Ensembl — the system can produce useful content for several audiences, clearly labelled with its evidence tier.

**Model organism selection briefings** — which model organisms are appropriate for which research questions about this pathway, why, and what the specific limitations are for each. Actionable for research teams choosing experimental systems. Grounded in D1/D2 Ensembl enrichment data (reliable) and D3 regulatory context annotations (inferred, labelled as such).

**Translational risk summaries** — a plain-language explanation of the risk scores for each pathway component, what the flags mean in biological terms, and what bridging experiments or orthogonal validations would reduce the risk level. Actionable for preclinical-to-clinical transition meetings. Grounded in the full five-dimension risk assessment.

**IND section drafts** — structured text for the pharmacological basis of use section of an IND application, synthesising the preclinical evidence base with explicit characterisation of its cross-species translation assumptions. These require fully validated D4 and D5 scores before they can be filed, but even at `evidence_tier: "partial"` they provide a useful draft structure and identify the evidence gaps that need to be filled before submission.

**Clinical trial design considerations** — for each component with a high or critical risk score, what does the risk imply for patient selection, biomarker strategy, and endpoint selection? Which risk flags are relevant to which aspects of trial design? Actionable for the clinical team. Requires at minimum validated D4 scores for the relevant species comparison.

**Investigator briefing documents** — for each model organism study cited in the clinical rationale, what does the cross-species analysis say about how much confidence to place in the result, and why? Grounded in phenotypic evidence entries and their caveats. Requires validated D4 entries to be fully trustworthy; useful even with inferred scores when clearly labelled.

---

## What needs to be built

The three constraints — right context, runtime validation, appropriate scoring — define the engineering requirements for a full AI-assisted content generation layer. The structured knowledge base and scoring system are already built. What remains:

**A generation module** that takes a pathway, component, species pair, target audience specification, and decision context, assembles the grounding context from validated data, constructs a structured prompt with confidence-propagation instructions, calls an AI model, and returns a draft document. This module should be callable from the pipeline and should integrate with the existing `education_level` settings.

**A validation module** that takes a generated document and its source evidence record, extracts quantitative claims and risk labels from the text, checks them against the structured record, verifies that caveats present in the source are present in the document, and assesses whether the confidence register of the text matches the evidence tier. Returns a validation report with any discrepancies flagged.

**A runtime update trigger** connected to the curation workflow: when a new evidence entry is approved via `validate_evidence.py --approve`, any generated documents that drew on the affected component should be flagged for regeneration, because the grounding context has changed. This prevents stale documents from circulating after the knowledge base has been updated.

**A document registry** that tracks which generated documents exist, what version of the knowledge base they were generated from, what their current validation status is, and whether they need regeneration. This is the audit trail that makes the system defensible in regulatory contexts.

---

## Why this is not a replacement for expert judgment

The purpose of AI-assisted content generation is not to remove experts from the process. It is to remove the bottleneck that currently prevents experts from doing their highest-value work.

Right now, a translational scientist who has spent years characterising the Rb pathway in Drosophila spends significant time producing documents — briefings, summaries, protocol rationale sections — that translate their expertise into formats other team members can use. This is necessary work, but it is not the work they are uniquely positioned to do. The work they are uniquely positioned to do is curating the evidence: reading the primary literature, evaluating experimental quality, making the scientific judgments that determine whether a study's findings are valid and what their caveats are. That judgment cannot be automated. The synthesis that renders those judgments into audience-specific documents can be.

The curation workflow built into this system — the evidence template, the schema validation, the scientific review, the approval gate — is where expert judgment is concentrated and preserved. Every piece of expert knowledge that passes through that workflow becomes reusable, version-controlled, and auditable. The AI generation layer draws on it without diluting it.

The constraint that makes this sustainable is that expert judgment is required to *enter* the knowledge base, not to *exit* from it as documents. A clinical pharmacologist reviewing a generated briefing document is checking the synthesis, not supplying the biology. A regulatory affairs specialist reviewing a generated IND section is editing for regulatory precision, not rewriting the science from scratch. The experts are still in the loop — they are just in the loop at the point where their expertise is actually required.

---

## A note on the current state of this system

The AI-assisted content generation layer described in this document does not yet exist as implemented code. The infrastructure that would make it trustworthy — the structured knowledge base, the evidence schema, the curation workflow, the scoring engine, the evidence tier system, the runtime validation checks — does exist and is documented throughout this repository.

This document is both an explanation of what is needed and a design specification for what comes next. The three constraints — right context, runtime validation, appropriate scoring criteria — are not aspirational principles. They are implementable engineering requirements that build directly on what has already been built. The generation module calls an AI model with a structured prompt assembled from validated pathways.json data. The validation module checks generated text against the same structured record. The update trigger connects to the existing `--approve` workflow. The document registry is a new JSON database.

None of it is scientifically novel. All of it is necessary. And the reason it is necessary is not that AI generation is powerful — it is that the alternative is a bottleneck that prevents the biological knowledge encoded in this system from reaching the people who need it to make better decisions about which drugs to develop, how to design the trials, and which patients to enrol.

---

*See also: [BACKGROUND.md](BACKGROUND.md) for the translational gap problem · [README.md](README.md) for pipeline documentation · [CURATOR_REVIEW_GUIDE.md](CURATOR_REVIEW_GUIDE.md) for evidence standards*
