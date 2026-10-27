"""Global CSS. Colours come from the design system (see .streamlit/config.toml)."""

import streamlit as st

# Design tokens (dark "night" theme)
BG = "#0B1220"
SURFACE = "#111A2E"
SURFACE_2 = "#17223A"
BORDER = "#24314D"
TEXT = "#E2E8F0"
MUTED = "#94A3B8"
PRIMARY = "#3B82F6"
ACCENT = "#F59E0B"      # meeting points, highlights
OK = "#22C55E"
KO = "#F87171"
UNMATCHED = "#64748B"

# Group colours on the map: distinct and readable on dark map tiles
GROUP_COLORS = ["#60A5FA", "#F59E0B", "#34D399", "#F472B6", "#A78BFA",
                "#22D3EE", "#FB923C", "#A3E635", "#F87171", "#FACC15"]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@500;600&family=Fira+Sans:wght@400;500;600;700&display=swap');

.block-container {{ padding-top: 4.2rem; padding-bottom: 3rem; max-width: 1400px; }}
h1, h2, h3 {{ letter-spacing: -0.01em; }}

/* KPI tiles: tabular figures in Fira Code */
[data-testid="stMetricValue"] {{ font-family: 'Fira Code', ui-monospace, monospace; font-weight: 600; }}
[data-testid="stMetricLabel"] p {{ color: {MUTED}; }}

/* Hero on the home page */
.sc-hero {{
  border: 1px solid {BORDER}; border-radius: 16px; padding: 2.2rem 2.4rem;
  background: radial-gradient(1200px 300px at 85% -40%, rgba(59,130,246,.28), transparent 60%),
              radial-gradient(600px 240px at 0% 120%, rgba(245,158,11,.14), transparent 60%),
              {SURFACE};
  margin-bottom: 1.2rem;
}}
.sc-hero h1 {{ font-size: 2.3rem; line-height: 1.15; margin: .2rem 0 .6rem 0; padding: 0; }}
.sc-hero p {{ color: {MUTED}; font-size: 1.08rem; max-width: 46rem; margin: 0; }}
.sc-eyebrow {{ color: {ACCENT}; font-weight: 600; font-size: .82rem; text-transform: uppercase;
              letter-spacing: .08em; }}

/* Page header */
.sc-head {{ margin-bottom: .8rem; }}
.sc-head h1 {{ font-size: 1.9rem; margin: 0; padding: 0; }}
.sc-head p {{ color: {MUTED}; margin: .3rem 0 0 0; }}

/* Numbered steps */
.sc-step {{ display: flex; align-items: center; gap: .6rem; font-weight: 600; margin: .2rem 0 .5rem 0; }}
.sc-step span {{ display: inline-flex; align-items: center; justify-content: center; width: 1.6rem; height: 1.6rem;
                border-radius: 999px; background: rgba(59,130,246,.18); color: #93C5FD; font-size: .85rem;
                font-family: 'Fira Code', monospace; }}

/* Currently selected place */
.sc-point {{ display: flex; gap: .5rem; align-items: center; font-size: .92rem; padding: .45rem .7rem;
            border-radius: 8px; background: {SURFACE_2}; border: 1px solid {BORDER}; margin-bottom: .5rem; }}
.sc-dot {{ width: .65rem; height: .65rem; border-radius: 999px; flex: none; }}

/* Result cards */
.sc-card {{ border: 1px solid {BORDER}; border-radius: 14px; padding: 1.1rem 1.3rem; margin: .4rem 0 .9rem 0;
           background: {SURFACE}; }}
.sc-card h3 {{ margin: 0; padding: 0; font-size: 1.25rem; }}
.sc-card p {{ margin: .45rem 0 0 0; }}
.sc-ok {{ border-left: 5px solid {OK}; }}
.sc-ko {{ border-left: 5px solid {KO}; }}
.sc-badge {{ display: inline-block; font-size: .78rem; font-weight: 600; padding: .15rem .55rem; border-radius: 999px;
            margin-bottom: .4rem; }}
.sc-badge-ok {{ background: rgba(34,197,94,.15); color: #86EFAC; }}
.sc-badge-ko {{ background: rgba(248,113,113,.15); color: #FCA5A5; }}
.sc-chip {{ display: inline-block; padding: .25rem .75rem; margin: .15rem .25rem .15rem 0; border-radius: 999px;
           background: rgba(59,130,246,.16); color: #BFDBFE; font-size: .92rem; }}
.sc-chip small {{ color: {ACCENT}; }}

/* Feature tiles on the home page */
.sc-tile {{ border: 1px solid {BORDER}; border-radius: 14px; padding: 1.1rem 1.2rem; background: {SURFACE};
           height: 100%; }}
.sc-tile b {{ display: block; margin-bottom: .3rem; }}
.sc-tile p {{ color: {MUTED}; margin: 0; font-size: .95rem; }}
.sc-num {{ font-family: 'Fira Code', monospace; color: {ACCENT}; font-weight: 600; }}

/* Map legend */
.sc-legend {{ display: flex; flex-wrap: wrap; gap: .9rem; color: {MUTED}; font-size: .85rem; margin-top: .3rem; }}
.sc-legend span {{ display: inline-flex; align-items: center; gap: .35rem; }}

/* Accessibility: visible keyboard focus, reduced motion */
a:focus-visible, button:focus-visible, [role="tab"]:focus-visible, input:focus-visible {{
  outline: 2px solid {ACCENT} !important; outline-offset: 2px; }}
@media (prefers-reduced-motion: reduce) {{
  *, *::before, *::after {{ animation: none !important; transition: none !important; }}
}}
</style>
"""


def apply() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
