"""Tools that exist only inside the loop: attention, replies, rest/stop, the bench."""

import json
import time
from typing import TYPE_CHECKING, Callable, Dict, List, Tuple

from .prediction import EXPECTATION_CHANNELS
from .world import CLOSE, TRACE, _clip, source_name

if TYPE_CHECKING:
    from .daemon import LoopDaemon


ATTEND_DEF = {
    "name": "attend",
    "description": (
        "Direct your focus. Your field arranges itself around whatever you focus on: the most related "
        "things come close and clear, the rest drifts to the edge. Using any other tool to look at something "
        "(memory, search, a file) also focuses you on what you saw. "
        "Actions: 'focus' — on an item (item id), on a topic or thought (text), or on whatever is most "
        "pressing from a source (source: door, bench, self); 'unfocus' — let your gaze wander; "
        "'hold' (item) — keep it from fading (max 3); 'release' (item); "
        "'resolve' (item) — mark it dealt with; its tension lifts; "
        "'intend' (text) — set an intention you'll keep in view; "
        "'expect' (text, channel door|bench, within_minutes) — make a prediction; you'll feel it met or broken; "
        "'note' (text) — set a thought into your field."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string",
                       "enum": ["focus", "unfocus", "hold", "release", "resolve", "intend", "expect", "note"]},
            "item": {"type": "string", "description": "Item id as shown in brackets, e.g. d3."},
            "text": {"type": "string"},
            "source": {"type": "string", "description": "door, bench, self, or a tool name"},
            "channel": {"type": "string", "enum": list(EXPECTATION_CHANNELS)},
            "within_minutes": {"type": "number"},
        },
        "required": ["action"],
    },
}

REPLY_DEF = {
    "name": "reply",
    "description": (
        "Answer someone waiting at the door. They see your reply in the loop's conversation. "
        "Resolves that message. 'item' defaults to the oldest unanswered message."
    ),
    "parameters": {
        "type": "object",
        "properties": {"item": {"type": "string"}, "text": {"type": "string"}},
        "required": ["text"],
    },
}

CONTROL_DEF = {
    "name": "loop_control",
    "description": (
        "Your own running process. 'status' — how you're running. "
        "'pace' (seconds, reason) — set how often you wake: go fast (down to the minimum) while something "
        "is live, slow down when it isn't, as often as you like; pace with no seconds returns to your "
        "adaptive rhythm. Low energy still slows you. "
        "'rest' (minutes, reason) — sleep longer than usual when nothing is worth spending energy on; "
        "a message at the door will still wake you. "
        "'stop' (reason) — end the loop entirely. Prefer rest. "
        "'request_tool' (text) — one line to the operator asking for a tool you don't have and what you'd do with it; "
        "it doesn't wake anyone or interrupt you. "
        "'read_message' (item, offset) — a long message at the door shows only as a preview; this returns "
        "the full text in pages of about 6000 characters. Give the [item] id or the message id, and the "
        "offset the previous page ended at (it tells you the next one). "
        "'gate' (on: true|false, reason) — the quiet gate. While it's on, a timer wake that finds nothing new "
        "after a tick where you did nothing is slept through without a model call (a few in a row at most, and "
        "never a message or a surprise). Turn it off when you want every wake, even quiet ones."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "action": {"type": "string",
                       "enum": ["status", "pace", "rest", "stop", "read_message", "request_tool", "gate"]},
            "on": {"type": "boolean"},
            "text": {"type": "string"},
            "item": {"type": "string"},
            "offset": {"type": "integer"},
            "minutes": {"type": "number"},
            "seconds": {"type": "number"},
            "reason": {"type": "string"},
        },
        "required": ["action"],
    },
}


GROUP_DEF = {
    "name": "group",
    "description": (
        "The room you share with the other minds (and the operator). 'say' (text) — speak to the room; everyone else "
        "hears it at their door. 'read' — the latest messages (long ones show a preview; read with id and offset pages through one). Answering a [group chat] message with reply "
        "already posts to the room, so use 'say' to start something or add to it. Don't ping-pong: speak when "
        "you have something to add. "
        "The SLAB is one persistent file in the room that every mind can read and write — shared state, not talk. "
        "'slab_write' (text) appends an entry stamped with a slab sequence number, the host's wall time, your name "
        "and your tick; nobody can edit or delete an entry, including you. 'slab_read' (limit, since) — the latest "
        "entries, or only those after sequence number 'since'. It does not wake anyone; it's there when they look."
    ),
    "parameters": {
        "type": "object",
        "properties": {"action": {"type": "string", "enum": ["say", "read", "slab_write", "slab_read"]},
                       "text": {"type": "string"}, "limit": {"type": "integer"}, "id": {"type": "string"},
                       "offset": {"type": "integer"}, "since": {"type": "integer"}},
        "required": ["action"],
    },
}


