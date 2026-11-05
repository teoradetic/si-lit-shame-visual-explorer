# si-lit-shame-visual-explorer

A free, public web app for exploring the shame passages an LLM detected in 305 Slovene novels (1828–1940). The code doesn't depend on shame, so it works for other emotions and larger corpora.

**Live app:** https://shame-visual-explorer-slovenian-literature.streamlit.app/

## Setup and run

```bash
uv sync
uv run pre-commit install
uv run streamlit run app/streamlit_app.py
```

The interface is in English and Slovene; the excerpts stay in Slovene.

## Data

| Folder | Contents |
|---|---|
| `data/raw/` | The entry points from [shame_sl_lit](https://github.com/teoradetic/shame_sl_lit) (commit `e075df3`), never edited: `corpus_metadata.csv` and the annotated corpus `main_shame_annotations.json.zst`. |
| `data/tokens/` | Every token with lemma, part of speech, morphology and named entity, one file per novel. |
| `data/processed/` | What the app reads: parquet tables and `meta.json`. |
| `data/corpora/`, `data/models/` | Downloaded source corpora and CLASSLA models; not committed. |

```bash
uv run emotion-explorer all                     # rebuild data/processed
uv run emotion-explorer words                   # or one step
uv run emotion-explorer corpora                 # download KDSP, PriLit, ELTeC (1.6 GB)
uv run --group corpus emotion-explorer tokens   # write missing data/tokens files
```

| Step | Writes | Ticket |
|---|---|---|
| `paragraphs` | one row per paragraph: scores, tier flags, novel metadata | DATA-01 |
| `comparison` | low-score partners of the broad-tier paragraphs | DATA-03 |
| `excerpts` | excerpts with ±2 paragraphs of context, and their texts | DATA-02 |
| `overview` | per-novel counts and counts by position in the novel | AN-01, AN-02 |
| `words` | lemma counts per novel, set, case and narration or speech; pairs in a sentence; corpus counts, word forms | AN-03, AN-06, AN-14, DATA-06 |
| `themes` | NMF themes and the main theme of each paragraph | AN-10 |
| `style` | style features per paragraph (whole, narration, speech), pooled per novel and set | AN-08, AN-09 |
| `corpora` | the annotated [KDSP](http://hdl.handle.net/11356/1823), [PriLit](http://hdl.handle.net/11356/1319) and [ELTeC-slv](https://github.com/COST-ELTeC/ELTeC-slv) editions (262 novels) | DATA-04 |
| `tokens` | their annotation, and CLASSLA for the other 43 novels | DATA-04 |

`corpora` and `tokens` are not part of `all`; `tokens` needs the optional `corpus` group (CLASSLA, torch). The pipeline only counts; the app compares whichever novels the sidebar selects (`app/helpers/stats.py`). What is specific to shame is in `src/emotion_explorer/emotion.py`.

## Layout

- `src/emotion_explorer/`: `cli.py`, `prep/` (sources, paragraphs, comparison set, excerpts, tokens), `analysis/` (the counts behind each view).
- `app/`: `streamlit_app.py`, `views/` (pages), `helpers/`, `assets/`.
- `tests/`: unit tests, and a smoke test of every page and chart type in both languages and every comparison.
