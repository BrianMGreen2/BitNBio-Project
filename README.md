# 🪰 Who Gives a Fly?

Project Team: Brian M. Green, Sarah Burke, and Adam Wenocur, at Bits in Bio, Show and Tell 2026, Feb. 21, 2026.

> *Bridging the valley of death in translational medicine through cross-species pathway mapping.*

---

## The Problem

One of the most persistent failures in modern medicine is the **translational gap** — the "valley of death" where promising genetic discoveries in model organisms never reach patients. Decades of research investment and billions in drug development spend have not solved this problem. Therapeutics that show remarkable efficacy in *Drosophila* or mouse models routinely fail in human clinical trials, often for reasons that could have been anticipated earlier.

The core issue is not that model organisms are wrong. It's that we lack robust, systematic frameworks for understanding **where, why, and how** molecular pathways diverge across species — and what those divergences mean for drug response.

---

## Our Approach

**Who Gives a Fly** leverages the evolutionary conservation of fundamental cellular pathways to build predictive models for cross-species translation. Rather than treating translational failure as an inevitable mystery, we treat it as a **mappable, quantifiable problem**.

Our framework rests on three pillars:

**1. Systematic Ortholog Mapping**
We catalog molecular similarities and divergences across *Drosophila melanogaster*, *Mus musculus*, and *Homo sapiens* at the gene, protein, and pathway level — identifying not just what is conserved, but where conservation breaks down and why.

**2. Pathway-Centered Analysis**
We focus on core regulatory pathways where conservation is deep but not perfect. The **Retinoblastoma (Rb) pathway** is our primary model system — a tumor suppressor circuit conserved across ~600 million years of evolution, yet with meaningful species-specific differences in gene family complexity, regulatory inputs, and downstream effectors.

**3. Predictive Translational Modeling**
Using cross-species molecular profiles, we are developing models that flag potential translational roadblocks *before* costly clinical trials begin — enabling earlier, better-informed go/no-go decisions in drug development pipelines.

---

## Why the Rb Pathway?

The Rb pathway is an ideal test case for cross-species translational research:

- It is **deeply conserved** — the core RBF/E2F/CDK circuit functions essentially identically in flies, mice, and humans
- It is **clinically critical** — dysregulated in virtually every human cancer through RB1 deletion, p16 silencing, Cyclin D amplification, or CDK4/6 amplification
- It is **tractably different** — flies run a simplified version (fewer paralogs, no INK4 family) that makes genetic dissection clean, while mammalian systems add regulatory complexity that matters for therapy
- It has **existing therapeutic targets** — CDK4/6 inhibitors (palbociclib, ribociclib, abemaciclib) are FDA-approved, giving us a real-world translational benchmark to model against

```
Drosophila          Mouse               Human
──────────          ─────               ─────
RBF1 / RBF2    →   Rb / p107 / p130 →  RB1 / RBL1 / RBL2
dE2F1 / dE2F2  →   E2F1–4          →   E2F1–8
1× Cyclin D    →   Cyclin D1/D2/D3  →  Cyclin D1/D2/D3
1× Cdk4        →   Cdk4 / Cdk6     →   CDK4 / CDK6
Dacapo         →   p21 / p27 / p57  →  p21 / p27 / p57
No INK4        →   p16/p15/p18/p19  →  p16/p15/p18/p19
```

This gradient of complexity — from the fly's minimal viable circuit to the human's redundant, tissue-specific elaboration — is exactly the kind of structured variation our models are designed to exploit.

---

## Pipeline

The core of this repository is a **Python analysis pipeline** that loads pathway and species data from JSON config files, computes quantitative conservation scores, identifies translational divergences, and generates educational reports automatically.

### How it works

```
config/pathways.json          config/settings.json
       │                              │
       └──────────┬───────────────────┘
                  ▼
            pipeline.py
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
  per-species   multi-    educational
  comparison   species      primer
   reports     summary     (.md/.html)
  (.md/.html)  (.md/.html)
```

### Quick start

```bash
git clone https://github.com/your-org/who-gives-a-fly.git
cd who-gives-a-fly
python pipeline.py --pathway rb_pathway --multi --primer
```

No dependencies beyond the Python standard library. Python ≥ 3.10 required.

### Usage

```bash
# Compare one pathway across all model organisms, generate all report types
python pipeline.py --pathway rb_pathway --multi --primer

# All pathways, clinical audience level, markdown only
python pipeline.py --pathway all --level clinical --formats markdown

# Specific species, specific pathway
python pipeline.py --pathway rb_pathway --species drosophila mouse --multi

# See all available pathways
python pipeline.py --list-pathways
```

