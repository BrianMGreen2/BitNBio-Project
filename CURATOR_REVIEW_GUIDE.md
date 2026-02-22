# Curator Review Guide
## Who Gives a Fly — Evidence Curation Standards

> Version 1.0 · Applies to: `phenotypic_evidence`, `pharmacological_evidence`, `regulatory_context`

---

## Why this document exists

`validate_evidence.py --check` enforces structure: required fields are present, types are correct, enums are valid. It does not enforce science. A curator could submit a score of 5/5 citing a single unpublished cell-line observation, the schema would accept it, and the scoring engine would treat it as ground truth indistinguishable from a score backed by three independent in vivo studies with human gene rescue.

This guide defines the decision criteria that sit between schema validity and approval. Every `--approve` action should be preceded by working through the relevant checklist below. The criteria here are also implemented as automated consistency warnings in `validate_evidence.py --review` (see Appendix), which catches the most common score-evidence mismatches before human review begins.

---

## The core principle: score must be justified by the weakest evidence that would support it

Scores are not averages. They represent the *strongest defensible claim* the existing evidence permits. This means:

- A score of 5 requires that every criterion for 5 is met, not just most of them.
- A single contradicting study can prevent a score even if ten supporting studies exist — it must be documented in `caveats` and factored into the score.
- When evidence is genuinely ambiguous, score down, not up. Uncertainty belongs in the risk assessment, not hidden in an inflated score.

The questions below operationalise this principle for each evidence type.

---

## Part 1 — Phenotypic Evidence (D4)

D4 asks: *has this model organism been experimentally shown to recapitulate the human disease phenotype when this gene is manipulated?*

### Score decision criteria

Before assigning any score, answer these questions in order. The first "no" answer caps your maximum score.

**Gate 1 — Is there a published, peer-reviewed study?**

| Answer | Score ceiling |
|--------|--------------|
| Yes, in a peer-reviewed journal with accessible full text | No cap from this gate |
| Yes, preprint only (bioRxiv/medRxiv) | Maximum 3 — downgrade when published version available |
| No — unpublished, conference abstract, or personal communication | Maximum 2 — flag with `evidence_tier: "ai_candidate"` pending publication |
| No primary data at all | Score 1 (predicted only) |

**Gate 2 — Is the experimental system in vivo or in vitro?**

| System | Score ceiling |
|--------|--------------|
| In vivo: whole animal, tumour model, or xenograft | No cap from this gate |
| Ex vivo: organoids, primary patient-derived cells | Maximum 4 |
| In vitro: established cell lines only | Maximum 3 |
| Computational / bioinformatic only | Maximum 2 |

*Rationale: cell lines are genetically unstable, lack tissue context, and frequently have additional mutations that confound single-gene phenotype interpretation. An RB1 knockout phenotype in a retinoblastoma cell line is not equivalent to an Rb1 knockout in a whole animal.*

**Gate 3 — Does the phenotype match the human disease, not just any phenotype?**

The model organism must recapitulate the *disease-relevant* phenotype, not merely show that the gene does something when manipulated.

| Match | Score ceiling |
|-------|--------------|
| Equivalent: same tissue, same developmental stage, same endpoint (tumour type, cell cycle arrest, apoptosis) | No cap |
| Partial: same pathway outcome but different tissue or developmental stage | Maximum 4 |
| Different: abnormal phenotype but not the human disease phenotype | Maximum 2 |
| Opposite: manipulation produces the reverse of the expected human phenotype | Score 0, `supports_validity: false` |

*Example: Rb1 heterozygous mouse develops pituitary tumours, not retinoblastoma. This is a partial match for RB1 loss-of-function cancer biology but a different match for retinoblastoma specifically. Score 3, not 4. Document in `caveats`.*

**Gate 4 — Has human gene rescue been demonstrated?**

