#!/usr/bin/env python3
"""
Who Gives a Fly — Evidence Validator
=====================================
Validates structured evidence blocks (regulatory_context, phenotypic_evidence,
pharmacological_evidence) against evidence_schema.json before they are committed
to pathways.json.

Upgrades evidence_tier from 'ai_candidate' → 'validated' on approval.

Usage:
    python validate_evidence.py --check config/pathways.json
    python validate_evidence.py --entry evidence_draft.json --component rb1
    python validate_evidence.py --report                    # coverage report
    python validate_evidence.py --approve evidence_draft.json --component rb1 --curator "J.Smith"
"""

import json
import argparse
import sys
import os
from datetime import date
from typing import Any


# ─────────────────────────────────────────────────────────
# Minimal JSON Schema validator (stdlib only)
# For production use, replace with: pip install jsonschema
# ─────────────────────────────────────────────────────────

class SchemaValidationError(Exception):
    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(f"[{path}] {message}")


def validate(instance: Any, schema: dict, path: str = "#") -> list[str]:
    """
    Minimal recursive JSON Schema validator (draft-07 subset).
    Returns list of error strings. Empty list = valid.
    """
    errors = []

    schema_type = schema.get("type")
    if schema_type:
        types = schema_type if isinstance(schema_type, list) else [schema_type]
        type_map = {
            "object": dict, "array": list, "string": str,
            "number": (int, float), "integer": int, "boolean": bool, "null": type(None)
        }
        if not any(isinstance(instance, type_map[t]) for t in types if t in type_map):
            errors.append(f"{path}: expected type {types}, got {type(instance).__name__}")
            return errors  # Can't validate further if type is wrong

    if schema_type == "object" or isinstance(instance, dict):
        # Required fields
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required field '{req}'")

        # Property schemas
        for prop, prop_schema in schema.get("properties", {}).items():
            if prop in instance:
                errors.extend(validate(instance[prop], prop_schema, f"{path}.{prop}"))

        # Pattern properties
        for pattern, prop_schema in schema.get("patternProperties", {}).items():
            import re
            for key, val in instance.items():
                if re.match(pattern, key):
                    errors.extend(validate(val, prop_schema, f"{path}.{key}"))

        # Additional properties
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for key in instance:
                # Check against patternProperties too
                import re
                matched_pattern = any(
                    re.match(pat, key)
                    for pat in schema.get("patternProperties", {})
                )
                if key not in allowed and not matched_pattern:
                    errors.append(f"{path}: unexpected property '{key}'")

    if schema_type == "array" or isinstance(instance, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                errors.extend(validate(item, item_schema, f"{path}[{i}]"))
        min_items = schema.get("minItems")
        if min_items is not None and len(instance) < min_items:
            errors.append(f"{path}: array has {len(instance)} items, minimum is {min_items}")

    # Enum
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: '{instance}' not in allowed values {schema['enum']}")

    # String pattern
    if schema_type == "string" and "pattern" in schema and isinstance(instance, str):
        import re
        if not re.match(schema["pattern"], instance):
            errors.append(f"{path}: '{instance}' does not match pattern '{schema['pattern']}'")

    # Numeric bounds
    if "minimum" in schema and isinstance(instance, (int, float)):
        if instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
    if "maximum" in schema and isinstance(instance, (int, float)):
        if instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    # $ref resolution (inline only — resolves definitions in same doc)
    # For external $refs, pass resolved schemas directly

    return errors


def resolve_refs(schema: dict, root: dict) -> dict:
    """Recursively resolve $ref within a schema document."""
    if "$ref" in schema:
        ref = schema["$ref"]
        if ref.startswith("#/definitions/"):
            def_name = ref.split("/")[-1]
            resolved = root.get("definitions", {}).get(def_name, {})
            return resolve_refs(resolved, root)
        return schema  # External refs not resolved here

    result = {}
    for key, val in schema.items():
        if isinstance(val, dict):
            result[key] = resolve_refs(val, root)
        elif isinstance(val, list):
            result[key] = [
                resolve_refs(item, root) if isinstance(item, dict) else item
                for item in val
            ]
        else:
            result[key] = val
    return result


# ─────────────────────────────────────────────────────────
# Evidence coverage analysis
# ─────────────────────────────────────────────────────────

EVIDENCE_KEYS = {
    "D3": "regulatory_context",
    "D4": "phenotypic_evidence",
    "D5": "pharmacological_evidence",
}

DIMENSION_LABELS = {
    "D3": "Regulatory context",
    "D4": "Phenotypic validity",
    "D5": "Therapeutic evidence",
}


def coverage_report(pathways_db: dict) -> dict:
    """
    Scan pathways.json and report which components have structured evidence
    vs which are still relying on inference for each dimension.
    """
    report = {
        "summary": {"total_components": 0, "fully_validated": 0, "partially_validated": 0, "all_inferred": 0},
        "by_pathway": {},
        "gaps": [],
        "coverage_pct": {},
    }

    dim_counts = {d: {"present": 0, "absent": 0} for d in EVIDENCE_KEYS}

    for pathway in pathways_db.get("pathways", []):
        pid  = pathway["id"]
        pname = pathway["name"]
        report["by_pathway"][pid] = {"name": pname, "components": {}}

        for comp in pathway.get("components", []):
            cid = comp["id"]
            report["summary"]["total_components"] += 1

            dims_present = []
            dims_absent  = []
            for dim, key in EVIDENCE_KEYS.items():
                if key in comp and comp[key]:
                    dims_present.append(dim)
                    dim_counts[dim]["present"] += 1
                else:
                    dims_absent.append(dim)
                    dim_counts[dim]["absent"] += 1
                    report["gaps"].append({
                        "pathway":   pid,
                        "component": cid,
                        "dimension": dim,
                        "key":       key,
                        "priority":  _gap_priority(comp, dim),
                    })

            if not dims_absent:
                report["summary"]["fully_validated"] += 1
                status = "fully_validated"
            elif not dims_present:
                report["summary"]["all_inferred"] += 1
                status = "all_inferred"
            else:
                report["summary"]["partially_validated"] += 1
                status = "partially_validated"

            report["by_pathway"][pid]["components"][cid] = {
                "status":       status,
                "dims_present": dims_present,
                "dims_absent":  dims_absent,
                "risk":         comp.get("translational_risk", "unknown"),
            }

    total = report["summary"]["total_components"]
    for dim, counts in dim_counts.items():
        pct = round(counts["present"] / total * 100) if total else 0
        report["coverage_pct"][dim] = pct

    # Sort gaps: high-risk components first, then by dimension weight
    dim_priority = {"D4": 0, "D5": 1, "D3": 2}
    report["gaps"].sort(key=lambda g: (
        {"high": 0, "moderate": 1, "low": 2}.get(
            _get_component_risk(pathways_db, g["pathway"], g["component"]), 3
        ),
        dim_priority.get(g["dimension"], 99)
    ))

    return report


def _gap_priority(comp: dict, dim: str) -> str:
    risk = comp.get("translational_risk", "moderate")
    dim_weight = {"D4": "high", "D5": "medium", "D3": "medium"}
    if risk == "high" and dim == "D4":
        return "critical"
    if risk in ("high", "moderate") and dim in ("D4", "D5"):
        return "high"
    return "normal"


def _get_component_risk(db: dict, pathway_id: str, component_id: str) -> str:
    for p in db.get("pathways", []):
        if p["id"] == pathway_id:
            for c in p.get("components", []):
                if c["id"] == component_id:
                    return c.get("translational_risk", "unknown")
    return "unknown"


def print_coverage_report(report: dict):
    print("\n═══ EVIDENCE COVERAGE REPORT ═══\n")

    s = report["summary"]
    total = s["total_components"]
    print(f"  Total components:     {total}")
    print(f"  Fully validated:      {s['fully_validated']} ({s['fully_validated']/total*100:.0f}%)")
    print(f"  Partially validated:  {s['partially_validated']} ({s['partially_validated']/total*100:.0f}%)")
    print(f"  All inferred:         {s['all_inferred']} ({s['all_inferred']/total*100:.0f}%)")

    print(f"\n  Per-dimension coverage (% components with structured data):")
    dim_labels = {"D3": "D3 Regulatory context ", "D4": "D4 Phenotypic validity ", "D5": "D5 Therapeutic evidence"}
    for dim, pct in report["coverage_pct"].items():
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"    {dim_labels[dim]}  {bar}  {pct:3d}%")

    print(f"\n  Priority gaps (top 10 by risk × dimension weight):")
    for gap in report["gaps"][:10]:
        print(f"    [{gap['priority'].upper():<8}] {gap['pathway']}/{gap['component']} → {gap['dimension']} ({gap['key']})")

    print(f"\n  By pathway:")
    for pid, pdata in report["by_pathway"].items():
        print(f"\n    {pdata['name']}")
        for cid, cdata in pdata["components"].items():
            icons = {"fully_validated": "✅", "partially_validated": "⚠️", "all_inferred": "🔶"}
            icon = icons.get(cdata["status"], "?")
            risk_icon = {"low": "✅", "moderate": "⚠️", "high": "🚫"}.get(cdata["risk"], "?")
            absent_str = ", ".join(cdata["dims_absent"]) if cdata["dims_absent"] else "none"
            print(f"      {icon} {cid:<25} risk:{risk_icon}  inferred dims: {absent_str}")

    print()


