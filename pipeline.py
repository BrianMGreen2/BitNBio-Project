#!/usr/bin/env python3
"""
Who Gives a Fly — Cross-Species Pathway Comparison Pipeline
============================================================
Loads pathway and species data from JSON config, computes conservation
scores, identifies translational divergences, and generates educational
markdown/HTML reports.

Usage:
    python pipeline.py --pathway rb_pathway --output output/
    python pipeline.py --pathway all --level graduate --species drosophila mouse
    python pipeline.py --list-pathways
    python pipeline.py --compare-species drosophila human --pathway rb_pathway
"""

import json
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


# ─────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_config(config_dir: str = "config") -> tuple[dict, dict]:
    pathways = load_json(os.path.join(config_dir, "pathways.json"))
    settings = load_json(os.path.join(config_dir, "settings.json"))
    return pathways, settings


# ─────────────────────────────────────────────
# Core analysis
# ─────────────────────────────────────────────

class PathwayAnalyser:
    """
    Analyses cross-species conservation for a single pathway.
    Produces structured comparison data used downstream by report generators.
    """

    def __init__(self, pathway: dict, settings: dict, species_meta: dict):
        self.pathway = pathway
        self.settings = settings
        self.species_meta = species_meta
        self.thresholds = settings["conservation_thresholds"]
        self.risk_levels = settings["translational_risk_levels"]

    def get_conservation_level(self, score: float) -> str:
        """Return conservation level label for a numeric score."""
        for level, cfg in self.thresholds.items():
            if score >= cfg["min"]:
                return level
        return "absent"

    def conservation_bar(self, score: float) -> str:
        """Return a 4-char ASCII conservation bar."""
        if score == 0:
            return "░░░░"
        filled = round(score * 4)
        return "█" * filled + "░" * (4 - filled)

    def risk_flag(self, risk: str) -> str:
        return self.risk_levels.get(risk, {}).get("icon", "?")

    def analyse_component(self, component: dict, ref: str, compare: str) -> dict:
        """
        Build a structured analysis dict for one pathway component
        comparing ref vs compare species.
        """
        key = f"{ref}_{compare}"
        alt_key = f"{compare}_{ref}"

        conservation = component.get("conservation", {})
        cons_data = conservation.get(key) or conservation.get(alt_key) or {}

        score = cons_data.get("score", 0.0)
        level = cons_data.get("level") or self.get_conservation_level(score)
        notes = cons_data.get("notes", "No data available.")

        ref_ortholog   = component.get("orthologs", {}).get(ref, {})
        comp_ortholog  = component.get("orthologs", {}).get(compare, {})

        return {
            "component_id":    component["id"],
            "component_role":  component["role"],
            "function":        component["function"],
            "is_core":         component.get("is_core", False),
            "ref_symbol":      ref_ortholog.get("symbol", "—"),
            "ref_disease":     ref_ortholog.get("disease", ""),
            "comp_symbol":     comp_ortholog.get("symbol", "—"),
            "comp_note":       comp_ortholog.get("note", ""),
            "conservation_score": score,
            "conservation_level": level,
            "conservation_bar":   self.conservation_bar(score),
            "conservation_notes": notes,
            "translational_risk": component.get("translational_risk", "moderate"),
            "translational_notes": component.get("translational_notes", ""),
        }

    def run(self, ref: str = "human", compare: str = "drosophila") -> dict:
        """
        Run full analysis for the pathway comparing ref vs compare species.
        Returns structured results dict.
        """
        components_analysis = []
        for comp in self.pathway.get("components", []):
            result = self.analyse_component(comp, ref, compare)
            components_analysis.append(result)

        # Aggregate scores
        scores = [c["conservation_score"] for c in components_analysis if c["conservation_score"] > 0]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        high_risk = [c for c in components_analysis if c["translational_risk"] == "high"]
        absent    = [c for c in components_analysis if c["conservation_level"] == "absent"]

        return {
            "pathway_id":     self.pathway["id"],
            "pathway_name":   self.pathway["name"],
            "description":    self.pathway["description"],
            "disease":        self.pathway.get("disease_relevance", ""),
            "ref_species":    ref,
            "comp_species":   compare,
            "ref_meta":       self.species_meta.get(ref, {}),
            "comp_meta":      self.species_meta.get(compare, {}),
            "components":     components_analysis,
            "avg_conservation": round(avg_score, 3),
            "avg_cons_level": self.get_conservation_level(avg_score),
            "avg_cons_bar":   self.conservation_bar(avg_score),
            "high_risk_components": [c["component_id"] for c in high_risk],
            "absent_components":    [c["component_id"] for c in absent],
            "n_components":         len(components_analysis),
            "n_high_risk":          len(high_risk),
            "generated_at":         datetime.now().isoformat(timespec="seconds"),
        }


