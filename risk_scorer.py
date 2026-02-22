#!/usr/bin/env python3
"""
Who Gives a Fly — Translational Risk Scoring Engine
====================================================
Implements the five-dimension weighted scoring rubric defined in
config/translational_risk_rubric.json. Produces structured risk
assessment records for every pathway component × model species pair.

Usage:
    python risk_scorer.py --pathway rb_pathway --species drosophila
    python risk_scorer.py --pathway all --species drosophila mouse zebrafish worm
    python risk_scorer.py --validate-rubric
    python risk_scorer.py --example
"""

import json
import argparse
import os
import sys
from datetime import date, datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


# ─────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────

@dataclass
class DimensionScore:
    raw:       int          # 0–5
    rationale: str
    dimension: str
    scored_by: str = "inferred"   # "ground_truth" | "enriched" | "inferred"

    @property
    def normalised(self) -> float:
        return self.raw / 5.0


@dataclass
class ModifierApplication:
    rule_id:  str
    value:    float
    reason:   str


@dataclass
class OverrideApplication:
    rule_id:    str
    elevated_to: str
    reason:     str


@dataclass
class RiskAssessment:
    assessment_id:           str
    pathway_id:              str
    component_id:            str
    ref_species:             str
    model_species:           str
    assessed_date:           str
    evidence_tier:           str

    D1: DimensionScore
    D2: DimensionScore
    D3: DimensionScore
    D4: DimensionScore
    D5: DimensionScore

    composite_raw:      float
    composite_modified: float
    modifiers_applied:  list
    overrides_applied:  list

    final_risk:  str
    risk_label:  str
    risk_icon:   str
    action:      str
    flags_raised: list
    summary_narrative: str

    evidence_references: list = field(default_factory=list)



def _compute_evidence_tier(*dims) -> str:
    """
    Compute record-level evidence_tier from all dimension scored_by values.
    - "validated"  : all inferred-mode dims are D1 or D2 (sequence/paralogs — less critical)
                     AND at least one of D3/D4/D5 is ground_truth or enriched
    - "partial"    : mix of inferred and ground_truth/enriched across D3/D4/D5
    - "inferred"   : D3, D4, and D5 are all inferred
    """
    critical_dims = [d for d in dims if d.dimension in ("D3", "D4", "D5")]
    tiers = set(d.scored_by for d in critical_dims)
    if all(t == "inferred" for t in (d.scored_by for d in critical_dims)):
        return "inferred"
    if all(t in ("validated", "ground_truth", "enriched")
           for t in (d.scored_by for d in critical_dims)):
        return "validated"
    return "partial"

# ─────────────────────────────────────────────────────────
# Scoring engine
# ─────────────────────────────────────────────────────────

