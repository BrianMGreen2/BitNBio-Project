#!/usr/bin/env python3
"""
Who Gives a Fly — Data Enricher
================================
Automates enrichment of pathways.json with ground-truth data from public APIs.
Targets D1 (sequence conservation) and D2 (paralog counts) primarily, with
optional D3 expression data from GTEx / Expression Atlas.

All API-sourced data is written into a separate enriched/ layer and never
overwrites curator-validated entries. The scoring engine reads enriched/
data preferentially over base pathways.json annotations.

Usage:
    python data_enricher.py --component rb1 --dry-run
    python data_enricher.py --pathway rb_pathway
    python data_enricher.py --pathway all --skip-existing
    python data_enricher.py --check-apis           # Test which APIs are reachable
    python data_enricher.py --status               # Show enrichment status

Network note: APIs require outbound internet access.
Set ENRICHER_CACHE=1 to use local cache (data/cache/) for offline runs.
"""

import json
import os
import sys
import time
import argparse
import hashlib
from datetime import datetime, date
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from typing import Optional


# ─────────────────────────────────────────────────────────
# API clients (stdlib urllib only — no requests dependency)
# ─────────────────────────────────────────────────────────

APIS = {
    "ensembl":        "https://rest.ensembl.org",
    "uniprot":        "https://rest.uniprot.org",
    "chembl":         "https://www.ebi.ac.uk/chembl/api/data",
    "gtex":           "https://gtexportal.org/api/v2",
    "europepmc":      "https://www.ebi.ac.uk/europepmc/webservices/rest",
}

RATE_LIMITS = {
    "ensembl":   0.07,   # ~15 req/sec without API key
    "uniprot":   0.10,
    "chembl":    0.20,
    "gtex":      0.20,
    "europepmc": 0.10,
}

USE_CACHE = os.environ.get("ENRICHER_CACHE", "0") == "1"
CACHE_DIR = "data/cache"


class APIError(Exception):
    def __init__(self, api: str, endpoint: str, status: int, message: str):
        self.api      = api
        self.endpoint = endpoint
        self.status   = status
        super().__init__(f"{api} {endpoint} → HTTP {status}: {message}")


