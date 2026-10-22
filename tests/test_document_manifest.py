"""
Keeps docs/documents.toml in step with the repository, per
docs/schemas/schema-document-descriptor.md.
"""

import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "docs" / "documents.toml"

REQUIRED = {"path", "title", "type", "status", "normative", "audience", "summary"}
OPTIONAL = {"governed_by", "depends_on", "supersedes", "superseded_by", "version"}
TYPES = {"overview", "license", "policy", "project-record", "research", "model", "schema",
         "template", "data-source", "engineering", "code-guide", "community"}
STATUSES = {"draft", "proposed", "active", "superseded"}
AUDIENCES = {"everyone", "contributors", "scientists", "developers", "maintainers", "worldbuilders"}
ROOT_DOCUMENTS = ["README.md", "NAVIGATION.md", "LICENSE", "LICENSE-CONTENT"]


def documents_in_scope() -> set[str]:
    """Schema section 6: every .md and .txt under docs/, plus the root documents."""
    docs = {p.relative_to(REPO).as_posix() for p in (REPO / "docs").rglob("*")
            if p.is_file() and p.suffix in (".md", ".txt")}
    return docs | {name for name in ROOT_DOCUMENTS if (REPO / name).exists()}


@pytest.fixture(scope="module")
def entries() -> list[dict]:
    with open(MANIFEST, "rb") as f:
        return tomllib.load(f)["document"]


@pytest.fixture(scope="module")
def by_path(entries) -> dict[str, dict]:
    return {e["path"]: e for e in entries}


def test_paths_are_unique(entries):
    paths = [e["path"] for e in entries]
    assert len(paths) == len(set(paths))


def test_every_document_is_described(by_path):
    missing = documents_in_scope() - set(by_path)
    assert not missing, f"add these to docs/documents.toml: {sorted(missing)}"


def test_every_entry_is_a_real_document(by_path):
    stale = set(by_path) - documents_in_scope()
    assert not stale, f"these entries don't match a document in scope: {sorted(stale)}"


def test_descriptors_have_exactly_the_allowed_attributes(entries):
    for e in entries:
        assert REQUIRED <= set(e), (e.get("path"), REQUIRED - set(e))
        assert set(e) <= REQUIRED | OPTIONAL, (e["path"], set(e) - REQUIRED - OPTIONAL)


def test_attribute_values_are_valid(entries):
    for e in entries:
        where = e["path"]
        assert e["type"] in TYPES, where
        assert e["status"] in STATUSES, where
        assert isinstance(e["normative"], bool), where
        assert e["audience"] and set(e["audience"]) <= AUDIENCES, where
        assert isinstance(e["depends_on"] if "depends_on" in e else [], list), where


def test_summaries_are_one_sentence_lines(entries):
    for e in entries:
        summary = e["summary"]
        assert "\n" not in summary and summary.endswith("."), e["path"]
        assert 20 <= len(summary) <= 200, e["path"]


def test_titles_match_headings(entries):
    for e in entries:
        lines = (REPO / e["path"]).read_text(encoding="utf-8").splitlines()
        if lines and lines[0].startswith("# "):
            assert e["title"] == lines[0][2:].strip(), e["path"]


def test_references_resolve(entries, by_path):
    for e in entries:
        where = e["path"]
        for ref in e.get("depends_on", []) + [e[k] for k in ("governed_by", "supersedes") if k in e]:
            assert ref in by_path, f"{where} refers to {ref}, which is not in the manifest"
            assert ref != where, f"{where} refers to itself"
        if "superseded_by" in e:
            assert (REPO / e["superseded_by"]).exists(), where
            assert e["superseded_by"] != where, where


def test_governing_documents_are_normative_schemas_or_templates(entries, by_path):
    for e in entries:
        if "governed_by" in e:
            governor = by_path[e["governed_by"]]
            assert governor["type"] in ("schema", "template"), e["path"]


def test_status_rules(entries):
    for e in entries:
        where = e["path"]
        in_archive = where.startswith("docs/archive/")
        if e["status"] == "superseded":
            assert "superseded_by" in e, f"{where}: superseded documents name their replacement"
            assert in_archive, f"{where}: superseded documents live in docs/archive/"
        else:
            assert "superseded_by" not in e, f"{where}: only superseded documents have superseded_by"
            assert not in_archive, f"{where}: everything in docs/archive/ is superseded"
        if e["status"] == "proposed":
            assert not e["normative"], f"{where}: a proposal can't be binding yet"


def test_supersession_is_recorded_both_ways(entries, by_path):
    for e in entries:
        if "supersedes" in e:
            old = by_path[e["supersedes"]]
            assert old.get("superseded_by") == e["path"], e["path"]
