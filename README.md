# si-lit-shame-visual-explorer

A free, public web app for exploring the shame passages an LLM detected in 305 Slovene novels (1828–1940). The code doesn't depend on shame, so the same pipeline can be used for other emotions and larger corpora.

**Live app:** https://shame-visual-explorer-slovenian-literature.streamlit.app/

## Setup

```bash
uv sync                  # Python 3.13 and the default dependency groups
uv run pre-commit install
```

## Run the app

```bash
uv run streamlit run app/streamlit_app.py
```

The interface is in English and Slovene (switch at the top); the excerpts stay in Slovene.

## Data

All numbers are derived in this repo by Python CLI commands.

| Folder | Contents |
|---|---|
| `data/raw/` | The two entry points, taken from [shame_sl_lit](https://github.com/teoradetic/shame_sl_lit) at commit `e075df3` and never edited: `corpus_metadata.csv` and the annotated corpus `main_shame_annotations.json.zst` (zstd-compressed JSON). |
| `data/processed/` | Compact outputs (parquet, and `meta.json` with definitions and counts) that the app reads. |
| `data/tokens/` | Every token of every novel with its lemma, part of speech, morphology and named entity, one parquet file per novel. Committed, but not read by the app. |
| `data/corpora/`, `data/models/` | The downloaded source corpora and CLASSLA models. Not committed. |

Rebuild everything, or one step:

```bash
uv run emotion-explorer all
uv run emotion-explorer words
```

| Step | Writes | Ticket |
|---|---|---|
| `paragraphs` | `paragraphs.parquet`: one row per paragraph with scores, tier flags and novel metadata | DATA-01 |
| `comparison` | `comparison.parquet`: low-score partners of the broad-tier paragraphs | DATA-03 |
| `excerpts` | `excerpts.parquet`, `texts.parquet`: excerpts with ±2 paragraphs of context | DATA-02 |
| `overview` | `novels.parquet`, `position_bins.parquet` | AN-01, AN-02 |
| `words` | `word_counts.parquet`, `word_prior.parquet`: word counts per novel and set, corpus counts (preliminary) | AN-03 |
| `style` | `style_paragraphs.parquet`, `style_novels.parquet`: style features per paragraph, pooled per novel and set | AN-08 |

Lemmas and tags are a separate build, because they need downloads and a heavy optional dependency group (`corpus`: CLASSLA and torch). `all` doesn't run them.

```bash
uv run emotion-explorer corpora                 # download KDSP, PriLit and ELTeC (1.6 GB)
uv run --group corpus emotion-explorer tokens   # write the missing files in data/tokens
```

| Step | Writes | Ticket |
|---|---|---|
| `corpora` | `data/corpora/`: the annotated editions of [KDSP](http://hdl.handle.net/11356/1823), [PriLit](http://hdl.handle.net/11356/1319) and [ELTeC-slv](https://github.com/COST-ELTeC/ELTeC-slv) (262 novels) | DATA-04 |
| `tokens` | `data/tokens/<novel_id>.parquet`: the corpus's own annotation for those 262 novels, CLASSLA for the other 43 (Wikisource and Wikivir), whose text comes from the annotated corpus. The models are set in `src/emotion_explorer/tokens.py` | DATA-04 |

The pipeline only counts. The app compares whichever novels the sidebar selects and splits (`app/stats.py`: weighted log-odds for words, a permutation test for style), so every filter and comparison applies to every view.

The emotion-specific parts (raw field names, tiers, the low-score rule) are in `src/emotion_explorer/emotion.py`.

## Layout

- `src/emotion_explorer/`: the library and the data CLI.
- `app/`: the Streamlit app (`streamlit_app.py` is the entry point, `views/` the pages, `content/` the method texts).
- `tests/`: unit tests for the pipeline and the app's statistics, and a smoke test that renders every page and chart type in both languages and with every comparison.
