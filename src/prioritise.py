#!/usr/bin/env python3
"""
Who Gives a Fly — Content Prioritisation Tool
===============================================
Ranks curation and enrichment work by expected impact on risk score precision.

Combines three signals for each gap:
  1. Current risk level of the component (higher risk = more urgent to get right)
  2. Evidence tier of the affected dimension (inferred = most uncertain)
  3. Dimension weight in the composite score (D1 30%, D2/D3/D4 20%, D5 10%)

Outputs a ranked action backlog — what to do first, why, and how.

Usage:
    python prioritise.py                          # full backlog
    python prioritise.py --pathway rb_pathway     # single pathway
    python prioritise.py --top 10                 # top N items only
    python prioritise.py --format csv             # machine-readable
    python prioritise.py --mode enrich            # API enrichment tasks only
    python prioritise.py --mode curate            # literature curation tasks only
    python prioritise.py --mode all               # both (default)
"""

import json
import os
import argparse
import csv
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


# ─────────────────────────────────────────────────────────
# Scoring model
# ─────────────────────────────────────────────────────────

# Impact weight of each dimension on composite score precision
DIM_WEIGHTS = {"D1": 0.30, "D2": 0.20, "D3": 0.20, "D4": 0.20, "D5": 0.10}

# Urgency multiplier by current risk level
RISK_URGENCY = {"critical": 4.0, "high": 3.0, "moderate": 2.0, "low": 1.0}

# Score uncertainty reduction from upgrading inference → ground-truth
# D1/D2 inferred from conservation_score float (fairly reliable) → lower gain
# D3/D4/D5 inferred from free-text keyword scan → high uncertainty, large gain
INFERENCE_GAIN = {"D1": 0.4, "D2": 0.5, "D3": 0.9, "D4": 1.0, "D5": 0.8}

# Enrichment type mapping: which tool/source addresses which dimension
ENRICH_SOURCE = {
    "D1": {"tool": "data_enricher.py", "api": "Ensembl", "prereq": "ensembl_id in pathways.json"},
    "D2": {"tool": "data_enricher.py", "api": "Ensembl", "prereq": "ensembl_id in pathways.json"},
    "D3": {"tool": "validate_evidence.py", "api": "GTEx / curator", "prereq": "gencode_id + tissue curation"},
    "D4": {"tool": "validate_evidence.py", "api": "PubMed / curator", "prereq": "phenotypic_evidence entries"},
    "D5": {"tool": "validate_evidence.py + data_enricher.py", "api": "ChEMBL / curator", "prereq": "pharmacological_evidence entries"},
}

EVIDENCE_KEYS = {"D3": "regulatory_context", "D4": "phenotypic_evidence", "D5": "pharmacological_evidence"}

SPECIES_ORDER = ["drosophila", "mouse", "zebrafish", "worm"]


@dataclass
class PriorityItem:
    rank:          int
    pathway_id:    str
    component_id:  str
    species:       str
    dimension:     str
    action_type:   str          # "enrich" | "curate"
    priority_score: float
    current_risk:  str
    evidence_key:  str
    tool:          str
    api_source:    str
    prereq:        str
    rationale:     str
    estimated_effort: str       # "low" | "medium" | "high"
    impact_on_composite: float  # approximate improvement in composite score precision


# ─────────────────────────────────────────────────────────
# Gap detection
# ─────────────────────────────────────────────────────────

def get_component_risk(component: dict) -> str:
    """Return the current translational_risk or infer from flags."""
    return component.get("translational_risk", "moderate")


def has_ensembl_ids(component: dict) -> bool:
    h = component.get("orthologs", {}).get("human", {})
    return bool(h.get("ensembl_id")) and bool(h.get("gencode_id"))


def has_enriched_file(pathway_id: str, component_id: str,
                       enriched_dir: str = "data/enriched") -> bool:
    path = os.path.join(enriched_dir, f"{pathway_id}__{component_id}__enriched.json")
    return os.path.exists(path)


def has_structured_evidence(component: dict, dim: str) -> bool:
    key = EVIDENCE_KEYS.get(dim)
    if not key:
        return True   # D1/D2 handled via enriched files
    evidence = component.get(key)
    if not evidence:
        return False
    # Check at least one validated/enriched entry
    entries = evidence if isinstance(evidence, list) else list(evidence.values())
    return any(e.get("evidence_tier") in ("validated", "enriched") for e in entries
               if isinstance(e, dict))


