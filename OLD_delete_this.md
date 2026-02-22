---

## Translational Risk Scoring

Beyond the conservation heatmap produced by `pipeline.py`, the system now includes a five-dimension weighted scoring engine that produces structured, traceable risk assessments for every pathway component × model species pair.

### How it works

`risk_scorer.py` scores each component on five dimensions and combines them into a composite translational risk rating:

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| D1 — Sequence conservation | 30% | Protein identity and functional domain coverage |
| D2 — Paralog complexity | 20% | Gene family size mismatch and compensation risk |
| D3 — Regulatory context | 20% | Upstream inputs, downstream targets, PTM sites, tissue expression |
| D4 — Phenotypic validity | 20% | Experimental evidence of disease model equivalence |
| D5 — Therapeutic evidence | 10% | Drug-response concordance between model and human |

Composite scores map to four risk levels: ✅ Low (≥0.75), ⚠️ Moderate (≥0.50), 🚫 High (≥0.25), 💀 Critical (<0.25). Five override rules can elevate a risk level regardless of composite score — for example, a missing homolog (OR-01) forces Critical regardless of other dimensions.

```bash
python risk_scorer.py --pathway rb_pathway --species drosophila mouse zebrafish worm
python risk_scorer.py --pathway all --species drosophila mouse
python risk_scorer.py --validate-rubric
```

Outputs are written to `output/{pathway}__risk__{species}.md` and `.json`. Risk scoring now also runs automatically inside `pipeline.py` — every JSON report includes a `risk_assessments` block appended alongside the conservation analysis.

### Inferred vs ground-truth scores

Three dimensions (D3, D4, D5) cannot be computed from sequence data alone. When no structured evidence is present, the scorer infers scores from free-text annotations in `pathways.json`. Every inferred score is labelled `[INFERRED]` in the rationale field and the assessment record carries `"evidence_tier": "inferred"`. The system is transparent about this: inferred scores are useful starting points, not clinical conclusions.

When structured evidence is added (see Evidence Curation below), the affected dimensions upgrade automatically to `[VALIDATED]` and `evidence_tier` advances to `"partial"` or `"validated"`. The `dimension_scored_by` field in every JSON output record shows the source of each dimension's score at a glance.

---

## Evidence Curation

### The evidence pipeline

Upgrading inferred scores to ground-truth follows a three-step pipeline:

```
PubMed / APIs
     │
     ├── data_enricher.py ──→ data/enriched/       (D1, D2: Ensembl; D5: ChEMBL)
     │
     └── curator + template ─→ evidence draft .json  (D3, D4, D5: literature)
                                      │
                               validate_evidence.py
                               ├── --entry   (schema check)
                               ├── --review  (scientific consistency)
                               └── --approve (merge to pathways.json)
```

`data_enricher.py` handles dimensions that have authoritative API sources — sequence identity and paralog counts from Ensembl, drug activity from ChEMBL, tissue expression from GTEx. Its outputs are written to `data/enriched/` and never directly to `pathways.json`, keeping API data and curator data separate. `risk_scorer.py` reads enriched files automatically if they are present.

`validate_evidence.py` handles dimensions that require human judgment — regulatory context, phenotypic equivalence, pharmacological concordance. It generates blank templates, validates structure against `config/evidence_schema.json`, runs scientific consistency checks, and merges approved entries into `pathways.json`.

### Getting started: what to do first

```bash
# See which components have no structured evidence and what the priorities are
python prioritise.py --top 20

# Check which API calls are ready to run
python data_enricher.py --check-apis
python data_enricher.py --pathway rb_pathway --dry-run

# Run API enrichment for one pathway (requires internet access)
python data_enricher.py --pathway rb_pathway

# Generate a curation template for the highest-priority gap
python validate_evidence.py --template ink4_family --pathway rb_pathway \
  --species mouse drosophila --output ink4_evidence.json

# Validate → review → approve
python validate_evidence.py --entry ink4_evidence.json --component ink4_family
python validate_evidence.py --review ink4_evidence.json --component ink4_family
python validate_evidence.py --approve ink4_evidence.json \
  --component ink4_family --curator "Your Name"
```

### Prerequisites for API enrichment

`data_enricher.py` requires Ensembl gene IDs to run D1/D2 enrichment and Gencode IDs for D3 GTEx expression data. These are now present in `pathways.json` for all current components. When adding new components, include them in the human ortholog entry:

```jsonc
"human": {
  "symbol":     "RB1",
  "ensembl_id": "ENSG00000139687",    // enables D1/D2 Ensembl enrichment
  "gencode_id": "ENSG00000139687.14", // enables D3 GTEx expression enrichment
  "disease":    "Retinoblastoma, osteosarcoma"
}
```

