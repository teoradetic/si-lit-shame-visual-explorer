"""DATA-02: excerpts, each tagged paragraph with its context.

An excerpt spans CONTEXT paragraphs before and after its focus paragraphs,
within one novel. Excerpts whose spans overlap are merged, so one excerpt can
have several focus paragraphs. Texts are stored once per paragraph in a
separate table, since excerpts of different sets share context.
"""

import pandas as pd

CONTEXT = 2


def merge_spans(
    focus_ids: list[int], n_paragraphs: int
) -> list[tuple[int, int, list[int]]]:
    """(start, end, focus ids) per merged span; `end` is inclusive."""
    spans: list[tuple[int, int, list[int]]] = []
    for pid in sorted(focus_ids):
        start, end = max(pid - CONTEXT, 0), min(pid + CONTEXT, n_paragraphs - 1)
        if spans and start <= spans[-1][1]:
            prev_start, _, prev_focus = spans[-1]
            spans[-1] = (prev_start, end, [*prev_focus, pid])
        else:
            spans.append((start, end, [pid]))
    return spans


def build_excerpts(
    paragraphs: pd.DataFrame, sets: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Excerpts for each named set of focus paragraphs (novel_id, para_id)."""
    # Paragraphs are sorted and para_id runs 0..n-1, so ids index the arrays.
    novels = {
        novel_id: {
            col: group[col].to_numpy()
            for col in ("n_chars", "score", "rel_position", "over_context")
        }
        for novel_id, group in paragraphs.groupby("novel_id", observed=True)
    }
    records = []
    for set_name, focus in sets.items():
        for novel_id, group in focus.groupby("novel_id", observed=True):
            novel = novels[novel_id]
            n = len(novel["n_chars"])
            for start, end, focus_ids in merge_spans(group["para_id"].tolist(), n):
                records.append(
                    {
                        "set": set_name,
                        "excerpt_id": f"{set_name}-{novel_id}-{start}",
                        "novel_id": novel_id,
                        "start": start,
                        "end": end,
                        "focus_ids": focus_ids,
                        "n_focus": len(focus_ids),
                        "rel_position": float(novel["rel_position"][focus_ids[0]]),
                        "max_score": float(novel["score"][focus_ids].max()),
                        "n_chars": int(novel["n_chars"][start : end + 1].sum()),
                        "over_context": bool(novel["over_context"][focus_ids].any()),
                    }
                )
    return pd.DataFrame.from_records(records).astype(
        {"set": "category", "start": "int32", "end": "int32", "n_focus": "int16"}
    )


def excerpt_texts(annotations: dict, excerpts: pd.DataFrame) -> pd.DataFrame:
    """The text of every paragraph inside some excerpt."""
    keys = {
        (row.novel_id, pid)
        for row in excerpts.itertuples()
        for pid in range(row.start, row.end + 1)
    }
    records = [
        (novel_id, pid, annotations[novel_id]["paragraphs"][str(pid)]["text"])
        for novel_id, pid in sorted(keys)
    ]
    return pd.DataFrame.from_records(
        records, columns=["novel_id", "para_id", "text"]
    ).astype({"para_id": "int32"})
