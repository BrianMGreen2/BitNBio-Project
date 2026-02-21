# RB1 Tumor Suppressor Pathway
### Cell Cycle Regulation · G1 → S Phase Checkpoint

---

## Pathway Diagram

```
                    ┌─────────────────────────────────────┐
                    │         MITOGENIC SIGNALS            │
                    │   EGF · IGF-1 · Ras/ERK · PI3K/AKT  │
                    └──────────────────┬──────────────────┘
                                       │ induces
                                       ▼
  ┌─────────────────────┐     ┌────────────────────────┐
  │   p16^INK4a         │     │   Cyclin D · CDK4/6    │
  │   (CDKN2A)          │━━━⊣ │   Early G1 complex     │
  │   TUMOR SUPPRESSOR  │     └────────────┬───────────┘
  └─────────────────────┘                  │ phosphorylates
                                           │ (Ser780/795)
                                           ▼
                         ┌─────────────────────────────┐
                         │         pRb  ●●○○            │
                         │   PARTIAL PHOSPHORYLATION    │
                         │      (brake loosening)       │
                         └──────────────┬──────────────┘
                                        │ partially releases E2F
                          ┌─────────────┴──────────────┐
                          ▼                             ▼
               ┌──────────────────┐       ┌────────────────────┐
               │  E2F (partial)   │──────▶│    Cyclin E        │
               │  low-level       │drives │  transcription ↑   │
               │  transcription   │       └────────────────────┘
               └──────────────────┘                 │
                                                     │ activates
                                                     ▼
  ┌─────────────────────┐     ┌────────────────────────────┐
  │   p21^CIP1 · p27    │     │   Cyclin E · CDK2          │
  │   (CDKN1A/CDKN1B)   │━━━⊣ │   Late G1 complex          │
  │   TUMOR SUPPRESSOR  │     └────────────┬───────────────┘
  └─────────────────────┘                  │ hyperphosphorylates
                                           │ (Ser567, Thr373 +)
                                           ▼
                         ┌─────────────────────────────┐
                         │        ppRb  ●●●●            │
                         │    HYPERPHOSPHORYLATED       │
                         │    pocket domain unfolded    │
                         │         (INACTIVE)           │
                         └──────────────┬──────────────┘
                                        │ fully releases
                                        ▼
                    ┌─────────────────────────────────────┐
                    │        E2F FULLY RELEASED            │
                    │   transactivation domain unmasked   │
                    └──────────────────┬──────────────────┘
                                       │ drives transcription
                                       ▼
                    ┌─────────────────────────────────────┐
                    │     S-PHASE GENE TRANSCRIPTION       │
                    │  PCNA · MCM2-7 · Cyclin A · CDC25A  │
                    └──────────────────┬──────────────────┘
                                       │
                                       ▼
                    ┌─────────────────────────────────────┐
                    │          CELL CYCLE ENTRY            │
                    │            G1 ──▶ S phase            │
                    └─────────────────────────────────────┘
```

> **Symbol key:**  
> `━━━⊣` = inhibition &nbsp;|&nbsp; `──▶` = activation &nbsp;|&nbsp; `●●○○` = partial phosphorylation &nbsp;|&nbsp; `●●●●` = hyperphosphorylated

---

## Key Players

| Molecule | Role | State in Active Pathway |
|---|---|---|
| **pRb** | Tumor suppressor / brake | Hypophosphorylated → binds & silences E2F |
| **ppRb** | Inactivated pRb | Hyperphosphorylated → releases E2F |
| **Cyclin D · CDK4/6** | Early G1 kinase complex | Partially phosphorylates pRb |
| **Cyclin E · CDK2** | Late G1 kinase complex | Hyperphosphorylates pRb (point of no return) |
| **E2F 1–3** | Transcription factor | Drives S-phase gene expression when released |
| **p16^INK4a** | CDK inhibitor (INK4 family) | Blocks CDK4/6 → keeps pRb active |
| **p21^CIP1 / p27** | CDK inhibitors (CIP/KIP family) | Blocks CDK2 → keeps pRb active |

---

## The Restriction Point

The **Cyclin E · CDK2** step is the point of no return.  
Once this fires, a **positive feedback loop** is established:

```
E2F released → Cyclin E ↑ → CDK2 activity ↑ → ppRb ↑ → more E2F released
      ▲_____________________________________________________|
```

The cell is now irreversibly committed to S phase regardless of external signals.

---

## Cancer: How Each Node Is Hijacked

```
┌──────────────────────────────────────────────────────────────────────┐
│  NODE               │  ALTERATION          │  CANCER TYPE           │
├──────────────────────────────────────────────────────────────────────┤
│  RB1                │  Deletion/mutation   │  Retinoblastoma, SCLC  │
│  p16^INK4a (CDKN2A) │  Promoter silencing  │  Melanoma, pancreatic  │
│  Cyclin D1          │  Amplification       │  Breast, head & neck   │
│  CDK4 / CDK6        │  Amplification       │  Liposarcoma, breast   │
│  CDK4 (R24C mutant) │  Cannot bind p16     │  Familial melanoma     │
│  HPV E7 oncoprotein │  Degrades pRb        │  Cervical cancer       │
│  Adenovirus E1A     │  Binds pRb pocket    │  —                     │
└──────────────────────────────────────────────────────────────────────┘
```

> **Net result in all cases:** pRb is permanently inactivated → E2F constitutively
> active → uncontrolled cell proliferation.

---

## Therapeutic Targeting

| Drug Class | Examples | Mechanism | Limitation |
|---|---|---|---|
| **CDK4/6 inhibitors** | Palbociclib, Ribociclib, Abemaciclib | Restore pRb activity | Only works if **RB1 is intact** |
| **MDM2 inhibitors** | Nutlin-3a, RG7388 | Reactivate p53 (retinoblastoma) | p53 must be wild-type |
| **EZH2 inhibitors** | Tazemetostat | Target RB1-null epigenetic dependency | Investigational |
| **Aurora kinase inhibitors** | Alisertib | Exploit mitotic vulnerability in RB1-loss | Investigational |

---

*RBF is the Drosophila melanogaster homolog of human RB1 — functionally conserved across ~600 million years of evolution.*
