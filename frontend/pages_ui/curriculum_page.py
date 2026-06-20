import streamlit as st

from profiles.curriculum import CURRICULUM_STAGES, stages_relevant_to_age_band


def render_curriculum() -> None:
    profile = st.session_state.get("profile", {})

    st.markdown(
        """
        <section class="app-hero">
            <h1>Child Development Guide</h1>
            <p>Ages 0–21, with real ways to build connection and structure at every stage.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    suggested = stages_relevant_to_age_band(profile.get("age_band", ""))
    if suggested:
        st.caption("Suggested for your community, based on common ages of children at this stage — but every stage below is open to everyone.")

    stage_labels = [s["age_range"] for s in CURRICULUM_STAGES]
    default_index = 0
    if suggested:
        default_index = CURRICULUM_STAGES.index(suggested[0])

    selected_label = st.selectbox("Jump to a stage", stage_labels, index=default_index)
    stage = next(s for s in CURRICULUM_STAGES if s["age_range"] == selected_label)

    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown(f"### {stage['age_range']}")
    st.markdown(f"**Focus:** {stage['focus']}")
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
        st.markdown("#### 📍 Milestones to Watch For")
        for m in stage["milestones"]:
            st.markdown(f"- {m}")
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
        st.markdown("#### 💛 Building Connection")
        for tip in stage["connection_tips"]:
            st.markdown(f"- {tip}")
        st.markdown("#### 🧱 Building Structure")
        for tip in stage["structure_tips"]:
            st.markdown(f"- {tip}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("This is general parenting guidance, not medical advice. Talk to your pediatrician about anything that concerns you.")
