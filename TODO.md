# si-lit-shame-visual-explorer: TODO

## Goal
Build a free, public web app in which the literary experts (Ivana Zajc, Katja Mihurko) can explore the shame passages detected in 305 Slovene novels (1828–1940). The app should show:

- where shame appears;
- the themes, words, actions, emotions and style that come with it;
- how this differs from passages without shame;
- how all of this varies by literary period, author gender, author and year.

Every chart leads to the passages behind it.

**Outputs, in this order:** a tool the experts use, then research findings, then an article. Only part of the work will be publishable.

**Big picture:** the approach must also work for other emotions and for a corpus of about 1,000 novels. Nothing in the app may depend on shame specifically (e.g. the stem *sram*).

**Dates:**
- First review of the visualizations with Ivana: **30 Oct 2026, 13:00**.
- The collaboration ends on **31 Dec 2026**; about €2,000 is possible in 2027.

## Architecture decision
- **App:** Streamlit, hosted for free on Streamlit Community Cloud, with a multipage layout.
- **Look:** a custom theme in `.streamlit/config.toml` (fonts, palette, light and dark). All charts in Altair, with a shared Altair theme; no matplotlib in the app. Charts respond to clicks (`on_select`), and the selected points open their passages.
- **Custom views:** a Streamlit custom component (v2, written in JS: D3 or Observable Plot) only for one or two central views, if Altair can't draw them well.
- **Passages shown as excerpts:** the tagged paragraph is highlighted, with 2 paragraphs of context on each side, shown plainly. Whole novels are never shown.
- **Data:** all results are computed in advance in Python and stored as small parquet files in the app repo. The app does no NLP and runs no models.
- **Standalone project:** every number and derivation is recomputed here with Python CLI commands, not notebooks. No code is reused from the first project ([shame_sl_lit](https://github.com/teoradetic/shame_sl_lit)). This repo is the setup: it needs nothing from outside it.
- **Entry points (the only files taken from the first project):** `corpus_metadata.csv` and the annotated corpus `main_shame_annotations.json`, committed to `data/raw/` (the JSON zstd-compressed, 39 MB). Nothing else comes over: the models are 29 GB and the raw corpora 3.5 GB.
- **Language:** the interface is in English with an EN/SL switch at the top. The excerpts stay in Slovene.
- **Shame tiers (Mistral):**

  | Tier | Rule | Cut-offs | Paragraphs | Gold-set precision / recall / F1 |
  |---|---|---|---|---|
  | **Core** | the paper's rule: top 1% on all three score ranges | 0–1 ≥ 0.95, 0–10 ≥ 8, 0–100 ≥ 85 | 4,475 | 77.4 / 78.6 / 78.0 |
  | **Broad** | top 5% on all three ranges | 0–1 ≥ 0.85, 0–10 ≥ 8, 0–100 ≥ 85 | 18,386 | 69.5 / 81.3 / 74.9 |

  The gold-set metrics are stratum-weighted, as in the paper.
- **Rejected options:**

  | Option | Why not |
  |---|---|
  | Static site (Observable Framework on GitHub Pages) | Better looking and never sleeps, but the interface is in JS and it would be slower to build before 30.10. Revisit if the 1,000-novel overview becomes a public showcase. |
  | Python in the browser (marimo, Shinylive) | Slow first load. |
  | Hugging Face Spaces | Docker and Gradio Spaces now need a paid plan. |
  | shinyapps.io | 25 active hours per month. |
  | Plotly Cloud | A free trial only. |

## Gotchas that apply everywhere
- **Detected shame is not all shame.** In the paper's estimate, Mistral finds at most about 25% of the shame-related paragraphs in the corpus, and its precision on the gold set was 77%. Every view should describe the *detected* passages. "Shame is absent here" can't be concluded from the data.
- **The app is public,** and so is everything in its repo. The novels and excerpts are public domain and open source by default.
- **The scores are not intensity.** Mistral's scores measure how strongly a paragraph relates to shame, and they use only a few distinct values. So "intensity" is the score, and the app must say exactly that.
- **Confounds to control or show:**
  - Cankar wrote 32 of the 67 Modernist novels.
  - Only 31 novels are by women.
  - Realism and Modernism overlap in time.
  - Few novels were published before 1870.
  - Paragraph length varies widely.
  - Dialogue and narration differ in style.
- **Many breakdowns on small data produce chance patterns.** Mark which patterns are tested and which are only descriptive.
- **The app sleeps after 12 hours without visitors.** Open it before every meeting.

---

## Tickets
⏰ = needed for the 30.10 review.

### Setup
- [ ] **SET-01 Create the repo and environment** ⏰
  - uv (dependency groups: app runtime / `prep` / `dev`), Python 3.13 managed by uv, ruff, pre-commit, and a commit-msg hook for strict Conventional Commits.
  - Feature branches only; `main` is protected by a pre-commit hook.
  - Commit the two entry points to `data/raw/`.
  - *Gotcha:* the app repo must stay small enough to deploy, so data prep scripts write only compact outputs into it.
- [ ] **SET-02 Deploy an empty app to Community Cloud** ⏰
  - Deploy on day one, so that hosting problems show up early.
- [ ] **SET-03 Set up the theme and the chart style** ⏰
  - Write `config.toml` (fonts, palette, light and dark) and one Altair theme used by every chart.
  - Choose a colour pair for Realism and Modernism and keep it the same in every view.

### Data
- [ ] **DATA-01 Build the paragraph table** ⏰
  - One row for each of the 336,014 paragraphs, with:
    - novel id and paragraph id;
    - relative position in the novel;
    - length in characters;
    - whether it contains *sram*;
    - the three Mistral scores;
    - the core and broad tier flags;
    - author, gender, year and period.
  - Source: `data/raw/main_shame_annotations.json.zst` and `data/raw/corpus_metadata.csv`.
  - *Gotchas:*
    - Paragraph ids are string keys in the JSON.
    - `corpus_metadata.csv` has Realism 231, Modernism 67 and unknown 7, while the paper says 232 / 6. Decide which to use and document it.
- [ ] **DATA-02 Build the excerpts** ⏰
  - Each tagged paragraph with 2 paragraphs before and after it, from the same novel only. Merge excerpts that overlap.
  - Expected size: about 8.3 M characters for core and 23.6 M for broad.
  - *Gotchas:*
    - Paragraphs range up to 24k characters, so truncate long ones in the display.
    - 20 very long paragraphs were cut off during LLM scoring (the reproducibility record in `ARTICLE_WRITING_PLAN.md`); flag them.
- [ ] **DATA-03 Define the comparison set without shame** ⏰
  - Paragraphs with low Mistral scores, matched to the shame set by novel and length.
  - The shame set is the broad tier (top 5% on all three ranges).
  - What counts as a "low" score is still open: explore the score distributions first and agree on a working definition.
  - *Gotcha:* don't use "all untagged paragraphs", because they still contain most of the corpus's shame.
- [ ] **DATA-04 Add part-of-speech and grammatical tags**
  - Run CLASSLA (lemma, POS and morphology including grammatical gender; also named entities) on the shame and comparison sets.
  - Run it once and cache the output.
  - *Gotchas:*
    - The novels use historical spelling, so accuracy will be lower. Spot-check about 50 sentences.
    - Replace the lemmagen3 lemmas from the first project, which contain errors.
- [x] ~~**DATA-05 Import Ivana's database metadata**~~ Dropped (10 Oct 2026): the metadata won't arrive. Use the corpus and `corpus_metadata.csv`.
  - Join it to the paragraph table.
  - *Gotchas:*
    - Their passages are most likely the 440 paragraphs tagged by all three LLMs (`output/paragraphs_marked_as_shame_related_by_all_llm_for_ivana.csv`, 24 Apr 2026), not the Mistral set, so the ids must be mapped.
    - The data may not be shareable or public.

### Analyses (each one feeds an app view)
- [ ] **AN-01 Shame over time, period and gender** ⏰
  - Share of tagged paragraphs per novel against publication year, split by period and gender, plus the mean score.
  - *Gotcha:* normalize by novel length, because novels range from 24 to 17,671 paragraphs.
- [ ] **AN-02 Where shame falls in the novel** ⏰
  - Tagged paragraphs by relative position (start to end), per novel and summed by period.
  - Show it as one line per novel, with the shame paragraphs as marks.
  - *Gotcha:* with the core tier, many novels have only a few marks. Show the broad tier by default.
- [ ] **AN-03 Words typical of shame passages** ⏰
  - Nouns and adjectives that distinguish the shame set from the comparison set, using the weighted log-odds ratio with an informative prior (Monroe et al. 2008).
  - *Gotcha:* character names will dominate the list. Filter out proper nouns (DATA-04) and check that each word occurs in several novels by different authors.
- [ ] **AN-04 Actions: verbs in shame passages** ⏰
  - The same method as AN-03, restricted to verbs.
- [ ] **AN-05 Women and femininity**
  - Female roles (mother, wife, widow, maid, streetwalker…) and grammatically feminine nouns and adjectives, in the shame set against the comparison set.
  - *Gotchas:*
    - Grammatical gender is not social gender.
    - The list of roles comes from the experts.
- [ ] **AN-06 Word networks**
  - Pairs of words that occur together in shame passages (PMI with a frequency floor).
  - *Gotcha:* without strict filtering the graph is unreadable.
- [ ] **AN-07 Other emotions in shame passages**
  - Emotion words from the LiLaH lexicon (Ljubešić et al. 2022), against the comparison set.
  - *Gotcha:* the lexicon was built from modern, non-literary text. Scoring other emotions with an LLM instead would take a long GPU run on the local machine.
- [ ] **AN-08 Style** ⏰ (basic version)
  - Sentence length, vocabulary diversity (MATTR, which doesn't depend on text length), repeated words, and punctuation (`! ? ; , … –`), shame against comparison.
  - *Gotchas:*
    - Dialogue and narration differ, so split them where possible (quotation marks »« „“).
    - Sentence splitting is unreliable on historical text.
- [ ] **AN-09 Silence and pauses**
  - Signs in the text: ellipses, dashes, broken-off speech, very short sentences.
  - *Gotcha:* absence can only be measured through such signs, and the experts must agree on what counts.
- [ ] **AN-10 Themes with and without shame**
  - Topics on the broad tier and on the comparison set, to see which themes appear mainly with or without detected shame.
  - *Gotchas:*
    - A theme without detected shame may still contain shame.
    - Avoid repeating the paper's LDA.
- [ ] **AN-11 Who shames whom**
  - Have an LLM extract the shamer, the person shamed and their roles; pilot on 50 passages checked by the experts.
  - *Gotcha:* this is hard, so drop it if the pilot accuracy is poor.
- [ ] **AN-12 Shame categories on a radar chart**
  - Categories at the corners (femininity, orphans, poverty, blasphemy…), split by period.
  - *Gotcha:* the categories come from LLM labels checked by the experts. Agree on the list and definitions first.
- [ ] **AN-13 Cankar in depth**
  - His 32 novels split into early, middle and late phases, using Ivana's stylometry dates.
  - Optionally extend to his whole oeuvre.
  - *Gotchas:*
    - New texts must be scored with the identical setup: Ollama 0.9.6, Q4_0, temperature 0, three ranges, same prompt (`helpers/llm_prompts.py`).
    - Use the cut-offs of the 305-novel corpus.

### App
- [ ] **APP-01 Global filters** ⏰
  - Language (EN/SL), tier (core or broad, broad by default), period, gender, author and year range, kept in session state and applied to every view.
- [ ] **APP-02 Excerpt reader** ⏰
  - A single component used by every view: the tagged paragraph highlighted, the context in grey, and author, title, year and position in the novel.
  - It opens when a chart point is clicked.
- [ ] **APP-03 A page for each analysis** ⏰ (pages for the analyses marked ⏰)
  - One chart, split by period on the same chart, plus the excerpts behind the selected points.
- [ ] **APP-04 Method and caveats page** ⏰
  - How the passages were tagged, precision and recall for each tier, and what the app can't show (see the gotchas above).
- [ ] **APP-05 Custom central view** (optional)
  - A custom component for AN-02 or AN-06, if Altair isn't good enough.

### Milestones
- [ ] **MS-01 Review on 30 Oct 2026, 13:00**
  - Deployed app with SET-01–03, DATA-01–03, AN-01–04, the basic AN-08 and APP-01–04.
- [ ] **MS-02 End of year**
  - The remaining analyses as far as data and time allow.
  - Decide with Ivana which findings are publishable and outline the article.
- [ ] **MS-03 Big-picture note**
  - One page on how the app would scale to other emotions and about 1,000 novels: what is specific to shame, and what would need a new gold set.
