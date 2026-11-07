"""Words (lemmas) typical of the detected passages."""

import math

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from helpers import charts, compare, filters, notes, reader, stats, tables
from helpers.language import labels, num, t

CHART_TYPES = ("cloud", "map", "dots", "network")
# Verbs, the actions; "content" leaves out the function words.
WORD_CLASSES = {"content": None, "nouns": ("NOUN", "ADJ"), "verbs": ("VERB",)}
# A word belongs to a group when its frequency ratio there is at least this
# many times its ratio in every other group. Ratios, not z-scores: z grows
# with the amount of text, and groups differ greatly in size.
GROUP_FACTOR = 1.5
CLOUD_WIDTH, CLOUD_HEIGHT = 900, 420
# The map has a fixed size, so that its labels can be placed without overlap.
MAP_WIDTH, MAP_HEIGHT = 720, 520
N_FINDINGS = 5
# Function words listed in their explanation, the commonest first.
N_FUNCTION_LISTED = 40
CASES = ("Nom", "Gen", "Dat", "Acc", "Loc", "Ins")
# Two words are linked when they share at least this many sentences in
# the selected novels, as often as the pipeline's floor asks (`pair_min_pmi`).
MIN_TOGETHER = 3
N_NEIGHBOURS = 12
# Each word in the network keeps only its strongest links, or larger networks
# turn into a tangle.
MAX_LINKS = 3

f = filters.current()
st.title(t("words.title"))
st.write(t("words.intro"))
filters.stop_if_empty()
groups = compare.require()
shame_mode = compare.mode() == "shame"
split = compare.is_split()
findings_box = st.container()
st.caption(t("words.lemmas"))
if f.text != "all":
    st.info(t(f"paragraphs.note.{f.text}"), icon=":material/record_voice_over:")

c1, c2, c3 = st.columns([2, 2, 3], vertical_alignment="bottom")
chart_type = c1.selectbox(
    t("chart.type"),
    CHART_TYPES,
    format_func=lambda v: t(f"words.type.{v}"),
    key="words_type",
)
word_class = c2.selectbox(
    t("words.class"),
    [*WORD_CLASSES, "all"],
    format_func=lambda v: t(f"words.class.{v}"),
    key="words_class",
    help=t("words.class_help"),
)
n_words = c3.slider(
    t("words.n"),
    10,
    60,
    40 if chart_type == "cloud" else 20,
    step=5,
    key=f"words_n_{chart_type}",
)
text_split = f.text


def prepare(table: pd.DataFrame) -> pd.DataFrame:
    """Keep the chosen word class; `ratio` is how many times more frequent."""
    if table.empty:
        return table.assign(strength=[], ratio=[])
    if word_class == "content":
        table = table[~table["function_word"]]
    elif word_class != "all":
        table = table[table["pos"].isin(WORD_CLASSES[word_class])]
    return table.assign(strength=table["z"])


pool_ids = frozenset().union(*(g.novel_ids for g in groups))
pool = prepare(tables.group_words(f.tier, text_split, pool_ids))
by_group = (
    {
        g.label: prepare(tables.group_words(f.tier, text_split, g.novel_ids))
        for g in groups
    }
    if split
    else {}
)
shared = t("words.shared")
belong_domain = [g.label for g in groups] + ([shared] if split else [])
belong_range = [g.color for g in groups] + ([charts.ink()] if split else [])
belong_color = alt.Color(
    "belongs:N",
    scale=alt.Scale(domain=belong_domain, range=belong_range),
    legend=alt.Legend(orient="top", title=None),
)


def typical(table: pd.DataFrame, n: int, side: str = "emotion") -> pd.DataFrame:
    """The n words most typical of one side, with `strength` towards it."""
    if table.empty:
        return table
    if side == "comparison":
        table = table.assign(strength=-table["z"], ratio=1 / table["ratio"])
    return table[table["strength"] > 0].nlargest(n, "strength")


def ratios_by_group() -> pd.DataFrame:
    """Each word's frequency ratio (with shame against without) per group."""
    return pd.DataFrame(
        {label: table.set_index("word")["ratio"] for label, table in by_group.items()}
    )


def belongs(words: pd.Series, ratios: pd.DataFrame) -> pd.Series:
    """The group a word is clearly more tied to shame in, or `shared`."""
    rows = ratios.reindex(words).fillna(1.0)

    def pick(row: pd.Series) -> str:
        best = row.idxmax()
        others = row.drop(best)
        return best if (row[best] >= GROUP_FACTOR * others).all() else shared

    return pd.Series([pick(r) for _, r in rows.iterrows()], index=words.index)


