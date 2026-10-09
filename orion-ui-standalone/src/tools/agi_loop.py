"""agi_loop — lets an agent in ordinary chat look in on (or talk to) its running loop.

Inside the loop itself this tool is not offered; the loop has its own
attend / reply / loop_control tools. See ``src/agi_loop``.
"""

import json

from src.agi_loop import get_daemon


class AGILoopTool:
    @staticmethod
    def definition() -> dict:
        return {
            "name": "agi_loop",
            "description": (
                "Look in on your continuously running loop (your inner world between conversations). "
                "Actions: 'status' — phase, energy, mood, focus; "
                "'field' — your field exactly as your looping self last saw it; "
                "'message' (text) — leave a message at the loop's door (it wakes the loop); "
                "'pause' / 'resume' / 'stop' (reason)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["status", "field", "message", "pause", "resume", "stop"]},
                    "text": {"type": "string", "description": "Message text for 'message'."},
                    "reason": {"type": "string", "description": "Why, for 'stop'."},
                },
                "required": ["action"],
            },
        }

    @staticmethod
    def execute(arguments: dict) -> str:
        d = get_daemon()
        action = (arguments or {}).get("action", "status")
        if d is None:
            return json.dumps({"ok": False, "reason": "The loop has not been started in this process."})
        if action == "status":
            s = d.status()
            return json.dumps({k: s[k] for k in ("running", "paused", "phase", "tick", "focus_name", "mood",
                                                 "budget", "waiting", "stop_reason")}, default=str)
        if action == "field":
            last = d.ticks.tail(1)
            return last[0].get("view", "") if last else "The loop hasn't seen anything yet."
        if action == "message":
            text = (arguments.get("text") or "").strip()
            if not text:
                return json.dumps({"ok": False, "reason": "'text' is required"})
            d.post_message(text, sender="chat")
            return json.dumps({"ok": True, "message": "Left at the door."})
        if action == "pause":
            d.pause()
            return json.dumps({"ok": True})
        if action == "resume":
            d.resume()
            return json.dumps({"ok": True})
        if action == "stop":
            if not d.running:
                return json.dumps({"ok": False, "reason": "Loop is not running"})
            d.stop(f"chat: {arguments.get('reason') or 'requested'}")
            return json.dumps({"ok": True})
        return json.dumps({"error": f"Unknown action: {action}"})
