"""
Returns the global CSS block, injected once via st.markdown(unsafe_allow_html=True)
at app startup. Keeping this as a function (not raw CSS in every page)
means every page gets identical styling automatically.
"""
from styles.theme import (
    PRIMARY, PRIMARY_DARK, ACCENT, WARM_ACCENT, BACKGROUND,
    CARD_BG, TEXT_DARK, TEXT_MUTED, GRADIENT_MAIN, FONT_STACK,
)


def get_global_css() -> str:
    return f"""
<style>
    .stApp {{
        background-color: {BACKGROUND};
        font-family: {FONT_STACK};
    }}

    /* ---------- Hero / page header ---------- */
    .app-hero {{
        background: {GRADIENT_MAIN};
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        box-shadow: 0 4px 14px rgba(61, 90, 128, 0.25);
    }}
    .app-hero h1 {{
        color: #ffffff;
        margin: 0 0 4px 0;
        font-size: 26px;
        letter-spacing: 0.2px;
    }}
    .app-hero p {{
        color: rgba(255,255,255,0.92);
        margin: 0;
        font-size: 14px;
    }}

    /* ---------- Sticky bottom main nav (mobile-style 4-tab bar) ---------- */
    .p2p-bottom-nav {{
        position: sticky;
        bottom: 0;
        z-index: 999;
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: {CARD_BG};
        border-top: 1px solid #e2e6ea;
        border-radius: 16px 16px 0 0;
        padding: 10px 6px;
        margin-top: 18px;
        box-shadow: 0 -4px 14px rgba(0,0,0,0.06);
    }}

    /* ---------- Cards ---------- */
    .p2p-card {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        border: 1px solid #ECEFF2;
    }}
    .p2p-card h3 {{
        margin-top: 0;
        color: {TEXT_DARK};
    }}
    .p2p-card p {{
        color: {TEXT_MUTED};
    }}

    /* ---------- Chat bubbles ---------- */
    .p2p-chat-bubble {{
        background: #EEF2F7;
        border-radius: 14px;
        padding: 10px 14px;
        margin-bottom: 8px;
        max-width: 80%;
        font-size: 14px;
        color: {TEXT_DARK};
    }}
    .p2p-chat-bubble .sender {{
        font-weight: 700;
        color: {PRIMARY};
        font-size: 12px;
        margin-bottom: 2px;
        display: block;
    }}
    .p2p-chat-bubble.system {{
        background: #FFF4ED;
        border-left: 3px solid {WARM_ACCENT};
        color: {TEXT_DARK};
    }}

    /* ---------- Pro-style expandable sub-menu ---------- */
    .p2p-submenu-trigger {{
        background: {PRIMARY_DARK};
        color: #fff;
        border-radius: 10px;
        padding: 10px 16px;
        font-size: 14px;
        font-weight: 600;
    }}

    /* ---------- Badges ---------- */
    .p2p-badge {{
        display: inline-block;
        background: {ACCENT};
        color: #ffffff;
        border-radius: 999px;
        padding: 3px 10px;
        font-size: 11px;
        font-weight: 700;
        margin-left: 6px;
    }}
    .p2p-badge.warm {{ background: {WARM_ACCENT}; }}

    /* Tighten default Streamlit spacing a bit for an app-like feel */
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 0.5rem;
    }}
</style>
"""