| Flag | Default | Description |
|------|---------|-------------|
| `--pathway` | `rb_pathway` | Pathway ID to analyse, or `all` |
| `--species` | all configured | Comparison species |
| `--ref` | `human` | Reference species |
| `--level` | `graduate` | Education level: `undergraduate` `graduate` `clinical` |
| `--formats` | all | `markdown` `html` `json_report` |
| `--multi` | off | Generate multi-species conservation summary |
| `--primer` | off | Generate standalone educational primer |
| `--output` | `output/` | Output directory |

---

## Repository Structure

```
who-gives-a-fly/
├── pipeline.py                        # Main analysis + report generation pipeline
│
├── config/
│   ├── pathways.json                  # Pathway database: orthologs, conservation scores, risk ratings
│   └── settings.json                  # Thresholds, education levels, output config
│
├── output/                            # Generated reports (committed as examples)
│   ├── rb_pathway__drosophila.md/.html
│   ├── rb_pathway__mouse.md/.html
│   ├── rb_pathway__zebrafish.md/.html
│   ├── rb_pathway__worm.md/.html
│   ├── rb_pathway__multi_species_summary.md/.html
│   ├── rb_pathway__primer.md/.html
│   ├── notch_pathway__*.md/.html
│   └── wnt_pathway__*.md/.html
│
├── data/
│   ├── orthologs/                     # Cross-species ortholog mappings (DIOPT, OrthoFinder)
│   ├── expression/                    # Tissue- and stage-specific expression profiles
│   └── clinical/                      # Human variant and clinical outcome data
│
├── pathway_maps/
│   ├── rb_pathway/                    # Rb/E2F pathway maps across three species
│   ├── comparisons/                   # Divergence annotations and confidence scores
│   └── diagrams/                      # Visual pathway diagrams (.html, .md)
│
├── models/
│   ├── translational/                 # Predictive translational roadblock models
│   └── validation/                    # Cross-validation against known drug outcomes
│
├── notebooks/
│   ├── exploratory/                   # Analysis and visualization notebooks
│   └── figures/                       # Publication-ready figure generation
│
└── docs/
    └── pathway_glossary.md
```

---

## Config Files

### `config/pathways.json`

The core knowledge database. Defines pathways, components, orthologs, and conservation scores for every species pair. Currently contains:

| Pathway | ID | Components | Species covered |
|---|---|---|---|
| Retinoblastoma (Rb) Tumor Suppressor | `rb_pathway` | 7 | Human, Mouse, Fly, Zebrafish, Worm |
| Notch Signalling | `notch_pathway` | 1 | Human, Mouse, Fly, Zebrafish, Worm |
| Wnt / β-catenin | `wnt_pathway` | 2 | Human, Mouse, Fly, Zebrafish, Worm |

Each component entry includes:

```jsonc
{
  "id": "ink4_family",
  "role": "CDK inhibitor / tumor suppressor",
  "function": "Binds CDK4/6 monomers, prevents Cyclin D association...",
  "orthologs": {
    "human":      { "symbol": "CDKN2A/B/C/D", "disease": "Melanoma, pancreatic, NSCLC" },
    "drosophila": { "symbol": "NONE", "note": "CRITICAL GAP — no fly homolog exists" },
    "mouse":      { "symbol": "Cdkn2a/b/c/d", "note": "All 4 members present" }
  },
  "conservation": {
    "human_drosophila": { "score": 0.00, "level": "absent",  "notes": "No INK4 homolog in fly." },
    "human_mouse":      { "score": 0.88, "level": "high",    "notes": "All 4 members conserved." }
  },
  "translational_risk": "high",
  "translational_notes": "Fly is a poor model for INK4-mediated CDK4/6 inhibition..."
}
```

### `config/settings.json`

Controls conservation thresholds, risk level definitions, and education output profiles:

```jsonc
{
  "conservation_thresholds": {
    "very_high": { "min": 0.90, "symbol": "████", "description": "Highly predictive." },
    "high":      { "min": 0.70, "symbol": "███░", "description": "Minor divergences." },
    "moderate":  { "min": 0.45, "symbol": "██░░", "description": "Core function conserved." },
    "low":       { "min": 0.20, "symbol": "█░░░", "description": "Use cautiously." },
    "absent":    { "min": 0.00, "symbol": "░░░░", "description": "Do not extrapolate." }
  },
  "education_levels": {
    "undergraduate": { "include_mechanisms": false, "include_clinical": true  },
    "graduate":      { "include_mechanisms": true,  "include_clinical": true  },
    "clinical":      { "include_mechanisms": false, "include_clinical": true  }
  }
}
```

---

## Generated Outputs

Running the pipeline produces three types of report, in Markdown, HTML, and JSON:

**Per-species comparison report** (e.g. `rb_pathway__drosophila.md`)
Detailed component-by-component analysis comparing one model organism to human. Includes conservation scores, ASCII conservation heatmap, species-specific ortholog table, and translational recommendations.