def shown_words() -> pd.DataFrame:
    """The words of the current chart, with `belongs` for the colour."""
    if shame_mode:
        half = max(n_words // 2, 5)
        return pd.concat(
            [
                typical(pool, half).assign(belongs=groups[0].label, side="emotion"),
                typical(pool, half, "comparison").assign(
                    belongs=groups[1].label, side="comparison"
                ),
            ],
            ignore_index=True,
        )
    if not split:
        return typical(pool, n_words).assign(belongs=groups[0].label, side="emotion")
    ratios = ratios_by_group()
    strongest = (
        pd.concat(by_group.values())
        .loc[lambda d: d["strength"] > 0]
        .groupby("word")["strength"]
        .max()
        .nlargest(n_words)
    )
    words = pool.set_index("word").reindex(strongest.index).dropna(subset=["z"])
    words = words.reset_index().assign(strength=lambda d: d["word"].map(strongest))
    return words.assign(belongs=belongs(words["word"], ratios), side="emotion")


tooltip = [
    alt.Tooltip("word:N", title=t("words.col.word")),
    alt.Tooltip("belongs:N", title=t("field.group")),
    alt.Tooltip("ratio:Q", title=t("words.col.ratio"), format=".2f"),
    alt.Tooltip(
        "per_10k_emotion:Q", title=t("words.col.per_10k_emotion"), format=".1f"
    ),
    alt.Tooltip(
        "per_10k_comparison:Q", title=t("words.col.per_10k_comparison"), format=".1f"
    ),
    alt.Tooltip("n_novels:Q", title=t("words.col.n_novels")),
]
pick = alt.selection_point(name="word", fields=["word", "side"], on="click")


def cloud_layout(df: pd.DataFrame) -> pd.DataFrame:
    """Place words on an outward spiral, largest first, without overlaps."""
    low, high = df["strength"].min(), df["strength"].max()
    span = high - low or 1
    placed: list[tuple[float, float, float, float]] = []
    rows = []
    for row in df.sort_values("strength", ascending=False).itertuples():
        size = 14 + 32 * math.sqrt((row.strength - low) / span)
        w, h = len(row.word) * size * 0.58 + 8, size * 1.05
        for i in range(6000):
            theta = 0.18 * i
            radius = 2.5 * theta
            x, y = radius * math.cos(theta) * 1.8, radius * math.sin(theta)
            box = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
            inside = (
                abs(x) + w / 2 < CLOUD_WIDTH / 2 and abs(y) + h / 2 < CLOUD_HEIGHT / 2
            )
            if inside and all(
                box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]
                for b in placed
            ):
                placed.append(box)
                rows.append((row.word, row.side, x, y, size))
                break
    layout = pd.DataFrame(rows, columns=["word", "side", "x", "y", "size"])
    return layout.merge(df, on=["word", "side"])


def diagonal(scale: alt.Scale, low: float, high: float) -> alt.Chart:
    return (
        alt.Chart(pd.DataFrame({"a": [low, high]}))
        .mark_line(strokeWidth=1, opacity=0.5, color=charts.ink())
        .encode(x=alt.X("a:Q", scale=scale), y=alt.Y("a:Q", scale=scale))
    )


def network_words() -> pd.DataFrame:
    """The words of the network: those typical of the passages with shame,
    whose sentences the pairs count."""
    if shame_mode:
        return typical(pool, n_words).assign(belongs=groups[0].label, side="emotion")
    return words


def network_edges() -> pd.DataFrame:
    """Links among the network's words; each keeps its strongest."""
    shown = network_words()["word"]
    pairs = tables.group_pairs(f.tier, pool_ids)
    edges = pairs[
        pairs["a"].isin(shown)
        & pairs["b"].isin(shown)
        & (pairs["n"] >= MIN_TOGETHER)
        & (pairs["pmi"] >= tables.meta()["words"]["pair_min_pmi"])
    ]
    ends = pd.concat([edges["a"], edges["b"]])
    rank = (
        edges["pmi"]
        .reindex(ends.index)
        .groupby(ends.to_numpy())
        .rank(ascending=False, method="first")
    )
    return edges.loc[rank[rank <= MAX_LINKS].index.unique()]


words = shown_words()
chosen = None
read_key = f"words.read.{chart_type}"
if words.empty:
    st.info(t("reader.none"))
