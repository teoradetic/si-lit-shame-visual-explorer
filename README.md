# si-lit-shame-visual-explorer

A free, public web app for exploring the shame passages an LLM detected in 305 Slovene novels (1828–1940). The code doesn't depend on shame, so it works for other emotions and larger corpora.

**Live app:** https://shame-visual-explorer-slovenian-literature.streamlit.app/

## How it fits together

1. **Prepare data:** the raw entry points and the source corpora become paragraph tables and token tables (`src/emotion_explorer/prep/`).
2. **Analyze data:** the tables are counted into the small files the app reads, `data/processed/` (`src/emotion_explorer/analysis/`).
3. **Explore:** the app (`app/`) reads only `data/processed/` and compares whichever novels the sidebar selects; it runs no NLP.

Everything in `data/processed/` and `data/tokens/` is committed, so the app runs without steps 1 and 2.

## Dependencies

| Group | Installed by | Needed for |
|---|---|---|
| runtime | `uv sync`, and the deployed app | the app: Streamlit, Altair, pandas, pyarrow, PyYAML |
| `prep` | `uv sync` (default group) | steps 1 and 2: zstandard reads the raw corpus, scikit-learn fits the themes and arcs |
| `corpus` | `uv sync --group corpus` | the `tokens` step only: CLASSLA, with torch |
| `dev` | `uv sync` (default group) | tests, ruff, pre-commit |

```bash
uv sync
uv run pre-commit install
```

## 1. Prepare data

| Folder | Contents |
|---|---|
| `data/raw/` | The entry points from [shame_sl_lit](https://github.com/teoradetic/shame_sl_lit) (commit `e075df3`), never edited: `corpus_metadata.csv` and the annotated corpus `main_shame_annotations.json.zst`. |
| `data/corpora/`, `data/models/` | Downloaded source corpora and CLASSLA models; not committed. |
| `data/tokens/` | Every token with lemma, part of speech, morphology and named entity, one file per novel. |

| Step | Writes |
|---|---|
| `corpora` | downloads the annotated [KDSP](http://hdl.handle.net/11356/1823), [PriLit](http://hdl.handle.net/11356/1319) and [ELTeC-slv](https://github.com/COST-ELTeC/ELTeC-slv) editions (262 novels, 1.6 GB) |
| `tokens` | `data/tokens/`: their annotation, and CLASSLA for the other 43 novels |
| `paragraphs` | one row per paragraph: scores, whether it is detected, novel metadata |
| `comparison` | low-score partners of the detected paragraphs |
| `excerpts` | excerpts with ±2 paragraphs of context, and their texts |

```bash
uv run emotion-explorer corpora                 # only to rebuild the tokens
uv run --group corpus emotion-explorer tokens   # writes missing data/tokens files
```

## 2. Analyze data

| Step | Writes |
|---|---|
| `overview` | per-novel counts, counts by position in the novel, typical arcs |
| `words` | lemma counts per novel, set, case and narration or speech; pairs in a sentence; names and the gender of past-tense subjects; corpus counts, word forms |
| `themes` | NMF themes, the main theme of each paragraph, and word counts per theme |
| `style` | style features per paragraph (whole, narration, speech), pooled per novel and set |

```bash
uv run emotion-explorer all     # paragraphs to style: rebuilds data/processed
uv run emotion-explorer words   # or one step
```

`all` runs the steps from `paragraphs` on, not `corpora` and `tokens`. What is specific to shame is in `src/emotion_explorer/emotion.py`.

## 3. Run the app

```bash
uv run streamlit run app/streamlit_app.py
```

The interface is in English and Slovene; the excerpts stay in Slovene. Each language has two files in `app/assets/languages/`: a YAML file with its interface text, name, flag and number format, and its method page. Adding them adds the language to the menu.

## Code layout

- `src/emotion_explorer/`: `cli.py`, `prep/` (step 1), `analysis/` (step 2).
- `app/`: `streamlit_app.py`, `views/` (pages), `helpers/` (filters, comparison, statistics, charts), `assets/languages/`.
- `tests/`: unit tests, and a smoke test of every page and chart type in both languages and every comparison.
