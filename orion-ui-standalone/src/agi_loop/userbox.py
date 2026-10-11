"""Users' Linux boxes — one Fly machine and disk per user loop, paid from their credits.

The owner's minds have fixed boxes (services/elysia-linux, reached over the private network).
A signed-in user's loop can get its own: a machine plus a volume in the app
``orionforge-user-boxes``, created through the Fly Machines API. That app lives on its own
private network, so a user's box can't reach the engine, the owner's boxes, or other users'
boxes. The engine reaches each box over HTTPS (``fly-force-instance-id`` routes to it) with
that box's own random SHELL_TOKEN.

Billing is twice Fly's price: per second while the machine runs, and for the disk for as long
as it exists. ``meter`` adds the cost since the last meter to a running ``owed`` total and the
caller charges the whole credits of it, so tiny amounts aren't rounded up every few minutes.

Configuration (engine environment): FLY_USER_BOXES_TOKEN (a deploy token for the app; without
it the feature is off), USER_BOX_APP, USER_BOX_IMAGE, USER_BOX_REGION.
"""

import json
import os
import secrets
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, Optional

from .linux import Linux

APP = os.environ.get("USER_BOX_APP", "orionforge-user-boxes")
IMAGE = os.environ.get("USER_BOX_IMAGE", "registry.fly.io/orionforge-user-boxes:userbox-v1")
REGION = os.environ.get("USER_BOX_REGION", "iad")
API = "https://api.machines.dev/v1"
BOX_USER = "agent"

# Fly's prices (docs.fly.io/about/pricing, shared-cpu-1x in iad): USD per second while running.
RUN_USD_PER_SEC = {512: 0.00000143, 1024: 0.00000258, 2048: 0.00000490}
DISK_USD_PER_GB_MONTH = 0.15
MARKUP = 2.0
CREDITS_PER_USD = 1000
MEMORY_CHOICES = (512, 1024, 2048)
DEFAULT_MEMORY, DEFAULT_DISK_GB = 512, 1
MAX_DISK_GB, ROOMY_DISK_GB = 50, 5           # above ROOMY the wizard says it isn't needed yet

RECORD = "linux_box.json"


def enabled() -> bool:
    return bool(os.environ.get("FLY_USER_BOXES_TOKEN"))


def credits_per_hour(memory_mb: int) -> float:
    return RUN_USD_PER_SEC[memory_mb] * 3600 * MARKUP * CREDITS_PER_USD


def disk_credits_per_day(disk_gb: int) -> float:
    return disk_gb * DISK_USD_PER_GB_MONTH / 30 * MARKUP * CREDITS_PER_USD


def prices() -> dict:
    """What the Linux tab shows before someone makes a box."""
    return {"memory": {m: round(credits_per_hour(m), 1) for m in MEMORY_CHOICES},
            "disk_per_gb_day": round(disk_credits_per_day(1), 1),
            "default_memory": DEFAULT_MEMORY, "default_disk_gb": DEFAULT_DISK_GB,
            "roomy_disk_gb": ROOMY_DISK_GB, "max_disk_gb": MAX_DISK_GB}


def public_url() -> str:
    return f"https://{APP}.fly.dev"