class TranslationalRiskScorer:
    """
    Computes translational risk scores for pathway components
    using the five-dimension weighted rubric.
    """

    WEIGHTS = {
        "D1": 0.30,  # Sequence conservation
        "D2": 0.20,  # Paralog complexity
        "D3": 0.20,  # Regulatory context
        "D4": 0.20,  # Phenotypic validity
        "D5": 0.10,  # Therapeutic evidence
    }

    # Maps (conservation_level from pathways.json) → D1 raw score
    CONSERVATION_LEVEL_TO_D1 = {
        "very_high": 5,
        "high":      4,
        "moderate":  3,
        "low":       2,
        "absent":    0,
    }

    # Maps qualitative translational_risk → approximate composite
    LEGACY_RISK_TO_COMPOSITE = {
        "low":      0.80,
        "moderate": 0.60,
        "high":     0.30,
    }

    RISK_THRESHOLDS = [
        (0.75, "low",      "Low Risk",      "✅", "Model organism findings are likely to translate directly. Proceed with confidence; document assumptions."),
        (0.50, "moderate", "Moderate Risk", "⚠️", "Translate with caution. Identify the divergent dimension(s) and design bridging experiments before clinical development."),
        (0.25, "high",     "High Risk",     "🚫", "Significant translational gap. Do not extrapolate without orthogonal validation in a higher-fidelity model or human cell system."),
        (0.00, "critical", "Critical Gap",  "💀", "Do not extrapolate. Use an alternative model or human-derived system (organoids, iPSCs, patient samples)."),
    ]

    def __init__(self, rubric: dict, pathways_db: dict):
        self.rubric     = rubric
        self.pathways   = pathways_db
        self.species_meta = pathways_db["metadata"]["species"]
        self.overrides  = rubric["aggregation"]["override_rules"]
        self.modifiers  = rubric["aggregation"]["modifier_rules"]
        self.flags_def  = rubric["flags"]

    # ── D1: Sequence conservation ──────────────────────────

    def score_D1(self, component: dict, ref: str, compare: str) -> DimensionScore:
        key     = f"{ref}_{compare}"
        alt_key = f"{compare}_{ref}"
        cons    = component.get("conservation", {})
        data    = cons.get(key) or cons.get(alt_key) or {}

        level  = data.get("level", "absent")
        score  = self.CONSERVATION_LEVEL_TO_D1.get(level, 0)
        notes  = data.get("notes", "No conservation data available.")
        seqid  = data.get("score", 0.0)

        # Refine: if score float doesn't match level, recalculate
        if seqid >= 0.90 and score < 5:
            score = 5
        elif seqid >= 0.70 and score < 4:
            score = 4
        elif seqid >= 0.45 and score < 3:
            score = 3
        elif seqid >= 0.20 and score < 2:
            score = 2
        elif seqid > 0.00 and score == 0:
            score = 1

        rationale = (
            f"Sequence identity: {seqid:.0%}. Conservation level: {level}. {notes}"
        )
        return DimensionScore(raw=score, rationale=rationale, dimension="D1")

    # ── D2: Paralog complexity ─────────────────────────────

    def score_D2(self, component: dict, ref: str, compare: str) -> DimensionScore:
        ref_orth  = component.get("orthologs", {}).get(ref, {})
        comp_orth = component.get("orthologs", {}).get(compare, {})

        ref_paralogs  = len(ref_orth.get("paralogs", []))
        comp_paralogs = len(comp_orth.get("paralogs", []))
        comp_symbol   = comp_orth.get("symbol", "—")

        # No homolog at all
        if comp_symbol in ("NONE", "—", "") or not comp_orth:
            return DimensionScore(
                raw=0,
                rationale=f"No homolog in {compare}. Paralog complexity irrelevant — component absent.",
                dimension="D2"
            )

        diff = abs(ref_paralogs - comp_paralogs)

        if diff == 0:
            score = 5
            verdict = "Equivalent paralog count."
        elif diff == 1:
            score = 4
            verdict = f"±1 paralog difference ({comp_paralogs} vs {ref_paralogs} in {ref})."
        elif diff <= 3:
            score = 3
            verdict = f"Moderate mismatch: {comp_paralogs} paralogs in {compare} vs {ref_paralogs} in {ref}."
        elif diff <= 5:
            score = 2
            verdict = f"Major mismatch: {comp_paralogs} paralogs in {compare} vs {ref_paralogs} in {ref}."
        else:
            score = 1
            verdict = f"Severe mismatch: single gene in {compare} vs large family ({ref_paralogs} paralogs) in {ref}."

        # Penalise if human has named paralogs and compare has none listed
        if ref_paralogs > 2 and comp_paralogs == 0 and comp_symbol != "NONE":
            score = max(score - 1, 1)
            verdict += f" Human has {ref_paralogs} named paralogs; none listed for {compare}."

        rationale = (
            f"{verdict} "
            f"Human paralogs: {ref_paralogs}. {compare.capitalize()} paralogs: {comp_paralogs}."
        )
        return DimensionScore(raw=score, rationale=rationale, dimension="D2")

    # ── D3: Regulatory context ─────────────────────────────

    def score_D3(self, component: dict, ref: str, compare: str) -> DimensionScore:
        """
        Scores D3 from structured regulatory_context block if present (ground truth),
        otherwise infers from conservation level and free-text notes.
        """
        key     = f"{ref}_{compare}"
        alt_key = f"{compare}_{ref}"

        # ── Ground-truth path ──────────────────────────────────────────────
        reg_ctx = component.get("regulatory_context", {})
        entry   = reg_ctx.get(key) or reg_ctx.get(alt_key)
        if entry and entry.get("evidence_tier") in ("validated", "enriched"):
            score = entry.get("score", 0)
            notes_text = entry.get("notes", "")
            tier  = entry.get("evidence_tier", "validated")
            rationale = (
                f"[{tier.upper()}] Regulatory context scored from structured entry. "
                f"Upstream conserved: {entry.get('upstream_inputs_conserved')}. "
                f"Downstream conserved: {entry.get('downstream_targets_conserved')}. "
                f"PTM sites conserved: {entry.get('ptm_sites_conserved')}. "
                f"Tissue expression overlap: {entry.get('tissue_expression_overlap')}. "
                f"Known rewiring: {entry.get('known_rewiring')}. "
                f"{notes_text}"
            )
            return DimensionScore(raw=score, rationale=rationale,
                                  dimension="D3", scored_by=tier)

        # ── Inference fallback ─────────────────────────────────────────────
        cons    = component.get("conservation", {})
        data    = cons.get(key) or cons.get(alt_key) or {}
        level   = data.get("level", "absent")
        notes   = data.get("notes", "").lower()
        comp_note = component.get("orthologs", {}).get(compare, {}).get("note", "").lower()

        base = self.CONSERVATION_LEVEL_TO_D1.get(level, 0)

        if any(w in notes for w in ["regulatory", "fully conserved", "equivalent pathway"]):
            base = min(base + 1, 5)
        if any(w in notes for w in ["conserved pathway", "same upstream", "identical"]):
            base = min(base + 1, 5)
        if any(w in notes for w in ["rewiring", "different upstream", "absent regulatory", "no tgf", "no ink4"]):
            base = max(base - 2, 0)
        if any(w in comp_note for w in ["different tissue", "no equivalent", "absent in", "not present"]):
            base = max(base - 1, 0)
        if "no true" in comp_note or "no clear" in comp_note:
            base = max(base - 2, 0)
        if compare == "drosophila":
            if "ink4" in component["id"].lower():
                base = 0
            if "tgf" in notes or "tgf" in comp_note:
                base = max(base - 2, 0)

        rationale = (
            f"[INFERRED] Regulatory context derived from conservation level ({level}) "
            f"and species-specific notes. "
            f"Add a 'regulatory_context.{key}' block to pathways.json to enable ground-truth scoring."
        )
        return DimensionScore(raw=base, rationale=rationale,
                              dimension="D3", scored_by="inferred")

    # ── D4: Phenotypic validity ────────────────────────────

    def score_D4(self, component: dict, ref: str, compare: str) -> DimensionScore:
        """
        Scores D4 from structured phenotypic_evidence entries if present (ground truth),
        otherwise infers from translational_notes and ortholog annotations.
        """
        # ── Ground-truth path ──────────────────────────────────────────────
        pheno_entries = [
            e for e in component.get("phenotypic_evidence", [])
            if e.get("model_species") == compare
            and e.get("evidence_tier") in ("validated", "enriched")
        ]
        if pheno_entries:
            # Score = max of individual evidence scores; flag contradictions
            supporting   = [e for e in pheno_entries if e.get("supports_validity", True)]
            contradicting = [e for e in pheno_entries if not e.get("supports_validity", True)]
            if contradicting and not supporting:
                score = 0
            else:
                score = max((e.get("score", 0) for e in supporting), default=1)
                if contradicting:
                    score = max(score - 1, 1)  # Penalise contradicting evidence
            pmids = [e.get("pmid") for e in pheno_entries if e.get("pmid")]
            tier  = pheno_entries[0].get("evidence_tier", "validated")
            rationale = (
                f"[{tier.upper()}] Phenotypic validity scored from {len(pheno_entries)} structured "
                f"evidence {'entry' if len(pheno_entries)==1 else 'entries'} "
                f"({len(supporting)} supporting, {len(contradicting)} contradicting). "
                f"PMIDs: {', '.join(pmids) if pmids else 'none'}. "
                f"Evidence types: {', '.join(set(e.get('evidence_type','?') for e in pheno_entries))}."
            )
            return DimensionScore(raw=score, rationale=rationale,
                                  dimension="D4", scored_by=tier)

        # ── Inference fallback ─────────────────────────────────────────────
        t_risk  = component.get("translational_risk", "moderate")
        t_notes = component.get("translational_notes", "").lower()
        comp_note = component.get("orthologs", {}).get(compare, {}).get("note", "").lower()

        # Strong positive signals
        if any(w in comp_note for w in ["rescue", "recapitulates", "validated model", "gold standard"]):
            score = 5
        elif any(w in comp_note for w in ["closely mirrors", "equivalent phenotype", "disease model"]):
            score = 4
        elif any(w in t_notes for w in ["fly useful", "mouse required", "zebrafish adequate"]):
            score = 3
        elif t_risk == "low":
            score = 4
        elif t_risk == "moderate":
            score = 3
        else:
            score = 2  # high risk starts at 2

        # Downward adjustments for known mismatches
        if "embryonic lethal" in comp_note or "lethal" in comp_note:
            score = max(score - 1, 1)
        if "poor model" in t_notes or "not predict" in t_notes or "cannot model" in t_notes:
            score = max(score - 2, 0)
        if "do not" in t_notes and compare in t_notes:
            score = max(score - 2, 0)
        if "not suitable" in comp_note or "unsuitable" in comp_note:
            score = max(score - 1, 0)

        # Specific known good models
        if compare == "mouse" and "gold standard" in comp_note:
            score = min(score + 1, 5)
        if compare == "drosophila" and "pathway-level" in t_notes:
            score = max(score, 3)

        rationale = (
            f"[INFERRED] Phenotypic validity estimated from translational notes and "
            f"ortholog-specific annotations for {compare}. "
            f"Legacy risk rating: {t_risk}. "
            f"Add 'phenotypic_evidence' entries for {compare} to pathways.json to enable ground-truth scoring."
        )
        return DimensionScore(raw=score, rationale=rationale,
                              dimension="D4", scored_by="inferred")

    # ── D5: Therapeutic evidence ───────────────────────────

    def score_D5(self, component: dict, ref: str, compare: str) -> DimensionScore:
        """
        Scores D5 from structured pharmacological_evidence entries if present (ground truth),
        otherwise infers from disease annotations and translational notes.
        """
        # ── Ground-truth path ──────────────────────────────────────────────
        pharm_entries = [
            e for e in component.get("pharmacological_evidence", [])
            if e.get("model_species") == compare
            and e.get("evidence_tier") in ("validated", "enriched")
        ]
        if pharm_entries:
            concordant   = [e for e in pharm_entries if e.get("concordance") is True]
            discordant   = [e for e in pharm_entries if e.get("concordance") is False]
            unknown      = [e for e in pharm_entries if e.get("concordance") is None]

            if discordant and not concordant:
                score = 0   # Override OR-03 will also fire
            else:
                score = max((e.get("score", 1) for e in concordant), default=1)
                if discordant:
                    score = max(score - 1, 1)

            pmids = [e.get("pmid") for e in pharm_entries if e.get("pmid")]
            drugs = list(set(e.get("drug", "") for e in pharm_entries if e.get("drug")))
            tier  = pharm_entries[0].get("evidence_tier", "validated")
            stages = list(set(e.get("clinical_stage") for e in pharm_entries if e.get("clinical_stage")))
            rationale = (
                f"[{tier.upper()}] Therapeutic evidence from {len(pharm_entries)} structured "
                f"{'entry' if len(pharm_entries)==1 else 'entries'} "
                f"({len(concordant)} concordant, {len(discordant)} discordant, {len(unknown)} unknown). "
                f"Drugs: {', '.join(drugs[:3]) if drugs else 'none'}. "
                f"Clinical stages: {', '.join(stages) if stages else 'not specified'}. "
                f"PMIDs: {', '.join(pmids) if pmids else 'none'}."
            )
            return DimensionScore(raw=score, rationale=rationale,
                                  dimension="D5", scored_by=tier)

        # ── Inference fallback ─────────────────────────────────────────────
        ref_orth  = component.get("orthologs", {}).get(ref, {})
        t_notes   = component.get("translational_notes", "").lower()
        disease   = ref_orth.get("disease", "").lower()

        if any(w in disease for w in ["approved", "fda"]):
            score = 5
        elif any(w in t_notes for w in ["fda-approved", "approved drug", "cdk4/6 inhibitor", "palbociclib"]):
            score = 4
        elif any(w in t_notes for w in ["clinical trial", "nutlin", "mdm2 inhibitor"]):
            score = 3
        elif any(w in t_notes for w in ["drug screen", "preclinical"]):
            score = 2
        elif t_notes == "" and disease == "":
            score = 1
        else:
            score = 2

        if any(w in t_notes for w in ["discordant", "fails in human", "not translate"]):
            score = 0
        if compare == "drosophila" and "do not use" in t_notes:
            score = max(score - 1, 1)
        if compare == "worm" and score > 2:
            score = 2

        rationale = (
            f"[INFERRED] Therapeutic evidence estimated from disease annotations and translational notes. "
            f"Disease context: '{ref_orth.get('disease', 'not specified')}'. "
            f"Add 'pharmacological_evidence' entries for {compare} to pathways.json to enable ground-truth scoring."
        )
        return DimensionScore(raw=score, rationale=rationale,
                              dimension="D5", scored_by="inferred")

    # ── Composite + risk level ─────────────────────────────

    def compute_composite(
        self, d1: DimensionScore, d2: DimensionScore, d3: DimensionScore,
        d4: DimensionScore, d5: DimensionScore
    ) -> float:
        return (
            d1.normalised * self.WEIGHTS["D1"] +
            d2.normalised * self.WEIGHTS["D2"] +
            d3.normalised * self.WEIGHTS["D3"] +
            d4.normalised * self.WEIGHTS["D4"] +
            d5.normalised * self.WEIGHTS["D5"]
        )

    def apply_modifiers(
        self, composite: float, component: dict, compare: str
    ) -> tuple[float, list]:
        applied = []
        comp_note = component.get("orthologs", {}).get(compare, {}).get("note", "").lower()
        t_notes   = component.get("translational_notes", "").lower()

        for rule in self.modifiers:
            rid = rule["rule_id"]
            mod = rule["modifier"]

            if rid == "MR-01" and "rescue" in comp_note:
                composite = min(composite + mod, 1.0)
                applied.append({"rule_id": rid, "value": mod, "reason": rule["condition"]})
            elif rid == "MR-02" and "concordance" in t_notes and "validated" in t_notes:
                composite = min(composite + mod, 1.0)
                applied.append({"rule_id": rid, "value": mod, "reason": rule["condition"]})
            elif rid == "MR-03" and ("different tissue" in t_notes or "not expressed" in comp_note):
                composite = max(composite + mod, 0.0)
                applied.append({"rule_id": rid, "value": mod, "reason": rule["condition"]})
            elif rid == "MR-04" and compare == "zebrafish" and "duplication" in comp_note:
                composite = max(composite + mod, 0.0)
                applied.append({"rule_id": rid, "value": mod, "reason": rule["condition"]})
            elif rid == "MR-05" and "convergent" in t_notes:
                composite = max(composite + mod, 0.0)
                applied.append({"rule_id": rid, "value": mod, "reason": rule["condition"]})

        return round(composite, 4), applied

    def apply_overrides(
        self, risk: str, d1: DimensionScore, d2: DimensionScore,
        d3: DimensionScore, d4: DimensionScore, d5: DimensionScore
    ) -> tuple[str, list]:
        applied = []
        for rule in self.overrides:
            rid = rule["rule_id"]
            elevate_to = rule["override_to"]

            triggered = False
            if rid == "OR-01" and d1.raw == 0:
                triggered = True
            elif rid == "OR-02" and d4.raw == 0:
                triggered = True
            elif rid == "OR-03" and d5.raw == 0:
                triggered = True
            elif rid == "OR-04" and d2.raw == 0 and d1.raw <= 2:
                triggered = True
            elif rid == "OR-05" and d3.raw <= 1 and d4.raw <= 1:
                triggered = True

            if triggered:
                applied.append({"rule_id": rid, "elevated_to": elevate_to, "reason": rule["rationale"]})
                # Elevate to worst of current vs override
                order = ["low", "moderate", "high", "critical"]
                if order.index(elevate_to) > order.index(risk):
                    risk = elevate_to

        return risk, applied

    def map_composite_to_risk(self, composite: float) -> tuple[str, str, str, str]:
        for threshold, level, label, icon, action in self.RISK_THRESHOLDS:
            if composite >= threshold:
                return level, label, icon, action
        return "critical", "Critical Gap", "💀", self.RISK_THRESHOLDS[-1][4]

    def evaluate_flags(self, component: dict, compare: str,
                       d1: DimensionScore, d2: DimensionScore) -> list:
        flags = []
        comp_note = component.get("orthologs", {}).get(compare, {}).get("note", "").lower()
        t_notes   = component.get("translational_notes", "").lower()
        comp_sym  = component.get("orthologs", {}).get(compare, {}).get("symbol", "")

        if d1.raw == 0 or comp_sym in ("NONE", ""):
            flags.append("no_homolog")
        if d2.raw <= 2 and "compensation" in comp_note:
            flags.append("paralog_compensation_risk")
        if "different tissue" in t_notes or "not expressed" in comp_note:
            flags.append("tissue_expression_mismatch")
        if "phosphorylation" in t_notes and "absent" in t_notes:
            flags.append("ptm_site_absent")
        if "rewiring" in t_notes or "different upstream" in t_notes:
            flags.append("regulatory_rewiring")
        if "embryonic" in comp_note and "developmental" in comp_note:
            flags.append("developmental_vs_somatic_mismatch")
        if "discordant" in t_notes or "fails in human" in t_notes:
            flags.append("drug_discordance")
        if compare == "zebrafish":
            ref_orth  = component.get("orthologs", {}).get("human", {})
            comp_orth = component.get("orthologs", {}).get(compare, {})
            n_ref  = len(ref_orth.get("paralogs", []))
            n_comp = len(comp_orth.get("paralogs", []))
            if n_comp > n_ref:
                flags.append("wgd_paralog_risk")

        return flags

    def generate_narrative(
        self, component: dict, compare: str, final_risk: str,
        composite: float, flags: list, d1: DimensionScore, d2: DimensionScore
    ) -> str:
        comp_name = compare.capitalize()
        comp_sym  = component.get("orthologs", {}).get(compare, {}).get("symbol", "—")
        ref_sym   = component.get("orthologs", {}).get("human", {}).get("symbol", "—")
        level_labels = {"low": "Low", "moderate": "Moderate", "high": "High", "critical": "Critical"}
        icons = {"low": "✅", "moderate": "⚠️", "high": "🚫", "critical": "💀"}

        narrative = (
            f"{icons.get(final_risk,'')} **{level_labels.get(final_risk,'')} translational risk** "
            f"(composite score: {composite:.2f}). "
            f"The {comp_name} ortholog of human **{ref_sym}** is **{comp_sym}**. "
        )

        if final_risk == "low":
            narrative += (
                f"Conservation is strong and the regulatory context is largely equivalent. "
                f"Findings from {comp_name} models are likely to predict human biology for this component."
            )
        elif final_risk == "moderate":
            narrative += (
                f"Core function is conserved but notable divergences exist "
                f"(see dimension rationales). Validate key findings in a complementary system "
                f"before advancing to clinical development."
            )
        elif final_risk == "high":
            narrative += (
                f"Significant gaps in conservation, regulatory context, or phenotypic equivalence "
                f"reduce confidence in direct translation. Orthogonal validation in mouse, "
                f"organoids, or human cell lines is recommended."
            )
        else:
            narrative += (
                f"This component cannot be reliably modelled in {comp_name}. "
                f"Do not extrapolate findings to human biology without validation in a "
                f"higher-fidelity system."
            )

        if flags:
            flag_msgs = {
                "no_homolog":                  "No ortholog identified.",
                "paralog_compensation_risk":   "Paralog compensation may mask phenotype.",
                "tissue_expression_mismatch":  "Tissue expression mismatch with human disease context.",
                "ptm_site_absent":             "Key PTM sites absent.",
                "regulatory_rewiring":         "Regulatory rewiring documented.",
                "developmental_vs_somatic_mismatch": "Developmental vs somatic timing mismatch.",
                "drug_discordance":            "Drug discordance known.",
                "wgd_paralog_risk":            "WGD paralog subfunctionalisation risk.",
            }
            flag_text = "; ".join(flag_msgs.get(f, f) for f in flags)
            narrative += f" **Flags:** {flag_text}"

        return narrative

    # ── Main entry point ───────────────────────────────────

    def assess(self, component: dict, pathway_id: str,
               ref: str = "human", compare: str = "drosophila") -> RiskAssessment:

        d1 = self.score_D1(component, ref, compare)
        d2 = self.score_D2(component, ref, compare)
        d3 = self.score_D3(component, ref, compare)
        d4 = self.score_D4(component, ref, compare)
        d5 = self.score_D5(component, ref, compare)

        composite_raw      = self.compute_composite(d1, d2, d3, d4, d5)
        composite_modified, modifiers = self.apply_modifiers(composite_raw, component, compare)

        risk_level, risk_label, risk_icon, action = self.map_composite_to_risk(composite_modified)
        risk_level, overrides = self.apply_overrides(risk_level, d1, d2, d3, d4, d5)

        # Re-fetch label/icon/action after potential override
        for thr, lv, lbl, ic, act in self.RISK_THRESHOLDS:
            if lv == risk_level:
                risk_label, risk_icon, action = lbl, ic, act
                break

        flags     = self.evaluate_flags(component, compare, d1, d2)
        narrative = self.generate_narrative(component, compare, risk_level,
                                            composite_modified, flags, d1, d2)

        assessment_id = f"{pathway_id}__{component['id']}__{compare}"

        return RiskAssessment(
            assessment_id          = assessment_id,
            pathway_id             = pathway_id,
            component_id           = component["id"],
            ref_species            = ref,
            model_species          = compare,
            assessed_date          = date.today().isoformat(),
            evidence_tier          = _compute_evidence_tier(d1, d2, d3, d4, d5),
            D1=d1, D2=d2, D3=d3, D4=d4, D5=d5,
            composite_raw          = round(composite_raw, 4),
            composite_modified     = round(composite_modified, 4),
            modifiers_applied      = modifiers,
            overrides_applied      = overrides,
            final_risk             = risk_level,
            risk_label             = risk_label,
            risk_icon              = risk_icon,
            action                 = action,
            flags_raised           = flags,
            summary_narrative      = narrative,
        )


