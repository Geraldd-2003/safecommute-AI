"""Data loading, sidebar settings and the matching result shared by every page."""

import io
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import streamlit as st

import engine as E

APP_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = APP_DIR / "data"
TRAIN_DEMO = DATA_DIR / "train_data_demo.xlsx"
TEST = DATA_DIR / "test_data.xlsx"
DATASETS = {
    "Train night + simulated gender (demo)": TRAIN_DEMO,
    "Train night (team's original file)": DATA_DIR / "train_data.xlsx",
    "Test night (17-18 Nov 2026)": TEST,
}
UPLOAD = "Upload my own file"
SIMULATED = {"Train night + simulated gender (demo)", "Test night (17-18 Nov 2026)"}


@dataclass
class Context:
    df: pd.DataFrame
    result: E.MatchResult
    cfg: E.MatchConfig
    slots: list[str]
    dataset: str

    @property
    def simulated_gender(self) -> bool:
        return self.dataset in SIMULATED


# ---------------------------------------------------------------------------
# Cached computations
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_builtin(path: str) -> pd.DataFrame:
    return E.load_dataset(path)


@st.cache_data(show_spinner=False)
def load_upload(content: bytes, name: str) -> pd.DataFrame:
    buf = io.BytesIO(content)
    buf.name = name
    return E.load_dataset(buf)


@st.cache_data(show_spinner="Matching commuters...")
def cached_matching(df: pd.DataFrame, cfg: E.MatchConfig) -> E.MatchResult:
    return E.run_matching(df, cfg)


@st.cache_data(show_spinner="Testing thresholds...")
def cached_sensitivity(df: pd.DataFrame, cfg: E.MatchConfig) -> pd.DataFrame:
    return E.sensitivity(df, cfg, origins=(0.5, 0.75, 1.0, 1.5, 2.0),
                         dests=(1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0))


@st.cache_data(ttl=3600, show_spinner="Searching the address...")
def geocode(query: str):
    """Address -> (lat, lng, full address) with OpenStreetMap Nominatim (needs internet)."""
    from geopy.geocoders import Nominatim
    loc = Nominatim(user_agent="safecommute-ai-student-project", timeout=8).geocode(query, country_codes="fr")
    return None if loc is None else (loc.latitude, loc.longitude, loc.address)


# ---------------------------------------------------------------------------
# Sidebar -> Context
# ---------------------------------------------------------------------------
def build_context() -> Context | None:
    """Draw the sidebar settings and return the matching context (None if no data yet)."""
    ss = st.session_state
    ss.setdefault("added", [])       # commuters registered from the app
    ss.setdefault("my_ids", [])      # pool entries that are "me" (never matched with myself)

    with st.sidebar:
        st.markdown("### :material/dataset: Data")
        choice = st.radio("Dataset", list(DATASETS) + [UPLOAD], key="dataset", label_visibility="collapsed")
        base_df, error = None, None
        if choice == UPLOAD:
            up = st.file_uploader("Excel or CSV with the team's columns", type=["xlsx", "xls", "csv"])
            if up is not None:
                try:
                    base_df = load_upload(up.getvalue(), up.name)
                except Exception as exc:
                    error = str(exc)
        else:
            base_df = load_builtin(str(DATASETS[choice]))

        st.markdown("### :material/tune: Matching rules")
        max_o = st.slider("Max distance between starts (km)", 0.2, 3.0, 1.0, 0.1, key="max_o",
                          help="Two people can travel together if they start at most this far apart.")
        max_d = st.slider("Max distance between destinations (km)", 0.5, 10.0, 3.0, 0.5, key="max_d",
                          help="Every member's destination must be at most this far from every other member's.")
        max_g = st.slider("Max group size", 2, 6, 4, key="max_g")
        wo_rule = st.toggle("Respect women-only preferences", value=True, key="wo_rule",
                            help="Women who opt in are only grouped with other women. "
                                 "Everyone else can be in mixed groups.")
        cfg = E.MatchConfig(max_o, max_d, max_g, wo_rule)

        if ss.added:
            st.divider()
            st.caption(f"{len(ss.added)} commuter(s) added from this app")
            if st.button("Remove them", icon=":material/delete:"):
                ss.added, ss.my_ids = [], []
                st.rerun()
        st.divider()
        st.caption("Group 28 · Audrey Laurent, Augustine Nay, Diego Alonso Lopez Romero, Gérald Veuillot")

    if error:
        st.error(f"This file can't be used: {error}", icon=":material/error:")
        return None
    if base_df is None:
        st.info("Upload a file in the sidebar to start. Required columns: "
                + ", ".join(E.REQUIRED_COLUMNS) + ". Optional: Gender, Women_Only.",
                icon=":material/upload_file:")
        return None

    df = pd.concat([base_df, pd.DataFrame(ss.added)], ignore_index=True) if ss.added else base_df
    df = df.drop_duplicates("User_ID", keep="last").reset_index(drop=True)
    result = cached_matching(df, cfg)
    slots = sorted(df["Travel_Time_Slot"].unique(), key=E.slot_sort_key)
    return Context(df, result, cfg, slots, choice)


def ctx() -> Context:
    return st.session_state["ctx"]


def dest_spread(result: E.MatchResult) -> float:
    """Average, over groups, of the largest distance between two members' destinations."""
    from itertools import combinations
    s = [max(E.dest_dist(a, b) for a, b in combinations(g, 2)) for g in result.groups]
    return sum(s) / len(s) if s else 0.0
