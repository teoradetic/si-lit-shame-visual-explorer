"""APP-02: the excerpt reader that every view opens its passages in.

The focus paragraph is highlighted, its context is grey, and long paragraphs
are shortened for display. Whole novels are never shown.
"""

import html
import re

import numpy as np
import pandas as pd
import streamlit as st

import tables
from language import label, num, t

PAGE_SIZE = 5
FOCUS_CHARS = 2_500
CONTEXT_CHARS = 600

CSS = """
<style>
.excerpt { font-family: Literata, Georgia, serif; font-size: 1.02rem;
  line-height: 1.6; }
.excerpt p { margin: 0 0 0.6rem 0; }
.excerpt .ctx { opacity: 0.55; font-size: 0.95rem; }
.excerpt .focus { padding: 0.35rem 0.7rem; border-left: 3px solid #8a4f7d;
  background: rgba(138, 79, 125, 0.10); border-radius: 0 4px 4px 0; }
.excerpt mark { background: rgba(237, 161, 0, 0.35); color: inherit;
  padding: 0 0.1rem; border-radius: 2px; }
.excerpt-meta { font-size: 0.9rem; margin-bottom: 0.15rem; }
.excerpt-where { font-size: 0.85rem; opacity: 0.8; margin-bottom: 0.5rem;
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.posbar { position: relative; display: inline-block; flex: none; width: 110px;
  height: 3px; border-radius: 2px; background: rgba(128, 128, 128, 0.45); }
.posdot { position: absolute; top: -4px; width: 11px; height: 11px;
  border-radius: 50%; background: #8a4f7d; transform: translateX(-50%); }
.score { padding: 0.05rem 0.45rem; border-radius: 999px;
  border: 1px solid rgba(138, 79, 125, 0.45); }
.reader-legend { font-size: 0.9rem; display: flex; gap: 1.2rem; flex-wrap: wrap;
  align-items: center; margin: 0.2rem 0 0.6rem 0; }
.swatch { display: inline-block; width: 0.9rem; height: 0.9rem;
  vertical-align: -0.12rem; margin-right: 0.35rem; border-radius: 2px; }
.swatch.focus { border-left: 3px solid #8a4f7d; background: rgba(138, 79, 125, 0.18); }
.swatch.ctx { background: currentColor; opacity: 0.25; }
</style>
"""


def inject_css() -> None:
    st.html(CSS)


def _shorten(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    cut = text.rfind(" ", 0, limit)
    return text[: cut if cut > 0 else limit] + " …"


def _render(text: str, highlight: re.Pattern | None) -> str:
    escaped = html.escape(text)
    if highlight is not None:
        escaped = highlight.sub(lambda m: f"<mark>{m.group()}</mark>", escaped)
    return escaped


def _position_bar(share: float) -> str:
    """A thin line for the whole novel with a dot where the passage is.

    Plain spans: st.html strips inline SVG.
    """
    return (
        '<span class="posbar" aria-hidden="true">'
        f'<span class="posdot" style="left:{share * 100:.1f}%"></span></span>'
    )


def legend(set_name: str) -> None:
    """What the highlighted and the grey paragraphs are."""
    focus = t(
        "reader.legend.comparison"
        if set_name == "comparison"
        else "reader.legend.focus"
    )
    context = t("reader.legend.context")
    st.html(
        '<div class="reader-legend">'
        f'<span><span class="swatch focus"></span>{html.escape(focus)}</span>'
        f'<span><span class="swatch ctx"></span>{html.escape(context)}</span>'
        "</div>"
    )


def _excerpt(row, highlight: re.Pattern | None) -> None:
    texts = tables.texts()
    focus = set(row.focus_ids)
    meta_line = (
        f"<b>{html.escape(row.author)}</b>: <i>{html.escape(row.title)}</i> "
        f"({row.year}) · {html.escape(label('period', row.period))}"
    )
    where = t(
        "reader.position",
        n=num(row.focus_ids[0] + 1, 0),
        total=num(row.n_paragraphs, 0),
    )
    score = t("reader.score", score=round(row.max_score * 100))
    where_line = (
        f"{_position_bar(row.rel_position)}<span>{html.escape(where)}</span>"
        f'<span class="score" title="{html.escape(t("reader.score_help"))}">'
        f"{html.escape(score)}</span>"
    )
    parts = []
    long_focus = []
    for pid in range(row.start, row.end + 1):
        text = texts.loc[(row.novel_id, pid)]
        if pid in focus:
            shown = _shorten(text, FOCUS_CHARS)
            if shown != text:
                long_focus.append(text)
            parts.append(f'<p class="focus">{_render(shown, highlight)}</p>')
        else:
            shown = _shorten(text, CONTEXT_CHARS)
            parts.append(f'<p class="ctx">{_render(shown, highlight)}</p>')
    with st.container(border=True):
        st.html(
            f'<div class="excerpt-meta">{meta_line}</div>'
            f'<div class="excerpt-where">{where_line}</div>'
            f'<div class="excerpt" lang="sl">{"".join(parts)}</div>'
        )
        if row.over_context:
            st.caption(t("reader.over_context"))
        for text in long_focus:
            st.caption(t("reader.truncated", n=num(len(text), 0)))
            with st.expander(t("reader.full")):
                st.html(
                    f'<div class="excerpt" lang="sl"><p>{_render(text, highlight)}'
                    "</p></div>"
                )


def show_excerpts(
    excerpts: pd.DataFrame,
    key: str,
    title: str | None = None,
    highlight_word: str | None = None,
    default_sort: str = "score",
) -> None:
    """A sortable, paged list of excerpts (rows of the excerpts table)."""
    st.subheader(title or t("reader.header"))
    if excerpts.empty:
        st.info(t("reader.none"))
        return
    legend(str(excerpts["set"].iloc[0]))
    sorts = ["score", "position", "random"]
    left, right = st.columns([3, 1])
    sort = left.segmented_control(
        t("reader.sort"),
        sorts,
        default=default_sort,
        required=True,
        format_func=lambda v: t(
            "reader.sort.rank"
            if v == "score" and "rank" in excerpts
            else f"reader.sort.{v}"
        ),
        key=f"{key}_sort",
    )
    if sort == "score":
        # A view may rank by its own measure instead of the score.
        rank = "rank" if "rank" in excerpts else "max_score"
        ordered = excerpts.sort_values([rank, "excerpt_id"], ascending=[False, True])
    elif sort == "position":
        ordered = excerpts.sort_values(["year", "novel_id", "start"])
    else:
        # Seeded by the selection, so paging through a random order is stable.
        rng = np.random.default_rng(len(excerpts))
        ordered = excerpts.iloc[rng.permutation(len(excerpts))]

    n_pages = max(1, -(-len(ordered) // PAGE_SIZE))
    page = right.number_input(
        t("reader.page"),
        1,
        n_pages,
        1,
        key=f"{key}_page",
        help=t("reader.of", n=n_pages),
    )
    st.caption(
        t("reader.count", n=num(len(ordered), 0))
        + f" · {t('reader.page')} {page} {t('reader.of', n=n_pages)}"
    )
    highlight = None
    if highlight_word:
        highlight = re.compile(
            rf"(?<!\w){re.escape(html.escape(highlight_word))}(?!\w)", re.IGNORECASE
        )
    for row in ordered.iloc[(page - 1) * PAGE_SIZE : page * PAGE_SIZE].itertuples():
        _excerpt(row, highlight)
