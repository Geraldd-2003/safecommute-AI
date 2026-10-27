"""Small reusable pieces of interface (HTML is always escaped)."""

from html import escape as esc

import streamlit as st

import engine as E
from ui import style


def page_header(title: str, subtitle: str = "") -> None:
    sub = f"<p>{esc(subtitle)}</p>" if subtitle else ""
    st.markdown(f"<div class='sc-head'><h1>{esc(title)}</h1>{sub}</div>", unsafe_allow_html=True)


def step(n: int, text: str) -> None:
    st.markdown(f"<div class='sc-step'><span>{n}</span>{esc(text)}</div>", unsafe_allow_html=True)


def place(label: str, color: str) -> None:
    st.markdown(f"<div class='sc-point'><i class='sc-dot' style='background:{color}'></i>{esc(label)}</div>",
                unsafe_allow_html=True)


def group_card(others: list[dict], meeting: str, slot: str) -> None:
    chips = "".join(
        f"<span class='sc-chip'>{esc(E.short_name(m['User_Name']))}"
        f"{' <small>· women-only</small>' if m['Women_Only'] else ''}</span>" for m in others)
    people = "person" if len(others) == 1 else "people"
    st.markdown(
        "<div class='sc-card sc-ok'><span class='sc-badge sc-badge-ok'>Group found</span>"
        f"<h3>You're travelling with {len(others)} {people}</h3>"
        f"<p>{chips}</p>"
        f"<p><b>Meet at</b> {esc(meeting)} &nbsp;·&nbsp; <b>Slot</b> {esc(slot)}</p></div>",
        unsafe_allow_html=True)


def no_group_card(reason: str) -> None:
    st.markdown(
        "<div class='sc-card sc-ko'><span class='sc-badge sc-badge-ko'>No group yet</span>"
        "<h3>Nobody fits this trip with the current rules</h3>"
        f"<p>{esc(reason)}.</p></div>", unsafe_allow_html=True)


def tile(title: str, text: str) -> None:
    st.markdown(f"<div class='sc-tile'><b>{esc(title)}</b><p>{esc(text)}</p></div>", unsafe_allow_html=True)


def legend(items: list[tuple[str, str, bool]]) -> None:
    """items: (label, colour, ring) - ring=True draws an outlined dot."""
    parts = []
    for label, color, ring in items:
        dot = (f"border:2px solid {color};background:transparent" if ring else f"background:{color}")
        parts.append(f"<span><i class='sc-dot' style='{dot}'></i>{esc(label)}</span>")
    st.markdown(f"<div class='sc-legend'>{''.join(parts)}</div>", unsafe_allow_html=True)


MAP_LEGEND = [("Start", style.GROUP_COLORS[0], False), ("Destination", style.GROUP_COLORS[0], True),
              ("Meeting point", style.ACCENT, False), ("Not matched", style.UNMATCHED, False)]
