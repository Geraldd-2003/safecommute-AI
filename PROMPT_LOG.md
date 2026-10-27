# Prompt log · SafeCommute AI (Group 28)

The assignment asks us to report every prompt used with AI tools, and where and how its output was used.
Prompts are copied **verbatim** (original language, typos included), followed by an English translation where needed.

> Items marked **[TO COMPLETE]** must be filled in by the teammate concerned before submission.

## Summary

| # | Who | Tool | Date | Used for | Files affected |
|---|---|---|---|---|---|
| 1 | [TO COMPLETE: teammate] | [TO COMPLETE: e.g. ChatGPT / Gemini, model] | [TO COMPLETE] | Project concept, matching rules, first Python engine, simulated datasets, team brief | `data/train_data.xlsx`, rules in `engine.py` |
| 2 | Gérald Veuillot | Claude (Anthropic), Claude Opus 5.5, claude.ai | 26 Oct 2026, 19:29 | Review of the first engine, bug fix, first runnable version | superseded by #3 |
| 3 | Gérald Veuillot | Claude (Anthropic), Claude Opus 5.5, claude.ai | 26 Oct 2026, 19:47 | Streamlit app built on the team's data, women-only design, test set, tests | `engine.py`, `app.py`, `prepare_data.py`, `test_engine.py`, `data/` |
| 4 | Gérald Veuillot | Claude (Anthropic), Claude Opus 5.5, claude.ai | 26 Oct 2026, 19:57 | Interactive map, calibration tab, About tab, documentation for evaluation | `app.py`, `engine.py`, `README.md`, `USER_GUIDE.md`, this file |

---

## Prompt 1 · Concept, rules and data

- **Who / tool**: [TO COMPLETE]
- **Prompt(s)**:
  ```
  [TO COMPLETE: paste the exact prompt(s) used]
  ```
- **What the AI produced**: the "SafeCommute AI" concept (safety + sustainability), the 7 matching rules (same slot, max 4 people, origins ≤ 1 km, destinations ≤ 3 km, closest first, one group per slot), a first Python engine using the Haversine formula, two simulated datasets of 200 commuters (Cergy + Paris), three design questions (women-only filter, real walking distance, meeting point) and a team brief.
- **How we used it**: the rules and `train_data.xlsx` are kept as the basis of the app; the file is in `data/` unchanged. The first engine was replaced (see #2). The `test_data.xlsx` from that session was not shared, so a new test night was generated in #3.
- **Human checks**: [TO COMPLETE: e.g. reviewed the rules, chose thresholds, checked places in Cergy]

---

## Prompt 2 · Review and first runnable version

- **Prompt** (attached: the full text output of Prompt 1):
  ```
  tu peux t'occuper de ca dis moi si t'as besoin de precisions
  ```
  *Translation: "can you take care of this, tell me if you need details"*
- **What the AI produced**: rebuilt and ran the engine (the Excel files mentioned in Prompt 1 were not attached). It found a bug: the first engine picked people in file order, so the "closest origins first" rule was not actually applied. Fixed by sorting all valid pairs by distance before grouping. Also flagged an inconsistency in the brief (">40 records in Cergy" vs. "45%").
- **How we used it**: the corrected matching logic (closest pairs first, women-only option, rule re-check of every group) was carried into `engine.py`. The datasets from this step were not used in the final app.

---

## Prompt 3 · Python app on the team's data

- **Prompt** (attached: Prompt 1 output again and `train_data.xlsx`):
  ```
  il faut faire un app codé en phyton creer la. voici de la data. le filtre femme est selon ce que tu penses etre le plus adapté. Livrable c'est en premier lieu un code phyton et une app fonctionnelle. Aide toi de ca fait par ma collegue en PJ
  ```
  *Translation: "we need an app coded in Python, create it. Here is some data. The women filter is whatever you think is most suitable. The deliverable is first of all Python code and a working app. Use what my colleague made, attached."*
- **What the AI produced**: `engine.py` (matching, explanations for unmatched people, Excel export), a first Streamlit app, `prepare_data.py` (simulated gender from first names, ~35% of women opting in, a test night from the same distributions, fixed seeds), `test_engine.py` (10 rule checks).
- **Design decision proposed by the AI and kept**: women-only matching is **opt-in per user**, not imposed on all women, because a mandatory filter shrinks everyone's pool and leaves more women alone. Measured cost on the demo data: 26.0% matched without the rule, 21.5% with it.
- **Finding reported by the AI**: only 26% of commuters are matched on the team's data because destinations were drawn at random (two thirds more than 10 km from the start).

---

## Prompt 4 · Interactive map and evaluation material

- **Prompt**:
  ```
  donne moi le code phyton. et aussi fais une app interactive avec une  arte et reprends aussi ce qu'as dit mon collegue ses datas etc reprends l'ensemble dont ca AAA Group Assignment: Summary (Group 28) [...] ( considere simplement ce qui est relatif a ala creation de l'app et l'utilisation pour qu'ils l'evaluent)
  ```
  *(The `[...]` is the assignment summary pasted in full: goal, requirements, tools, deliverables, grading, deadlines.)*
  *Translation: "give me the Python code. Also make an interactive app with a map, and take up what my colleague said, her data etc., take everything, including this [assignment summary] (only consider what relates to building and using the app, so that they can evaluate it)."*
- **What the AI produced**:
  - Map on OpenStreetMap (folium): click to set start or destination, address search (Nominatim), live group update, meeting point, map of all groups on the Dashboard.
  - *Calibration* tab: thresholds chosen on train and checked on test, with coverage vs. destination spread.
  - *About* tab: problem, value proposition, answers to the three design questions from Prompt 1, AI concepts, credits.
  - `README.md`, `USER_GUIDE.md`, this prompt log, pinned `requirements.txt`, launchers.
  - Verification: automatic tests, the app driven end-to-end in a headless browser, and a clean reinstall from `requirements.txt` reproducing the same files and figures.

---

## Where the team's own work sits

[TO COMPLETE before submission — for example: choice of the problem and the Cergy focus, the matching rules and thresholds, review of the AI output, testing the app on each teammate's computer, demo video script, recording and editing.]