| Evidence | Score modifier |
|----------|---------------|
| Human gene fully rescues model phenotype (published) | +1 to score, maximum 5 |
| Partial rescue demonstrated | Note in `description`, no score change |
| Rescue not tested | No penalty, but score cannot reach 5 on D4 alone without this |
| Rescue tested and failed | Score 0 for rescue entry, `supports_validity: false` |

**Gate 5 — How many independent studies?**

| Replication | Score modifier |
|-------------|---------------|
| ≥3 independent labs, consistent findings | Confirms score |
| 2 independent labs | Confirms score if consistent |
| 1 lab, ≥2 independent experiments in same paper | Score as submitted, note single-lab limitation in `caveats` |
| 1 experiment in 1 paper | Maximum 3, regardless of experimental quality |
| No replication possible to assess | Note in `caveats` |

### Score-to-evidence mapping (D4)

| Score | Minimum evidence required | Typical entry count |
|-------|--------------------------|---------------------|
| 5 | In vivo model + equivalent phenotype + human gene rescue + ≥2 independent studies | 3–5 entries |
| 4 | In vivo model + equivalent or partial phenotype + either rescue OR drug concordance + published | 2–3 entries |
| 3 | Published in vivo or high-quality ex vivo + some phenotypic overlap + single lab acceptable | 1–2 entries |
| 2 | In vitro only, or in vivo with substantially different phenotype, or preprint | 1 entry |
| 1 | No experimental data — pathway membership or sequence homology only | 0 entries (inferred) |
| 0 | Experimental evidence of non-equivalence or opposite phenotype | 1+ contradicting entries, `supports_validity: false` |

### Common D4 errors to catch in review

**Score inflation:** Assigning 4 or 5 based on a single cell-line study. Gate 2 caps this at 3.

**Phenotype conflation:** Recording that "the gene is expressed and functional" as evidence of disease model validity. Expression ≠ phenotypic equivalence.

**Missing caveats:** Rb1 KO lethality, different tumour spectra, tissue-specific expression mismatches, and compensating paralog effects must all be captured in `caveats`. A score without caveats for a known-complex component is a red flag.

**Rescue omission:** If a human gene rescue experiment exists for this component, it must be captured as a separate entry even if the main knockout entry is already committed. Rescue entries are the strongest individual evidence type and are used by the modifier rule MR-01 (+0.10 to composite).

---

## Part 2 — Pharmacological Evidence (D5)

D5 asks: *does drug or intervention response in the model organism predict what happens in humans?*

The key distinction from D4 is that D5 is about *mechanism*, not just phenotype. A drug can produce tumour regression in a mouse through a different mechanism than it works in humans — convergent pharmacology — and still fail clinically. The concordance field must reflect whether the mechanism is conserved, not just whether the endpoint matched.

### Score decision criteria

**Gate 1 — What is the clinical development stage of the drug?**

| Stage | Score ceiling |
|-------|--------------|
| Approved (any indication) | No cap |
| Phase 3 | Maximum 4 |
| Phase 2 | Maximum 3 |
| Phase 1 or preclinical only | Maximum 3 |
| No clinical data | Maximum 2 |

**Gate 2 — Is the mechanism confirmed in the model, not just the endpoint?**

| Mechanism evidence | Score modifier |
|-------------------|---------------|
| On-target mechanism confirmed (target engagement assay, rescue by resistant allele, etc.) | Confirms score |
| Mechanism assumed from phenotype match — not confirmed | Cap at 3, document in `notes` |
| Off-target effects documented or suspected | Score 2 regardless of endpoint |

*Example: palbociclib causes cell cycle arrest in Drosophila Cdk4 models, but without a kinase-dead rescue experiment, it is not confirmed to act via the same CDK4 mechanism as in humans. Score 3, not 4, until mechanism is confirmed.*

**Gate 3 — Is concordance direct or inferred?**

`concordance: true` means the model drug response has been directly compared to human clinical data or a human cell system in the same study or a direct follow-up. It does not mean "the drug works in the model AND the drug is approved in humans" — that is circumstantial concordance and belongs in `notes`, not `concordance: true`.

