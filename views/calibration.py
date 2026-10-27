"""Calibration: choose the distance limits on the train night, check them on the test night."""

import altair as alt
import pandas as pd
import streamlit as st

import engine as E
from ui import components as C
from ui import state, style

c = state.ctx()
cfg = c.cfg

C.page_header("Calibration",
              "Choose the limits on the train night, check them on a night the choice never saw.")
st.markdown(
    "The engine is rule-based, so there is nothing to *train* in the machine-learning sense: what we tune are "
    "its two distance limits. Two metrics pull in opposite directions:\n"
    "- **Coverage**: share of commuters placed in a group (higher is better).\n"
    "- **Destination spread**: average largest gap between two members' destinations "
    "(lower is safer, because the last person walks alone over that distance).")


def heatmap(sens: pd.DataFrame, value: str, fmt: str, scheme: str) -> alt.LayerChart:
    base = alt.Chart(sens).encode(
        x=alt.X("Max_Destination_km:O", title="Max distance between destinations (km)",
                axis=alt.Axis(labelAngle=0)),
        y=alt.Y("Max_Origin_km:O", title="Max distance between starts (km)", sort="descending"))
    rect = base.mark_rect(cornerRadius=3).encode(
        color=alt.Color(f"{value}:Q", title=None, scale=alt.Scale(scheme=scheme)),
        tooltip=[alt.Tooltip("Max_Origin_km", title="Starts ≤ km"),
                 alt.Tooltip("Max_Destination_km", title="Destinations ≤ km"), "Groups",
                 alt.Tooltip("Match_Rate:Q", format=".1%", title="Coverage"),
                 alt.Tooltip("Avg_Dest_Spread_km:Q", format=".2f", title="Spread (km)")])
    text = base.mark_text(fontSize=12, color="#0B1220").encode(text=alt.Text(f"{value}:Q", format=fmt))
    current = base.transform_filter(
        (alt.datum.Max_Origin_km == cfg.max_origin_km) & (alt.datum.Max_Destination_km == cfg.max_dest_km)
    ).mark_rect(fill=None, stroke=style.TEXT, strokeWidth=2.5)
    return (rect + text + current).properties(height=270)


train_df, test_df = state.load_builtin(str(state.TRAIN_DEMO)), state.load_builtin(str(state.TEST))
s_train = state.cached_sensitivity(train_df, cfg)
h1, h2 = st.columns(2, gap="large")
with h1, st.container(border=True):
    st.markdown("**Coverage on train** · share of commuters matched")
    st.altair_chart(heatmap(s_train, "Match_Rate", ".0%", "blues"), width="stretch")
with h2, st.container(border=True):
    st.markdown("**Destination spread on train** · km, lower is safer")
    st.altair_chart(heatmap(s_train, "Avg_Dest_Spread_km", ".1f", "oranges"), width="stretch")
st.caption("The outlined cell is the current setting, when it is on the grid. Change it in the sidebar.")

r_train, r_test = E.run_matching(train_df, cfg), E.run_matching(test_df, cfg)
st.markdown(f"### Current rules · starts ≤ {cfg.max_origin_km:g} km, destinations ≤ {cfg.max_dest_km:g} km")
k = st.columns(4)
k[0].metric("Coverage on train", f"{r_train.match_rate:.1%}", border=True)
k[1].metric("Coverage on test", f"{r_test.match_rate:.1%}",
            f"{(r_test.match_rate - r_train.match_rate) * 100:+.1f} pts vs. train", delta_color="off", border=True)
k[2].metric("Spread on train", f"{state.dest_spread(r_train):.2f} km", border=True)
k[3].metric("Spread on test", f"{state.dest_spread(r_test):.2f} km", border=True)

gap = abs(r_train.match_rate - r_test.match_rate)
if gap < 0.05:
    st.success(f"Train and test coverage differ by {gap * 100:.1f} points: the rules generalise to a new night.",
               icon=":material/check_circle:")
else:
    st.warning(f"Train and test coverage differ by {gap * 100:.1f} points: the rules behave differently on a "
               "new night, worth checking.", icon=":material/warning:")