**Multi-species summary** (`rb_pathway__multi_species_summary.md`)
A single matrix view of conservation and translational risk across all model organisms simultaneously. The fastest way to choose the right model for a given research question.

**Educational primer** (`rb_pathway__primer.md`)
A standalone document explaining the pathway, its components, and translational implications — written for the specified audience level (undergraduate / graduate / clinical).

Example conservation heatmap from a generated report:

```
Component            Score   Bar     Risk  Level
────────────────────────────────────────────────────────────
rb1                   0.52   ██░░    ⚠️    Moderate
cdk4_6                0.79   ███░    ✅    High
cyclin_d              0.41   █░░░    ⚠️    Low
ink4_family           0.00   ░░░░    🚫    Absent
e2f_family            0.58   ██░░    ✅    Moderate
cip_kip_family        0.48   ██░░    ⚠️    Moderate
arf_p53               0.38   █░░░    🚫    Low
────────────────────────────────────────────────────────────
AVERAGE               0.45   ██░░
```

---

---

## Translational Risk Scoring

The pipeline's conservation scores tell you *how similar* two genes are. But similarity alone is not enough to predict whether drug findings in a fly or mouse will hold up in a human clinical trial. The **translational risk scoring system** addresses this directly — it combines sequence conservation with four other dimensions of biological equivalence to produce a composite risk rating for every pathway component × model organism pair.

### The five dimensions

Risk is computed across five independently weighted dimensions. Each is scored 0–5.

| # | Dimension | Weight | What it captures |
|---|-----------|--------|-----------------|
| **D1** | Sequence conservation | 30% | Protein identity and domain coverage between model and human |
| **D2** | Paralog complexity | 20% | Gene family size mismatch and compensation risk |
| **D3** | Regulatory context | 20% | Upstream inputs, PTM sites, tissue expression overlap |
| **D4** | Phenotypic validity | 20% | Experimental evidence that the model recapitulates human disease |
| **D5** | Therapeutic evidence | 10% | Drug response concordance between model and human |

The weights reflect a deliberate hierarchy. Sequence conservation is necessary but not sufficient — a 90% identical protein embedded in a completely rewired regulatory network will still fail to translate. Phenotypic validity (D4) is the most direct evidence available, but often the hardest to obtain, which is why it shares equal weight with regulatory context rather than dominating the score.

### How scores map to risk levels

Each dimension score is normalised to 0–1, multiplied by its weight, and summed into a composite:

```
composite = (D1×0.30 + D2×0.20 + D3×0.20 + D4×0.20 + D5×0.10)

Score ≥ 0.75  →  ✅  Low Risk      Model findings likely to translate directly
Score ≥ 0.50  →  ⚠️  Moderate Risk  Translate with caution; validate divergent dimensions
Score ≥ 0.25  →  🚫  High Risk      Do not extrapolate without orthogonal validation
Score < 0.25  →  💀  Critical Gap   Use an alternative model or human-derived system
```

### Override rules

Certain conditions are serious enough to elevate the final risk level regardless of the composite score. These are applied *after* the weighted sum:

| Rule | Condition | Override |
|------|-----------|---------|
| OR-01 | D1 = 0 — no homolog exists | → Critical |
| OR-02 | D4 = 0 — phenotype experimentally contradicted | → High |
| OR-03 | D5 = 0 — drug response known to be discordant | → High |
| OR-04 | D2 = 0 AND D1 ≤ 2 — no homolog, low similarity | → Critical |
| OR-05 | D3 ≤ 1 AND D4 ≤ 1 — regulatory and phenotypic evidence both weak | → High |

The INK4 family in *Drosophila* is a clear example of OR-01 firing: there is no fly homolog of p16/p15/p18/p19, so regardless of how well the rest of the Rb pathway is conserved, the fly is a poor model for any drug mechanism that depends on INK4-mediated CDK4/6 inhibition. This is exactly the kind of gap that causes clinical trial failure when missed.

### Modifier rules

Positive or negative adjustments to the composite score can be applied when specific evidence is present:

| Rule | Condition | Adjustment |
|------|-----------|-----------|
| MR-01 | Human gene rescues model phenotype | +0.10 |
| MR-02 | Drug concordance replicated in ≥2 independent studies | +0.08 |
| MR-03 | Tissue expression mismatch for disease-relevant cell type | −0.10 |
| MR-04 | Zebrafish whole-genome duplication creates subfunctionalised paralogs | −0.08 |
| MR-05 | Convergent evolution — same phenotype, different mechanism | −0.12 |

MR-05 deserves particular attention. A model organism can produce a phenotype that looks like the human disease through an entirely different molecular mechanism. This is dangerous for drug development because a compound that corrects the model phenotype may be acting on the model-specific mechanism rather than the conserved one — and will therefore fail in humans.