def estimate_effort(dim: str, component: dict) -> str:
    """Rough effort estimate for filling a gap."""
    if dim in ("D1", "D2"):
        return "low"       # API call once ensembl_id present
    if dim == "D5":
        gene = component.get("orthologs", {}).get("human", {}).get("symbol", "")
        if gene in ("RB1", "CDK4", "CDK6", "TP53", "APC", "NOTCH1"):
            return "low"   # well-studied targets, ChEMBL data abundant
        return "medium"
    if dim == "D3":
        return "medium"    # regulatory context needs 4 sub-questions per species
    if dim == "D4":
        return "high"      # requires reading primary literature per species
    return "medium"


def compute_priority_score(risk: str, dim: str,
                            action_type: str) -> tuple[float, float]:
    """Return (priority_score, impact_on_composite)."""
    urgency = RISK_URGENCY.get(risk, 1.0)
    weight  = DIM_WEIGHTS.get(dim, 0.1)
    gain    = INFERENCE_GAIN.get(dim, 0.5)
    # API enrichment is lower marginal gain than curator validation
    # (API data is accurate for D1/D2 but less interpretive)
    action_multiplier = 1.0 if action_type == "curate" else 0.7
    score  = urgency * weight * gain * action_multiplier
    impact = weight * gain * action_multiplier * 0.2   # rough composite improvement
    return round(score, 4), round(impact, 4)


def build_rationale(component: dict, dim: str, species: str,
                     action_type: str, risk: str) -> str:
    symbol = component.get("orthologs", {}).get("human", {}).get("symbol", component["id"])
    comp_sym = component.get("orthologs", {}).get(species, {}).get("symbol", "?")
    risk_phrase = {"critical": "Critical Gap", "high": "High Risk",
                   "moderate": "Moderate Risk", "low": "Low Risk"}.get(risk, risk)
    dim_phrase = {
        "D1": "sequence conservation score",
        "D2": "paralog complexity score",
        "D3": "regulatory context score (D3 — highest inference noise)",
        "D4": "phenotypic validity score (D4 — directly affects clinical confidence)",
        "D5": "therapeutic evidence score",
    }.get(dim, dim)

    if action_type == "enrich":
        return (f"{symbol}/{comp_sym} is currently {risk_phrase}. "
                f"API enrichment would replace inferred {dim_phrase} with Ensembl ground-truth data.")
    else:
        return (f"{symbol}/{comp_sym} is currently {risk_phrase}. "
                f"Literature curation would replace inferred {dim_phrase} "
                f"with PMID-backed structured evidence, directly affecting risk classification.")


# ─────────────────────────────────────────────────────────
# Main prioritisation engine
# ─────────────────────────────────────────────────────────