elif chart_type == "cloud":
    cloud = cloud_layout(words)
    chart = (
        alt.Chart(cloud)
        .mark_text(fontWeight=600, baseline="middle", align="center")
        .encode(
            x=alt.X(
                "x:Q",
                scale=alt.Scale(domain=[-CLOUD_WIDTH / 2, CLOUD_WIDTH / 2]),
                axis=None,
            ),
            y=alt.Y(
                "y:Q",
                scale=alt.Scale(domain=[-CLOUD_HEIGHT / 2, CLOUD_HEIGHT / 2]),
                axis=None,
            ),
            text="word:N",
            size=alt.Size("size:Q", scale=None, legend=None),
            color=belong_color,
            opacity=alt.condition(pick, alt.value(1), alt.value(0.35)),
            tooltip=tooltip,
        )
        .add_params(pick)
        .properties(width=CLOUD_WIDTH, height=CLOUD_HEIGHT)
    )
    event = charts.show_chart(chart, key="words_cloud", fit=False)
    chosen = (charts.selected(event, "word", "word") or [None])[0]
    read_key = "words.read.cloud_" + (
        "shame" if shame_mode else "split" if split else "none"
    )
elif chart_type == "map" and not shame_mode and len(by_group) != 2:
    st.info(t("words.map_needs_two"))
    read_key = None
elif chart_type == "map":
    if shame_mode:
        table = words.rename(
            columns={"per_10k_emotion": "a", "per_10k_comparison": "b"}
        )
        x_title, y_title = t("words.map.with"), t("words.map.without")
    else:
        first, second = list(by_group)
        ratios = ratios_by_group()
        leaders = set().union(
            *(set(typical(table, n_words)["word"]) for table in by_group.values())
        )
        table = (
            ratios.dropna()
            .loc[lambda d: d.index.isin(leaders)]
            .rename(columns={first: "a", second: "b"})
            .rename_axis("word")
            .reset_index()
        )
        table = table.assign(
            belongs=belongs(table["word"], ratios),
            side="emotion",
        )
        x_title = t("words.map.ratio_in", group=first)
        y_title = t("words.map.ratio_in", group=second)
        read_key = "words.read.map_split"
    # A log scale has no place for words never seen on one side.
    table = table[(table["a"] > 0) & (table["b"] > 0)]
    values = table[["a", "b"]].to_numpy()
    floor, limit = float(values.min()) / 1.15, float(values.max()) * 1.15
    scale = alt.Scale(type="log", domain=[floor, limit])
    x = alt.X("a:Q", title=x_title, scale=scale)
    y = alt.Y("b:Q", title=y_title, scale=scale)
    map_tooltip = [
        alt.Tooltip("word:N", title=t("words.col.word")),
        alt.Tooltip("a:Q", title=x_title, format=".2f"),
        alt.Tooltip("b:Q", title=y_title, format=".2f"),
    ]
    dots = (
        alt.Chart(table)
        .mark_point(filled=True, size=60, strokeWidth=0)
        .encode(
            x=x,
            y=y,
            color=belong_color,
            tooltip=map_tooltip,
            opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
        )
        .add_params(pick)
    )
    # The words furthest from the diagonal get their labels first.
    distinct = np.abs(np.log(table["a"] / table["b"]))
    placed = charts.place_labels(
        table.loc[distinct.sort_values(ascending=False).index],
        (floor, limit),
        MAP_WIDTH,
        MAP_HEIGHT,
    )
    label_x = alt.X("label_a:Q", title=x_title, scale=scale)
    label_y = alt.Y("label_b:Q", title=y_title, scale=scale)
    leaders = (
        alt.Chart(placed[placed["leader"]])
        .mark_rule(strokeWidth=0.8, opacity=0.6)
        .encode(x=x, y=y, x2="label_a:Q", y2="label_b:Q", color=belong_color)
    )
    labels = [
        alt.Chart(placed[placed["labelled"] & (placed["align"] == align)])
        .mark_text(align=align, baseline="middle", fontSize=12)
        .encode(
            x=label_x,
            y=label_y,
            text="word:N",
            color=belong_color,
            tooltip=map_tooltip,
        )
        for align in ("left", "right", "center")
    ]
    chart = alt.layer(diagonal(scale, floor, limit), leaders, dots, *labels).properties(
        width=MAP_WIDTH, height=MAP_HEIGHT
    )
    event = charts.show_chart(chart, key="words_map", fit=False)
    hidden = int((~placed["labelled"]).sum())
    if hidden:
        st.caption(t("words.hidden_labels", n=hidden))
    chosen = (charts.selected(event, "word", "word") or [None])[0]
    if shame_mode:
        read_key = "words.read.map_shame"
