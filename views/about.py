"""About: problem, value, design choices, AI concepts, credits."""

import streamlit as st

from ui import components as C

C.page_header("About SafeCommute AI", "Group 28 · Audrey Laurent, Augustine Nay, Diego Alonso Lopez Romero, "
                                      "Gérald Veuillot")

st.markdown("""
**The problem.** Late at night, the most exposed part of a trip is often the last one: the walk from the
metro or RER station to home. Many people, women first of all, either walk alone and feel unsafe, or pay for
a solo taxi or ride-share. Students on suburban campuses such as Cergy and staff finishing late shifts
(hotels, restaurants, events) face this several times a week.

**The solution.** SafeCommute AI groups 2 to 4 people who leave the same station at the same time and head
the same way, and gives them a meeting point at the station exit. First names and initials only.
""")

a, b = st.columns(2, gap="large")
with a, st.container(border=True):
    st.markdown("""
#### Value if widely adopted
- **Safety**: fewer people walking alone at night. Safety in numbers.
- **Sustainability (ESG)**: walking together and staying on public transport replaces solo taxi trips.
- **Operators and cities**: the dashboard shows where and when people end up alone, i.e. where to add a
  night bus, lighting or staff.
- **Employers and campuses**: a duty-of-care tool for night-shift staff and students.
""")
with b, st.container(border=True):
    st.markdown("""
#### AI concepts applied
- **Rule-based (symbolic) AI**: explicit, auditable matching rules instead of a black box.
- **Constrained grouping heuristic**: a greedy algorithm (closest pairs first) under time, distance, size and
  preference constraints.
- **Train / test methodology**: limits tuned on one night, checked on another.
- **Metrics and trade-offs**: coverage vs. destination spread.
- **Explainability**: every unmatched person gets a plain-language reason and alternative slots.
- **Responsible AI**: opt-in gender preference, first name + initial only, no data kept outside the session.
""")

st.markdown("""
#### Design choices
| Question | Our choice |
|---|---|
| Women-only matching? | **Opt-in, per user.** A woman who ticks it only travels with declared women; other women stay in the mixed pool. Making it mandatory would shrink everyone's pool and leave more women alone. The cost is visible on the dashboard. |
| Straight-line or walking distance? | **Straight line (Haversine)** in this prototype: free, offline, explainable. Real walking routes (OpenStreetMap / OSRM) are the next step. |
| Meeting point? | **Yes.** The start point of the member closest to the middle of the group, so always a real station or campus exit. |

#### Data and tools
- Data: 200 simulated commuters around Cergy and Paris created by the team (train night), plus a test night
  and simulated gender columns generated from it (`prepare_data.py`). No real personal data.
- Map: © OpenStreetMap contributors (ODbL), dark tiles © CARTO; address search with Nominatim.
- Interface design: night palette, Fira Sans / Fira Code and accessibility checklist from the
  *ui-ux-pro-max* design system.
- Python packages: Streamlit, pandas, openpyxl, folium, streamlit-folium, geopy, Altair.
- AI assistants used for data generation and code: see `PROMPT_LOG.md`.

#### Limits
- Straight-line distances, not walking routes.
- Greedy matching is fast and explainable but not guaranteed optimal.
- No accounts, chat or live location: a real launch needs identity checks and a reporting button.
""")