### Warning flags

Flags are raised independently of the composite score and annotate each assessment record with interpretive warnings. They are surfaced in reports to draw attention to specific biological features that the numeric score alone may not capture:

| Flag | Severity | Meaning |
|------|---------|---------|
| `no_homolog` | Critical | Component cannot be studied in this model at all |
| `paralog_compensation_risk` | High | Paralog compensation may mask loss-of-function phenotype |
| `tissue_expression_mismatch` | High | Gene not expressed in the disease-relevant tissue equivalent |
| `ptm_site_absent` | Moderate | Key phosphorylation or ubiquitination site missing |
| `regulatory_rewiring` | Moderate | Documented change in upstream or downstream connections |
| `developmental_vs_somatic_mismatch` | Moderate | Model phenotype is developmental; human disease is adult/somatic |
| `drug_discordance` | Critical | Known failure of drug response concordance for this target |
| `wgd_paralog_risk` | Moderate | Zebrafish WGD extra paralogs — assess subfunctionalisation |

### The config files

Two new files in `config/` define and drive the scoring system:

**`config/translational_risk_rubric_data.json`** is the working rubric — the file curators edit to refine scoring logic. It contains all five dimension definitions with their level criteria, the override and modifier rule sets, flag definitions, and risk level thresholds. When you want to tighten a criterion, add a new modifier rule, or update a threshold based on new evidence, this is the file you change.

**`config/translational_risk_rubric.json`** is the formal JSON Schema that defines what a valid rubric file must look like. It specifies required fields, value types, and constraints. This is used to validate new rubric versions programmatically before they are accepted — important for maintaining consistency as the rubric evolves and contributors propose changes.

The separation is intentional: the schema enforces structure, the data file holds content. You can update scoring criteria without touching the schema, and you can tighten the schema's validation rules without changing any scores.

### The scoring engine

**`risk_scorer.py`** implements each dimension as a separate method, so they can be improved independently as richer data becomes available. The engine currently derives D3–D5 scores by inference from annotations already present in `pathways.json` — a deliberate design choice that lets the system produce useful scores immediately while clearly flagging in every output where richer data would improve precision.

```bash
# Score one pathway for all species
python risk_scorer.py --pathway rb_pathway --species drosophila mouse zebrafish worm

# Score all pathways and generate the rubric reference card
python risk_scorer.py --pathway all --species drosophila mouse zebrafish worm

# Print the rubric reference card to stdout
python risk_scorer.py --rubric-card

# Validate that the rubric data file is well-formed
python risk_scorer.py --validate-rubric
```

Outputs are written to `output/` as `{pathway}__{risk}__{species}.md` and `.json`. The JSON output contains the full structured assessment record for each component, including all dimension scores, applied modifiers and overrides, raised flags, and a plain-language narrative — suitable for downstream processing, database ingestion, or feeding into the educational report generator in `pipeline.py`.

### Example: Rb pathway, *Drosophila* vs Human

The scoring system produces scientifically meaningful differentiation even within a single pathway. For the Rb pathway in *Drosophila*:

```
Component         D1   D2   D3   D4   D5   Composite   Risk
─────────────────────────────────────────────────────────────
rb1               3    4    3    4    2    0.66 ███░    ⚠️  Moderate
cdk4_6            4    5    4    4    2    0.80 ████    ✅  Low
cyclin_d          2    5    2    3    2    0.56 ███░    ⚠️  Moderate
ink4_family       0    0    0    0    0    0.00 ░░░░    💀  Critical ← OR-01
e2f_family        3    5    3    3    2    0.66 ███░    ⚠️  Moderate
cip_kip_family    3    5    3    3    2    0.66 ███░    ⚠️  Moderate
arf_p53           2    5    0    0    3    0.38 ██░░    🚫  High ← OR-05
─────────────────────────────────────────────────────────────
```

This tells a researcher: use *Drosophila* freely for CDK4 biology (Low Risk), use it cautiously for RBF1/E2F studies with complementary validation (Moderate Risk), and do not use it for INK4 inhibitor drug screens or ARF/p53 failsafe studies (Critical/High Risk). That is a directly actionable set of model organism selection decisions — which is exactly what the scoring system is designed to produce.

---

---

## Inference Flags and Data Enrichment

### Where inference is used and why

The scoring engine produces useful risk assessments immediately — but three of the five dimensions (D3, D4, D5) currently derive their scores by inference from free-text annotations already present in `pathways.json`, rather than from structured ground-truth data. This was a deliberate design choice: it lets the system run without external dependencies and surface meaningful differentiation on day one, while being transparent about where the scores are estimated versus measured.

