# SafeCommute AI

**Never walk home alone after a late train.**
Group 28 · Audrey Laurent, Augustine Nay, Diego Alonso Lopez Romero, Gérald Veuillot

SafeCommute AI groups 2 to 4 people who leave the same metro/RER station at the same time late at night and head the same way, and gives them a meeting point at the exit. It is a local web app written in Python with Streamlit.

## Run it locally

You need **Python 3.11 or newer** ([python.org](https://www.python.org/downloads/); on Windows tick "Add Python to PATH").

**Windows, one click:** double-click `run_app.bat`. The first start creates a virtual environment and installs the packages (1-2 minutes).

**macOS / Linux:** `bash run_app.sh`

**By hand (any system):**

```bash
python -m venv .venv
# Windows:        .venv\Scripts\activate
# macOS / Linux:  source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at **http://localhost:8501** (usage statistics are off). Stop it with `Ctrl + C` in the terminal.

It can also be deployed for free on [Streamlit Community Cloud](https://share.streamlit.io): push this folder to a GitHub repository, then choose *Create app*, the repository and `app.py` as the main file.

Internet is used only for the map background (OpenStreetMap) and the address search. Without it, everything else works: pick places from the lists.

## Tests

```bash
python -m pytest                 # all 21 tests
python -m pytest test_engine.py  # 10 checks of the matching rules
python -m pytest test_app.py     # 11 interface checks (each page renders, main flows work)
```

## Pages

| Page | What you can do |
|---|---|
| **Home** | What the app does, tonight's figures, how it works, the rules in plain words. |
| **Find my group** | Set your start and destination (list, address search or click on the map), your slot and, for women, the optional women-only preference. Your group, meeting point and walk update live. If nobody fits, the app says why and lists the slots where you would have company. |
| **Dashboard** | Operator view: KPIs, matched vs. alone per slot, map of all groups in a slot, group list, reasons people were not matched, Excel export. |
| **Calibration** | Limits chosen on the train night and checked on the test night, with the coverage vs. safety trade-off as two heatmaps (current setting outlined). |
| **Data** | Dataset preview with a row filter, commuters per place. |
| **About** | Problem, value, design choices, AI concepts, credits, limits. |

The sidebar switches dataset (or uploads your own Excel/CSV) and changes every rule live, on every page.

## Matching rules

1. Same time slot only; groups of 2 to 4 people.
2. Two people match if they start ≤ 1 km apart; a 3rd or 4th joins if they start ≤ 1 km from the middle of the group.
3. Every member's destination is ≤ 3 km from every other member's.
4. Closest pairs first, one group per person per slot.
5. **Women-only, opt-in**: a woman who ticks it is only grouped with declared women; people who don't declare a gender are never put in a women-only group.
6. Meeting point: the start of the member closest to the middle of the group, so always a real station or campus exit.

Every group is re-checked against these rules before it is shown (`engine.verify_group`).

| Dataset (rules 1 km / 3 km) | Groups | Commuters matched |
|---|---|---|
| Train night, team's original file | 23 | 52 / 200 (26.0%) |
| Train night + simulated gender, women-only on | 20 | 43 / 200 (21.5%) |
| Test night, women-only on | 23 | 51 / 200 (25.5%) |

Coverage is low because the team's destinations were drawn at random among 12 towns: most unmatched people have company at the station but are heading elsewhere. The Calibration page shows the trade-off of loosening the limits.

## Project structure

```
SafeCommute_AI/
├── app.py                Entry point: navigation, shared sidebar, runs the matching once
├── views/                One file per page (home, find, dashboard, calibration, data, about)
├── ui/
│   ├── state.py          Data loading, sidebar settings, cached matching
│   ├── style.py          Design tokens and global CSS
│   ├── components.py     Page header, steps, result cards, legends
│   └── maps.py           Folium maps (OpenStreetMap, night filter)
├── engine.py             Matching engine, no UI code (python engine.py data/train_data.xlsx)
├── prepare_data.py       Rebuilds the demo and test files from the team's train file
├── test_engine.py        10 rule checks
├── test_app.py           11 interface checks
├── data/                 train_data.xlsx, train_data_demo.xlsx, test_data.xlsx
├── assets/logo.svg
├── .streamlit/config.toml  Theme + local-only server
├── requirements.txt  run_app.bat  run_app.sh
└── README.md  USER_GUIDE.md  PROMPT_LOG.md
```

## Design

The interface follows a design system generated with the **ui-ux-pro-max** skill ("data-dense dashboard" style, navy/blue data colours with an amber accent, Fira Sans + Fira Code), adapted to a dark night theme for a product used after 10 pm:

- Colour tokens in `ui/style.py` and `.streamlit/config.toml`; amber marks meeting points everywhere.
- Text contrast ≥ 4.5:1 on the dark background, visible keyboard focus, `prefers-reduced-motion` respected.
- Material icons instead of emojis; every map has a written legend, so meaning never relies on colour alone.
- Only first name + initial of other commuters is ever shown.

## Credits

Streamlit (Apache 2.0), pandas (BSD-3), openpyxl (MIT), folium / Leaflet (MIT / BSD-2), streamlit-folium (MIT), geopy (MIT), Altair (BSD-3). Map data © OpenStreetMap contributors (ODbL); address search with Nominatim (max 1 request/second). Fonts: Fira Sans and Fira Code (SIL Open Font License). Commuter data simulated by the team; no real personal data. AI assistants used: see [PROMPT_LOG.md](PROMPT_LOG.md).
