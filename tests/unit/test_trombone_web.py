from pathlib import Path


def test_trombone_web_contains_functional_data_and_interaction_surfaces():
    root = Path(__file__).parents[2]
    html = (root / "web" / "trombone" / "index.html").read_text(encoding="utf-8")
    app = (root / "web" / "trombone" / "app.js").read_text(encoding="utf-8")

    assert 'src="app.js"' in html
    for surface in ("volumeChart", "qualityChart", "export", "import", "search", "log"):
        assert f'id="{surface}"' in html
    for behavior in ("localStorage", "normalizeSession", "transformSessions", "forecastProgress", "searchRepertoire"):
        assert behavior in app
