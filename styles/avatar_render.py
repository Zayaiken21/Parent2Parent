"""
Renders an avatar as inline HTML (base64-encoded SVG inside an <img>
tag) instead of plain markdown image syntax. Markdown images can't be
wrapped in a styled <div> for a circular "profile picture" frame —
this can, since it returns a raw HTML string the caller embeds inside
whatever container markup they want.
"""
from __future__ import annotations

import base64
from pathlib import Path


def avatar_data_uri(file_path: str) -> str:
    """Reads an SVG file and returns a data: URI suitable for an
    <img src="..."> tag. Falls back to an empty string if the file is
    missing, so a broken avatar reference never crashes the page —
    callers should render a neutral placeholder when this is empty.
    """
    path = Path(file_path)
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def avatar_img_html(file_path: str, size_px: int = 96, css_class: str = "p2p-avatar-img") -> str:
    """Returns a ready-to-embed <img> tag for an avatar, or a neutral
    placeholder circle if the file can't be found."""
    uri = avatar_data_uri(file_path)
    if not uri:
        return (
            f'<div class="{css_class}" style="width:{size_px}px;height:{size_px}px;'
            f'background:#E0E0E8;display:flex;align-items:center;justify-content:center;'
            f'border-radius:50%;color:#8a93a1;font-size:{size_px // 3}px;">?</div>'
        )
    return f'<img src="{uri}" class="{css_class}" width="{size_px}" height="{size_px}" alt="avatar" />'
