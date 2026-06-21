"""
Single source of truth for color/theme. Every page imports from here
so the gradient/accent stays consistent app-wide and changing the
brand color later is a one-file edit.

This palette was widened for visibility across a broad age range
(11-year-olds' parents through 27-year-olds' parents, plus the CEO):
deeper, more saturated hues with stronger contrast against white text,
rather than the earlier muted slate/sky-blue pairing, which read a
little flat/corporate for a community-feeling app.
"""

"""
Single source of truth for color/theme. Every page imports from here
so the gradient/accent stays consistent app-wide and changing the
brand color later is a one-file edit.

This palette was widened for visibility across a broad age range
(11-year-olds' parents through 65-year-olds' parents, plus the CEO):
deeper, more saturated hues with stronger contrast against white text,
rather than the earlier muted slate/sky-blue pairing, which read a
little flat/corporate for a community-feeling app.
"""

PRIMARY = "#5B3CC4"        # confident violet-indigo — distinctive, not generic "app blue"
PRIMARY_DARK = "#3B2680"
PRIMARY_LIGHT = "#8B6CE0"
ACCENT = "#0F7A70"         # deep teal — chosen so white text stays readable (WCAG AA, 5.2:1) anywhere on the hero gradient, not just near PRIMARY
ACCENT_LIGHT = "#3FB5A8"
WARM_ACCENT = "#C73838"    # warm red, used for CTAs/highlights/urgent badges — also WCAG AA (5.2:1) with white text
GOLD_ACCENT = "#E8A33D"    # used for streaks/highlights/celebratory touches in chat & profile

BACKGROUND = "#F6F5FB"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2733"
TEXT_MUTED = "#5A6679"
SUCCESS = "#2FA86A"
DANGER = "#E2403A"
WARNING = "#E8A33D"

GRADIENT_MAIN = f"linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%)"
GRADIENT_WARM = f"linear-gradient(135deg, {WARM_ACCENT} 0%, #FFB86B 100%)"
GRADIENT_CEO = f"linear-gradient(135deg, {PRIMARY_DARK} 0%, {PRIMARY} 55%, {ACCENT} 100%)"
GRADIENT_PROFILE = f"linear-gradient(160deg, {PRIMARY} 0%, {PRIMARY_LIGHT} 55%, {ACCENT_LIGHT} 100%)"
GRADIENT_CHAT_BG = f"linear-gradient(180deg, #FBFAFF 0%, #F1ECFA 100%)"
GRADIENT_APP_BG = "linear-gradient(165deg, #F6F5FB 0%, #EFEAFB 38%, #E6F3F1 100%)"

FONT_STACK = "'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"