# ─────────────────────────────────────────────────────────
# Report generation
# ─────────────────────────────────────────────────────────

class RiskReportWriter:

    ICON = {"low": "✅", "moderate": "⚠️", "high": "🚫", "critical": "💀"}
    BAR  = {"low": "████", "moderate": "███░", "high": "██░░", "critical": "█░░░"}

    def to_dict(self, a: RiskAssessment) -> dict:
        return {
            "assessment_id":      a.assessment_id,
            "pathway_id":         a.pathway_id,
            "component_id":       a.component_id,
            "ref_species":        a.ref_species,
            "model_species":      a.model_species,
            "assessed_date":      a.assessed_date,
            "evidence_tier":      a.evidence_tier,
            "dimension_scores": {
                "D1_sequence_conservation": a.D1.raw,
                "D2_paralog_complexity":    a.D2.raw,
                "D3_regulatory_context":    a.D3.raw,
                "D4_phenotypic_validity":   a.D4.raw,
                "D5_therapeutic_evidence":  a.D5.raw,
            },
            "dimension_scored_by": {
                "D1": a.D1.scored_by,
                "D2": a.D2.scored_by,
                "D3": a.D3.scored_by,
                "D4": a.D4.scored_by,
                "D5": a.D5.scored_by,
            },
            "dimension_rationales": {
                "D1": a.D1.rationale,
                "D2": a.D2.rationale,
                "D3": a.D3.rationale,
                "D4": a.D4.rationale,
                "D5": a.D5.rationale,
            },
            "composite_score_raw":      a.composite_raw,
            "composite_score_modified": a.composite_modified,
            "modifiers_applied":        a.modifiers_applied,
            "overrides_applied":        a.overrides_applied,
            "final_risk":               a.final_risk,
            "risk_label":               a.risk_label,
            "risk_icon":                a.risk_icon,
            "action":                   a.action,
            "flags_raised":             a.flags_raised,
            "summary_narrative":        a.summary_narrative,
        }

    def markdown_detail(self, assessments: list[RiskAssessment],
                         pathway_name: str, compare: str) -> str:
        lines = [
            f"# Translational Risk Assessment",
            f"## {pathway_name}",
            f"### Model organism: {compare.capitalize()} → Human",
            f"> Generated: {datetime.now().isoformat(timespec='seconds')}  ",
            f"> Evidence tier: inferred (from pathways.json annotations)",
            "",
            "---",
            "",
            "## Scoring Summary",
            "",
            f"| Component | D1 Seq | D2 Para | D3 Reg | D4 Pheno | D5 Ther | Composite | Risk |",
            f"|-----------|--------|---------|--------|----------|---------|-----------|------|",
        ]

        for a in assessments:
            comp = a.composite_modified
            bar  = self.BAR.get(a.final_risk, "░░░░")
            icon = a.risk_icon
            lines.append(
                f"| `{a.component_id}` | {a.D1.raw}/5 | {a.D2.raw}/5 | {a.D3.raw}/5 | "
                f"{a.D4.raw}/5 | {a.D5.raw}/5 | `{comp:.2f}` {bar} | {icon} {a.risk_label} |"
            )

        lines += [
            "",
            "> **D1** Sequence conservation (weight 30%) · **D2** Paralog complexity (20%) · "
            "**D3** Regulatory context (20%) · **D4** Phenotypic validity (20%) · "
            "**D5** Therapeutic evidence (10%)",
            "",
            "---",
            "",
            "## Component Detail",
            "",
        ]

        for a in assessments:
            lines += [
                f"### {a.component_id}",
                "",
                f"{a.summary_narrative}",
                "",
                "**Dimension breakdown:**",
                "",
                f"| Dimension | Score | Rationale |",
                f"|-----------|-------|-----------|",
                f"| D1 Sequence conservation | {a.D1.raw}/5 | {a.D1.rationale} |",
                f"| D2 Paralog complexity    | {a.D2.raw}/5 | {a.D2.rationale} |",
                f"| D3 Regulatory context    | {a.D3.raw}/5 | {a.D3.rationale} |",
                f"| D4 Phenotypic validity   | {a.D4.raw}/5 | {a.D4.rationale} |",
                f"| D5 Therapeutic evidence  | {a.D5.raw}/5 | {a.D5.rationale} |",
                "",
            ]

            if a.modifiers_applied:
                lines += ["**Modifiers applied:**", ""]
                for m in a.modifiers_applied:
                    lines.append(f"- `{m['rule_id']}` ({m['value']:+.2f}): {m['reason']}")
                lines.append("")

            if a.overrides_applied:
                lines += ["**Override rules triggered:**", ""]
                for o in a.overrides_applied:
                    lines.append(f"- `{o['rule_id']}` → elevated to **{o['elevated_to']}**: {o['reason']}")
                lines.append("")

            if a.flags_raised:
                lines += ["**Flags:**", ""]
                for f in a.flags_raised:
                    lines.append(f"- `{f}`")
                lines.append("")

            lines += ["**Recommended action:**", "", f"> {a.action}", "", "---", ""]

        return "\n".join(lines)

    def markdown_rubric_summary(self) -> str:
        """Generate a human-readable rubric reference card in markdown."""
        lines = [
            "# Translational Risk Rubric — Reference Card",
            "",
            "> *Who Gives a Fly · v1.0.0*",
            "",
            "---",
            "",
            "## Five Scoring Dimensions",
            "",
            "| # | Dimension | Weight | What it measures |",
            "|---|-----------|--------|-----------------|",
            "| D1 | Sequence conservation | 30% | Protein identity and domain coverage |",
            "| D2 | Paralog complexity    | 20% | Gene family size mismatch and compensation risk |",
            "| D3 | Regulatory context    | 20% | Upstream inputs, PTMs, tissue expression |",
            "| D4 | Phenotypic validity   | 20% | Experimental disease model concordance |",
            "| D5 | Therapeutic evidence  | 10% | Drug response concordance |",
            "",
            "---",
            "",
            "## Scoring Scale (per dimension: 0–5)",
            "",
            "| Score | D1 Sequence | D2 Paralogs | D3 Regulatory | D4 Phenotype | D5 Therapeutic |",
            "|-------|-------------|-------------|---------------|--------------|----------------|",
            "| 5 | ≥90% identity | Equivalent count | Fully conserved | Fully validated | Clinical concordance |",
            "| 4 | 70–89% | ±1 paralog | Largely conserved | Substantially validated | Strong preclinical |",
            "| 3 | 45–69% | 2–3 difference | Partially conserved | Partially validated | Preclinical evidence |",
            "| 2 | 20–44% | Major mismatch | Substantially diverged | Limited validation | Limited evidence |",
            "| 1 | <20% | Single vs family | Largely diverged | Predicted only | No drug data |",
            "| 0 | Absent | No homolog | Completely diverged | Contradicted | Discordant |",
            "",
            "---",
            "",
            "## Risk Level Thresholds",
            "",
            "```",
            "Composite score = D1×0.30 + D2×0.20 + D3×0.20 + D4×0.20 + D5×0.10",
            "                  (each dimension normalised to 0–1 before weighting)",
            "",
            "Score ≥ 0.75  →  ✅ Low Risk      — findings likely to translate",
            "Score ≥ 0.50  →  ⚠️  Moderate Risk — translate with caution",
            "Score ≥ 0.25  →  🚫 High Risk     — do not extrapolate without validation",
            "Score < 0.25  →  💀 Critical Gap  — use alternative model",
            "```",
            "",
            "---",
            "",
            "## Override Rules (applied after composite score)",
            "",
            "| Rule | Condition | Override |",
            "|------|-----------|---------|",
            "| OR-01 | D1 = 0 (no homolog) | → Critical |",
            "| OR-02 | D4 = 0 (contradicted phenotype) | → High |",
            "| OR-03 | D5 = 0 (discordant drug response) | → High |",
            "| OR-04 | D2 = 0 AND D1 ≤ 2 | → Critical |",
            "| OR-05 | D3 ≤ 1 AND D4 ≤ 1 | → High |",
            "",
            "---",
            "",
            "## Modifier Rules (adjust composite before threshold mapping)",
            "",
            "| Rule | Condition | Adjustment |",
            "|------|-----------|-----------|",
            "| MR-01 | Human gene rescue demonstrated | +0.10 |",
            "| MR-02 | Drug concordance in ≥2 studies | +0.08 |",
            "| MR-03 | Tissue expression mismatch | −0.10 |",
            "| MR-04 | Zebrafish WGD subfunctionalisation | −0.08 |",
            "| MR-05 | Convergent evolution (different mechanism) | −0.12 |",
            "",
            "---",
            "",
            "## Warning Flags",
            "",
            "Flags are raised independently of composite score and annotate the output record.",
            "",
            "| Flag | Trigger | Severity |",
            "|------|---------|---------|",
            "| `no_homolog` | D1 = 0 | Critical |",
            "| `paralog_compensation_risk` | D2 ≤ 2 + compensation evidence | High |",
            "| `tissue_expression_mismatch` | Expression overlap <40% | High |",
            "| `ptm_site_absent` | Key modification site missing | Moderate |",
            "| `regulatory_rewiring` | Documented pathway rewiring | Moderate |",
            "| `developmental_vs_somatic_mismatch` | Phenotype timing mismatch | Moderate |",
            "| `drug_discordance` | D5 = 0 | Critical |",
            "| `wgd_paralog_risk` | Zebrafish: more paralogs than human | Moderate |",
            "",
        ]
        return "\n".join(lines)


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Who Gives a Fly — Translational Risk Scoring Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python risk_scorer.py --pathway rb_pathway --species drosophila
  python risk_scorer.py --pathway all --species drosophila mouse zebrafish worm
  python risk_scorer.py --rubric-card
  python risk_scorer.py --validate-rubric
        """
    )
    parser.add_argument("--pathway",  default="rb_pathway", help="Pathway ID or 'all'")
    parser.add_argument("--species",  nargs="+", default=["drosophila","mouse","zebrafish","worm"])
    parser.add_argument("--ref",      default="human")
    parser.add_argument("--output",   default="output")
    parser.add_argument("--config",   default="config")
    parser.add_argument("--formats",  nargs="+", default=["markdown","json"],
                        choices=["markdown","json"])
    parser.add_argument("--rubric-card",     action="store_true", help="Print rubric reference card and exit")
    parser.add_argument("--validate-rubric", action="store_true", help="Validate rubric JSON and exit")
    parser.add_argument("--list-pathways",   action="store_true")
    args = parser.parse_args()

    # Load configs
    pathways_db = load_json(os.path.join(args.config, "pathways.json"))
    rubric      = load_json(os.path.join(args.config, "translational_risk_rubric_data.json"))
    writer      = RiskReportWriter()
    scorer      = TranslationalRiskScorer(rubric, pathways_db)

    if args.validate_rubric:
        print("✓ translational_risk_rubric.json loaded and parsed successfully.")
        dims = rubric.get("dimensions", {})
        print(f"  Dimensions defined: {list(dims.keys())}")
        total_weight = sum(d.get("weight", 0) for d in dims.values())
        print(f"  Total weight: {total_weight:.2f} {'✓' if abs(total_weight - 1.0) < 0.01 else '⚠ should sum to 1.0'}")
        print(f"  Override rules: {len(rubric['aggregation']['override_rules'])}")
        print(f"  Modifier rules: {len(rubric['aggregation']['modifier_rules'])}")
        print(f"  Flags defined:  {len(rubric['flags'])}")
        return

    if args.rubric_card:
        print(writer.markdown_rubric_summary())
        return

    if args.list_pathways:
        for p in pathways_db["pathways"]:
            print(f"  {p['id']:<25} {p['name']}  ({len(p.get('components',[]))} components)")
        return

    os.makedirs(args.output, exist_ok=True)

    # Select pathways
    selected = pathways_db["pathways"] if args.pathway == "all" else \
               [p for p in pathways_db["pathways"] if p["id"] == args.pathway]

    if not selected:
        print(f"ERROR: Pathway '{args.pathway}' not found.")
        sys.exit(1)

    for pathway in selected:
        pid = pathway["id"]
        print(f"\n── {pathway['name']} ──")

        for sp in args.species:
            if sp == args.ref or sp not in pathways_db["metadata"]["species"]:
                continue
            print(f"  Scoring {sp.capitalize()} vs {args.ref.capitalize()}...")

            assessments = [
                scorer.assess(comp, pid, ref=args.ref, compare=sp)
                for comp in pathway.get("components", [])
            ]

            if "markdown" in args.formats:
                path = os.path.join(args.output, f"{pid}__risk__{sp}.md")
                with open(path, "w") as f:
                    f.write(writer.markdown_detail(assessments, pathway["name"], sp))
                print(f"    ✓ Markdown → {path}")

            if "json" in args.formats:
                path = os.path.join(args.output, f"{pid}__risk__{sp}.json")
                with open(path, "w") as f:
                    json.dump([writer.to_dict(a) for a in assessments], f, indent=2)
                print(f"    ✓ JSON     → {path}")

    # Rubric reference card
    card_path = os.path.join(args.output, "translational_risk_rubric_card.md")
    with open(card_path, "w") as f:
        f.write(writer.markdown_rubric_summary())
    print(f"\n  ✓ Rubric reference card → {card_path}")
    print(f"\n✓ Done. Outputs in: {args.output}/")


def load_json(path):
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    main()
