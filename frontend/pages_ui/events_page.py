import calendar as cal_module
from datetime import date

import streamlit as st

from events.events_service import (
    list_events_in_window,
    list_all_upcoming_events,
    create_event,
    delete_event,
    _window_bounds,
)
from backend.event_importer import import_event_from_url, EventImportError
from config.age_bands import AGE_BAND_ORDER, AGE_BANDS


def _render_calendar_grid(month_start: date, events_by_day: dict[int, list[dict]]) -> None:
    """Renders a month grid with event dots on days that have events."""
    month_name = month_start.strftime("%B %Y")
    st.markdown('<div class="p2p-calendar">', unsafe_allow_html=True)
    st.markdown(f'<div class="p2p-calendar-header">{month_name}</div>', unsafe_allow_html=True)

    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    weeks = cal_module.Calendar(firstweekday=0).monthdayscalendar(month_start.year, month_start.month)

    grid_html = '<div class="p2p-calendar-grid">'
    for label in day_labels:
        grid_html += f'<div class="p2p-calendar-daylabel">{label}</div>'

    for week in weeks:
        for day_num in week:
            if day_num == 0:
                grid_html += '<div class="p2p-calendar-day empty"></div>'
                continue
            day_events = events_by_day.get(day_num, [])
            css_class = "p2p-calendar-day has-event" if day_events else "p2p-calendar-day"
            dots = "".join(
                f'<span class="event-dot">{ev["title"][:14]}</span>' for ev in day_events[:2]
            )
            if len(day_events) > 2:
                dots += f'<span class="event-dot">+{len(day_events) - 2} more</span>'
            grid_html += f'<div class="{css_class}"><span class="daynum">{day_num}</span>{dots}</div>'

    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_event_card(ev: dict, ceo_controls: bool, shard_id: str) -> None:
    st.markdown('<div class="p2p-event-card">', unsafe_allow_html=True)
    st.markdown('<div class="event-banner">', unsafe_allow_html=True)
    st.markdown(f"<h3>{ev['title']}</h3>", unsafe_allow_html=True)
    time_str = f" · {ev['event_time']}" if ev.get("event_time") else ""
    st.markdown(f'<div class="event-date">{ev["event_date"]}{time_str}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="event-body">', unsafe_allow_html=True)
    if ev.get("image_url"):
        st.image(ev["image_url"], use_container_width=True)
    if ev.get("description"):
        st.write(ev["description"])
    if ev.get("source_url"):
        st.caption(f"Source: {ev['source_url']}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if ceo_controls:
        if st.button("🗑️ Delete event", key=f"delete_event_{ev['id']}", use_container_width=True):
            delete_event(shard_id, ev["id"])
            st.rerun()


def _render_ceo_event_management(shard_id: str) -> None:
    st.markdown("### Manage Events")
    tab_manual, tab_import = st.tabs(["Create Manually", "Import from URL"])

    with tab_manual:
        with st.form("manual_event_form", clear_on_submit=True):
            title = st.text_input("Event title")
            description = st.text_area("Description")
            event_date = st.date_input("Event date", value=date.today())
            event_time = st.text_input("Time (optional)", placeholder="e.g. 6:00 PM ET")
            image_url = st.text_input("Image URL (optional)")
            audience = st.multiselect(
                "Limit to specific age ranges (optional — leave blank for everyone)",
                AGE_BAND_ORDER,
                format_func=lambda b: AGE_BANDS[b]["label"],
            )
            submitted = st.form_submit_button("Create Event", use_container_width=True)
            if submitted:
                if not title.strip():
                    st.error("Enter a title.")
                else:
                    create_event(
                        shard_id=shard_id,
                        title=title,
                        description=description,
                        event_date=event_date.isoformat(),
                        event_time=event_time or None,
                        audience_age_bands=audience or None,
                        image_url=image_url or None,
                    )
                    st.success("Event created.")
                    st.rerun()

    with tab_import:
        st.caption(
            "Paste a link to an event page. We'll try to pull the title, description, "
            "date, and image automatically — review and edit before saving. Some sites "
            "block automated requests; if that happens, use Create Manually instead."
        )
        url = st.text_input("Event page URL", key="import_url_input")
        if st.button("Fetch Details", use_container_width=True):
            try:
                draft = import_event_from_url(url)
                st.session_state.import_draft = draft
                st.success("Pulled details below — review and edit before saving.")
            except EventImportError as exc:
                st.error(str(exc))

        draft = st.session_state.get("import_draft")
        if draft:
            with st.form("import_event_form"):
                title = st.text_input("Event title", value=draft.title)
                description = st.text_area("Description", value=draft.description)
                event_date = st.date_input(
                    "Event date",
                    value=date.fromisoformat(draft.event_date) if draft.event_date else date.today(),
                )
                event_time = st.text_input("Time (optional)", placeholder="e.g. 6:00 PM ET")
                image_url = st.text_input("Image URL", value=draft.image_url or "")
                audience = st.multiselect(
                    "Limit to specific age ranges (optional)",
                    AGE_BAND_ORDER,
                    format_func=lambda b: AGE_BANDS[b]["label"],
                    key="import_audience",
                )
                submitted = st.form_submit_button("Save Imported Event", use_container_width=True)
                if submitted:
                    if not title.strip():
                        st.error("Enter a title.")
                    else:
                        create_event(
                            shard_id=shard_id,
                            title=title,
                            description=description,
                            event_date=event_date.isoformat(),
                            event_time=event_time or None,
                            audience_age_bands=audience or None,
                            image_url=image_url or None,
                            source_url=draft.source_url,
                        )
                        st.success("Event created from imported details.")
                        st.session_state.pop("import_draft", None)
                        st.rerun()


def render_events() -> None:
    role = st.session_state.get("role")
    is_ceo = role == "ceo"
    profile = st.session_state.get("profile", {})
    shard_id = st.session_state.get("shard_id", "shard_001")

    hero_class = "app-hero ceo" if is_ceo else "app-hero"
    st.markdown(
        f"""
        <section class="{hero_class}">
            <h1>{"Event Management" if is_ceo else "Upcoming Events"}</h1>
            <p>{"Create, import, and manage community events." if is_ceo else "See what's happening, by month."}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    if is_ceo:
        _render_ceo_event_management(shard_id)
        st.divider()
        st.markdown("### All Upcoming Events")
        events = list_all_upcoming_events(shard_id)
    else:
        if "events_window_offset" not in st.session_state:
            st.session_state.events_window_offset = 0
        events = list_events_in_window(
            shard_id,
            st.session_state.events_window_offset,
            age_band=profile.get("age_band"),
        )

    if not events:
        st.info("No events scheduled yet.")
        return

    # ---- calendar view ----
    events_by_month: dict[tuple[int, int], dict[int, list[dict]]] = {}
    for ev in events:
        ev_date = date.fromisoformat(ev["event_date"])
        month_key = (ev_date.year, ev_date.month)
        events_by_month.setdefault(month_key, {}).setdefault(ev_date.day, []).append(ev)

    for (year, month), days in sorted(events_by_month.items()):
        _render_calendar_grid(date(year, month, 1), days)

    st.divider()
    st.markdown("### Details")
    for ev in events:
        _render_event_card(ev, ceo_controls=is_ceo, shard_id=shard_id)

    if not is_ceo:
        left, mid, right = st.columns([1, 2, 1])
        with left:
            if st.button("← Earlier", disabled=st.session_state.events_window_offset <= 0):
                st.session_state.events_window_offset -= 1
                st.rerun()
        with right:
            if st.button("Later →"):
                st.session_state.events_window_offset += 1
                st.rerun()

    st.markdown(
        """
        <div class="p2p-page-footer">
            <div class="p2p-page-footer-brand">Parent2Parent</div>
            <div class="p2p-page-footer-tag">Real people. Real problems. Real education. · Est. 2026</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
