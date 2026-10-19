# Algerian Darija — rules for every Arabic word Claude writes or corrects (wailzenz-video-dz)

Algerian creators speak mostly **Darija (الدارجة الجزائرية)**, sometimes with Standard Arabic (فصحى) words,
and drop in **French or English** terms to teach, highlight, or name something technical.
These rules override the Gulf/Kuwaiti wording inside the original skill text.

## Defaults (a creator can change them — ask on their first video, then follow their answer)

| Topic | Default |
|---|---|
| French/English words in captions | Latin letters, followed by an Arabic gloss in quotes: «هادي حاجة normal "عادية"» · «Claude Code "كلود كود"». In `fixes.json`: `"gloss": {"normal": "عادية", "Claude Code": "كلود كود"}`. Terms are highlighted automatically (`"hot_latin": false` to stop). `"gloss_quotes": "()"` switches to parentheses. `02_captions.py` lists any Latin term you forgot to gloss. |
| Transcription engine | `--engine auto`: whisper.cpp large-v3 on a Mac, openai-whisper large-v3 elsewhere. On a new speaker's first video run `--engine compare` (adds the Algerian Hadra model), keep the transcript that needed fewer fixes, and save it: `02a_transcribe_dz.py --save-default cpp|hadra|whisper`. |
| Digits | Western (1 2 3) — the hook checker enforces it. |

### Writing a good gloss

- The gloss is the meaning in plain Arabic the viewer understands — Darija or simple فصحى, whichever is clearer: «algorithme "خوارزمية"», «feedback "رأي"», «prompt "الأمر"».
- Brand and product names get their Arabic pronunciation, not a translation: «Claude Code "كلود كود"», «TikTok "تيك توك"».
- One to three words. If no short gloss exists, ask the user.

## Correcting the transcript

- Keep the user's own words and word order. Never rewrite Darija into Standard Arabic (فصحى), and never "Gulf-ify" it. When the user deliberately says a فصحى word, keep it as فصحى too.
- French/English terms: Whisper often writes them in Arabic letters («كلاد كود») — restore the Latin spelling («Claude Code») and add its gloss.
- Whisper tends to: turn Darija into فصحى (كيفاش → كيف), split or merge words (ماكانش → ما كان ش), and mangle French words into nonsense Arabic. Fix those.
- Word count per sentence must still equal Whisper's count (02_captions.py rule). Use the hallucination escape (whole sentence as a string) when Whisper invented text.
- Don't know a word, a name or a brand? **Ask the creator** — never guess.

## Spelling conventions (most common on Algerian social media)

| Meaning | Write | Not |
|---|---|---|
| what / question particle | واش | شنو، وش، ايش، شو |
| how | كيفاش | شلون، ازاي |
| why | علاش | ليش، ليه |
| who / when / where from | شكون · وقتاش · منين | منو |
| how much | شحال / قداش | شكثر |
| now | درك | الحين، دلوقتي |
| a lot / very | بزاف | وايد، كتير، جدا |
| a little | شوية | |
| only | برك | بس، فقط |
| but | بصح | بس، لكن |
| not | ماشي | مو، مب، ليس |
| there is / isn't | كاين / ماكانش | |
| want | حاب / حابة · نحب | أبي، تبي، بدي |
| in order to | باش | عشان |
| all | قاع | |
| good / bad | مليح / خايب | زين |
| like this | هكا | جذي، هيك |
| this (m / f / pl) | هذا / هادي / هادو | ده، دي |
| of | تاع / نتاع | |
| I am / you are | راني / راك | |

Grammar markers to keep: negation ما…ش (مانيش، ماتديرش)، 1st person ن (نروح، نقول)، plural و (نروحو، تديرو)، future رايح/راح.

## Hooks, covers and CTAs

- 3–8 words, Western digits (1 2 3), no emoji (the hook checker enforces this; it runs with `DZ_DIALECT=dz`, which `setup/env.sh` sets; `DZ_DIALECT=kw` restores the original Kuwaiti rules).
- Example hooks: «علاش 90% يغلطو في هادي؟» · «زوج حوايج لازم تعرفهم قبل ما تبدا» · «هادي هي الغلطة اللي خسّرتني بزاف».
- Example CTAs: «تابعني باش مايفوتكش الجديد» · «قولّي في الكومنتار واش رايك».
- Map move (moves.js #77) defaults to the title «من الكويت للعالم» — always pass the creator's own title (e.g. «من الجزاير للعالم») or `null`.
