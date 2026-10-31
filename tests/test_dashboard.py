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

def test_four_distinct_synchronized_panels():
    figure = dashboard.build_figure(analyze_exploratory(generate_demo_dataset()))
    assert [a.text for a in figure.layout.annotations] == [
        "Left · Raw", "Right · Raw", "Left · Filtered", "Right · Filtered"
    ]
    assert sum(
        getattr(figure.layout, f"xaxis{i}").matches is not None
        for i in (1, 2, 3, 4)
    ) >= 3
    assert len(figure.data) == 6


def test_vertical_layout_and_side_filter():
    result = analyze_exploratory(generate_demo_dataset())
    stacked = dashboard.build_figure(result, panel_layout="stack")
    assert stacked.layout.height >= 1040
    assert len(stacked.layout.annotations) == 4
    single = dashboard.build_figure(result, view_mode="left")
    assert len(single.layout.annotations) == 2
    assert [t.name for t in single.data] == [
        "Left raw", "Left filtered", "Left candidate peaks"
    ]


def test_candidates_only_and_invalid_layout():
    result = analyze_exploratory(generate_demo_dataset())
    only_peaks = dashboard.build_figure(result, visible_layers=("candidates",))
    assert len(only_peaks.data) == 2
    assert all("candidate" in t.name for t in only_peaks.data)
    with pytest.raises(ValueError, match="Unknown panel layout"):
        dashboard.build_figure(result, panel_layout="unsupported")
