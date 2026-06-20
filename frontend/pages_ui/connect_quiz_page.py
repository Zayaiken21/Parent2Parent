"""
Connect Quiz: a short reflection tool to help a parent think about
how their child learns and connects best, plus concrete ways to use
that day to day.

Per explicit requirement, this does NOT touch Supabase or any
database — everything lives only in st.session_state for the current
browser session, and disappears when the tab closes or the user logs
out. There is nothing here to leak, store, or review later, by design.

Framing note: this is a reflective conversation-starter, not a
validated psychological or educational assessment. "Learning style"
inventories like this are popular but not strongly supported by
education research as predictors of how someone learns best — so we
present results as a prompt for noticing and connecting, not as a
diagnosis or a label to act on rigidly.
"""
import streamlit as st

QUIZ_QUESTIONS = [
    {
        "key": "explains",
        "question": "When your child is excited about something, they usually...",
        "options": {
            "show": "Show you (a drawing, a move, acting it out)",
            "tell": "Tell you about it, often in a lot of detail",
            "do": "Want you to do/try it together right away",
        },
    },
    {
        "key": "calms",
        "question": "When your child is upset, what tends to help them settle fastest?",
        "options": {
            "show": "A quiet space with something to look at or watch",
            "tell": "Talking it through out loud with you",
            "do": "Moving — a walk, fidgeting, physical activity",
        },
    },
    {
        "key": "learns_new",
        "question": "When learning something brand new, your child prefers to...",
        "options": {
            "show": "Watch someone else do it first",
            "tell": "Have it explained step by step",
            "do": "Just try it hands-on and adjust as they go",
        },
    },
    {
        "key": "connects",
        "question": "Your child feels closest to you when you two are...",
        "options": {
            "show": "Doing something visual together (a show, building, art)",
            "tell": "Having a real conversation, just talking",
            "do": "Doing an activity side by side (cooking, sport, a project)",
        },
    },
]

RESULT_PROFILES = {
    "show": {
        "label": "Visual & Observant",
        "summary": "Your child seems to take in the world through watching and seeing — images, demonstrations, and visual cues tend to land well.",
        "connection_ideas": [
            "Watch something together and talk about it afterward instead of during.",
            "Use drawing, photos, or videos as a way to ask 'tell me about this' questions.",
            "Show them what you mean instead of only explaining — demonstrate first.",
        ],
    },
    "tell": {
        "label": "Verbal & Reflective",
        "summary": "Your child seems to process things by talking them through — conversation itself may be one of their main ways of connecting.",
        "connection_ideas": [
            "Build in real conversation time with no distractions — car rides are great for this.",
            "Ask open-ended questions and let them think out loud without rushing to fix or respond.",
            "Narrate your own reasoning when you explain decisions — they're likely listening closely.",
        ],
    },
    "do": {
        "label": "Hands-On & Active",
        "summary": "Your child seems to learn and connect best through doing — movement and hands-on activity may matter more to them than sitting and listening.",
        "connection_ideas": [
            "Look for shared activities (cooking, sports, building something) over sit-down talks.",
            "Let them try things hands-on before over-explaining — they may learn faster by doing.",
            "If they're restless during a hard conversation, try having it while walking or doing a task together.",
        ],
    },
}


def _reset_quiz():
    for key in list(st.session_state.keys()):
        if key.startswith("connectquiz_"):
            del st.session_state[key]


def render_connect_quiz() -> None:
    st.markdown(
        """
        <section class="app-hero">
            <h1>Connect Quiz</h1>
            <p>A short reflection on how your child connects and learns best.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "This is a quick, personal reflection tool — not a clinical or educational "
        "assessment. Nothing you enter here is saved or stored; it only exists for "
        "this session."
    )

    if st.session_state.get("connectquiz_done"):
        tally = st.session_state.get("connectquiz_tally", {})
        if tally:
            top_key = max(tally, key=tally.get)
            profile = RESULT_PROFILES[top_key]

            st.markdown('<div class="p2p-card">', unsafe_allow_html=True)
            st.markdown(f"### 🌟 {profile['label']}")
            st.write(profile["summary"])
            st.markdown("#### Ways to connect, starting today:")
            for idea in profile["connection_ideas"]:
                st.markdown(f"- {idea}")
            st.markdown("</div>", unsafe_allow_html=True)

            st.caption(
                "Kids are rarely just one style — most show a mix depending on mood "
                "and situation. Use this as a starting point for noticing, not a fixed label."
            )

        if st.button("Retake the quiz", use_container_width=True):
            _reset_quiz()
            st.rerun()
        return

    with st.form("connect_quiz_form"):
        answers = {}
        for q in QUIZ_QUESTIONS:
            choice_label = st.radio(
                q["question"],
                options=list(q["options"].keys()),
                format_func=lambda k, opts=q["options"]: opts[k],
                key=f"connectquiz_q_{q['key']}",
            )
            answers[q["key"]] = choice_label

        submitted = st.form_submit_button("See My Reflection", use_container_width=True)
        if submitted:
            tally = {"show": 0, "tell": 0, "do": 0}
            for v in answers.values():
                tally[v] += 1
            st.session_state.connectquiz_tally = tally
            st.session_state.connectquiz_done = True
            st.rerun()
