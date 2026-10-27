"""
SafeCommute AI - matching engine
================================

Groups commuters leaving metro/RER stations (or nearby points) late at night
so that nobody has to walk home alone.

Matching rules
--------------
1. Same time slot   : members share the exact same departure window.
2. Group size       : 2 to 4 people (configurable).
3. Origin, solo     : two solo commuters match only if their origins are
                      <= 1.0 km apart.
4. Origin, group    : a commuter joins a group of 2-3 only if their origin is
                      <= 1.0 km from the group's origin centroid.
5. Destination      : every pair of members has destinations <= 3.0 km apart.
6. Priority         : groups are seeded from the CLOSEST pair of origins in the
                      slot, then grown with the closest eligible commuters.
7. Availability     : one group per commuter per time slot.
8. Women-only       : opt-in, per commuter. A woman who ticks "Women_Only" is
                      only grouped with other declared women. Women who do not
                      tick it can be in mixed groups. People whose gender is not
                      declared are never placed in a women-only group.

Compared with the first prototype, rule 6 is now actually enforced: the old
loop picked anchors in file order, so the first row of the file always chose
first, whatever the distances.

The engine has no UI dependency: app.py (Streamlit) imports it, and it can
also be run on its own:  python engine.py data/train_data.xlsx
"""

from __future__ import annotations

import io
import math
import sys
from dataclasses import dataclass
from itertools import combinations

import pandas as pd

REQUIRED_COLUMNS = [
    "User_ID", "User_Name", "Origin_Address", "Origin_Lat", "Origin_Lng",
    "Destination_Address", "Destination_Lat", "Destination_Lng",
    "Transport_Preference", "Travel_Time_Slot",
]
OPTIONAL_COLUMNS = {"Gender": "Not declared", "Women_Only": False}


@dataclass(frozen=True)
class MatchConfig:
    max_origin_km: float = 1.0
    max_dest_km: float = 3.0
    max_group_size: int = 4
    women_only_rule: bool = True


# ---------------------------------------------------------------------------
# Data loading and validation
# ---------------------------------------------------------------------------
def load_dataset(source) -> pd.DataFrame:
    """Read an .xlsx / .csv path or uploaded file object."""
    name = getattr(source, "name", str(source)).lower()
    df = pd.read_csv(source) if name.endswith(".csv") else pd.read_excel(source)
    return prepare_dataset(df)


def validate_dataset(df: pd.DataFrame) -> list[str]:
    """Return a list of human-readable problems (empty list = OK)."""
    problems = []
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        problems.append(f"Missing columns: {', '.join(missing)}")
        return problems
    for c in ["Origin_Lat", "Origin_Lng", "Destination_Lat", "Destination_Lng"]:
        bad = pd.to_numeric(df[c], errors="coerce").isna().sum()
        if bad:
            problems.append(f"{bad} row(s) with a non-numeric {c}")
    if df["User_ID"].duplicated().any():
        problems.append(f"{df['User_ID'].duplicated().sum()} duplicated User_ID(s)")
    return problems


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    problems = validate_dataset(df)
    if problems:
        raise ValueError("; ".join(problems))
    for c in ["Origin_Lat", "Origin_Lng", "Destination_Lat", "Destination_Lng"]:
        df[c] = pd.to_numeric(df[c])
    for c in ["User_ID", "User_Name", "Origin_Address", "Destination_Address",
              "Transport_Preference", "Travel_Time_Slot"]:
        df[c] = df[c].astype(str).str.strip()
    for col, default in OPTIONAL_COLUMNS.items():
        if col not in df.columns:
            df[col] = default
    df["Gender"] = df["Gender"].fillna("Not declared").astype(str).str.strip()
    df["Women_Only"] = df["Women_Only"].map(_to_bool)
    return df


def _to_bool(v) -> bool:
    if isinstance(v, str):
        return v.strip().lower() in {"true", "yes", "oui", "1", "y"}
    return bool(v) if v == v else False  # NaN -> False


# ---------------------------------------------------------------------------
# Geometry
# ---------------------------------------------------------------------------
def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Straight-line (great-circle) distance in km."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def origin_dist(a, b) -> float:
    return haversine_km(a["Origin_Lat"], a["Origin_Lng"], b["Origin_Lat"], b["Origin_Lng"])


