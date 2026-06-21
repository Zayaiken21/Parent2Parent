import streamlit as st

from backend.nyc_resources_service import (
    CATEGORIES, CATEGORY_DESCRIPTIONS, DISCLAIMER_TEXT,
    list_resources_by_category, create_resource, delete_resource, ResourceError,
)


def _render_resource_card(resource: dict, ceo_controls: bool, shard_id: str) -> None:
    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown(f"#### {resource['name']}")
    if resource.get("description"):
        st.write(resource["description"])
    if resource.get("address"):
        st.caption(f"📍 {resource['address']}")
    if resource.get("phone"):
        st.caption(f"📞 {resource['phone']}")
    if resource.get("url"):
        st.link_button("Visit Website ↗", resource["url"], use_container_width=True)
    if ceo_controls:
        if st.button("🗑️ Remove", key=f"delete_resource_{resource['id']}", use_container_width=True):
            delete_resource(shard_id, resource["id"])
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _render_ceo_add_form(shard_id: str) -> None:
    st.markdown("### Add a Resource")
    with st.form("add_resource_form", clear_on_submit=True):
        category = st.selectbox(
            "Category",
            list(CATEGORIES.keys()),
            format_func=lambda k: CATEGORIES[k],
        )
        name = st.text_input("Name")
        description = st.text_area("Description (optional)")
        url = st.text_input("Website URL (optional)")
        phone = st.text_input("Phone (optional)")
        address = st.text_input("Address (optional)")
        submitted = st.form_submit_button("Add Resource", use_container_width=True, type="primary")
        if submitted:
            try:
                create_resource(
                    shard_id=shard_id,
                    category=category,
                    name=name,
                    description=description,
                    url=url,
                    phone=phone,
                    address=address,
                )
                st.success(f"Added to {CATEGORIES[category]}.")
                st.rerun()
            except ResourceError as exc:
                st.error(str(exc))


def render_nyc_resources() -> None:
    role = st.session_state.get("role")
    is_ceo = role == "ceo"
    shard_id = st.session_state.get("shard_id", "shard_001")

    hero_class = "app-hero ceo" if is_ceo else "app-hero"
    st.markdown(
        f"""
        <section class="{hero_class}">
            <h1>🗽 NYC Programs & Resources</h1>
            <p>{"Manage the resource directory for all parents." if is_ceo else "Real support, close to home."}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="p2p-card" style="border-left:3px solid #E8A33D;">'
        f'<small>{DISCLAIMER_TEXT}</small></div>',
        unsafe_allow_html=True,
    )

    if is_ceo:
        _render_ceo_add_form(shard_id)
        st.divider()

    grouped = list_resources_by_category(shard_id)

    tabs = st.tabs([CATEGORIES[key] for key in CATEGORIES])
    for tab, key in zip(tabs, CATEGORIES):
        with tab:
            st.caption(CATEGORY_DESCRIPTIONS[key])
            resources = grouped.get(key, [])
            if not resources:
                st.info("No resources in this category yet.")
            for resource in resources:
                _render_resource_card(resource, ceo_controls=is_ceo, shard_id=shard_id)
