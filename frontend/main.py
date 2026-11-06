"""Run from the repository root with: python -m frontend.main."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from nicegui import ui  # noqa: E402

from frontend.pages import accounts, analytics, assistant, auth, emissions, home  # noqa: E402, F401

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="CarbonDesk",
        host=os.getenv("FRONTEND_HOST", "127.0.0.1"),
        port=int(os.getenv("FRONTEND_PORT", "8080")),
        reload=os.getenv("FRONTEND_RELOAD", "False").lower() == "true",
        show=False,
        # Signs the browser cookie that links a visitor to their server-side session.
        storage_secret=os.getenv("FRONTEND_STORAGE_SECRET", "local-dev-only-change-me"),
    )
