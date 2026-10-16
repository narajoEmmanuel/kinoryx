import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("dash")

from kinoryx.demo.synthetic import generate_demo_dataset
from kinoryx.pipeline import analyze_exploratory

module_path = Path(__file__).resolve().parents[1] / "apps" / "biomechanics_dashboard" / "app.py"
spec = importlib.util.spec_from_file_location("kinoryx_dashboard", module_path)
dashboard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dashboard)


def test_dashboard_initializes():
    assert dashboard.create_app().layout is not None


def test_demo_chart_default_layers_have_six_traces():
    figure = dashboard.build_figure(analyze_exploratory(generate_demo_dataset()))
    assert len(figure.data) == 6


def test_demo_chart_single_side_filtered_only():
    figure = dashboard.build_figure(
        analyze_exploratory(generate_demo_dataset()),
        view_mode="left",
        visible_layers=("filtered",),
    )
    assert len(figure.data) == 1
    assert figure.data[0].name == "Left filtered"


def test_graph_export_defaults_to_svg():
    assert dashboard.GRAPH_CONFIG["toImageButtonOptions"]["format"] == "svg"