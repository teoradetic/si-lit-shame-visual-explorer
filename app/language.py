"""Interface strings in English and Slovene. The excerpts stay in Slovene.

The texts are written for readers outside literary studies and statistics;
technical detail lives on the method page and in "how is this calculated"
boxes. Slovene strings avoid number agreement ("Romanov: 5" rather than
"5 romanov") so that one template fits every count.
"""

import streamlit as st

LANGUAGES = ("en", "sl")

STRINGS: dict[str, dict[str, str]] = {
    # App frame
    "app.title": {
        "en": "Shame in Slovene novels, 1828–1940",
        "sl": "Sram v slovenskih romanih, 1828–1940",
    },
    "app.language": {"en": "Language", "sl": "Jezik"},
    "nav.home": {"en": "Overview", "sl": "Pregled"},
    "nav.time": {"en": "Over time", "sl": "Skozi čas"},
    "nav.position": {"en": "Within the novel", "sl": "Znotraj romana"},
    "nav.words": {"en": "Words", "sl": "Besede"},
    "nav.style": {"en": "Style", "sl": "Slog"},
    "nav.method": {"en": "Method and caveats", "sl": "Metodologija in omejitve"},
    "chart.type": {"en": "Chart", "sl": "Graf"},
    # Filters
    "filters.header": {"en": "Filters", "sl": "Filtri"},
    "filters.tier": {"en": "Which passages", "sl": "Kateri odlomki"},
    "filters.tier_help": {
        "en": "Broad: the passages the model is fairly sure are about shame. "
        "Core: only those it is most sure about; fewer passages, but fewer "
        "mistakes.",
        "sl": "Širši nabor: odlomki, za katere je model precej prepričan, da "
        "govorijo o sramu. Jedro: le tisti, za katere je najbolj prepričan; "
        "manj odlomkov, a tudi manj napak.",
    },
    "filters.period": {"en": "Literary period", "sl": "Literarno obdobje"},
    "filters.authors": {"en": "Authors", "sl": "Avtorji"},
    "filters.authors_placeholder": {"en": "All authors", "sl": "Vsi avtorji"},
    "filters.novels": {"en": "Novels", "sl": "Romani"},
    "filters.novels_placeholder": {"en": "All novels", "sl": "Vsi romani"},
    "filters.years": {"en": "Year of publication", "sl": "Leto izida"},
    "filters.reset": {"en": "Reset filters", "sl": "Ponastavi filtre"},
    "filters.summary": {
        "en": "{novels} novels · {paragraphs} shame-related paragraphs",
        "sl": "Romanov: {novels} · odstavkov o sramu: {paragraphs}",
    },
    "filters.empty": {
        "en": "No novels match these filters.",
        "sl": "Filtrom ne ustreza noben roman.",
    },
    # Labels for data values
    "tier.core": {"en": "Core (most certain)", "sl": "Jedro (najbolj gotovi)"},
    "tier.broad": {"en": "Broad (fairly certain)", "sl": "Širši nabor (precej gotovi)"},
    "period.Realism": {"en": "Realism", "sl": "realizem"},
    "period.Modernism": {"en": "Modernism", "sl": "modernizem"},
    "period.unknown": {"en": "Period unknown", "sl": "obdobje neznano"},
    "set.emotion": {"en": "With shame", "sl": "S sramom"},
    "set.comparison": {"en": "Without shame", "sl": "Brez sramu"},
    "paragraphs.all": {"en": "All paragraphs", "sl": "Vsi odstavki"},
    "paragraphs.narration": {"en": "Narration only", "sl": "Samo pripoved"},
    "paragraphs.dialogue": {"en": "With dialogue", "sl": "Z dialogom"},
    "field.novel": {"en": "Novel", "sl": "Roman"},
    "field.group": {"en": "Group", "sl": "Skupina"},
    "field.period": {"en": "Period", "sl": "Obdobje"},
    "field.novels": {"en": "Novels", "sl": "Romani"},
    "field.set": {"en": "Passages", "sl": "Odlomki"},
    "field.paragraphs": {"en": "Paragraphs", "sl": "Odstavki"},
    "field.tagged": {"en": "Shame-related paragraphs", "sl": "Odstavki o sramu"},
    "field.score": {"en": "Shame score (0–100)", "sl": "Ocena sramu (0–100)"},
    # Excerpt reader
    "reader.header": {"en": "Passages", "sl": "Odlomki"},
    "reader.legend.focus": {
        "en": "Marked by the model as about shame",
        "sl": "Model ga je označil kot odstavek o sramu",
    },
    "reader.legend.comparison": {
        "en": "Rated by the model as not about shame (for comparison)",
        "sl": "Model ga je ocenil kot odstavek brez sramu (za primerjavo)",
    },
    "reader.legend.context": {
        "en": "The paragraphs around it, for context",
        "sl": "Sosednji odstavki, za kontekst",
    },
    "reader.count": {"en": "{n} passages", "sl": "Odlomkov: {n}"},
    "reader.sort": {"en": "Order", "sl": "Vrstni red"},
    "reader.sort.score": {
        "en": "Highest shame score first",
        "sl": "Najprej najvišja ocena sramu",
    },
    "reader.sort.position": {
        "en": "By novel, in reading order",
        "sl": "Po romanih, v vrstnem redu branja",
    },
    "reader.sort.random": {"en": "Random", "sl": "Naključno"},
    "reader.sort.rank": {
        "en": "Highest value first",
        "sl": "Najprej najvišja vrednost",
    },
    "reader.page": {"en": "Page", "sl": "Stran"},
    "reader.of": {"en": "of {n}", "sl": "od {n}"},
    "reader.position": {
        "en": "paragraph {n} of {total}",
        "sl": "odstavek {n} od {total}",
    },
    "reader.score": {
        "en": "shame score {score} / 100",
        "sl": "ocena sramu {score} / 100",
    },
    "reader.score_help": {
        "en": "How sure the model is that the paragraph is about shame: its three "
        "ratings, rescaled to 0–100 and averaged.",
        "sl": "Kako prepričan je model, da odstavek govori o sramu: njegove tri "
        "ocene, preračunane na 0–100 in povprečene.",
    },
    "reader.over_context": {
        "en": "This paragraph was too long for the model, which read only its end.",
        "sl": "Odstavek je bil za model predolg, zato je prebral le njegov konec.",
    },
    "reader.truncated": {
        "en": "Shortened for display; the paragraph has {n} characters.",
        "sl": "Za prikaz skrajšano; odstavek ima {n} znakov.",
    },
    "reader.full": {"en": "Show the full paragraph", "sl": "Prikaži cel odstavek"},
    "reader.empty": {
        "en": "Click a point in the chart to read the passages behind it.",
        "sl": "Kliknite točko v grafu, da preberete odlomke, ki so za njo.",
    },
    "reader.none": {
        "en": "Nothing to show for this selection.",
        "sl": "Za ta izbor ni ničesar za prikaz.",
    },
    # Overview page
    "home.intro": {
        "en": "Where, when and how does shame appear in Slovene novels? A computer "
        "model read all {novels} novels in this collection, by {authors} "
        "authors and published {first}–{last}, paragraph by paragraph, and "
        "marked the paragraphs it judged to be about shame. Use the charts to "
        "explore these paragraphs; every chart leads to the passages themselves.",
        "sl": "Kje, kdaj in kako se v slovenskih romanih pojavlja sram? Računalniški "
        "model je prebral vseh {novels} romanov te zbirke ({authors} avtorjev in "
        "avtoric, izdanih v letih {first}–{last}), odstavek za odstavkom, in "
        "označil tiste, za katere je presodil, da govorijo o sramu. Z grafi "
        "lahko te odstavke raziskujete; vsak graf vodi do samih odlomkov.",
    },
    "home.caveat": {
        "en": "**The model does not find all shame.** It catches perhaps a quarter "
        "of the paragraphs about shame, and about one in four of the paragraphs "
        "it marks are not really about shame. So the charts show where the model "
        "*found* shame, not everywhere shame is. More in *Method and caveats*.",
        "sl": "**Model ne najde vsega sramu.** Ujame morda četrtino odstavkov o "
        "sramu, približno eden od štirih odstavkov, ki jih označi, pa v resnici "
        "ne govori o sramu. Grafi zato kažejo, kje je model sram *našel*, ne pa "
        "povsod, kjer sram je. Več v razdelku *Metodologija in omejitve*.",
    },
    "home.m_novels": {"en": "Novels", "sl": "Romani"},
    "home.m_paragraphs": {"en": "Paragraphs read", "sl": "Prebrani odstavki"},
    "home.m_tagged": {"en": "About shame", "sl": "O sramu"},
    "home.m_excerpts": {"en": "Passages to read", "sl": "Odlomki za branje"},
    "home.views": {"en": "What you can explore", "sl": "Kaj lahko raziskujete"},
    "home.view.time": {
        "en": "**Over time:** which novels, periods and authors have more shame, "
        "and how this changes from 1828 to 1940.",
        "sl": "**Skozi čas:** kateri romani, obdobja in avtorji imajo več sramu in "
        "kako se to spreminja od 1828 do 1940.",
    },
    "home.view.position": {
        "en": "**Within the novel:** whether shame comes at the beginning, the "
        "middle or the end of a story.",
        "sl": "**Znotraj romana:** ali se sram pojavi na začetku, v sredini ali na "
        "koncu zgodbe.",
    },
    "home.view.words": {
        "en": "**Words:** the words that come with shame, compared with passages "
        "without it.",
        "sl": "**Besede:** besede, ki spremljajo sram, v primerjavi z odlomki brez "
        "njega.",
    },
    "home.view.style": {
        "en": "**Style:** how passages about shame are written: sentence length, "
        "question marks, exclamations, repetition.",
        "sl": "**Slog:** kako so napisani odlomki o sramu: dolžina povedi, "
        "vprašaji, klicaji, ponavljanje.",
    },
    "home.view.method": {
        "en": "**Method and caveats:** how the model found the passages and how "
        "far it can be trusted.",
        "sl": "**Metodologija in omejitve:** kako je model našel odlomke in koliko mu "
        "lahko zaupamo.",
    },
    "home.sample": {
        "en": "A few passages to start with",
        "sl": "Nekaj odlomkov za začetek",
    },
    # Over time (AN-01)
    "time.title": {"en": "Shame over time", "sl": "Sram skozi čas"},
    "time.type.scatter": {"en": "Every novel", "sl": "Vsak roman"},
    "time.type.trend": {
        "en": "Trend (moving average)",
        "sl": "Trend (drseče povprečje)",
    },
    "time.type.decades": {
        "en": "Spread per decade",
        "sl": "Razpršenost po desetletjih",
    },
    "time.type.authors": {"en": "Authors", "sl": "Avtorji"},
    "time.type.top": {
        "en": "Novels with the most shame",
        "sl": "Romani z največ sramu",
    },
    "time.metric": {"en": "Measure", "sl": "Mera"},
    "time.metric.share": {"en": "Share of paragraphs", "sl": "Delež odstavkov"},
    "time.metric.per_10k_words": {"en": "Per 10,000 words", "sl": "Na 10.000 besed"},
    "time.metric.mean_score": {
        "en": "Average shame score",
        "sl": "Povprečna ocena sramu",
    },
    "time.measures_help_title": {
        "en": "What do the measures mean?",
        "sl": "Kaj pomenijo mere?",
    },
    "time.trend": {"en": "Trend line", "sl": "Trendna črta"},
    "time.x": {"en": "Year of publication", "sl": "Leto izida"},
    "time.decade": {"en": "Decade of publication", "sl": "Desetletje izida"},
    "time.window_centre": {"en": "Years around", "sl": "Leta okoli"},
    "time.median": {"en": "Median", "sl": "Mediana"},
    "time.min_novels": {
        "en": "Authors with at least this many novels",
        "sl": "Avtorji z vsaj toliko romani",
    },
    "time.n_top": {"en": "Novels shown", "sl": "Prikazani romani"},
    "time.read.trend": {
        "en": "How to read: the line is the average of the novels published within "
        "{window} years around each year (only where at least {n} novels are "
        "available); the shaded band shows how uncertain that average is. A "
        "wide band means few or very different novels. Click the line to read "
        "the passages of the novels behind it.",
        "sl": "Kako brati: črta je povprečje romanov, izdanih v {window} letih okoli "
        "posameznega leta (le kjer je vsaj {n} romanov); osenčeni pas kaže, kako "
        "negotovo je to povprečje. Širok pas pomeni malo ali zelo različnih "
        "romanov. Kliknite črto, da preberete odlomke romanov za njo.",
    },
    "time.read.decades": {
        "en": "How to read: for each decade the box holds the middle half of the "
        "novels, the line inside it is the median, and the whiskers reach the "
        "rest. Dots are single novels; click one to read its passages.",
        "sl": "Kako brati: za vsako desetletje škatla zajame srednjo polovico "
        "romanov, črta v njej je mediana, ročaja segata do ostalih. Točke so "
        "posamezni romani; kliknite eno, da preberete odlomke.",
    },
    "time.read.authors": {
        "en": "How to read: each row is an author (number of novels in brackets), "
        "each dot one of their novels, the dark bar their median. Authors are "
        "sorted from most to least shame. Click a dot to read its passages.",
        "sl": "Kako brati: vsaka vrstica je avtor (v oklepaju število romanov), "
        "vsaka točka eden od njegovih romanov, temna črtica mediana. Avtorji so "
        "razvrščeni od največ do najmanj sramu. Kliknite točko za odlomke.",
    },
    "time.read.top": {
        "en": "How to read: the novels with the highest value on the chosen "
        "measure, from the top. Click a bar to read the novel's passages.",
        "sl": "Kako brati: romani z najvišjo vrednostjo izbrane mere, od zgoraj "
        "navzdol. Kliknite stolpec, da preberete odlomke romana.",
    },
    "time.descriptive": {
        "en": "These charts describe; they do not test. Keep in mind: Cankar wrote "
        "32 of the 67 Modernist novels, only 31 novels are by female authors, and few "
        "novels appeared before 1870.",
        "sl": "Grafi opisujejo, ne testirajo. Upoštevajte: Cankar je napisal 32 od "
        "67 modernističnih romanov, avtorice le 31 romanov, pred letom 1870 pa je "
        "izšlo malo romanov.",
    },
    "time.selected": {
        "en": "Passages from the selected novels ({n})",
        "sl": "Odlomki iz izbranih romanov ({n})",
    },
    # Within the novel (AN-02)
    "position.title": {
        "en": "Where shame falls in the novel",
        "sl": "Kje v romanu se pojavi sram",
    },
    "position.explain": {
        "en": "**Position in the novel:** every novel is stretched to the same "
        "length, from its first paragraph (0 %) to its last (100 %). 50 % is the "
        "middle of the novel, 90 % is near the end, whatever the novel's length. "
        "The charts divide each novel into 20 equal parts of 5 %.",
        "sl": "**Mesto v romanu:** vsak roman je raztegnjen na isto dolžino, od "
        "prvega (0 %) do zadnjega odstavka (100 %). 50 % je sredina romana, 90 % "
        "je blizu konca, ne glede na dolžino romana. Grafi razdelijo vsak roman "
        "na 20 enakih delov po 5 %.",
    },
    "position.type.concentration": {
        "en": "Where shame concentrates",
        "sl": "Kje se sram zgosti",
    },
    "position.type.share": {"en": "Share in each part", "sl": "Delež v vsakem delu"},
    "position.type.violin": {
        "en": "Distribution (violins)",
        "sl": "Porazdelitev (violine)",
    },
    "position.type.heatmap": {
        "en": "Heatmap: novels side by side",
        "sl": "Toplotni zemljevid: romani drug ob drugem",
    },
    "position.type.novels": {"en": "Novel by novel", "sl": "Roman za romanom"},
    "position.share_x": {"en": "About shame (%)", "sl": "O sramu (%)"},
    "position.part_from": {"en": "Part starting at (%)", "sl": "Del od (%)"},
    "position.density": {
        "en": "Density (1 = even spread)",
        "sl": "Gostota (1 = enakomerno)",
    },
    "position.smooth": {
        "en": "Smooth (average each part with its neighbours)",
        "sl": "Zgladi (vsak del povpreči s sosednjima)",
    },
    "position.columns": {"en": "Columns", "sl": "Stolpci"},
    "position.columns.novels": {"en": "One per novel", "sl": "Po en za roman"},
    "position.columns.decades": {
        "en": "Novels grouped by decade",
        "sl": "Romani, združeni po desetletjih",
    },
    "position.relative": {
        "en": "Relative to each column's average",
        "sl": "Glede na povprečje stolpca",
    },
    "position.relative_title": {
        "en": "Shame compared with the average (1 = average)",
        "sl": "Sram glede na povprečje (1 = povprečje)",
    },
    "position.order": {"en": "Order novels by", "sl": "Razvrsti romane po"},
    "position.order.year": {
        "en": "Year of publication (oldest first)",
        "sl": "letu izida (najstarejši prvi)",
    },
    "position.order.count": {
        "en": "Number of shame-related paragraphs (most first)",
        "sl": "številu odstavkov o sramu (največ prvi)",
    },
    "position.order.share": {
        "en": "Share of shame-related paragraphs (highest first)",
        "sl": "deležu odstavkov o sramu (najvišji prvi)",
    },
    "position.order.author": {"en": "Author (A–Z)", "sl": "avtorju (A–Ž)"},
    "position.marks": {"en": "Show", "sl": "Prikaži"},
    "position.marks.marks": {"en": "Each paragraph", "sl": "Vsak odstavek"},
    "position.marks.smoothed": {"en": "Smoothed", "sl": "Zglajeno"},
    "position.show_all": {"en": "All novels", "sl": "Vsi romani"},
    "position.limit": {
        "en": "Showing {n} of {total} novels. Tick “All novels” to see them all.",
        "sl": "Prikazanih romanov: {n} od {total}. Za vse označite »Vsi romani«.",
    },
    "position.read.concentration": {
        "en": "How to read: 1 means a part of the novel has as much shame as the "
        "novel as a whole; 1.2 means 20 % more, 0.8 means 20 % less. Each novel "
        "counts equally (novels with fewer than {min_tagged} shame-related "
        "paragraphs are left out). The shaded band shows the uncertainty. Click a "
        "point to read passages from that part of the novels.",
        "sl": "Kako brati: 1 pomeni, da ima del romana toliko sramu kot roman v "
        "celoti; 1,2 pomeni 20 % več, 0,8 pa 20 % manj. Vsak roman šteje enako "
        "(romani z manj kot {min_tagged} odstavki o sramu so izpuščeni). Osenčeni "
        "pas kaže negotovost. Kliknite točko za odlomke iz tega dela romanov.",
    },
    "position.read.share": {
        "en": "How to read: the percentage of all paragraphs in each part of the "
        "novels that the model marked as about shame. Long novels weigh more "
        "here. Click a point to read passages from that part.",
        "sl": "Kako brati: odstotek vseh odstavkov v posameznem delu romanov, ki "
        "jih je model označil kot odstavke o sramu. Dolgi romani tu štejejo več. "
        "Kliknite točko za odlomke iz tega dela.",
    },
    "position.read.violin": {
        "en": "How to read: each shape shows where the shame-related paragraphs "
        "lie, from the beginning (top) to the end (bottom). Where the shape is "
        "wide, there are many; if shame were spread evenly, the shape would be a "
        "straight band.",
        "sl": "Kako brati: vsaka oblika kaže, kje ležijo odstavki o sramu, od "
        "začetka (zgoraj) do konca (spodaj). Kjer je oblika široka, jih je veliko; "
        "če bi bil sram enakomerno razporejen, bi bila oblika raven pas.",
    },
    "position.bin_selected": {
        "en": "Passages between {a} % and {b} % of the novels",
        "sl": "Odlomki med {a} % in {b} % romanov",
    },
    # Words (AN-03)
    "words.title": {
        "en": "Words that come with shame",
        "sl": "Besede, ki spremljajo sram",
    },
    "words.type.cloud": {"en": "Word cloud", "sl": "Oblak besed"},
    "words.type.dots": {"en": "Dot chart", "sl": "Točkovni graf"},
    "words.n": {"en": "Words shown", "sl": "Prikazane besede"},
    "words.hide_function": {
        "en": "Hide function words",
        "sl": "Skrij funkcijske besede",
    },
    "words.hide_stem": {
        "en": "Hide words containing “{stem}”",
        "sl": "Skrij besede, ki vsebujejo »{stem}«",
    },
    "words.function_title": {
        "en": "What are function words?",
        "sl": "Kaj so funkcijske besede?",
    },
    "words.function_help": {
        "en": "Function words are short grammatical words that carry little meaning "
        "on their own: pronouns (*jaz, ti, njega*), forms of *biti* (*sem, je, "
        "bi*), prepositions (*v, na, z*), conjunctions (*in, da, ker*) and "
        "particles (*ne, še, že*). They dominate any word list, so they are "
        "hidden by default. They come from a hand-made list of {n} words, which "
        "also holds a few old spellings (*sim, de, ino*):",
        "sl": "Funkcijske besede so kratke slovnične besede, ki same po sebi "
        "nimajo veliko pomena: zaimki (*jaz, ti, njega*), oblike glagola *biti* "
        "(*sem, je, bi*), predlogi (*v, na, z*), vezniki (*in, da, ker*) in "
        "členki (*ne, še, že*). Prevladale bi v vsakem seznamu, zato so privzeto "
        "skrite. Izhajajo iz ročno sestavljenega seznama {n} besed, ki vsebuje "
        "tudi nekaj starih zapisov (*sim, de, ino*):",
    },
    "words.counts": {"en": "Numbers behind the chart", "sl": "Številke za grafom"},
    "words.col.word": {"en": "Word", "sl": "Beseda"},
    "words.col.ratio": {
        "en": "Times more frequent",
        "sl": "Kolikokrat pogostejša",
    },
    "words.col.per_10k_emotion": {
        "en": "Per 10,000 words, with shame",
        "sl": "Na 10.000 besed, s sramom",
    },
    "words.col.per_10k_comparison": {
        "en": "Per 10,000 words, without shame",
        "sl": "Na 10.000 besed, brez sramu",
    },
    "words.col.n_novels": {"en": "Novels", "sl": "Romani"},
    "words.selected": {
        "en": "Passages containing “{word}”",
        "sl": "Odlomki z besedo »{word}«",
    },
    # Style (AN-08)
    "style.title": {"en": "How shame is written", "sl": "Kako je sram napisan"},
    "style.type.index": {
        "en": "Compared with passages without shame",
        "sl": "V primerjavi z odlomki brez sramu",
    },
    "style.type.raw": {"en": "Actual values side by side", "sl": "Dejanske vrednosti"},
    "style.type.time": {"en": "Over time", "sl": "Skozi čas"},
    "style.per_1k": {
        "en": "{feature} per 1,000 characters",
        "sl": "{feature} na 1.000 znakov",
    },
    "style.split": {"en": "Paragraphs", "sl": "Odstavki"},
    "style.measures_title": {
        "en": "What do the measures mean?",
        "sl": "Kaj pomenijo mere?",
    },
    "style.measures_help": {
        "en": "- **Words per sentence:** the average length of a sentence.\n"
        "- **Vocabulary diversity (MATTR):** take any 100 words in a row and count "
        "how many of them are different; MATTR is the average share over the "
        "whole text. 0.78 means about 78 different words in every 100. Higher "
        "means a richer, less repetitive vocabulary. Unlike a simple count, it "
        "does not depend on the length of the text.\n"
        "- **Words repeated within 10 words:** the share of words that already "
        "appeared among the 10 words before them (short words are ignored).\n"
        "- **Exclamation marks, question marks, semicolons, commas, ellipses, "
        "dashes:** how many per 1,000 characters.",
        "sl": "- **Besede na poved:** povprečna dolžina povedi.\n"
        "- **Raznolikost besedišča (MATTR):** vzemite poljubnih 100 zaporednih "
        "besed in preštejte, koliko je različnih; MATTR je povprečni delež čez "
        "celotno besedilo. 0,78 pomeni približno 78 različnih besed na vsakih "
        "100. Višje pomeni bogatejše, manj ponavljajoče se besedišče. Za razliko "
        "od preprostega štetja ni odvisna od dolžine besedila.\n"
        "- **Besede, ponovljene v razmiku 10 besed:** delež besed, ki so se že "
        "pojavile med 10 besedami pred njimi (kratke besede so izpuščene).\n"
        "- **Klicaji, vprašaji, podpičja, vejice, tropičja, pomišljaji:** koliko "
        "jih je na 1.000 znakov.",
    },
    "style.legend.without": {
        "en": "Without shame (always 100)",
        "sl": "Brez sramu (vedno 100)",
    },
    "style.legend.with": {"en": "With shame", "sl": "S sramom"},
    "style.legend.filled": {
        "en": "Clear difference: very unlikely to be chance",
        "sl": "Jasna razlika: zelo malo verjetno naključje",
    },
    "style.legend.hollow": {
        "en": "Could be chance",
        "sl": "Lahko je naključje",
    },
    "style.verdict.clear": {"en": "Clear difference", "sl": "Jasna razlika"},
    "style.verdict.chance": {"en": "Could be chance", "sl": "Lahko je naključje"},
    "style.read.index": {
        "en": "How to read: each row compares the two kinds of passage on one "
        "measure. The grey dot is the passages without shame, always set to 100; "
        "the coloured dot is the passages with shame. A coloured dot at 200 means "
        "passages with shame have twice as much of that measure; at 80, a fifth "
        "less. The coloured line shows the uncertainty. Click a measure to read "
        "the passages highest on it.",
        "sl": "Kako brati: vsaka vrstica primerja obe vrsti odlomkov pri eni meri. "
        "Siva točka so odlomki brez sramu, vedno postavljeni na 100; barvna točka "
        "so odlomki s sramom. Barvna točka pri 200 pomeni, da imajo odlomki s "
        "sramom te mere dvakrat več; pri 80 petino manj. Barvna črta kaže "
        "negotovost. Kliknite mero za odlomke z najvišjo vrednostjo.",
    },
    "style.caveat": {
        "en": "Old spelling makes splitting sentences unreliable. Dialogue is "
        "recognized by quotation marks and speech dashes. Only novels with at "
        "least 5 paragraphs of each kind are compared. Whether a difference is "
        "clear was tested with a permutation test over novels, corrected for "
        "testing nine measures at once (Holm).",
        "sl": "Zaradi starega črkopisa je delitev na povedi nezanesljiva. Dialog je "
        "prepoznan po narekovajih in pomišljajih pred govorom. Primerjani so le "
        "romani z vsaj 5 odstavki vsake vrste. Ali je razlika jasna, je "
        "preverjeno s permutacijskim testom po romanih, popravljenim za hkratno "
        "testiranje devetih mer (Holm).",
    },
    "style.feature.sentence_words": {
        "en": "Words per sentence",
        "sl": "Besede na poved",
    },
    "style.feature.mattr": {
        "en": "Vocabulary diversity (MATTR)",
        "sl": "Raznolikost besedišča (MATTR)",
    },
    "style.feature.repetition": {
        "en": "Words repeated within 10 words",
        "sl": "Besede, ponovljene v razmiku 10 besed",
    },
    "style.feature.exclamation_per_1k": {"en": "Exclamation marks", "sl": "Klicaji"},
    "style.feature.question_per_1k": {"en": "Question marks", "sl": "Vprašaji"},
    "style.feature.semicolon_per_1k": {"en": "Semicolons", "sl": "Podpičja"},
    "style.feature.comma_per_1k": {"en": "Commas", "sl": "Vejice"},
    "style.feature.ellipsis_per_1k": {"en": "Ellipses", "sl": "Tropičja"},
    "style.feature.dash_per_1k": {"en": "Dashes", "sl": "Pomišljaji"},
    "style.no_paragraph": {
        "en": "This measure exists only for a whole novel, so no passages can be "
        "ranked by it.",
        "sl": "Ta mera obstaja le za cel roman, zato po njej ni mogoče razvrstiti "
        "odlomkov.",
    },
    "style.col.feature": {"en": "Measure", "sl": "Mera"},
    "style.col.n_novels": {"en": "Novels compared", "sl": "Primerjani romani"},
    "style.col.mean_emotion": {"en": "With shame", "sl": "S sramom"},
    "style.col.mean_comparison": {"en": "Without shame", "sl": "Brez sramu"},
    "style.col.verdict": {"en": "Difference", "sl": "Razlika"},
    "style.units": {
        "en": "Punctuation is counted per 1,000 characters; repetition is a share "
        "of words.",
        "sl": "Ločila so šteta na 1.000 znakov; ponavljanje je delež besed.",
    },
    "style.selected": {
        "en": "Passages with shame highest in: {feature}",
        "sl": "Odlomki s sramom z najvišjo vrednostjo: {feature}",
    },
    # Comparison, findings and methodology
    "filters.gender": {
        "en": "Author gender",
        "sl": "Spol avtorja",
    },
    "gender.F": {
        "en": "Female authors",
        "sl": "Avtorice",
    },
    "gender.M": {
        "en": "Male authors",
        "sl": "Avtorji",
    },
    "gender.unknown": {
        "en": "Gender unknown",
        "sl": "Spol neznan",
    },
    "gender_short.F": {
        "en": "Female",
        "sl": "Ženski",
    },
    "gender_short.M": {
        "en": "Male",
        "sl": "Moški",
    },
    "gender_short.unknown": {
        "en": "Unknown",
        "sl": "Neznan",
    },
    "field.counted": {
        "en": "Paragraphs counted",
        "sl": "Prešteti odstavki",
    },
    "compare.header": {
        "en": "Compare",
        "sl": "Primerjaj",
    },
    "compare.mode": {
        "en": "What to compare",
        "sl": "Kaj primerjati",
    },
    "compare.help": {
        "en": "Every chart on every page is broken down by this choice. The filters "
        "below choose the novels; the comparison splits them into groups.",
        "sl": "Ta izbira razdeli vsak graf na vsaki strani. Filtri spodaj izberejo "
        "romane, primerjava pa jih razdeli v skupine.",
    },
    "compare.mode.none": {
        "en": "Nothing: all novels together",
        "sl": "Nič: vsi romani skupaj",
    },
    "compare.mode.shame": {
        "en": "With and without shame",
        "sl": "S sramom in brez njega",
    },
    "compare.mode.period": {
        "en": "Realism and Modernism",
        "sl": "Realizem in modernizem",
    },
    "compare.mode.gender": {
        "en": "Female and male authors",
        "sl": "Avtorice in avtorje",
    },
    "compare.mode.authors": {
        "en": "Two authors",
        "sl": "Dva avtorja",
    },
    "compare.mode.novels": {
        "en": "Novels of one author",
        "sl": "Romane enega avtorja",
    },
    "compare.author_a": {
        "en": "First author",
        "sl": "Prvi avtor",
    },
    "compare.author_b": {
        "en": "Second author",
        "sl": "Drugi avtor",
    },
    "compare.author": {
        "en": "Author",
        "sl": "Avtor",
    },
    "compare.novels": {
        "en": "Novels (up to three)",
        "sl": "Romani (največ trije)",
    },
    "compare.everyone": {
        "en": "All selected novels",
        "sl": "Vsi izbrani romani",
    },
    "compare.left_out.period": {
        "en": "Novels of unknown period are left out of this comparison ({n}).",
        "sl": "Romani neznanega obdobja so iz te primerjave izpuščeni ({n}).",
    },
    "compare.left_out.gender": {
        "en": "Novels whose author's gender is unknown are left out of this "
        "comparison ({n}).",
        "sl": "Romani avtorjev neznanega spola so iz te primerjave izpuščeni ({n}).",
    },
    "compare.need_two_authors": {
        "en": "Pick two different authors in the sidebar.",
        "sl": "V stranski vrstici izberite dva različna avtorja.",
    },
    "compare.need_groups": {
        "en": "This needs at least {n} groups to compare; change the comparison in "
        "the sidebar.",
        "sl": "Za to so potrebne vsaj {n} skupine; spremenite primerjavo v stranski "
        "vrstici.",
    },
    "findings.title": {
        "en": "Findings",
        "sl": "Ugotovitve",
    },
    "findings.note": {
        "en": "Computed from the novels and the comparison selected in the sidebar. "
        "They describe the detected passages; only the Style page tests its "
        "differences.",
        "sl": "Izračunano iz romanov in primerjave, izbranih v stranski vrstici. "
        "Opisujejo zaznane odlomke; le stran Slog svoje razlike tudi testira.",
    },
    "methodology.title": {
        "en": "Methodology (technical)",
        "sl": "Metodologija (tehnično)",
    },
    "time.intro": {
        "en": "How much shame does each novel contain, and does this change over the "
        "years? Choose a chart; each shows the same novels in a different way, "
        "split by the comparison chosen in the sidebar.",
        "sl": "Koliko sramu vsebuje posamezen roman in ali se to spreminja skozi "
        "leta? Izberite graf; vsak pokaže iste romane na drugačen način, "
        "razdeljene po primerjavi, izbrani v stranski vrstici.",
    },
    "time.type.groups": {
        "en": "Groups side by side",
        "sl": "Skupine drugo ob drugi",
    },
    "time.axis.share": {
        "en": "Share of paragraphs (%)",
        "sl": "Delež odstavkov (%)",
    },
    "time.axis.per_10k_words": {
        "en": "Paragraphs per 10,000 words",
        "sl": "Odstavki na 10.000 besed",
    },
    "time.axis.mean_score": {
        "en": "Average shame score",
        "sl": "Povprečna ocena sramu",
    },
    "time.measures_help": {
        "en": "- **Share of paragraphs:** of all the paragraphs in a novel, the "
        "percentage the model marked as about shame. A novel of 1,000 "
        "paragraphs with 50 marked scores 5 %. Long and short novels can be "
        "compared.\n"
        "- **Per 10,000 words:** the same count, divided by the novel's length "
        "in words. Useful because paragraph length differs between authors.\n"
        "- **Average shame score:** every paragraph, marked or not, has a "
        "shame score from 0 to 100 (how sure the model is that it is about "
        "shame). This is the novel's average. It does not depend on where the "
        "line between marked and unmarked is drawn, but it is not how "
        "*intense* the shame is.\n"
        "- **With and without shame:** the second group counts the paragraphs "
        "the model rated clearly *not* about shame (a low rating on all three "
        "of its scales). Its numbers are about ten times larger, so it gets "
        "its own panel.",
        "sl": "- **Delež odstavkov:** od vseh odstavkov romana odstotek tistih, ki "
        "jih je model označil kot odstavke o sramu. Roman s 1.000 odstavki, od "
        "katerih je 50 označenih, ima 5 %. Tako lahko primerjamo dolge in "
        "kratke romane.\n"
        "- **Na 10.000 besed:** isto število, deljeno z dolžino romana v "
        "besedah. Uporabno, ker so odstavki pri avtorjih različno dolgi.\n"
        "- **Povprečna ocena sramu:** vsak odstavek, označen ali ne, ima oceno "
        "sramu od 0 do 100 (kako prepričan je model, da govori o sramu). To je "
        "povprečje romana. Ni odvisno od tega, kje potegnemo mejo med "
        "označenimi in neoznačenimi, ni pa mera *jakosti* sramu.\n"
        "- **S sramom in brez njega:** druga skupina šteje odstavke, za katere "
        "je model presodil, da zagotovo *ne* govorijo o sramu (nizka ocena na "
        "vseh treh lestvicah). Njene vrednosti so približno desetkrat večje, "
        "zato ima svoj graf.",
    },
    "time.read.scatter": {
        "en": "How to read: each dot is a novel, placed by its year (across) and its "
        "amount of shame (up), coloured by group. The lines follow each "
        "group's typical level over time. Click a dot to read its passages; "
        "shift-click to add more.",
        "sl": "Kako brati: vsaka točka je roman, postavljen po letu (vodoravno) in "
        "količini sramu (navpično), obarvan po skupini. Črte sledijo običajni "
        "ravni vsake skupine skozi čas. Kliknite točko, da preberete odlomke; "
        "s Shift+klik jih dodate več.",
    },
    "time.read.groups": {
        "en": "How to read: each row is a group of the comparison (number of novels "
        "in brackets), each dot a novel, the dark bar the group's median. "
        "Groups with few novels can look different by chance. Click a dot to "
        "read its passages.",
        "sl": "Kako brati: vsaka vrstica je skupina primerjave (v oklepaju število "
        "romanov), vsaka točka roman, temna črtica mediana skupine. Skupine z "
        "malo romani so lahko drugačne po naključju. Kliknite točko za odlomke.",
    },
    "time.trend_too_few": {
        "en": "Too few novels for a moving average: it needs {n} novels within "
        "{window} years.",
        "sl": "Premalo romanov za drseče povprečje: potrebuje {n} romane v "
        "{window} letih.",
    },
    "time.top_shame_only": {
        "en": "This chart ranks the novels by their passages with shame only.",
        "sl": "Ta graf razvrsti romane le po odlomkih s sramom.",
    },
    "time.find.group": {
        "en": "**{group}** ({n} novels): median {median}; over time {trend} (ρ = "
        "{rho}).",
        "sl": "**{group}** (romanov: {n}): mediana {median}; skozi čas {trend} (ρ = "
        "{rho}).",
    },
    "time.find.rise": {
        "en": "it tends to rise",
        "sl": "se navadno zvišuje",
    },
    "time.find.fall": {
        "en": "it tends to fall",
        "sl": "se navadno znižuje",
    },
    "time.find.flat": {
        "en": "there is no clear trend",
        "sl": "ni jasnega trenda",
    },
    "time.find.ratio": {
        "en": "The median of **{a}** is {x}× that of **{b}**.",
        "sl": "Mediana skupine **{a}** je {x}-kratnik mediane skupine **{b}**.",
    },
    "time.find.top": {
        "en": "Most shame: *{novel}*, {value}.",
        "sl": "Največ sramu: *{novel}*, {value}.",
    },
    "time.methodology": {
        "en": "- **Unit:** the novel. *Share* = detected paragraphs ÷ all its "
        "paragraphs; *per 10,000 words* = detected paragraphs ÷ the word count "
        "in the corpus metadata × 10,000; *average shame score* = mean over "
        "all its paragraphs of the three ratings rescaled to 0–1 and averaged, "
        "× 100.\n"
        "- **Without shame:** paragraphs with a low rating on all three scales "
        "(0–1 ≤ 0.30, 0–10 ≤ 3, 0–100 ≤ 30).\n"
        "- **Trend lines:** LOESS (Vega-Lite, bandwidth 0.5) for groups of at "
        "least {trend} novels.\n"
        "- **Moving average:** unweighted mean of the novels published from y "
        "− {half} to y + {half} − 1, drawn where at least {n} novels fall in "
        "the window; band = mean ± 1.96 · SD / √n (a normal approximation, not "
        "a test).\n"
        "- **Box plots:** quartiles; whiskers reach the furthest novel within "
        "1.5 × IQR.\n"
        "- **Findings:** the median per group, and Spearman's rank correlation "
        "ρ of the measure with the year (|ρ| < {clear} counts as no clear "
        "trend). Descriptive only: no test, and no control for confounds such "
        "as the author.",
        "sl": "- **Enota:** roman. *Delež* = zaznani odstavki ÷ vsi odstavki romana; "
        "*na 10.000 besed* = zaznani odstavki ÷ število besed iz metapodatkov "
        "korpusa × 10.000; *povprečna ocena sramu* = povprečje vseh odstavkov "
        "romana, pri čemer je ocena odstavka povprečje treh ocen, preračunanih "
        "na 0–1, × 100.\n"
        "- **Brez sramu:** odstavki z nizko oceno na vseh treh lestvicah (0–1 "
        "≤ 0,30, 0–10 ≤ 3, 0–100 ≤ 30).\n"
        "- **Trendne črte:** LOESS (Vega-Lite, pasovna širina 0,5) za skupine "
        "z vsaj {trend} romani.\n"
        "- **Drseče povprečje:** netehtano povprečje romanov, izdanih od leta "
        "y − {half} do y + {half} − 1, prikazano, kjer je v oknu vsaj {n} "
        "romanov; pas = povprečje ± 1,96 · SD / √n (normalni približek, ne "
        "test).\n"
        "- **Škatle z ročaji:** kvartili; ročaja segata do najbolj oddaljenega "
        "romana znotraj 1,5 × IQR.\n"
        "- **Ugotovitve:** mediana posamezne skupine in Spearmanov koeficient "
        "ρ med mero in letom (|ρ| < {clear} pomeni, da jasnega trenda ni). Le "
        "opisno: brez testa in brez nadzora motečih dejavnikov, kot je avtor.",
    },
    "position.intro": {
        "en": "Does shame come early in a story, in the middle, or towards the end? "
        "Choose a chart; each looks at the question from a different side, "
        "split by the comparison chosen in the sidebar.",
        "sl": "Ali se sram pojavi zgodaj v zgodbi, v sredini ali proti koncu? "
        "Izberite graf; vsak pogleda na vprašanje z druge strani, razdeljen po "
        "primerjavi, izbrani v stranski vrstici.",
    },
    "position.x": {
        "en": "Position in the novel (%)",
        "sl": "Mesto v romanu (%)",
    },
    "position.x_down": {
        "en": "Position (beginning at the top)",
        "sl": "Mesto (začetek na vrhu)",
    },
    "position.y.concentration": {
        "en": "× the novel's average",
        "sl": "× povprečje romana",
    },
    "position.y.share": {
        "en": "Share of paragraphs (%)",
        "sl": "Delež odstavkov (%)",
    },
    "position.legend_share": {
        "en": "% about shame",
        "sl": "% o sramu",
    },
    "position.legend_relative": {
        "en": "× the column's average",
        "sl": "× povprečje stolpca",
    },
    "position.heatmap_shame_only": {
        "en": "The heatmap shows the passages with shame only.",
        "sl": "Toplotni zemljevid prikazuje le odlomke s sramom.",
    },
    "position.read.novels": {
        "en": "How to read: each row is a novel from beginning (left) to end "
        "(right); each mark is a paragraph about shame (grey marks: paragraphs "
        "without shame, when they are compared). The coloured square shows the "
        "group. “Smoothed” turns the marks into a band that is darker where "
        "they cluster. The line on the right is each novel's share of paragraphs "
        "about shame; with the novels in year order it shows how the amount "
        "rises and falls. Click to read the passages.",
        "sl": "Kako brati: vsaka vrstica je roman od začetka (levo) do konca "
        "(desno); vsaka oznaka je odstavek o sramu (sive oznake: odstavki brez "
        "sramu, kadar jih primerjamo). Barvni kvadratek kaže skupino. "
        "»Zglajeno« oznake spremeni v pas, ki je temnejši, kjer se zgostijo. "
        "Črta na desni je delež odstavkov o sramu v vsakem romanu; če so romani "
        "razvrščeni po letu izida, kaže, kako količina narašča in upada. "
        "Kliknite za odlomke.",
    },
    "position.read.heatmap": {
        "en": "How to read: each column is a novel (or a group of novels), read from "
        "top (beginning) to bottom (end), like pages laid side by side. Darker "
        "cells have more shame. When groups are compared, the coloured strip "
        "on top shows the group. Click a cell to read its passages.",
        "sl": "Kako brati: vsak stolpec je roman (ali skupina romanov), ki se bere "
        "od zgoraj (začetek) navzdol (konec), kot strani, položene druga ob "
        "drugo. Temnejše celice imajo več sramu. Kadar primerjamo skupine, "
        "barvni trak na vrhu kaže skupino. Kliknite celico za odlomke.",
    },
    "position.find.group": {
        "en": "**{group}:** most concentrated at {a}–{b} % of the novel ({peak}× the "
        "novel's average); the first fifth has {first}×, the last fifth "
        "{last}×.",
        "sl": "**{group}:** najbolj zgoščeno pri {a}–{b} % romana ({peak}× povprečje "
        "romana); prva petina ima {first}×, zadnja petina {last}×.",
    },
    "position.methodology": {
        "en": "- **Parts:** a paragraph's position is (i + 0.5) / N for paragraph i "
        "of N; positions are cut into {bins} equal parts of {part} %.\n"
        "- **Where shame concentrates:** per novel, the share of detected "
        "paragraphs in a part ÷ the novel's overall share, averaged over the "
        "novels with at least {min_tagged} counted paragraphs, so that every "
        "novel weighs the same; band = mean ± 1.96 · SE across novels.\n"
        "- **Share in each part:** pooled, i.e. detected ÷ all paragraphs "
        "summed over the novels, so long novels weigh more.\n"
        "- **Smoothing:** a centred moving average over three parts.\n"
        "- **Violins:** Gaussian kernel density of the positions (bandwidth "
        "{bw} percentage points), reflected at 0 and 100 % against edge bias, "
        "scaled so that an even spread is 1.\n"
        "- **Without shame:** paragraphs with a low rating on all three "
        "scales; in *Novel by novel* the length-matched comparison set of the "
        "Words and Style pages.\n"
        "- **Findings:** the part with the highest concentration, and the mean "
        "concentration of the first and last fifth. Descriptive only.",
        "sl": "- **Deli:** mesto odstavka i od N je (i + 0,5) / N; mesta so "
        "razdeljena na {bins} enakih delov po {part} %.\n"
        "- **Kje se sram zgosti:** za vsak roman delež zaznanih odstavkov v "
        "delu ÷ delež v celem romanu, povprečeno čez romane z vsaj "
        "{min_tagged} preštetimi odstavki, tako da vsak roman šteje enako; pas "
        "= povprečje ± 1,96 · SE čez romane.\n"
        "- **Delež v vsakem delu:** združeno, tj. zaznani ÷ vsi odstavki, "
        "sešteto čez romane, zato dolgi romani štejejo več.\n"
        "- **Glajenje:** centrirano drseče povprečje treh delov.\n"
        "- **Violine:** Gaussova jedrna gostota mest (pasovna širina {bw} "
        "odstotnih točk), zrcaljena pri 0 in 100 % proti pristranskosti na "
        "robovih, umerjena tako, da je enakomerna porazdelitev 1.\n"
        "- **Brez sramu:** odstavki z nizko oceno na vseh treh lestvicah; v "
        "pogledu *Roman za romanom* po dolžini usklajeni primerjalni nabor "
        "strani Besede in Slog.\n"
        "- **Ugotovitve:** del z največjo zgostitvijo ter povprečna zgostitev "
        "prve in zadnje petine. Le opisno.",
    },
    "words.intro": {
        "en": "Which words are used more often in passages about shame than in "
        "passages from the same novels that are not about shame? The lists are "
        "computed for the novels and the comparison chosen in the sidebar.",
        "sl": "Katere besede so v odlomkih o sramu pogostejše kot v odlomkih iz "
        "istih romanov, ki ne govorijo o sramu? Seznami so izračunani za "
        "romane in primerjavo, izbrane v stranski vrstici.",
    },
    "words.prelim": {
        "en": "Preliminary: the lists count word forms as they appear (*sram*, "
        "*sramu* and *sramota* separately) and all kinds of words. Names are "
        "removed because they are capitalized. A grammatical analysis will "
        "replace this.",
        "sl": "Predhodno: seznami štejejo besedne oblike, kot se pojavijo (*sram*, "
        "*sramu* in *sramota* posebej), in vse vrste besed. Imena so "
        "odstranjena, ker se pišejo z veliko začetnico. Nadomestila jih bo "
        "slovnična analiza.",
    },
    "words.type.map": {
        "en": "Map",
        "sl": "Zemljevid",
    },
    "words.shared": {
        "en": "Shared by the groups",
        "sl": "Skupne skupinam",
    },
    "words.map_needs_two": {
        "en": "The map compares two groups: under Compare in the sidebar, choose "
        "with and without shame, periods, author gender, two authors, or two "
        "novels.",
        "sl": "Zemljevid primerja dve skupini: v stranski vrstici pod Primerjaj "
        "izberite s sramom in brez njega, obdobji, spol avtorja, dva avtorja "
        "ali dva romana.",
    },
    "words.map.with": {
        "en": "Per 10,000 words, with shame",
        "sl": "Na 10.000 besed, s sramom",
    },
    "words.map.without": {
        "en": "Per 10,000 words, without shame",
        "sl": "Na 10.000 besed, brez sramu",
    },
    "words.map.ratio_in": {
        "en": "Times more frequent with shame: {group}",
        "sl": "Kolikokrat pogostejša ob sramu: {group}",
    },
    "words.dots.both": {
        "en": "With shame ÷ without (log scale)",
        "sl": "S sramom ÷ brez (log. lestvica)",
    },
    "words.col.belongs": {
        "en": "Typical of",
        "sl": "Značilna za",
    },
    "words.read.cloud_none": {
        "en": "How to read: the bigger the word, the more typical it is of passages "
        "with shame. Click a word to read passages that contain it.",
        "sl": "Kako brati: večja kot je beseda, bolj je značilna za odlomke s "
        "sramom. Kliknite besedo, da preberete odlomke z njo.",
    },
    "words.read.cloud_shame": {
        "en": "How to read: plum words are typical of passages with shame, grey "
        "words of passages without it; the bigger, the more typical. Click a "
        "word to read passages that contain it.",
        "sl": "Kako brati: vijoličaste besede so značilne za odlomke s sramom, sive "
        "za odlomke brez njega; večja kot je beseda, bolj je značilna. "
        "Kliknite besedo za odlomke z njo.",
    },
    "words.read.cloud_split": {
        "en": "How to read: the bigger the word, the more typical it is of shame in "
        "some group. Colour shows the group in which it is clearly more tied "
        "to shame: there its frequency ratio (with shame against without) is "
        "at least {factor} times that of every other group. Dark words are "
        "shared. Click a word to read passages that contain it.",
        "sl": "Kako brati: večja kot je beseda, bolj je v neki skupini značilna za "
        "sram. Barva kaže skupino, v kateri je izrazito bolj povezana s "
        "sramom: tam je njeno razmerje pogostnosti (s sramom proti brez) vsaj "
        "{factor}-krat večje kot v vsaki drugi skupini. Temne besede so "
        "skupne. Kliknite besedo za odlomke.",
    },
    "words.hidden_labels": {
        "en": "Labels hidden so that they do not overlap: {n}. Point at a dot to see "
        "its word.",
        "sl": "Skritih oznak, da se ne prekrivajo: {n}. Pokažite na točko, da vidite "
        "besedo.",
    },
    "words.read.map_split": {
        "en": "How to read: each word is placed by how many times more frequent it "
        "is in passages with shame, in one group (across) and in the other "
        "(up). Words on the diagonal are equally tied to shame in both; words "
        "below it lean to the first group, words above it to the second. Click "
        "a word to read passages.",
        "sl": "Kako brati: vsaka beseda je postavljena glede na to, kolikokrat "
        "pogostejša je v odlomkih s sramom v eni skupini (vodoravno) in v "
        "drugi (navpično). Besede na diagonali so s sramom enako povezane v "
        "obeh; besede pod njo se nagibajo k prvi skupini, nad njo k drugi. "
        "Kliknite besedo za odlomke.",
    },
    "words.read.map_shame": {
        "en": "How to read: each word is placed by how often it appears in passages "
        "with shame (across) and without (up). Words below the diagonal are "
        "more frequent with shame, words above it without. Click a word to "
        "read passages.",
        "sl": "Kako brati: vsaka beseda je postavljena glede na to, kako pogosto se "
        "pojavi v odlomkih s sramom (vodoravno) in brez njega (navpično). "
        "Besede pod diagonalo so pogostejše ob sramu, nad njo brez njega. "
        "Kliknite besedo za odlomke.",
    },
    "words.read.dots": {
        "en": "How to read: words are listed from most to least typical; the dot "
        "shows how many times more frequent a word is in passages with shame "
        "than without. Click a word to read passages.",
        "sl": "Kako brati: besede so razvrščene od najbolj do najmanj značilne; "
        "točka kaže, kolikokrat pogostejša je beseda v odlomkih s sramom kot "
        "brez njega. Kliknite besedo za odlomke.",
    },
    "words.read.dots_shame": {
        "en": "How to read: right of the line at 1, words more frequent in passages "
        "with shame; left of it, words more frequent without (0.5 = half as "
        "frequent with shame). Click a word to read passages.",
        "sl": "Kako brati: desno od črte pri 1 so besede, pogostejše v odlomkih s "
        "sramom, levo besede, pogostejše brez njega (0,5 = ob sramu pol manj "
        "pogosta). Kliknite besedo za odlomke.",
    },
    "words.read.dots_split": {
        "en": "How to read: the dark dot shows how many times more frequent a word "
        "is with shame in all compared novels together, the coloured dots the "
        "same within each group. Click a word to read passages.",
        "sl": "Kako brati: temna točka kaže, kolikokrat pogostejša je beseda ob "
        "sramu v vseh primerjanih romanih skupaj, barvne točke isto znotraj "
        "posamezne skupine. Kliknite besedo za odlomke.",
    },
    "words.find.shame": {
        "en": "Most typical of passages with shame: {words}.",
        "sl": "Najbolj značilne za odlomke s sramom: {words}.",
    },
    "words.find.without": {
        "en": "Most typical of passages without shame: {words}.",
        "sl": "Najbolj značilne za odlomke brez sramu: {words}.",
    },
    "words.find.group": {
        "en": "Tied to shame mainly in **{group}**: {words}.",
        "sl": "S sramom povezane predvsem v skupini **{group}**: {words}.",
    },
    "words.find.common": {
        "en": "Tied to shame in every group: {words}.",
        "sl": "S sramom povezane v vseh skupinah: {words}.",
    },
    "words.methodology": {
        "en": "- **Words:** lower-cased runs of letters; no lemmas or parts of "
        "speech yet. Names are removed: words capitalized in more than half of "
        "their uses in the corpus that do not start a sentence.\n"
        "- **Sets:** the detected paragraphs of the compared novels against "
        "their comparison paragraphs (one low-score partner per detected "
        "paragraph, from the same novel, within a factor of 2 in length).\n"
        "- **Measure:** weighted log-odds ratio δ with an informative "
        "Dirichlet prior (Monroe, Colaresi and Quinn 2008); the prior is the "
        "corpus word frequency, scaled to the size of the two sets. Words are "
        "ranked by z = δ / SE(δ). *Times more frequent* is the plain ratio of "
        "the two frequencies, with half a count added to each side so that a "
        "word missing on one side stays finite; e^δ is not used for it, "
        "because the prior pulls it towards 1, the more so the rarer the "
        "word.\n"
        "- **Filters:** at least {min_count} occurrences in the two sets; a "
        "typical word must recur on its side in at least {novels} novels by "
        "{authors} authors (the rule is relaxed for small groups).\n"
        "- **Groups:** each group is computed on its own novels. A word "
        "belongs to a group when its ratio there is at least {factor}× that of "
        "every other group; z is not compared across groups, because it grows "
        "with the amount of text.\n"
        "- Thousands of words are compared, so the lists are descriptive: z > "
        "3 is not a corrected significance level.",
        "sl": "- **Besede:** zaporedja črk z malimi črkami; brez lem in besednih "
        "vrst. Imena so odstranjena: besede, ki so z veliko začetnico zapisane "
        "v več kot polovici pojavitev v korpusu, ki niso na začetku povedi.\n"
        "- **Nabora:** zaznani odstavki primerjanih romanov proti njihovim "
        "primerjalnim odstavkom (en par z nizko oceno na zaznani odstavek, iz "
        "istega romana, do 2-krat daljši ali krajši).\n"
        "- **Mera:** uteženo razmerje logaritemskih obetov δ z informativno "
        "Dirichletovo apriorno porazdelitvijo (Monroe, Colaresi in Quinn "
        "2008); apriorna je pogostnost besede v korpusu, umerjena na velikost "
        "obeh naborov. Besede so razvrščene po z = δ / SE(δ). *Kolikokrat "
        "pogostejša* je navadno razmerje obeh pogostnosti, pri čemer je vsaki "
        "strani dodana polovica pojavitve, da beseda, ki na eni strani manjka, "
        "ostane končna; e^δ za to ni uporabljen, ker ga apriorna porazdelitev "
        "vleče proti 1, tem bolj, čim redkejša je beseda.\n"
        "- **Filtri:** vsaj {min_count} pojavitev v obeh naborih; značilna "
        "beseda se mora na svoji strani ponoviti v vsaj {novels} romanih "
        "{authors} avtorjev (za majhne skupine je pravilo blažje).\n"
        "- **Skupine:** vsaka skupina je izračunana na svojih romanih. Beseda "
        "pripada skupini, če je njeno razmerje tam vsaj {factor}-krat večje kot v "
        "vsaki drugi skupini; z med skupinami ni primerjan, ker raste s "
        "količino besedila.\n"
        "- Primerjamo na tisoče besed, zato so seznami opisni: z > 3 ni "
        "popravljena raven statistične značilnosti.",
    },
    "style.intro": {
        "en": "Are passages about shame written differently from other passages in "
        "the same novels: shorter sentences, more questions, more "
        "exclamations, more repetition? Each measure is compared within each "
        "novel, then summed up over the novels of each group in the sidebar's "
        "comparison.",
        "sl": "Ali so odlomki o sramu napisani drugače kot drugi odlomki v istih "
        "romanih: krajše povedi, več vprašanj, več vzklikov, več ponavljanja? "
        "Vsaka mera je primerjana znotraj vsakega romana in nato povzeta čez "
        "romane vsake skupine iz primerjave v stranski vrstici.",
    },
    "style.x": {
        "en": "Index (without shame = 100)",
        "sl": "Indeks (brez sramu = 100)",
    },
    "style.read.raw": {
        "en": "How to read: one small chart per measure, each with its own scale; "
        "plum bars are passages with shame, grey bars passages without, in the "
        "average novel of each group.",
        "sl": "Kako brati: za vsako mero majhen graf z lastno lestvico; vijoličasti "
        "stolpci so odlomki s sramom, sivi odlomki brez njega, v povprečnem "
        "romanu vsake skupine.",
    },
    "style.read.time": {
        "en": "How to read: the line is the average of the novels published within "
        "{window} years around each year (only where at least {n} novels are "
        "available); plum is the passages with shame, grey the matched passages "
        "without, from the same novels. The shaded band shows how uncertain the "
        "average is. Click the line to read the passages highest on the measure in "
        "the novels behind it.",
        "sl": "Kako brati: črta je povprečje romanov, izdanih v {window} letih okoli "
        "vsakega leta (le kjer je na voljo vsaj {n} romanov); vijoličasta so "
        "odlomki s sramom, siva usklajeni odlomki brez sramu iz istih romanov. "
        "Senčeni pas kaže, kako negotovo je povprečje. Kliknite črto za odlomke z "
        "najvišjo vrednostjo mere v romanih za njo.",
    },
    "style.read.time_split": {
        "en": "How to read: the line is the average of the novels published within "
        "{window} years around each year (only where at least {n} novels are "
        "available); the colour is the group, solid lines the passages with "
        "shame, dashed lines the matched passages without. The shaded band shows "
        "how uncertain the average with shame is. Click the line to read the passages "
        "highest on the measure in the novels behind it.",
        "sl": "Kako brati: črta je povprečje romanov, izdanih v {window} letih okoli "
        "vsakega leta (le kjer je na voljo vsaj {n} romanov); barva je skupina, "
        "polna črta odlomki s sramom, črtkana usklajeni odlomki brez sramu. "
        "Senčeni pas kaže, kako negotovo je povprečje s sramom. Kliknite črto "
        "za odlomke z najvišjo vrednostjo mere v romanih za njo.",
    },
    "style.shame_mode": {
        "en": "Every chart on this page compares passages with and without shame, "
        "so this comparison shows all the selected novels together.",
        "sl": "Vsak graf na tej strani primerja odlomke s sramom in brez njega, "
        "zato ta primerjava prikaže vse izbrane romane skupaj.",
    },
    "style.too_few": {
        "en": "Too few novels to compare: {groups}. A group needs at least {n} "
        "novels with {p} or more paragraphs with and without shame.",
        "sl": "Premalo romanov za primerjavo: {groups}. Skupina potrebuje vsaj {n} "
        "romane z vsaj {p} odstavki s sramom in brez njega.",
    },
    "style.find.group": {
        "en": "**{group}:** {items}.",
        "sl": "**{group}:** {items}.",
    },
    "style.find.more": {
        "en": "{feature} {x}× as frequent with shame",
        "sl": "{feature}: ob sramu {x}-krat pogostejši",
    },
    "style.find.less": {
        "en": "{feature} {pct} % lower with shame",
        "sl": "{feature}: ob sramu {pct} % nižje",
    },
    "style.find.time": {
        "en": "**{group}:** over time {trend} ({feature} with shame, ρ = {rho}).",
        "sl": "**{group}:** skozi čas {trend} ({feature} s sramom, ρ = {rho}).",
    },
    "style.find.rise": {
        "en": "the value tends to rise",
        "sl": "vrednost navadno narašča",
    },
    "style.find.fall": {
        "en": "the value tends to fall",
        "sl": "vrednost navadno pada",
    },
    "style.find.flat": {
        "en": "there is no clear trend",
        "sl": "ni jasnega trenda",
    },
    "style.find.none": {
        "en": "**{group}:** no clear difference.",
        "sl": "**{group}:** ni jasne razlike.",
    },
    "style.methodology": {
        "en": "- **Measures** per paragraph: words per sentence (rule-based sentence "
        "split); words of three or more letters repeated within the previous "
        "10 words; ! ? ; , … and dashes per 1,000 characters. MATTR (window of "
        "100 words) is computed on all the words of a novel's set.\n"
        "- **Pooling:** counts are summed per novel and set before rates are "
        "formed, so each novel gives one pair, with against without shame. "
        "Novels need at least {min_p} paragraphs in each set; a group needs at "
        "least {min_n} such novels.\n"
        "- **Index:** 100 × (1 + mean per-novel difference ÷ mean value "
        "without shame); the 95 % interval comes from {boot} bootstrap "
        "resamples of novels.\n"
        "- **Test:** a two-sided sign-flip permutation test of the mean "
        "per-novel difference ({perms} permutations), with Holm's correction "
        "across the {n_features} measures of each group. Filled dots: "
        "Holm-adjusted p < 0.05.\n"
        "- **Dialogue:** paragraphs with quotation marks (» « „ “) or starting "
        "with a speech dash.\n"
        "- **Over time:** the per-novel values of each set, averaged over the "
        "novels published within {window} years around each year; years with "
        "fewer than {min_window} novels are left out. The band is a 95 % normal "
        "interval over novels. The trend in the findings is Spearman's ρ "
        "between the year and the value with shame; |ρ| < {clear} counts as no "
        "clear trend.",
        "sl": "- **Mere** na odstavek: besede na poved (delitev na povedi s "
        "pravili); besede s tremi ali več črkami, ponovljene med 10 besedami "
        "pred njimi; ! ? ; , … in pomišljaji na 1.000 znakov. MATTR (okno 100 "
        "besed) je izračunan na vseh besedah nabora posameznega romana.\n"
        "- **Združevanje:** števila so seštevana po romanu in naboru, preden "
        "so izračunani deleži, zato vsak roman da en par, s sramom proti brez. "
        "Roman potrebuje vsaj {min_p} odstavkov v vsakem naboru, skupina vsaj "
        "{min_n} take romane.\n"
        "- **Indeks:** 100 × (1 + povprečna razlika po romanih ÷ povprečna "
        "vrednost brez sramu); 95-odstotni interval izhaja iz {boot} ponovnih "
        "vzorčenj romanov (bootstrap).\n"
        "- **Test:** dvostranski permutacijski test z naključnim obračanjem "
        "predznakov povprečne razlike po romanih ({perms} permutacij), s "
        "Holmovim popravkom čez {n_features} mer vsake skupine. Polne točke: p "
        "po Holmu < 0,05.\n"
        "- **Dialog:** odstavki z narekovaji (» « „ “) ali s pomišljajem pred "
        "govorom na začetku.\n"
        "- **Skozi čas:** vrednosti posameznih romanov v vsakem naboru, "
        "povprečene čez romane, izdane v {window} letih okoli vsakega leta; leta "
        "z manj kot {min_window} romani so izpuščena. Pas je 95-odstotni "
        "normalni interval čez romane. Trend v ugotovitvah je Spearmanov ρ med "
        "letom in vrednostjo s sramom; |ρ| < {clear} šteje kot brez jasnega "
        "trenda.",
    },
    # Method (APP-04)
    "method.title": {"en": "Method and caveats", "sl": "Metodologija in omejitve"},
}


def lang() -> str:
    return st.session_state.get("lang") or "en"


def t(key: str, **values) -> str:
    text = STRINGS[key][lang()]
    return text.format(**values) if values else text


def label(prefix: str, value: str) -> str:
    """Translated label of a data value, e.g. label("period", "Realism")."""
    return t(f"{prefix}.{value}")


def labels(prefix: str, values) -> dict[str, str]:
    return {v: label(prefix, v) for v in values}


def num(value: float, digits: int = 1) -> str:
    """A number in the reader's language: 1,234.5 in English, 1.234,5 in Slovene."""
    text = f"{value:,.{digits}f}"
    if lang() == "sl":
        text = text.replace(",", " ").replace(".", ",").replace(" ", ".")
    return text
