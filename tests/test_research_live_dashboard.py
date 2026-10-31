"""Research-only visualisation tests use synthetic samples, not participant data."""
import importlib.util
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("dash")
pytest.importorskip("plotly")

from kinoryx.io.xsens_emg import EmgChannel, EmgRecording
from kinoryx.research_lab import make_emg_figure, preview_transform
from kinoryx.plot_layout import plan_subplot_layout, wrap_plot_title


def _synthetic() -> EmgRecording:
    fs = 2000.0
    times = np.arange(2000) / fs
    left = np.sin(2 * np.pi * 80 * times)
    right = np.sin(2 * np.pi * 120 * times)
    return EmgRecording(
        channels=(
            EmgChannel(0, "Synthetic left", "test", "1", fs),
            EmgChannel(1, "Synthetic right", "test", "2", fs),
        ),
        samples=(tuple(left), tuple(right)),
        sample_count=2000,
        sampling_hz=fs,
        source_timestamp=None,
    )


def test_original_is_always_present_in_comparison():
    sample = _synthetic()
    raw = make_emg_figure(sample, "all", 0, 1, "raw")
    assert len(raw.data) == 2
    assert all("raw EMG" in trace.name for trace in raw.data)
    compared = make_emg_figure(sample, "all", 0.1, 0.25, "rms")
    assert len(compared.data) == 4
    assert sum("raw EMG" in trace.name for trace in compared.data) == 2
    assert all(len(trace.x) == 500 for trace in compared.data)


def test_synthetic_filter_changes_preview_without_changing_source():
    sample = _synthetic()
    original = np.asarray(sample.samples[0])
    before = original.copy()
    filtered = preview_transform(original, sample.sampling_hz, "bandpass")
    envelope = preview_transform(original, sample.sampling_hz, "rms")
    assert filtered.shape == original.shape
    assert envelope.shape == original.shape
    assert np.all(envelope >= 0)
    assert np.array_equal(original, before)


@pytest.mark.parametrize("mode", ["nonsense", "filtered"])
def test_unknown_preview_rejected(mode):
    with pytest.raises(ValueError, match="Unknown"):
        preview_transform(np.arange(1000, dtype=float), 2000, mode)


def test_invalid_channel_or_window_rejected():
    source = _synthetic()
    for ch, start, window in [
        ("3", 0, 1),
        ("all", -0.1, 1),
        ("all", 0, 0),
        ("all", 100, 1),
    ]:
        with pytest.raises(ValueError):
            make_emg_figure(source, ch, start, window, "raw")


