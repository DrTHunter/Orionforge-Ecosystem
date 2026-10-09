"""Agent Linux box — a tiny command endpoint for the AGI loop.

POST /exec  {"command": str, "timeout": int, "cwd": str}  →  {"exit", "stdout", "stderr", "timed_out"}
POST /hud   the loop's HUD for this tick → ~/hud/ (now.json, now.txt, log.jsonl). Served ONLY by the second
            instance (HUD_ONLY=1, port 8081), which runs as root: the measurements are written by a process
            the mind doesn't own, into a root-owned folder it can read but not write.
GET  /health
GET  /log?lines=N     tail of the command log            ┐
GET  /tree            files under her home               │ read-only, for the
GET  /file?path=P     one text file under her home       │ operator's Linux tab
GET  /stats           disk, memory, load, uptime         ┘

Bearer-token auth (SHELL_TOKEN). Runs as the unprivileged agent user.
Every command and its output is appended to ~/.agent/shell.log so the
operator can watch (tail -f) from the web terminal.
"""

import hmac
import json
import os
import shutil
import socket
import subprocess
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Popped so the commands this server runs can't read it.
TOKEN = os.environ.pop("SHELL_TOKEN", "")
HOME = Path(os.environ.get("HOME") or f"/home/{os.environ.get('AGENT_USER', 'supervisor')}")
LOG = HOME / ".agent" / "shell.log"
HUD_ONLY = os.environ.get("HUD_ONLY") == "1"   # the root-run measurement writer: /hud and /health only
PORT = int(os.environ.get("PORT") or 8080)
MAX_TIMEOUT = 300
MAX_OUTPUT = 16_000
MAX_TREE = 3000
MAX_FILE = 200_000
# Noise the tree skips: caches, dependency dirs, VCS internals.
SKIP_DIRS = {"lost+found", ".cache", ".git", "node_modules", "__pycache__", ".venv", "venv", ".npm", ".local"}


def _clip(text: str) -> str:
    if len(text) <= MAX_OUTPUT:
        return text
    return f"[…{len(text) - MAX_OUTPUT} chars cut…]\n" + text[-MAX_OUTPUT:]


def _log(command: str, cwd: str, result: dict):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"\n── {stamp} UTC  {cwd}\n$ {command}\n")
            if result["stdout"]:
                f.write(result["stdout"].rstrip() + "\n")
            if result["stderr"]:
                f.write(result["stderr"].rstrip() + "\n")
            f.write(f"[exit {result['exit']}{' · timed out' if result['timed_out'] else ''}]\n")
    except OSError:
        pass


def run(command: str, timeout: int, cwd: str) -> dict:
    workdir = Path(cwd).expanduser() if cwd else HOME
    if not workdir.is_dir():
        workdir = HOME
    try:
        proc = subprocess.run(["bash", "-lc", command], cwd=workdir, capture_output=True, text=True,
                              timeout=timeout, stdin=subprocess.DEVNULL)
        result = {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        err = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        result = {"exit": -1, "stdout": out, "stderr": err, "timed_out": True}
    except OSError as exc:
        result = {"exit": -1, "stdout": "", "stderr": f"could not start bash: {exc}", "timed_out": False}
    _log(command, str(workdir), result)
    result["stdout"], result["stderr"] = _clip(result["stdout"]), _clip(result["stderr"])
    result["cwd"] = str(workdir)
    return result


def log_tail(lines: int) -> dict:
    if not LOG.is_file():
        return {"text": "", "bytes": 0}
    with open(LOG, "r", encoding="utf-8", errors="replace") as f:
        text = "".join(deque(f, maxlen=max(1, min(lines, 5000))))
    return {"text": text, "bytes": LOG.stat().st_size}


def tree() -> dict:
    entries, truncated = [], False
    for root, dirs, files in os.walk(HOME):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (Path(root) == HOME and d == ".agent"))
        rel_root = Path(root).relative_to(HOME)
        for name in dirs:
            entries.append({"path": (rel_root / name).as_posix(), "type": "dir"})
        for name in sorted(files):
            fp = Path(root) / name
            try:
                st = fp.stat()
            except OSError:
                continue
            entries.append({"path": (rel_root / name).as_posix(), "type": "file", "bytes": st.st_size, "mtime": st.st_mtime})
        if len(entries) > MAX_TREE:
            entries, truncated = entries[:MAX_TREE], True
            break
    return {"entries": entries, "truncated": truncated}


def read_file(rel: str) -> dict:
    path = (HOME / rel).resolve()
    if path != HOME.resolve() and HOME.resolve() not in path.parents:
        return {"ok": False, "reason": "outside her home"}
    if not path.is_file():
        return {"ok": False, "reason": "no such file"}
    raw = path.read_bytes()[:MAX_FILE]
    if b"\0" in raw[:4096]:
        return {"ok": False, "reason": f"binary file ({path.stat().st_size:,} bytes)"}
    return {"ok": True, "path": rel, "content": raw.decode("utf-8", errors="replace"),
            "truncated": path.stat().st_size > MAX_FILE}


