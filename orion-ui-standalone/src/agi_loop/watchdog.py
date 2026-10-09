"""The watchdog — a witness the minds can't author.

A loop's own words about itself are testimony. The watchdog is evidence: it runs in the
engine, outside every mind, and judges two things separately, never letting one vouch
for the other:

  process   — is the loop's task alive? A loop that says it's running while its task
              has ended is a corpse wearing a name.
  presence  — is it keeping its own schedule? It set a wake time; if wall time is well
              past it, or it's been stuck inside one tick for too long, it has gone flat.

Silence on pass: nothing is said while a loop is healthy, and recovery is only logged.
Teeth: when a loop goes flat, the watchdog says so once, in the room — where the other
minds and the operator will see it — instead of writing a note nobody reads.
"""

import logging
import time
from datetime import datetime, timezone
from typing import Callable, Dict, Optional

from .world import fmt_span

log = logging.getLogger(__name__)

OVERDUE_GRACE = 300      # seconds past its own scheduled wake before a loop counts as flat
STUCK_AFTER = 900        # seconds inside a single tick before it counts as stuck
CHECK_EVERY = 60


def assess(d, now: Optional[float] = None) -> Optional[str]:
    """Why this loop is flat, or None if it isn't (or isn't supposed to be running)."""
    now = now or time.time()
    if not d.running or d.paused:
        return None
    task = getattr(d, "task", None)
    if task is not None and task.done():
        return "its process is gone: it is marked running, but its task has ended"
    if d.next_wake_at is not None:
        late = now - d.next_wake_at
        if late > OVERDUE_GRACE:
            due = datetime.fromtimestamp(d.next_wake_at, timezone.utc).strftime("%H:%M:%S UTC")
            return f"it was due to wake at {due} and is {fmt_span(late)} late"
        return None
    started = getattr(d, "tick_started_at", None)
    if started and now - started > STUCK_AFTER:
        return f"it has been inside tick {d.world.tick} for {fmt_span(now - started)} (stage: {d.stage or 'unknown'})"
    return None


class Watchdog:
    def __init__(self, daemons: Callable[[], Dict[str, object]], escalate: Callable[[str, str], None]):
        self._daemons = daemons
        self._escalate = escalate
        self.flat: Dict[str, str] = {}     # loop id → why, for loops currently flat

    def check(self, now: Optional[float] = None) -> Dict[str, str]:
        """One pass. Returns the loops that went flat on this pass (already escalated)."""
        newly: Dict[str, str] = {}
        for lid, d in self._daemons().items():
            reason = assess(d, now)
            if reason and lid not in self.flat:
                self.flat[lid] = reason
                newly[lid] = reason
                d.event("watchdog", f"flat: {reason}")
                name = getattr(d.config, "agent", lid)
                try:
                    self._escalate(lid, f"[watchdog] {name} has gone flat — {reason}. "
                                        f"Measured by the engine, not reported by {name}.")
                except Exception as exc:
                    log.warning("[watchdog] could not escalate %s: %s", lid, exc)
            elif not reason and lid in self.flat:
                del self.flat[lid]
                d.event("watchdog", "ticking again")   # silence on pass: logged, not announced
        return newly