### Scientific review — score quality gates

`validate_evidence.py --review` enforces that scores are justified by the evidence submitted, not just that the entry is structurally valid. The key gates:

- Score ≥4 requires at least one PMID (error if absent)
- D4 score = 5 requires a human gene rescue entry (warning if absent)
- In vitro evidence caps D4 at 3, D5 at 2 (error if exceeded)
- `concordance: true` in D5 requires direct comparison to human data, not circumstantial co-occurrence with clinical approval (error if unverified)
- Drug screen hits cap at 2 until mechanism is confirmed (error if exceeded)

The full decision criteria — gate hierarchy, evidence strength framework, worked examples for Rb1 KO, human RB1 rescue, palbociclib in fly, and nutlin-3a discordance — are in `CURATOR_REVIEW_GUIDE.md`.

---

## Content Prioritisation

With 190 gaps across 10 components × 4 species × 3 inferred dimensions, not all curation work is equally valuable. `prioritise.py` ranks the backlog by expected impact on risk score precision, combining three signals: current risk level of the component, dimension weight in the composite, and inference uncertainty of the affected dimension.

```bash
python prioritise.py                          # full ranked backlog (190 items)
python prioritise.py --top 20                 # most impactful work first
python prioritise.py --mode curate            # literature tasks only
python prioritise.py --mode enrich            # API tasks only
python prioritise.py --pathway rb_pathway     # one pathway
python prioritise.py --format csv --output backlog.csv
```

The tool outputs a ranked table with the exact command to run for each action, effort estimate, and rationale. Current top priorities as of initial release:

```
#  Risk     Component      Sp         Dim  Type    Eff  Action
─────────────────────────────────────────────────────────────────────
1  🚫 high  ink4_family    mouse      D4   curate  ●    validate_evidence.py --template ...
2  🚫 high  ink4_family    zebrafish  D4   curate  ●    validate_evidence.py --template ...
3  🚫 high  arf_p53        drosophila D4   curate  ●    validate_evidence.py --template ...
4  🚫 high  arf_p53        mouse      D4   curate  ●    validate_evidence.py --template ...
```

`ink4_family` and `arf_p53` lead because they are already flagged 🚫 High Risk from qualitative assessment, D4 (phenotypic validity) has the highest inference uncertainty, and ground-truth evidence for these components is available in the published literature — making them high-impact, achievable curation targets.

---

## How the Tools Fit Together

```
config/pathways.json          ← primary knowledge store
config/evidence_schema.json   ← enforces structure of evidence entries
config/translational_risk_rubric_data.json ← scoring criteria and weights
config/settings.json          ← pipeline display settings
        │
        ├── pipeline.py       ← educational reports (MD/HTML/JSON)
        │       └── calls risk_scorer.py automatically
        │
        ├── risk_scorer.py    ← five-dimension risk assessments
        │       └── reads data/enriched/ for D1/D2 if available
        │
        ├── data_enricher.py  ← API enrichment → data/enriched/
        │
        ├── validate_evidence.py ← curation CLI (template/entry/review/approve)
        │
        └── prioritise.py     ← ranked action backlog
```

The only manual inputs required are: adding `ensembl_id`/`gencode_id` to new pathway components in `pathways.json`, and filling in evidence templates for D3/D4/D5 curation. Everything else is automated or tool-assisted.

---

## Updated Repository Structure

```
who-gives-a-fly/
├── pipeline.py              ← educational reports; now calls risk_scorer internally
├── risk_scorer.py           ← five-dimension risk scoring engine
├── validate_evidence.py     ← curation CLI: template / validate / review / approve
├── data_enricher.py         ← API enrichment: Ensembl, ChEMBL, GTEx
├── prioritise.py            ← ranked curation backlog
│
├── config/
│   ├── pathways.json        ← pathway knowledge + evidence entries (primary data)
│   ├── settings.json        ← display settings (now includes 'critical' risk level)
│   ├── translational_risk_rubric_data.json  ← scoring weights and thresholds
│   ├── translational_risk_rubric.json       ← JSON Schema for rubric files
│   └── evidence_schema.json ← JSON Schema for evidence blocks
│
├── data/
│   ├── enriched/            ← API enrichment outputs (auto-generated, do not edit)
│   └── cache/               ← local API cache (set ENRICHER_CACHE=1)
│
├── output/                  ← all generated reports
│   ├── {pathway}__{species}.md / .html / .json
│   └── {pathway}__risk__{species}.md / .json
│
└── CURATOR_REVIEW_GUIDE.md  ← evidence standards, decision gates, worked examples
```

---
