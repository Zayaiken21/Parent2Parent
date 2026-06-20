import streamlit as st
import random
from datetime import date

CONNECTION_PROMPTS = [
    "Ask your child one question today you've never asked before.",
    "Spend 10 minutes doing something THEY chose, with no phone nearby.",
    "Tell your child one specific thing you're proud of them for — be specific, not general.",
    "Let them see you make a mistake and handle it calmly. It teaches more than any lecture.",
    "Ask about their favorite song or show right now, and actually listen without judging it.",
    "Say 'I missed you today' or an equivalent — even teens want to hear it, even if they act like they don't.",
    "Sit in silence together doing parallel activities (cooking, drawing) — connection doesn't always need words.",
    "Validate a feeling before offering a solution: 'That sounds really frustrating' before any advice.",
    "Share a story from your own childhood at their age — it makes you human, not just 'the parent.'",
    "Ask 'what's something I could do differently as your parent?' and just listen, no defending.",
]


def render_connection_builder() -> None:
    st.markdown(
        """
        <section class="app-hero">
            <h1>Connection Builder</h1>
            <p>One small, real way to connect today.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    seed = int(date.today().strftime("%Y%m%d"))
    prompt = CONNECTION_PROMPTS[seed % len(CONNECTION_PROMPTS)]

    st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
    st.markdown("### 🌟 Today's Prompt")
    st.markdown(f"**{prompt}**")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("More Ideas")
    for p in CONNECTION_PROMPTS:
        if p != prompt:
            st.markdown(f"- {p}")
