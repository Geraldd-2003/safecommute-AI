"""Folium map helpers (OpenStreetMap tiles, darkened with a CSS filter to match the night theme)."""

from html import escape as esc

import folium

import engine as E
from ui import style

# Free OSM tiles need no API key; the filter only recolours the background, not the markers.
NIGHT_TILES_CSS = """<style>
.leaflet-tile-pane { filter: invert(1) hue-rotate(180deg) brightness(.92) contrast(.9) saturate(.6); }
.leaflet-container { background: #0B1220; }
</style>"""


def _map(location, zoom: int) -> folium.Map:
    m = folium.Map(location=location, zoom_start=zoom, tiles="OpenStreetMap", control_scale=True)
    m.get_root().header.add_child(folium.Element(NIGHT_TILES_CSS))
    return m


def base_map(points) -> folium.Map:
    """Map centred on the points. The zoom is computed here rather than with
    fit_bounds, which fails when the map is drawn in a hidden container."""
    if not points:
        return _map((49.0, 2.2), 10)
    lats, lngs = [p[0] for p in points], [p[1] for p in points]
    span = max(max(lats) - min(lats), (max(lngs) - min(lngs)) * 0.66)
    zoom = next((z for z, s in [(15, .008), (14, .016), (13, .03), (12, .06), (11, .12),
                                (10, .25), (9, .5)] if span <= s), 8)
    return _map(((max(lats) + min(lats)) / 2, (max(lngs) + min(lngs)) / 2), zoom)


def add_group(m: folium.Map, group: list[dict], color: str, me_id=None, label: str = "") -> None:
    mp = E.meeting_point(group)
    for mbr in group:
        if mbr["User_ID"] == me_id:
            continue
        name = esc(E.short_name(mbr["User_Name"]))
        folium.CircleMarker([mbr["Origin_Lat"], mbr["Origin_Lng"]], radius=7, color=color, fill=True,
                            fill_opacity=.95, tooltip=f"{label}{name} starts here").add_to(m)
        folium.CircleMarker([mbr["Destination_Lat"], mbr["Destination_Lng"]], radius=6, color=color,
                            fill=True, fill_color=style.BG, fill_opacity=1, weight=3,
                            tooltip=f"{label}{name} goes to {esc(mbr['Destination_Address'])}").add_to(m)
        folium.PolyLine([[mp["lat"], mp["lng"]], [mbr["Destination_Lat"], mbr["Destination_Lng"]]],
                        color=color, weight=3, opacity=.7, dash_array="6 6").add_to(m)
    folium.Marker([mp["lat"], mp["lng"]], tooltip=f"{label}Meeting point: {esc(mp['address'])}",
                  icon=folium.Icon(color="orange", icon="users", prefix="fa")).add_to(m)


def add_alone(m: folium.Map, users: list[dict], tooltip: str | None = None) -> None:
    for u in users:
        folium.CircleMarker([u["Origin_Lat"], u["Origin_Lng"]], radius=4, color=style.UNMATCHED, fill=True,
                            fill_opacity=.7,
                            tooltip=tooltip or f"{esc(E.short_name(u['User_Name']))} · not matched").add_to(m)