| Concordance basis | `concordance` value | Score ceiling |
|-------------------|--------------------|----|
| Direct comparison in same study | `true` | No cap |
| Sequential studies from same lab, consistent | `true` | No cap |
| Drug works in model; also clinically approved — no direct comparison | `null` | Maximum 3 |
| Drug works in model; fails in humans for this target | `false` | Score 0, triggers OR-03 |
| Unknown / not tested | `null` | Maximum 2 |

**Gate 4 — Evidence type hierarchy**

| Evidence type | Score ceiling |
|--------------|--------------|
| `approved_use` — drug approved targeting this gene | 5 if mechanism confirmed |
| `clinical_trial` — active trial, gene is target | 4 |
| `in_vivo` — animal model study, endpoint measured | 4 |
| `ex_vivo` — patient-derived organoids or PDX | 3 |
| `in_vitro` — cell lines | 2 |
| `drug_screen` — unvalidated screen hit | 2 |

### Score-to-evidence mapping (D5)

| Score | Minimum evidence required |
|-------|--------------------------|
| 5 | Approved drug, model response directly compared to clinical outcome, mechanism confirmed |
| 4 | Clinical-stage drug OR confirmed in-vivo mechanism with strong phenotypic concordance |
| 3 | Preclinical in-vivo data, drug active in model, mechanism plausible but unconfirmed |
| 2 | In-vitro only, or mechanism unclear, or circumstantial clinical association |
| 1 | No pharmacological data for this gene in this species |
| 0 | Documented discordance: drug fails in humans for this target, or is inactive in model |

### Common D5 errors to catch in review

**Conflating approval with concordance:** A drug approved for a human cancer does not automatically mean the model recapitulates the drug's mechanism. Palbociclib is approved for RB1-intact breast cancer; using this to score `concordance: true` for a fly CDK4 study is incorrect without a direct comparison.

**Missing discordance entries:** If a drug is known to fail for a specific target in a specific species, that negative result must be committed as a `concordance: false` entry. Omitting known failures inflates D5 scores and suppresses OR-03 override.

**Screen hits without validation:** Drug screen hits (`evidence_type: "drug_screen"`) are hypothesis-generating, not validating. They must not score above 2 until followed up with a mechanistic study.

---

## Part 3 — Regulatory Context (D3)

D3 asks four sub-questions and the score is the curator's synthesis across all four. Unlike D4 and D5, D3 rarely has a single clean experiment to cite — it is typically assembled from multiple sources.

### Sub-dimension decision criteria

For each sub-dimension, record a yes/no answer and cite at least one source.

**Upstream inputs conserved?** (`upstream_inputs_conserved`)

Yes if: the same activating kinases, ligands, or transcription factors operate on the ortholog in the model organism in a disease-relevant tissue. No if: a major upstream regulator is absent (e.g. TGF-β → p15^INK4b in fly) or acts through a different intermediate. Partial cases: score the component at 3 and document the specific divergent input in `notes`.

**Downstream targets conserved?** (`downstream_targets_conserved`)

Yes if: the same set of target genes or target gene classes (e.g. E2F target genes) respond to manipulation of this component in the model. No if: the gene drives a different transcriptional programme. Use expression data (RNA-seq following KO/OE) if available; otherwise infer from published pathway studies.

**PTM sites conserved?** (`ptm_sites_conserved`)

Yes if: the key phosphorylation, ubiquitination, SUMOylation, or acetylation sites relevant to regulation are present and in the same sequence context. Check PhosphoSitePlus for human PTM sites, then BLAST the model organism sequence to confirm conservation. No if: a regulatory PTM site is absent or the surrounding sequence context is too diverged for the same kinase to recognise the site.

**Tissue expression overlap** (`tissue_expression_overlap`, 0–1 float)