# ─────────────────────────────────────────────────────────
# Validation workflows
# ─────────────────────────────────────────────────────────

def validate_pathways_file(pathways_path: str, schema_path: str) -> bool:
    """
    Validate all evidence blocks in pathways.json against evidence_schema.json.
    Returns True if all entries are valid.
    """
    with open(pathways_path) as f:
        db = json.load(f)
    with open(schema_path) as f:
        raw_schema = json.load(f)

    schema = resolve_refs(raw_schema, raw_schema)
    all_valid = True

    print(f"\n═══ VALIDATING EVIDENCE BLOCKS IN {pathways_path} ═══\n")

    for pathway in db.get("pathways", []):
        for comp in pathway.get("components", []):
            cid = comp["id"]
            pid = pathway["id"]

            for key in EVIDENCE_KEYS.values():
                if key not in comp:
                    continue

                # Build a mini-document to validate
                entry = {
                    "component_id": cid,
                    key: comp[key],
                }

                prop_schema = schema.get("properties", {}).get(key)
                if not prop_schema:
                    continue

                errors = validate(comp[key], prop_schema, f"{pid}/{cid}/{key}")

                if errors:
                    all_valid = False
                    print(f"  ✗ {pid}/{cid}/{key}:")
                    for e in errors:
                        print(f"      {e}")
                else:
                    # Count entries and tiers
                    entries = comp[key] if isinstance(comp[key], list) else comp[key].values()
                    tiers = [e.get("evidence_tier", "?") for e in entries]
                    tier_str = ", ".join(sorted(set(tiers)))
                    print(f"  ✓ {pid}/{cid}/{key}  ({len(list(entries))} entries, tiers: {tier_str})")

    if all_valid:
        print(f"\n  All evidence blocks valid.\n")
    else:
        print(f"\n  Validation errors found. Fix before committing to pathways.json.\n")

    return all_valid