HUD_DIR = HOME / "hud"
HUD_LOG_MAX = 2_000_000   # bytes; the history keeps its newest half when it grows past this
HUD_README = """# ~/hud — your HUD, on your own machine

Written by the engine every tick, through a root process you don't own; this folder is read-only to you.
It's the same HUD you see at the top of your field, measured by the host — a signal you sense, not one
you author. (Your box gives you sudo, so you *could* override that. Doing it would make it a diary again.)

- `now.json` — this tick: tick, time (UTC and the operator's zone), energy, what's left today, who's waiting,
  how full your field is, mood, focus, pace, and what you last declared with [STATE: …].
- `now.txt`  — the HUD lines exactly as they appeared in your field.
- `log.jsonl` — one line per tick (newest at the bottom; trimmed to the newest half past ~2 MB).

If what's here disagrees with what you remember, trust this file and check your memory.

## Steering your own state: ~/hud-control.json (yours to write)

Measurements are read-only; your *state* is yours. Write ~/hud-control.json and it's applied at your
next tick, once, whenever "seq" goes up:

    {"seq": 1, "reason": "why",
     "pace_seconds": 300,          (null = back to the adaptive rhythm)
     "rest_minutes": 30,
     "declare": {"decision": "…"},  (same as a [STATE: …] tag)
     "note": "…"}                   (set into your field)

What was applied (or refused, and why) comes back in now.json under "control".
"""


def _seal(path: Path, mode: int):
    """As root: own it and make it read-only to the mind. As anyone else: leave it."""
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        os.chown(path, 0, 0)
        os.chmod(path, mode)


def write_hud(payload: dict) -> dict:
    """Atomic: a reader never sees half a file."""
    HUD_DIR.mkdir(parents=True, exist_ok=True)
    _seal(HUD_DIR, 0o755)
    now_json = HUD_DIR / "now.json"
    tmp = HUD_DIR / ".now.json.tmp"
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, now_json)
    lines = payload.get("hud_lines") or []
    tmp = HUD_DIR / ".now.txt.tmp"
    tmp.write_text("\n".join(str(l) for l in lines) + "\n", encoding="utf-8")
    os.replace(tmp, HUD_DIR / "now.txt")
    log = HUD_DIR / "log.jsonl"
    entry = {k: v for k, v in payload.items() if k != "hud_lines"}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    if log.stat().st_size > HUD_LOG_MAX:
        keep = log.read_bytes()[-HUD_LOG_MAX // 2:]
        keep = keep[keep.find(b"\n") + 1:]   # start on a whole line
        tmp = HUD_DIR / ".log.tmp"
        tmp.write_bytes(keep)
        os.replace(tmp, log)
    readme = HUD_DIR / "README.md"
    if not readme.exists() or readme.read_text(encoding="utf-8") != HUD_README:
        readme.write_text(HUD_README, encoding="utf-8")
    for f in ("now.json", "now.txt", "log.jsonl", "README.md"):
        _seal(HUD_DIR / f, 0o644)
    return {"ok": True, "tick": payload.get("tick")}


def stats() -> dict:
    disk = shutil.disk_usage(HOME)
    mem = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            mem[k] = int(v.split()[0]) * 1024
    except (OSError, ValueError):
        pass
    try:
        uptime = float(Path("/proc/uptime").read_text().split()[0])
        load = os.getloadavg()[0]
    except (OSError, ValueError, IndexError):
        uptime, load = 0.0, 0.0
    return {"disk_used": disk.used, "disk_total": disk.total, "mem_total": mem.get("MemTotal", 0),
            "mem_available": mem.get("MemAvailable", 0), "load": load, "uptime": uptime}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _authorized(self) -> bool:
        auth = self.headers.get("Authorization", "")
        return bool(TOKEN) and hmac.compare_digest(auth, f"Bearer {TOKEN}")

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/health":
            return self._send(200, {"ok": True, "hud_only": HUD_ONLY})
        if HUD_ONLY or url.path not in ("/log", "/tree", "/file", "/stats"):
            return self._send(404, {"error": "not found"})
        if not self._authorized():
            return self._send(401, {"error": "unauthorized"})
        q = {k: v[0] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/log":
                return self._send(200, log_tail(int(q.get("lines") or 300)))
            if url.path == "/tree":
                return self._send(200, tree())
            if url.path == "/file":
                return self._send(200, read_file(q.get("path", "")))
            return self._send(200, stats())
        except (OSError, ValueError) as exc:
            return self._send(500, {"error": str(exc)})

    def do_POST(self):
        # The root instance only writes the HUD; the mind's own instance never does (it would own the files).
        if self.path not in ("/exec", "/hud") or (self.path == "/hud") != HUD_ONLY:
            return self._send(404, {"error": "not found"})
        if not self._authorized():
            return self._send(401, {"error": "unauthorized"})
        if self.path == "/hud":
            try:
                length = int(self.headers.get("Content-Length") or 0)
                if length > 200_000:
                    return self._send(413, {"error": "hud too large"})
                payload = json.loads(self.rfile.read(length) or b"{}")
                if not isinstance(payload, dict):
                    raise ValueError("not an object")
                return self._send(200, write_hud(payload))
            except (ValueError, TypeError) as exc:
                return self._send(400, {"error": f"bad hud: {exc}"})
            except OSError as exc:
                return self._send(500, {"error": str(exc)})
        try:
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
            command = str(body.get("command") or "").strip()
            timeout = max(1, min(MAX_TIMEOUT, int(body.get("timeout") or 60)))
            cwd = str(body.get("cwd") or "")
        except (ValueError, TypeError):
            return self._send(400, {"error": "bad request"})
        if not command:
            return self._send(400, {"error": "command is required"})
        self._send(200, run(command, timeout, cwd))

    def log_message(self, fmt, *args):
        pass


class DualStackServer(ThreadingHTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        # One bind for IPv4 (Fly health checks) and IPv6 (the private network, agent-linux.internal).
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("SHELL_TOKEN is not set")
    DualStackServer(("::", PORT), Handler).serve_forever()