This is the fraction of disease-relevant tissues in which the ortholog is expressed at a comparable level (within one order of magnitude TPM). Use GTEx for human, FlyAtlas2 for fly, EMBL-EBI Expression Atlas for zebrafish and worm. Express as a float: 1.0 = identical expression profile, 0.0 = no overlap. For cancer, use the cancer-relevant tissue, not whole-organism average.

### D3 score synthesis

| Score | Criteria |
|-------|---------|
| 5 | All four sub-dimensions positive; tissue overlap ≥0.80; no known rewiring |
| 4 | Three of four positive; tissue overlap ≥0.60; minor regulatory differences documented |
| 3 | Two of four positive; tissue overlap 0.30–0.59; some rewiring documented |
| 2 | One of four positive; tissue overlap <0.30; substantial regulatory divergence |
| 1 | All sub-dimensions negative; gene embedded in different pathway context |
| 0 | No meaningful regulatory conservation whatsoever |

### Common D3 errors

**Using whole-organism expression data:** FlyAtlas vs GTEx tissue-level data gives very different answers. Always use tissue-specific data matched to the disease context.

**Missing rewiring documentation:** If `known_rewiring: true`, the specific rewiring event must be described in `notes`. "Known rewiring" without description is not reviewable.

**Conflating expression with function:** A gene expressed in the right tissue does not mean it is regulated the same way. PTM site absence can completely disconnect a gene from its upstream regulators even with equivalent expression.

---

## Part 4 — Cross-cutting review rules

These apply regardless of evidence type and are checked by `validate_evidence.py --review`.

### Score-PMID consistency

| Score | PMID requirement |
|-------|-----------------|
| 5 | ≥2 PMIDs required |
| 4 | ≥1 PMID required |
| 3 | ≥1 PMID strongly recommended; absence requires justification in `notes` |
| 2 | PMID optional but absence must be explained |
| 1 | No PMID expected (inferred / no data) |
| 0 | ≥1 PMID required for the contradicting result |

Score 5 with zero PMIDs is an automatic review failure. Score 3 with no PMID and no justification triggers a warning.

### The contradiction rule

If any entry for a component × species pair has `supports_validity: false` (D4) or `concordance: false` (D5), the curator must:

1. Explicitly document the contradicting result in the entry's `description` or `notes`.
2. Assess whether the contradiction is explained (different assay, different cell type, off-target effect) or genuine.
3. If genuine, the score for the positive entries must be reduced: a 4/5 in the presence of one unexplained contradicting study becomes a 3/5 at most.
4. If there are more contradicting entries than supporting entries, `supports_validity` on the composite assessment should be set to false and score should not exceed 2.

### The single-source rule

A single paper, regardless of quality, cannot justify a score above 3 for D4 or D5 except in one circumstance: the paper contains an independent replication within it (e.g. two independent Cre-lox lines both showing the same tumour phenotype). If the replication is internal to a single paper, note it explicitly.

### The null fields rule

`null` is not the same as "unknown" everywhere. In `pharmacological_evidence`, `concordance: null` specifically means "not tested" — the model drug response has not been compared to human data. In `regulatory_context`, all boolean fields (`upstream_inputs_conserved` etc.) should be true or false, not null. If the answer is genuinely unknowable from existing data, record false and explain in `notes`.

---

## Part 5 — Worked examples

### Example 1: Rb1 knockout mouse — D4, score 3

```jsonc
{
  "model_species":     "mouse",
  "evidence_type":     "knockout",
  "pmid":              "7585548",
  "score":             3,
  "description":       "Rb1 homozygous knockout is embryonic lethal at E14.5 with defects in erythropoiesis and neurogenesis. Heterozygotes develop pituitary tumours and thyroid carcinomas with high penetrance. Neither phenotype matches the human RB1 loss phenotype of retinoblastoma.",
  "supports_validity": true,
  "caveats":           "Tumour spectrum does not match human disease. Lethality prevents adult somatic disease modelling. Heterozygote tumours arise by LOH of the remaining Rb1 allele — consistent with Knudson two-hit model but in a different tissue.",
  "phenotype_match":   "partial",
  "evidence_tier":     "validated"
}
```