def test_dashboard_serves_lab_on_same_localhost_server():
    file_path = Path(__file__).resolve().parents[1] / "apps/biomechanics_dashboard/app.py"
    spec = importlib.util.spec_from_file_location("kinoryx_visual_test_app", file_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dashboard = module.create_app()
    client = dashboard.server.test_client()
    main_response = client.get("/")
    lab_response = client.get("/lab/")
    assert main_response.status_code == 200
    assert lab_response.status_code == 200
    dashboard_response = client.get("/dashboard/")
    assert dashboard_response.status_code == 200
    assert b"Choose your workspace" in main_response.data
    assert b"Laboratory" in main_response.data
    assert b"Dashboard" in main_response.data
    assert b"Biomechanics Dashboard" in dashboard_response.data
    assert b"Laboratory" in lab_response.data
    assert b"Biomechanics Dashboard" not in lab_response.data
    for stage in ("exploration", "quality", "experimentation", "evaluation"):
        assert client.get(f"/lab/{stage}").status_code == 200


def test_emg_chart_has_one_shared_y_axis_label():
    recording = _synthetic()
    figure = make_emg_figure(recording, "all", 0, 1, "raw")
    assert all(axis.title.text is None for axis in (figure.layout.yaxis, figure.layout.yaxis2))
    captions = [note for note in figure.layout.annotations
                if "EMG amplitude (unit not established)" in note.text]
    assert len(captions) == 1
    assert figure.layout.height > 460


def test_plot_layout_expands_when_scientific_titles_are_long():
    short = plan_subplot_layout(["Right rectus femoris | Raw EMG"] * 4, cols=1)
    long_title = (
        "Right rectus femoris | Raw EMG | an unusually detailed scientific "
        "annotation covering an extended multi-line acquisition description "
        "that must never collide with another panel or axis label"
    )
    longer = plan_subplot_layout([long_title] * 4, cols=1)
    assert longer.height > short.height
    assert longer.vertical_spacing > short.vertical_spacing
    assert "<br>" in longer.titles[0]
    escaped, lines = wrap_plot_title("<test> & signal", 10)
    assert "&lt;" in escaped and "&amp;" in escaped
    assert lines >= 2



def test_local_server_enables_hot_reload(monkeypatch):
    """Ensure local development can keep the same server process workflow."""
    file_path = Path(__file__).resolve().parents[1] / "apps/biomechanics_dashboard/app.py"
    spec = importlib.util.spec_from_file_location("kinoryx_dev_reload_test_app", file_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class StubApp:
        def __init__(self):
            self.kwargs = None

        def run(self, **kwargs):
            self.kwargs = kwargs

    app = StubApp()
    monkeypatch.setattr(module, "create_app", lambda: app)
    module.run_local_server()
    assert app.kwargs == {
        "host": "127.0.0.1",
        "port": 8050,
        "debug": True,
        "use_reloader": True,
        "dev_tools_hot_reload": True,
    }



def test_four_explicit_lab_subpages_and_saved_exploration():
    from kinoryx.research_lab import (
        STAGES, exploration_content, other_stage_content,
        stage_from_path,
    )
    from kinoryx.lab_workspace import DEFAULT_WORKSPACE
    assert [slug for slug, _ in STAGES] == [
        "exploration", "quality", "experimentation", "evaluation"
    ]
    assert stage_from_path("/lab/") == "exploration"
    assert stage_from_path("/lab/exploration") == "exploration"
    assert stage_from_path("/lab/quality") == "quality"
    assert stage_from_path("/lab/experimentation") == "experimentation"
    assert stage_from_path("/lab/evaluation") == "evaluation"
    assert stage_from_path("/lab/unknown") == "exploration"
    assert DEFAULT_WORKSPACE == {"left": ["0"], "right": []}
    assert exploration_content(_synthetic()) is not None
    for stage in ("quality", "experimentation", "evaluation"):
        assert other_stage_content(stage) is not None


def test_raw_workspace_arrangements_preserve_original_points():
    from kinoryx.lab_workspace import build_workspace_figure, canonical_workspace
    recording = _synthetic()
    layout = {"left": ["0"], "right": ["1"]}
    overlay = build_workspace_figure(recording, layout, mode="overlay",
                                     start_seconds=0.1, window_seconds=0.25)
    side = build_workspace_figure(recording, layout, mode="side",
                                  start_seconds=0.1, window_seconds=0.25)
    stacked = build_workspace_figure(recording, layout, mode="stack",
                                     start_seconds=0.1, window_seconds=0.25)
    assert len(overlay.data) == len(side.data) == len(stacked.data) == 2
    for figure in (overlay, side, stacked):
        assert all(len(trace.x) == 500 for trace in figure.data)
        assert all("synthetic" in trace.name for trace in figure.data)
        np.testing.assert_allclose(
            np.asarray(figure.data[0].y, dtype=float),
            np.asarray(recording.samples[0][200:700], dtype=float),
        )
    assert overlay.data[0].line.color != overlay.data[1].line.color
    assert canonical_workspace({"left": ["0", "0", "unknown"], "right": ["1"]},
                               recording) == {"left": ["0"], "right": ["1"]}
    with pytest.raises(ValueError):
        build_workspace_figure(recording, layout, mode="unknown")
    with pytest.raises(ValueError):
        build_workspace_figure(recording, layout, start_seconds=-2)


def test_empty_panel_b_never_generates_a_blank_plot():
    from kinoryx.lab_workspace import build_workspace_figure, DEFAULT_WORKSPACE
    recording = _synthetic()
    for arrangement in ("side", "stack", "overlay"):
        figure = build_workspace_figure(
            recording, DEFAULT_WORKSPACE, mode=arrangement,
            start_seconds=0.1, window_seconds=0.25,
        )
        assert len(figure.data) == 1
        assert len(figure.data[0].x) == 500
        assert not any("Panel B" in annotation.text for annotation in figure.layout.annotations)
        assert "xaxis2" not in figure.layout.to_plotly_json()
        assert figure.data[0].line.color is not None


def test_all_and_single_channel_views_restore_original_raw_traces():
    recording = _synthetic()
    four = make_emg_figure(recording, "all", 0.1, 0.25, "raw")
    single = make_emg_figure(recording, "1", 0.1, 0.25, "raw")
    assert len(four.data) == 2
    assert len(single.data) == 1
    assert len(single.data[0].x) == 500
    np.testing.assert_allclose(
        np.asarray(single.data[0].y, dtype=float),
        np.asarray(recording.samples[1][200:700], dtype=float),
    )


def test_exploration_has_view_modes_and_conditional_comparison_controls():
    from kinoryx.research_lab import build_layout, exploration_content

    def flatten(root):
        yield root
        children = getattr(root, "children", [])
        if children is None:
            return
        if not isinstance(children, (list, tuple)):
            children = [children]
        for child in children:
            yield from flatten(child)

    layout = exploration_content(_synthetic())
    nodes = {node.id: node for node in flatten(layout)
             if getattr(node, "id", None) is not None}
    assert [item["value"] for item in nodes["lab-view"].options] == [
        "all", "single", "compare",
    ]
    assert nodes["lab-view"].value == "all"
    assert nodes["lab-single-channel"].value == "0"
    assert nodes["lab-channel-select-wrap"].style["display"] == "none"
    assert nodes["lab-compare-controls"].style["display"] == "none"
    assert nodes["lab-panel-b"].style["display"] == "none"
    assert nodes["lab-add-b-target"].style["display"] == "none"
    assert nodes["lab-mode"].value == "side"
    assert "lab-current-title" in {
        node.id for node in flatten(build_layout())
        if getattr(node, "id", None) is not None
    }


def test_official_blue_stage_navigation_and_kinoryx_only_footers():
    from kinoryx.research_lab import build_layout, stage_navigation
    from kinoryx.landing import HOME_HTML

    for stage in ("exploration", "quality", "experimentation", "evaluation"):
        tabs = stage_navigation(stage)
        assert len(tabs) == 4
        assert sum("is-active" in tab.className for tab in tabs) == 1
        assert "is-active" in tabs[
            ["exploration", "quality", "experimentation", "evaluation"].index(stage)
        ].className

    lab = build_layout()
    footer = [child for child in lab.children if getattr(child, "_type", None) == "Footer"]
    assert len(footer) == 1
    assert footer[0].children == "KINORYX"
    assert footer[0].className == "kinoryx-bottom-bar"
    assert '<footer class="foot">KINORYX</footer>' in HOME_HTML

    app_file = Path(__file__).resolve().parents[1] / "apps/biomechanics_dashboard/app.py"
    spec = importlib.util.spec_from_file_location("kinoryx_footer_test_app", app_file)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    dashboard = module.create_app()
    footers = [child for child in dashboard.layout.children
               if getattr(child, "_type", None) == "Footer"]
    assert len(footers) == 1
    assert footers[0].children == "KINORYX"


def test_plot_fonts_have_minimum_10_pixels():
    from kinoryx.lab_workspace import build_workspace_figure

    recording = _synthetic()
    figures = (
        make_emg_figure(recording, "all", 0.1, 0.25, "raw"),
        build_workspace_figure(
            recording, {"left": ["0"], "right": ["1"]},
            mode="overlay", start_seconds=0.1, window_seconds=0.25,
        ),
    )
    for figure in figures:
        assert figure.layout.font.size >= 10
        assert figure.layout.hoverlabel.font.size >= 10
        for axis in figure.select_xaxes():
            assert axis.tickfont.size >= 10
        for axis in figure.select_yaxes():
            assert axis.tickfont.size >= 10
        for annotation in figure.layout.annotations:
            if annotation.font is not None and annotation.font.size is not None:
                assert annotation.font.size >= 10


def test_css_keeps_text_above_12_px_and_original_typography():
    import re
    root = Path(__file__).resolve().parents[1]
    css_files = [
        root / "apps/biomechanics_dashboard/assets/workspace.css",
        root / "apps/biomechanics_dashboard/assets/research-lab.css",
        root / "apps/biomechanics_dashboard/assets/lab-restructure.css",
    ]
    for path in css_files:
        content = path.read_text(encoding="utf-8")
        for declaration in re.findall(r"\\bfont(?:-size)?\\s*:\\s*[^;{}]+", content):
            for size in re.findall(r"(?<![\\w.])(\\d*\\.\\d+)rem\\b", declaration):
                assert float(size) >= 0.75, (path.name, declaration)
    theme = css_files[0].read_text(encoding="utf-8")
    lab_css = css_files[2].read_text(encoding="utf-8")
    assert "--heading-blue: #0847A6" in theme
    assert "background: var(--heading-blue)" in lab_css
    assert "border-radius: 19px 19px 0 0" in lab_css
    assert "font-family: var(--title-font)" in lab_css