def build_priority_list(
    pathways_db: dict,
    pathway_filter: Optional[str] = None,
    mode: str = "all",
    enriched_dir: str = "data/enriched",
) -> list[PriorityItem]:

    items = []
    species_list = list(pathways_db["metadata"]["species"].keys())
    species_list = [s for s in SPECIES_ORDER if s in species_list]

    for pathway in pathways_db["pathways"]:
        pid = pathway["id"]
        if pathway_filter and pathway_filter != "all" and pid != pathway_filter:
            continue

        for comp in pathway.get("components", []):
            cid  = comp["id"]
            risk = get_component_risk(comp)
            has_ids = has_ensembl_ids(comp)
            has_enriched = has_enriched_file(pid, cid, enriched_dir)

            for sp in species_list:
                if sp == "human":
                    continue
                # Skip if no ortholog at all
                comp_sym = comp.get("orthologs", {}).get(sp, {}).get("symbol", "")
                if comp_sym in ("NONE", ""):
                    continue

                # D1/D2: API enrichment gaps
                if mode in ("all", "enrich"):
                    for dim in ("D1", "D2"):
                        if not has_enriched:
                            if not has_ids:
                                # Prerequisite gap — add IDs first
                                score, impact = compute_priority_score(risk, dim, "enrich")
                                items.append(PriorityItem(
                                    rank=0, pathway_id=pid, component_id=cid,
                                    species=sp, dimension=dim,
                                    action_type="prereq",
                                    priority_score=score * 0.5,  # lower — needs ID first
                                    current_risk=risk,
                                    evidence_key="ensembl_id",
                                    tool="manual edit pathways.json",
                                    api_source="Ensembl gene lookup",
                                    prereq="none",
                                    rationale=f"Add ensembl_id and gencode_id to {cid} human ortholog entry before D1/D2 enrichment can run.",
                                    estimated_effort="low",
                                    impact_on_composite=impact,
                                ))
                                break  # one prereq item per component, not per dim+species
                            else:
                                score, impact = compute_priority_score(risk, dim, "enrich")
                                items.append(PriorityItem(
                                    rank=0, pathway_id=pid, component_id=cid,
                                    species=sp, dimension=dim,
                                    action_type="enrich",
                                    priority_score=score,
                                    current_risk=risk,
                                    evidence_key="D1_ensembl / D2_ensembl",
                                    tool=ENRICH_SOURCE[dim]["tool"],
                                    api_source=ENRICH_SOURCE[dim]["api"],
                                    prereq=ENRICH_SOURCE[dim]["prereq"],
                                    rationale=build_rationale(comp, dim, sp, "enrich", risk),
                                    estimated_effort=estimate_effort(dim, comp),
                                    impact_on_composite=impact,
                                ))

                # D3/D4/D5: literature curation gaps
                if mode in ("all", "curate"):
                    for dim in ("D3", "D4", "D5"):
                        if not has_structured_evidence(comp, dim):
                            score, impact = compute_priority_score(risk, dim, "curate")
                            items.append(PriorityItem(
                                rank=0, pathway_id=pid, component_id=cid,
                                species=sp, dimension=dim,
                                action_type="curate",
                                priority_score=score,
                                current_risk=risk,
                                evidence_key=EVIDENCE_KEYS[dim],
                                tool=ENRICH_SOURCE[dim]["tool"],
                                api_source=ENRICH_SOURCE[dim]["api"],
                                prereq=ENRICH_SOURCE[dim]["prereq"],
                                rationale=build_rationale(comp, dim, sp, "curate", risk),
                                estimated_effort=estimate_effort(dim, comp),
                                impact_on_composite=impact,
                            ))

    # Deduplicate prereq items (one per component, not per species×dim)
    seen_prereqs = set()
    deduped = []
    for item in items:
        if item.action_type == "prereq":
            key = (item.pathway_id, item.component_id)
            if key in seen_prereqs:
                continue
            seen_prereqs.add(key)
        deduped.append(item)

    # Sort by priority score descending, then by risk level, then by dim weight
    risk_order = {"critical": 0, "high": 1, "moderate": 2, "low": 3}
    dim_order  = {"D4": 0, "D3": 1, "D5": 2, "D1": 3, "D2": 4}
    deduped.sort(key=lambda x: (
        -x.priority_score,
        risk_order.get(x.current_risk, 9),
        dim_order.get(x.dimension, 9),
    ))

    # Assign ranks
    for i, item in enumerate(deduped):
        item.rank = i + 1

    return deduped


# ─────────────────────────────────────────────────────────
# Output formatters
# ─────────────────────────────────────────────────────────

RISK_ICON = {"critical": "💀", "high": "🚫", "moderate": "⚠️", "low": "✅"}
ACTION_ICON = {"curate": "📚", "enrich": "🔌", "prereq": "🔑"}
EFFORT_ICON = {"low": "◎", "medium": "◑", "high": "●"}