elif chart_type == "network" and network_edges().empty:
    st.info(t("words.network.none", n=MIN_TOGETHER))
    read_key = None
elif chart_type == "network":
    nodes, edges = network_words(), network_edges()
    # Words without a link are listed, not drawn: they would push the rest
    # into the middle.
    linked = nodes["word"].isin(edges["a"]) | nodes["word"].isin(edges["b"])
    loners = nodes.loc[~linked, "word"].tolist()
    nodes = nodes[linked]
    pos = charts.spring_layout(nodes["word"].tolist(), edges)
    nodes = nodes.assign(x=pos[:, 0], y=pos[:, 1])
    at = nodes.set_index("word")
    edges = edges.assign(
        x=edges["a"].map(at["x"]),
        y=edges["a"].map(at["y"]),
        x2=edges["b"].map(at["x"]),
        y2=edges["b"].map(at["y"]),
        pair=edges["a"] + " – " + edges["b"],
        times=2 ** edges["pmi"],
    )
    # One colour without groups: every word comes from passages with shame.
    node_color = belong_color if split else alt.value(charts.set_color("emotion"))
    # Room on the right for the labels.
    x = alt.X("x:Q", scale=alt.Scale(domain=[-1.1, 1.4]), axis=None)
    y = alt.Y("y:Q", scale=alt.Scale(domain=[-1.1, 1.1]), axis=None)
    lines = (
        # In the shame colour, not grey: the links come from passages with
        # shame, and grey stands for those without.
        alt.Chart(edges)
        .mark_rule(color=charts.set_color("emotion"), opacity=0.35)
        .encode(
            x=x,
            y=y,
            x2="x2:Q",
            y2="y2:Q",
            strokeWidth=alt.StrokeWidth(
                "times:Q", scale=alt.Scale(range=[0.5, 4]), legend=None
            ),
            tooltip=[
                alt.Tooltip("pair:N", title=t("words.pairs.pair")),
                alt.Tooltip("times:Q", title=t("words.pairs.times"), format=".1f"),
                alt.Tooltip("n:Q", title=t("words.pairs.n")),
            ],
        )
    )
    dots = (
        alt.Chart(nodes)
        .mark_point(filled=True, size=90, strokeWidth=0)
        .encode(
            x=x,
            y=y,
            color=node_color,
            tooltip=tooltip,
            opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
        )
        .add_params(pick)
    )
    labels = (
        alt.Chart(nodes)
        .mark_text(align="left", dx=7, fontSize=12)
        .encode(x=x, y=y, text="word:N", color=node_color)
    )
    chart = alt.layer(lines, dots, labels).properties(
        width=MAP_WIDTH, height=MAP_HEIGHT
    )
    event = charts.show_chart(chart, key="words_network", fit=False)
    if loners:
        st.caption(t("words.network.loners", words=", ".join(loners)))
    chosen = (charts.selected(event, "word", "word") or [None])[0]
    read_key = "words.read.network"
