# 🪰 Who Gives a Fly?

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