def dest_dist(a, b) -> float:
    return haversine_km(a["Destination_Lat"], a["Destination_Lng"],
                        b["Destination_Lat"], b["Destination_Lng"])


def origin_centroid(group) -> tuple[float, float]:
    return (sum(m["Origin_Lat"] for m in group) / len(group),
            sum(m["Origin_Lng"] for m in group) / len(group))


def slot_sort_key(slot: str):
    """Night order: 21:30 ... 23:30, then 00:00, 00:30 (works whether or not
    the date rolls over after midnight in the data)."""
    try:
        date, start = slot.split()[0], slot.split()[1]
        h, m = map(int, start.split(":"))
        return (date if h >= 12 else _prev_day(date), h + 24 if h < 12 else h, m)
    except (IndexError, ValueError):
        return (slot, 0, 0)


def _prev_day(date: str) -> str:
    try:
        return (pd.Timestamp(date) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    except ValueError:
        return date


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------
def gender_ok(group, cfg: MatchConfig) -> bool:
    if not cfg.women_only_rule:
        return True
    if any(m.get("Women_Only", False) for m in group):
        return all(str(m.get("Gender", "")).upper() in {"F", "FEMALE", "WOMAN"} for m in group)
    return True


def can_join(candidate, group, cfg: MatchConfig) -> bool:
    if len(group) >= cfg.max_group_size:
        return False
    c_lat, c_lng = origin_centroid(group)
    if haversine_km(candidate["Origin_Lat"], candidate["Origin_Lng"], c_lat, c_lng) > cfg.max_origin_km:
        return False
    if any(dest_dist(candidate, m) > cfg.max_dest_km for m in group):
        return False
    return gender_ok(group + [candidate], cfg)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------
def match_slot(users: list[dict], cfg: MatchConfig = MatchConfig()):
    """Greedy matching inside one time slot -> (groups, unmatched)."""
    pairs = []
    for a, b in combinations(users, 2):
        d_o = origin_dist(a, b)
        if d_o <= cfg.max_origin_km and dest_dist(a, b) <= cfg.max_dest_km and gender_ok([a, b], cfg):
            pairs.append((d_o, a["User_ID"], b["User_ID"], a, b))
    pairs.sort(key=lambda p: (p[0], p[1], p[2]))  # closest origins first (rule 6)

    assigned, groups = set(), []
    for _, id_a, id_b, a, b in pairs:
        if id_a in assigned or id_b in assigned:
            continue
        group = [a, b]
        assigned.update((id_a, id_b))
        while len(group) < cfg.max_group_size:
            c_lat, c_lng = origin_centroid(group)
            free = sorted((u for u in users if u["User_ID"] not in assigned),
                          key=lambda u: haversine_km(u["Origin_Lat"], u["Origin_Lng"], c_lat, c_lng))
            nxt = next((u for u in free if can_join(u, group, cfg)), None)
            if nxt is None:
                break
            group.append(nxt)
            assigned.add(nxt["User_ID"])
        groups.append(group)

    unmatched = [u for u in users if u["User_ID"] not in assigned]
    return groups, unmatched


@dataclass
class MatchResult:
    groups: list            # list of groups; each group is a list of user dicts
    unmatched: list         # list of user dicts
    slot_stats: pd.DataFrame
    config: MatchConfig

    @property
    def n_matched(self) -> int:
        return sum(len(g) for g in self.groups)

    @property
    def n_users(self) -> int:
        return self.n_matched + len(self.unmatched)

    @property
    def match_rate(self) -> float:
        return self.n_matched / self.n_users if self.n_users else 0.0


def run_matching(df: pd.DataFrame, cfg: MatchConfig = MatchConfig()) -> MatchResult:
    groups, unmatched, stats = [], [], []
    for slot in sorted(df["Travel_Time_Slot"].unique(), key=slot_sort_key):
        users = df[df["Travel_Time_Slot"] == slot].to_dict("records")
        g, u = match_slot(users, cfg)
        for grp in g:
            verify_group(grp, cfg)
        groups.extend(g)
        unmatched.extend(u)
        n = sum(len(x) for x in g)
        stats.append({"Time_Slot": slot, "Users": len(users), "Groups": len(g),
                      "Matched": n, "Unmatched": len(u),
                      "Match_Rate": n / len(users) if users else 0.0})
    return MatchResult(groups, unmatched, pd.DataFrame(stats), cfg)


def verify_group(group, cfg: MatchConfig) -> None:
    """Independent re-check of every rule on a finished group."""
    assert 2 <= len(group) <= cfg.max_group_size, "group size"
    assert len({m["Travel_Time_Slot"] for m in group}) == 1, "time slot"
    for a, b in combinations(group, 2):
        assert dest_dist(a, b) <= cfg.max_dest_km + 1e-9, "destination distance"
    assert gender_ok(group, cfg), "women-only preference"
    for k in range(1, len(group)):
        c_lat, c_lng = origin_centroid(group[:k])
        assert haversine_km(group[k]["Origin_Lat"], group[k]["Origin_Lng"], c_lat, c_lng) \
            <= cfg.max_origin_km + 1e-9, "origin distance"


# ---------------------------------------------------------------------------
# Explaining results
# ---------------------------------------------------------------------------
def meeting_point(group) -> dict:
    """The member origin closest to the group centroid: a real, named place."""
    c_lat, c_lng = origin_centroid(group)
    m = min(group, key=lambda u: haversine_km(u["Origin_Lat"], u["Origin_Lng"], c_lat, c_lng))
    return {"address": m["Origin_Address"], "lat": m["Origin_Lat"], "lng": m["Origin_Lng"]}


def diagnose_unmatched(user: dict, slot_users: list[dict], cfg: MatchConfig) -> str:
    """Plain-language reason why a commuter could not be grouped."""
    others = [u for u in slot_users if u["User_ID"] != user["User_ID"]]
    if not others:
        return "Nobody else travels in this time slot"
    near_origin = [u for u in others if origin_dist(user, u) <= cfg.max_origin_km]
    if not near_origin:
        nearest = min(origin_dist(user, u) for u in others)
        return f"Nobody leaves within {cfg.max_origin_km:g} km (nearest: {nearest:.1f} km)"
    same_way = [u for u in near_origin if dest_dist(user, u) <= cfg.max_dest_km]
    if not same_way:
        nearest = min(dest_dist(user, u) for u in near_origin)
        return (f"{len(near_origin)} people leave nearby, but none heads within "
                f"{cfg.max_dest_km:g} km of the destination (closest: {nearest:.1f} km)")
    compatible = [u for u in same_way if gender_ok([user, u], cfg)]
    if not compatible:
        return "Compatible commuters exist, but none fits the women-only preference"
    return "Compatible commuters were already placed in full or incompatible groups"


def short_name(full_name: str) -> str:
    """'Inès Girard' -> 'Inès G.' (users only see first name + initial)."""
    parts = str(full_name).split()
    return parts[0] if len(parts) < 2 else f"{parts[0]} {parts[-1][0]}."


def find_group_for(new_user: dict, df: pd.DataFrame, cfg: MatchConfig = MatchConfig()):
    """Add one commuter to the live pool of their slot and rerun matching.

    Returns (group or None, reason, slot_groups).
    """
    slot_users = df[df["Travel_Time_Slot"] == new_user["Travel_Time_Slot"]].to_dict("records")
    slot_users = [u for u in slot_users if u["User_ID"] != new_user["User_ID"]] + [new_user]
    groups, _ = match_slot(slot_users, cfg)
    for g in groups:
        if any(m["User_ID"] == new_user["User_ID"] for m in g):
            return g, "", groups
    return None, diagnose_unmatched(new_user, slot_users, cfg), groups


# ---------------------------------------------------------------------------
# Tables and export
# ---------------------------------------------------------------------------
def groups_frame(result: MatchResult) -> pd.DataFrame:
    rows = []
    for i, g in enumerate(result.groups, 1):
        mp = meeting_point(g)
        max_o = max(origin_dist(a, b) for a, b in combinations(g, 2))
        max_d = max(dest_dist(a, b) for a, b in combinations(g, 2))
        for m in g:
            rows.append({
                "Group_ID": f"GRP-{i:03d}", "Group_Size": len(g),
                "Travel_Time_Slot": m["Travel_Time_Slot"], "Meeting_Point": mp["address"],
                "Walk_To_Meeting_m": round(1000 * haversine_km(m["Origin_Lat"], m["Origin_Lng"],
                                                               mp["lat"], mp["lng"])),
                "Max_Origin_Gap_km": round(max_o, 2), "Max_Destination_Gap_km": round(max_d, 2),
                "User_ID": m["User_ID"], "User_Name": m["User_Name"], "Gender": m["Gender"],
                "Women_Only": m["Women_Only"], "Origin_Address": m["Origin_Address"],
                "Destination_Address": m["Destination_Address"],
                "Transport_Preference": m["Transport_Preference"],
                "Origin_Lat": m["Origin_Lat"], "Origin_Lng": m["Origin_Lng"],
                "Destination_Lat": m["Destination_Lat"], "Destination_Lng": m["Destination_Lng"],
            })
    return pd.DataFrame(rows)


def unmatched_frame(result: MatchResult, df: pd.DataFrame) -> pd.DataFrame:
    by_slot = {s: d.to_dict("records") for s, d in df.groupby("Travel_Time_Slot")}
    rows = []
    for u in result.unmatched:
        row = {k: u[k] for k in df.columns}
        row["Reason"] = diagnose_unmatched(u, by_slot[u["Travel_Time_Slot"]], result.config)
        rows.append(row)
    return pd.DataFrame(rows)


def sensitivity(df: pd.DataFrame, base: MatchConfig,
                origins=(0.5, 1.0, 1.5), dests=(2.0, 3.0, 4.0, 5.0)) -> pd.DataFrame:
    """Coverage vs. safety trade-off for a grid of thresholds.

    Match_Rate        : share of commuters placed in a group (coverage, higher = better)
    Avg_Dest_Spread_km: average, over groups, of the largest distance between two
                        members' destinations; a proxy for how far the last member
                        walks alone after the others drop off (lower = safer)
    """
    rows = []
    for o in origins:
        for d in dests:
            r = run_matching(df, MatchConfig(o, d, base.max_group_size, base.women_only_rule))
            spreads = [max(dest_dist(a, b) for a, b in combinations(g, 2)) for g in r.groups]
            rows.append({"Max_Origin_km": o, "Max_Destination_km": d, "Groups": len(r.groups),
                         "Matched": r.n_matched, "Match_Rate": r.match_rate,
                         "Avg_Dest_Spread_km": sum(spreads) / len(spreads) if spreads else 0.0})
    return pd.DataFrame(rows)


def summary_frame(result: MatchResult, df: pd.DataFrame) -> pd.DataFrame:
    cfg = result.config
    sizes = [len(g) for g in result.groups]
    wo = df[df["Women_Only"]]
    matched_ids = {m["User_ID"] for g in result.groups for m in g}
    rows = [
        ("Commuters", len(df)),
        ("Groups formed", len(result.groups)),
        ("Commuters matched", result.n_matched),
        ("Match rate", f"{result.match_rate:.1%}"),
        ("Commuters unmatched", len(result.unmatched)),
        ("Groups of 2 / 3 / 4", " / ".join(str(sizes.count(k)) for k in (2, 3, 4))),
        ("Women-only users matched", f"{wo['User_ID'].isin(matched_ids).sum()} / {len(wo)}"),
        ("Rules", f"same slot; {2}-{cfg.max_group_size} people; origin <= {cfg.max_origin_km:g} km; "
                  f"destinations <= {cfg.max_dest_km:g} km apart; women-only "
                  f"{'on' if cfg.women_only_rule else 'off'}"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Value"])


def export_excel(result: MatchResult, df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    stats = result.slot_stats.copy()
    stats["Match_Rate"] = (stats["Match_Rate"] * 100).round(1).astype(str) + "%"
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        summary_frame(result, df).to_excel(xw, index=False, sheet_name="Summary")
        stats.to_excel(xw, index=False, sheet_name="By_Time_Slot")
        groups_frame(result).to_excel(xw, index=False, sheet_name="Groups")
        unmatched_frame(result, df).to_excel(xw, index=False, sheet_name="Unmatched")
        for ws in xw.sheets.values():
            for col in ws.columns:
                w = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(w + 2, 55)
            ws.freeze_panes = "A2"
    return buf.getvalue()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/train_data.xlsx"
    data = load_dataset(path)
    res = run_matching(data)
    print(res.slot_stats.to_string(index=False))
    print(summary_frame(res, data).to_string(index=False))
    out = path.rsplit(".", 1)[0] + "_matching_results.xlsx"
    with open(out, "wb") as f:
        f.write(export_excel(res, data))
    print(f"\nResults written to {out}")