def validate_entry_file(entry_path: str, component_id: str, schema_path: str) -> bool:
    """
    Validate a standalone evidence draft file against the schema.
    """
    with open(entry_path) as f:
        entry = json.load(f)
    with open(schema_path) as f:
        raw_schema = json.load(f)

    schema = resolve_refs(raw_schema, raw_schema)

    print(f"\n═══ VALIDATING DRAFT: {entry_path} ═══\n")

    all_valid = True
    for key in EVIDENCE_KEYS.values():
        if key not in entry:
            continue

        prop_schema = schema.get("properties", {}).get(key)
        if not prop_schema:
            print(f"  WARN: No schema found for '{key}'")
            continue

        errors = validate(entry[key], prop_schema, f"{component_id}/{key}")
        if errors:
            all_valid = False
            print(f"  ✗ {key}:")
            for e in errors:
                print(f"      {e}")
        else:
            print(f"  ✓ {key} — valid")

    if all_valid:
        print(f"\n  Entry valid. Ready for --approve.\n")
    else:
        print(f"\n  Fix errors before approving.\n")

    return all_valid


def approve_entry(entry_path: str, pathways_path: str,
                  component_id: str, curator: str, schema_path: str) -> bool:
    """
    After validation, merge an evidence entry into pathways.json,
    upgrading evidence_tier from 'ai_candidate' → 'validated'.
    """
    # Validate first
    if not validate_entry_file(entry_path, component_id, schema_path):
        print("  Approval aborted — fix validation errors first.")
        return False

    with open(entry_path) as f:
        entry = json.load(f)
    with open(pathways_path) as f:
        db = json.load(f)

    today = date.today().isoformat()
    component_found = False

    for pathway in db.get("pathways", []):
        for comp in pathway.get("components", []):
            if comp["id"] != component_id:
                continue
            component_found = True

            for key in EVIDENCE_KEYS.values():
                if key not in entry:
                    continue

                # Upgrade ai_candidate → validated, stamp curator + date
                new_data = entry[key]
                if isinstance(new_data, list):
                    for item in new_data:
                        if item.get("evidence_tier") == "ai_candidate":
                            item["evidence_tier"] = "validated"
                        item.setdefault("curator", curator)
                        item.setdefault("curated_date", today)
                elif isinstance(new_data, dict):
                    for sp_key, item in new_data.items():
                        if isinstance(item, dict):
                            if item.get("evidence_tier") == "ai_candidate":
                                item["evidence_tier"] = "validated"
                            item.setdefault("curator", curator)
                            item.setdefault("curated_date", today)

                # Merge into component (extend arrays, merge dicts)
                if key not in comp:
                    comp[key] = new_data
                elif isinstance(comp[key], list):
                    comp[key].extend(new_data)
                elif isinstance(comp[key], dict):
                    comp[key].update(new_data)

                print(f"  ✓ Merged {key} into {component_id}")

            break
        if component_found:
            break

    if not component_found:
        print(f"  ERROR: Component '{component_id}' not found in {pathways_path}")
        return False

    # Write back
    with open(pathways_path, "w") as f:
        json.dump(db, f, indent=2)

    print(f"\n  ✓ {pathways_path} updated. evidence_tier upgraded to 'validated' where applicable.")
    print(f"  Curator: {curator}  |  Date: {today}\n")
    return True