# ─────────────────────────────────────────────
# Markdown generators
# ─────────────────────────────────────────────

class MarkdownReportGenerator:
    """Generates educational Markdown reports from analysis results."""

    def __init__(self, settings: dict, education_level: str = "graduate"):
        self.settings = settings
        self.edu = settings["education_levels"].get(education_level, settings["education_levels"]["graduate"])
        self.edu_level = education_level
        self.thresholds = settings["conservation_thresholds"]
        self.risk_levels = settings["translational_risk_levels"]

    def _species_label(self, meta: dict) -> str:
        return f"*{meta.get('latin_name', 'Unknown')}* ({meta.get('common_name', '')})"

    def _risk_row(self, risk: str) -> str:
        cfg = self.risk_levels.get(risk, {})
        return f"{cfg.get('icon','?')} **{cfg.get('label','?')}** — {cfg.get('description','')}"

    def generate_comparison_report(self, result: dict) -> str:
        """Generate a full comparison report for one pathway × species pair."""
        ref_meta  = result["ref_meta"]
        comp_meta = result["comp_meta"]
        lines = []

        # ── Header ──
        lines += [
            f"# {result['pathway_name']}",
            f"### Cross-Species Comparison: {comp_meta.get('common_name','?')} → {ref_meta.get('common_name','?')}",
            "",
            f"> **Reference species:** {self._species_label(ref_meta)}  ",
            f"> **Comparison species:** {self._species_label(comp_meta)}  ",
            f"> **Generated:** {result['generated_at']}  ",
            f"> **Education level:** {self.edu.get('label','')}",
            "",
            "---",
            "",
        ]

        # ── Pathway overview ──
        lines += [
            "## Pathway Overview",
            "",
            result["description"],
            "",
            f"**Disease relevance:** {result['disease']}",
            "",
        ]

        # ── Overall conservation summary ──
        avg_cfg = self.thresholds.get(result["avg_cons_level"], {})
        lines += [
            "## Overall Conservation Summary",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Overall conservation score | `{result['avg_conservation']:.2f}` {result['avg_cons_bar']} |",
            f"| Conservation level | **{avg_cfg.get('label','?')}** |",
            f"| Components analysed | {result['n_components']} |",
            f"| High-risk translational gaps | {result['n_high_risk']} |",
            f"| Absent homologs | {len(result['absent_components'])} |",
            "",
            f"*{avg_cfg.get('description','')}*",
            "",
        ]

        if result["high_risk_components"]:
            lines += [
                "### ⚠️ High-Risk Translational Gaps",
                "",
                "The following components have **high translational risk** — findings from the comparison species may **not translate** to humans:",
                "",
            ]
            for cid in result["high_risk_components"]:
                comp_data = next((c for c in result["components"] if c["component_id"] == cid), None)
                if comp_data:
                    lines.append(f"- **{comp_data['ref_symbol']}** ({cid}): {comp_data['translational_notes']}")
            lines.append("")

        # ── Component-by-component ──
        lines += [
            "---",
            "",
            "## Component Analysis",
            "",
        ]

        for comp in result["components"]:
            level_cfg = self.thresholds.get(comp["conservation_level"], {})
            risk_cfg  = self.risk_levels.get(comp["translational_risk"], {})

            lines += [
                f"### {comp['ref_symbol']}",
                f"**Role:** {comp['component_role']}  ",
                f"**Function:** {comp['function']}",
                "",
                f"| Species | Symbol | Notes |",
                f"|---------|--------|-------|",
                f"| {ref_meta.get('common_name','Ref')} | `{comp['ref_symbol']}` | {comp.get('ref_disease','')} |",
                f"| {comp_meta.get('common_name','Compare')} | `{comp['comp_symbol']}` | {comp['comp_note']} |",
                "",
                f"**Conservation:** `{comp['conservation_score']:.2f}` {comp['conservation_bar']} — "
                f"**{level_cfg.get('label','?')}**  ",
                f"*{comp['conservation_notes']}*",
                "",
                f"**Translational risk:** {risk_cfg.get('icon','?')} {risk_cfg.get('label','?')}  ",
                f"*{comp['translational_notes']}*",
                "",
            ]

            if self.edu.get("include_mechanisms") and comp["is_core"]:
                lines += [
                    "<details>",
                    "<summary>Mechanistic detail</summary>",
                    "",
                    f"> **Function in pathway:** {comp['function']}",
                    "",
                    "</details>",
                    "",
                ]

        # ── ASCII pathway conservation heatmap ──
        lines += [
            "---",
            "",
            "## Conservation Heatmap",
            "",
            "```",
            f"{'Component':<20} {'Score':>6}  {'Bar':<6}  {'Risk':<4}  Level",
            "─" * 60,
        ]
        for comp in result["components"]:
            level_cfg = self.thresholds.get(comp["conservation_level"], {})
            risk_icon = self.risk_levels.get(comp["translational_risk"], {}).get("icon", "?")
            lines.append(
                f"{comp['component_id']:<20} {comp['conservation_score']:>6.2f}  "
                f"{comp['conservation_bar']:<6}  {risk_icon:<4}  {level_cfg.get('label','?')}"
            )
        lines += [
            "─" * 60,
            f"{'AVERAGE':<20} {result['avg_conservation']:>6.2f}  {result['avg_cons_bar']:<6}",
            "```",
            "",
            "> Bar key: `████` Very High · `███░` High · `██░░` Moderate · `█░░░` Low · `░░░░` Absent",
            "",
        ]

        # ── Translational recommendations ──
        lines += [
            "---",
            "",
            "## Translational Recommendations",
            "",
            f"Based on this analysis of the **{result['pathway_name']}** in "
            f"{comp_meta.get('common_name','?')} as a model for human disease:",
            "",
        ]

        low_risk  = [c for c in result["components"] if c["translational_risk"] == "low"]
        mod_risk  = [c for c in result["components"] if c["translational_risk"] == "moderate"]
        high_risk = [c for c in result["components"] if c["translational_risk"] == "high"]

        if low_risk:
            lines.append("**✅ Directly translatable components:**")
            for c in low_risk:
                lines.append(f"- `{c['ref_symbol']}` — {c['translational_notes']}")
            lines.append("")

        if mod_risk:
            lines.append("**⚠️ Translate with caution:**")
            for c in mod_risk:
                lines.append(f"- `{c['ref_symbol']}` — {c['translational_notes']}")
            lines.append("")

        if high_risk:
            lines.append("**🚫 Do not extrapolate without validation:**")
            for c in high_risk:
                lines.append(f"- `{c['ref_symbol']}` — {c['translational_notes']}")
            lines.append("")

        lines += ["---", ""]

        # ── Glossary (graduate/clinical levels) ──
        if self.edu.get("glossary_depth") in ("full", "clinical"):
            lines += self._glossary()

        return "\n".join(lines)

    def generate_multi_species_summary(self, results: list[dict], pathway_name: str) -> str:
        """Generate a summary table comparing one pathway across multiple species."""
        lines = [
            f"# {pathway_name}",
            "## Multi-Species Conservation Summary",
            "",
            f"> Generated: {datetime.now().isoformat(timespec='seconds')}",
            "",
            "---",
            "",
            "## Conservation Score Matrix",
            "",
        ]

        # Header row
        species_list = list({r["comp_species"] for r in results})
        header = f"| Component | Role | " + " | ".join(s.capitalize() for s in species_list) + " |"
        sep    = "|-----------|------|" + "|".join(["------"] * len(species_list)) + "|"
        lines += [header, sep]

        # Get all component ids from first result
        if results:
            for comp in results[0]["components"]:
                cid  = comp["component_id"]
                role = comp["component_role"]
                cells = []
                for sp in species_list:
                    result = next((r for r in results if r["comp_species"] == sp), None)
                    if result:
                        c = next((x for x in result["components"] if x["component_id"] == cid), None)
                        if c:
                            cells.append(f"`{c['conservation_score']:.2f}` {c['conservation_bar']}")
                        else:
                            cells.append("—")
                    else:
                        cells.append("—")
                lines.append(f"| `{cid}` | {role} | " + " | ".join(cells) + " |")

        lines += [
            "",
            "> `████` ≥0.90 Very High · `███░` ≥0.70 High · `██░░` ≥0.45 Moderate · `█░░░` ≥0.20 Low · `░░░░` Absent",
            "",
            "---",
            "",
            "## Translational Risk Summary",
            "",
            "| Component | " + " | ".join(s.capitalize() for s in species_list) + " |",
            "|-----------|" + "|".join(["------"] * len(species_list)) + "|",
        ]

        if results:
            risk_icons = {"low": "✅", "moderate": "⚠️", "high": "🚫"}
            for comp in results[0]["components"]:
                cid = comp["component_id"]
                cells = []
                for sp in species_list:
                    result = next((r for r in results if r["comp_species"] == sp), None)
                    if result:
                        c = next((x for x in result["components"] if x["component_id"] == cid), None)
                        if c:
                            cells.append(risk_icons.get(c["translational_risk"], "?"))
                        else:
                            cells.append("—")
                    else:
                        cells.append("—")
                lines.append(f"| `{cid}` | " + " | ".join(cells) + " |")

        lines += [
            "",
            "> ✅ Low risk · ⚠️ Moderate risk · 🚫 High risk (avoid extrapolation)",
            "",
            "---",
            "",
            "## Species Suitability Guide",
            "",
            "Which model organism should you use for each research question?",
            "",
        ]

        if results:
            for comp in results[0]["components"]:
                cid = comp["component_id"]
                best = []
                for sp in species_list:
                    result = next((r for r in results if r["comp_species"] == sp), None)
                    if result:
                        c = next((x for x in result["components"] if x["component_id"] == cid), None)
                        if c and c["translational_risk"] == "low":
                            best.append(sp.capitalize())
                if best:
                    lines.append(f"- **{cid}**: Best modelled in {', '.join(best)}")
                else:
                    lines.append(f"- **{cid}**: Use caution in all listed models — verify in human cells/tissue")

        lines += ["", "---", ""]
        return "\n".join(lines)

    def generate_educational_primer(self, pathway: dict, species_meta: dict) -> str:
        """Generate a standalone educational primer about a pathway."""
        lines = [
            f"# Educational Primer: {pathway['name']}",
            "",
            f"> **Level:** {self.edu.get('label','')}  ",
            f"> **Generated:** {datetime.now().isoformat(timespec='seconds')}",
            "",
            "---",
            "",
            "## What is this pathway?",
            "",
            pathway["description"],
            "",
            f"**Clinical relevance:** {pathway.get('disease_relevance', '')}",
            "",
            "---",
            "",
            "## Key Components",
            "",
        ]

        for comp in pathway.get("components", []):
            lines += [
                f"### {comp['id'].replace('_',' ').title()}",
                f"**Role:** {comp['role']}  ",
                f"**Function:** {comp['function']}",
                "",
            ]

            if self.edu.get("include_mechanisms"):
                lines += [
                    "**Orthologs across species:**",
                    "",
                    "| Species | Gene Symbol | Notes |",
                    "|---------|------------|-------|",
                ]
                for sp, data in comp.get("orthologs", {}).items():
                    sp_meta = species_meta.get(sp, {})
                    latin = sp_meta.get("latin_name", sp)
                    lines.append(
                        f"| *{latin}* | `{data.get('symbol','—')}` | {data.get('note', data.get('disease',''))} |"
                    )
                lines.append("")

            lines += [
                f"**Translational risk:** {self.risk_levels.get(comp.get('translational_risk','moderate'),{}).get('icon','?')} "
                f"{comp.get('translational_risk','').replace('_',' ').title()}",
                "",
                f"*{comp.get('translational_notes','')}*",
                "",
            ]

        if self.edu.get("include_clinical"):
            lines += [
                "---",
                "",
                "## Clinical Implications",
                "",
                "Understanding cross-species conservation of this pathway informs:",
                "",
                "- Which model organism results are most likely to translate to patients",
                "- Where preclinical drug screens may fail to predict clinical outcomes",
                "- Which pathway nodes are safe drug targets across species",
                "",
            ]

        lines += self._glossary()
        return "\n".join(lines)

    def _glossary(self) -> list[str]:
        return [
            "---",
            "",
            "## Glossary",
            "",
            "| Term | Definition |",
            "|------|-----------|",
            "| **Ortholog** | A gene in two different species descended from a common ancestral gene |",
            "| **Paralog** | A gene related by duplication within the same species |",
            "| **Conservation score** | Sequence identity (0–1) between orthologous proteins |",
            "| **Pocket domain** | The functional region of Rb that binds E2F transcription factors |",
            "| **CDK inhibitor (CKI)** | Protein that blocks cyclin-dependent kinase activity |",
            "| **Restriction point** | Point in G1 after which cell cycle entry is irreversible |",
            "| **Translational gap** | Difference between model organism and human biology that limits predictive validity |",
            "| **Valley of death** | The gap between promising preclinical results and successful clinical outcomes |",
            "| **Synthetic lethality** | When loss of two genes is lethal but loss of either alone is viable |",
            "| **Endoreplication** | DNA replication without cell division; common in fly polytene tissues |",
            "",
        ]


