# Background: The Translational Gap in Drug Development

> *Why promising biology in model organisms so rarely becomes medicine — and what a systematic approach to cross-species divergence can do about it.*

---

## The scale of the problem

Drug development fails at a rate that would be considered catastrophic in almost any other engineering discipline. Of every 10,000 compounds that enter preclinical development, roughly 250 make it to human trials. Of those, approximately 1 succeeds. The overall probability of a compound entering Phase I and eventually reaching approval is around 10% — and for oncology specifically, it falls closer to 5%.

The cost is not only financial. Each failed trial represents years of patient time, regulatory effort, manufacturing scale-up, and opportunity cost for compounds that might have worked. More importantly, it represents patients enrolled in trials for drugs that, in retrospect, had fundamental biological reasons to fail — reasons that were present in the preclinical data but not recognised.

The question this project addresses is a specific one: of all the reasons drugs fail in humans, how many are attributable to species-specific biology that was present in the model organism data but never systematically characterised?

The answer, from the available evidence, is: a lot.

---

## What the preclinical pipeline was designed to establish — and what it wasn't

Preclinical development serves several purposes. It establishes that a compound has biological activity against a target (pharmacodynamics), that it reaches the target at effective concentrations (pharmacokinetics), and that it does not produce unacceptable toxicity at anticipated therapeutic doses (safety). These are the core requirements for an IND application to the FDA, and the preclinical package is structured around demonstrating them.

What the preclinical pipeline was not designed to do is characterise the degree to which the biology of the target — the pathway it operates in, the regulatory context that controls its activity, the downstream effectors it governs — is equivalent between the model organism and the patient. This is assumed rather than measured. The assumption is that if a gene is conserved enough to produce a relevant phenotype in a mouse or a fly, the pathway it operates in is conserved enough that a drug hitting that gene will produce the same therapeutic outcome in a human.

This assumption is often wrong, and wrong in specific, predictable ways that are not random.

---

## Where the gap actually lives: three categories of species-specific failure

### 1. Target biology divergence

The most direct failure mode is that the molecular target itself behaves differently in the human disease context than in the model. This is distinct from poor sequence conservation — it can occur even when the protein sequence is nearly identical, if the regulatory context has diverged.

The INK4 family illustrates this sharply. *Drosophila* has no INK4 homologs. The four human INK4 proteins (p16^INK4a, p15^INK4b, p18^INK4c, p19^INK4d) are critical nodes connecting TGF-β signalling, oncogene-induced senescence, and CDK4/6 regulation. A drug screen in fly cells that identifies CDK4 inhibitors as anti-proliferative is testing a simplified circuit that lacks the regulatory inputs most relevant to human cancer. When that compound moves to a patient whose tumour has lost p16 specifically — a near-universal event in many cancers — the predictive relationship between the fly result and the clinical outcome has already broken down.

This is not a flaw in the fly as a model organism. It is a known, characterised divergence that should inform how fly results are weighted and what bridging experiments are required before clinical development.

### 2. Paralog compensation

Gene family expansion across evolution creates a systematic trap. When a human gene family has multiple paralogs with partially overlapping functions, a model organism experiment using a single ancestral gene — or using one family member — may not predict what happens when a drug hits all family members simultaneously in a patient.

Cyclin D is a clean example. Flies have a single Cyclin D. Humans have Cyclin D1, D2, and D3 with distinct tissue-specific expression patterns and partially distinct CDK-binding preferences. A compound that disrupts fly Cyclin D activity will be tested in human clinical development against tumours that may depend differentially on Cyclin D1 amplification (breast), Cyclin D2 upregulation (multiple myeloma), or Cyclin D3 expression (T-cell lymphoma). The single-gene fly result does not resolve which paralog is the driver, and the drug may behave differently in each tumour subtype in ways that were not predicted.

Mouse models partially address this, since mice have all three Cyclin D paralogs — but paralog compensation during development (where knockout of one member is rescued by upregulation of another) can mask somatic phenotypes that are relevant to cancer but not to embryogenesis.

### 3. Regulatory rewiring

The most underappreciated failure mode is regulatory rewiring: the target gene is conserved, the phenotype is conserved, but the upstream signals that control the target, and the downstream targets it controls, are different between species. A drug that modulates the target in the model organism may produce a clinical effect in humans, but via different effector genes, in different tissues, with different feedback loops engaged.

