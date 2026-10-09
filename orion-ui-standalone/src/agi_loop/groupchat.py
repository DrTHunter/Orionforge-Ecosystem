"""Group chat — one shared room the loops (and the operator) talk in.

A message posted to the room is logged and handed to every other loop's door,
tagged as a group message. A loop's reply to a group message goes back into the
room; so does anything it chooses to say with the ``group`` tool.

There is no cap on how long they can talk; each loop's own energy budget is what
ends a conversation.
"""

import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List

from .daemon import JsonlLog

MAX_TEXT = 100_000


class GroupChat:
    def __init__(self, path: Path, loops: Callable[[], Dict[str, object]]):
        self.log = JsonlLog(Path(path), 500)
        self._loops = loops
        self.slab = Slab(Path(path).with_name("slab.jsonl"))

    def post(self, origin: str, sender: str, text: str) -> dict:
        """``origin`` is "operator" or a loop id. Returns the logged entry."""
        text = (text or "").strip()[:MAX_TEXT]
        entry = {"id": uuid.uuid4().hex[:10], "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                 "origin": origin, "sender": sender, "text": text}
        if not text:
            return entry
        self.log.append(entry)
        for loop_id, daemon in self._loops().items():
            if loop_id != origin:
                daemon.post_message(text, sender=sender, group=True)
        return entry

    def say(self, loop_id: str, name: str, text: str) -> str:
        self.post(loop_id, name, text)
        return "Said to the group."

    def read(self, n: int = 20) -> List[dict]:
        return self.log.tail(max(1, min(100, n)))


SLAB_MAX_TEXT = 8_000


class Slab:
    """One persistent file in the room that every mind can write to and read — append-only.

    Nobody edits or deletes an entry, including the one who wrote it. Each entry carries a
    global sequence number (the slab's own order: causality across minds), the host's wall
    time, the author, and the author's own tick. The file lives beside the room's log, so it
    survives restarts.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.log = JsonlLog(self.path, 2000)
        self.seq = max((e.get("seq", 0) for e in self.log.items), default=0)
        self._lock = threading.Lock()

    def write(self, author: str, loop_id: str, tick: int, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            raise ValueError("Write what?")
        with self._lock:
            self.seq += 1
            entry = {"seq": self.seq, "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                     "author": author, "loop": loop_id, "tick": tick, "text": text[:SLAB_MAX_TEXT]}
            self.log.append(entry)
            # The same entry, human-readable: slab.md reads like a document, newest at the bottom.
            try:
                with open(self.path.with_suffix(".md"), "a", encoding="utf-8") as f:
                    f.write(f"### #{entry['seq']} · {entry['ts']} · {author} (tick {tick})\n\n{entry['text']}\n\n")
            except OSError:
                pass
        return entry

    def read(self, limit: int = 30, since: int = 0) -> List[dict]:
        items = [e for e in self.log.items if e.get("seq", 0) > since]
        return items[-max(1, min(200, limit)):]

    @staticmethod
    def line(e: dict) -> str:
        return f"#{e['seq']} · {e['ts']} · {e['author']} (tick {e['tick']}): {e['text']}"
