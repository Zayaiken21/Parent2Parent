"""
Single source of truth for color/theme. Every page imports from here
so the gradient/accent stays consistent app-wide and changing the
brand color later is a one-file edit.
"""

PRIMARY = "#3D5A80"        # deep slate blue — calm, trustworthy
PRIMARY_DARK = "#293B53"
ACCENT = "#98C1D9"         # soft sky blue
WARM_ACCENT = "#EE6C4D"    # warm coral, used sparingly for CTAs/highlights
BACKGROUND = "#F4F6F8"
CARD_BG = "#FFFFFF"
TEXT_DARK = "#1F2733"
TEXT_MUTED = "#5A6679"
SUCCESS = "#3A8F5B"
DANGER = "#C0473F"
WARNING = "#D9A33C"

GRADIENT_MAIN = f"linear-gradient(135deg, {PRIMARY} 0%, {ACCENT} 100%)"
GRADIENT_WARM = f"linear-gradient(135deg, {WARM_ACCENT} 0%, {ACCENT} 100%)"

FONT_STACK = "'Helvetica Neue', Arial, sans-serif"
