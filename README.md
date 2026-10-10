# si-lit-shame-visual-explorer

A free, public web app for exploring the shame passages an LLM detected in 305 Slovene novels (1828–1940). The code doesn't depend on shame, so the same pipeline can be used for other emotions and larger corpora.

## Setup

```bash
uv sync                  # Python 3.13 and all dependency groups
uv run pre-commit install
```

## Data

All numbers are derived in this repo by Python CLI commands.

| Folder | Contents |
|---|---|
| `data/raw/` | The two entry points, taken from [shame_sl_lit](https://github.com/teoradetic/shame_sl_lit) at commit `e075df3` and never edited: `corpus_metadata.csv` and the annotated corpus `main_shame_annotations.json.zst` (zstd-compressed JSON). |
| `data/processed/` | Compact outputs (parquet) that the app reads. |

## Layout

- `src/emotion_explorer/`: the library and the data CLI.
- `app/`: the Streamlit app.