Rb1 illustrates this. The pocket protein family function — binding E2F transcription factors to suppress cell cycle entry — is deeply conserved from flies to humans. But the regulatory inputs are not equivalent. TGF-β → p15^INK4b → CDK4/6 → Rb is a central tumour suppressor axis in human epithelial cancers, absent in fly entirely. Mitogen signalling converges on Cyclin D through different intermediates. The feedback between E2F targets and DNA damage response involves ARF/MDM2/p53 in mammals, a circuit present in simplified form in fly but substantially different in its connectivity. A drug that produces Rb pathway activation in a fly model is working through a different set of upstream and downstream connections than the same drug would engage in a patient.

None of these divergences makes the fly result wrong. It makes the fly result *differently informative* — and the question of which aspects of the result transfer to humans, and which do not, is precisely what systematic cross-species analysis is designed to answer.

---

## What happens between preclinical data and the IND application

An IND application to the FDA requires, at minimum: a summary of the compound's pharmacological basis for use, a detailed description of prior human experience (if any), information on manufacturing and stability, and a clinical protocol with safety monitoring plan. The scientific basis is the pharmacology package.

The pharmacology package is where species-specific biology should be caught — and where it most often isn't. The package demonstrates efficacy in a rodent model and typically one non-rodent model (often primate for toxicology). It does not require systematic characterisation of target pathway biology across species. The FDA's guidance on pharmacology/toxicology INDs asks whether the drug works and whether it is safe in animals. It does not ask: does the pathway the drug targets function equivalently between your model organism and the intended patient population?

This gap exists for understandable regulatory reasons — the IND is a gateway to early-phase human trials, not a definitive efficacy package. The biological plausibility of the mechanism is assumed if the preclinical activity is demonstrated. But it means that systematic species-specific divergences are never formally characterised as part of the regulatory pathway. They emerge instead as unexplained Phase II failures, negative biomarker correlations, and retrospective mechanistic analyses of why the biology didn't translate.

### The specific stages where divergence surfaces — and when it should have been caught

| Stage | Where divergence appears | When it should have been caught |
|-------|--------------------------|--------------------------------|
| Target identification | Pathway member selected based on model organism screen | Before screen design — which paralogs are present, which are relevant? |
| Lead optimisation | Compound potency optimised against model organism target | At structure selection — does human ortholog have same binding site? |
| Mechanism of action studies | MOA established in cell lines or model organism | At MOA characterisation — which pathway connections are conserved? |
| In vivo efficacy | Tumour regression observed in mouse xenograft | At model selection — does the xenograft recapitulate human tumour genetics? |
| IND-enabling studies | Tox established in rodent/non-rodent | At species selection for tox — is the metabolic pathway equivalent? |
| Phase I | PK/PD relationship established in humans | At trial design — are human PD markers equivalent to model PD markers? |
| Phase II | Efficacy signal absent or weaker than predicted | Too late — this is retrospective discovery of preclinical failure |

The pattern is consistent: divergences that could have been characterised at the biology stage are instead discovered at the clinical stage, after substantial investment. The earlier in this sequence the divergence is identified, the lower the cost — in money, in time, and in patient exposure to ineffective treatment.

---

## Why existing approaches don't systematically solve this

Several tools exist that partially address cross-species biology. None of them do what this project does.

**Ortholog databases** (DIOPT, OrthoFinder, Ensembl Compara) identify whether a human gene has a counterpart in a model organism and compute sequence identity. They answer: is the gene there, and how similar is the protein? They do not answer: does the pathway it operates in function equivalently? Does the regulatory context transfer? Has the gene been validated as a disease model?

**Pathway databases** (KEGG, Reactome, WikiPathways) describe pathway topology for human biology and, to varying degrees, for model organisms. They are rarely maintained with the specificity needed to capture species-specific differences in regulatory inputs, paralog-specific expression, or PTM site conservation. They describe canonical pathways, not divergences from canon.

**Literature curation** captures individual experimental results — a mouse knockout phenotype, a drug response in fly cells, a rescue experiment. It does not aggregate these results into a scored, comparable framework across species and pathways. A researcher planning a drug development program has no systematic way to query what is known about a target pathway's conservation across species without reading hundreds of papers and synthesising them manually.

**Standard pharmacology packages** for IND applications characterise the compound's behaviour in animals. They do not characterise the target pathway's species-specific biology independently of the compound. The assumption embedded in every IND package is that the model organism is an adequate proxy for human pathway biology. This assumption is tested implicitly by the trial, not explicitly before it.

