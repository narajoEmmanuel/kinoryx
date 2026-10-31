"""Title-aware spacing for scientific Plotly subplot figures.

A chart should reserve actual vertical space for its title lines and axis labels.
Do not repeat lengthy axis labels on every panel: use one shared axis caption.
"""
from dataclasses import dataclass
from html import escape
import math
import textwrap


@dataclass(frozen=True)
class SubplotLayout:
    titles: tuple[str, ...]
    rows: int
    height: int
    vertical_spacing: float
    title_lines: int


def wrap_plot_title(title: str, max_chars: int) -> tuple[str, int]:
    """Escape arbitrary display labels and wrap them at word boundaries."""
    if max_chars < 5:
        raise ValueError("Title width must be at least 5 characters")
    text = str(title).replace("\r\n", "\n").replace("\r", "\n")
    lines: list[str] = []
    for paragraph in text.split("\n"):
        lines.extend(textwrap.wrap(
            paragraph,
            width=max_chars,
            break_long_words=True,
            break_on_hyphens=False,
            replace_whitespace=True,
            drop_whitespace=True,
        ) or [""])
    return "<br>".join(escape(line) for line in lines), len(lines)


def plan_subplot_layout(
    titles: list[str] | tuple[str, ...],
    *,
    cols: int,
    minimum_height: int = 0,
    preferred_panel_height: int = 260,
) -> SubplotLayout:
    """Produce scalable Plotly geometry from title content and panel count.

    Both the overall height and the gap between successive rows grow with the
    wrapped title line count. All labels are HTML-escaped before Plotly markup.
    """
    if cols < 1:
        raise ValueError("At least one subplot column is required")
    rows = max(1, math.ceil(len(titles) / cols))
    width = 46 if cols == 1 else 29
    wrapped = tuple(wrap_plot_title(title, width) for title in titles)
    max_lines = max((n for _, n in wrapped), default=1)
    # Room for a subplot title, bottom x tick labels and the next row's title.
    gap_px = 66 + 21 * max(0, max_lines - 1)
    top_px = 76 + 21 * max(0, max_lines - 1)
    bottom_px = 82
    plot_area = rows * preferred_panel_height + (rows - 1) * gap_px
    height = max(minimum_height, top_px + plot_area + bottom_px)
    spacing = gap_px / plot_area if rows > 1 else 0.0
    return SubplotLayout(
        titles=tuple(value for value, _ in wrapped),
        rows=rows,
        height=height,
        vertical_spacing=spacing,
        title_lines=max_lines,
    )