Every inferred score is flagged in the output. When you see the following phrases in a dimension rationale field, the score was derived by inference and should be treated as an estimate:

```
# D3 — Regulatory context
"Regulatory context score derived from conservation level (...) and species-specific notes.
 Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json."

# D4 — Phenotypic validity
"Phenotypic validity estimated from translational notes and ortholog-specific annotations.
 Legacy risk rating: {low|moderate|high}. For precise scoring, add phenotypic_evidence
 entries to pathways.json."

# D5 — Therapeutic evidence
"Therapeutic evidence estimated from disease annotations and translational notes.
 Disease context: '...'. For precise scoring, add pharmacological_evidence entries
 to pathways.json."
```

The `evidence_tier` field in every JSON output record also signals this globally:

```json
"evidence_tier": "inferred"
```

When a dimension is scored from structured ground-truth data, this changes to `"validated"` at the component level. When all five dimensions are ground-truth scored, the record-level `evidence_tier` upgrades to `"validated"` as well. This field is the primary machine-readable signal for downstream consumers (dashboards, databases, report generators) to distinguish estimated from measured scores.

---

### What triggers each inference flag

The three inferred dimensions each detect ground-truth data via a specific key they look for in `pathways.json`. When that key is absent, inference mode activates.

**D3 — Regulatory context** looks for a `regulatory_context` block in the component entry:

```jsonc
// Ground-truth entry — D3 scores from this directly
"regulatory_context": {
  "human_drosophila": {
    "upstream_inputs_conserved":    false,
    "downstream_targets_conserved": true,
    "ptm_sites_conserved":          false,
    "tissue_expression_overlap":    0.3,
    "known_rewiring":               true,
    "score": 2,
    "notes": "TGF-β input absent in fly; Armadillo/β-catenin targets partially conserved."
  }
}

// Without this block → D3 infers from conservation level + keyword scan of notes fields
```

**D4 — Phenotypic validity** looks for a `phenotypic_evidence` array:

```jsonc
// Ground-truth entry — D4 scores from this directly
"phenotypic_evidence": [
  {
    "model_species":  "mouse",
    "evidence_type":  "knockout",
    "pmid":           "7585548",
    "score":          3,
    "description":    "Rb1 homozygous KO lethal E14.5; heterozygotes develop pituitary tumours, not retinoblastoma.",
    "supports_validity": true,
    "caveats":        "Tumour spectrum differs from human. Does not model retinal disease."
  },
  {
    "model_species":  "mouse",
    "evidence_type":  "rescue",
    "pmid":           "8413634",
    "score":          5,
    "description":    "Human RB1 rescues developmental defects in Rb1-null mouse embryos.",
    "supports_validity": true
  }
]

// Without this array → D4 infers from translational_risk + keyword scan of notes fields
```

**D5 — Therapeutic evidence** looks for a `pharmacological_evidence` array:

```jsonc
// Ground-truth entry — D5 scores from this directly
"pharmacological_evidence": [
  {
    "drug":           "palbociclib",
    "target":         "CDK4/CDK6",
    "model_species":  "mouse",
    "evidence_type":  "in_vivo",
    "pmid":           "24122810",
    "concordance":    true,
    "score":          4,
    "notes":          "Tumour regression in Rb1-intact mouse mammary model; concordant with HR+ breast cancer clinical outcome."
  },
  {
    "drug":           "palbociclib",
    "target":         "CDK4/CDK6",
    "model_species":  "drosophila",
    "evidence_type":  "in_vivo",
    "pmid":           null,
    "concordance":    null,
    "score":          1,
    "notes":          "No published pharmacological data for palbociclib in Drosophila CDK4 models."
  }
]

// Without this array → D5 infers from disease field + keyword scan of translational_notes
```

Adding any of these structured blocks to a component entry in `pathways.json` immediately upgrades that dimension from inferred to ground-truth scoring on the next run, with no code changes required.

---

### Prioritising which gaps to fill first

Not all inference gaps matter equally. The dimensions with the highest weights (D3 and D4, each 20%) cause the most score uncertainty, and inference in those dimensions for high-risk components compounds the problem — an estimated score on a flagged component is precisely where you least want uncertainty.

A practical prioritisation order:

**1. Add `phenotypic_evidence` (D4) for any component currently scored 💀 Critical or 🚫 High Risk.** These are the decisions with the most clinical consequence. If a Critical Gap is based on inferred D4 data, you cannot be confident the gap is real or know how to bridge it. PubMed searches for the component × species combination with terms like "knockout phenotype", "disease model", "transgenic" are the fastest path to structured entries here.

**2. Add `pharmacological_evidence` (D5) for any component that is a known drug target.** CDK4/6, MDM2, and EZH2 all have published preclinical data in multiple model organisms. These entries are straightforward to populate from ChEMBL and the primary literature and immediately raise score precision for the most therapeutically relevant components.