# ─────────────────────────────────────────────
# HTML generator
# ─────────────────────────────────────────────

class HTMLReportGenerator:
    """Wraps a markdown report in a styled HTML page for web viewing."""

    STYLE = """
    <style>
      body { font-family: Georgia, serif; max-width: 900px; margin: 40px auto;
             padding: 0 24px; color: #2c2c2c; line-height: 1.7; }
      h1 { color: #1a3a2a; border-bottom: 3px solid #52b788; padding-bottom: 8px; }
      h2 { color: #2d6a4f; margin-top: 2em; }
      h3 { color: #1b4332; }
      table { border-collapse: collapse; width: 100%; margin: 1em 0; font-size: 0.9em; }
      th { background: #d8f3dc; color: #1b4332; padding: 8px 12px; text-align: left; }
      td { padding: 7px 12px; border-bottom: 1px solid #e0e0e0; }
      tr:hover td { background: #f0fdf4; }
      code { background: #f1f5f0; padding: 2px 6px; border-radius: 3px; font-size: 0.88em; }
      pre  { background: #f1f5f0; padding: 16px; border-radius: 6px; overflow-x: auto;
             font-size: 0.82em; border-left: 4px solid #52b788; }
      blockquote { border-left: 4px solid #b7e4c7; padding-left: 16px; color: #555;
                   margin: 1em 0; font-style: italic; }
      details { background: #f9fafb; border: 1px solid #e0e0e0; border-radius: 6px;
                padding: 8px 16px; margin: 8px 0; }
      summary { cursor: pointer; font-weight: bold; color: #2d6a4f; }
      .risk-low    { color: #2d6a4f; }
      .risk-mod    { color: #e76f51; }
      .risk-high   { color: #d62828; font-weight: bold; }
      hr { border: none; border-top: 1px solid #d8e8d8; margin: 2em 0; }
    </style>
    """

    def wrap(self, markdown_text: str, title: str) -> str:
        # Very lightweight markdown → HTML (just enough for our output)
        import re
        html = markdown_text
        html = re.sub(r"^# (.+)$",   r"<h1>\1</h1>",   html, flags=re.MULTILINE)
        html = re.sub(r"^## (.+)$",  r"<h2>\1</h2>",   html, flags=re.MULTILINE)
        html = re.sub(r"^### (.+)$", r"<h3>\1</h3>",   html, flags=re.MULTILINE)
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(r"\*(.+?)\*",     r"<em>\1</em>",          html)
        html = re.sub(r"`(.+?)`",       r"<code>\1</code>",       html)
        html = re.sub(r"^> (.+)$",  r"<blockquote>\1</blockquote>", html, flags=re.MULTILINE)
        html = re.sub(r"^---$",     r"<hr>",                         html, flags=re.MULTILINE)
        # Tables
        def convert_table(m):
            rows = [r.strip() for r in m.group(0).strip().split("\n") if r.strip() and not re.match(r"^\|[-| ]+\|$", r.strip())]
            out = ["<table>"]
            for i, row in enumerate(rows):
                cells = [c.strip() for c in row.strip("|").split("|")]
                tag = "th" if i == 0 else "td"
                out.append("<tr>" + "".join(f"<{tag}>{c}</{tag}>" for c in cells) + "</tr>")
            out.append("</table>")
            return "\n".join(out)
        html = re.sub(r"(\|.+\|\n)+", convert_table, html)
        # Code blocks
        html = re.sub(r"```[\w]*\n([\s\S]+?)```", r"<pre>\1</pre>", html)
        # Paragraphs
        lines = html.split("\n")
        result = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("<"):
                result.append(f"<p>{stripped}</p>")
            else:
                result.append(line)
        html = "\n".join(result)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — Who Gives a Fly</title>
{self.STYLE}
</head>
<body>
<p style="font-size:0.75em;color:#888;border-bottom:1px solid #eee;padding-bottom:8px;">
  🪰 <strong>Who Gives a Fly</strong> · Cross-Species Translational Pathway Analysis
