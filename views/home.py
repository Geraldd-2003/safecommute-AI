"""Home: what the app does, today's figures, entry points."""

import streamlit as st

from ui import components as C
from ui import state

c = state.ctx()
r = c.result

st.markdown(
    "<div class='sc-hero'><div class='sc-eyebrow'>Late-night commuting · Cergy & Paris</div>"
    "<h1>Never walk home alone after a late train.</h1>"
    "<p>SafeCommute AI groups 2 to 4 people who leave the same metro or RER station at the same time and head "
    "the same way, and gives them a meeting point at the exit.</p></div>",
    unsafe_allow_html=True)

b1, b2, _ = st.columns([1.2, 1.2, 4])
b1.page_link("views/find.py", label="Find my group", icon=":material/group_add:")
b2.page_link("views/dashboard.py", label="Open the dashboard", icon=":material/monitoring:")

st.markdown("#### Tonight in the selected dataset")
k = st.columns(4)
k[0].metric("Commuters", len(c.df), border=True)
k[1].metric("Groups formed", len(r.groups), border=True)
k[2].metric("Matched", f"{r.match_rate:.0%}", f"{r.n_matched} people", delta_color="off", border=True)
k[3].metric("Time slots", len(c.slots), border=True)

st.markdown("#### How it works")
t = st.columns(3, gap="medium")
with t[0]:
    C.tile("1 · Tell us your trip", "Pick where you leave from and where you go: from a list, an address search "
                                    "or a click on the map. Choose your departure slot.")
with t[1]:
    C.tile("2 · Get your group", "The engine finds up to 3 people starting within 1 km of you, in the same "
                                 "slot, whose homes are within 3 km of yours.")
with t[2]:
    C.tile("3 · Meet and walk", "Meet at a real station or campus exit. Only first names and initials are "
                                "shown. Women can choose women-only groups.")

st.markdown("#### The rules, in plain words")
st.markdown(f"""
- Same departure slot only, groups of **2 to {c.cfg.max_group_size}** people.
- Starting points at most **{c.cfg.max_origin_km:g} km** apart; destinations at most **{c.cfg.max_dest_km:g} km** apart.
- The closest people are grouped first, and nobody is in two groups.
- Women-only is **opt-in** and currently **{'respected' if c.cfg.women_only_rule else 'ignored'}**.

Change any rule in the sidebar: every page updates instantly.
""")