def print_backlog(items: list[PriorityItem], top_n: Optional[int] = None):
    show = items[:top_n] if top_n else items

    # Summary header
    total = len(items)
    curate_n = sum(1 for i in items if i.action_type == "curate")
    enrich_n = sum(1 for i in items if i.action_type == "enrich")
    prereq_n = sum(1 for i in items if i.action_type == "prereq")
    critical_n = sum(1 for i in items if i.current_risk == "critical")
    high_n     = sum(1 for i in items if i.current_risk == "high")

    print(f"\n{'═'*72}")
    print(f"  WHO GIVES A FLY — CURATION PRIORITY BACKLOG")
    print(f"{'═'*72}\n")
    print(f"  Total gaps:   {total}")
    print(f"  📚 Curate:    {curate_n}   (D3/D4/D5 — literature, PubMed, ChEMBL)")
    print(f"  🔌 Enrich:    {enrich_n}   (D1/D2 — API: Ensembl, GTEx)")
    print(f"  🔑 Prereq:    {prereq_n}   (add ensembl_id/gencode_id to pathways.json first)")
    print(f"  💀 Critical-risk gaps: {critical_n}")
    print(f"  🚫 High-risk gaps:     {high_n}")
    if top_n:
        print(f"\n  Showing top {top_n} of {total} items.\n")
    else:
        print()

    print(f"  {'#':<4} {'Risk':<10} {'Component':<18} {'Sp':<12} {'Dim':<4} "
          f"{'Type':<7} {'Eff':<3} {'Score':<7} {'Action'}")
    print(f"  {'─'*4} {'─'*10} {'─'*18} {'─'*12} {'─'*4} "
          f"{'─'*7} {'─'*3} {'─'*7} {'─'*40}")

    for item in show:
        risk_str  = f"{RISK_ICON.get(item.current_risk,'')} {item.current_risk}"
        type_str  = f"{ACTION_ICON.get(item.action_type,'')} {item.action_type}"
        eff_str   = EFFORT_ICON.get(item.estimated_effort, "?")
        score_str = f"{item.priority_score:.3f}"

        # One-line action
        if item.action_type == "prereq":
            action = f"Add ensembl_id to {item.component_id}/human in pathways.json"
        elif item.action_type == "enrich":
            action = f"python data_enricher.py --pathway {item.pathway_id} --component {item.component_id}"
        else:
            action = f"python validate_evidence.py --template {item.component_id} --pathway {item.pathway_id} --species {item.species}"

        print(f"  {item.rank:<4} {risk_str:<10} {item.component_id:<18} {item.species:<12} "
              f"{item.dimension:<4} {type_str:<7} {eff_str:<3} {score_str:<7} {action}")

    print()
    print(f"  Effort: ◎ low (<30min)  ◑ medium (1–3hr)  ● high (half-day+)\n")

    # Top 3 rationales
    print(f"  TOP PRIORITY RATIONALES:\n")
    for item in show[:3]:
        print(f"  [{item.rank}] {item.component_id} / {item.species} / {item.dimension}")
        print(f"      {item.rationale}")
        print(f"      Tool: {item.tool}")
        print(f"      Expected composite improvement: ~{item.impact_on_composite:.2f}\n")


def write_csv(items: list[PriorityItem], path: str):
    fields = ["rank", "pathway_id", "component_id", "species", "dimension",
              "action_type", "priority_score", "current_risk", "evidence_key",
              "tool", "api_source", "prereq", "estimated_effort",
              "impact_on_composite", "rationale"]
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for item in items:
            row = asdict(item)
            writer.writerow({k: row[k] for k in fields})
    print(f"  ✓ CSV written → {path}")


def write_json(items: list[PriorityItem], path: str):
    with open(path, "w") as f:
        json.dump([asdict(i) for i in items], f, indent=2)
    print(f"  ✓ JSON written → {path}")


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Who Gives a Fly — Content Prioritisation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python prioritise.py                            # full ranked backlog
  python prioritise.py --top 10                  # top 10 items
  python prioritise.py --pathway rb_pathway      # one pathway only
  python prioritise.py --mode curate             # literature tasks only
  python prioritise.py --mode enrich             # API tasks only
  python prioritise.py --format csv --output backlog.csv
  python prioritise.py --format json --output backlog.json
        """
    )
    parser.add_argument("--pathway",  default="all",     help="Pathway ID or 'all'")
    parser.add_argument("--mode",     default="all",     choices=["all","curate","enrich"], help="Filter by action type")
    parser.add_argument("--top",      type=int,          help="Show top N items only")
    parser.add_argument("--format",   default="table",   choices=["table","csv","json"])
    parser.add_argument("--output",   default=None,      help="Output file path (csv/json)")
    parser.add_argument("--pathways", default="config/pathways.json")
    parser.add_argument("--enriched-dir", default="data/enriched")
    args = parser.parse_args()

    with open(args.pathways) as f:
        db = json.load(f)

    items = build_priority_list(
        db,
        pathway_filter=args.pathway,
        mode=args.mode,
        enriched_dir=args.enriched_dir,
    )

    if args.format == "table":
        print_backlog(items, top_n=args.top)
    elif args.format == "csv":
        out = args.output or "priority_backlog.csv"
        write_csv(items[:args.top] if args.top else items, out)
    elif args.format == "json":
        out = args.output or "priority_backlog.json"
        write_json(items[:args.top] if args.top else items, out)


if __name__ == "__main__":
    main()