def generate_entry_template(component_id: str, pathway_id: str,
                             species: list[str], output_path: str):
    """
    Generate a blank evidence entry template for a given component.
    Curators fill this in, then run --entry / --approve.
    """
    template = {
        "_instructions": (
            "Fill in this template and validate with: "
            "python validate_evidence.py --entry <this_file> --component " + component_id
        ),
        "component_id": component_id,
        "pathway_id":   pathway_id,

        "regulatory_context": {
            f"human_{sp}": {
                "upstream_inputs_conserved":    None,
                "downstream_targets_conserved": None,
                "ptm_sites_conserved":          None,
                "tissue_expression_overlap":    None,
                "known_rewiring":               None,
                "score":                        None,
                "evidence_tier":                "ai_candidate",
                "notes":                        "",
                "pmids":                        [],
                "curator":                      "",
                "curated_date":                 ""
            }
            for sp in species if sp != "human"
        },

        "phenotypic_evidence": [
            {
                "model_species":   sp,
                "evidence_type":   "knockout",
                "pmid":            None,
                "score":           None,
                "description":     "",
                "supports_validity": None,
                "caveats":         "",
                "phenotype_match": None,
                "evidence_tier":   "ai_candidate",
                "curator":         "",
                "curated_date":    ""
            }
            for sp in species if sp != "human"
        ],

        "pharmacological_evidence": [
            {
                "drug":            "",
                "chembl_id":       None,
                "target":          "",
                "model_species":   sp,
                "evidence_type":   "in_vivo",
                "pmid":            None,
                "concordance":     None,
                "score":           None,
                "notes":           "",
                "clinical_stage":  None,
                "evidence_tier":   "ai_candidate",
                "curator":         "",
                "curated_date":    ""
            }
            for sp in species if sp != "human"
        ]
    }

    with open(output_path, "w") as f:
        json.dump(template, f, indent=2)

    print(f"\n  ✓ Template written to {output_path}")
    print(f"  Fill in all null values, then validate with:")
    print(f"  python validate_evidence.py --entry {output_path} --component {component_id}\n")


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Who Gives a Fly — Evidence Validator & Curation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all evidence blocks in pathways.json
  python validate_evidence.py --check

  # Show which components have no structured evidence (coverage report)
  python validate_evidence.py --report

  # Generate a blank template for a component
  python validate_evidence.py --template rb1 --pathway rb_pathway --species drosophila mouse

  # Validate a filled-in evidence draft
  python validate_evidence.py --entry my_evidence_draft.json --component rb1

  # Approve and merge into pathways.json
  python validate_evidence.py --approve my_evidence_draft.json --component rb1 --curator "J.Smith"
        """
    )

    parser.add_argument("--check",      action="store_true", help="Validate all evidence blocks in pathways.json")
    parser.add_argument("--report",     action="store_true", help="Show evidence coverage report")
    parser.add_argument("--entry",      type=str,            help="Path to a standalone evidence draft JSON to validate")
    parser.add_argument("--approve",    type=str,            help="Path to a validated draft to merge into pathways.json")
    parser.add_argument("--template",   type=str,            help="Component ID to generate a blank template for")
    parser.add_argument("--component",  type=str,            help="Component ID (required with --entry, --approve)")
    parser.add_argument("--pathway",    type=str,            default="rb_pathway", help="Pathway ID (for --template)")
    parser.add_argument("--species",    nargs="+",           default=["drosophila","mouse","zebrafish","worm"])
    parser.add_argument("--curator",    type=str,            default="", help="Curator name or ORCID (required with --approve)")
    parser.add_argument("--output",     type=str,            default="evidence_template.json", help="Output path for --template")
    parser.add_argument("--pathways",   type=str,            default="config/pathways.json")
    parser.add_argument("--schema",     type=str,            default="config/evidence_schema.json")

    args = parser.parse_args()

    if not any([args.check, args.report, args.entry, args.approve, args.template]):
        parser.print_help()
        return

    if args.report or args.check:
        with open(args.pathways) as f:
            db = json.load(f)

    if args.report:
        report = coverage_report(db)
        print_coverage_report(report)

    if args.check:
        ok = validate_pathways_file(args.pathways, args.schema)
        sys.exit(0 if ok else 1)

    if args.entry:
        if not args.component:
            print("ERROR: --entry requires --component")
            sys.exit(1)
        ok = validate_entry_file(args.entry, args.component, args.schema)
        sys.exit(0 if ok else 1)

    if args.approve:
        if not args.component:
            print("ERROR: --approve requires --component")
            sys.exit(1)
        if not args.curator:
            print("ERROR: --approve requires --curator")
            sys.exit(1)
        ok = approve_entry(args.approve, args.pathways, args.component, args.curator, args.schema)
        sys.exit(0 if ok else 1)

    if args.template:
        generate_entry_template(args.template, args.pathway, args.species, args.output)


if __name__ == "__main__":
    main()
