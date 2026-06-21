"""
Returns the global CSS block, injected once via st.markdown(unsafe_allow_html=True)
at app startup. Keeping this as a function (not raw CSS in every page)
means every page gets identical styling automatically.

This is a full design-system pass, not a light theme tweak: it hides
Streamlit's own chrome (header bar, footer, menu — the toolbar itself
is also hidden at the framework level via .streamlit/config.toml,
this CSS catches what that setting doesn't reach), restyles every
base widget (buttons, inputs, tabs, forms, toggles) so nothing reads
as "stock Streamlit gray," and adds the custom components the app
actually needs: a real profile header with a framed avatar, livelier
gradient-driven chat bubbles, and a polished calendar/event system.
Mobile-first sizing throughout — the top nav and hero stay legible
and tappable on a narrow phone screen, not just a desktop window.
"""
from styles.theme import (
    PRIMARY, PRIMARY_DARK, PRIMARY_LIGHT, ACCENT, ACCENT_LIGHT,
    WARM_ACCENT, GOLD_ACCENT, BACKGROUND, CARD_BG, TEXT_DARK, TEXT_MUTED,
    SUCCESS, WARNING, DANGER, GRADIENT_MAIN, GRADIENT_CEO, GRADIENT_PROFILE,
    GRADIENT_CHAT_BG, FONT_STACK,
)