</p>
{html}
<footer style="margin-top:3em;padding-top:1em;border-top:1px solid #e0e0e0;
               font-size:0.75em;color:#888;">
  Generated by Who Gives a Fly pipeline · {datetime.now().strftime("%Y-%m-%d")}
</footer>
</body>
</html>"""


# ─────────────────────────────────────────────
# JSON report writer
# ─────────────────────────────────────────────

def save_json_report(result: dict, path: str):
    with open(path, "w") as f:
        json.dump(result, f, indent=2)


# ─────────────────────────────────────────────
# CLI orchestration
# ─────────────────────────────────────────────

def build_output_path(output_dir: str, pathway_id: str, comp_species: str, fmt: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    return os.path.join(output_dir, f"{pathway_id}__{comp_species}.{fmt}")


def run_pipeline(
    config_dir:      str   = "config",
    pathway_id:      str   = "rb_pathway",
    comp_species:    list  = None,
    ref_species:     str   = "human",
    output_dir:      str   = "output",
    education_level: str   = "graduate",
    formats:         list  = None,
    generate_primer: bool  = False,
    generate_multi:  bool  = False,
):
    pathways_db, settings = load_config(config_dir)
    species_meta = pathways_db["metadata"]["species"]

    if comp_species is None:
        comp_species = settings["settings"]["default_comparison_species"]
    if formats is None:
        formats = ["markdown", "html", "json_report"]

    # Select pathway(s)
    if pathway_id == "all":
        selected = pathways_db["pathways"]
    else:
        selected = [p for p in pathways_db["pathways"] if p["id"] == pathway_id]
        if not selected:
            print(f"ERROR: Pathway '{pathway_id}' not found. Use --list-pathways to see options.")
            sys.exit(1)

    md_gen   = MarkdownReportGenerator(settings, education_level)
    html_gen = HTMLReportGenerator()

    for pathway in selected:
        pid = pathway["id"]
        print(f"\n── Pathway: {pathway['name']} ──")
        analyser = PathwayAnalyser(pathway, settings, species_meta)

        all_results = []

        for sp in comp_species:
            if sp not in species_meta:
                print(f"  SKIP: Species '{sp}' not in metadata.")
                continue
            if sp == ref_species:
                continue

            print(f"  Analysing {sp.capitalize()} vs {ref_species.capitalize()}...")
            result = analyser.run(ref=ref_species, compare=sp)
            all_results.append(result)

            # Per-species comparison report
            if "markdown" in formats:
                path = build_output_path(output_dir, pid, sp, "md")
                md_text = md_gen.generate_comparison_report(result)
                with open(path, "w") as f:
                    f.write(md_text)
                print(f"    ✓ Markdown → {path}")

            if "html" in formats:
                path = build_output_path(output_dir, pid, sp, "html")
                md_text = md_gen.generate_comparison_report(result)
                html_text = html_gen.wrap(md_text, f"{pathway['name']} — {sp.capitalize()}")
                with open(path, "w") as f:
                    f.write(html_text)
                print(f"    ✓ HTML     → {path}")

            if "json_report" in formats:
                path = build_output_path(output_dir, pid, sp, "json")
                save_json_report(result, path)
                print(f"    ✓ JSON     → {path}")

        # Multi-species summary
        if generate_multi and len(all_results) > 1:
            print(f"  Generating multi-species summary...")
            md_text = md_gen.generate_multi_species_summary(all_results, pathway["name"])

            if "markdown" in formats:
                path = os.path.join(output_dir, f"{pid}__multi_species_summary.md")
                with open(path, "w") as f:
                    f.write(md_text)
                print(f"    ✓ Multi-species Markdown → {path}")

            if "html" in formats:
                path = os.path.join(output_dir, f"{pid}__multi_species_summary.html")
                html_text = html_gen.wrap(md_text, f"{pathway['name']} — Multi-Species Summary")
                with open(path, "w") as f:
                    f.write(html_text)
                print(f"    ✓ Multi-species HTML     → {path}")

        # Educational primer
        if generate_primer:
            print(f"  Generating educational primer...")
            md_text = md_gen.generate_educational_primer(pathway, species_meta)

            if "markdown" in formats:
                path = os.path.join(output_dir, f"{pid}__primer.md")
                with open(path, "w") as f:
                    f.write(md_text)
                print(f"    ✓ Primer Markdown → {path}")

            if "html" in formats:
                path = os.path.join(output_dir, f"{pid}__primer.html")
                html_text = html_gen.wrap(md_text, f"{pathway['name']} — Educational Primer")
                with open(path, "w") as f:
                    f.write(html_text)
                print(f"    ✓ Primer HTML     → {path}")

    print(f"\n✓ Done. All outputs written to: {output_dir}/")


# ─────────────────────────────────────────────
# CLI entry point
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Who Gives a Fly — Cross-Species Pathway Comparison Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py --pathway rb_pathway --multi --primer
  python pipeline.py --pathway all --species drosophila mouse zebrafish --level clinical
  python pipeline.py --list-pathways
  python pipeline.py --pathway wnt_pathway --species mouse --formats markdown html
        """
    )
    parser.add_argument("--pathway",    default="rb_pathway", help="Pathway ID to analyse, or 'all'")
    parser.add_argument("--species",    nargs="+",            help="Comparison species (default: all configured)")
    parser.add_argument("--ref",        default="human",      help="Reference species (default: human)")
    parser.add_argument("--output",     default="output",     help="Output directory")
    parser.add_argument("--config",     default="config",     help="Config directory")
    parser.add_argument("--level",      default="graduate",   choices=["undergraduate","graduate","clinical"],
                        help="Education level for reports")
    parser.add_argument("--formats",    nargs="+",            default=["markdown","html","json_report"],
                        choices=["markdown","html","json_report"],
                        help="Output formats to generate")
    parser.add_argument("--multi",      action="store_true",  help="Generate multi-species summary table")
    parser.add_argument("--primer",     action="store_true",  help="Generate educational primer")
    parser.add_argument("--list-pathways", action="store_true", help="List available pathways and exit")

    args = parser.parse_args()

    if args.list_pathways:
        pathways_db, _ = load_config(args.config)
        print("\nAvailable pathways:")
        for p in pathways_db["pathways"]:
            n_comps = len(p.get("components", []))
            print(f"  {p['id']:<25} {p['name']}  ({n_comps} components)")
        print()
        return

    run_pipeline(
        config_dir      = args.config,
        pathway_id      = args.pathway,
        comp_species    = args.species,
        ref_species     = args.ref,
        output_dir      = args.output,
        education_level = args.level,
        formats         = args.formats,
        generate_primer = args.primer,
        generate_multi  = args.multi,
    )


if __name__ == "__main__":
    main()
