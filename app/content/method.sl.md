## Kako so bili odlomki najdeni

Korpus obsega **{n_novels} slovenskih romanov** ({n_authors} avtorjev in avtoric), izdanih v letih {first}–{last}, razdeljenih na **{n_paragraphs} odstavkov**. Jezikovni model (Mistral 7B Instruct, lokalno, pri temperaturi 0) je vsak odstavek trikrat ocenil, kako močno je povezan s sramom: na lestvicah 0–1, 0–10 in 0–100. Odstavek je *zaznan*, če so visoke vse tri ocene:

| Nabor | Pravilo | Odstavki | Natančnost | Priklic | F1 |
|---|---|---|---|---|---|
| **Jedro** | zgornji 1 %: 0–1 ≥ {core_0_1}, 0–10 ≥ {core_0_10}, 0–100 ≥ {core_0_100} | {n_core} | 77,4 % | 78,6 % | 78,0 % |
| **Širši nabor** (privzeto) | zgornjih 5 %: 0–1 ≥ {broad_0_1}, 0–10 ≥ {broad_0_10}, 0–100 ≥ {broad_0_100} | {n_broad} | 69,5 % | 81,3 % | 74,9 % |

Natančnost, priklic in F1 izhajajo iz zlatega standarda, ki so ga označili strokovnjaki, uteženo po stratumih kot v članku. Jedro je pravilo iz članka.

Aplikacija namesto treh ocen prikaže eno **oceno sramu** na odstavek: vsako oceno, preračunano na 0–100, nato povprečeno. Pove, kako prepričan je model, da odstavek govori o sramu, ne pa, kako močan je sram.

## Odlomki

Vsak zaznani odstavek je prikazan s {context} odstavkoma pred njim in za njim iz istega romana. Odlomki, ki se prekrivajo, so združeni, zato ima lahko en odlomek več zaznanih odstavkov. Dolgi odstavki so za prikaz skrajšani. Celotni romani niso nikoli prikazani.

Zelo dolgi odstavki ({n_over_context}, daljši od {over_context_chars} znakov) niso šli v kontekstno okno modela (4.096 žetonov), zato je model videl le njihov konec. V bralniku so označeni.

## Primerjalni nabor

Pogleda *Besede* in *Slog* primerjata zaznane odlomke z odstavki, ki imajo **nizke ocene na vseh treh lestvicah** (0–1 ≤ {low_0_1}, 0–10 ≤ {low_0_10}, 0–100 ≤ {low_0_100}; odstavkov: {n_low}). Vsak odstavek širšega nabora dobi en tak odstavek **iz istega romana in podobne dolžine** (največ {max_length_ratio:g}-krat daljši ali krajši), ki je od vsakega zaznanega odstavka oddaljen vsaj tri odstavke. Par je našlo {n_matched} od {n_broad} odstavkov širšega nabora (romanov: {n_novels_with_pairs}); dolgih odstavkov z nizko oceno je malo, zato najdaljši zaznani odstavki para pogosto nimajo.

Primerjalni nabor ni »vsi drugi odstavki«: ti še vedno vsebujejo večino sramu v korpusu. Ta opredelitev nizke ocene je **začasna** in jo moramo še uskladiti.

Če je pod *Primerjaj* izbrano *s sramom in brez njega*, pogleda *Skozi čas* in *Znotraj romana* štejeta vse odstavke z nizko oceno, saj sprašujeta, koliko in kje; *Besede* in *Slog* ohranita po dolžini usklajeni primerjalni nabor.

## Česa aplikacija ne more pokazati

- **Zaznani sram ni ves sram.** Po oceni v članku model najde največ približno 25 % odstavkov v korpusu, povezanih s sramom. Noben pogled ne more pokazati, da sramu nekje ni.
- **Ocene niso intenzivnost.** Merijo, kako močno je odstavek povezan s sramom, in imajo le nekaj različnih vrednosti. Kjer jih aplikacija povpreči, povpreči to povezanost.
- **Veliko razčlemb na majhnih podatkih da naključne vzorce.** Pogled *Slog* označi, katere razlike prestanejo test s popravkom za večkratne primerjave. Vse drugo je opisno.
- **Moteči dejavniki:** Cankar je napisal 32 od 67 modernističnih romanov; avtorice so napisale le 31 romanov; realizem in modernizem se časovno prekrivata; pred letom 1870 je izšlo malo romanov; dolžina odstavkov se zelo razlikuje; dialog in pripoved se slogovno razlikujeta.
- **Seznami besed so predhodni.** Do oblikoskladenjskega označevanja uporabljajo besedne oblike, ne leme, in vse besedne vrste.

## Opombe o podatkih

- Obdobja in spol so prevzeti iz metapodatkov korpusa, kot so: realizem {n_realism}, modernizem {n_modernism}, neznano {n_period_unknown} romanov. Članek šteje 232 realističnih romanov in 6 romanov neznanega obdobja; roman, ki se razlikuje, tu ni prerazporejen.
- Vsaka številka v aplikaciji je ponovno izračunana iz dveh datotek, označenega korpusa in njegovih metapodatkov, s podatkovnim cevovodom projekta.
