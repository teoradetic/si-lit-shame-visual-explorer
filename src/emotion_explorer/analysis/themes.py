"""Themes (NMF topics) shared by the passages with and without the
emotion, and the main theme of each paragraph."""

import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfTransformer

N_THEMES = 20
N_TOP_WORDS = 10
# Nouns and adjectives carry the themes. A lemma must occur in at least
# MIN_PARAGRAPHS paragraphs and at most MAX_SHARE of them.
THEME_POS = ("NOUN", "ADJ")
MIN_PARAGRAPHS = 10
MAX_SHARE = 0.3


def fit_themes(words: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Themes of the paragraphs in `words` (novel_id, para_id, word).

    Returns the top words of each theme (theme, rank, word, weight) and the
    main theme of each paragraph (novel_id, para_id, theme, weight: its share
    of the paragraph's theme weights).
    """
    counts = words.astype({"word": str}).groupby(["novel_id", "para_id", "word"]).size()
    n_paragraphs = counts.droplevel("word").index.nunique()
    spread = counts.groupby(level="word").size()
    usable = spread[(spread >= MIN_PARAGRAPHS) & (spread <= MAX_SHARE * n_paragraphs)]
    counts = counts[counts.index.get_level_values("word").isin(usable.index)]
    doc, docs = pd.factorize(counts.droplevel("word").index)
    term, terms = pd.factorize(counts.index.get_level_values("word"))
    matrix = sparse.csr_matrix((counts.to_numpy(float), (doc, term)))
    model = NMF(N_THEMES, init="nndsvda", random_state=0, max_iter=500)
    weights = model.fit_transform(TfidfTransformer().fit_transform(matrix))
    # A theme's words ranked by weight times the share of the word's weight
    # that falls on this theme: words common to many themes (*sin, hči*) give
    # way to those that set the theme apart.
    weight = model.components_
    distinct = weight * weight / weight.sum(axis=0).clip(min=1e-12)
    top = np.argsort(-distinct, axis=1)[:, :N_TOP_WORDS]
    themes = pd.DataFrame(
        [
            (theme, rank, terms[j], weight[theme, j])
            for theme, row in enumerate(top)
            for rank, j in enumerate(row)
        ],
        columns=["theme", "rank", "word", "weight"],
    )
    total = weights.sum(axis=1)
    has = total > 0
    main = (
        docs[has]
        .to_frame(index=False, name=["novel_id", "para_id"])
        .assign(
            theme=weights[has].argmax(axis=1),
            weight=weights[has].max(axis=1) / total[has],
        )
    )
    # Rounded, so that a rebuild writes the same bytes.
    return themes.round({"weight": 4}), main.round({"weight": 4})
