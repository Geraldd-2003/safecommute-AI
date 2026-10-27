"""Find my group: commuter view. Set a trip and see your group live on the map."""

from html import escape as esc

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

import engine as E
from ui import components as C
from ui import maps, state, style

DEFAULT_START = {"lat": 49.0356, "lng": 2.0692,
                 "label": "ESSEC Business School, 3 Av. Bernard Hirsch, 95000 Cergy"}
DEFAULT_DEST = {"lat": 49.0170, "lng": 2.0924, "label": "Éragny-sur-Oise, 95610 Eragny"}
DEFAULT_SLOT = "2026-11-10 22:00 - 22:30"
ME = "APP-ME"
GENDERS = {"Prefer not to say": "Not declared", "Woman": "F", "Man": "M"}

c = state.ctx()
df, cfg = c.df, c.cfg
ss = st.session_state
ss.setdefault("start", dict(DEFAULT_START))
ss.setdefault("dest", dict(DEFAULT_DEST))
ss.setdefault("handled_click", None)
ss.setdefault("geo_msg", {})


def places(kind: str) -> pd.DataFrame:
    cols = {"start": ["Origin_Address", "Origin_Lat", "Origin_Lng"],
            "dest": ["Destination_Address", "Destination_Lat", "Destination_Lng"]}[kind]
    p = df[cols].groupby(cols[0]).mean()
    p.columns = ["lat", "lng"]
    return p.sort_index()


def pick_from_list(point: str, table: pd.DataFrame) -> None:
    label = ss[f"{point}_pick"]
    if label in table.index:
        lat, lng = table.loc[label]
        ss[point] = {"lat": float(lat), "lng": float(lng), "label": label}


def search_address(point: str) -> None:
    q = ss.get(f"{point}_q", "").strip()
    ss.geo_msg.pop(point, None)
    if not q:
        ss.geo_msg[point] = "Type an address first."
        return
    try:
        hit = state.geocode(q)
    except Exception:  # no internet, service busy...
        ss.geo_msg[point] = ("Address search needs an internet connection (OpenStreetMap). "
                             "Pick a place from the list or click on the map instead.")
        return
    if hit is None:
        ss.geo_msg[point] = f"No address found for “{q}”. Try adding the town name."
    else:
        ss[point] = {"lat": hit[0], "lng": hit[1], "label": hit[2]}


def place_inputs(point: str, color: str, list_label: str, placeholder: str) -> None:
    C.place(ss[point]["label"], color)
    table = places(point)
    st.selectbox(list_label, list(table.index), index=None, placeholder="Choose from the list",
                 key=f"{point}_pick", on_change=pick_from_list, args=(point, table))
    with st.form(f"{point}_search", border=False, enter_to_submit=True):
        a, b = st.columns([4, 1.3], vertical_alignment="bottom")
        a.text_input("Or search an address", key=f"{point}_q", placeholder=placeholder)
        b.form_submit_button("Search", icon=":material/search:", on_click=search_address, args=(point,),
                             width="stretch")
    if ss.geo_msg.get(point):
        st.warning(ss.geo_msg[point], icon=":material/warning:")


C.page_header("Find people to travel home with",
              "Set your trip on the left. Your group, meeting point and walk update live on the map.")

left, right = st.columns([2, 3], gap="large")

with left:
    with st.container(border=True):
        C.step(1, "Where do you leave from?")
        place_inputs("start", style.OK, "Station or campus", "e.g. Gare de Pontoise")
    with st.container(border=True):
        C.step(2, "Where are you going?")
        place_inputs("dest", style.KO, "Destination", "e.g. 10 Rue de Paris, Osny")
    with st.container(border=True):
        C.step(3, "When, and who are you?")
        slot = st.selectbox("Departure time slot", c.slots,
                            index=c.slots.index(DEFAULT_SLOT) if DEFAULT_SLOT in c.slots else 0)
        name = st.text_input("First and last name", "Gerald Veuillot",
                             help="Other commuters only see your first name and initial.")
        g1, g2 = st.columns(2)
        gender = g1.selectbox("Gender (optional)", list(GENDERS))
        transport = g2.selectbox("Then I take", sorted(df["Transport_Preference"].unique()))
        women_only = st.checkbox("I only want to travel with women", disabled=gender != "Woman",
                                 help="Available to commuters who declare themselves as women.")

