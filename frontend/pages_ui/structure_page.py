import streamlit as st

STRUCTURE_FRAMEWORKS = [
    {
        "title": "The 3-Rule Household",
        "summary": "Pick 3 non-negotiable rules, not 15. Fewer rules, enforced consistently, beat many rules enforced inconsistently.",
        "steps": [
            "Write down only the 3 rules that matter most for safety/respect right now.",
            "Explain the 'why' behind each one in one sentence your child can repeat back.",
            "Apply the same consequence every time, calmly — consistency builds trust in the structure itself.",
        ],
    },
    {
        "title": "Visual Routine Charts (ages 2–10)",
        "summary": "Young kids thrive on seeing what's next, not just hearing it.",
        "steps": [
            "List the daily routine in 4-6 simple steps (wake up, brush teeth, breakfast, etc).",
            "Use pictures or icons next to each step if your child isn't reading fluently yet.",
            "Let them check off each step themselves — ownership matters more than the chart.",
        ],
    },
    {
        "title": "Earned Independence Ladder (ages 11+)",
        "summary": "Structure shifts from 'rules imposed' to 'privileges earned and renegotiated' as kids age.",
        "steps": [
            "List current privileges (screen time, curfew, etc) and what would earn the next level up.",
            "Revisit the ladder together every few months — kids age out of agreements fast.",
            "Let natural consequences (not just punishments) teach the lesson where it's safe to do so.",
        ],
    },
]


def render_structure_tools() -> None:
    st.markdown(
        """
        <section class="app-hero">
            <h1>Structure & Routines</h1>
            <p>Frameworks for building healthy, consistent structure at home.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    for fw in STRUCTURE_FRAMEWORKS:
        st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
        st.markdown(f"### {fw['title']}")
        st.write(fw["summary"])
        for step in fw["steps"]:
            st.markdown(f"- {step}")
        st.markdown("</div>", unsafe_allow_html=True)
