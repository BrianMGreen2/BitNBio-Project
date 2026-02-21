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

## Repository Structure

```
who-gives-a-fly/
├── data/
│   ├── orthologs/          # Cross-species ortholog mappings (DIOPT, OrthoFinder)
│   ├── expression/         # Tissue- and stage-specific expression profiles
│   └── clinical/           # Human variant and clinical outcome data
├── pathway_maps/
│   ├── rb_pathway/         # Rb/E2F pathway maps across three species
│   ├── comparisons/        # Divergence annotations and confidence scores
│   └── diagrams/           # Visual pathway diagrams (.html, .md, .svg)
├── models/
│   ├── translational/      # Predictive translational roadblock models
│   └── validation/         # Cross-validation against known drug outcomes
├── notebooks/
│   ├── exploratory/        # Analysis and visualization notebooks
│   └── figures/            # Publication-ready figure generation
├── scripts/
│   ├── ortholog_mapping.py
│   ├── pathway_comparison.py
│   └── divergence_scoring.py
└── docs/
    └── pathway_glossary.md
```

---

## Getting Started

### Prerequisites

```bash
python >= 3.9
pip install -r requirements.txt
```

### Installation

```bash
git clone https://github.com/your-org/who-gives-a-fly.git
cd who-gives-a-fly
pip install -e .
```

### Quick Start

```python
from whogivesafly import PathwayMapper, TranslationalModel

# Load the Rb pathway cross-species map
rb_map = PathwayMapper.load("rb_pathway")

# Identify divergence points between fly and human
divergences = rb_map.compare(species_a="drosophila", species_b="human")
divergences.summary()

# Score translational risk for a candidate compound
model = TranslationalModel.from_pathway(rb_map)
risk_score = model.score(compound="palbociclib", source_species="mouse")
print(risk_score)
```

---

## Key Concepts

### The Valley of Death
The gap between preclinical efficacy and clinical success. Approximately 90% of compounds that enter clinical trials fail — a significant proportion due to unexpected species-specific biology that was never characterized.

### Translational Roadblocks
Specific molecular divergences between species that predict differential drug response. Examples include: gene family expansion (one fly gene → three human paralogs with distinct expression patterns), regulatory rewiring (same pathway, different upstream inputs), and tissue-specific isoform switching.

### Conservation Score
A compound metric capturing both sequence identity and functional equivalence of pathway components across species. High conservation score ≠ guaranteed translational success, but low score is a strong predictor of failure.

---

## Contributing

We welcome contributions from researchers in genetics, computational biology, pharmacology, and translational medicine. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we are actively seeking input:

- Additional pathway modules beyond Rb (Notch, Wnt, Hedgehog are priority targets)
- Clinical outcome datasets for benchmarking translational predictions
- Experimental validation in *Drosophila* disease models
- Integration with existing drug repurposing databases

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