**3. Add `regulatory_context` (D3) for Moderate Risk components where the decision whether to proceed is genuinely ambiguous.** D3 inference is the noisiest — it relies on keyword matching against free text — so Moderate Risk scores are the least reliable outputs in the current system. Structured regulatory context entries for these components will most often resolve ambiguity in a meaningful direction.

**4. Low Risk components at high confidence (very_high D1 conservation + mouse as model species) are lowest priority.** If D1 is 5/5 and the model is mouse, D3–D5 inference is unlikely to change the final risk level.

---

### Data integration architecture

The question of *how* to bring richer data into the scoring system has three answers depending on the use case, update frequency, and data source type. They are not mutually exclusive — the recommended architecture uses all three in combination.

---

#### Option 1: Direct JSON enrichment (structured curation)

**Best for:** Literature-derived phenotypic and pharmacological evidence. PMIDs, experimental results, expert-curated regulatory annotations.

**How it works:** Curators add `phenotypic_evidence`, `pharmacological_evidence`, and `regulatory_context` blocks directly to `pathways.json` following the schemas above. The scoring engine picks them up automatically on the next run.

**Workflow:**

```
Literature / database search
         │
         ▼
Curator populates structured entry
(phenotypic_evidence / pharmacological_evidence / regulatory_context)
         │
         ▼
Pull request to pathways.json
         │
         ▼
Schema validation (translational_risk_rubric.json)
         │
         ▼
risk_scorer.py re-run → evidence_tier upgrades to "validated"
```

**Strengths:** Highest precision. Human-verified. Fully auditable with PMIDs. Version-controlled in git.

**Limitations:** Labour-intensive. Does not scale automatically to new pathways or species. Requires expert judgment for each entry.

**Recommended tools:** Manual curation with a spreadsheet → JSON conversion script, or a lightweight curation interface (Google Form → GitHub Action → PR).

---

#### Option 2: API integration (live data retrieval)

**Best for:** Conservation scores (D1), paralog counts (D2), and expression data (D3 sub-dimension). These data are available from well-maintained public APIs and change infrequently enough that periodic retrieval is practical.

**How it works:** A data enrichment script queries external APIs and writes results into the component entries in `pathways.json`, or into a separate `data/enriched/` layer that the scoring engine reads preferentially over the base annotations.

**Recommended API integrations by dimension:**