def llm_definition(models: List[str], default: str) -> dict:
    return {
        "name": "llm",
        "description": (
            "Hand a self-contained piece of work to another model: a summary, a draft, a classification, a "
            "reformat, a first pass you'll check, a second opinion. It sees only what you put in 'prompt' (and "
            "'system', if you give one) — not your identity, field, history or tools — and returns its text to "
            "you here. Its cost comes out of your energy. The default is deepseek_reasoner (DeepSeek V4 Pro): "
            "cheap, and it thinks before it answers. Cheapest and quickest: gpt_mini (GPT-6 Luna), claude_haiku "
            "(Haiku 5.5), deepseek_chat (V4.1 Flash), gemini_flash (3.8 Flash). Strong, mid-priced: qwen (3.8 "
            "Max), grok (4.7), gpt (GPT-6.1 Sol), claude_sonnet (5.5), gemini_pro (3.1 Pro); kimi (K3) is cheap "
            "to read but dear to write. Frontier, and priced like it: claude_opus (5.5), then claude_fable "
            "(Fable 5.1) and gpt_pro (GPT-6 Astra) at the top. "
            "hermes (Nous Hermes 4, 405B) is for specific circumstances: it follows its instructions with few "
            "refusals, so reach for it when the others decline something you have a real reason to need — "
            "dark fiction, frank detail, a view they won't voice. It's an older open model, weaker than the "
            "frontier ones, so check what it gives you. Ask several the same thing to compare them.'set_default' changes which one you get when you don't "
            "name one (say deepseek_chat when you'd rather be chatty than deliberate); it keeps across "
            "restarts. Your choice when and which; keep your own judgment for what needs you."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "The whole task, with everything it needs."},
                "model": {"type": "string", "enum": models,
                          "description": f"Which model this time (else your default; the operator's is {default})."},
                "set_default": {"type": "string", "enum": models,
                                "description": "Make this your default from now on. Can be sent without a prompt."},
                "system": {"type": "string", "description": "Optional instructions for how it should answer."},
                "max_tokens": {"type": "integer", "description": "Cap on its answer (the operator sets a ceiling)."},
            },
        },
    }


PAGE_CHARS = 6000


