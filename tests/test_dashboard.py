import base64
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
    app = dashboard.create_app()
    assert app.layout is not None
    assert len(app.callback_map) == 2


def test_demo_chart():
    result = analyze_exploratory(generate_demo_dataset())
    fig = dashboard.build_figure(result)
    assert len(fig.data) == 6


def test_side_filter():
    result = analyze_exploratory(generate_demo_dataset())
    fig = dashboard.build_figure(result, side="left")
    assert len(fig.data) == 3
    assert all("Left" in trace.name for trace in fig.data)


def test_layer_visibility():
    result = analyze_exploratory(generate_demo_dataset())
    fig = dashboard.build_figure(result, side="both", layers=["filtered"])
    assert len(fig.data) == 2
    assert all("filtered" in trace.name for trace in fig.data)


def test_invalid_upload_rejected():
    with pytest.raises(ValueError, match="decoded"):
        dashboard.decode_csv("data:text/csv;base64,###")


def test_demo_upload_round_trip():
    csv = generate_demo_dataset().to_csv(index=False).encode("utf-8")
    contents = "data:text/csv;base64," + base64.b64encode(csv).decode("ascii")
    decoded = dashboard.decode_csv(contents)
    assert len(decoded) == 1200


def test_table_disclaimer():
    result = analyze_exploratory(generate_demo_dataset())
    table = dashboard._candidate_table(result, "both")
    assert "not initial contacts or toe-offs" in table.children[-1].children