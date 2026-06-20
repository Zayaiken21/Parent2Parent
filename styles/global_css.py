"""
Returns the global CSS block, injected once via st.markdown(unsafe_allow_html=True)
at app startup. Keeping this as a function (not raw CSS in every page)
means every page gets identical styling automatically.
"""
from styles.theme import (
    PRIMARY, PRIMARY_DARK, ACCENT, WARM_ACCENT, BACKGROUND,
    CARD_BG, TEXT_DARK, TEXT_MUTED, SUCCESS, WARNING,
    GRADIENT_MAIN, GRADIENT_CEO, FONT_STACK,
)


def get_global_css() -> str:
    return f"""
<style>
    /* App-wide soft gradient backdrop (not just the hero box) so the
       gradient reads as a whole-app aesthetic, not a single banner.
       Kept light/washed so body text stays comfortably readable for
       all ages, per the "easily visible for all ages" requirement. */
    .stApp {{
        background: linear-gradient(160deg, #F6F5FB 0%, #EFEAFB 35%, #E6F3F1 100%);
        font-family: {FONT_STACK};
    }}

    /* ---------- Hero / page header ---------- */
    .app-hero {{
        background: {GRADIENT_MAIN};
        border-radius: 16px;
        padding: 30px 32px;
        margin-bottom: 24px;
        box-shadow: 0 6px 18px rgba(91, 60, 196, 0.28);
        text-align: center;
    }}
    .app-hero.ceo {{
        background: {GRADIENT_CEO};
        box-shadow: 0 6px 18px rgba(59, 38, 128, 0.32);
    }}
    .app-hero h1 {{
        color: #ffffff;
        margin: 0 0 6px 0;
        font-size: 28px;
        letter-spacing: 0.2px;
        text-align: center;
    }}
    .app-hero p {{
        color: rgba(255,255,255,0.94);
        margin: 0;
        font-size: 14.5px;
        text-align: center;
    }}

    /* ---------- Sticky bottom main nav (mobile-style tab bar) ---------- */
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
        box-shadow: 0 -4px 14px rgba(0,0,0,0.08);
    }}

    /* ---------- Cards ---------- */
    .p2p-card {{
        background: {CARD_BG};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 2px 10px rgba(91, 60, 196, 0.08);
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
    .p2p-badge.success {{ background: {SUCCESS}; }}
    .p2p-badge.warning {{ background: {WARNING}; color: {TEXT_DARK}; }}

    /* ---------- Calendar month grid ---------- */
    .p2p-calendar {{
        background: {CARD_BG};
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 2px 10px rgba(91, 60, 196, 0.08);
        margin-bottom: 18px;
    }}
    .p2p-calendar-header {{
        text-align: center;
        font-weight: 700;
        font-size: 18px;
        color: {TEXT_DARK};
        margin-bottom: 10px;
    }}
    .p2p-calendar-grid {{
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 4px;
    }}
    .p2p-calendar-daylabel {{
        text-align: center;
        font-size: 11px;
        font-weight: 700;
        color: {TEXT_MUTED};
        padding-bottom: 4px;
    }}
    .p2p-calendar-day {{
        min-height: 56px;
        border-radius: 10px;
        background: #F8F8FC;
        padding: 4px 6px;
        font-size: 12px;
        color: {TEXT_MUTED};
        border: 1px solid #ECEFF2;
    }}
    .p2p-calendar-day.empty {{
        background: transparent;
        border: none;
    }}
    .p2p-calendar-day.has-event {{
        background: linear-gradient(160deg, #EFEAFB 0%, #E6F3F1 100%);
        border: 1px solid {PRIMARY};
    }}
    .p2p-calendar-day .daynum {{
        font-weight: 700;
        color: {TEXT_DARK};
    }}
    .p2p-calendar-day .event-dot {{
        display: block;
        font-size: 10px;
        color: {PRIMARY};
        font-weight: 600;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* ---------- Event detail card ---------- */
    .p2p-event-card {{
        background: {CARD_BG};
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 16px;
        box-shadow: 0 4px 14px rgba(91, 60, 196, 0.10);
        border: 1px solid #ECEFF2;
    }}
    .p2p-event-card .event-banner {{
        background: {GRADIENT_MAIN};
        padding: 16px 20px;
    }}
    .p2p-event-card .event-banner h3 {{
        color: #fff;
        margin: 0;
        font-size: 18px;
        text-align: center;
    }}
    .p2p-event-card .event-banner .event-date {{
        color: rgba(255,255,255,0.92);
        font-size: 13px;
        text-align: center;
        margin-top: 2px;
    }}
    .p2p-event-card .event-body {{
        padding: 14px 20px;
        color: {TEXT_DARK};
        font-size: 14px;
    }}

    /* Tighten default Streamlit spacing a bit for an app-like feel */
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 0.5rem;
    }}

    /* Center any standard page title used outside the hero component */
    h1, h2.p2p-centered {{
        text-align: center;
    }}
</style>
"""

