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

from pathlib import Path
from typing import Dict, Optional

from .config import LoopConfig
from .daemon import Completion, Host, LoopDaemon
from .embedding import HashEmbedder, SentenceEmbedder
from .world import InnerWorld

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = _PROJECT_ROOT / "config" / "agi_loop.json"
DATA_DIR = _PROJECT_ROOT / "data" / "orion" / "agi_loop"

# Each loop is its own agent with its own config, state and Linux machine.
# "supervisor" is the original loop and keeps its original paths; every other id
# gets agi_loop_<id>.json and data/orion/agi_loop_<id>/.
DEFAULT_LOOP = "supervisor"
LOOP_DEFAULT_AGENTS = {"supervisor": "supervisor", "k_os": "k_os"}

_daemons: Dict[str, LoopDaemon] = {}


def normalize_loop_id(loop_id: Optional[str]) -> str:
    """Known loop ids only — the id becomes part of a path and an env var name."""
    loop_id = (loop_id or DEFAULT_LOOP).strip().lower()
    return loop_id if loop_id in LOOP_DEFAULT_AGENTS else DEFAULT_LOOP


def loop_ids() -> list:
    return list(LOOP_DEFAULT_AGENTS)


def config_file(loop_id: str = DEFAULT_LOOP) -> Path:
    loop_id = normalize_loop_id(loop_id)
    return CONFIG_FILE if loop_id == DEFAULT_LOOP else CONFIG_FILE.with_name(f"agi_loop_{loop_id}.json")


def data_dir(loop_id: str = DEFAULT_LOOP) -> Path:
    loop_id = normalize_loop_id(loop_id)
    return DATA_DIR if loop_id == DEFAULT_LOOP else DATA_DIR.with_name(f"agi_loop_{loop_id}")


def load_config(loop_id: str = DEFAULT_LOOP) -> LoopConfig:
    """The saved config, or — for a loop that has none yet — defaults pointed at its own agent."""
    path = config_file(loop_id)
    if path.exists():
        return LoopConfig.load(path)
    cfg = LoopConfig()
    cfg.agent = LOOP_DEFAULT_AGENTS[normalize_loop_id(loop_id)]
    return cfg


def get_daemon(loop_id: str = DEFAULT_LOOP) -> Optional[LoopDaemon]:
    return _daemons.get(normalize_loop_id(loop_id))


def set_daemon(daemon: Optional[LoopDaemon], loop_id: str = DEFAULT_LOOP):
    loop_id = normalize_loop_id(loop_id)
    if daemon is None:
        _daemons.pop(loop_id, None)
    else:
        _daemons[loop_id] = daemon


__all__ = ["CONFIG_FILE", "DATA_DIR", "DEFAULT_LOOP", "config_file", "data_dir", "load_config", "loop_ids",
           "normalize_loop_id", "Completion", "Host", "InnerWorld", "LoopConfig", "LoopDaemon",
           "HashEmbedder", "SentenceEmbedder", "get_daemon", "set_daemon"]