| Dimension | Data needed | Recommended API | Endpoint |
|-----------|-------------|-----------------|---------|
| D1 — Sequence conservation | % identity, domain coverage | [DIOPT](https://www.flyrnai.org/diopt) | `/api/convert` with BLASTP scores |
| D1 — Sequence conservation | Structural alignment | [UniProt](https://www.uniprot.org/help/api) | `/uniprotkb/{id}` + BLAST |
| D2 — Paralog count | Gene family size | [Ensembl](https://rest.ensembl.org) | `/homology/id/{gene_id}` |
| D3 — Tissue expression | Expression by tissue | [GTEx API](https://gtexportal.org/api/v2) | `/expression/geneExpression` |
| D3 — Tissue expression | Cross-species expression | [Expression Atlas](https://www.ebi.ac.uk/gxa/api) | `/experiments` |
| D5 — Drug targets | Approved drug-target pairs | [ChEMBL API](https://www.ebi.ac.uk/chembl/api/data/) | `/target` + `/activity` |
| D5 — Drug targets | Clinical trial status | [ClinicalTrials.gov API](https://clinicaltrials.gov/api/v2) | `/studies` |

**Example enrichment script skeleton:**

```python
# data_enricher.py — fetches D1 conservation scores from Ensembl for all components
import requests, json

ENSEMBL = "https://rest.ensembl.org"

def fetch_paralogs(gene_id: str, species: str) -> list:
    url = f"{ENSEMBL}/homology/id/{gene_id}"
    r = requests.get(url, params={"type": "paralogues", "target_species": species},
                     headers={"Content-Type": "application/json"})
    r.raise_for_status()
    return r.json().get("data", [{}])[0].get("homologies", [])

def enrich_component(component: dict, ref_gene_id: str) -> dict:
    # Fetch paralog count from Ensembl
    paralogs = fetch_paralogs(ref_gene_id, "homo_sapiens")
    component["orthologs"]["human"]["paralogs_ensembl"] = [
        p["target"]["id"] for p in paralogs
    ]
    component["orthologs"]["human"]["n_paralogs_ensembl"] = len(paralogs)
    component["_enriched_at"] = datetime.now().isoformat()
    return component
```

**Recommended update cadence:** Run the enrichment script quarterly, or triggered by a GitHub Action when `pathways.json` adds a new component. Pin API response versions where possible (Ensembl release numbers, UniProt accessions) to maintain reproducibility.

**Strengths:** Scalable. Keeps conservation and paralog data current without manual effort. Ensembl and UniProt are authoritative sources.

**Limitations:** API availability and schema stability. Rate limits (Ensembl: 15 req/sec without key). Expression data requires careful tissue-type matching to disease context — this cannot be automated without curation of which tissue is disease-relevant for each component.

---

#### Option 3: RAG over the literature (unstructured evidence retrieval)

**Best for:** D4 (phenotypic validity) and D5 (therapeutic evidence) when structured database entries do not exist — i.e., for newly characterised genes, rare disease models, or unpublished/preprint evidence. Also useful for generating candidate `phenotypic_evidence` entries for curator review before they are formalised into `pathways.json`.

**How it works:** A retrieval-augmented generation system indexes the biomedical literature (PubMed abstracts, full-text open access articles, bioRxiv preprints) and retrieves relevant passages for a given component × species query. A language model then extracts structured evidence — phenotype descriptions, drug response data, rescue experiments — which is presented to curators for validation before being committed to `pathways.json`.

**RAG is a pipeline component here, not a replacement for curation.** The output of the RAG step is a *candidate* structured entry, not a committed score. Every AI-extracted entry carries an `evidence_tier: "ai_candidate"` flag and requires human sign-off before upgrading to `"validated"`.

**Recommended architecture:**

```
PubMed / bioRxiv / PMC full text
         │
         ▼ (nightly index update)
Vector store (e.g. Chroma, Weaviate, pgvector)
  — chunked by abstract / section
  — metadata: PMID, species, gene symbols, MeSH terms
         │
         ▼ (on-demand, triggered by new component or flag)
Retrieval query:
  "{component_id} {model_species} phenotype model disease knockout"
         │
         ▼
Top-k retrieved passages (k = 10–20)
         │
         ▼
LLM extraction prompt:
  "From the following passages, extract any experimental evidence
   of phenotypic equivalence or discordance between {model_species}
   and human for {component_id}. Return structured JSON matching
   the phenotypic_evidence schema."
         │
         ▼
Candidate phenotypic_evidence entries (evidence_tier: "ai_candidate")
         │
         ▼
Curator review interface
         │
   ┌─────┴─────┐
   ▼           ▼
Accept        Reject
   │
   ▼
Committed to pathways.json (evidence_tier: "validated")
```

**Recommended index sources:**

| Source | Content | Access |
|--------|---------|--------|
| [PubMed Central Open Access](https://ftp.ncbi.nlm.nih.gov/pub/pmc/oa_bulk/) | Full text, open access articles | Bulk FTP download |
| [Europe PMC API](https://europepmc.org/RestfulWebService) | Abstracts + some full text | REST API, no auth |
| [bioRxiv / medRxiv](https://api.biorxiv.org) | Preprints | REST API |
| [Semantic Scholar API](https://api.semanticscholar.org) | Abstracts + citation graph | REST API, free key |

**Chunking strategy for biomedical RAG:** Chunk by section (Abstract, Methods, Results, Discussion) rather than fixed token windows. Results sections contain phenotype descriptions; Methods sections contain species and construct details. Keep PMID, gene symbols (from NER or MeSH), and species as chunk metadata for pre-filtering before vector search.

**Strengths:** Can surface evidence for components with no structured database entries. Scales to the full literature without manual reading. Particularly powerful for rare model organisms (worm, zebrafish) where curated databases are less complete.

**Limitations:** LLM extraction is imperfect — phenotype descriptions are ambiguous, species are sometimes unclear, and numerical data (penetrance, effect sizes) is often inconsistently reported. Human validation is non-negotiable before any AI-extracted entry affects a risk score. RAG latency also makes it unsuitable for real-time scoring; treat it as a batch enrichment step.

---

### Recommended integration sequence

For a project at early stage, the most productive order of operations is:

**Phase 1 — Structured curation of priority components** (now → 3 months). Focus on `phenotypic_evidence` (D4) for any component rated 💀 Critical or 🚫 High Risk in the Rb pathway. These are the decisions that matter most and the data is findable in 2–3 PubMed searches per component. Add `pharmacological_evidence` (D5) for CDK4/6, MDM2, and EZH2 from ChEMBL. Run `risk_scorer.py` after each addition and verify that `evidence_tier` upgrades from `"inferred"` to `"validated"`.

**Phase 2 — API enrichment for D1 and D2** (3–6 months). Write `data_enricher.py` to automate Ensembl paralog counts and UniProt conservation scores. Set up a GitHub Action to run enrichment quarterly. This eliminates the main source of D2 inference error (paralog counts currently read from manually maintained arrays in `pathways.json`).

**Phase 3 — RAG pipeline for D4/D5 at scale** (6–12 months). Once the curation workflow is established and you understand what good `phenotypic_evidence` entries look like, set up a RAG pipeline to generate candidates for the Notch, Wnt, and Hedgehog pathways. Use Europe PMC as the primary index. Route all AI-extracted candidates through the curator review step before they touch `pathways.json`.

**Phase 4 — Live API integration for D3 expression data** (12+ months). Tissue-specific expression matching is the hardest dimension to automate because it requires knowing which tissue is disease-relevant for each component — a judgment call that changes by cancer subtype. Build this only after the curation vocabulary is stable enough to define tissue-relevance rules programmatically.

---

### Summary: inference flags at a glance

| Signal | Location | Meaning | Fix |
|--------|----------|---------|-----|
| `"evidence_tier": "inferred"` | JSON output record | ≥1 dimension is estimated | Add structured entries to `pathways.json` |
| `"Regulatory context score derived from..."` | D3 rationale field | No `regulatory_context` block | Add `regulatory_context` entry |
| `"Phenotypic validity estimated from..."` | D4 rationale field | No `phenotypic_evidence` array | Add `phenotypic_evidence` entries with PMIDs |
| `"Therapeutic evidence estimated from..."` | D5 rationale field | No `pharmacological_evidence` array | Add `pharmacological_evidence` from ChEMBL |
| `"Legacy risk rating: {low\|moderate\|high}"` | D4 rationale field | Score bootstrapped from old single-value field | Replace with structured evidence array |
| `"For precise scoring, add ... entries"` | Any rationale field | Explicit curator prompt | Targeted curation action |

---

## Extending the Pipeline

**Adding a new pathway** — add a new entry to `config/pathways.json` following the existing structure. The pipeline picks it up automatically with `--pathway all`.

**Adding a new species** — add the species metadata to the `metadata.species` block, then add ortholog entries and conservation scores for each pathway component. Run with `--species your_new_species`.

**Adding a new output format** — subclass `MarkdownReportGenerator` or add a new generator class to `pipeline.py` and hook it into the `run_pipeline()` format dispatch block.

---

## Key Concepts

**The Valley of Death**
The gap between preclinical efficacy and clinical success. Approximately 90% of compounds that enter clinical trials fail — a significant proportion due to unexpected species-specific biology that was never characterised.

**Translational Roadblocks**
Specific molecular divergences between species that predict differential drug response. Examples include gene family expansion (one fly gene → three human paralogs with distinct expression), regulatory rewiring (same pathway, different upstream inputs), and tissue-specific isoform switching.

**Conservation Score**
A numeric metric (0–1) capturing sequence identity and functional equivalence of pathway components across species. High score ≠ guaranteed translational success, but a low or absent score is a strong predictor of failure.

**Translational Risk**
A qualitative rating (`low` / `moderate` / `high`) derived from conservation score, paralog complexity, and known biological divergences. Used to flag which components — and which model organisms — are appropriate for a given research question.

---

## Contributing

We welcome contributions from researchers in genetics, computational biology, pharmacology, and translational medicine. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we are actively seeking input:

- Additional pathway modules (Hedgehog, PI3K/AKT, p53 are next priorities)
- Quantitative conservation scores backed by published sequence alignments
- Clinical outcome datasets for benchmarking translational predictions
- Experimental validation in *Drosophila* disease models
- Integration with drug repurposing databases (ChEMBL, DGIdb)

---

## Data Sources

| Resource | Use |
|---|---|
| [DIOPT](https://www.flyrnai.org/diopt) | Drosophila ortholog prediction |
| [FlyBase](https://flybase.org) | Drosophila gene and phenotype data |
| [OMIM](https://omim.org) | Human disease gene associations |
| [TCGA](https://www.cancer.gov/tcga) | Human cancer genomics |
| [ChEMBL](https://www.ebi.ac.uk/chembl/) | Drug-target bioactivity data |
| [STRING](https://string-db.org) | Protein interaction networks |
| [MGI](https://www.informatics.jax.org) | Mouse genome informatics |
| [ZFIN](https://zfin.org) | Zebrafish model organism database |
| [WormBase](https://wormbase.org) | *C. elegans* genome and biology |

---

## Citation

If you use this work in your research, please cite:

```bibtex
@software{whogivesafly2025,
  title   = {Who Gives a Fly: Cross-Species Pathway Mapping for Translational Medicine},
  year    = {2025},
  url     = {https://github.com/your-org/who-gives-a-fly}
}
```

---

## License

[MIT License](LICENSE) — see LICENSE for details.

---

## Contact

For questions, collaborations, or to report issues, please open a GitHub Issue or reach out via the Discussions tab.

---

*"The fly is not a small, hairy human. But it's closer than you think."*