# ── Fly Machines API ──────────────────────────────────────────────
def _api(method: str, path: str, body: Optional[dict] = None, timeout: int = 60) -> dict:
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 method=method, headers={
                                     "Authorization": "Bearer " + os.environ.get("FLY_USER_BOXES_TOKEN", ""),
                                     "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"Fly said {exc.code}: {detail}") from None
    return json.loads(raw) if raw else {}


def _machine_config(token: str, volume_id: str, memory_mb: int) -> dict:
    def service(internal: int, public: int) -> dict:
        # autostart/autostop off: the engine starts and stops boxes itself, so billing follows the loop.
        return {"protocol": "tcp", "internal_port": internal, "autostart": False, "autostop": "off",
                "ports": [{"port": public, "handlers": ["tls", "http"]}]}
    return {
        "image": IMAGE,
        "env": {"SHELL_TOKEN": token, "AGENT_USER": BOX_USER},
        "guest": {"cpu_kind": "shared", "cpus": 1, "memory_mb": memory_mb},
        "mounts": [{"volume": volume_id, "path": f"/home/{BOX_USER}"}],
        "services": [service(8080, 443), service(8081, 8443)],
        "checks": {"health": {"type": "http", "port": 8080, "path": "/health", "interval": "30s", "timeout": "5s",
                              "grace_period": "30s"}},
        "restart": {"policy": "on-failure", "max_retries": 3},
    }


# ── One box per loop ──────────────────────────────────────────────
class Box:
    """The record of a loop's box (``linux_box.json`` in the loop's data folder) and its machine."""

    def __init__(self, data_dir: Path, record: dict):
        self.data_dir = Path(data_dir)
        self.r = record

    @classmethod
    def load(cls, data_dir: Path) -> Optional["Box"]:
        path = Path(data_dir) / RECORD
        if not path.exists():
            return None
        try:
            return cls(data_dir, json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return None

    def save(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        tmp = self.data_dir / (RECORD + ".part")
        tmp.write_text(json.dumps(self.r, indent=1), encoding="utf-8")
        tmp.replace(self.data_dir / RECORD)

    @property
    def machine_id(self) -> str:
        return self.r["machine_id"]

    def linux(self) -> Linux:
        """The loop's client for this box, routed to its machine."""
        return Linux(public_url(), self.r["token"], BOX_USER,
                     headers={"fly-force-instance-id": self.machine_id},
                     hud_url=public_url() + ":8443")

    def summary(self) -> dict:
        return {k: self.r.get(k) for k in ("memory_mb", "disk_gb", "state", "created_at")} | {
            "credits_per_hour": round(credits_per_hour(self.r["memory_mb"]), 1),
            "disk_credits_per_day": round(disk_credits_per_day(self.r["disk_gb"]), 1)}

    # Lifecycle ----------------------------------------------------
    @classmethod
    def create(cls, data_dir: Path, name: str, memory_mb: int, disk_gb: int, start: bool,
               api: Callable = None) -> "Box":
        api = api or _api
        if memory_mb not in MEMORY_CHOICES:
            raise ValueError(f"Memory must be one of {', '.join(map(str, MEMORY_CHOICES))} MB")
        if not 1 <= int(disk_gb) <= MAX_DISK_GB:
            raise ValueError(f"Disk must be 1–{MAX_DISK_GB} GB")
        token = secrets.token_urlsafe(32)
        vol_name = ("home_" + "".join(c for c in name.lower() if c.isalnum()))[:30]
        vol = api("POST", f"/apps/{APP}/volumes", {"name": vol_name, "size_gb": int(disk_gb), "region": REGION,
                                                   "encrypted": True})
        try:
            m = api("POST", f"/apps/{APP}/machines", {"name": name[:60], "region": REGION, "skip_launch": not start,
                                                      "config": _machine_config(token, vol["id"], memory_mb)})
        except Exception:
            api("DELETE", f"/apps/{APP}/volumes/{vol['id']}")
            raise
        now = time.time()
        box = cls(data_dir, {"machine_id": m["id"], "volume_id": vol["id"], "token": token,
                             "memory_mb": memory_mb, "disk_gb": int(disk_gb), "created_at": now,
                             "state": "started" if start else "stopped",
                             "run_metered_at": now, "disk_metered_at": now, "owed": 0.0})
        box.save()
        return box

    def start(self, api: Callable = None):
        (api or _api)("POST", f"/apps/{APP}/machines/{self.machine_id}/start")
        self.r["state"], self.r["run_metered_at"] = "started", time.time()
        self.save()

    def stop(self, api: Callable = None):
        """Stop the machine. The caller meters first, so the running time is charged."""
        try:
            (api or _api)("POST", f"/apps/{APP}/machines/{self.machine_id}/stop")
        finally:
            self.r["state"] = "stopped"
            self.save()

    def resize(self, memory_mb: int, api: Callable = None):
        api = api or _api
        if memory_mb not in MEMORY_CHOICES:
            raise ValueError(f"Memory must be one of {', '.join(map(str, MEMORY_CHOICES))} MB")
        api("POST", f"/apps/{APP}/machines/{self.machine_id}",
            {"config": _machine_config(self.r["token"], self.r["volume_id"], memory_mb),
             "skip_launch": self.r.get("state") != "started"})
        self.r["memory_mb"] = memory_mb
        self.save()

    def grow_disk(self, disk_gb: int, api: Callable = None):
        disk_gb = int(disk_gb)
        if disk_gb <= self.r["disk_gb"]:
            raise ValueError("A disk can only grow")
        if disk_gb > MAX_DISK_GB:
            raise ValueError(f"Disk can be at most {MAX_DISK_GB} GB")
        (api or _api)("PUT", f"/apps/{APP}/volumes/{self.r['volume_id']}/extend", {"size_gb": disk_gb})
        self.r["disk_gb"] = disk_gb
        self.save()

    def destroy(self, api: Callable = None):
        """Delete the machine and its disk for good, and forget the box."""
        api = api or _api
        try:
            api("DELETE", f"/apps/{APP}/machines/{self.machine_id}?force=true")
        finally:
            try:
                api("DELETE", f"/apps/{APP}/volumes/{self.r['volume_id']}")
            finally:
                (self.data_dir / RECORD).unlink(missing_ok=True)

    # Billing ------------------------------------------------------
    def meter(self, now: Optional[float] = None, running: Optional[bool] = None) -> int:
        """Add the cost since the last meter to ``owed`` and return the whole credits now due
        (taken off ``owed``; the caller charges them). ``running`` says whether the machine
        ran since the last meter (default: the recorded state)."""
        now = now or time.time()
        running = self.r.get("state") == "started" if running is None else running
        usd = 0.0
        if running:
            usd += max(0.0, now - self.r["run_metered_at"]) * RUN_USD_PER_SEC[self.r["memory_mb"]]
        usd += max(0.0, now - self.r["disk_metered_at"]) * self.r["disk_gb"] * DISK_USD_PER_GB_MONTH / (30 * 86400)
        self.r["run_metered_at"] = self.r["disk_metered_at"] = now
        self.r["owed"] = self.r.get("owed", 0.0) + usd * MARKUP * CREDITS_PER_USD
        due = int(self.r["owed"])
        self.r["owed"] -= due
        self.save()
        return due