What is missing is a framework that systematically characterises pathway conservation across species — not just sequence identity, not just pathway membership, but the full biological context: regulatory inputs, downstream effectors, PTM sites, tissue expression, paralog landscape, and experimental phenotypic evidence — scored and integrated into a translational risk assessment that can inform go/no-go decisions before IND filing.

---

## What the Rb pathway tells us about the general problem

The Rb pathway is the best-characterised tumour suppressor pathway in cancer biology and an ideal case study precisely because its divergences are so well-documented. If systematic cross-species analysis catches known divergences — the absent INK4 family in fly, the TGF-β input absent in invertebrates, the Cyclin D paralog expansion, the tissue-specific Rb family member usage — then it is doing something real. The divergences are not hypothetical; they have direct clinical consequences documented in the literature.

CDK4/6 inhibitors are FDA-approved for RB1-intact breast cancer. They fail in RB1-deleted cancers entirely. The fly, which has no INK4 and runs Rb regulation through a simpler circuit, cannot predict RB1 deletion status as a response biomarker — not because flies are a bad model, but because the specific regulatory axis that makes RB1 status clinically relevant does not exist in fly. A translational risk assessment that flags `ink4_family` as a Critical Gap for fly, and correctly notes the absence of TGF-β upstream signalling, is capturing exactly the biology that matters for clinical trial design.

The same analysis applied to mouse would flag different issues: Rb1 knockout lethality means adult somatic cancer phenotypes must be modelled with conditional alleles, and the pituitary/thyroid tumour spectrum of heterozygous mice doesn't match the retinoblastoma/osteosarcoma human phenotype. These are known, documented divergences. The value of the framework is not that it discovers them — it is that it collects them in a structured, queryable, scored format that can be applied systematically across pathways and species pairs, and updated as new evidence accumulates.

---

## How this connects to IND planning specifically

An IND application is not the endpoint of preclinical development — it is the gateway. But the decisions that determine whether Phase II will succeed are mostly made before the IND is filed: which target, which patient population, which biomarker, which species for toxicology, which model for the efficacy claim. These decisions are currently made with incomplete information about cross-species pathway biology.

The translational risk scores produced by this system are designed to be inputs to those decisions:

- A 💀 Critical risk score for a pathway component in a given model organism is a signal that the model cannot answer the clinical question being asked — not that the model is useless, but that a different model or orthogonal validation is required before the IND efficacy claim can stand.
- A ⚠️ Moderate risk score for D3 (regulatory context) flags that the drug may work through different mechanisms in the patient than in the model, and that a mechanistic biomarker study should be part of the IND-enabling work.
- A 🚫 High risk score for D4 (phenotypic validity) combined with a strong D1 (sequence conservation) score is the classic CDK4/6 inhibitor pattern — the protein is conserved, the drug binds, but the disease phenotype doesn't fully translate. It is a signal to add a human-relevant model (patient-derived organoids, iPSC-derived cells, or CRISPR-corrected cell lines) to the efficacy package.

None of this replaces animal studies. It complements them by making the interpretation of animal data more rigorous — and by flagging, before the IND is filed, which species-specific assumptions are embedded in the preclinical efficacy claim and whether they are supported by evidence.

---

## Summary

The translational gap between preclinical biology and clinical success has multiple causes, but a significant and underappreciated one is the systematic failure to characterise target pathway biology across species as part of the preclinical development process. This failure is not random — it is concentrated in specific, predictable categories: target biology divergence (regulatory context that doesn't transfer), paralog compensation (gene family complexity that model organisms don't replicate), and regulatory rewiring (same gene, different pathway connections).

The current IND process does not require this characterisation. The pharmacology package demonstrates that the drug works in animals; it does not demonstrate that the biology of the target pathway is equivalent between the animal and the patient. That gap is left for clinical trials to discover — expensively, slowly, and with direct patient impact.

This project proposes that the gap is mappable in advance. Cross-species pathway analysis — systematic, scored, evidence-based, and integrated across sequence conservation, paralog landscape, regulatory context, phenotypic validity, and therapeutic evidence — can identify translational risks before IND filing and inform better preclinical study design, species selection, biomarker strategy, and go/no-go decisions.

The Rb pathway is the first test case. The framework is designed to generalise.

---

*See also: [README.md](README.md) for pipeline documentation · [CURATOR_REVIEW_GUIDE.md](CURATOR_REVIEW_GUIDE.md) for evidence standards*
