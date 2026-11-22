"""Editorial and bilingual publication contracts."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROSE = [
    ROOT / "README.md", ROOT / "docs" / "README.es.md",
    ROOT / "docs" / "methodology.md", ROOT / "docs" / "methodology.es.md",
    ROOT / "docs" / "data_provenance.md", ROOT / "app.py",
]

def test_no_long_dashes_in_public_editorial_copy():
    for path in PROSE:
        source = path.read_text(encoding="utf-8")
        assert "\u2014" not in source, path.name
        assert "\u2013" not in source, path.name

def test_same_verified_numbers_in_both_readmes():
    en = (ROOT / "README.md").read_text(encoding="utf-8")
    es = (ROOT / "docs" / "README.es.md").read_text(encoding="utf-8")
    for value in ("1,067,371", "20.97", "1.53", "20.11", "4,875", "5,852", "4,234", "396", "2,662"):
        assert value in en and value in es, value
    assert "docs/README.es.md" in en
    assert "../README.md" in es

def test_distinguishes_powerbi_from_streamlit():
    for path in (ROOT / "README.md", ROOT / "docs" / "README.es.md"):
        source = path.read_text(encoding="utf-8")
        assert "app.py" in source
        assert ".pbix" in source
