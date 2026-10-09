"""Documents — files and long text that arrive with a message.

A message can carry whole documents: a soul script, a transcript, a software
project (as a .zip). They are saved into the receiving loop's workbench under
documents/<batch>/ so the agent reads them with the workbench tool, a page at
a time. Text too long for a message becomes a .txt the same way.
"""

import io
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

LONG_TEXT = 12_000            # messages longer than this become a document
PREVIEW_CHARS = 1_500         # how much of it stays in the message itself
MAX_FILE_BYTES = 10_000_000   # one uploaded file
MAX_BATCH_BYTES = 25_000_000  # everything in one message
MAX_ZIP_FILES = 3_000
MAX_ZIP_BYTES = 40_000_000    # unzipped
SKIP_PARTS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".idea", ".DS_Store"}

_BAD = re.compile(r"[^A-Za-z0-9._\- ]")


def _safe_part(part: str) -> str:
    part = _BAD.sub("_", part).strip().lstrip(".")
    return part[:80]


def _safe_rel(name: str) -> Optional[str]:
    """A relative path with no traversal, no hidden files, no empty parts."""
    parts = [_safe_part(p) for p in re.split(r"[\\/]+", name or "") if p not in ("", ".", "..")]
    parts = [p for p in parts if p]
    return "/".join(parts) if parts else None


def batch_folder(label: str = "") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"documents/{stamp}" + (f"-{_safe_part(label)}" if _safe_part(label) else "")


def _unzip(data: bytes) -> List[Tuple[str, bytes]]:
    out, total = [], 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            rel = _safe_rel(info.filename)
            if not rel or any(p in SKIP_PARTS for p in info.filename.replace("\\", "/").split("/")):
                continue
            total += info.file_size
            if len(out) >= MAX_ZIP_FILES or total > MAX_ZIP_BYTES:
                raise ValueError("That zip is too large (limit 3,000 files / 40 MB unzipped)")
            out.append((rel, z.read(info)))
    return out


def save_documents(root: Path, files: List[Dict], label: str = "", folder: Optional[str] = None) -> List[dict]:
    """Save uploaded files under ``root``/documents/<batch>/. ``files`` items are {"name", "data": bytes}.

    A .zip is unpacked into a folder named after it. Returns [{"path", "bytes"}] relative to ``root``.
    """
    root = Path(root).resolve()
    folder = folder or batch_folder(label)
    total = sum(len(f["data"]) for f in files)
    if total > MAX_BATCH_BYTES:
        raise ValueError(f"Too much at once ({total / 1e6:.0f} MB; limit {MAX_BATCH_BYTES / 1e6:.0f} MB)")
    saved: List[dict] = []
    for f in files:
        name = _safe_rel(f.get("name", "")) or "document.txt"
        data = f["data"]
        if len(data) > MAX_FILE_BYTES:
            raise ValueError(f"'{name}' is too large (limit {MAX_FILE_BYTES / 1e6:.0f} MB)")
        if name.lower().endswith(".zip"):
            base = name[:-4] or "archive"
            try:
                members = [(f"{base}/{rel}", blob) for rel, blob in _unzip(data)]
            except zipfile.BadZipFile:
                raise ValueError(f"'{name}' is not a valid zip")
        else:
            members = [(name, data)]
        for rel, blob in members:
            dest = (root / folder / rel).resolve()
            if root not in dest.parents:
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(blob)
            saved.append({"path": dest.relative_to(root).as_posix(), "bytes": len(blob)})
    return saved


def text_to_document(root: Path, text: str, stem: str = "message") -> dict:
    """Turn long text into a .txt document. Returns {"path", "bytes"}."""
    saved = save_documents(root, [{"name": f"{stem}.txt", "data": text.encode("utf-8")}], label=stem)
    return saved[0]


def describe(saved: List[dict], limit: int = 25) -> str:
    """The lines that go into the message so the agent knows what arrived and where."""
    if not saved:
        return ""
    lines = [f"  {s['path']} ({_size(s['bytes'])})" for s in saved[:limit]]
    if len(saved) > limit:
        lines.append(f"  … and {len(saved) - limit} more files in the same folder")
    return ("[documents attached — on your workbench. Read one with workbench read (path, offset); "
            "list a folder with workbench list (path):\n" + "\n".join(lines) + "]")


def _size(n: int) -> str:
    return f"{n / 1024:.1f} KB" if n >= 1024 else f"{n} B"
