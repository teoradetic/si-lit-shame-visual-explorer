## How the passages were found

The corpus has **{n_novels} Slovene novels** by {n_authors} authors, published {first}–{last}, split into **{n_paragraphs} paragraphs**. A language model (Mistral 7B Instruct, run locally at temperature 0) scored every paragraph three times for how strongly it relates to shame: on a 0–1, a 0–10 and a 0–100 scale. A paragraph is *detected* when all three scores are high:

| Tier | Rule | Paragraphs | Precision | Recall | F1 |
|---|---|---|---|---|---|
| **Core** | top 1%: 0–1 ≥ {core_0_1}, 0–10 ≥ {core_0_10}, 0–100 ≥ {core_0_100} | {n_core} | 77.4 % | 78.6 % | 78.0 % |
| **Broad** (default) | top 5%: 0–1 ≥ {broad_0_1}, 0–10 ≥ {broad_0_10}, 0–100 ≥ {broad_0_100} | {n_broad} | 69.5 % | 81.3 % | 74.9 % |

Precision, recall and F1 come from the expert-annotated gold set, weighted by stratum as in the paper. Core is the paper's rule.

The app shows one **shame score** per paragraph instead of the three ratings: each rating rescaled to 0–100, then averaged. It says how sure the model is that a paragraph is about shame, not how intense the shame is.

## Excerpts

Each detected paragraph is shown with {context} paragraphs before and after it, from the same novel. Excerpts that overlap are merged, so one excerpt can hold several detected paragraphs. Long paragraphs are shortened for display. Whole novels are never shown.

{n_over_context} very long paragraphs (over {over_context_chars} characters) did not fit into the model's context window of 4,096 tokens, so the model saw only their end. They are marked in the reader.

## The comparison set

The *Words* and *Style* views compare the detected passages with paragraphs that have **low scores on all three ranges** (0–1 ≤ {low_0_1}, 0–10 ≤ {low_0_10}, 0–100 ≤ {low_0_100}; {n_low} paragraphs). Each broad-tier paragraph is paired with one such paragraph **from the same novel and of similar length** (within a factor of {max_length_ratio:g}), at least three paragraphs away from any detected one. {n_matched} of the {n_broad} broad-tier paragraphs found a partner, in {n_novels_with_pairs} novels; long low-score paragraphs are scarce, so the longest detected paragraphs often have none.

The comparison set is not "all other paragraphs": those still contain most of the corpus's shame. This definition of a low score is **provisional** and still to be agreed.

When *with and without shame* is chosen under *Compare*, the *Over time* and *Within the novel* views count all low-score paragraphs, since they ask how much and where; *Words* and *Style* keep the length-matched comparison set.

## What the app cannot show

- **Detected shame is not all shame.** In the paper's estimate the model finds at most about 25 % of the shame-related paragraphs in the corpus. No view can show that shame is absent somewhere.
- **The scores are not intensity.** They measure how strongly a paragraph relates to shame and take only a few distinct values. Where the app averages them, it averages this relatedness.
- **Many breakdowns on small data produce chance patterns.** The *Style* view marks which differences survive a test with correction for multiple comparisons. Everything else is descriptive.
- **Confounds:** Cankar wrote 32 of the 67 Modernist novels; only 31 novels are by female authors; Realism and Modernism overlap in time; few novels were published before 1870; paragraph length varies widely; dialogue and narration differ in style.
- **Word lists are preliminary.** They use word forms, not lemmas, and every part of speech, until part-of-speech tagging is added.

## Data notes

- Periods and genders come from the corpus metadata as they are: Realism {n_realism}, Modernism {n_modernism}, unknown {n_period_unknown} novels. The paper counts 232 Realist novels and 6 of unknown period; the one novel that differs is not reassigned here.
- Every number in this app is recomputed from two files, the annotated corpus and its metadata, by the project's data pipeline.