**Review reasoning:** Gate 1 — published, peer-reviewed ✓. Gate 2 — in vivo ✓ (no cap). Gate 3 — partial match (cancer biology confirmed but wrong tissue) → ceiling 4. Gate 4 — rescue not tested → cannot reach 5. Gate 5 — replicated many times by independent labs ✓. Score 3 because phenotype_match is partial and the disease-specific endpoint (retinoblastoma) is not recapitulated. Score 4 would require equivalent tissue match.

---

### Example 2: Human RB1 rescue of Rb1-null mouse — D4, score 5 (combined with above)

```jsonc
{
  "model_species":     "mouse",
  "evidence_type":     "rescue",
  "pmid":              "8413634",
  "score":             5,
  "description":       "Transgenic expression of human RB1 rescues the embryonic lethality of Rb1-null mice. Rescued animals are viable and show delayed tumour onset compared to heterozygotes, confirming functional conservation of the RB1 pocket domain.",
  "supports_validity": true,
  "caveats":           "Rescue is partial — transgenic animals still develop tumours, suggesting dosage or regulatory context differences between mouse Rb1 and human RB1 in vivo.",
  "phenotype_match":   "equivalent",
  "evidence_tier":     "validated"
}
```

**Review reasoning:** This entry alone warrants 5 at the entry level — rescue is the gold standard. Combined with the knockout entry above, the D4 scorer takes max(3, 5) = 5 from supporting entries, then checks for contradictions (none), applying MR-01 (+0.10 modifier). However: the curator should consider whether the partial rescue noted in caveats is sufficient to warrant a penalty. Decision: keep score 5 at entry level, document partial rescue in caveats, let the modifier system handle the composite adjustment.

---

### Example 3: Palbociclib in a fly model — D5, score 2

```jsonc
{
  "drug":            "palbociclib",
  "chembl_id":       "CHEMBL3301610",
  "target":          "CDK4",
  "model_species":   "drosophila",
  "evidence_type":   "in_vivo",
  "pmid":            null,
  "concordance":     null,
  "score":           2,
  "notes":           "No published study directly testing palbociclib in Drosophila Cdk4 models as of 2026-02. Drug is FDA-approved for CDK4/6 in HR+ breast cancer. Fly lacks CDK6 and lacks p16/INK4. Mechanism not confirmed in fly. Score reflects absence of data, not predicted failure.",
  "clinical_stage":  "approved",
  "evidence_tier":   "validated"
}
```

**Review reasoning:** Gate 1 — no PMID → max 2. Gate 2 — no concordance established → `concordance: null` is correct. Gate 3 — mechanism not confirmed in fly. Result: score 2 is correct. Do not score higher because the drug is approved in humans — that is circumstantial. Score 1 would be appropriate if the gene were not a drug target at all; score 2 correctly reflects "some context, no direct model data."

---

### Example 4: Contradicting pharmacological evidence — D5, score 0

```jsonc
{
  "drug":            "nutlin-3a",
  "chembl_id":       "CHEMBL279347",
  "target":          "MDM2",
  "model_species":   "drosophila",
  "evidence_type":   "in_vitro",
  "pmid":            "18316557",
  "concordance":     false,
  "score":           0,
  "notes":           "Nutlin-3a does not activate p53 pathway in Drosophila S2 cells. Fly Mdm2 (Dm) has diverged significantly from human MDM2 in the p53-binding domain. Fly p53 is also structurally diverged. MDM2 inhibitor strategy does not translate to Drosophila.",
  "clinical_stage":  "phase_2",
  "evidence_tier":   "validated"
}
```

**Review reasoning:** `concordance: false` is justified — direct experimental test shows no activity via expected mechanism. Score 0 triggers override rule OR-03, elevating the final risk level to High regardless of composite. This is intentional: known drug discordance is a direct translational failure signal and must not be masked by positive scores on other dimensions.

