#!/usr/bin/env python3
"""Validate authored YAML and generate the versioned static catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMAS = ROOT / "schemas" / "v1"
OUTPUT = ROOT / "site" / "catalog" / "v1"
STATUS = {"active", "beta", "deprecated", "archived", "unknown", "draft"}
URL_KEYS = {
    "docs_url", "api_base_url", "api_spec_url", "mcp_endpoint_url",
    "mcp_repo_url", "sdk_repo_url", "source_repo_url", "other_url",
}
PACKAGE_KEYS = {"mcp_package", "sdk_package"}


class CatalogError(Exception):
    pass


def load_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as stream:
            value = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise CatalogError(f"{path.relative_to(ROOT)}: {exc}") from exc
    if value is None:
        raise CatalogError(f"{path.relative_to(ROOT)}: file is empty")
    return value


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(json_bytes(value))


def validate_schema(value: Any, schema_path: Path, source_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda err: list(map(str, err.absolute_path)))
    if errors:
        details = "; ".join(
            f"/{'/'.join(map(str, error.absolute_path))}: {error.message}" for error in errors
        )
        raise CatalogError(f"{source_path.relative_to(ROOT)}: {details}")


def add_unique(records: dict[str, dict[str, Any]], record: dict[str, Any], source: Path) -> None:
    record_id = record["id"]
    if record_id in records:
        raise CatalogError(f"duplicate id '{record_id}' in {source.relative_to(ROOT)}")
    records[record_id] = record


def pointer_value(subject: Any, pointer: str, evidence_id: str) -> Any:
    if not pointer.startswith("/"):
        raise CatalogError(f"{evidence_id}: claim_path must be an RFC 6901 JSON Pointer")
    current = subject
    for raw_token in pointer[1:].split("/"):
        if re.search(r"~(?![01])", raw_token):
            raise CatalogError(f"{evidence_id}: invalid RFC 6901 escape in claim_path")
        token = raw_token.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            if token.isdecimal():
                raise CatalogError(f"{evidence_id}: numeric array indexes are not stable claim paths")
            raise CatalogError(f"{evidence_id}: claim_path may point to an array, not into an array")
        if not isinstance(current, dict) or token not in current:
            raise CatalogError(f"{evidence_id}: claim_path does not exist in the canonical subject record")
        current = current[token]
    return current


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT, help="Generated catalog directory")
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT / "site").resolve()) or output == (ROOT / "site").resolve():
        raise CatalogError("generated output must be a child directory of site/")

    services: dict[str, dict[str, Any]] = {}
    integrations: dict[str, dict[str, Any]] = {}
    bindings: dict[str, dict[str, Any]] = {}
    operations: dict[str, dict[str, Any]] = {}
    evidence: dict[str, dict[str, Any]] = {}
    service_sources: dict[str, Path] = {}
    source_files = sorted(DATA.rglob("*.yaml"))
    if not source_files:
        raise CatalogError("no authored YAML files found under data/")

    for path in sorted((DATA / "services").rglob("service.yaml")):
        bundle = load_yaml(path)
        validate_schema(bundle, SCHEMAS / "service-bundle.schema.json", path)
        service = bundle["service"]
        add_unique(services, service, path)
        service_sources[service["id"]] = path
        for integration in bundle["integrations"]:
            add_unique(integrations, integration, path)
        for binding in bundle["bindings"]:
            add_unique(bindings, binding, path)

    for path in sorted((DATA / "operations").glob("*.yaml")):
        operation = load_yaml(path)
        validate_schema(operation, SCHEMAS / "operation.schema.json", path)
        add_unique(operations, operation, path)

    for path in sorted((DATA / "evidence").glob("*.yaml")):
        item = load_yaml(path)
        validate_schema(item, SCHEMAS / "evidence.schema.json", path)
        add_unique(evidence, item, path)

    vocab_path = DATA / "vocab" / "categories.yaml"
    categories = load_yaml(vocab_path) if vocab_path.exists() else []
    category_ids = {item["id"] for item in categories}
    if len(category_ids) != len(categories):
        raise CatalogError("category vocabulary contains duplicate IDs")

    subjects: dict[str, dict[str, Any]] = {**services, **integrations, **bindings, **operations}
    operation_bindings: dict[str, list[dict[str, Any]]] = defaultdict(list)
    required_location: dict[str, set[str]] = {
        "http_api": {"api_base_url", "api_spec_url"},
        "sdk": {"sdk_package"},
        "agent_connector": {"other_url", "source_repo_url"},
        "other": {"other_url", "source_repo_url"},
    }
    for integration in integrations.values():
        if integration["service_id"] not in services:
            raise CatalogError(f"{integration['id']}: service_id does not resolve")

    for binding in bindings.values():
        kind = binding["resource_kind"]
        integration = integrations.get(binding["integration_id"])
        if integration is None:
            raise CatalogError(f"{binding['id']}: integration_id does not resolve")
        if integration["service_id"] not in services:
            raise CatalogError(f"{binding['id']}: owning service does not resolve")
        schemes = binding["auth_schemes"]
        if "unknown" in schemes and len(schemes) != 1:
            raise CatalogError(f"{binding['id']}: auth_schemes unknown must be the only value")
        locations = binding["locations"]
        if binding["status"] == "active":
            needed = required_location.get(kind, set())
            if kind == "mcp_server":
                transport = binding.get("transport")
                needed = {"mcp_package"} if transport == "stdio" else {"mcp_endpoint_url"}
            if not (set(locations) & needed):
                raise CatalogError(f"{binding['id']}: active {kind} needs one of {sorted(needed)}")
        transport = binding.get("transport")
        if kind == "http_api" and transport not in {"http", "unknown"}:
            raise CatalogError(f"{binding['id']}: http_api transport must be http or unknown")
        if kind == "mcp_server":
            if transport not in {"stdio", "streamable_http", "sse", "unknown"}:
                raise CatalogError(f"{binding['id']}: invalid MCP transport")
            if not binding.get("mcp_primitives"):
                raise CatalogError(f"{binding['id']}: MCP binding needs mcp_primitives")
            if transport == "stdio" and "mcp_package" not in locations:
                raise CatalogError(f"{binding['id']}: stdio MCP needs mcp_package")
            if transport in {"streamable_http", "sse"} and "mcp_endpoint_url" not in locations:
                raise CatalogError(f"{binding['id']}: remote MCP needs mcp_endpoint_url")
            if transport == "sse":
                print(f"warning: {binding['id']}: MCP SSE transport is deprecated", file=sys.stderr)
        if kind == "sdk" and transport not in {None, "other", "unknown"}:
            raise CatalogError(f"{binding['id']}: SDK transport should be omitted or unknown")
        allowed_ref = {"http_api": "http_operation", "mcp_server": "mcp_tool", "sdk": "sdk_symbol"}.get(kind)
        for ref in binding.get("operation_refs", []):
            operation_id = ref["operation_id"]
            operation = operations.get(operation_id)
            if operation is None:
                raise CatalogError(f"{binding['id']}: operation reference '{operation_id}' does not resolve")
            if ref.get("native_ref") and ref["native_ref"]["kind"] not in {allowed_ref, "other"}:
                raise CatalogError(f"{binding['id']}: native_ref kind does not match resource_kind")
            if any(row["id"] == binding["id"] for row in operation_bindings[operation_id]):
                raise CatalogError(f"{binding['id']}: duplicate operation reference '{operation_id}'")
            operation_bindings[operation_id].append(binding)

    for operation in operations.values():
        unknown_categories = set(operation.get("category_ids", [])) - category_ids
        if unknown_categories:
            raise CatalogError(f"{operation['id']}: unknown categories {sorted(unknown_categories)}")
        if operation["status"] == "active" and not any(
            binding["status"] == "active" for binding in operation_bindings[operation["id"]]
        ):
            print(f"warning: active operation {operation['id']} has no active binding; excluded from search")

    evidence_by_subject: dict[str, list[dict[str, Any]]] = defaultdict(list)
    evidence_claim_sources: set[tuple[str, str, str]] = set()
    for item in evidence.values():
        subject = subjects.get(item["subject_id"])
        if subject is None:
            raise CatalogError(f"{item['id']}: subject_id does not resolve")
        pointer_value(subject, item["claim_path"], item["id"])
        claim_source = (item["subject_id"], item["claim_path"], item["source_url"])
        if claim_source in evidence_claim_sources:
            raise CatalogError(f"{item['id']}: duplicate evidence for the same subject, path and source")
        evidence_claim_sources.add(claim_source)
        evidence_by_subject[item["subject_id"]].append(item)

    def has_claim(subject_id: str, path: str, *, verified: bool = False) -> bool:
        matches = [row for row in evidence_by_subject[subject_id] if row["claim_path"] == path]
        if not matches:
            return False
        if not verified:
            return True
        return any(row["verification_state"] == "verified" and row["source_grade"] in {"A", "B"} for row in matches)

    binding_claims: dict[str, list[str]] = {}
    for binding in bindings.values():
        claims = ["/resource_kind", "/status"]
        if "version" in binding:
            claims.append("/version")
        claims.extend(f"/locations/{key}/{('url' if key in URL_KEYS else 'package')}" for key in binding["locations"])
        claims.extend(["/auth_schemes"])
        if "transport" in binding:
            claims.append("/transport")
        if binding.get("operation_refs"):
            claims.append("/operation_refs")
        if "mcp_primitives" in binding:
            claims.append("/mcp_primitives")
        binding_claims[binding["id"]] = claims
        missing = [claim for claim in claims if not has_claim(binding["id"], claim)]
        if binding["status"] == "active" and missing:
            raise CatalogError(f"{binding['id']}: active binding missing Evidence for {', '.join(missing)}")
    for operation in operations.values():
        claims = ["/effect"]
        if operation.get("inputs"):
            claims.append("/inputs")
        if operation["status"] == "active":
            missing = [claim for claim in claims if not has_claim(operation["id"], claim)]
            if missing:
                raise CatalogError(f"{operation['id']}: active operation missing Evidence for {', '.join(missing)}")

    search_rows = []
    for operation in sorted(operations.values(), key=lambda row: row["id"]):
        if operation["status"] != "active":
            continue
        active_bindings = [b for b in operation_bindings[operation["id"]] if b["status"] == "active"]
        if not active_bindings:
            continue
        per_binding = []
        for binding in sorted(active_bindings, key=lambda row: row["id"]):
            integration = integrations[binding["integration_id"]]
            service = services[integration["service_id"]]
            all_claims_verified = all(has_claim(binding["id"], claim, verified=True) for claim in binding_claims[binding["id"]])
            claim_states = {
                claim: "verified" if has_claim(binding["id"], claim, verified=True) else "unknown"
                for claim in binding_claims[binding["id"]]
            }
            per_binding.append({
                "id": binding["id"],
                "name": binding["name"],
                "resource_kind": binding["resource_kind"],
                "transport": binding.get("transport", "unknown"),
                "auth_schemes": binding["auth_schemes"],
                "integration_name": integration["name"],
                "service_name": service["name"],
                "provider_name": service["provider_name"],
                "claim_states": claim_states,
                "status": binding["status"],
                "evidence_state": "verified" if all_claims_verified else "unknown",
                "detail_url": f"../bindings/{binding['id']}.json",
            })
        search_rows.append({
            "id": operation["id"],
            "name": operation["name"],
            "purpose": operation["purpose"],
            "category_ids": operation.get("category_ids", []),
            "category_labels": [row["label"] for row in categories if row["id"] in operation.get("category_ids", [])],
            "aliases": operation.get("aliases", []),
            "entity_types": operation.get("entity_types", []),
            "effect": operation["effect"],
            "effect_evidence_state": "verified" if has_claim(operation["id"], "/effect", verified=True) else "unknown",
            "status": operation["status"],
            "inputs": operation.get("inputs", []),
            "binding_summaries": per_binding,
            "detail_url": f"../operations/{operation['id']}.json",
        })

    source_hash = hashlib.sha256()
    for path in source_files:
        source_hash.update(path.relative_to(ROOT).as_posix().encode("utf-8"))
        source_hash.update(path.read_bytes())
    revision = source_hash.hexdigest()[:16]
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if epoch:
        generated_at = datetime.fromtimestamp(int(epoch), timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    else:
        commit_time = subprocess.run(
            ["git", "log", "-1", "--format=%cI", "--", "data"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        ).stdout.strip()
        generated_at = commit_time or None

    if output.exists():
        shutil.rmtree(output)

    for folder in ("services", "integrations", "bindings", "operations", "evidence", "browse", "search", "bulk"):
        (output / folder).mkdir(parents=True, exist_ok=True)
    for record in services.values():
        write_json(output / "services" / f"{record['id']}.json", record)
    for record in integrations.values():
        write_json(output / "integrations" / f"{record['id']}.json", record)
    reverse_refs: dict[str, list[str]] = defaultdict(list)
    for operation_id, rows in operation_bindings.items():
        reverse_refs[operation_id] = sorted(b["id"] for b in rows)
    for record in operations.values():
        detail = {**record, "binding_ids": reverse_refs[record["id"]], "evidence_ids": sorted(e["id"] for e in evidence_by_subject[record["id"]])}
        write_json(output / "operations" / f"{record['id']}.json", detail)
    for record in bindings.values():
        integration = integrations[record["integration_id"]]
        detail = {**record, "service_id": integration["service_id"], "evidence_ids": sorted(e["id"] for e in evidence_by_subject[record["id"]])}
        write_json(output / "bindings" / f"{record['id']}.json", detail)
    for record in evidence.values():
        write_json(output / "evidence" / f"{record['id']}.json", record)

    search_index = {
        "algorithm": "lexical-v3",
        "normalization": "Unicode NFKC, casefold, tokenization, Korean common-particle stripping",
        "weights": {"exact_id": 20, "exact_name": 10, "name_token": 5, "alias": 4, "purpose": 2, "entity_type": 1, "context": 2},
        "context_fields": ["binding_name", "integration_name", "service_name", "provider_name", "resource_kind", "transport", "auth_schemes", "category_labels"],
        "minimum_query_term_coverage": "min(2, unique_query_terms)",
        "tie_break": "id_ascending",
        "default_limit": 5,
        "max_limit": 20,
        "items": search_rows,
    }
    write_json(output / "search" / "operations.json", search_index)
    browse_index = {
        "categories": categories,
        "services": [
            {"id": s["id"], "name": s["name"], "summary": s["summary"], "integration_ids": sorted(i["id"] for i in integrations.values() if i["service_id"] == s["id"])}
            for s in sorted(services.values(), key=lambda row: row["name"].casefold())
        ],
    }
    write_json(output / "browse" / "index.json", browse_index)
    bulk_records = [*services.values(), *integrations.values(), *bindings.values(), *operations.values(), *evidence.values()]
    bulk_path = output / "bulk" / "catalog.jsonl"
    bulk_path.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in sorted(bulk_records, key=lambda row: row["id"])), encoding="utf-8")
    manifest = {
        "catalog_version": "1",
        "schema_version": "1",
        "catalog_revision": revision,
        "generated_at": generated_at,
        "counts": {"services": len(services), "integrations": len(integrations), "bindings": len(bindings), "operations": len(operations), "searchable_operations": len(search_rows), "evidence": len(evidence)},
        "search_index": "search/operations.json",
        "browse_index": "browse/index.json",
        "detail_patterns": {"operation": "operations/{id}.json", "binding": "bindings/{id}.json", "evidence": "evidence/{id}.json"},
        "bulk_catalog": "bulk/catalog.jsonl",
        "bulk_catalog_default_for_queries": False,
    }
    write_json(output / "manifest.json", manifest)
    print(f"Catalog generated: {output} ({len(search_rows)} searchable operations; revision {revision})")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CatalogError as exc:
        print(f"catalog error: {exc}", file=sys.stderr)
        raise SystemExit(1)
