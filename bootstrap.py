"""
Bootstraps environment variables from two possible sources, so every
other module can just do os.environ.get(...) regardless of where the
app is running:

1. Local dev: loads a .env file if present (simple manual parser —
   no extra dependency needed for something this small).
2. Streamlit Cloud: copies st.secrets into os.environ, since Cloud
   secrets aren't environment variables by default.

Import this ONCE, at the very top of streamlit_app.py, before any
other app module is imported.
"""
from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _load_streamlit_secrets() -> None:
    try:
        import streamlit as st
    except ImportError:
        return  # not running inside Streamlit at all (e.g. a standalone script)

    try:
        secrets = st.secrets
    except Exception:
        # No secrets.toml configured at all — totally normal for local
        # dev that only uses .env. Nothing to do.
        return

    for key, value in secrets.items():
        if isinstance(value, str):
            os.environ[key] = value
        elif hasattr(value, "items"):
            # Value pasted under a [section] heading instead of flat at
            # the top level — flatten one level so SHARD_1_SUPABASE_URL
            # still resolves even if someone organized secrets.toml with
            # headers like [shard_1].
            for sub_key, sub_value in value.items():
                if isinstance(sub_value, str):
                    os.environ[sub_key] = sub_value


def bootstrap_env() -> None:
    _load_dotenv()
    _load_streamlit_secrets()


bootstrap_env()
