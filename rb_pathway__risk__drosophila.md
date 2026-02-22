# Translational Risk Assessment
## Retinoblastoma (Rb) Tumor Suppressor Pathway
### Model organism: Drosophila → Human
> Generated: 2026-02-22T02:34:13  
> Evidence tier: inferred (from pathways.json annotations)

---

## Scoring Summary

| Component | D1 Seq | D2 Para | D3 Reg | D4 Pheno | D5 Ther | Composite | Risk |
|-----------|--------|---------|--------|----------|---------|-----------|------|
| `rb1` | 3/5 | 4/5 | 3/5 | 4/5 | 2/5 | `0.66` ███░ | ⚠️ Moderate Risk |
| `cdk4_6` | 4/5 | 5/5 | 4/5 | 4/5 | 2/5 | `0.80` ████ | ✅ Low Risk |
| `cyclin_d` | 2/5 | 5/5 | 2/5 | 3/5 | 2/5 | `0.56` ███░ | ⚠️ Moderate Risk |
| `ink4_family` | 0/5 | 0/5 | 0/5 | 0/5 | 0/5 | `0.00` █░░░ | 💀 Critical Gap |
| `e2f_family` | 3/5 | 5/5 | 3/5 | 3/5 | 2/5 | `0.66` ███░ | ⚠️ Moderate Risk |
| `cip_kip_family` | 3/5 | 5/5 | 3/5 | 3/5 | 2/5 | `0.66` ███░ | ⚠️ Moderate Risk |
| `arf_p53` | 2/5 | 5/5 | 0/5 | 0/5 | 3/5 | `0.38` ██░░ | 🚫 High Risk |

> **D1** Sequence conservation (weight 30%) · **D2** Paralog complexity (20%) · **D3** Regulatory context (20%) · **D4** Phenotypic validity (20%) · **D5** Therapeutic evidence (10%)

---

## Component Detail

### rb1

⚠️ **Moderate translational risk** (composite score: 0.66). The Drosophila ortholog of human **RB1** is **RBF1**. Core function is conserved but notable divergences exist (see dimension rationales). Validate key findings in a complementary system before advancing to clinical development.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 3/5 | Sequence identity: 52%. Conservation level: moderate. Pocket domain conserved; overall 52% identity; 2 fly paralogs vs 3 human |
| D2 Paralog complexity    | 4/5 | ±1 paralog difference (1 vs 2 in human). Human paralogs: 2. Drosophila paralogs: 1. |
| D3 Regulatory context    | 3/5 | Regulatory context score derived from conservation level (moderate) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 4/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'Retinoblastoma, osteosarcoma'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Translate with caution. Identify the divergent dimension(s) and design bridging experiments before clinical development.

---

### cdk4_6

✅ **Low translational risk** (composite score: 0.80). The Drosophila ortholog of human **CDK4/CDK6** is **Cdk4**. Conservation is strong and the regulatory context is largely equivalent. Findings from Drosophila models are likely to predict human biology for this component.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 4/5 | Sequence identity: 79%. Conservation level: high. Fly Cdk4 kinase domain well conserved; absence of Cdk6 is key divergence |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Drosophila paralogs: 0. |
| D3 Regulatory context    | 4/5 | Regulatory context score derived from conservation level (high) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 4/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'Amplified in liposarcoma, breast; CDK4-R24C in familial melanoma'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Model organism findings are likely to translate directly. Proceed with confidence; document assumptions.

---

### cyclin_d

⚠️ **Moderate translational risk** (composite score: 0.56). The Drosophila ortholog of human **CCND1/D2/D3** is **CycD**. Core function is conserved but notable divergences exist (see dimension rationales). Validate key findings in a complementary system before advancing to clinical development.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 2/5 | Sequence identity: 41%. Conservation level: low. Single fly CycD; functional emphasis differs — more growth than cell cycle entry |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Drosophila paralogs: 0. |
| D3 Regulatory context    | 2/5 | Regulatory context score derived from conservation level (low) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: moderate. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'CCND1 amplified in breast, mantle cell lymphoma, head & neck'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Translate with caution. Identify the divergent dimension(s) and design bridging experiments before clinical development.

---

### ink4_family

💀 **Critical translational risk** (composite score: 0.00). The Drosophila ortholog of human **CDKN2A/B/C/D** is **NONE**. This component cannot be reliably modelled in Drosophila. Do not extrapolate findings to human biology without validation in a higher-fidelity system. **Flags:** No ortholog identified.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 0/5 | Sequence identity: 0%. Conservation level: absent. No INK4 homolog. Roughex (Rux) overlaps functionally but is not structurally related. MAJOR translational gap. |
| D2 Paralog complexity    | 0/5 | No homolog in drosophila. Paralog complexity irrelevant — component absent. |
| D3 Regulatory context    | 0/5 | Regulatory context score derived from conservation level (absent) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 0/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: high. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 0/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'CDKN2A most commonly silenced gene in cancer; familial melanoma, pancreatic, NSCLC'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Override rules triggered:**

