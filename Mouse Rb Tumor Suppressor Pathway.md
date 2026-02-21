# *Mus musculus* — Rb Tumor Suppressor Pathway
### Retinoblastoma · G1/S Checkpoint · Full Mammalian Complexity

---

## Pathway Diagram

```
                    ┌──────────────────────────────────────────┐
                    │           MITOGENIC SIGNALS               │
                    │  EGF · IGF-1 · FGF · Ras/ERK · PI3K/Akt  │
                    └─────────────────────┬────────────────────┘
                                          │ induces
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │       Cyclin D1  ·  Cyclin D2  ·  Cyclin D3   │
                    │         3 tissue-specific isoforms        │
                    │           [expanded vs. fly: 1×]          │
                    └─────────────────────┬────────────────────┘
                                          │ partners with
                                          ▼
  ┌────────────────────────┐    ┌─────────────────────────────┐
  │  p16^INK4a             │    │      CDK4  ·  CDK6           │
  │  p15^INK4b  ←TGF-β     │━━━⊣│   2 paralogous kinases       │
  │  p18^INK4c             │    │  [CDK6 absent in fly]        │
  │  p19^INK4d             │    └──────────────┬──────────────┘
  │  ── 4-member INK4 ──   │                   │ phosphorylates
  │  [no fly homolog]      │                   │ (Ser/Thr residues)
  └────────────────────────┘                   ▼
                              ┌────────────────────────────────────┐
                              │   POCKET PROTEIN FAMILY  ●●○○      │
                              │                                    │
                              │   ┌──────┐  ┌──────┐  ┌──────┐   │
                              │   │ Rb1  │  │ p107 │  │ p130 │   │
                              │   │(1°)  │  │      │  │      │   │
                              │   └──────┘  └──────┘  └──────┘   │
                              │      3 paralogs [fly: RBF1+RBF2]  │
                              └──────────────────┬─────────────────┘
                                                 │ partially releases E2F
                               ┌─────────────────┴──────────────────┐
                               ▼                                     ▼
                  ┌────────────────────────┐          ┌──────────────────────┐
                  │  E2F1–4 · DP1/2        │─────────▶│   Cyclin E1 · E2     │
                  │  (partial; activating) │  drives  │   transcription ↑    │
                  │  [8-member family      │          └──────────────────────┘
                  │   in mammals vs 2 fly] │
                  └────────────────────────┘
                              │
                              │ also drives
                              ▼
                  ┌────────────────────────┐
                  │  p19^ARF transcription │  ← E2F1 failsafe arm
                  │  ARF sequesters Mdm2   │
                  │  → p53 stabilised      │
                  │  → apoptosis/senescence│
                  └────────────────────────┘

                                          │ (Cyclin E activates)
                                          ▼
  ┌─────────────────────────┐    ┌─────────────────────────────┐
  │  p21^CIP1  (p53/damage) │    │      Cyclin E · CDK2         │
  │  p27^KIP1  (quiescence) │━━━⊣│   Late G1 · Restriction pt.  │
  │  p57^KIP2  (development)│    └──────────────┬──────────────┘
  └─────────────────────────┘                   │ hyperphosphorylates
                                                │
                                                ▼
                         ┌──────────────────────────────────────┐
                         │     ppRb / pp107 / pp130  ●●●●        │
                         │     HYPERPHOSPHORYLATED · INACTIVE    │
                         │     pocket domain unfolded            │
                         └──────────────────┬───────────────────┘
                                            │ fully releases
                                            ▼
                    ┌──────────────────────────────────────────┐
                    │          E2F FULLY RELEASED               │
                    │   E2F1–3 transactivation domains unmasked │
                    └─────────────────────┬────────────────────┘
                                          │ drives transcription
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │       S-PHASE GENE TRANSCRIPTION          │
                    │   Pcna · Mcm2-7 · Ccna2 · Cdc25a · Rrm2  │
                    └─────────────────────┬────────────────────┘
                                          │
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │           CELL CYCLE ENTRY                │
                    │              G1 ──▶ S phase               │
                    └──────────────────────────────────────────┘
```

> **Symbol key:**
> `━━━⊣` = inhibition &nbsp;|&nbsp; `──▶` = activation &nbsp;|&nbsp;
> `●●○○` = partial phosphorylation &nbsp;|&nbsp; `●●●●` = hyperphosphorylated &nbsp;|&nbsp;
> `[...]` = species comparison note

---

## Mouse vs. Fly — Key Structural Differences

| Component | *Drosophila* | *Mus musculus* | What it means |
|---|---|---|---|
| **Cyclin D** | 1 isoform | D1, D2, D3 (3) | Tissue-specific regulation; D1=breast, D2=B-cells, D3=haematopoietic |
| **CDK4/6** | Cdk4 only | CDK4 + CDK6 | CDK6 dominates in lymphoid/haematopoietic lineages |
| **Pocket proteins** | RBF1 + RBF2 | Rb1, p107, p130 (3) | Overlapping but non-redundant; p107/p130 compensate during development |
| **INK4 family** | **None** | p16, p15, p18, p19 (4) | Major gap — fly has no INK4 homolog; p15 induced by TGF-β |
| **E2F family** | dE2F1 + dE2F2 | E2F1–8 (8) | Activating (E2F1–3) vs repressive (E2F4–8) specialisation |
| **CIP/KIP family** | Dacapo (1) | p21, p27, p57 (3) | p57 important in embryonic development |
| **ARF/p53 failsafe** | Partial | p19^ARF fully wired to p53 | Robust; co-deletion of Rb1+Trp53 required to escape |
| **TGF-β feedback** | Absent | p15^INK4b induced by TGF-β | Anti-mitogenic loop that restrains CDK4/6 |

