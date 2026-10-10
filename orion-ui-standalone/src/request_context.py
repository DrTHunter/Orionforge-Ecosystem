"""Per-request user identity, shared by the web app and ``src/`` modules.

The web app's AuthMiddleware sets ``current_user_id`` for each request;
modules under ``src/`` read it to find per-user overrides (e.g. memory
profiles) without importing the web layer.
"""

import contextvars
import re
from pathlib import Path
from typing import Optional

current_user_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "current_user_id", default="__local__"
)

# Whose copy of the shared, operator-style data a request (or a background loop) works in:
# None for the owner (admins, or local single-user mode), who keeps the global files;
# a user id for everyone else, who gets their own under data/users/<uid>/. Set by the
# web app's middleware next to current_user_id. The inbox, the memory tool and the AGI
# loop read it, so nobody sees another user's copy.
data_scope: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("data_scope", default=None)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_SAFE_ID = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")  # same rule as web/user_data.py


def scope_dir(*parts: str, create: bool = False) -> Optional[Path]:
    """``data/users/<uid>/<parts>`` for a scoped (non-owner) user, or None for the owner."""
    uid = data_scope.get()
    if not uid or uid == "__local__" or not _SAFE_ID.match(uid):
        return None
    path = _DATA_DIR.joinpath("users", uid, *parts)
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def user_config_dir(create: bool = False) -> Optional[Path]:
    """``data/users/<uid>/config`` for the current signed-in user.

    Returns None in local single-user mode (``__local__``), where the global
    ``config/`` files are edited directly.
    """
    uid = current_user_id.get()
    if not uid or uid == "__local__" or not _SAFE_ID.match(uid):
        return None
    path = _DATA_DIR / "users" / uid / "config"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path
