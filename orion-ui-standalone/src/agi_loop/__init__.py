"""AGI Loop — a continuously running inner world for one agent.

    channels  → raw signals the agent can't author (time, energy, body, door, bench)
    prediction→ beliefs per signal; error becomes surprise; surprise drives learning
    world     → the field: focus anywhere, things arranged by relatedness, HUD gauges,
                alerts, fading, finite capacity, emergent mood
    embedding → relatedness (MiniLM, with a hashed fallback)
    daemon    → wall-time process: sense → update → predict → attend → feel →
                render → think/act → guard → record → sleep (woken by messages)
    tools     → attend, reply, loop_control, workbench (loop-only tools)
"""

import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

from src.request_context import data_scope

from .config import LoopConfig
from .daemon import Completion, Host, LoopDaemon
from .embedding import HashEmbedder, SentenceEmbedder
from .world import InnerWorld

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = _PROJECT_ROOT / "config" / "agi_loop.json"
DATA_DIR = _PROJECT_ROOT / "data" / "orion" / "agi_loop"
USERS_DIR = _PROJECT_ROOT / "data" / "users"

# Each loop is its own agent with its own config, state and Linux machine.
# "supervisor" is the original loop and keeps its original paths; every other id
# gets agi_loop_<id>.json and data/orion/agi_loop_<id>/.
DEFAULT_LOOP = "supervisor"
LOOP_DEFAULT_AGENTS = {"supervisor": "supervisor", "k_os": "k_os"}

# Loops made with the wizard exist because their config file does. The id is part of a
# path and an env var name, so it's held to this shape.
LOOP_ID_RE = re.compile(r"^[a-z][a-z0-9_]{1,23}$")
_SAFE_UID = re.compile(r"^[a-zA-Z0-9_-]{1,128}$")

# ── Whose loops ──────────────────────────────────────────────────────
# request_context.data_scope says whose loops a request (or a running loop) works with:
# None is the owner, with the built-in loops and the global paths above; a user id is a
# signed-in user, whose loops live in data/users/<uid>/agi_loop/ with no built-ins. A
# loop's task inherits the scope it was started in, so it keeps working in its owner's.

_daemons: Dict[Tuple[Optional[str], str], LoopDaemon] = {}


def owner() -> Optional[str]:
    """The current scope: None for the owner, else the signed-in user's id."""
    uid = data_scope.get()
    return uid if uid and uid != "__local__" and _SAFE_UID.match(uid) else None


def _user_base() -> Optional[Path]:
    uid = owner()
    return USERS_DIR / uid / "agi_loop" if uid else None


def built_in() -> dict:
    """The loops this scope has without creating them: the owner's four, nobody else's."""
    return LOOP_DEFAULT_AGENTS if owner() is None else {}


def _custom_loop_ids() -> list:
    base = _user_base()
    if base is None:
        found = (p.stem[len("agi_loop_"):] for p in CONFIG_FILE.parent.glob("agi_loop_*.json"))
    else:
        found = (p.stem for p in (base / "config").glob("*.json"))
    return sorted(i for i in found if LOOP_ID_RE.match(i) and i not in built_in())


def default_loop() -> str:
    """The loop a page opens on: "supervisor" for the owner, a user's first loop, or "" when they have none."""
    if owner() is None:
        return DEFAULT_LOOP
    mine = _custom_loop_ids()
    return mine[0] if mine else ""


def normalize_loop_id(loop_id: Optional[str]) -> str:
    """Known loop ids only — the id becomes part of a path and an env var name."""
    fallback = default_loop()
    loop_id = (loop_id or fallback).strip().lower()
    if loop_id in built_in():
        return loop_id
    return loop_id if LOOP_ID_RE.match(loop_id) and loop_id in _custom_loop_ids() else fallback


def loop_ids() -> list:
    return list(built_in()) + _custom_loop_ids()


def _config_path(loop_id: str) -> Path:
    base = _user_base()
    if base is not None:
        return base / "config" / f"{loop_id}.json"
    return CONFIG_FILE if loop_id == DEFAULT_LOOP else CONFIG_FILE.with_name(f"agi_loop_{loop_id}.json")


def _data_path(loop_id: str) -> Path:
    base = _user_base()
    if base is not None:
        return base / "data" / loop_id
    return DATA_DIR if loop_id == DEFAULT_LOOP else DATA_DIR.with_name(f"agi_loop_{loop_id}")


def shared_dir() -> Path:
    """Where this scope's loops share things: the group chat, its slab, tool requests."""
    base = _user_base()
    return base / "data" if base is not None else DATA_DIR.parent


