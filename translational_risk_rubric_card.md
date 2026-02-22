# Translational Risk Rubric — Reference Card

> *Who Gives a Fly · v1.0.0*

---

## Five Scoring Dimensions

| # | Dimension | Weight | What it measures |
|---|-----------|--------|-----------------|
| D1 | Sequence conservation | 30% | Protein identity and domain coverage |
| D2 | Paralog complexity    | 20% | Gene family size mismatch and compensation risk |
| D3 | Regulatory context    | 20% | Upstream inputs, PTMs, tissue expression |
| D4 | Phenotypic validity   | 20% | Experimental disease model concordance |
| D5 | Therapeutic evidence  | 10% | Drug response concordance |

---

## Scoring Scale (per dimension: 0–5)

| Score | D1 Sequence | D2 Paralogs | D3 Regulatory | D4 Phenotype | D5 Therapeutic |
|-------|-------------|-------------|---------------|--------------|----------------|
| 5 | ≥90% identity | Equivalent count | Fully conserved | Fully validated | Clinical concordance |
| 4 | 70–89% | ±1 paralog | Largely conserved | Substantially validated | Strong preclinical |
| 3 | 45–69% | 2–3 difference | Partially conserved | Partially validated | Preclinical evidence |
| 2 | 20–44% | Major mismatch | Substantially diverged | Limited validation | Limited evidence |
| 1 | <20% | Single vs family | Largely diverged | Predicted only | No drug data |
| 0 | Absent | No homolog | Completely diverged | Contradicted | Discordant |

---

## Risk Level Thresholds

```
Composite score = D1×0.30 + D2×0.20 + D3×0.20 + D4×0.20 + D5×0.10
                  (each dimension normalised to 0–1 before weighting)

Score ≥ 0.75  →  ✅ Low Risk      — findings likely to translate
Score ≥ 0.50  →  ⚠️  Moderate Risk — translate with caution
Score ≥ 0.25  →  🚫 High Risk     — do not extrapolate without validation
Score < 0.25  →  💀 Critical Gap  — use alternative model
```

---

## Override Rules (applied after composite score)

| Rule | Condition | Override |
|------|-----------|---------|
| OR-01 | D1 = 0 (no homolog) | → Critical |
| OR-02 | D4 = 0 (contradicted phenotype) | → High |
| OR-03 | D5 = 0 (discordant drug response) | → High |
| OR-04 | D2 = 0 AND D1 ≤ 2 | → Critical |
| OR-05 | D3 ≤ 1 AND D4 ≤ 1 | → High |

---

## Modifier Rules (adjust composite before threshold mapping)

| Rule | Condition | Adjustment |
|------|-----------|-----------|
| MR-01 | Human gene rescue demonstrated | +0.10 |
| MR-02 | Drug concordance in ≥2 studies | +0.08 |
| MR-03 | Tissue expression mismatch | −0.10 |
| MR-04 | Zebrafish WGD subfunctionalisation | −0.08 |
| MR-05 | Convergent evolution (different mechanism) | −0.12 |

---

## Warning Flags

Flags are raised independently of composite score and annotate the output record.

| Flag | Trigger | Severity |
|------|---------|---------|
| `no_homolog` | D1 = 0 | Critical |
| `paralog_compensation_risk` | D2 ≤ 2 + compensation evidence | High |
| `tissue_expression_mismatch` | Expression overlap <40% | High |
| `ptm_site_absent` | Key modification site missing | Moderate |
| `regulatory_rewiring` | Documented pathway rewiring | Moderate |
| `developmental_vs_somatic_mismatch` | Phenotype timing mismatch | Moderate |
| `drug_discordance` | D5 = 0 | Critical |
| `wgd_paralog_risk` | Zebrafish: more paralogs than human | Moderate |
