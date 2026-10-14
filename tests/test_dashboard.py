import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("dash")

module_path = Path(__file__).resolve().parents[1] / "apps" / "biomechanics_dashboard" / "app.py"
spec = importlib.util.spec_from_file_location("kinoryx_dashboard", module_path)
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


def test_dashboard_initializes():
    assert dashboard.create_app().layout is not None


def test_demo_chart():
    from kinoryx.demo.synthetic import generate_demo_dataset
    from kinoryx.pipeline import analyze_exploratory
    figure = dashboard.build_figure(analyze_exploratory(generate_demo_dataset()))
    assert len(figure.data) == 6