def create_loop(loop_id: str, config: LoopConfig) -> str:
    """Register a new loop by writing its config. Raises ValueError for a bad or taken id."""
    loop_id = (loop_id or "").strip().lower()
    if not LOOP_ID_RE.match(loop_id):
        raise ValueError("Loop name must be 2–24 characters: lowercase letters, digits and _, starting with a letter")
    if loop_id in loop_ids():
        raise ValueError(f"A loop called '{loop_id}' already exists")
    path = _config_path(loop_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    config.save(path)
    return loop_id


def archive_dir() -> Path:
    """Where deleted loops go when they're archived rather than purged."""
    base = _user_base()
    return base / "archive" if base is not None else DATA_DIR.with_name("agi_loop_archive")


def delete_loop(loop_id: str, archive: bool = True) -> Optional[Path]:
    """Unregister a wizard-made loop by moving its config and data out of the way.

    ``archive`` moves both into ``archive_dir()/<id>-<UTC time>/`` (``config.json``
    and ``data/``) and returns that folder; otherwise both are removed for good.
    The caller stops the loop first. Raises ValueError for a built-in or unknown loop.
    """
    loop_id = (loop_id or "").strip().lower()
    if loop_id in built_in():
        raise ValueError(f"'{loop_id}' is a built-in loop and can't be deleted")
    if loop_id not in _custom_loop_ids():
        raise ValueError(f"There's no loop called '{loop_id}'")
    cfg, data = config_file(loop_id), data_dir(loop_id)
    _daemons.pop((owner(), loop_id), None)
    if not archive:
        if data.exists():
            shutil.rmtree(data)
        cfg.unlink(missing_ok=True)
        return None
    dest = archive_dir() / f"{loop_id}-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}"
    dest.mkdir(parents=True)
    if data.exists():
        shutil.move(str(data), str(dest / "data"))
    # The config goes last: the loop stops existing only once its data is safe.
    shutil.move(str(cfg), str(dest / "config.json"))
    return dest


ARCHIVE_NAME_RE = re.compile(r"^([a-z][a-z0-9_]{1,23})-(\d{8}T\d{6}Z)$")


def archived_loops() -> list:
    """Archived loops, newest first: ``[{name, id, archived_at, agent, path}]``."""
    root = archive_dir()
    found = []
    for p in root.iterdir() if root.exists() else ():
        m = ARCHIVE_NAME_RE.match(p.name)
        if not (m and p.is_dir() and (p / "config.json").exists()):
            continue
        agent = ""
        try:
            agent = LoopConfig.load(p / "config.json").agent
        except Exception:
            pass
        stamp = datetime.strptime(m.group(2), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        found.append({"name": p.name, "id": m.group(1), "archived_at": stamp.isoformat(),
                      "agent": agent, "path": p})
    return sorted(found, key=lambda a: a["archived_at"], reverse=True)


def restore_loop(archive_name: str, loop_id: Optional[str] = None) -> str:
    """Bring an archived loop back, under its old id or ``loop_id``. Returns the id.

    Raises ValueError for an unknown archive or a bad or taken id.
    """
    m = ARCHIVE_NAME_RE.match(archive_name or "")
    src = archive_dir() / (archive_name or "")
    if not (m and (src / "config.json").exists()):
        raise ValueError("That archive doesn't exist")
    loop_id = (loop_id or m.group(1)).strip().lower()
    if not LOOP_ID_RE.match(loop_id):
        raise ValueError("Loop name must be 2–24 characters: lowercase letters, digits and _, starting with a letter")
    if loop_id in loop_ids():
        raise ValueError(f"A loop called '{loop_id}' already exists. Restore it under another name")
    cfg_dest = _config_path(loop_id)
    data_dest = _data_path(loop_id)
    if data_dest.exists():
        raise ValueError(f"Leftover data for '{loop_id}' is in the way. Restore it under another name")
    cfg_dest.parent.mkdir(parents=True, exist_ok=True)
    data_dest.parent.mkdir(parents=True, exist_ok=True)
    if (src / "data").exists():
        shutil.move(str(src / "data"), str(data_dest))
    # The config goes last: the loop exists again once it's back.
    shutil.move(str(src / "config.json"), str(cfg_dest))
    shutil.rmtree(src, ignore_errors=True)
    return loop_id


def config_file(loop_id: str = DEFAULT_LOOP) -> Path:
    loop_id = normalize_loop_id(loop_id)
    if not loop_id:
        raise ValueError("No loop yet")
    return _config_path(loop_id)


def data_dir(loop_id: str = DEFAULT_LOOP) -> Path:
    loop_id = normalize_loop_id(loop_id)
    if not loop_id:
        raise ValueError("No loop yet")
    return _data_path(loop_id)


def load_config(loop_id: str = DEFAULT_LOOP) -> LoopConfig:
    """The saved config, or — for a loop that has none yet — defaults pointed at its own agent."""
    path = config_file(loop_id)
    if path.exists():
        return LoopConfig.load(path)
    cfg = LoopConfig()
    cfg.agent = built_in().get(normalize_loop_id(loop_id), DEFAULT_LOOP)
    return cfg


def get_daemon(loop_id: str = DEFAULT_LOOP) -> Optional[LoopDaemon]:
    return _daemons.get((owner(), normalize_loop_id(loop_id)))


def set_daemon(daemon: Optional[LoopDaemon], loop_id: str = DEFAULT_LOOP):
    key = (owner(), normalize_loop_id(loop_id))
    if daemon is None:
        _daemons.pop(key, None)
    else:
        _daemons[key] = daemon


def all_daemons() -> Dict[Tuple[Optional[str], str], LoopDaemon]:
    """Every loop in this process, across owners: {(owner, loop id): daemon}. For the watchdog."""
    return dict(_daemons)


def scopes_with_loops() -> list:
    """The signed-in users who have loops (for bringing them back after a restart)."""
    if not USERS_DIR.exists():
        return []
    return sorted(p.name for p in USERS_DIR.iterdir()
                  if _SAFE_UID.match(p.name) and (p / "agi_loop" / "config").is_dir())


__all__ = ["CONFIG_FILE", "DATA_DIR", "DEFAULT_LOOP", "LOOP_ID_RE", "all_daemons", "archive_dir", "archived_loops",
           "built_in", "config_file", "create_loop", "data_dir", "default_loop", "delete_loop", "load_config",
           "loop_ids", "normalize_loop_id", "owner", "restore_loop", "scopes_with_loops", "shared_dir",
           "Completion", "Host", "InnerWorld", "LoopConfig", "LoopDaemon",
           "HashEmbedder", "SentenceEmbedder", "get_daemon", "set_daemon"]