else:  # dots
    if shame_mode:
        # One axis for both sides: below 1 is typical of passages without shame.
        words = words.assign(
            ratio=np.where(
                words["side"] == "comparison", 1 / words["ratio"], words["ratio"]
            )
        )
        x_title = t("words.dots.both")
        read_key = "words.read.dots_shame"
    else:
        x_title = t("words.col.ratio")
    # Rows in the order of the axis: the largest ratio on top.
    order = words.sort_values("ratio", ascending=False)["word"].tolist()
    y = alt.Y(
        "word:N",
        sort=order,
        title=None,
        axis=alt.Axis(labelFontSize=13, labelOverlap=False, labelLimit=200),
    )
    x = alt.X("ratio:Q", title=x_title, scale=alt.Scale(type="log", nice=False))
    # A dashed line at 1×, as often with shame as without, and a stem from
    # it to each dot in the dot's colour (grey stands for "without shame").
    one = (
        alt.Chart(pd.DataFrame({"one": [1.0]}))
        .mark_rule(strokeDash=[4, 3], color=charts.ink(), opacity=0.6)
        .encode(x=alt.X("one:Q", scale=alt.Scale(type="log")))
    )
    rule = (
        # A field, not a datum, for the baseline: Vega-Lite cannot layer a
        # typeless datum with the points' quantitative x.
        alt.Chart(words.assign(baseline=1.0))
        .mark_rule(strokeWidth=1.5, opacity=0.5)
        .encode(y=y, x="baseline:Q", x2="ratio:Q", color=belong_color)
    )
    main = (
        alt.Chart(words)
        .mark_point(filled=True, size=100, strokeWidth=0)
        .encode(
            y=y,
            x=x,
            color=belong_color,
            tooltip=tooltip,
            opacity=alt.condition(pick, alt.value(1), alt.value(0.4)),
        )
        .add_params(pick)
    )
    layers = [one, rule, main]
    if split:
        # Each group's own ratio, as smaller dots on the word's row.
        per_group = pd.concat(
            [
                table[table["word"].isin(order)].assign(belongs=label)
                for label, table in by_group.items()
            ]
        )
        # The dark dot: all compared novels together; a line spans the groups.
        everyone = t("words.all_novels")
        dot_color = alt.Color(
            "belongs:N",
            scale=alt.Scale(
                domain=[g.label for g in groups] + [everyone],
                range=[g.color for g in groups] + [charts.ink()],
            ),
            legend=alt.Legend(orient="top", title=None),
        )
        main = main.transform_calculate(belongs=f"{everyone!r}").encode(color=dot_color)
        spread = (
            alt.Chart(per_group)
            .mark_rule(strokeWidth=1, opacity=0.5, color=charts.ink())
            .encode(y=y, x="min(ratio):Q", x2="max(ratio):Q")
        )
        layers = [
            one,
            spread,
            alt.Chart(per_group)
            .mark_point(filled=True, size=55, strokeWidth=0, opacity=0.9)
            .encode(
                y=y,
                x="ratio:Q",
                color=dot_color,
                tooltip=[
                    alt.Tooltip("word:N", title=t("words.col.word")),
                    alt.Tooltip("belongs:N", title=t("field.group")),
                    alt.Tooltip("ratio:Q", title=t("words.col.ratio"), format=".2f"),
                ],
            ),
            main,
        ]
        read_key = "words.read.dots_split"
    chart = alt.layer(*layers).properties(height=22 * len(order) + 80)
    event = charts.show_chart(chart, key="words_dots")
    chosen = (charts.selected(event, "word", "word") or [None])[0]

if read_key:
    st.caption(t(read_key, factor=GROUP_FACTOR))
min_novels, min_authors = stats.spread_rule(
    len(pool_ids),
    tables.novels().set_index("novel_id").loc[list(pool_ids), "author"].nunique(),
)
notes.methodology(
    "words",
    factor=GROUP_FACTOR,
    novels=min_novels,
    authors=min_authors,
    min_count=stats.MIN_COUNT,
    pair_sentences=tables.meta()["words"]["pair_min_sentences"],
    pair_novels=tables.meta()["words"]["pair_min_novels"],
    together=MIN_TOGETHER,
    links=MAX_LINKS,
    function_words=", ".join(
        tables.word_prior()
        .query("function_word")["n_corpus"]
        .nlargest(N_FUNCTION_LISTED)
        .index
    ),
)
with st.expander(t("words.counts")):
    cols = [
        "word",
        "belongs",
        "ratio",
        "per_10k_emotion",
        "per_10k_comparison",
        "n_novels",
    ]
    if not words.empty:
        st.dataframe(
            words[cols].round(2).rename(columns={c: t(f"words.col.{c}") for c in cols}),
            hide_index=True,
        )


def listing(table: pd.DataFrame) -> str:
    return ", ".join(
        f"*{row.word}* ({num(row.ratio)}×)"
        for row in table.head(N_FINDINGS).itertuples()
    )


def finding_lines() -> list[str]:
    lines = []
    if not split:
        top = typical(pool, N_FINDINGS)
        if not top.empty:
            lines.append(t("words.find.shame", words=listing(top)))
        if shame_mode:
            other = typical(pool, N_FINDINGS, "comparison")
            if not other.empty:
                lines.append(t("words.find.without", words=listing(other)))
        return lines
    ratios = ratios_by_group()
    for label, table in by_group.items():
        top = typical(table, 40)
        own = top[belongs(top["word"], ratios) == label]
        if not own.empty:
            lines.append(t("words.find.group", group=label, words=listing(own)))
    candidates = typical(pool, 40)
    common = candidates[belongs(candidates["word"], ratios) == shared]
    if not common.empty:
        lines.append(t("words.find.common", words=listing(common)))
    return lines


with findings_box:
    notes.findings(finding_lines())


