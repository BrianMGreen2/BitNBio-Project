# Translational Risk Assessment
## Retinoblastoma (Rb) Tumor Suppressor Pathway
### Model organism: Mouse → Human
> Generated: 2026-02-22T02:34:13  
> Evidence tier: inferred (from pathways.json annotations)

---

## Scoring Summary

| Component | D1 Seq | D2 Para | D3 Reg | D4 Pheno | D5 Ther | Composite | Risk |
|-----------|--------|---------|--------|----------|---------|-----------|------|
| `rb1` | 5/5 | 5/5 | 5/5 | 3/5 | 2/5 | `0.86` ████ | ✅ Low Risk |
| `cdk4_6` | 5/5 | 5/5 | 5/5 | 4/5 | 2/5 | `0.90` ████ | ✅ Low Risk |
| `cyclin_d` | 5/5 | 5/5 | 5/5 | 3/5 | 2/5 | `0.86` ████ | ✅ Low Risk |
| `ink4_family` | 4/5 | 5/5 | 4/5 | 0/5 | 0/5 | `0.60` ██░░ | 🚫 High Risk |
| `e2f_family` | 5/5 | 5/5 | 5/5 | 4/5 | 2/5 | `0.90` ████ | ✅ Low Risk |
| `cip_kip_family` | 5/5 | 5/5 | 5/5 | 3/5 | 2/5 | `0.86` ████ | ✅ Low Risk |
| `arf_p53` | 5/5 | 5/5 | 5/5 | 0/5 | 3/5 | `0.76` ██░░ | 🚫 High Risk |

> **D1** Sequence conservation (weight 30%) · **D2** Paralog complexity (20%) · **D3** Regulatory context (20%) · **D4** Phenotypic validity (20%) · **D5** Therapeutic evidence (10%)

---

## Component Detail

### rb1

✅ **Low translational risk** (composite score: 0.86). The Mouse ortholog of human **RB1** is **Rb1**. Conservation is strong and the regulatory context is largely equivalent. Findings from Mouse models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 97%. Conservation level: very_high. 97% protein identity; functionally interchangeable in most contexts |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 2. Mouse paralogs: 2. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'Retinoblastoma, osteosarcoma'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### cdk4_6

✅ **Low translational risk** (composite score: 0.90). The Mouse ortholog of human **CDK4/CDK6** is **Cdk4/Cdk6**. Conservation is strong and the regulatory context is largely equivalent. Findings from Mouse models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 96%. Conservation level: very_high. Nearly identical. R24C mutation conserved in function. |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 4/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'Amplified in liposarcoma, breast; CDK4-R24C in familial melanoma'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### cyclin_d

✅ **Low translational risk** (composite score: 0.86). The Mouse ortholog of human **CCND1/D2/D3** is **Ccnd1/d2/d3**. Conservation is strong and the regulatory context is largely equivalent. Findings from Mouse models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 93%. Conservation level: very_high. Isoform pattern and tissue specificity conserved |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: moderate. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'CCND1 amplified in breast, mantle cell lymphoma, head & neck'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### ink4_family

🚫 **High translational risk** (composite score: 0.60). The Mouse ortholog of human **CDKN2A/B/C/D** is **Cdkn2a/b/c/d**. Significant gaps in conservation, regulatory context, or phenotypic equivalence reduce confidence in direct translation. Orthogonal validation in mouse, organoids, or human cell lines is recommended.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 4/5 | Sequence identity: 88%. Conservation level: high. All 4 members present. p19ARF (mouse) ≈ p14ARF (human) — same locus, ~50% sequence identity, equivalent function |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 4/5 | Regulatory context score derived from conservation level (high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 0/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: high. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 0/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'CDKN2A most commonly silenced gene in cancer; familial melanoma, pancreatic, NSCLC'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Override rules triggered:**

- `OR-02` → elevated to **high**: Experimental evidence of non-equivalence overrides positive sequence or regulatory scores.
- `OR-03` → elevated to **high**: Known drug discordance between model and human is a direct translational failure signal.

**Recommended action:**

> Significant translational gap. Do not extrapolate without orthogonal validation in a higher-fidelity model or human cell system.

---

### e2f_family

✅ **Low translational risk** (composite score: 0.90). The Mouse ortholog of human **E2F1-8/DP1-2** is **E2f1-8/Dp1-2**. Conservation is strong and the regulatory context is largely equivalent. Findings from Mouse models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 94%. Conservation level: very_high. 8-member family conserved; tissue and cell-cycle-stage expression patterns equivalent |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 4/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'E2F1 overexpression in many cancers; E2F3 amplified in bladder cancer'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### cip_kip_family

✅ **Low translational risk** (composite score: 0.86). The Mouse ortholog of human **CDKN1A/B/C** is **Cdkn1a/b/c**. Conservation is strong and the regulatory context is largely equivalent. Findings from Mouse models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 91%. Conservation level: very_high. All 3 members conserved; p21 p53-responsiveness equivalent |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: moderate. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'p27 loss correlates with poor prognosis breast/colorectal; p57 mutations in Beckwith-Wiedemann'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### arf_p53

🚫 **High translational risk** (composite score: 0.76). The Mouse ortholog of human **CDKN2A(ARF)/TP53/MDM2** is **Cdkn2a(Arf)/Trp53/Mdm2**. Significant gaps in conservation, regulatory context, or phenotypic equivalence reduce confidence in direct translation. Orthogonal validation in mouse, organoids, or human cell lines is recommended.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 5/5 | Sequence identity: 90%. Conservation level: very_high. Functionally equivalent; p19ARF/p14ARF are different isoforms of same logic. Co-deletion of Rb+p53 required for full escape. |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Mouse paralogs: 0. |
| D3 Regulatory context    | 5/5 | Regulatory context score derived from conservation level (very_high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 0/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for mouse. Legacy risk rating: high. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 3/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'TP53 mutated in >50% cancers; MDM2 amplified in sarcomas'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Override rules triggered:**

- `OR-02` → elevated to **high**: Experimental evidence of non-equivalence overrides positive sequence or regulatory scores.

**Recommended action:**

> Significant translational gap. Do not extrapolate without orthogonal validation in a higher-fidelity model or human cell system.

---
