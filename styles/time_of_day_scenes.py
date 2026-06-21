"""
Time-of-day "scene" animations: a brief (~3 second), purely decorative
glimpse that plays once per session at specific times -- a comet
crossing the sky at 12:00 AM, a plane flying past with a faded sky
backdrop at 12:00 PM. These never block interaction (pointer-events:
none throughout) and never alter scroll position or layout -- they're
an overlay that fades in, plays, and fades out on its own.

Design constraints honored:
- Only triggers once per local day per scene (tracked in
  st.session_state so refreshing doesn't replay it constantly).
- Pure CSS animation, no external assets, no JS scroll manipulation.
- Self-removing: the overlay's own CSS animation reduces it to
  opacity 0 and height 0 by the end, so it doesn't leave dead space.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st


def _today_key(suffix: str) -> str:
    return f"p2p_scene_played_{datetime.now().strftime('%Y%m%d')}_{suffix}"


def _comet_scene_html() -> str:
    return """
    <div class="p2p-scene-overlay p2p-scene-midnight">
        <div class="p2p-scene-comet"></div>
        <div class="p2p-scene-stars"></div>
    </div>
    """


def _plane_scene_html() -> str:
    return """
    <div class="p2p-scene-overlay p2p-scene-noon">
        <div class="p2p-scene-plane">✈️</div>
        <div class="p2p-scene-cloud p2p-scene-cloud-1"></div>
        <div class="p2p-scene-cloud p2p-scene-cloud-2"></div>
    </div>
    """


def maybe_render_time_of_day_scene() -> None:
    """Call once near the top of a page render. Shows a brief scene
    overlay if the current local time matches a trigger window and
    that scene hasn't already played today in this session.
    """
    now = datetime.now()
    hour, minute = now.hour, now.minute

    # Midnight comet: 12:00 AM - 12:02 AM window (so a slightly-late
    # page load still catches it, without playing all night).
    if hour == 0 and minute < 2:
        key = _today_key("comet")
        if not st.session_state.get(key):
            st.session_state[key] = True
            st.markdown(_comet_scene_html(), unsafe_allow_html=True)
            return

    # Noon plane: 12:00 PM - 12:02 PM window, same reasoning.
    if hour == 12 and minute < 2:
        key = _today_key("plane")
        if not st.session_state.get(key):
            st.session_state[key] = True
            st.markdown(_plane_scene_html(), unsafe_allow_html=True)
            return