---

## Mouse vs. Human — Key Differences

Despite ~95% conservation of pathway architecture, important divergences exist:

**Tumour spectrum after Rb1 loss**
In mouse, germline *Rb1* heterozygosity leads primarily to **pituitary and thyroid tumours**, not retinoblastoma. Human *RB1* mutation causes **retinoblastoma**. This reflects species differences in retinal progenitor cell biology and the degree of p107/p130 compensation in the mouse retina.

**Rb1 knockout lethality**
Complete *Rb1* knockout in mouse causes **embryonic lethality at E14.5** due to defects in erythropoiesis and neurogenesis. Human *RB1* homozygous loss is tolerated somatically — only specific cell types (retinal precursors, osteoblasts) become tumourigenic. This limits how well mouse knockouts model the human germline disease.

**p19^ARF vs p14^ARF**
Both arise from the *Cdkn2a* locus via alternative reading frames. Mouse p19^ARF and human p14^ARF are functionally equivalent but share limited sequence identity (~50%) — both sequester Mdm2/MDM2 to stabilise p53.

**CDK4 R24C**
The CDK4 point mutation that abolishes p16 binding causes **familial melanoma** in both species — one of the strongest pieces of evidence for direct translational relevance of this node.

---

## The p53 Failsafe — Critical for Translational Modelling

```
  Rb1 loss
     │
     ▼
  E2F1 deregulated
     │
     ▼
  p19^ARF transcribed   ←── This step is E2F1-dependent
     │
     ▼
  ARF sequesters Mdm2 in nucleolus
     │
     ▼
  p53 stabilised + activated
     │
     ├──▶  p21^CIP1 → G1 arrest
     │
     └──▶  Bax · Puma · Noxa → Apoptosis

  ══════════════════════════════════════════════
  To escape: tumour must ALSO inactivate p53
  Mouse models: Rb1 loss + Trp53 loss (compound KO)
  Human cancers: RB1 loss + TP53 mutation/MDM2 amp
  ══════════════════════════════════════════════
```

---

## The Restriction Point — Positive Feedback Loop

Once Cyclin E·CDK2 fires, the cell is irreversibly committed to S phase:

```
E2F released → Cyclin E ↑ → CDK2 ↑ → ppRb ↑ → more E2F released
     ▲___________________________________________________|
```

This loop is fully conserved across fly, mouse, and human.
The mouse adds further amplification via **Cyclin A·CDK2**, which also maintains Rb hyperphosphorylation through S and G2 phases.

---

## Pathway Disruption in Mouse Cancer Models

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  GENE / LOCUS      │  ALTERATION             │  MOUSE PHENOTYPE                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Rb1               │  Germline KO (het)      │  Pituitary & thyroid tumours     │
│  Rb1               │  Homozygous KO          │  Embryonic lethal (E14.5)        │
│  Cdkn2a (p16/ARF)  │  Homozygous deletion    │  Lymphomas, sarcomas, melanomas  │
│  Ccnd1 (Cyclin D1) │  Transgenic OE          │  Mammary adenocarcinoma          │
│  Cdk4 (R24C KI)    │  Cannot bind p16        │  Melanoma, pituitary, sarcoma    │
│  Rb1 + Trp53       │  Compound KO            │  Accelerated tumourigenesis      │
│  E2f1              │  Knockout               │  Testicular atrophy, T-cell lymphoma │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Three-Species Comparison Summary

```
COMPONENT          DROSOPHILA        MOUSE             HUMAN
─────────────────────────────────────────────────────────────
Rb family          RBF1, RBF2        Rb1, p107, p130   RB1, p107, p130
E2F family         dE2F1, dE2F2      E2F1–8            E2F1–8
Cyclin D           1×                D1, D2, D3        D1, D2, D3
CDK4/6             Cdk4 only         CDK4 + CDK6       CDK4 + CDK6
INK4 inhibitors    NONE              p16/15/18/19 (4)  p16/15/18/19 (4)
CIP/KIP inhibitors Dacapo (1)        p21, p27, p57     p21, p27, p57
ARF/p53 failsafe   Partial           p19ARF — robust   p14ARF — robust
TGF-β arm          Absent            p15^INK4b ↑       p15^INK4b ↑
Tumour on Rb loss  Eye/wing disc     Pituitary/thyroid Retina/bone
─────────────────────────────────────────────────────────────
Conservation:      Core logic ✓      ~95% to human     Reference
```

---

*Mouse gene names follow MGI convention (lowercase italic): **Rb1**, **Cdkn2a**, **Ccnd1**, **Trp53**.
Human orthologs use uppercase: **RB1**, **CDKN2A**, **CCND1**, **TP53**.*
