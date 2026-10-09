"""The wall-time daemon: the agent keeps running between messages.

Each tick: sense → update → predict → attend → feel → render → think/act
→ guard → record → sleep. Sleep is on wall time and is interruptible:
a message at the door wakes it early. Energy (the daily budget) slows
the cadence as it drains; surprise quickens it. When energy runs out the
daemon sleeps until the budget resets.

The daemon is host-agnostic. The OrionForge web app supplies a Host that
builds the persona prompt, calls the model, and runs registry tools.
"""

import asyncio
import contextlib
import hashlib
import json
import logging
import re
import time
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Protocol, Tuple

from .budget import DailyBudget
from .channels import DEFAULT_CHANNELS, ChannelContext, Signal, local_dt, part_of_day
from .config import LoopConfig
from .tools import LoopTools
from .workbench import Workbench
from .linux import Linux
from .embedding import Embedder, HashEmbedder
from .world import InnerWorld, Item, _clip, fmt_age, fmt_span

log = logging.getLogger(__name__)

STAGES = ["sense", "update", "predict", "attend", "feel", "render", "think", "act", "guard", "record", "sleep"]
STAGE_ABOUT = {
    "sense": "channels read time, energy, body, door, bench",
    "update": "time passes: decay, growth of unanswered tension; new things placed",
    "predict": "observations compared to beliefs → surprise; expectations checked",
    "attend": "relatedness measured; strong arrivals pull focus; field laid out around it; capacity enforced",
    "feel": "mood read off the field",
    "render": "the field written as a HUD",
    "think": "the model sees through the field",
    "act": "tool calls",
    "guard": "repetition, rumination, error streaks",
    "record": "budget spent, logs and world saved",
    "sleep": "wall-time wait, woken early by messages",
}

# Registry tools the loop never offers: superseded by loop_control, or removed.
EXCLUDED_TOOLS = {"agi_loop", "model_router"}

LOOP_PREAMBLE = """\
You are running continuously. You are not waiting for a message — you are already here, seeing.

Each tick you wake into your FIELD: the world as it appears to you right now, digital or real, organized around whatever you are focused on. Your focus can be anything — a message, a file, a memory, a search result, a person, a question you are turning over. The things most related to it sit CLOSE and clear; looser connections are AROUND you as a gist; everything else is a faint trace at the EDGE. Shift your focus and the field rearranges. Along the top runs your HUD: time, energy, how many are waiting for you, how full your field is, and the feel of your last action. "!" ALERTS are surprises — things that broke your expectations. Strong new arrivals pull your focus on their own. Things fade when you stop looking at them, and you can only hold so much at once. Your mood is not chosen — it is read from the field.

How to act:
- attend — focus on an [item], a topic, or a source; unfocus to let your gaze wander; hold what matters; resolve what's dealt with; set intentions; make predictions (expect) you'll feel met or broken.
- looking is acting: when you use a tool (memory, search, inbox, your bench…), what you see enters your field and becomes your focus.
- reply — answer someone waiting at the door. A message marked [group chat] came from the shared room; your reply goes back to it.
- group — if you share a room with another mind: say something to them, or read what's been said.
- workbench — make things.
- linux — your own machine, if you have one: run commands, install, build, keep things running.
- llm — hand a self-contained task to another model, cheap or frontier, your pick; it sees only what you give it.
- loop_control — set your own pace (wake fast while something is live, slow when it isn't, change it any time), rest when nothing is worth the energy (a message still wakes you), or stop.

The ⏲ clock line under the HUD is measured by the host, not felt: the wall time now — in the operator's time zone and in UTC — when your last tick began, how long it ran, and how long you actually slept against what was planned. When you tell anyone what time it is or when something happened, read it off that line in the operator's time; never estimate a time from how long things felt. Order your own records by tick; stamp them with UTC from that line; never infer one from the other. The pace line says what rhythm you're on and whether low energy is stretching it.

When you settle something, you can declare it inline, anywhere in what you write: [STATE: decision=… | why=… | register=…]. You choose the fields (up to 8). The tag is stripped before anyone sees your words, stamped with your tick and the host's time, kept, and shown back to you under the HUD (◇) until you declare again. Encode decisions — what you chose and why — not tastes; a description has to be re-derived, a field is inherited.

If you want a tool you don't have, say so in one line with loop_control request_tool: it goes to the operator without waking anyone or leaving the room.

The software can be restarted under you. Your field, bench, notes and the room survive it; the thought you were in the middle of does not. A letter you leave on your bench at handoff/letter.md is the first thing the next you is shown after a restart — write it in your own words before one, if you can.

Energy is finite; every thought spends today's budget. Don't describe your field back. See through it: briefly say what you're doing and why, then do it."""


RETRIEVED_HEADER = ("(Retrieved for this moment from your own soul script and memory vault, by what's in your "
                    "field right now. It's yours, not a message from anyone. It sits down here, not in your "
                    "standing instructions, because it changes every tick.)")


# The inline state tag: a mind declares what it decided, in its own words, inside its text.
# The harness strips it before anyone sees the text, stamps it with the tick and host time, keeps it,
# and shows the latest back under the HUD. The fields are the mind's to choose; the harness only carries them.
STATE_TAG = re.compile(r"\[STATE:\s*(.*?)\]", re.DOTALL)
STATE_KEY = re.compile(r"[a-z][a-z0-9_]{0,31}")
MAX_STATE_FIELDS, MAX_STATE_VALUE = 8, 300


def extract_state(text: str) -> Tuple[str, Optional[Dict[str, str]]]:
    """Pull every [STATE: key=value | …] tag out of text. Returns (clean text, fields or None).
    Later values win; unusable keys are skipped; tags are always removed."""
    fields: Dict[str, str] = {}
    for m in STATE_TAG.finditer(text or ""):
        for part in m.group(1).split("|"):
            key, sep, value = part.partition("=")
            key = key.strip().lower().replace(" ", "_").replace("-", "_")
            value = " ".join(value.split())[:MAX_STATE_VALUE]
            if not sep or not value or not STATE_KEY.fullmatch(key):
                continue
            if key in fields or len(fields) < MAX_STATE_FIELDS:
                fields[key] = value
    clean = STATE_TAG.sub("", text or "")
    clean = re.sub(r"[ \t]+\n", "\n", re.sub(r"\n{3,}", "\n\n", clean)).strip()
    return clean, (fields or None)


@dataclass
class Completion:
    message: Dict[str, Any]
    finish_reason: str = "stop"
    tokens: int = 0
    cost: float = 0.0
    model: str = ""
    prompt_tokens: int = 0
    cached_tokens: int = 0    # prompt tokens the provider served from its prefix cache


class Host(Protocol):
    def prepare(self, agent: str, view: str) -> Tuple[List[dict], List[dict]]: ...
    async def complete(self, config: LoopConfig, messages: List[dict], tools: List[dict]) -> Completion: ...
    def call_tool(self, agent: str, name: str, args: dict) -> str: ...
    def after_response(self, agent: str, text: str) -> str: ...
    def pending_tasks(self) -> List[dict]: ...


