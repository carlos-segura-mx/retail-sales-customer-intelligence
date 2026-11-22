"""Run on GitHub Actions with Streamlit installed; local environments may lack it."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

entry = Path(__file__).resolve().parents[1] / "app.py"
app = AppTest.from_file(str(entry), default_timeout=60).run()
if app.exception:
    raise AssertionError("Spanish app failed: " + str(app.exception))
assert len(app.tabs) == 6, "Expected six dashboard tabs"
assert "Inteligencia de ventas y clientes" in app.title[0].value
assert any("Ventas positivas" == metric.label for metric in app.metric)
app.sidebar.radio[0].set_value("English").run()
if app.exception:
    raise AssertionError("English app failed: " + str(app.exception))
assert "Retail Sales & Customer Intelligence" in app.title[0].value
assert any("Positive sales" == metric.label for metric in app.metric)
print("PASS: Spanish and English dashboard with six tabs")
