"""Integration checks for graph rejection, resource validation and reproducible builds."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import yaml
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class CatalogContracts(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="catalog-contract-")
        self.root = Path(self.temp.name).resolve()
        self.assertTrue(self.root.is_relative_to(Path(tempfile.gettempdir()).resolve()))
        for folder in ("data", "schemas", "scripts"):
            shutil.copytree(ROOT / folder, self.root / folder)
        self.addCleanup(self.temp.cleanup)

    def build(self, output="catalog/v1", success=True):
        result = subprocess.run([sys.executable, str(self.root / "scripts/build_catalog.py"), "--output", str(self.root / "site" / output)], capture_output=True, text=True, env={**os.environ, "SOURCE_DATE_EPOCH": "1793491200"})
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_reproducible_build_and_ancestor_membership(self):
        self.build("check-a"); self.build("check-b")
        def hashes(folder):
            return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.rglob("*") if p.is_file()}
        self.assertEqual(hashes(self.root / "site/check-a"), hashes(self.root / "site/check-b"))
        index = json.loads((self.root / "site/check-a/search/index.json").read_text(encoding="utf8"))
        geocode = next(r for r in index["items"] if r["id"] == "op_search_geocoding")
        self.assertIn("spatial-analysis", geocode["category_ids"])

    def test_cycle_and_missing_parent_rejected(self):
        path = self.root / "data/vocab/categories.yaml"
        path.write_text(yaml.safe_dump([{"id":"a","label":"A","parent_ids":["b"]},{"id":"b","label":"B","parent_ids":["a"]}]), encoding="utf8")
        self.assertIn("cycle", self.build(success=False))
        path.write_text(yaml.safe_dump([{"id":"a","label":"A","parent_ids":["missing"]}]), encoding="utf8")
        self.assertIn("unknown parent", self.build(success=False))

    def test_resource_needs_evidence_and_has_separate_detail(self):
        folder = self.root / "data/resources"; folder.mkdir(exist_ok=True)
        resource = {"id":"res_contract_fixture","name":"<script>Fixture</script>","purpose":"Contract fixture only","resource_type":"dataset","source_url":"https://example.invalid/data","status":"active","category_ids":["research"],"scope":"Synthetic test data","access":"unknown","license_status":"unknown"}
        (folder / "fixture.yaml").write_text(yaml.safe_dump(resource), encoding="utf8")
        self.assertIn("missing Evidence", self.build(success=False))
        for n, claim in enumerate(("/source_url", "/scope", "/access", "/license_status")):
            evidence = {"id":f"ev_contract_fixture_{n}","subject_id":resource["id"],"claim_path":claim,"source_url":resource["source_url"],"source_type":"unknown","source_grade":"D","verification_state":"unverified"}
            (self.root / f"data/evidence/fixture-{n}.yaml").write_text(yaml.safe_dump(evidence), encoding="utf8")
        self.build()
        generated = self.root / "site/catalog/v1"
        index = json.loads((generated / "search/index.json").read_text(encoding="utf8"))
        self.assertTrue(any(r["id"] == resource["id"] and r["record_kind"] == "information_resource" for r in index["items"]))
        legacy = json.loads((generated / "search/operations.json").read_text(encoding="utf8"))
        self.assertTrue(all(r["record_kind"] == "operation" for r in legacy["items"]))
        detail = json.loads((generated / "resources/res_contract_fixture.json").read_text(encoding="utf8"))
        self.assertEqual(len(detail["evidence_ids"]), 4)
        page = (generated / "resources/res_contract_fixture.html").read_text(encoding="utf8")
        self.assertIn("&lt;script&gt;Fixture&lt;/script&gt;", page)
        self.assertNotIn("<script>", page)

    def test_static_navigation_absolute_entrypoints_and_evidence_links(self):
        self.build()
        generated = self.root / "site/catalog/v1"
        base = "https://ik-e.github.io/agent-capability-map/catalog/v1/"
        manifest = json.loads((generated / "manifest.json").read_text(encoding="utf8"))
        for url in manifest["entrypoints"].values():
            self.assertTrue(url.startswith(base))
            self.assertTrue((generated / url.removeprefix(base)).is_file(), url)
        class Links(HTMLParser):
            def __init__(self): super().__init__(); self.urls=[]; self.scripts=0
            def handle_starttag(self, tag, attrs):
                if tag == "script": self.scripts+=1
                if tag == "a": self.urls.append(dict(attrs).get("href", ""))
        for path in generated.rglob("*.html"):
            parser = Links(); parser.feed(path.read_text(encoding="utf8"))
            self.assertEqual(parser.scripts, 0)
            for url in parser.urls:
                self.assertTrue(url.startswith("https://"), url)
                if url.startswith(base): self.assertTrue((generated / url.removeprefix(base)).is_file(), url)
        index = (generated / "index.html").read_text(encoding="utf8")
        self.assertIn("res_seoul_open_data_catalog.html", index)
        master = (generated / "resources/res_seoul_bike_station_master.html").read_text(encoding="utf8")
        self.assertIn("주장별 근거", master)
        self.assertIn("실제 ST-* 값", master)

if __name__ == "__main__":
    unittest.main()