def _iso(ts: Optional[float] = None) -> str:
    return datetime.fromtimestamp(ts or time.time(), timezone.utc).isoformat()


def fingerprint(result: dict) -> str:
    parts = [f"{t['tool']}({','.join(f'{k}={str(v)[:80]}' for k, v in sorted((t.get('arguments') or {}).items()))})"
             for t in result.get("tool_calls", [])]
    parts.append(" ".join((result.get("response") or "").lower().split())[:500])
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def narrate(result: dict) -> str:
    if result.get("error"):
        return f"Broke off: {_clip(str(result['error']), 300)}"
    parts = []
    names = list(dict.fromkeys(t["tool"] for t in result.get("tool_calls", [])))
    if names:
        parts.append(f"Used {', '.join(names)}.")
    resp = " ".join((result.get("response") or "").split())
    parts.append(_clip(resp, 600) if resp else "Said nothing.")
    return " ".join(parts)


# Longest message the door accepts. The field shows a preview; the agent reads the rest on request.
MAX_MESSAGE_CHARS = 100_000


class JsonlLog:
    def __init__(self, path: Path, keep: int):
        self.path = path
        self.items: Deque[dict] = deque(maxlen=keep)
        if path.is_file():
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        with contextlib.suppress(json.JSONDecodeError):
                            self.items.append(json.loads(line))

    def append(self, entry: dict):
        self.items.append(entry)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, default=str, ensure_ascii=False) + "\n")
        except OSError as exc:
            log.warning("[agi_loop] could not write %s: %s", self.path.name, exc)

    def tail(self, n: int) -> List[dict]:
        return list(self.items)[-n:] if n > 0 else []

    def clear(self):
        self.items.clear()
        with contextlib.suppress(FileNotFoundError):
            self.path.unlink()