- `OR-01` → elevated to **critical**: No homolog means the component cannot be modelled at all. Composite score is meaningless.
- `OR-02` → elevated to **high**: Experimental evidence of non-equivalence overrides positive sequence or regulatory scores.
- `OR-03` → elevated to **high**: Known drug discordance between model and human is a direct translational failure signal.
- `OR-04` → elevated to **critical**: No homolog AND low sequence similarity: component functionally absent in model.
- `OR-05` → elevated to **high**: Both regulatory context and phenotypic evidence indicate non-equivalence.

**Flags:**

- `no_homolog`

**Recommended action:**

> Do not extrapolate. Use an alternative model or human-derived system (organoids, iPSCs, patient samples).

---

### e2f_family

⚠️ **Moderate translational risk** (composite score: 0.66). The Drosophila ortholog of human **E2F1-8/DP1-2** is **dE2F1/dE2F2/dDP**. Core function is conserved but notable divergences exist (see dimension rationales). Validate key findings in a complementary system before advancing to clinical development.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 3/5 | Sequence identity: 58%. Conservation level: moderate. Core DNA-binding domain conserved; only 2 members. Activator/repressor logic intact. Good model for pathway logic, not isoform-specific biology. |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Drosophila paralogs: 0. |
| D3 Regulatory context    | 3/5 | Regulatory context score derived from conservation level (moderate) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: low. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'E2F1 overexpression in many cancers; E2F3 amplified in bladder cancer'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Translate with caution. Identify the divergent dimension(s) and design bridging experiments before clinical development.

---

### cip_kip_family

⚠️ **Moderate translational risk** (composite score: 0.66). The Drosophila ortholog of human **CDKN1A/B/C** is **dap**. Core function is conserved but notable divergences exist (see dimension rationales). Validate key findings in a complementary system before advancing to clinical development.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 3/5 | Sequence identity: 48%. Conservation level: moderate. Single Dacapo most similar to p27. p21 DNA damage response not equivalent. Reduced complexity. |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Drosophila paralogs: 0. |
| D3 Regulatory context    | 3/5 | Regulatory context score derived from conservation level (moderate) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 3/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: moderate. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 2/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'p27 loss correlates with poor prognosis breast/colorectal; p57 mutations in Beckwith-Wiedemann'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Recommended action:**

> Translate with caution. Identify the divergent dimension(s) and design bridging experiments before clinical development.

---

### arf_p53

🚫 **High translational risk** (composite score: 0.38). The Drosophila ortholog of human **CDKN2A(ARF)/TP53/MDM2** is **Dp53/Dmn**. Significant gaps in conservation, regulatory context, or phenotypic equivalence reduce confidence in direct translation. Orthogonal validation in mouse, organoids, or human cell lines is recommended.

**Dimension breakdown:**

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| D1 Sequence conservation | 2/5 | Sequence identity: 38%. Conservation level: low. Dp53 present but ARF-MDM2 link is partial. Fly apoptosis program diverged (uses Reaper/Hid/Grim). Important gap for p53-targeted drug studies. |
| D2 Paralog complexity    | 5/5 | Equivalent paralog count. Human paralogs: 0. Drosophila paralogs: 0. |
| D3 Regulatory context    | 0/5 | Regulatory context score derived from conservation level (low) and species-specific notes. Note: Full regulatory scoring requires explicit regulatory_context entries in pathways.json. |
| D4 Phenotypic validity   | 0/5 | Phenotypic validity estimated from translational notes and ortholog-specific annotations for drosophila. Legacy risk rating: high. For precise scoring, add phenotypic_evidence entries to pathways.json. |
| D5 Therapeutic evidence  | 3/5 | Therapeutic evidence estimated from disease annotations and translational notes. Disease context: 'TP53 mutated in >50% cancers; MDM2 amplified in sarcomas'. For precise scoring, add pharmacological_evidence entries to pathways.json. |

**Override rules triggered:**

- `OR-02` → elevated to **high**: Experimental evidence of non-equivalence overrides positive sequence or regulatory scores.
- `OR-05` → elevated to **high**: Both regulatory context and phenotypic evidence indicate non-equivalence.

**Recommended action:**

> Significant translational gap. Do not extrapolate without orthogonal validation in a higher-fidelity model or human cell system.

---