---

## Part 6 — Curator checklist

Print or copy this checklist for each evidence entry before running `--approve`.

### Before submitting any entry

- [ ] I have read the primary source, not just the abstract
- [ ] The PMID links to the specific experiment I am describing, not a review
- [ ] The species in `model_species` matches the species used in the experiment
- [ ] The `description` field contains enough detail that another curator could verify my score without reading the paper
- [ ] All known contradicting results are captured as separate entries with `supports_validity: false` or `concordance: false`

### Before assigning score 4 or 5 (D4)

- [ ] The evidence is from an in vivo whole-animal system (not cell lines)
- [ ] The phenotype matches the human disease in both tissue and endpoint, not just in pathway membership
- [ ] At least one PMID is provided
- [ ] If score is 5: human gene rescue has been demonstrated and is captured as a separate entry
- [ ] If score is 5: findings have been replicated in ≥2 independent studies

### Before assigning score 4 or 5 (D5)

- [ ] The drug-target mechanism has been confirmed in the model organism, not just the endpoint
- [ ] `concordance: true` is based on a direct comparison to human data, not circumstantial co-occurrence of model efficacy and clinical approval
- [ ] At least one PMID is provided
- [ ] If score is 5: the drug is approved and the model response has been directly compared to clinical outcome data

### Before assigning `concordance: false` or `supports_validity: false`

- [ ] The contradicting result is from a primary experimental study, not a commentary or review
- [ ] I have checked whether the contradiction is explained (different assay system, off-target effect, different genetic background) or genuine
- [ ] If genuine: I have verified that the composite score for this component × species pair will not reach Low Risk without manual review

### Before running `--approve`

- [ ] `validate_evidence.py --review` has been run and all warnings addressed (not just schema errors)
- [ ] A second curator has reviewed entries with score ≥4 or `concordance: false`
- [ ] My name and ORCID (if available) are in the `curator` field

---

## Appendix — Automated consistency warnings (`--review` mode)

These checks are implemented in `validate_evidence.py --review` and run automatically before `--approve`. They do not block approval but generate warnings that must be addressed or explicitly overridden with `--override-warnings`.

| Warning ID | Condition | Action required |
|------------|-----------|----------------|
| `W-S01` | D4 score ≥4 with zero PMIDs | Add PMID or downgrade score |
| `W-S02` | D4 score 5 with no rescue entry | Add rescue entry or downgrade to 4 |
| `W-S03` | D4 score ≥4 with `evidence_type: in_vitro` | Gate 2 violation — downgrade to ≤3 |
| `W-S04` | D4 score 5 with single PMID | Replication requirement — downgrade or add second source |
| `W-S05` | D5 score ≥4 with `concordance: null` | Concordance not established — downgrade or confirm |
| `W-S06` | D5 score ≥4 with `evidence_type: in_vitro` | Gate 4 violation — downgrade |
| `W-S07` | D5 `concordance: true` with no PMID | Cannot confirm concordance without source |
| `W-S08` | D5 `evidence_type: drug_screen` with score ≥3 | Screen hits cap at 2 |
| `W-C01` | Supporting entries outnumbered by contradicting entries | Score should not exceed 2 |
| `W-C02` | Score ≥3 with a `concordance: false` entry present | Contradiction must be explained in notes |
| `W-C03` | `known_rewiring: true` in D3 with empty `notes` | Rewiring must be described |
| `W-C04` | D3 `tissue_expression_overlap` ≥0.80 but `known_rewiring: true` | Unusual combination — verify |
| `W-C05` | D4 score decreasing from prior committed entry | Potential retraction or update — flag for review |
| `W-N01` | `caveats` field empty for D4 score ≤3 | Complex results require documented caveats |
| `W-N02` | `phenotype_match: different` with `supports_validity: true` | Verify — different phenotype rarely supports validity |
| `W-N03` | `description` field fewer than 30 characters | Insufficient to verify score independently |