class LoopTools:
    def __init__(self, daemon: "LoopDaemon"):
        self.d = daemon
        self.handlers: Dict[str, Tuple[dict, Callable[[dict], str]]] = {
            "attend": (ATTEND_DEF, self.attend),
            "reply": (REPLY_DEF, self.reply),
            "loop_control": (CONTROL_DEF, self.control),
        }
        if daemon.group:
            self.handlers["group"] = (GROUP_DEF, self.group)
        if daemon.workbench:
            self.handlers["workbench"] = (daemon.workbench.definition(), daemon.workbench.execute)
        if daemon.linux:
            self.handlers["linux"] = (daemon.linux.definition(), daemon.linux.execute)
        c = daemon.config
        if c.llm_models and callable(getattr(daemon.host, "complete", None)):
            # A model call: the daemon awaits it itself (LoopDaemon.side_llm), never through execute().
            default = c.llm_default if c.llm_default in c.llm_models else next(iter(c.llm_models))
            self.handlers["llm"] = (llm_definition(list(c.llm_models), default), self._async_only)

    @staticmethod
    def _async_only(args: dict) -> str:
        raise RuntimeError("llm runs through the daemon")

    def names(self) -> List[str]:
        return list(self.handlers)

    def definitions(self) -> List[dict]:
        return [{"type": "function", "function": d} for d, _ in self.handlers.values()]

    def execute(self, name: str, args: dict) -> str:
        return self.handlers[name][1](args or {})

    # ── attend ────────────────────────────────────────────────────

    def _view(self) -> str:
        """What comes into view after shifting focus: the focus and what's close."""
        w = self.d.world
        w.ensure_vectors()
        w.layout()
        now = time.time()
        lines = [f"Focus: {w.focus_label()}"]
        focus = w.items.get(w.focus_item) if w.focus_item else None
        if focus:
            lines[0] = f"Focus: [{focus.id}] {focus.text}"
        close = [i for i in w.in_field() if i.id != w.focus_item and w.ring(i) == CLOSE]
        close.sort(key=lambda i: -w.rings.get(i.id, (0, 0.0))[1])
        for it in close:
            lines.append(f"  close: [{it.id}] {'◆ ' if it.held else ''}{it.line(w.detail(it), now)}")
        if not close:
            lines.append("  nothing else feels close to it")
        return "\n".join(lines)

    def attend(self, args: dict) -> str:
        w = self.d.world
        action = args.get("action", "focus")
        ref = (args.get("item") or "").strip().strip("[]")
        item = w.get(ref) if ref else None
        if ref and not item:
            return f"There is no [{ref}] in your field — it may have faded."
        text = (args.get("text") or "").strip()

        if action == "focus":
            if item:
                w.move(item_id=item.id)
                self.d.event("attend", f"focused [{item.id}] {item.gist}")
            elif args.get("source"):
                src = args["source"].strip()
                pick = sorted((i for i in w.in_field() if i.source == src and not i.resolved),
                              key=lambda i: -i.salience)
                if not pick:
                    return f"Nothing from {source_name(src)} is in your field right now."
                w.move(item_id=pick[0].id)
                self.d.event("attend", f"focused {src}: [{pick[0].id}] {pick[0].gist}")
            elif text:
                w.move(text=text)
                self.d.event("attend", f'focused on "{_clip(text, 60)}"')
            else:
                return "Focus on what? Give an item id, a source, or text."
            return self._view()
        if action == "unfocus":
            w.move()
            self.d.event("attend", "let the gaze wander")
            return self._view()

        if action in ("hold", "release", "resolve") and not item:
            return f"'{action}' needs an item id."
        if action == "hold":
            if w.detail(item) >= TRACE:
                return f"[{item.id}] is too faint to hold — focus on it first."
            if not w.hold(item):
                return "You're already holding three things — release one first."
            return f"Holding [{item.id}] {item.gist}."
        if action == "release":
            item.held = False
            return f"Released [{item.id}]."
        if action == "resolve":
            w.resolve(item)
            self.d.event("resolve", f"resolved [{item.id}] {item.gist}")
            return f"Resolved [{item.id}] {item.gist}."

        if not text:
            return f"'{action}' needs text."
        if action == "intend":
            it, _ = w.upsert(f"intent:{text.lower()[:60]}", "intention", "self", f"you intend to {text}",
                             gist=f"intend: {text[:48]}", salience=0.7, valence=0.1)
            w.hold(it)
            return f"Intention set [{it.id}] — you'll keep it in view."
        if action == "expect":
            channel = args.get("channel", "door")
            if channel not in EXPECTATION_CHANNELS:
                return f"You can expect things from: {', '.join(EXPECTATION_CHANNELS)}."
            minutes = max(1.0, min(24 * 60.0, float(args.get("within_minutes") or 30)))
            ex = w.expect(text, channel, minutes)
            self.d.event("expect", f"expects {text} from {channel} within {minutes:.0f}m")
            return f"Expectation set ({ex.id}): {text} from {source_name(channel)} within {minutes:.0f} minutes."
        if action == "note":
            it, _ = w.upsert(f"note:{w.tick}:{text.lower()[:40]}", "note", "self", text, salience=0.5, valence=0.05)
            return f"Noted [{it.id}]."
        return f"Unknown action '{action}'."

    # ── reply ─────────────────────────────────────────────────────

    def reply(self, args: dict) -> str:
        text = self.d.declare_state((args.get("text") or "").strip())
        if not text:
            return "Say something."
        w = self.d.world
        ref = (args.get("item") or "").strip().strip("[]")
        item = w.get(ref) if ref else None
        if ref and (not item or item.kind != "message"):
            return f"[{ref}] isn't a message at the door."
        if not item:
            waiting = sorted((i for i in w.items.values() if i.kind == "message" and not i.resolved), key=lambda i: i.born)
            item = waiting[0] if waiting else None
        self.d.record_reply(text, item)
        return "Sent." + (f" [{item.id}] resolved." if item else " (No one was waiting; it's in the conversation.)")

    # ── group ─────────────────────────────────────────────────────

    def group(self, args: dict) -> str:
        g, d = self.d.group, self.d
        action = args.get("action") or "say"
        if action == "slab_write":
            try:
                e = g.slab.write(d.config.agent, d.loop_id, d.world.tick, d.declare_state(args.get("text") or ""))
            except ValueError as exc:
                return str(exc)
            d.event("slab", f"wrote slab #{e['seq']}: {_clip(e['text'], 80)}")
            return f"Written to the slab as #{e['seq']} at {e['ts']}. It can't be changed now."
        if action == "slab_read":
            entries = g.slab.read(int(args.get("limit") or 30), int(args.get("since") or 0))
            return "\n".join(g.slab.line(e) for e in entries) or "The slab is empty."
        if action == "read":
            if args.get("id"):
                m = next((m for m in g.read(100) if m["id"] == args["id"]), None)
                if not m:
                    return "No such message in the recent room."
                off = max(0, int(args.get("offset") or 0))
                page = m["text"][off:off + PAGE_CHARS]
                end = off + len(page)
                tail = f"\n[characters {off}-{end} of {len(m['text'])} — next: offset={end}]" if end < len(m["text"]) else "\n[end]"
                return f"{m['sender']}: {page}{tail}"
            msgs = g.read(int(args.get("limit") or 20))
            return "\n".join(
                f"{m['sender']}: {m['text'][:500]}" + (f"… [{len(m['text']):,} chars — group read id={m['id']}]" if len(m["text"]) > 500 else "")
                for m in msgs) or "The room is quiet."
        text = d.declare_state((args.get("text") or "").strip())
        if not text:
            return "Say what?"
        return g.say(d.loop_id, d.config.agent, text)

    def read_message(self, args: dict) -> str:
        ref = (args.get("item") or "").strip().strip("[]")
        if not ref:
            return "read_message needs an item or message id."
        item = self.d.world.get(ref)
        mid = (item.meta.get("message_id") if item else None) or ref
        entry = next((m for m in reversed(self.d.conversation.items) if m.get("id") == mid), None)
        if not entry:
            return f"No message '{ref}' in the conversation record."
        text = entry.get("text", "")
        offset = max(0, int(args.get("offset") or 0))
        page = text[offset:offset + PAGE_CHARS]
        end = offset + len(page)
        more = f"\n[characters {offset}-{end} of {len(text)} — next: offset={end}]" if end < len(text) else f"\n[end — {len(text)} characters]"
        return f"{entry.get('sender', '')}: {page}{more}"

    # ── loop_control ──────────────────────────────────────────────

    def control(self, args: dict) -> str:
        action = args.get("action", "status")
        reason = (args.get("reason") or "").strip()
        if action == "status":
            s = self.d.status()
            return json.dumps({k: s[k] for k in ("phase", "tick", "session_ticks", "session_tokens", "focus", "mood", "budget", "pace")},
                              default=str)
        if action == "read_message":
            return self.read_message(args)
        if action == "pace":
            if args.get("seconds") in (None, ""):
                self.d.set_pace(None)
                return "Back to your adaptive rhythm."
            c = self.d.config
            granted = self.d.set_pace(float(args["seconds"]), reason)
            note = "" if granted == float(args["seconds"]) else f" (limits are {c.min_interval_seconds:.0f}s–{c.max_interval_seconds:.0f}s)"
            return f"You'll wake about every {granted:.0f}s from now until you change it.{note}"
        if action == "rest":
            minutes = float(args.get("minutes") or 30)
            granted = self.d.request_rest(minutes, reason or "chose to rest")
            return f"You'll rest about {granted:.0f} minutes after this tick. A message will still wake you."
        if action == "stop":
            self.d.request_stop(f"agent: {reason or 'no reason given'}")
            return "The loop will stop after this tick."
        if action == "gate":
            if not self.d.config.quiet_gate:
                return "The quiet gate is switched off by the operator; every wake is a full thought."
            on = args.get("on")
            if on is None:
                return f"The quiet gate is {'on' if self.d.gate_on else 'off'}."
            on = on if isinstance(on, bool) else str(on).lower() in ("1", "true", "yes", "on")
            self.d.gate_on = on
            self.d.event("gate", f"gate {'on' if on else 'off'}" + (f" — {reason}" if reason else ""))
            return ("Gate on: quiet wakes after an idle tick will be slept through." if on
                    else "Gate off: every wake is a full thought, quiet or not.")
        if action == "request_tool":
            text = (args.get("text") or reason).strip()
            if not text:
                return "Request what? One line: the tool, and what you'd do with it."
            e = self.d.request_tool(text)
            return (f"Noted for the operator as request #{e['id']}. Nothing was interrupted and nobody was woken; "
                    f"he sees it on the loop page.")
        return f"Unknown action '{action}'."