def get_global_css() -> str:
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* HIDE STREAMLIT'S OWN CHROME */
    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; height: 0; }}
    header[data-testid="stHeader"] {{
        background: transparent;
        height: 0;
    }}
    div[data-testid="stToolbar"] {{ display: none; }}
    div[data-testid="stDecoration"] {{ display: none; }}
    div[data-testid="stStatusWidget"] {{ display: none; }}
    a[href*="streamlit.io"] {{ display: none !important; }}

    /* APP-WIDE BASE */
    html, body, [class*="css"] {{
        font-family: {FONT_STACK} !important;
    }}
    .stApp {{
        background: linear-gradient(165deg, #F6F5FB 0%, #EFEAFB 30%, #E6F3F1 65%, #F0EAFB 100%);
        background-size: 200% 200%;
        animation: p2pBgDrift 28s ease-in-out infinite;
    }}
    @keyframes p2pBgDrift {{
        0%   {{ background-position: 0% 0%; }}
        50%  {{ background-position: 100% 60%; }}
        100% {{ background-position: 0% 0%; }}
    }}
    /* Width targeting uses data-testid selectors (Streamlit's stated
       stable API surface) ALONGSIDE class/element selectors from
       older DOM versions, since plain class-name targeting has been
       reported to stop working reliably across Streamlit version
       upgrades — this covers every plausible version's markup so it
       survives version changes either way. */
    div[data-testid="stAppViewContainer"] .block-container,
    div[data-testid="stMainBlockContainer"],
    section.main > div.block-container,
    .appview-container .block-container,
    .block-container {{
        padding-top: 0.6rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 1600px !important;
        margin: 0 auto !important;
        width: 100% !important;
    }}
    /* Some Streamlit versions wrap content in an additional outer
       element that itself constrains width — neutralize that too. */
    div[data-testid="stAppViewContainer"],
    section.main {{
        max-width: 100% !important;
        width: 100% !important;
    }}
    /* Tablet: a bit narrower than full desktop width, still roomy */
    @media (max-width: 900px) {{
        div[data-testid="stAppViewContainer"] .block-container,
        div[data-testid="stMainBlockContainer"],
        .block-container {{
            max-width: 100% !important;
            padding-left: 1.2rem !important;
            padding-right: 1.2rem !important;
        }}
    }}
    /* Phone: full width, minimal side padding so nothing feels cramped */
    @media (max-width: 480px) {{
        div[data-testid="stAppViewContainer"] .block-container,
        div[data-testid="stMainBlockContainer"],
        .block-container {{
            max-width: 100% !important;
            padding-left: 0.7rem !important;
            padding-right: 0.7rem !important;
        }}
    }}
    h1, h2, h3, h4 {{
        font-family: {FONT_STACK} !important;
        color: {TEXT_DARK};
        font-weight: 700;
    }}
    p, span, label, div {{
        font-family: {FONT_STACK};
    }}

    /* STICKY TOP NAV */
    .p2p-top-nav {{
        position: sticky;
        top: 0;
        z-index: 999;
        display: flex;
        justify-content: space-around;
        align-items: center;
        background: rgba(255,255,255,0.92);
        backdrop-filter: blur(8px);
        border-bottom: 1px solid rgba(91,60,196,0.10);
        border-radius: 0 0 18px 18px;
        padding: 8px 4px;
        margin: -0.4rem -0.2rem 16px -0.2rem;
        box-shadow: 0 4px 20px rgba(91,60,196,0.10);
    }}
    .p2p-top-nav .stButton button {{
        background: transparent;
        border: none;
        color: {TEXT_MUTED};
        font-weight: 600;
        font-size: 13px;
        padding: 8px 4px;
        border-radius: 12px;
        box-shadow: none;
        transition: all 0.15s ease;
    }}
    .p2p-top-nav .stButton button:hover {{
        background: rgba(91,60,196,0.08);
        color: {PRIMARY};
        transform: none;
    }}
    @media (max-width: 480px) {{
        .p2p-top-nav .stButton button {{ font-size: 11px; padding: 6px 2px; }}
    }}

    /* Responsive nav switch: show the full tab row on tablet/desktop,
       show the hamburger row + collapsible menu on phones. Exactly
       one of the two is visible at any given width. */
    .p2p-nav-desktop-row {{ display: block; }}
    .p2p-nav-mobile-row {{ display: none; }}
    .p2p-nav-mobile-menu {{ display: none; }}
    @media (max-width: 640px) {{
        .p2p-nav-desktop-row {{ display: none; }}
        .p2p-nav-mobile-row {{ display: block; }}
        .p2p-nav-mobile-menu {{ display: block; }}
    }}

    .p2p-nav-mobile-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 4px 8px;
    }}
    @media (max-width: 640px) {{
        .p2p-nav-mobile-row {{ display: flex; }}
    }}
    .p2p-nav-mobile-current {{
        font-weight: 700;
        font-size: 15px;
        color: {TEXT_DARK};
    }}
    .p2p-top-nav .p2p-nav-mobile-row .stButton button {{
        background: {GRADIENT_MAIN};
        color: #fff;
        font-size: 18px;
        border-radius: 10px;
        width: 42px;
        height: 38px;
        padding: 0;
    }}
    .p2p-nav-mobile-menu {{
        background: {CARD_BG};
        border-radius: 0 0 16px 16px;
        padding: 6px 10px 10px;
        border-top: 1px solid rgba(91,60,196,0.08);
    }}
    .p2p-nav-mobile-menu .stButton button {{
        text-align: left;
        justify-content: flex-start;
        background: transparent;
        color: {TEXT_MUTED};
        font-weight: 600;
        font-size: 14px;
        padding: 10px 12px;
        margin-bottom: 2px;
    }}
    .p2p-nav-mobile-menu .stButton button:hover {{
        background: rgba(91,60,196,0.08);
        color: {PRIMARY};
    }}

    /* HERO / PAGE HEADER */
    .app-hero {{
        background: {GRADIENT_MAIN};
        border-radius: 20px;
        padding: 28px 24px;
        margin-bottom: 22px;
        box-shadow: 0 10px 28px rgba(91, 60, 196, 0.30);
        text-align: center;
        position: relative;
        overflow: hidden;
    }}
    .app-hero::before {{
        content: "";
        position: absolute;
        top: -40%;
        right: -20%;
        width: 60%;
        height: 180%;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
        transform: rotate(15deg);
    }}
    .app-hero.ceo {{
        background: {GRADIENT_CEO};
        box-shadow: 0 10px 28px rgba(59, 38, 128, 0.34);
    }}
    .app-hero h1 {{
        color: #ffffff !important;
        margin: 0 0 6px 0;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: 0.2px;
        text-align: center;
        position: relative;
        z-index: 1;
    }}
    .app-hero p {{
        color: rgba(255,255,255,0.94) !important;
        margin: 0;
        font-size: 14px;
        text-align: center;
        position: relative;
        z-index: 1;
    }}

    /* PROFILE HEADER */
    .p2p-profile-header {{
        background: {GRADIENT_PROFILE};
        border-radius: 24px;
        padding: 32px 20px 24px;
        margin-bottom: 22px;
        text-align: center;
        box-shadow: 0 12px 30px rgba(91,60,196,0.28);
        position: relative;
        overflow: hidden;
    }}
    .p2p-profile-header::before {{
        content: "";
        position: absolute;
        top: -50%;
        left: -10%;
        width: 70%;
        height: 200%;
        background: rgba(255,255,255,0.07);
        border-radius: 50%;
    }}
    .p2p-avatar-frame {{
        width: 108px;
        height: 108px;
        margin: 0 auto 14px;
        border-radius: 50%;
        background: #ffffff;
        padding: 4px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.22), 0 0 0 4px rgba(255,255,255,0.35);
        position: relative;
        z-index: 1;
    }}
    .p2p-avatar-img {{
        width: 100%;
        height: 100%;
        border-radius: 50%;
        display: block;
        object-fit: cover;
    }}
    .p2p-profile-header .p2p-profile-name {{
        color: #ffffff;
        font-size: 22px;
        font-weight: 800;
        margin: 0;
        position: relative;
        z-index: 1;
    }}
    .p2p-profile-header .p2p-profile-sub {{
        color: rgba(255,255,255,0.92);
        font-size: 13.5px;
        margin: 4px 0 0;
        position: relative;
        z-index: 1;
    }}
    .p2p-profile-header .p2p-profile-badges {{
        margin-top: 12px;
        position: relative;
        z-index: 1;
    }}

    /* CARDS */
    .p2p-card {{
        background: {CARD_BG};
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 3px 14px rgba(91, 60, 196, 0.09);
        border: 1px solid #ECEFF2;
        transition: box-shadow 0.2s ease;
    }}
    .p2p-card:hover {{
        box-shadow: 0 6px 20px rgba(91, 60, 196, 0.14);
    }}
    .p2p-card h3 {{ margin-top: 0; color: {TEXT_DARK}; }}
    .p2p-card p {{ color: {TEXT_MUTED}; }}

    /* CHAT */
    .p2p-chat-bubble {{
        background: #ffffff;
        border-radius: 16px 16px 16px 4px;
        padding: 10px 14px;
        margin-bottom: 10px;
        max-width: 82%;
        font-size: 14px;
        color: {TEXT_DARK};
        box-shadow: 0 2px 8px rgba(91,60,196,0.08);
        border-left: 3px solid {PRIMARY_LIGHT};
        animation: p2pFadeIn 0.25s ease;
    }}
    .p2p-chat-bubble .sender {{
        font-weight: 800;
        background: {GRADIENT_MAIN};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 12px;
        margin-bottom: 2px;
        display: block;
    }}
    .p2p-chat-bubble.system {{
        background: linear-gradient(135deg, #FFF4ED 0%, #FFEAE0 100%);
        border-left: 3px solid {WARM_ACCENT};
        color: {TEXT_DARK};
    }}
    @keyframes p2pFadeIn {{
        from {{ opacity: 0; transform: translateY(4px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* SUB-MENU TOOL TILES */
    .p2p-submenu-heading {{
        font-size: 18px;
        font-weight: 800;
        color: {TEXT_DARK};
        margin: 8px 0 14px;
        text-align: center;
    }}
    .p2p-submenu-tile {{
        background: {CARD_BG};
        border-radius: 18px;
        padding: 16px 18px 14px;
        margin-bottom: 12px;
        border: 1px solid #ECEFF2;
        box-shadow: 0 3px 14px rgba(91, 60, 196, 0.08);
        transition: box-shadow 0.2s ease, transform 0.15s ease;
    }}
    .p2p-submenu-tile:hover {{
        box-shadow: 0 8px 22px rgba(91, 60, 196, 0.16);
        transform: translateY(-1px);
    }}
    .p2p-submenu-tile-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }}
    .p2p-submenu-icon {{
        flex-shrink: 0;
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: {GRADIENT_MAIN};
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        box-shadow: 0 3px 10px rgba(91,60,196,0.25);
    }}
    .p2p-submenu-title {{
        font-weight: 700;
        color: {TEXT_DARK};
        font-size: 15px;
    }}
    .p2p-submenu-desc {{
        color: {TEXT_MUTED};
        font-size: 12.5px;
        margin-top: 1px;
    }}
    div[data-testid="stExpander"] {{
        border-radius: 16px !important;
        border: 1px solid #ECEFF2 !important;
        box-shadow: 0 2px 10px rgba(91,60,196,0.06);
        overflow: hidden;
    }}
    div[data-testid="stExpander"] summary {{
        font-weight: 700;
        color: {TEXT_DARK};
    }}

    /* BADGES */
    .p2p-badge {{
        display: inline-block;
        background: {ACCENT};
        color: #ffffff;
        border-radius: 999px;
        padding: 4px 12px;
        font-size: 11px;
        font-weight: 700;
        margin: 2px 4px 2px 0;
        letter-spacing: 0.2px;
    }}
    .p2p-badge.warm {{ background: {WARM_ACCENT}; }}
    .p2p-badge.success {{ background: {SUCCESS}; }}
    .p2p-badge.warning {{ background: {WARNING}; color: {TEXT_DARK}; }}
    .p2p-badge.gold {{ background: {GOLD_ACCENT}; color: {TEXT_DARK}; }}
    .p2p-badge.on-gradient {{
        background: rgba(255,255,255,0.22);
        color: #ffffff;
        backdrop-filter: blur(4px);
    }}

    /* CALENDAR */
    .p2p-calendar {{
        background: {CARD_BG};
        border-radius: 18px;
        padding: 16px 14px;
        box-shadow: 0 3px 14px rgba(91, 60, 196, 0.09);
        margin-bottom: 18px;
        border: 1px solid #ECEFF2;
    }}
    .p2p-calendar-header {{
        text-align: center;
        font-weight: 800;
        font-size: 17px;
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
        font-size: 10.5px;
        font-weight: 700;
        color: {TEXT_MUTED};
        padding-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    .p2p-calendar-day {{
        min-height: 52px;
        border-radius: 12px;
        background: #F8F8FC;
        padding: 4px 5px;
        font-size: 11.5px;
        color: {TEXT_MUTED};
        border: 1px solid #ECEFF2;
        transition: transform 0.15s ease;
    }}
    .p2p-calendar-day.empty {{ background: transparent; border: none; }}
    .p2p-calendar-day.has-event {{
        background: linear-gradient(160deg, #EFEAFB 0%, #E6F3F1 100%);
        border: 1.5px solid {PRIMARY};
        box-shadow: 0 2px 8px rgba(91,60,196,0.15);
    }}
    .p2p-calendar-day .daynum {{ font-weight: 800; color: {TEXT_DARK}; }}
    .p2p-calendar-day .event-dot {{
        display: block;
        font-size: 9.5px;
        color: {PRIMARY};
        font-weight: 700;
        margin-top: 2px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* EVENT CARDS */
    .p2p-event-card {{
        background: {CARD_BG};
        border-radius: 18px;
        overflow: hidden;
        margin-bottom: 16px;
        box-shadow: 0 6px 18px rgba(91, 60, 196, 0.12);
        border: 1px solid #ECEFF2;
    }}
    .p2p-event-card .event-banner {{
        background: {GRADIENT_MAIN};
        padding: 18px 20px;
    }}
    .p2p-event-card .event-banner h3 {{
        color: #fff !important;
        margin: 0;
        font-size: 17px;
        text-align: center;
    }}
    .p2p-event-card .event-banner .event-date {{
        color: rgba(255,255,255,0.92);
        font-size: 12.5px;
        text-align: center;
        margin-top: 2px;
        font-weight: 600;
    }}
    .p2p-event-card .event-body {{
        padding: 14px 20px;
        color: {TEXT_DARK};
        font-size: 14px;
    }}

    /* WIDGET RESTYLING */
    .stButton button, .stFormSubmitButton button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        border: none !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease !important;
        box-shadow: 0 2px 8px rgba(91,60,196,0.10) !important;
    }}
    .stButton button[kind="primary"], .stFormSubmitButton button[kind="primary"] {{
        background: {GRADIENT_MAIN} !important;
        color: #fff !important;
    }}
    .stButton button[kind="secondary"], .stFormSubmitButton button[kind="secondary"] {{
        background: #ffffff !important;
        color: {PRIMARY} !important;
        border: 1.5px solid {PRIMARY_LIGHT} !important;
    }}
    .stButton button:hover, .stFormSubmitButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(91,60,196,0.20) !important;
    }}

    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        border-radius: 12px !important;
        border: 1.5px solid #E4E1F2 !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }}
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 3px rgba(91,60,196,0.12) !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        border-radius: 12px !important;
        border: 1.5px solid #E4E1F2 !important;
    }}

    div[data-testid="stForm"] {{
        background: rgba(255,255,255,0.5);
        border-radius: 18px;
        padding: 18px;
        border: 1px solid rgba(91,60,196,0.08);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: rgba(91,60,196,0.06);
        border-radius: 14px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        font-weight: 600;
        color: {TEXT_MUTED};
    }}
    .stTabs [aria-selected="true"] {{
        background: #ffffff !important;
        color: {PRIMARY} !important;
        box-shadow: 0 2px 6px rgba(91,60,196,0.12);
    }}

    div[data-testid="stToggle"] label div[data-checked="true"] {{
        background-color: {PRIMARY} !important;
    }}

    div[data-testid="stMetric"] {{
        background: #ffffff;
        border-radius: 14px;
        padding: 12px 14px;
        border: 1px solid #ECEFF2;
        box-shadow: 0 2px 8px rgba(91,60,196,0.06);
    }}

    .stRadio div[role="radiogroup"] label {{
        background: #ffffff;
        border-radius: 12px;
        border: 1.5px solid #ECEFF2;
        padding: 8px 12px;
        margin-bottom: 6px;
        transition: border-color 0.15s ease;
    }}

    /* AMBIENT FLOATING DECORATION — subtle movement across the
       screen, purely decorative, low opacity so it never competes
       with readability. Fixed position so it drifts behind content
       regardless of scroll. */
    .stApp::before, .stApp::after {{
        content: "";
        position: fixed;
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        filter: blur(2px);
    }}
    .stApp::before {{
        width: 180px;
        height: 180px;
        top: 8%;
        left: -60px;
        background: radial-gradient(circle, rgba(91,60,196,0.10) 0%, transparent 70%);
        animation: p2pFloatA 18s ease-in-out infinite;
    }}
    .stApp::after {{
        width: 220px;
        height: 220px;
        bottom: 10%;
        right: -80px;
        background: radial-gradient(circle, rgba(15,122,112,0.10) 0%, transparent 70%);
        animation: p2pFloatB 22s ease-in-out infinite;
    }}
    @keyframes p2pFloatA {{
        0%, 100% {{ transform: translate(0, 0); }}
        50% {{ transform: translate(40px, 60px); }}
    }}
    @keyframes p2pFloatB {{
        0%, 100% {{ transform: translate(0, 0); }}
        50% {{ transform: translate(-50px, -40px); }}
    }}

    /* TIME-OF-DAY SCENES — brief (~3s) decorative overlays, never
       block interaction, never affect layout/scroll. Self-contained:
       fade in, play, fade out, collapse to zero height. */
    .p2p-scene-overlay {{
        position: fixed;
        top: 0; left: 0; right: 0;
        height: 100vh;
        pointer-events: none;
        z-index: 9000;
        overflow: hidden;
        animation: p2pSceneLifecycle 3s ease forwards;
    }}
    @keyframes p2pSceneLifecycle {{
        0%   {{ opacity: 0; }}
        10%  {{ opacity: 1; }}
        80%  {{ opacity: 1; }}
        100% {{ opacity: 0; height: 0; }}
    }}

    .p2p-scene-midnight {{
        background: linear-gradient(180deg, rgba(10,8,30,0.55) 0%, rgba(20,15,45,0.25) 60%, transparent 100%);
    }}
    .p2p-scene-comet {{
        position: absolute;
        top: 12%;
        left: -10%;
        width: 6px;
        height: 6px;
        background: #FFFFFF;
        border-radius: 50%;
        box-shadow: 0 0 12px 4px rgba(255,255,255,0.9), -40px 4px 18px rgba(180,200,255,0.5);
        animation: p2pCometFly 2.6s ease-in forwards;
    }}
    .p2p-scene-comet::after {{
        content: "";
        position: absolute;
        top: 1px;
        right: 4px;
        width: 140px;
        height: 2px;
        background: linear-gradient(90deg, rgba(255,255,255,0.9), transparent);
        transform: rotate(8deg);
    }}
    @keyframes p2pCometFly {{
        0%   {{ transform: translate(0, 0); opacity: 0; }}
        12%  {{ opacity: 1; }}
        100% {{ transform: translate(130vw, 55vh); opacity: 0.2; }}
    }}
    .p2p-scene-stars {{
        position: absolute;
        inset: 0;
        background-image:
            radial-gradient(1.5px 1.5px at 20% 30%, white, transparent),
            radial-gradient(1.5px 1.5px at 70% 15%, white, transparent),
            radial-gradient(1px 1px at 85% 45%, white, transparent),
            radial-gradient(1px 1px at 40% 70%, white, transparent),
            radial-gradient(1.5px 1.5px at 55% 25%, white, transparent);
        opacity: 0.6;
    }}

    .p2p-scene-noon {{
        background: linear-gradient(180deg, rgba(173,216,235,0.30) 0%, rgba(220,240,250,0.12) 70%, transparent 100%);
    }}
    .p2p-scene-plane {{
        position: absolute;
        top: 14%;
        left: -8%;
        font-size: 30px;
        animation: p2pPlaneFly 2.8s ease-in-out forwards;
    }}
    @keyframes p2pPlaneFly {{
        0%   {{ transform: translate(0, 0) rotate(0deg); opacity: 0; }}
        15%  {{ opacity: 1; }}
        100% {{ transform: translate(125vw, 8vh) rotate(2deg); opacity: 0.3; }}
    }}
    .p2p-scene-cloud {{
        position: absolute;
        width: 90px;
        height: 30px;
        background: rgba(255,255,255,0.55);
        border-radius: 50px;
        filter: blur(1px);
        animation: p2pCloudDrift 3s ease-in-out forwards;
    }}
    .p2p-scene-cloud-1 {{ top: 22%; left: 10%; animation-delay: 0.2s; }}
    .p2p-scene-cloud-2 {{ top: 35%; left: 55%; animation-delay: 0.5s; width: 70px; height: 24px; }}
    @keyframes p2pCloudDrift {{
        0%   {{ transform: translateX(0); opacity: 0; }}
        20%  {{ opacity: 0.8; }}
        100% {{ transform: translateX(40px); opacity: 0; }}
    }}

    /* PAGE FOOTER */
    .p2p-page-footer {{
        text-align: center;
        margin-top: 32px;
        padding: 18px 0 8px;
        border-top: 1px solid rgba(91,60,196,0.10);
        color: {TEXT_MUTED};
        font-size: 12px;
    }}
    .p2p-page-footer .p2p-footer-brand {{
        font-weight: 700;
        background: {GRADIENT_MAIN};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 13px;
    }}

    /* PAGE FOOTER — reusable closing element so pages don't just end
       abruptly with the last button on screen. */
    .p2p-page-footer {{
        text-align: center;
        margin-top: 32px;
        padding: 18px 12px;
        border-top: 1px solid rgba(91,60,196,0.10);
    }}
    .p2p-page-footer-brand {{
        font-weight: 800;
        font-size: 14px;
        background: {GRADIENT_MAIN};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .p2p-page-footer-tag {{
        font-size: 11.5px;
        color: {TEXT_MUTED};
        margin-top: 2px;
    }}

    /* MOBILE TUNING */
    @media (max-width: 480px) {{
        .app-hero {{ padding: 22px 16px; border-radius: 16px; }}
        .app-hero h1 {{ font-size: 21px; }}
        .app-hero p {{ font-size: 12.5px; }}
        .p2p-profile-header {{ padding: 26px 14px 18px; }}
        .p2p-avatar-frame {{ width: 86px; height: 86px; }}
        .p2p-card {{ padding: 14px 16px; }}
        .block-container {{ padding-left: 0.8rem; padding-right: 0.8rem; }}
    }}
</style>
"""
