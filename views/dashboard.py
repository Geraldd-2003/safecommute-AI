"""Dashboard: operator view of the whole night."""

import altair as alt
import streamlit as st
from streamlit_folium import st_folium

import engine as E
from ui import components as C
from ui import maps, state, style

c = state.ctx()
df, r = c.df, c.result

C.page_header("Operator dashboard",
              "Where and when people end up alone: the places to add a night bus, lighting or staff.")

wo_df = df[df["Women_Only"]]
matched_ids = {m["User_ID"] for g in r.groups for m in g}
k = st.columns(5)
k[0].metric("Commuters", len(df), border=True)
k[1].metric("Groups formed", len(r.groups), border=True)
k[2].metric("Matched", f"{r.match_rate:.0%}", f"{r.n_matched} people", delta_color="off", border=True)
k[3].metric("Travelling alone", len(r.unmatched), border=True)
k[4].metric("Women-only matched",
            f"{wo_df['User_ID'].isin(matched_ids).sum()} / {len(wo_df)}" if len(wo_df) else "n/a", border=True,
            help="Women who opted in to women-only groups and were placed in one.")

stats = r.slot_stats.copy()
stats["Slot"] = stats["Time_Slot"].str.split(" ", n=1).str[1].str.replace(" ", "")

with st.container(border=True):
    st.markdown("**Matched vs. alone, per departure slot**")
    long = stats.melt(id_vars=["Slot"], value_vars=["Matched", "Unmatched"],
                      var_name="Status", value_name="Commuters")
    long["Status"] = long["Status"].replace({"Unmatched": "Alone"})
    st.altair_chart(
        alt.Chart(long).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X("Slot:N", sort=list(stats["Slot"]), title=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y("Commuters:Q", stack=True, title="Commuters"),
            color=alt.Color("Status:N", title=None, legend=alt.Legend(orient="top"),
                            scale=alt.Scale(domain=["Matched", "Alone"], range=[style.PRIMARY, style.UNMATCHED])),
            tooltip=["Slot", "Status", "Commuters"]).properties(height=250),
        width="stretch")

st.markdown("### Map of one slot")
sel = st.selectbox("Time slot", c.slots, index=int(stats["Groups"].idxmax()) if len(stats) else 0)
sel_groups = [g for g in r.groups if g[0]["Travel_Time_Slot"] == sel]
sel_alone = [u for u in r.unmatched if u["Travel_Time_Slot"] == sel]
pts = ([(m["Origin_Lat"], m["Origin_Lng"]) for g in sel_groups for m in g]
       + [(m["Destination_Lat"], m["Destination_Lng"]) for g in sel_groups for m in g]
       + [(u["Origin_Lat"], u["Origin_Lng"]) for u in sel_alone])
dmap = maps.base_map(pts)
maps.add_alone(dmap, sel_alone)
group_ids = {id(g): f"GRP-{i:03d}" for i, g in enumerate(r.groups, 1)}
for i, g in enumerate(sel_groups):
    maps.add_group(dmap, g, style.GROUP_COLORS[i % len(style.GROUP_COLORS)], label=f"{group_ids[id(g)]} · ")
st_folium(dmap, key="dash_map", height=500, width="stretch", returned_objects=[])
C.legend([("Start (one colour per group)", style.GROUP_COLORS[0], False),
          ("Destination", style.GROUP_COLORS[0], True), ("Meeting point", style.ACCENT, False),
          ("Not matched", style.UNMATCHED, False)])
st.caption(f"{len(sel_groups)} groups and {len(sel_alone)} people alone in this slot.")

gdf = E.groups_frame(r)
udf = E.unmatched_frame(r, df)
left, right = st.columns([3, 2], gap="large")
with left:
    st.markdown("### Groups")
    if len(gdf):
        st.dataframe(gdf[["Group_ID", "Group_Size", "Travel_Time_Slot", "Meeting_Point", "User_Name",
                          "Women_Only", "Destination_Address", "Walk_To_Meeting_m", "Max_Destination_Gap_km"]],
                     hide_index=True, width="stretch", height=360,
                     column_config={
                         "Group_ID": "Group", "Group_Size": "Size", "Travel_Time_Slot": "Slot",
                         "Meeting_Point": "Meeting point", "User_Name": "Member",
                         "Women_Only": st.column_config.CheckboxColumn("Women-only"),
                         "Destination_Address": "Destination",
                         "Walk_To_Meeting_m": st.column_config.NumberColumn("Walk to meet", format="%d m"),
                         "Max_Destination_Gap_km": st.column_config.NumberColumn("Max dest. gap",
                                                                                 format="%.2f km")})
    else:
        st.info("No group with the current rules. Try loosening them in the sidebar.", icon=":material/info:")
with right:
    st.markdown("### Why people were not matched")
    if len(udf):
        reasons = (udf["Reason"].str.replace(r"^\d+ people leave nearby", "People leave nearby", regex=True)
                   .str.replace(r"\s*\(.*\)$", "", regex=True).value_counts()
                   .rename_axis("Reason").reset_index(name="Commuters"))
        st.altair_chart(
            alt.Chart(reasons).mark_bar(color=style.ACCENT, cornerRadiusEnd=3).encode(
                x=alt.X("Commuters:Q", title="Commuters"),
                y=alt.Y("Reason:N", sort="-x", title=None, axis=alt.Axis(labelLimit=260)),
                tooltip=["Reason", "Commuters"]).properties(height=max(120, 46 * len(reasons))),
            width="stretch")
    else:
        st.success("Everybody is in a group.", icon=":material/check_circle:")

if len(udf):
    with st.expander(f"All {len(udf)} unmatched commuters"):
        st.dataframe(udf[["User_ID", "User_Name", "Travel_Time_Slot", "Origin_Address",
                          "Destination_Address", "Reason"]], hide_index=True, width="stretch")

st.download_button("Download all results (Excel)", E.export_excel(r, df), file_name="safecommute_results.xlsx",
                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                   icon=":material/download:")