def _cache_key(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


def _cache_path(url: str) -> str:
    return os.path.join(CACHE_DIR, _cache_key(url) + ".json")


def fetch_json(url: str, api_name: str = "api",
               params: dict = None, headers: dict = None) -> dict:
    """
    Fetch JSON from a URL with caching, rate limiting, and error handling.
    """
    if params:
        url = url + "?" + urlencode(params)

    if USE_CACHE:
        cached = _cache_path(url)
        if os.path.exists(cached):
            with open(cached) as f:
                return json.load(f)

    req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        req_headers.update(headers)

    try:
        req  = Request(url, headers=req_headers)
        resp = urlopen(req, timeout=15)
        data = json.loads(resp.read().decode())
    except HTTPError as e:
        raise APIError(api_name, url, e.code, e.reason)
    except URLError as e:
        raise APIError(api_name, url, 0, str(e.reason))

    time.sleep(RATE_LIMITS.get(api_name, 0.1))

    if USE_CACHE:
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(_cache_path(url), "w") as f:
            json.dump(data, f)

    return data


def check_api_reachability() -> dict[str, bool]:
    """Test which APIs are reachable. Returns {api_name: reachable}."""
    results = {}
    probes = {
        "ensembl":   f"{APIS['ensembl']}/info/ping?content-type=application/json",
        "uniprot":   f"{APIS['uniprot']}/uniprotkb/P06400?format=json&fields=accession",
        "chembl":    f"{APIS['chembl']}/target/CHEMBL4523.json",
        "gtex":      f"{APIS['gtex']}/expression/geneExpression?gencodeId=ENSG00000139687.14&datasetId=gtex_v8",
        "europepmc": f"{APIS['europepmc']}/search?query=RB1&format=json&pageSize=1",
    }
    for name, url in probes.items():
        try:
            fetch_json(url, name)
            results[name] = True
            print(f"  ✓ {name:<15} reachable")
        except APIError as e:
            results[name] = False
            print(f"  ✗ {name:<15} unreachable (HTTP {e.status})")
        except Exception as e:
            results[name] = False
            print(f"  ✗ {name:<15} unreachable ({e})")
    return results


# ─────────────────────────────────────────────────────────
# D1 enrichment — Ensembl / UniProt
# ─────────────────────────────────────────────────────────

SPECIES_ENSEMBL = {
    "human":      "homo_sapiens",
    "mouse":      "mus_musculus",
    "drosophila": "drosophila_melanogaster",
    "zebrafish":  "danio_rerio",
    "worm":       "caenorhabditis_elegans",
}


def fetch_ensembl_homologs(gene_id: str, target_species: str) -> list[dict]:
    """
    Fetch homologs for a human Ensembl gene ID in a target species.
    Returns list of homolog records with percent_id and type.
    """
    sp = SPECIES_ENSEMBL.get(target_species)
    if not sp:
        return []

    url = f"{APIS['ensembl']}/homology/id/{gene_id}"
    try:
        data = fetch_json(url, "ensembl", params={
            "target_species": sp,
            "content-type": "application/json",
            "type": "all",
        })
        homologies = data.get("data", [{}])[0].get("homologies", [])
        return homologies
    except APIError as e:
        print(f"    WARN: Ensembl homology fetch failed for {gene_id} → {target_species}: {e}")
        return []


def fetch_ensembl_paralogs(gene_id: str) -> list[dict]:
    """Fetch human paralogs for a gene from Ensembl."""
    url = f"{APIS['ensembl']}/homology/id/{gene_id}"
    try:
        data = fetch_json(url, "ensembl", params={
            "target_species": "homo_sapiens",
            "type": "paralogues",
            "content-type": "application/json",
        })
        return data.get("data", [{}])[0].get("homologies", [])
    except APIError as e:
        print(f"    WARN: Ensembl paralog fetch failed for {gene_id}: {e}")
        return []


def enrich_D1_conservation(component: dict, ref_ensembl_id: str,
                            species_list: list[str]) -> dict:
    """
    Fetch sequence identity scores from Ensembl for all species pairs.
    Updates component['conservation'][pair]['percent_id_ensembl'].
    Returns a dict of enrichment results keyed by species pair.
    """
    enriched = {}

    for sp in species_list:
        if sp == "human":
            continue
        key = f"human_{sp}"

        homologs = fetch_ensembl_homologs(ref_ensembl_id, sp)
        if not homologs:
            enriched[key] = {"source": "ensembl", "status": "no_homolog_found", "percent_id": 0.0}
            continue

        # Take highest-confidence ortholog
        orthologs = [h for h in homologs if "ortholog" in h.get("type", "")]
        best = orthologs[0] if orthologs else homologs[0]

        percent_id = best.get("target", {}).get("perc_id", 0.0)
        enriched[key] = {
            "source":            "ensembl",
            "status":            "found",
            "homology_type":     best.get("type", "unknown"),
            "percent_id":        round(percent_id / 100, 4),   # normalise to 0–1
            "target_gene_id":    best.get("target", {}).get("id", ""),
            "target_gene_symbol":best.get("target", {}).get("display_label", ""),
            "retrieved_date":    date.today().isoformat(),
        }
        print(f"    D1 [{key}]: {percent_id:.1f}% identity ({best.get('type','')})")

    return enriched


def enrich_D2_paralogs(component: dict, ref_ensembl_id: str) -> dict:
    """
    Fetch paralog count from Ensembl for the human reference gene.
    """
    paralogs = fetch_ensembl_paralogs(ref_ensembl_id)
    paralog_ids = [p.get("target", {}).get("display_label", p.get("target", {}).get("id", ""))
                   for p in paralogs]
    result = {
        "source":           "ensembl",
        "n_paralogs":       len(paralogs),
        "paralog_symbols":  paralog_ids,
        "retrieved_date":   date.today().isoformat(),
    }
    print(f"    D2 [human paralogs]: {len(paralogs)} ({', '.join(paralog_ids[:5])})")
    return result


# ─────────────────────────────────────────────────────────
# D3 enrichment — GTEx expression
# ─────────────────────────────────────────────────────────

DISEASE_RELEVANT_TISSUES = {
    "rb_pathway":      ["Whole Blood", "Retina", "Adipose Tissue", "Breast - Mammary Tissue"],
    "notch_pathway":   ["Whole Blood", "Brain - Frontal Cortex", "Skin - Sun Exposed"],
    "wnt_pathway":     ["Colon - Transverse", "Liver", "Small Intestine - Terminal Ileum"],
}


def fetch_gtex_expression(gencode_id: str, tissues: list[str]) -> dict:
    """
    Fetch median TPM expression for a gene across specified tissues from GTEx v8.
    gencode_id example: 'ENSG00000139687.14'
    """
    url = f"{APIS['gtex']}/expression/geneExpression"
    try:
        data = fetch_json(url, "gtex", params={
            "gencodeId": gencode_id,
            "datasetId": "gtex_v8",
        })
        expressions = data.get("data", [])
        result = {}
        for entry in expressions:
            tissue = entry.get("tissueSiteDetailId", "")
            if any(t.lower() in tissue.lower() for t in tissues):
                result[tissue] = {
                    "median_tpm": entry.get("median", 0.0),
                    "unit": "TPM",
                }
        return result
    except APIError as e:
        print(f"    WARN: GTEx fetch failed for {gencode_id}: {e}")
        return {}


# ─────────────────────────────────────────────────────────
# D5 enrichment — ChEMBL
# ─────────────────────────────────────────────────────────

def fetch_chembl_activities(gene_symbol: str, limit: int = 20) -> list[dict]:
    """
    Fetch drug-target activity data from ChEMBL for a gene.
    Returns list of activity records with drug name, IC50, and clinical stage.
    """
    # First find ChEMBL target ID
    url = f"{APIS['chembl']}/target/search.json"
    try:
        data = fetch_json(url, "chembl", params={
            "q": gene_symbol,
            "limit": 5,
        })
        targets = data.get("targets", [])
        human_targets = [t for t in targets
                         if t.get("organism") == "Homo sapiens"
                         and t.get("target_type") == "SINGLE PROTEIN"]
        if not human_targets:
            print(f"    WARN: No ChEMBL target found for {gene_symbol}")
            return []

        target_chembl_id = human_targets[0]["target_chembl_id"]

        # Fetch activities
        act_url = f"{APIS['chembl']}/activity.json"
        act_data = fetch_json(act_url, "chembl", params={
            "target_chembl_id": target_chembl_id,
            "limit": limit,
            "standard_type__in": "IC50,Ki,Kd,EC50",
        })

        activities = act_data.get("activities", [])
        results = []
        for a in activities:
            results.append({
                "drug":         a.get("molecule_pref_name", a.get("molecule_chembl_id", "")),
                "chembl_id":    a.get("molecule_chembl_id", ""),
                "activity_type":a.get("standard_type", ""),
                "value":        a.get("standard_value", ""),
                "units":        a.get("standard_units", ""),
                "assay_type":   a.get("assay_type", ""),
                "target_id":    target_chembl_id,
            })
        print(f"    D5 [ChEMBL/{gene_symbol}]: {len(results)} activity records")
        return results

    except APIError as e:
        print(f"    WARN: ChEMBL fetch failed for {gene_symbol}: {e}")
        return []


def fetch_chembl_approved_drugs(gene_symbol: str) -> list[dict]:
    """
    Fetch only approved drugs for a target from ChEMBL.
    """
    url = f"{APIS['chembl']}/drug_indication.json"
    try:
        # Find target first
        t_url = f"{APIS['chembl']}/target/search.json"
        t_data = fetch_json(t_url, "chembl", params={"q": gene_symbol, "limit": 3})
        targets = [t for t in t_data.get("targets", [])
                   if t.get("organism") == "Homo sapiens"
                   and t.get("target_type") == "SINGLE PROTEIN"]
        if not targets:
            return []

        chembl_id = targets[0]["target_chembl_id"]
        act_data = fetch_json(
            f"{APIS['chembl']}/activity.json", "chembl",
            params={"target_chembl_id": chembl_id, "max_phase": 4, "limit": 10}
        )
        approved = [
            {"drug": a.get("molecule_pref_name", ""), "chembl_id": a.get("molecule_chembl_id", ""),
             "clinical_stage": "approved"}
            for a in act_data.get("activities", [])
        ]
        return approved
    except APIError:
        return []


# ─────────────────────────────────────────────────────────
# Enrichment orchestration
# ─────────────────────────────────────────────────────────

def enrich_component(component: dict, pathway_id: str,
                     species_list: list[str], dry_run: bool = False,
                     skip_existing: bool = False) -> dict:
    """
    Run all applicable enrichment steps for a component.
    Returns enrichment_record with fetched data and metadata.
    """
    cid = component["id"]
    ref_orth = component.get("orthologs", {}).get("human", {})

    ensembl_id  = ref_orth.get("ensembl_id")   # e.g. "ENSG00000139687"
    gencode_id  = ref_orth.get("gencode_id")    # e.g. "ENSG00000139687.14"
    gene_symbol = ref_orth.get("symbol", cid)

    record = {
        "component_id":    cid,
        "pathway_id":      pathway_id,
        "enriched_at":     datetime.now().isoformat(timespec="seconds"),
        "dry_run":         dry_run,
        "enrichments":     {},
    }

    print(f"\n  ── {cid} (human: {gene_symbol}) ──")

    # D1 + D2 via Ensembl (requires ensembl_id in pathways.json)
    if ensembl_id:
        if not skip_existing or "ensembl_homologs" not in component.get("_enriched", {}):
            print(f"    Fetching Ensembl homologs...")
            if not dry_run:
                d1_data = enrich_D1_conservation(component, ensembl_id, species_list)
                d2_data = enrich_D2_paralogs(component, ensembl_id)
                record["enrichments"]["D1_ensembl"] = d1_data
                record["enrichments"]["D2_ensembl"] = d2_data
            else:
                print(f"    [DRY RUN] Would fetch: GET {APIS['ensembl']}/homology/id/{ensembl_id}")
    else:
        print(f"    SKIP D1/D2: no 'ensembl_id' in human ortholog entry for {cid}")
        print(f"    → Add 'ensembl_id': 'ENSGXXX...' to pathways.json to enable")
        record["enrichments"]["D1_ensembl"] = {"status": "skipped", "reason": "no ensembl_id"}

    # D3 expression via GTEx (requires gencode_id)
    tissues = DISEASE_RELEVANT_TISSUES.get(pathway_id, [])
    if gencode_id and tissues:
        print(f"    Fetching GTEx expression ({len(tissues)} tissues)...")
        if not dry_run:
            expr_data = fetch_gtex_expression(gencode_id, tissues)
            record["enrichments"]["D3_gtex_expression"] = expr_data
        else:
            print(f"    [DRY RUN] Would fetch GTEx for {gencode_id}")
    else:
        reason = "no gencode_id" if not gencode_id else "no tissues configured for pathway"
        print(f"    SKIP D3 expression: {reason}")
        record["enrichments"]["D3_gtex"] = {"status": "skipped", "reason": reason}

    # D5 via ChEMBL (uses gene symbol — always available)
    if gene_symbol and gene_symbol not in ("—", "NONE"):
        print(f"    Fetching ChEMBL activity data for {gene_symbol}...")
        if not dry_run:
            approved = fetch_chembl_approved_drugs(gene_symbol)
            record["enrichments"]["D5_chembl_approved"] = approved
        else:
            print(f"    [DRY RUN] Would fetch ChEMBL for {gene_symbol}")
    else:
        print(f"    SKIP D5: no valid gene symbol")

    return record


def run_enrichment(pathways_path: str, output_dir: str,
                   pathway_id: str = "all", component_id: str = None,
                   species_list: list[str] = None,
                   dry_run: bool = False, skip_existing: bool = False):
    """
    Run enrichment for all or selected pathways/components.
    Writes results to output_dir/enriched/{pathway_id}__{component_id}.json.
    Never overwrites pathways.json directly.
    """
    with open(pathways_path) as f:
        db = json.load(f)

    if species_list is None:
        species_list = list(db["metadata"]["species"].keys())

    enriched_dir = os.path.join(output_dir, "enriched")
    os.makedirs(enriched_dir, exist_ok=True)

    selected = db["pathways"] if pathway_id == "all" \
               else [p for p in db["pathways"] if p["id"] == pathway_id]

    if not selected:
        print(f"ERROR: Pathway '{pathway_id}' not found.")
        sys.exit(1)

    all_records = []

    for pathway in selected:
        pid = pathway["id"]
        print(f"\n══ {pathway['name']} ══")

        for comp in pathway.get("components", []):
            if component_id and comp["id"] != component_id:
                continue

            record = enrich_component(
                comp, pid, species_list,
                dry_run=dry_run, skip_existing=skip_existing
            )
            all_records.append(record)

            if not dry_run:
                out_path = os.path.join(
                    enriched_dir, f"{pid}__{comp['id']}__enriched.json"
                )
                with open(out_path, "w") as f:
                    json.dump(record, f, indent=2)
                print(f"    ✓ Written → {out_path}")

    if dry_run:
        print(f"\n[DRY RUN] No files written. {len(all_records)} components would be enriched.")
    else:
        print(f"\n✓ Enrichment complete. {len(all_records)} components processed.")
        print(f"  Results in: {enriched_dir}/")
        print(f"  Next step: review enriched files, then run validate_evidence.py --report")

    return all_records


def enrichment_status(pathways_path: str, enriched_dir: str):
    """Show which components have been enriched and when."""
    with open(pathways_path) as f:
        db = json.load(f)

    print("\n═══ ENRICHMENT STATUS ═══\n")

    for pathway in db.get("pathways", []):
        pid = pathway["id"]
        print(f"  {pathway['name']}")

        for comp in pathway.get("components", []):
            cid = comp["id"]
            enriched_path = os.path.join(enriched_dir, f"{pid}__{cid}__enriched.json")

            if os.path.exists(enriched_path):
                with open(enriched_path) as f:
                    rec = json.load(f)
                ts  = rec.get("enriched_at", "unknown")
                keys = list(rec.get("enrichments", {}).keys())
                skipped = [k for k,v in rec.get("enrichments", {}).items()
                           if isinstance(v, dict) and v.get("status") == "skipped"]
                print(f"    ✅ {cid:<25} enriched {ts[:10]}  [{', '.join(keys)}]")
                if skipped:
                    print(f"       SKIPPED: {', '.join(skipped)}")
            else:
                missing = []
                if not comp.get("orthologs", {}).get("human", {}).get("ensembl_id"):
                    missing.append("no ensembl_id")
                if not comp.get("orthologs", {}).get("human", {}).get("gencode_id"):
                    missing.append("no gencode_id")
                status = f"({', '.join(missing)})" if missing else ""
                print(f"    🔶 {cid:<25} not yet enriched  {status}")

    print()
    print("  To add Ensembl/Gencode IDs, update the human ortholog entry in pathways.json:")
    print('  "human": { "symbol": "RB1", "ensembl_id": "ENSG00000139687",')
    print('             "gencode_id": "ENSG00000139687.14", ... }')
    print()


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Who Gives a Fly — Data Enricher (D1/D2/D3/D5 API integration)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data_enricher.py --check-apis
  python data_enricher.py --status
  python data_enricher.py --pathway rb_pathway --component rb1 --dry-run
  python data_enricher.py --pathway rb_pathway
  python data_enricher.py --pathway all --skip-existing

Note: Ensembl/Gencode IDs must be added to pathways.json human ortholog entries
before D1/D2/D3 enrichment can run. See --status for which are missing.

Set ENRICHER_CACHE=1 to cache API responses locally (data/cache/) for offline runs.
        """
    )
    parser.add_argument("--pathway",       default="rb_pathway", help="Pathway ID or 'all'")
    parser.add_argument("--component",     help="Specific component ID to enrich")
    parser.add_argument("--species",       nargs="+", default=["drosophila","mouse","zebrafish","worm"])
    parser.add_argument("--dry-run",       action="store_true", help="Show what would be fetched without calling APIs")
    parser.add_argument("--skip-existing", action="store_true", help="Skip components with existing enrichment files")
    parser.add_argument("--check-apis",    action="store_true", help="Test API reachability and exit")
    parser.add_argument("--status",        action="store_true", help="Show enrichment status for all components")
    parser.add_argument("--pathways",      default="config/pathways.json")
    parser.add_argument("--output",        default="data", help="Output directory for enriched/ files")
    args = parser.parse_args()

    if args.check_apis:
        print("\n═══ API REACHABILITY CHECK ═══\n")
        check_api_reachability()
        print()
        return

    if args.status:
        enrichment_status(args.pathways, os.path.join(args.output, "enriched"))
        return

    run_enrichment(
        pathways_path  = args.pathways,
        output_dir     = args.output,
        pathway_id     = args.pathway,
        component_id   = args.component,
        species_list   = args.species,
        dry_run        = args.dry_run,
        skip_existing  = args.skip_existing,
    )


if __name__ == "__main__":
    main()