def neighbour_chart(word: str) -> None:
    """The words that come with this one in a sentence, per group."""
    parts = []
    for g in groups if split else groups[:1]:
        pairs = tables.group_pairs(f.tier, g.novel_ids)
        mine = pairs[
            ((pairs["a"] == word) | (pairs["b"] == word))
            & (pairs["n"] >= MIN_TOGETHER)
            & (pairs["pmi"] > 0)
        ]
        parts.append(
            pd.DataFrame(
                {
                    "word": mine["a"].where(mine["b"] == word, mine["b"]),
                    "times": 2 ** mine["pmi"],
                    "n": mine["n"],
                    "group": g.label,
                }
            ).nlargest(N_NEIGHBOURS, "times")
        )
    df = pd.concat(parts)
    st.subheader(t("words.pairs.title", word=word))
    if df.empty:
        st.caption(t("words.pairs.none", n=MIN_TOGETHER))
        return
    order = df.groupby("word")["times"].max().sort_values(ascending=False).index
    chart = (
        alt.Chart(df)
        .mark_point(filled=True, size=90, strokeWidth=0)
        .encode(
            y=alt.Y("word:N", sort=order.tolist(), title=None),
            x=alt.X(
                "times:Q",
                title=t("words.pairs.times"),
                scale=alt.Scale(type="log", nice=False),
            ),
            color=compare.color(legend=split),
            tooltip=[
                alt.Tooltip("word:N", title=t("words.col.word")),
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("times:Q", title=t("words.pairs.times"), format=".1f"),
                alt.Tooltip("n:Q", title=t("words.pairs.n")),
            ],
        )
        .properties(height=22 * len(order) + 60)
    )
    charts.show_chart(chart, key="words_pairs", select=False)
    st.caption(t("words.pairs.read", n=MIN_TOGETHER))


def case_chart(word: str) -> None:
    """The word's share in each case: per group, or with against without shame."""
    sides = groups
    if not split:
        sides = [
            compare.Group(s, t(f"set.{s}"), charts.set_color(s), pool_ids, s)
            for s in stats.SIDES
        ]
    cases = tables.word_cases(f.tier, text_split)
    cases = cases[(cases["word"] == word) & cases["case"].notna()]
    df = pd.concat(
        cases[cases["novel_id"].isin(g.novel_ids) & (cases["side"] == g.set_name)]
        .groupby("case", observed=True)["n"]
        .sum()
        .reset_index()
        .assign(group=g.label)
        for g in sides
    )
    if df.empty:  # no case, e.g. a verb
        return
    totals = (
        df.groupby("group")["n"].sum().reindex([g.label for g in sides], fill_value=0)
    )
    legend = {
        g: t("words.cases.legend", group=g, n=num(n, 0)) for g, n in totals.items()
    }
    names = labels("case", CASES)
    df = df.assign(
        share=df["n"] / df["group"].map(totals),
        group=df["group"].map(legend),
        case=df["case"].map(names),
    )
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y("case:N", scale=alt.Scale(domain=list(names.values())), title=None),
            yOffset=alt.YOffset("group:N", sort=list(legend.values())),
            x=alt.X("share:Q", title=t("words.cases.share"), axis=alt.Axis(format="%")),
            color=alt.Color(
                "group:N",
                scale=alt.Scale(
                    domain=list(legend.values()), range=[g.color for g in sides]
                ),
                legend=alt.Legend(title=None),
            ),
            tooltip=[
                alt.Tooltip("group:N", title=t("field.group")),
                alt.Tooltip("case:N", title=t("words.cases.case")),
                alt.Tooltip("share:Q", title=t("words.cases.share"), format=".0%"),
                alt.Tooltip("n:Q", title=t("words.cases.n")),
            ],
        )
        .properties(height=len(CASES) * (12 * len(sides) + 8))
    )
    st.subheader(t("words.cases.title", word=word))
    charts.show_chart(chart, key="words_cases", select=False)
    st.caption(t("words.cases.read"))


if chosen:
    neighbour_chart(chosen)
    case_chart(chosen)
    side = "emotion"
    if shame_mode and chosen in set(words.loc[words["side"] == "comparison", "word"]):
        side = "comparison"
    set_name = f.tier if side == "emotion" else "comparison"
    picked, forms = tables.excerpts_with(chosen, set_name, pool_ids)
    reader.show_excerpts(
        picked,
        key="words_reader",
        title=t("words.selected", word=chosen),
        highlight_words=forms,
    )
else:
    st.info(t("reader.empty"))