me = {
    "User_ID": ME, "User_Name": name.strip() or "Anonymous",
    "Origin_Address": ss.start["label"], "Origin_Lat": ss.start["lat"], "Origin_Lng": ss.start["lng"],
    "Destination_Address": ss.dest["label"], "Destination_Lat": ss.dest["lat"],
    "Destination_Lng": ss.dest["lng"], "Transport_Preference": transport, "Travel_Time_Slot": slot,
    "Gender": GENDERS[gender], "Women_Only": bool(women_only and gender == "Woman"),
}
pool = df[~df["User_ID"].isin(ss.my_ids)]
group, reason, _ = E.find_group_for(me, pool, cfg)

with right:
    target = st.segmented_control("A click on the map sets your", ["Start", "Destination"], default="Start",
                                  key="map_target")
    pts = [(ss.start["lat"], ss.start["lng"]), (ss.dest["lat"], ss.dest["lng"])]
    if group:
        pts += [(m["Destination_Lat"], m["Destination_Lng"]) for m in group]
    fmap = maps.base_map(pts)
    in_group = {m["User_ID"] for m in group} if group else set()
    nearby = [u for u in pool[pool["Travel_Time_Slot"] == slot].to_dict("records")
              if u["User_ID"] not in in_group
              and E.haversine_km(u["Origin_Lat"], u["Origin_Lng"], ss.start["lat"], ss.start["lng"]) < 5]
    maps.add_alone(fmap, nearby, tooltip="Another commuter leaving in this slot")
    if group:
        maps.add_group(fmap, group, style.GROUP_COLORS[0], me_id=ME)
    folium.Marker([ss.start["lat"], ss.start["lng"]], tooltip=f"You start: {esc(ss.start['label'])}",
                  icon=folium.Icon(color="green", icon="person-walking", prefix="fa")).add_to(fmap)
    folium.Marker([ss.dest["lat"], ss.dest["lng"]], tooltip=f"You go to: {esc(ss.dest['label'])}",
                  icon=folium.Icon(color="red", icon="house", prefix="fa")).add_to(fmap)
    out = st_folium(fmap, key="find_map", height=540, width="stretch",
                    returned_objects=["last_clicked"])
    C.legend([("Your start", style.OK, False), ("Your destination", style.KO, False),
              ("Group member start / destination", style.GROUP_COLORS[0], False),
              ("Meeting point", style.ACCENT, False), ("Other commuters", style.UNMATCHED, False)])

    click = (out or {}).get("last_clicked")
    if click and click != ss.handled_click:
        ss.handled_click = click
        point = "start" if (target or "Start") == "Start" else "dest"
        ss[point] = {"lat": click["lat"], "lng": click["lng"],
                     "label": f"Pinned on map ({click['lat']:.4f}, {click['lng']:.4f})"}
        st.rerun()

st.markdown("### Your result")
if group:
    mp = E.meeting_point(group)
    others = [m for m in group if m["User_ID"] != ME]
    walk_m = round(1000 * E.haversine_km(me["Origin_Lat"], me["Origin_Lng"], mp["lat"], mp["lng"]))
    dmax = max(E.dest_dist(me, m) for m in others)
    C.group_card(others, mp["address"], slot)
    k1, k2, k3 = st.columns(3)
    k1.metric("Group size", len(group), border=True)
    k2.metric("Your walk to the meeting point", f"{walk_m} m", border=True)
    k3.metric("Furthest destination in the group", f"{dmax:.1f} km", border=True,
              help="Distance between your destination and the furthest one in the group.")
else:
    C.no_group_card(reason)
    alternatives = []
    for s in c.slots:
        if s != slot:
            g, _, _ = E.find_group_for({**me, "Travel_Time_Slot": s}, pool, cfg)
            if g:
                alternatives.append((s, len(g) - 1))
    if alternatives:
        st.write("**You would have company in another slot:**")
        st.dataframe(pd.DataFrame(alternatives, columns=["Time slot", "People to travel with"]),
                     hide_index=True, width="content")
    else:
        st.info("No other slot works with the current rules. Night buses (Noctilien) are the safest fallback.",
                icon=":material/directions_bus:")

if st.button("Add me to the pool so others can match with me", icon=":material/person_add:", type="primary"):
    new_id = f"APP-{len(ss.added) + 1:04d}"
    ss.added.append({**me, "User_ID": new_id})
    ss.my_ids.append(new_id)
    st.toast("You're in the pool. The dashboard now counts you.", icon=":material/check_circle:")
    st.rerun()