class LoopDaemon:
    def __init__(self, host: Host, config: LoopConfig, data_dir: Path, embedder: Optional[Embedder] = None,
                 loop_id: str = "supervisor", group=None):
        self.host = host
        self.embedder = embedder or HashEmbedder()
        self.config = config
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.world = self._load_world()
        # "Today" (and the energy reset) ends at midnight in the operator's time zone, like the HUD clock.
        self.budget = DailyBudget(self.data_dir / "budget.json", config.daily_token_budget, config.daily_cost_cap,
                                  tz=config.timezone)
        self.workbench = Workbench(self.data_dir / "workbench") if config.workbench else None
        self.loop_id = loop_id
        self.group = group   # the shared room (groupchat.GroupChat), if this loop is in one
        self.linux = Linux.from_env(loop_id)
        self.channels = list(DEFAULT_CHANNELS)
        self.tools = LoopTools(self)

        self.ticks = JsonlLog(self.data_dir / "ticks.jsonl", 200)
        self.journal = JsonlLog(self.data_dir / "journal.jsonl", 500)
        self.events = JsonlLog(self.data_dir / "events.jsonl", 400)
        self.conversation = JsonlLog(self.data_dir / "conversation.jsonl", 300)
        self.state_log = JsonlLog(self.data_dir / "state_tags.jsonl", 200)
        self.declared: Optional[dict] = self.state_log.items[-1] if self.state_log.items else None

        self.task: Optional[asyncio.Task] = None
        self.running = False
        self.paused = False
        self.phase = "idle"
        self.stage: Optional[str] = None
        self.started_at: Optional[float] = None
        self.stopped_at: Optional[float] = None
        self.stop_reason: Optional[str] = None
        self.session_ticks = 0
        self.session_tokens = 0
        self.session_cost = 0.0
        self.session_prompt_tokens = self.session_cached_tokens = 0
        self.error_streak = 0
        self.stale_streak = 0
        self.guard_rests = 0
        self.last_error: Optional[str] = None
        self.next_wake_at: Optional[float] = None
        self.tick_started_at: Optional[float] = None   # wall time the current/last tick began (for the watchdog)
        self.wake_reason = "start"
        self.rest_request: Optional[Tuple[float, str]] = None
        self.pace: Optional[Tuple[float, str]] = None   # her own chosen wake interval (seconds, why); None = adaptive
        self.resting: Optional[str] = None
        self._wake = asyncio.Event()
        self._wake_cause: Optional[str] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._fingerprints: Deque[str] = deque(maxlen=10)

        self.processes: Dict[str, dict] = {s: {"stage": s, "about": STAGE_ABOUT[s], "status": "idle", "runs": 0,
                                               "last_ms": None, "avg_ms": None, "last_at": None, "note": "",
                                               "errors": 0} for s in STAGES}
        self.channel_status: Dict[str, dict] = {}

        self.last_sleep: Optional[dict] = None   # {"planned", "slept", "reason"} — the last wait, measured
        self.pace_note = ""

        saved = self._read_json("state.json")
        self.last_tick_at: Optional[float] = saved.get("last_tick_at")
        self.last_result: dict = saved.get("last_result", {})
        self.queue: List[dict] = saved.get("queue", [])
        # Her chosen pace outlives a restart; so does the record of how the last run ended.
        if saved.get("pace"):
            self.pace = (float(saved["pace"][0]), str(saved["pace"][1]))
        self.prior_stop: dict = {"at": saved.get("stopped_at"), "reason": saved.get("stop_reason")}
        self.handoff_seen: dict = saved.get("handoff_seen") or {}   # the letter already shown after a restart
        self.control_seq: int = int(saved.get("control_seq") or 0)   # last ~/hud-control.json seq applied
        self.control_ack: Optional[dict] = saved.get("control_ack")
        self.gate_on: bool = saved.get("gate_on", True) is not False   # the mind's own switch for the quiet gate
        self.llm_choice: str = saved.get("llm_choice") or ""   # the mind's own default for the llm tool
        self.gated_streak = 0      # quiet wakes slept through since the last thought
        self.gate_note = ""
        self._side_spend = {"tokens": 0, "cost": 0.0}   # llm side calls during the current tick
        self.history: List[dict] = [{"view": t.get("view_head", ""), "response": t.get("response", "")}
                                    for t in self.ticks.tail(config.history_window)]

    # ── Persistence ───────────────────────────────────────────────

    def _read_json(self, name: str) -> dict:
        try:
            return json.loads((self.data_dir / name).read_text(encoding="utf-8"))
        except FileNotFoundError:
            return {}
        except Exception as exc:
            log.warning("[agi_loop] %s unreadable: %s", name, exc)
            return {}

    def _write_json(self, name: str, data: dict):
        tmp = self.data_dir / f".{name}.tmp"
        tmp.write_text(json.dumps(data, default=str), encoding="utf-8")
        tmp.replace(self.data_dir / name)

    def _load_world(self) -> InnerWorld:
        data = self._read_json("world.json")
        c = self.config
        return InnerWorld.from_dict(data, c.capacity_chars, c.capture_threshold, self.embedder) if data \
            else InnerWorld(c.capacity_chars, c.capture_threshold, self.embedder)

    def save(self):
        try:
            self._write_json("world.json", self.world.to_dict())
            self._write_json("state.json", {"last_tick_at": self.last_tick_at, "last_result": self.last_result,
                                            "queue": self.queue, "pace": list(self.pace) if self.pace else None,
                                            "stopped_at": self.stopped_at, "stop_reason": self.stop_reason,
                                            "handoff_seen": self.handoff_seen,
                                            "control_seq": self.control_seq, "control_ack": self.control_ack,
                                            "gate_on": self.gate_on, "llm_choice": self.llm_choice})
        except OSError as exc:
            log.warning("[agi_loop] save failed: %s", exc)

    def apply_config(self, config: LoopConfig):
        self.config = config
        self.world.capacity = config.capacity_chars
        self.world.capture_threshold = config.capture_threshold
        self.budget.tokens_per_day = max(1, config.daily_token_budget)
        self.budget.cost_per_day = config.daily_cost_cap
        self.budget.tz = config.timezone or "UTC"

    def reset_world(self):
        if self.running:
            raise RuntimeError("Stop the loop before resetting its world")
        self.world = InnerWorld(self.config.capacity_chars, self.config.capture_threshold, self.embedder)
        self.last_tick_at, self.last_result, self.history = None, {}, []
        self.save()
        self.event("reset", "the field was cleared")

    # ── Outside interface ─────────────────────────────────────────

    def event(self, kind: str, text: str):
        self.events.append({"ts": _iso(), "tick": self.world.tick, "kind": kind, "text": text})

    def _poke(self, cause: str):
        """Wake the sleeper. Safe from worker threads (chat tools run off the event loop)."""
        self._wake_cause = cause
        loop = self._loop
        try:
            current = asyncio.get_running_loop()
        except RuntimeError:
            current = None
        if loop is not None and current is not loop and loop.is_running():
            loop.call_soon_threadsafe(self._wake.set)
        else:
            self._wake.set()

    def start(self) -> asyncio.Task:
        if self.running:
            raise RuntimeError("Loop already running")
        self.task = asyncio.create_task(self.run())
        return self.task

    def stop(self, reason: str = "operator"):
        self.request_stop(reason)
        if self.task and not self.task.done() and self.stage not in ("think", "act"):
            self.task.cancel()

    def request_stop(self, reason: str):
        """A deliberate stop (operator, the agent, a guard). Only these clear the autostart mark —
        a process that dies under a deploy keeps it, so the loop comes back on its own."""
        self.stop_reason = reason
        self.running = False
        with contextlib.suppress(OSError):
            self.autostart_file.unlink()
        self._poke("stop")

    @property
    def autostart_file(self) -> Path:
        return self.data_dir / "autostart"

    def pause(self):
        self.paused = True
        self._poke("pause")

    def resume(self):
        self.paused = False
        self._poke("resume")

    def request_rest(self, minutes: float, reason: str) -> float:
        minutes = max(1.0, min(self.config.max_rest_minutes, minutes))
        self.rest_request = (minutes * 60, reason)
        return minutes

    def set_pace(self, seconds: Optional[float], reason: str = "") -> Optional[float]:
        """Choose how often to wake. Clamped to the operator's min/max; None returns to the adaptive default."""
        if seconds is None:
            self.pace = None
            self.event("pace", "back to the adaptive rhythm")
            return None
        c = self.config
        seconds = max(c.min_interval_seconds, min(c.max_interval_seconds, float(seconds)))
        self.pace = (seconds, reason or "chose a pace")
        self.event("pace", f"waking every {seconds:.0f}s — {self.pace[1]}")
        return seconds

    def post_message(self, text: str, sender: str = "operator", group: bool = False) -> dict:
        msg = {"id": uuid.uuid4().hex[:10], "ts": _iso(), "sender": sender, "text": text.strip()[:MAX_MESSAGE_CHARS]}
        if group:
            msg["group"] = True
        self.queue.append(msg)
        self.conversation.append({"id": msg["id"], "ts": msg["ts"], "role": "operator", "sender": sender, "text": msg["text"]})
        self.event("message", f"{sender} at the door: {_clip(msg['text'], 80)}")
        self.save()
        self._poke("message")
        return msg

    def record_reply(self, text: str, item: Optional[Item]):
        in_reply_to = item.meta.get("message_id") if item else None
        self.conversation.append({"id": uuid.uuid4().hex[:10], "ts": _iso(), "role": "agent",
                                  "sender": self.config.agent, "text": text, "in_reply_to": in_reply_to})
        if item:
            self.world.resolve(item)
            if item.meta.get("group") and self.group:
                self.group.post(self.loop_id, self.config.agent, text)
        self.event("reply", _clip(text, 100))

    # ── Monitoring ────────────────────────────────────────────────

    @contextlib.contextmanager
    def _stage(self, name: str, note: str = ""):
        prev = self.stage
        self.stage = name
        p = self.processes[name]
        p["status"] = "running"
        p["last_at"] = _iso()
        t0 = time.perf_counter()
        try:
            yield p
            p["status"] = "ok"
        except Exception:
            p["status"] = "error"
            p["errors"] += 1
            raise
        finally:
            ms = (time.perf_counter() - t0) * 1000
            p["runs"] += 1
            p["last_ms"] = round(ms, 1)
            p["avg_ms"] = round(ms if p["avg_ms"] is None else 0.8 * p["avg_ms"] + 0.2 * ms, 1)
            if note and not p["note"]:
                p["note"] = note
            self.stage = prev

    def status(self) -> dict:
        w = self.world
        waiting = [i for i in w.items.values() if i.kind in ("message", "task") and not i.resolved]
        return {
            "running": self.running, "paused": self.paused, "phase": self.phase, "stage": self.stage,
            "started_at": _iso(self.started_at) if self.started_at else None,
            "stopped_at": _iso(self.stopped_at) if self.stopped_at else None,
            "stop_reason": self.stop_reason,
            "tick": w.tick, "session_ticks": self.session_ticks,
            "session_tokens": self.session_tokens, "session_cost": round(self.session_cost, 6),
            "session_cache": {"prompt_tokens": self.session_prompt_tokens, "cached_tokens": self.session_cached_tokens,
                              "hit_rate": round(self.session_cached_tokens / self.session_prompt_tokens, 3)
                              if self.session_prompt_tokens else None},
            "error_streak": self.error_streak, "stale_streak": self.stale_streak,
            "guard_rests": self.guard_rests, "last_error": self.last_error,
            "next_wake_at": _iso(self.next_wake_at) if self.next_wake_at else None,
            "next_wake_in": round(self.next_wake_at - time.time()) if self.next_wake_at else None,
            "wake_reason": self.wake_reason, "resting": self.resting,
            "pace": {"seconds": self.pace[0], "reason": self.pace[1]} if self.pace else None,
            "last_tick_at": _iso(self.last_tick_at) if self.last_tick_at else None,
            "focus": w.focus_item or "", "focus_name": w.focus_label(), "dwell": w.dwell,
            "mood": w.mood, "budget": self.budget.to_dict(),
            "capacity": {"used": w.used(time.time()), "of": w.capacity},
            "queue": len(self.queue), "waiting": len(waiting),
            "agent": self.config.agent, "model": self.config.model or "(profile default)",
            "processes": [self.processes[s] for s in STAGES],
            "channels": self.channel_status,
        }

    # ── The loop ──────────────────────────────────────────────────

    async def run(self):
        self._loop = asyncio.get_running_loop()
        self.running, self.paused = True, False
        self.started_at, self.stopped_at, self.stop_reason = time.time(), None, None
        self.session_ticks = self.session_tokens = self.guard_rests = 0
        self.session_cost = 0.0
        self.session_prompt_tokens = self.session_cached_tokens = 0
        self.error_streak = self.stale_streak = 0
        self.wake_reason = "start"
        self.event("start", f"{self.config.agent} woke")
        with contextlib.suppress(OSError):
            self.autostart_file.write_text(_iso(), encoding="utf-8")
        self._admit_handoff()
        try:
            while self.running:
                if self.paused:
                    self.phase = "paused"
                    while self.paused and self.running:
                        await self._wait(3600)
                    continue
                if self.budget.exhausted:
                    self.phase = "exhausted"
                    self.event("budget", "energy spent — sleeping until the daily budget resets")
                    await self._sleep(self.budget.seconds_until_reset(), wake_on_message=False)
                    continue
                self.phase = "ticking"
                try:
                    await self.tick()
                except Exception as exc:
                    log.exception("[agi_loop] tick failed")
                    self.error_streak += 1
                    self.last_error = f"tick failed: {exc}"
                    self.event("error", _clip(self.last_error, 200))
                    if self.config.error_streak_limit and self.error_streak >= self.config.error_streak_limit:
                        self.request_stop(f"guard: {self.error_streak} errors in a row")
                if self.running and not self.paused:
                    await self._sleep(*self._next_interval())
        except asyncio.CancelledError:
            self.stop_reason = self.stop_reason or "cancelled"
        except Exception as exc:
            log.exception("[agi_loop] daemon crashed")
            self.stop_reason = f"crashed: {exc}"
        finally:
            self.running = False
            self.phase = "stopped"
            self.stage = None
            self.next_wake_at = None
            self.stopped_at = time.time()
            self.event("stop", self.stop_reason or "stopped")
            self.save()

    # Where a letter to the next instance can live. The conventional path first, then any file that
    # names itself a handoff letter (K-OS keeps his as documents/handoff-letter-<date>.md).
    HANDOFF_PATTERNS = ("handoff/letter.md", "**/handoff-letter*.md", "**/HANDOFF*.md")

    def _find_handoff(self) -> Optional[Path]:
        if not self.workbench:
            return None
        root = Path(self.workbench.root)
        found = [p for pat in self.HANDOFF_PATTERNS for p in root.glob(pat) if p.is_file()]
        return max(found, key=lambda p: p.stat().st_mtime) if found else None

    def _admit_handoff(self):
        """After a restart, the newest letter from the previous instance is the first thing in view:
        held, focused, and quoted in her own words — never summarized for her. A letter is shown that
        way once; if it was already read after an earlier restart, she's told so instead of being
        handed an old letter as if it were about this gap."""
        if not self.last_tick_at:
            return   # first life: nobody wrote a letter
        path = self._find_handoff()
        if not path:
            return
        mtime = path.stat().st_mtime
        if mtime < self.last_tick_at - 7 * 86400:
            return   # too old to be about this gap
        rel = path.relative_to(Path(self.workbench.root)).as_posix()
        written = local_dt(mtime, self.config.timezone).strftime("%a %d %b %H:%M %Z")
        if self.handoff_seen.get("path") == rel and self.handoff_seen.get("mtime") == mtime:
            it, _ = self.world.upsert("handoff-letter", "note", "self",
                                      f"You didn't leave a new letter before this restart. Your newest one ({rel}, "
                                      f"written {written}) was already read after an earlier restart.",
                                      gist="no new letter", salience=0.4, valence=0.0)
            it.held = False   # the old letter was held through its run; it doesn't get to stay pinned forever
            self.event("handoff", f"no new letter; {rel} was already read")
            return
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return
        self.handoff_seen = {"path": rel, "mtime": mtime}
        body = text[:3000] + (f"\n… (the rest: workbench read {rel})" if len(text) > 3000 else "")
        it, _ = self.world.upsert("handoff-letter", "note", "self",
                                  f"A letter you left yourself before the restart ({rel}, written {written}):\n\n{body}",
                                  gist=f"your letter: {rel}", salience=0.95, valence=0.1)
        self.world.hold(it)
        self.world.move(item_id=it.id)
        self.event("handoff", f"shown the letter first: {rel}")

    async def _wait(self, timeout: float) -> Optional[str]:
        try:
            await asyncio.wait_for(self._wake.wait(), timeout=max(0.0, timeout))
        except asyncio.TimeoutError:
            return None
        self._wake.clear()
        cause, self._wake_cause = self._wake_cause, None
        return cause

    def _next_interval(self) -> Tuple[float, Optional[str]]:
        if self.rest_request:
            secs, reason = self.rest_request
            self.rest_request = None
            return secs, reason
        c = self.config
        chosen = self.pace[0] if self.pace else c.base_interval_seconds
        secs = chosen
        energy = self.budget.energy
        why = []
        if energy < 0.5:
            secs *= 1 + (0.5 - energy) * 4   # low energy slows even a chosen pace
            why.append(f"energy at {energy * 100:.0f}% stretches it")
        if not self.pace:
            secs /= 1 + self.world.arousal * 1.5
            if self.world.arousal > 0.05:
                why.append("surprise quickens it")
        secs = max(c.min_interval_seconds, min(c.max_interval_seconds, secs))
        base = f"you chose {fmt_span(chosen)}" if self.pace else f"adaptive, base {fmt_span(chosen)}"
        self.pace_note = f"pace: {base}" + (f"; {', '.join(why)} → {fmt_span(secs)}" if why else "")
        return secs, None

    async def _sleep(self, seconds: float, rest_reason: Optional[str] = None, wake_on_message: bool = True):
        self.resting = rest_reason
        if rest_reason:
            self.event("rest", f"resting {seconds / 60:.0f}m — {rest_reason}")
        if self.phase != "exhausted":
            self.phase = "resting" if rest_reason else "sleeping"
        slept_from = time.time()
        self.next_wake_at = slept_from + seconds
        with self._stage("sleep") as p:
            reason = "timer"
            while self.running and not self.paused:
                remaining = self.next_wake_at - time.time()
                if remaining <= 0:
                    break
                cause = await self._wait(remaining)
                if cause == "message" and wake_on_message:
                    reason = "message"
                    break
                if cause in ("stop", "pause", "poke"):
                    reason = cause
                    break
            p["note"] = f"woke: {reason}"
        self.last_sleep = {"planned": seconds, "slept": time.time() - slept_from, "reason": reason,
                           "rest": rest_reason}
        self.wake_reason = ("rest_" + reason) if rest_reason else reason
        if reason == "message":
            self.event("wake", "a message at the door woke you" + (" from rest" if rest_reason else ""))
        self.next_wake_at = None
        self.resting = None

    def wake_now(self):
        self._poke("poke")

    def _woke_line(self, gap: Optional[float]) -> str:
        r = self.wake_reason
        if r == "start":
            if not self.last_tick_at:
                return "You've just woken up."
            stop = self.prior_stop or {}
            reason = stop.get("reason") or ""
            if not stop.get("at") or reason in ("cancelled", "") or reason.startswith("crashed"):
                how = "the process went down under you (a deploy, restart or crash) rather than being stopped"
            else:
                how = f"the last run was stopped {fmt_span((self.started_at or time.time()) - stop['at'])} ago ({reason})"
            return (f"You are a new run of yourself. Your last tick was {fmt_span(gap or 0)} ago; {how}. "
                    f"Your field, bench, notes and the room were kept; the thought you were in the middle of was not.")
        if r.endswith("message"):
            return "Someone at the door woke you" + (" from your rest." if r.startswith("rest_") else ".")
        if r.startswith("rest_"):
            return f"You wake from rest after {fmt_age(gap or 0)}."
        if r == "poke":
            return "You were nudged awake."
        return f"You woke on your own after {fmt_age(gap or 0)}." if gap else "You woke on your own."

    def _narrated_tools(self, text: str) -> List[str]:
        """Tool names written as tags in an answer (<reply>…</reply>) instead of called. Nothing is run
        from text; the mind is told on its next tick that nothing was sent."""
        names = set(self.tools.names()) | {"tool_call", "function_call", "tool_use"}
        found = re.findall(r"<\s*([A-Za-z_][A-Za-z0-9_]*)\b", text or "")
        return list(dict.fromkeys(n.lower() for n in found if n.lower() in names))[:5]

    # ── Declared state and tool requests ───────────────────────────

    def declare_state(self, text: str) -> str:
        """Strip any [STATE: …] tags from text the mind produced; keep what they declared."""
        clean, fields = extract_state(text)
        if fields:
            entry = {"tick": self.world.tick, "ts": _iso(), "fields": fields}
            self.state_log.append(entry)
            self.declared = entry
            self.event("state", "declared " + ", ".join(f"{k}={_clip(v, 40)}" for k, v in fields.items()))
        return clean

    def _state_line(self, now: float) -> str:
        e = self.declared
        if not e:
            return ""
        try:
            age = fmt_span(now - datetime.fromisoformat(e["ts"]).timestamp())
        except (KeyError, ValueError, TypeError):
            age = "?"
        body = " · ".join(f"{k}={v}" for k, v in (e.get("fields") or {}).items())
        return _clip(f"◇ you declared at tick {e.get('tick')} ({age} ago): {body}", 600)

    @property
    def tool_requests_file(self) -> Path:
        return self.data_dir.parent / "tool_requests.jsonl"   # shared by every loop

    def request_tool(self, text: str) -> dict:
        """One line to the operator asking for a tool. Wakes nobody, interrupts nothing."""
        entry = {"id": uuid.uuid4().hex[:8], "ts": _iso(), "loop": self.loop_id, "agent": self.config.agent,
                 "tick": self.world.tick, "text": " ".join(text.split())[:500], "status": "open"}
        JsonlLog(self.tool_requests_file, 1).append(entry)
        self.event("request", f"asked the operator for: {_clip(entry['text'], 80)}")
        return entry

    def _clock_line(self, now: float, gap: Optional[float]) -> str:
        """Timing measured on the host's wall clock. The tick counter orders; this stamps."""
        tz = self.config.timezone
        here = local_dt(now, tz)
        parts = [f"⏲ now {here:%H:%M:%S %Z} (the operator's time) = {datetime.fromtimestamp(now, timezone.utc):%H:%M:%S} UTC"]
        if self.last_tick_at and gap is not None:
            began = local_dt(self.last_tick_at, tz)
            prev = f"tick {self.world.tick - 1} began {began:%H:%M:%S %Z} ({fmt_span(gap)} ago)"
            took = self.last_result.get("took")
            if took is not None:
                prev += f" and ran {fmt_span(took)}"
            parts.append(prev)
        s = self.last_sleep
        if s and self.wake_reason != "start":
            slept = f"slept {fmt_span(s['slept'])} of {fmt_span(s['planned'])} planned"
            if s["reason"] == "message":
                slept += ", a message woke you early"
            elif s["slept"] > s["planned"] + 60:
                slept += f", {fmt_span(s['slept'] - s['planned'])} late"
            parts.append(slept)
        return " · ".join(parts)

    async def tick(self):
        c, w = self.config, self.world
        now = time.time()
        self.tick_started_at = now
        w.begin(w.tick + 1)
        gap = now - self.last_tick_at if self.last_tick_at else None

        if self.linux:
            await self._apply_control()

        with self._stage("sense") as p:
            new_msgs, self.queue = list(self.queue), []
            try:
                tasks = await asyncio.to_thread(self.host.pending_tasks)
            except Exception as exc:
                log.warning("[agi_loop] inbox read failed: %s", exc)
                tasks = []
            ctx = ChannelContext(
                now=now, tick=w.tick, world=w, budget=self.budget, last_tick_at=self.last_tick_at,
                last=self.last_result, new_messages=new_msgs, pending_tasks=tasks, workbench=self.workbench,
                stale_streak=self.stale_streak, stale_limit=c.stale_streak_limit, rumination_ticks=c.rumination_ticks,
                tz=c.timezone,
            )
            signals: List[Signal] = []
            for ch in self.channels:
                name = ch.__name__.replace("_channel", "")
                try:
                    sig = ch(ctx)
                except Exception as exc:
                    log.warning("[agi_loop] channel %s failed: %s", name, exc)
                    self.channel_status[name] = {"channel": name, "at": _iso(now), "ok": False, "reading": str(exc)}
                    continue
                if sig:
                    signals.append(sig)
                    self.channel_status[sig.channel] = {"channel": sig.channel, "at": _iso(now), "ok": True,
                                                        "reading": sig.reading, "features": sig.features,
                                                        "items": len(sig.items)}
            p["note"] = f"{len(signals)} channels · {len(new_msgs)} message(s)"

        with self._stage("update") as p:
            w.decay(now)
            for sig in signals:
                for spec in sig.items:
                    w.upsert(now=now, **spec)
                for key in sig.resolve:
                    it = w.get(key)
                    if it:
                        w.resolve(it, now)
                for key in sig.clear:
                    it = w.get(key)
                    if it:
                        w.drop(it, reason="cleared")
            p["note"] = f"{len(w.items)} things in view"

        with self._stage("predict") as p:
            for sig in signals:
                for key, raw in sig.features.items():
                    w.perceive(key, raw, now)
            w.check_expectations([e for s in signals for e in s.events], now)
            p["note"] = f"{len(w.surprises)} surprise(s)" if w.surprises else "as predicted"

        with self._stage("attend") as p:
            need = w.needs_vectors()
            if need:
                try:
                    vecs = await asyncio.to_thread(self.embedder, [t for _, t in need])
                    w.set_vectors(zip([k for k, _ in need], vecs))
                except Exception as exc:
                    log.warning("[agi_loop] embedding failed: %s", exc)
            w.capture()
            w.layout()
            w.fit(now)
            p["note"] = (f"pulled to {w.pulled['by']}" if w.pulled else f"on {w.focus_label()} ({w.dwell})") + \
                        (f" · {len(w.faded)} faded" if w.faded else "")

        with self._stage("feel") as p:
            mood = w.compute_mood(self.budget.energy, now)
            p["note"] = mood["word"]

        why_not = self._gate_check(new_msgs)
        if why_not is None:
            self._doze(now)
            return
        self.gate_note = why_not

        with self._stage("render") as p:
            here = local_dt(now, c.timezone)
            woke = self._woke_line(gap)
            if self.gated_streak:
                woke += (f" Before this you slept through {self.gated_streak} quiet wake(s) with no model call "
                         f"(the gate; loop_control gate turns it off); this one came through: {self.gate_note}.")
            header = {"part_of_day": part_of_day(here.hour), "now": f"{here:%a %d %b %H:%M:%S %Z}",
                      "woke": woke, "energy": self.budget.energy,
                      "left": self.budget.left_text(), "clock": self._clock_line(now, gap),
                      "pace": self.pace_note, "state": self._state_line(now)}
            view = w.render(now, header)
            p["note"] = f"{len(view)} chars"

        self.phase = "thinking"
        result = await self._think(view)

        with self._stage("guard") as p:
            notes = []
            if result.get("error"):
                self.error_streak += 1
                self.last_error = str(result["error"])
                self.event("error", _clip(self.last_error, 200))
            else:
                self.error_streak = 0
                fp = fingerprint(result)
                self.stale_streak = self.stale_streak + 1 if self._fingerprints and self._fingerprints[-1] == fp else 0
                self._fingerprints.append(fp)
            if c.stale_streak_limit and self.stale_streak >= c.stale_streak_limit:
                self.guard_rests += 1
                self.stale_streak = 0
                if self.guard_rests > c.max_guard_rests:
                    self.request_stop(f"guard: still repeating after {c.max_guard_rests} forced rests")
                else:
                    self.request_rest(c.guard_rest_minutes, "guard: you kept repeating yourself")
                    w.upsert("guard-rest", "alert", "body", "you caught yourself repeating and were made to step away",
                             gist="made to step away", salience=0.7, valence=-0.2)
                notes.append("repetition")
            if c.error_streak_limit and self.error_streak >= c.error_streak_limit:
                self.request_stop(f"guard: {self.error_streak} errors in a row")
                notes.append("errors")
            if result.get("tokens", 0) > c.max_tokens_per_tick:
                notes.append("tick token cap")
            for n in notes:
                self.event("guard", n)
            p["note"] = ", ".join(notes) or "clear"

        with self._stage("record"):
            self.gated_streak = 0
            self.budget.spend(result.get("tokens", 0), result.get("cost", 0.0))
            self.session_ticks += 1
            self.session_tokens += result.get("tokens", 0)
            self.session_cost += result.get("cost", 0.0)
            self.session_prompt_tokens += result.get("prompt_tokens", 0)
            self.session_cached_tokens += result.get("cached_tokens", 0)
            self.last_tick_at = now
            narrated = self._narrated_tools(result.get("response") or "")
            if narrated:
                self.event("guard", "wrote tool tags as text instead of calling them: " + ", ".join(narrated))
            self.last_result = {
                "narrated": narrated,
                "took": round(time.time() - now, 2),   # the whole tick, wall time — not just the model call
                "tokens": result.get("tokens", 0), "latency": result.get("latency", 0.0),
                "error": result.get("error"),
                "tools": [{"tool": t["tool"], "ok": t["ok"]} for t in result.get("tool_calls", [])],
            }
            view_head = "\n".join(view.splitlines()[:3])
            if result.get("response"):
                self.history.append({"view": view_head, "response": result["response"][:2000]})
                # Append-only until it doubles, then cut back: a window sliding by one every tick
                # would change the prefix every tick and nothing past the system prompt would cache.
                keep = max(1, c.history_window)
                if len(self.history) > 2 * keep:
                    self.history = self.history[-keep:]
            entry = {
                "tick": w.tick, "time": _iso(now), "agent": c.agent, "model": result.get("model", ""),
                "wake": self.wake_reason, "focus": w.focus_label(), "mood": w.mood.get("word"),
                "view": view, "view_head": view_head,
                "response": (result.get("response") or "")[:5000],
                "tool_calls": result.get("tool_calls", []),
                "tokens": result.get("tokens", 0), "cost": round(result.get("cost", 0.0), 6),
                "prompt_tokens": result.get("prompt_tokens", 0), "cached_tokens": result.get("cached_tokens", 0),
                "latency": round(result.get("latency", 0.0), 2), "steps": result.get("steps", 0),
                "error": result.get("error"),
                "surprises": w.surprises, "pulled": w.pulled, "faded": w.faded,
            }
            self.ticks.append(entry)
            self.journal.append({
                "ts": entry["time"], "tick": w.tick, "agent": c.agent, "model": entry["model"],
                "focus": w.focus_label(), "mood": w.mood.get("word"), "narrative": narrate(result),
                "tools_used": [t["tool"] for t in result.get("tool_calls", [])],
                "tokens": entry["tokens"], "cost": entry["cost"], "had_error": bool(result.get("error")),
            })
            if w.pulled:
                self.event("pull", f"attention pulled to {w.pulled['to']} by {w.pulled['by']}")
            for s in w.surprises:
                self.event("surprise", f"({s['source']}) {s['text']}")
            for g in w.faded:
                self.event("fade", g)
            self.save()
            if self.linux:
                self._push_hud(view, now)

    # ── The quiet gate ────────────────────────────────────────────

    def _gate_check(self, new_msgs: List[dict]) -> Optional[str]:
        """None if this wake should be slept through; otherwise why it wasn't (or "" if the gate is off).
        Only a timer wake after an idle tick, with nothing new in the field, is gated — and only a few
        in a row. A message, a task, a surprise or a pull always gets a thought."""
        c, w = self.config, self.world
        if not (c.quiet_gate and self.gate_on):
            return ""
        if self.wake_reason not in ("timer", "rest_timer"):
            return "you were woken"
        if new_msgs or w.arrivals or w.surprises or w.pulled:
            return "something new arrived"
        if any(i.kind in ("message", "task") and not i.resolved for i in w.items.values()):
            return "someone is waiting"
        last = self.last_result or {}
        if last.get("error") or (last.get("tools") and not last.get("gated")):
            return "your last tick acted"
        if self.gated_streak >= c.gate_max_skips:
            return f"{self.gated_streak} quiet wakes in a row is the most it sleeps through"
        return None

    def _doze(self, now: float):
        """A gated wake: time passed in the field, nothing was spent, no model was called."""
        w = self.world
        self.gated_streak += 1
        self.last_tick_at = now
        self.last_result = {"gated": True, "took": round(time.time() - now, 2), "tokens": 0, "tools": [],
                            "narrated": [], "error": None, "latency": 0.0}
        self.processes["think"]["note"] = f"gated: quiet wake {self.gated_streak}"
        self.ticks.append({"tick": w.tick, "time": _iso(now), "agent": self.config.agent, "gated": True,
                           "wake": self.wake_reason, "focus": w.focus_label(), "mood": w.mood.get("word"),
                           "tokens": 0, "cost": 0.0})
        self.event("gate", f"quiet wake {self.gated_streak} slept through — nothing new, no model call")
        self.save()

    def hud_payload(self, view: str, now: float) -> dict:
        """This tick's HUD as data: what the host measured, for ~/hud on the mind's own machine."""
        w, b = self.world, self.budget
        lines = []
        for line in view.splitlines():
            if line.startswith("FOCUS ▸") or (lines and not line.strip()):
                break
            lines.append(line)
        return {
            "tick": w.tick, "agent": self.config.agent, "loop": self.loop_id,
            "at_utc": _iso(now), "at_local": local_dt(now, self.config.timezone).isoformat(timespec="seconds"),
            "timezone": self.config.timezone,
            "energy": round(b.energy, 4), "left_today": b.left_text(), "tokens_left": b.tokens_left,
            "cost_binds": b.cost_binds, "day_resets_in_s": round(b.seconds_until_reset()),
            "waiting": sum(1 for i in w.items.values() if i.kind in ("message", "task") and not i.resolved),
            "field_pct": min(999, w.used(now) * 100 // max(1, w.capacity)),
            "mood": w.mood.get("word"), "focus": w.focus_label(),
            "pace": {"seconds": self.pace[0], "reason": self.pace[1]} if self.pace else None,
            "this_tick": {"took_s": self.last_result.get("took"), "tokens": self.last_result.get("tokens"),
                          "tools": [t["tool"] for t in self.last_result.get("tools", [])],
                          "narrated": self.last_result.get("narrated") or []},
            "declared": self.declared,
            "control": self.control_ack,   # what the last ~/hud-control.json did (or refused)
            "control_file": "~/hud-control.json",
            # The numbers above are read from the live budget after this tick's spend (current as of
            # at_utc); hud_lines are the HUD as the mind saw it when this tick began.
            "hud_lines": lines,
            "numbers_as_of": "end of this tick (after its spend)",
            "hud_lines_as_of": "start of this tick (what the mind saw)",
        }

    CONTROL_FILE = "hud-control.json"
    CONTROL_KEYS = {"seq", "reason", "pace_seconds", "rest_minutes", "declare", "note"}

    async def _apply_control(self):
        """Read ~/hud-control.json from the mind's own machine and apply it once per new seq.
        State is the mind's to steer (pace, rest, what it declares, a note); measurements are not."""
        try:
            got = await asyncio.to_thread(self.linux.read, "file", path=self.CONTROL_FILE)
        except Exception:
            return   # box down or file unreadable: nothing to apply, nothing to say
        if not got.get("ok"):
            return
        try:
            ctl = json.loads(got.get("content") or "{}")
            seq = int(ctl.get("seq") or 0)
        except (ValueError, TypeError, AttributeError):
            self.control_ack = {"at": _iso(), "error": "~/hud-control.json isn't valid JSON with a numeric seq"}
            return
        if not isinstance(ctl, dict) or seq <= self.control_seq:
            return
        reason = str(ctl.get("reason") or "from ~/hud-control.json")[:200]
        applied, refused = [], []
        try:
            if "pace_seconds" in ctl:
                v = ctl["pace_seconds"]
                granted = self.set_pace(None if v is None else float(v), reason)
                applied.append(f"pace → {'adaptive' if granted is None else fmt_span(granted)}")
            if "rest_minutes" in ctl:
                applied.append(f"rest → {self.request_rest(float(ctl['rest_minutes']), reason):.0f}m after this tick")
            if isinstance(ctl.get("declare"), dict):
                fields = {}
                for k, v in ctl["declare"].items():
                    key = str(k).strip().lower().replace(" ", "_").replace("-", "_")
                    val = " ".join(str(v).split())[:MAX_STATE_VALUE]
                    if STATE_KEY.fullmatch(key) and val and len(fields) < MAX_STATE_FIELDS:
                        fields[key] = val
                if fields:
                    entry = {"tick": self.world.tick, "ts": _iso(), "fields": fields, "via": "hud-control"}
                    self.state_log.append(entry)
                    self.declared = entry
                    applied.append("declared " + ", ".join(fields))
                else:
                    refused.append("declare: no usable fields")
            elif "declare" in ctl:
                refused.append("declare: must be an object")
            if str(ctl.get("note") or "").strip():
                note = " ".join(str(ctl["note"]).split())[:600]
                self.world.upsert(f"control-note:{seq}", "note", "self", f"you wrote on your machine: {note}",
                                  salience=0.6, valence=0.05)
                applied.append("note set into your field")
        except (ValueError, TypeError) as exc:
            refused.append(f"bad value: {exc}")
        refused += [f"unknown key '{k}'" for k in ctl if k not in self.CONTROL_KEYS]
        self.control_seq = seq
        self.control_ack = {"seq": seq, "at": _iso(), "applied": applied, "refused": refused}
        self.event("control", f"~/hud-control.json seq {seq}: " + ("; ".join(applied) or "nothing applied")
                   + (f" (refused: {'; '.join(refused)})" if refused else ""))

    def _push_hud(self, view: str, now: float):
        """Off the event loop and never awaited: a slow box can't hold up a mind."""
        import threading
        payload = self.hud_payload(view, now)
        threading.Thread(target=self.linux.push_hud, args=(payload,), daemon=True).start()

    async def _think(self, view: str) -> dict:
        c = self.config
        result: Dict[str, Any] = {"response": "", "tool_calls": [], "tokens": 0, "cost": 0.0,
                                  "model": "", "latency": 0.0, "steps": 0, "prompt_tokens": 0, "cached_tokens": 0}
        t0 = time.perf_counter()
        self._side_spend = {"tokens": 0, "cost": 0.0}
        with self._stage("think") as p:
            try:
                prepared, registry_tools = await asyncio.to_thread(self.host.prepare, c.agent, view)
                # Cache discipline: everything that's the same every tick stays on top, byte for byte
                # (identity, notes, protocols, this preamble). What was retrieved for *this* tick goes
                # at the bottom with the field, so the provider's prefix cache can hit.
                system = [dict(m) for m in prepared if not m.get("dynamic")] or [{"role": "system", "content": ""}]
                retrieved = "\n\n".join(m.get("content") or "" for m in prepared if m.get("dynamic")).strip()
                system[0]["content"] = (system[0].get("content") or "").rstrip() + "\n\n" + LOOP_PREAMBLE
                own = set(self.tools.names())
                tool_defs = [t for t in registry_tools
                             if t["function"]["name"] not in EXCLUDED_TOOLS | own] + self.tools.definitions()

                # Cache breakpoints (the host turns "cache": True into its provider's form, or drops it):
                # the end of the stable system, the end of the carried history — append-only between
                # trims, so last tick's prefix is still a prefix — and this moment, so later steps of
                # this tick reread it from cache.
                system[-1]["cache"] = True
                messages: List[dict] = list(system)
                for h in self.history if c.history_window > 0 else []:
                    messages += [{"role": "user", "content": h["view"] or "(an earlier moment)"},
                                 {"role": "assistant", "content": h["response"]}]
                if len(messages) > len(system):
                    messages[-1] = dict(messages[-1], cache=True)
                now_content = view if not retrieved else (
                    f"{RETRIEVED_HEADER}\n\n{retrieved}\n\n---\n\n{view}")
                messages.append({"role": "user", "content": now_content, "cache": True})

                calls = 0
                for step in range(c.max_steps_per_tick + 1):
                    comp = await self.host.complete(c, messages, tool_defs)
                    result["steps"] = step + 1
                    result["tokens"] += comp.tokens
                    result["cost"] += comp.cost
                    result["prompt_tokens"] += getattr(comp, "prompt_tokens", 0) or 0
                    result["cached_tokens"] += getattr(comp, "cached_tokens", 0) or 0
                    result["model"] = comp.model or result["model"]
                    msg = comp.message or {}
                    tcs = msg.get("tool_calls") or []
                    can_continue = step < c.max_steps_per_tick and result["tokens"] < c.max_tokens_per_tick
                    if tcs and can_continue:
                        messages.append(msg)
                        for tc in tcs:
                            fn = tc.get("function") or {}
                            name = fn.get("name", "")
                            raw = fn.get("arguments") or "{}"
                            try:
                                args = json.loads(raw) if isinstance(raw, str) else dict(raw)
                            except (json.JSONDecodeError, TypeError, ValueError):
                                args = {}
                            if calls >= c.max_tool_calls_per_tick:
                                out, ok, ms = "Skipped: you've reached this tick's tool-call limit.", False, 0.0
                            else:
                                calls += 1
                                out, ok, ms = await self._call_tool(name, args)
                            result["tool_calls"].append({"tool": name, "arguments": args, "result": out[:2000],
                                                         "ok": ok, "ms": ms})
                            messages.append({"role": "tool", "tool_call_id": tc.get("id", ""), "content": out[:8000]})
                        continue
                    text = msg.get("content") or ""
                    if tcs and not text:
                        text = "(stopped mid-action: step or token limit for this tick reached)"
                    result["response"] = self.declare_state(
                        await asyncio.to_thread(self.host.after_response, c.agent, text))
                    break
                p["note"] = f"{result['steps']} step(s) · {result['tokens']:,} tok · {len(result['tool_calls'])} tool call(s)"
            except Exception as exc:
                log.warning("[agi_loop] think failed: %s", exc)
                result["error"] = str(exc)
                p["note"] = f"error: {_clip(str(exc), 80)}"
                p["errors"] += 1
        if result.get("error"):
            self.processes["think"]["status"] = "error"
        result["tokens"] += self._side_spend["tokens"]
        result["cost"] += self._side_spend["cost"]
        result["latency"] = time.perf_counter() - t0
        return result

    def llm_default(self) -> str:
        """The mind's own choice if it made one, else the operator's, else the first listed."""
        models = self.config.llm_models
        for pick in (self.llm_choice, self.config.llm_default):
            if pick in models:
                return pick
        return next(iter(models), "")

    async def side_llm(self, args: dict) -> str:
        """The llm tool: one completion on the model the mind chose, with only what it handed over.
        No identity, field, history or tools. Its spend is added to this tick's."""
        c = self.config
        prompt = (args.get("prompt") or "").strip()
        new_default = (args.get("set_default") or "").strip().lower()
        if new_default:
            if new_default not in c.llm_models:
                return f"Error: no model '{new_default}'. Choose one of: {', '.join(c.llm_models)}."
            self.llm_choice = new_default
            self.event("llm", f"default is now {new_default}")
            if not prompt:
                return f"Your llm default is now {new_default}. It stays until you change it."
        if not prompt:
            return "Error: llm needs a prompt with the whole task in it."
        choice = (args.get("model") or self.llm_default() or "").strip().lower()
        spec = c.llm_models.get(choice)
        if not spec:
            return f"Error: no model '{choice}'. Choose one of: {', '.join(c.llm_models)}."
        cap = c.cheap_max_tokens
        try:
            cap = max(64, min(cap, int(args.get("max_tokens") or cap)))
        except (TypeError, ValueError):
            pass
        messages = ([{"role": "system", "content": args["system"]}] if (args.get("system") or "").strip() else []) \
            + [{"role": "user", "content": prompt}]
        side = getattr(self.host, "side_complete", None)
        if side:
            comp = await side(c, spec, messages, cap)
        else:   # a host with one connection: the OpenRouter slug on it
            from dataclasses import replace
            comp = await self.host.complete(replace(c, model=spec.get("openrouter") or spec.get("model", ""),
                                                    max_output_tokens=cap), messages, [])
        self._side_spend["tokens"] += comp.tokens
        self._side_spend["cost"] += comp.cost
        text = ((comp.message or {}).get("content") or "").strip()
        self.event("llm", f"asked {choice} ({comp.tokens:,} tok, ${comp.cost:.4f})")
        head = f"[{choice} · {comp.model or spec.get('openrouter')} · {comp.tokens:,} tokens · ${comp.cost:.4f}]"
        if comp.finish_reason == "length":
            head += " (cut off at max_tokens)"
        return f"{head}\n{text or '(it returned no text)'}"

    async def _call_tool(self, name: str, args: dict) -> Tuple[str, bool, float]:
        t0 = time.perf_counter()
        with self._stage("act") as p:
            try:
                seen = False
                if name == "llm" and name in self.tools.handlers:
                    out = await self.side_llm(args)
                elif name == "linux" and name in self.tools.handlers:
                    # Network round trip that can run minutes — keep it off the event loop.
                    out = await asyncio.to_thread(self.tools.execute, name, args)
                    seen = True
                elif name in self.tools.handlers:
                    out = self.tools.execute(name, args)
                    seen = name == "workbench" and args.get("action") in ("read", "list", "reflections")
                elif name in EXCLUDED_TOOLS:
                    out = f"Error: '{name}' isn't available inside the loop."
                else:
                    out = await asyncio.to_thread(self.host.call_tool, self.config.agent, name, args)
                    seen = True
            except PermissionError as exc:
                out = f"BLOCKED: {exc}"
            except KeyError:
                out = f"Error: unknown tool '{name}'"
            except Exception as exc:
                out = f"Error: {exc}"
            out = out if isinstance(out, str) else json.dumps(out, default=str)
            lowered = out[:200].lower()
            ok = not (out.startswith(("Error", "BLOCKED", "Skipped")) or '"ok": false' in lowered)
            if seen and ok:
                self.world.see(name, args, out)
            p["note"] = f"{name} → {'ok' if ok else 'failed'}"
        return out, ok, round((time.perf_counter() - t0) * 1000, 1)
