"""Offline tests for the AGI loop: the field, prediction, channels, daemon.

Run from project root:
    python -m tests.test_agi_loop

No LLM connection required — a scripted host stands in for the model.
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.agi_loop import LoopConfig, LoopDaemon, set_daemon
from src.agi_loop.budget import DailyBudget
from src.agi_loop.daemon import EXCLUDED_TOOLS, Completion
from src.agi_loop.prediction import Feature, Predictor
from src.agi_loop.workbench import Workbench
from src.agi_loop.embedding import HashEmbedder, cosine
from src.agi_loop.world import AROUND, CLOSE, EDGE, FOCUS, FULL, InnerWorld

PASS = 0
FAIL = 0


def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label}  {detail}")


def _call(name, args, cid="c1"):
    return {"id": cid, "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


class ScriptedHost:
    """Plays back a list of assistant messages, one per completion call."""

    def __init__(self, script=None, tokens=500):
        self.script = list(script or [])
        self.tokens = tokens
        self.calls = []
        self.tool_calls = []
        self.tasks = []
        self.fail = False

    def prepare(self, agent, view):
        tools = [{"type": "function", "function": {"name": n, "description": "", "parameters": {}}}
                 for n in ("memory", "inbox", "agi_loop", "model_router")]
        return [{"role": "system", "content": f"You are {agent}."}], tools

    async def complete(self, config, messages, tools):
        if self.fail:
            raise RuntimeError("provider down")
        self.calls.append({"messages": list(messages), "tools": [t["function"]["name"] for t in tools]})
        msg = self.script.pop(0) if self.script else {"role": "assistant", "content": "I sit with it."}
        return Completion(message=msg, tokens=self.tokens, cost=0.001, model="scripted")

    def call_tool(self, agent, name, args):
        self.tool_calls.append((name, args))
        return "Error: boom" if name == "inbox" and args.get("fail") else f"{name} ok"

    def after_response(self, agent, text):
        return text

    def pending_tasks(self):
        return list(self.tasks)


def _daemon(tmp, host, **cfg):
    base = dict(agent="tester", base_interval_seconds=5, min_interval_seconds=5, max_interval_seconds=60)
    base.update(cfg)
    return LoopDaemon(host, LoopConfig.from_dict(base), Path(tmp))


# ─────────────────────────────────────────────
# 1. Prediction
# ─────────────────────────────────────────────
def test_prediction():
    print("\n=== Prediction ===")
    f = Feature("time.gap", "gauss")
    first = f.observe(120)
    check("first observation carries no surprise", first.surprise == 0.0)
    for _ in range(10):
        steady = f.observe(120)
    check("steady signal → low surprise", steady.surprise < 0.05, steady.surprise)
    jolt = f.observe(5)
    check("outlier → high surprise", jolt.surprise > 0.6, jolt.surprise)
    check("outlier direction is 'less'", jolt.direction == -1)
    check("surprise describes itself", "sooner than you expected" in jolt.describe(), jolt.describe())
    check("belief moved toward the outlier", f.expected_raw() < 120)

    b = Feature("door.arrival", "bern")
    for _ in range(12):
        b.observe(0)
    knock = b.observe(1)
    check("rare event → surprise", knock.surprise > 0.4, knock.surprise)
    quiet = b.observe(0)
    check("expected non-event → no surprise", quiet.surprise < 0.1, quiet.surprise)

    p = Predictor()
    p.observe("body.burn", 1000)
    restored = Predictor.from_dict(json.loads(json.dumps(p.to_dict())))
    check("predictor round-trips", restored.features["body.burn"].n == 1)


# ─────────────────────────────────────────────
# 2. The field
# ─────────────────────────────────────────────
def _field(capacity=20000):
    return InnerWorld(capacity_chars=capacity, embedder=HashEmbedder())


def _settle(w):
    w.ensure_vectors()
    w.layout()


def test_embedder():
    print("\n=== Field: relatedness ===")
    e = HashEmbedder()
    a, b, c = e(["the whale essay draft", "notes on whale migration for the essay", "pizza order receipt"])
    check("related texts are closer", cosine(a, b) > cosine(a, c) + 0.1, (cosine(a, b), cosine(a, c)))
    check("vectors are unit length", abs(cosine(a, a) - 1.0) < 1e-6)
    check("mismatched vectors are unrelated", cosine([1.0], [1.0, 0.0]) == 0.0)


def test_field_layout():
    print("\n=== Field: arranged around focus ===")
    now = time.time()
    w = _field()
    w.begin(1)
    whale, _ = w.upsert("file:whale", "work", "bench", "drafts/whale_essay.md — the whale essay draft",
                        gist="whale essay draft", salience=0.3, now=now)
    notes, _ = w.upsert("seen:whale", "seen", "memory", "memory: notes on whale migration for the essay",
                        gist="whale migration notes", salience=0.3, now=now)
    pizza, _ = w.upsert("note:pizza", "note", "self", "pizza order receipt, pepperoni", gist="pizza receipt",
                        salience=0.9, now=now)
    for i in range(12):
        w.upsert(f"note:filler{i}", "note", "self", f"unrelated filler thought number {i} about gardening tools",
                 gist=f"filler {i}", salience=0.2, now=now)
    w.upsert("time", "time", "time", "evening light · 19:05 UTC", gist="evening, 19:05", salience=0.2,
             mode="level", anchor=True, now=now)

    _settle(w)
    check("unfocused: the most salient sits closest", w.ring(pizza) == CLOSE)

    w.move(text="writing the whale essay")
    _settle(w)
    check("focus on a topic pulls related things close", w.ring(whale) == CLOSE and w.ring(notes) == CLOSE,
          (w.rings.get(whale.id), w.rings.get(notes.id)))
    check("unrelated things fall back", w.ring(pizza) != CLOSE, w.rings.get(pizza.id))
    check("crowded field pushes some to the edge", any(w.ring(i) == EDGE for i in w.in_field()))
    check("gauges are not in the field", all(i.kind != "time" for i in w.in_field()))

    view = w.render(now, {"energy": 0.6, "tokens_left": "120,000", "part_of_day": "evening"})
    check("HUD carries the gauges", "⏱ evening, 19:05" in view and "⚡" in view and "60%" in view, view[:300])
    check("topic focus is shown", 'FOCUS ▸ "writing the whale essay"' in view)
    check("close things in full", "drafts/whale_essay.md — the whale essay draft" in view)
    check("edge things only as traces", "EDGE" in view and "unrelated filler thought number" not in view.split("EDGE")[1])

    w.move(item_id=pizza.id)
    _settle(w)
    check("focus on an item: it is the center", w.ring(pizza) == FOCUS)
    check("whale things drift off when you look away", w.ring(whale) != CLOSE or w.ring(notes) != CLOSE)
    view = w.render(now, {"energy": 0.6})
    check("item focus is shown with its id", f"FOCUS ▸ [{pizza.id}] pizza order receipt" in view)

    w.drop(pizza)
    check("losing the focus leaves its memory as the topic", w.focus_item is None and w.focus_text == "pizza receipt")
    w.move()
    check("unfocus lets the gaze wander", w.focus_label() == "nothing in particular")


def test_capture_and_seeing():
    print("\n=== Field: capture, seeing, alerts ===")
    now = time.time()
    w = _field()
    w.begin(1)
    w.move(text="the essay", deliberate=False)
    m, _ = w.upsert("msg:x", "message", "door", "Trent: urgent — are you there?", salience=0.9, now=now)
    w.capture()
    check("a strong arrival pulls focus to itself", w.focus_item == m.id and w.pulled and w.pulled["to"] == m.id)

    w2 = _field()
    w2.begin(1)
    w2.move(text="the essay", deliberate=True)
    w2.upsert("msg:y", "message", "door", "soft knock", salience=0.55, now=now)
    w2.capture()
    check("chosen focus resists a weaker pull", w2.focus_text == "the essay" and w2.dwell == 1)

    seen = w2.see("memory", {"action": "search", "query": "whales"}, "3 memories about whale songs")
    check("looking brings it into the field", seen.kind == "seen" and seen.source == "memory")
    check("what you look at becomes your focus", w2.focus_item == seen.id)

    w2.upsert("surprise:time.gap", "surprise", "time", "you woke sooner than you expected", salience=0.8, now=now)
    _settle(w2)
    view = w2.render(now, {"energy": 0.9})
    check("surprise flashes as an alert", "ALERTS" in view and "! you woke sooner" in view)
    check("alerts never pull focus", w2.focus_item == seen.id)


def test_capacity_and_decay():
    print("\n=== Field: capacity, holding, decay, growth ===")
    w = _field(capacity=600)
    now = time.time()
    w.begin(1)
    keep, _ = w.upsert("note:keep", "note", "self", "x" * 150, gist="the held thought", salience=0.1, now=now)
    w.hold(keep)
    for i in range(8):
        w.upsert(f"note:{i}", "note", "self", f"thought {i} " + "y" * 120, gist=f"thought {i}", salience=0.2 + i * 0.05, now=now)
    _settle(w)
    w.fit(now)
    check("field stays within capacity", w.used(now) <= w.capacity, w.used(now))
    check("something compressed or faded", w.faded or any(i.fidelity > FULL for i in w.items.values()))
    check("held item survives at full detail", keep.id in w.items and keep.fidelity == FULL)
    check("faded things are logged", len(w.fade_log) == len(w.faded))

    w = _field()
    w.begin(1)
    w.decay(now)
    n, _ = w.upsert("note:n", "note", "self", "a passing thought", salience=0.6, now=now)
    m, _ = w.upsert("msg:m", "message", "door", "unanswered", salience=0.5, valence=-0.3, grows=0.25, now=now)
    for i in range(12):
        w.upsert(f"note:f{i}", "note", "self", f"filler {i}", salience=0.9, now=now)
    _settle(w)
    w.decay(now + 7200)
    check("an unattended thought decays", n.salience <= 0.31, n.salience)
    check("an unanswered message grows heavier", m.valence < -0.6 and m.salience > 0.5, (m.valence, m.salience))
    w.decay(now + 7200 * 8)
    check("a thought left alone eventually fades out", "note:n" not in w.keys)


def test_mood_and_expectations():
    print("\n=== Field: mood, expectations ===")
    now = time.time()
    w = _field()
    w.begin(1)
    w.upsert("msg:1", "message", "door", "angry message", gist="angry message", salience=0.9, valence=-0.8, now=now)
    for _ in range(6):
        w.compute_mood(0.9, now)
    check("tension makes a heavy mood", w.mood["word"] in ("heavy", "unsettled"), w.mood)
    check("mood locates the tension", "angry message" in w.mood["phrase"], w.mood["phrase"])
    check("tension attributed to its source", w.mood["by_source"]["door"]["tension"] > 0)
    w.resolve(w.get("msg:1"))
    for _ in range(8):
        w.compute_mood(0.9, now)
    check("resolving lifts the mood", w.mood["valence"] > 0, w.mood)
    check("low energy reads as drained", w.compute_mood(0.05, now)["word"] == "drained")

    w = _field()
    w.begin(1)
    ex = w.expect("a reply from Trent", "door", 10, now=now)
    check("an expectation is something you hold in mind", w.get(f"expect:{ex.id}").source == "self")
    w.check_expectations(["door"], now + 60)
    check("expectation met", ex.status == "met" and w.get(f"met:{ex.id}") is not None)
    ex2 = w.expect("the draft to change", "bench", 1, now=now)
    w.begin(2)
    w.check_expectations([], now + 120)
    check("expectation broken → surprise", ex2.status == "violated" and w.surprises)

    w.move(text="the draft")
    data = json.loads(json.dumps(w.to_dict()))
    w2 = InnerWorld.from_dict(data, embedder=HashEmbedder())
    check("field round-trips", len(w2.items) == len(w.items) and w2.tick == w.tick and w2.focus_text == "the draft")
    old = {"items": [{"id": "d1", "key": "msg:1", "kind": "message", "region": "door", "text": "x", "gist": "x"}],
           "focus": "door", "predictor": {"window.gap": {"key": "window.gap", "kind": "gauss"}}}
    w3 = InnerWorld.from_dict(old)
    check("old room state is ignored, not crashed on", not w3.items and not w3.predictor.features)


# ─────────────────────────────────────────────
# 3. Workbench & budget
# ─────────────────────────────────────────────
def test_workbench_and_budget():
    print("\n=== Workbench & budget ===")
    tmp = tempfile.mkdtemp()
    try:
        wb = Workbench(Path(tmp) / "bench")
        check("confined to the bench", '"ok": false' in wb.execute({"action": "write", "path": "../x", "content": "a"}))
        wb.execute({"action": "write", "path": "a.md", "content": "hello"})
        check("own writes aren't outside changes", wb.outside_changes() == [])
        (Path(tmp) / "bench" / "b.md").write_text("from the operator")
        check("someone else's write is noticed", wb.outside_changes() == ["b.md"])
        wb.execute({"action": "reflect", "built": "a", "next": "polish"})
        check("reflections recorded", wb.reflections(1)[0]["next"] == "polish")

        b = DailyBudget(Path(tmp) / "budget.json", 1000)
        b.spend(400, 0.0)
        check("energy reflects spend", abs(b.energy - 0.6) < 1e-9)
        check("budget persists", DailyBudget(Path(tmp) / "budget.json", 1000).tokens == 400)
        b.spend(700, 0.0)
        check("over budget → exhausted", b.exhausted and b.tokens_left == 0)
        c = DailyBudget(Path(tmp) / "b2.json", 10_000, cost_per_day=1.0)
        c.spend(10, 0.75)
        check("cost cap can be the tighter limit", abs(c.energy - 0.25) < 1e-9)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_config():
    print("\n=== Config ===")
    c = LoopConfig.from_dict({"daily_token_budget": "5000", "workbench": "false", "temperature": "0.3",
                              "min_interval_seconds": 1, "tiers": [1, 2], "model": None})
    check("strings coerced", c.daily_token_budget == 5000 and c.workbench is False and c.temperature == 0.3)
    check("floors enforced", c.min_interval_seconds == 5.0)
    check("old router keys ignored", not hasattr(c, "tiers"))


# ─────────────────────────────────────────────
# 4. Daemon
# ─────────────────────────────────────────────
def test_daemon_tick():
    print("\n=== Daemon: one tick end to end ===")
    tmp = tempfile.mkdtemp()
    try:
        host = ScriptedHost([
            {"role": "assistant", "content": "", "tool_calls": [_call("attend", {"action": "focus", "source": "door"}, "a"),
                                                              _call("memory", {"action": "search"}, "b")]},
            {"role": "assistant", "content": "", "tool_calls": [_call("reply", {"text": "Here. Working on it."}, "c")]},
            {"role": "assistant", "content": "Answered Trent; back to the bench next."},
        ])
        d = _daemon(tmp, host)
        d.post_message("are you there?", sender="Trent")
        asyncio.run(d.tick())

        first = host.calls[0]
        check("router/self tools filtered out", not (EXCLUDED_TOOLS & set(first["tools"])), first["tools"])
        check("loop tools offered", {"attend", "reply", "loop_control", "workbench"} <= set(first["tools"]))
        check("persona prompt carries the loop preamble", "FIELD" in first["messages"][0]["content"])
        view = first["messages"][-1]["content"]
        check("the model sees through the field", view.startswith("FIELD"), view[:80])
        check("the message is in view", "Trent: are you there?" in view)
        check("the message pulled focus", "FOCUS ▸ [" in view and "Trent" in view.split("FOCUS ▸")[1].splitlines()[0])
        check("registry tool ran through the host", host.tool_calls == [("memory", {"action": "search"})])
        convo = d.conversation.tail(5)
        check("reply recorded in the conversation", convo[-1]["role"] == "agent" and convo[-1]["in_reply_to"])
        msg_item = d.world.get(f"msg:{convo[0]['id']}")
        check("message resolved by the reply", msg_item and msg_item.resolved)
        seen = d.world.get('seen:memory:action=search')
        check("what it looked at entered the field", seen is not None and seen.kind == "seen")
        check("budget spent", d.budget.tokens == 1500)
        t = d.ticks.tail(1)[0]
        check("tick recorded with view + tools", t["view"].startswith("FIELD") and len(t["tool_calls"]) == 3)
        check("journal narrated", "Answered Trent" in d.journal.tail(1)[0]["narrative"])
        procs = {p["stage"]: p for p in d.status()["processes"]}
        check("every stage ran", all(procs[s]["runs"] >= 1 for s in ("sense", "update", "predict", "attend",
                                                                      "feel", "render", "think", "act", "guard", "record")))
        check("channels reported", {"time", "body", "door", "bench"} <= set(d.channel_status))

        d2 = _daemon(tmp, ScriptedHost())
        check("field survives a restart", d2.world.tick == 1 and d2.world.focus_item == d.world.focus_item)
        check("history carried into the next tick", d2.history and "Answered Trent" in d2.history[-1]["response"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_daemon_tasks_and_limits():
    print("\n=== Daemon: inbox tasks, tool limits, errors ===")
    tmp = tempfile.mkdtemp()
    try:
        host = ScriptedHost([{"role": "assistant", "content": "",
                              "tool_calls": [_call("inbox", {"fail": True}, f"x{i}") for i in range(4)]}])
        host.tasks = [{"id": "t1", "type": "task", "status": "pending", "task": "summarise the logs", "priority": "high"}]
        d = _daemon(tmp, host, max_tool_calls_per_tick=2)
        asyncio.run(d.tick())
        check("inbox task appears at the door", d.world.get("task:t1") is not None)
        tools = d.ticks.tail(1)[0]["tool_calls"]
        check("every tool call answered", len(tools) == 4)
        check("calls beyond the limit skipped", [t["ok"] for t in tools][2:] == [False, False]
              and tools[3]["result"].startswith("Skipped"))
        check("failed tool calls felt next tick", d.last_result["tools"][0]["ok"] is False)

        host.tasks = []
        asyncio.run(d.tick())
        check("task done in the inbox → resolved in the room", d.world.get("task:t1").resolved)
        check("body registers the failures", "failed" in (d.world.get("proprio").text if d.world.get("proprio") else ""))

        host.fail = True
        for _ in range(2):
            asyncio.run(d.tick())
        check("errors counted", d.error_streak == 2 and d.last_error == "provider down")
        check("error felt on the floor", "broke off" in d.world.get("proprio").text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_multiple_loops():
    print("\n=== Multiple loops: supervisor + k_os ===")
    from src.agi_loop import (DEFAULT_LOOP, config_file, data_dir, get_daemon, load_config,
                              normalize_loop_id, set_daemon)
    from src.agi_loop.linux import Linux
    check("default loop keeps the original paths", config_file().name == "agi_loop.json" and data_dir().name == "agi_loop")
    check("k_os gets its own config and data", config_file("k_os").name == "agi_loop_k_os.json"
          and data_dir("k_os").name == "agi_loop_k_os")
    check("unknown ids can't make new paths", normalize_loop_id("../etc") == DEFAULT_LOOP)
    check("k_os defaults to the k_os agent", load_config("k_os").agent == "k_os")
    check("the default loop runs the supervisor", DEFAULT_LOOP == "supervisor" and load_config().agent == "supervisor")
    check("removed loop ids fall back to the default", normalize_loop_id("madara") == DEFAULT_LOOP)
    a, b = object(), object()
    set_daemon(a, "supervisor"); set_daemon(b, "k_os")
    check("daemons are kept per loop", get_daemon("supervisor") is a and get_daemon("k_os") is b)
    set_daemon(None, "supervisor"); set_daemon(None, "k_os")
    os.environ.update(SUPERVISOR_LINUX_URL="http://e", SUPERVISOR_LINUX_TOKEN="t1", KOS_LINUX_URL="http://k", KOS_LINUX_TOKEN="t2")
    try:
        e, k = Linux.from_env("supervisor"), Linux.from_env("k_os")
        check("each loop reaches its own machine", e.url == "http://e" and k.url == "http://k" and k.token == "t2")
        check("k_os's tool describes its own user", "'kos'" in k.definition()["description"]
              and "/home/kos" in k.definition()["description"] and "'supervisor'" in e.definition()["description"])
    finally:
        for v in ("SUPERVISOR_LINUX_URL", "SUPERVISOR_LINUX_TOKEN", "KOS_LINUX_URL", "KOS_LINUX_TOKEN"):
            os.environ.pop(v, None)
    check("no machine without its env", Linux.from_env("k_os") is None)


def test_group_chat():
    print("\n=== Group chat: loops talk to each other ===")
    from src.agi_loop.groupchat import GroupChat
    tmp = tempfile.mkdtemp()
    try:
        host = ScriptedHost()
        chat_box = {}
        da = LoopDaemon(host, LoopConfig(agent="supervisor"), Path(tmp) / "a", loop_id="supervisor",
                        group=type("G", (), {"post": lambda self, *a: chat_box["c"].post(*a), "say": lambda self, *a: chat_box["c"].say(*a),
                                             "read": lambda self, n=20: chat_box["c"].read(n)})())
        db = LoopDaemon(host, LoopConfig(agent="k_os"), Path(tmp) / "b", loop_id="k_os", group=da.group)
        chat = GroupChat(Path(tmp) / "g.jsonl", lambda: {"supervisor": da, "k_os": db})
        chat_box["c"] = chat
        chat.post("operator", "Trent", "hello both")
        check("operator message reaches every loop", len(da.queue) == 1 and len(db.queue) == 1)
        check("it is marked as a group message", da.queue[0].get("group") is True and da.queue[0]["sender"] == "Trent")
        out = da.tools.execute("group", {"action": "say", "text": "k_os, you there?"})
        check("a loop's say reaches the other loop, not itself", len(db.queue) == 2 and len(da.queue) == 1, out)
        check("the room keeps the log", [m["sender"] for m in chat.read()] == ["Trent", "supervisor"])
        check("group tool offered to loops in a room", "group" in da.tools.names())
        for _ in range(30):
            chat.post("k_os", "k_os", "ping")
        check("agent-to-agent chatter is not capped", len(da.queue) == 31)
        check("a loop with no room has no group tool",
              "group" not in LoopDaemon(host, LoopConfig(), Path(tmp) / "c").tools.names())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_long_messages():
    print("\n=== Long messages: a whole soul script at the door ===")
    from src.agi_loop.channels import _door_text
    tmp = tempfile.mkdtemp()
    try:
        d = _daemon(tmp, ScriptedHost())
        script = "".join(f"## Section {i}\nI am a line of the soul script number {i}.\n" for i in range(900)).strip()
        check("test script is long", len(script) > 30_000, len(script))
        msg = d.post_message(script, sender="Trent")
        check("the full text is accepted and kept", len(msg["text"]) == len(script)
              and d.conversation.items[-1]["text"] == script)
        check("the door shows a preview with a pointer", len(_door_text(msg)) < 800 and "read_message" in _door_text(msg))
        got, offset, pages = "", 0, 0
        while True:
            out = d.tools.execute("loop_control", {"action": "read_message", "item": msg["id"], "offset": offset})
            body, _, tail = out.partition(": ")[2].rpartition("\n[")
            got += body
            pages += 1
            if tail.startswith("end"):
                break
            offset = int(tail.split("offset=")[1].rstrip("]"))
        check("paging read_message returns every character", got == script and pages > 1, f"{pages} pages")
        check("cap is far above the old 8000", len(d.post_message("x" * 120_000)["text"]) == 100_000)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_documents():
    print("\n=== Documents: whole files and projects in the chat ===")
    import io, zipfile
    from src.agi_loop import documents as docs
    from src.agi_loop.workbench import Workbench
    tmp = tempfile.mkdtemp()
    try:
        wb = Workbench(Path(tmp) / "bench")
        big = "".join(f"line {i} of the soul script\n" for i in range(3000))
        saved = docs.save_documents(wb.root, [{"name": "soul.txt", "data": big.encode()}])
        check("a document is saved under documents/", saved[0]["path"].startswith("documents/") and saved[0]["bytes"] == len(big))
        got, off, pages = "", 0, 0
        while True:
            out = wb.execute({"action": "read", "path": saved[0]["path"], "offset": off})
            body, _, tail = out.rpartition("\n[")
            if not tail:
                got += out
                break
            got += body
            pages += 1
            if "end of file" in tail:
                break
            off = int(tail.split("offset=")[1].rstrip("]"))
        check("workbench read pages through a long file", got == big and pages > 1, f"{pages} pages")

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as z:
            z.writestr("proj/src/main.py", "print('hi')\n")
            z.writestr("proj/README.md", "# proj\n")
            z.writestr("proj/.git/config", "nope")
            z.writestr("proj/node_modules/x/index.js", "nope")
            z.writestr("../../evil.txt", "escape")
        saved = docs.save_documents(wb.root, [{"name": "proj.zip", "data": buf.getvalue()}], folder="documents/t1")
        paths = sorted(s["path"] for s in saved)
        check("a zip unpacks into a folder", "documents/t1/proj/proj/src/main.py" in paths and "documents/t1/proj/proj/README.md" in paths, paths)
        check("junk folders are skipped", not any(".git" in x or "node_modules" in x for x in paths))
        check("zip paths can't escape", not (Path(tmp) / "evil.txt").exists() and all(x.startswith("documents/t1/") for x in paths))
        listing = json.loads(wb.execute({"action": "list", "path": "documents/t1/"}))
        check("workbench list takes a folder prefix", len(listing["files"]) == len(paths))
        try:
            docs.save_documents(wb.root, [{"name": "x.zip", "data": b"not a zip"}])
            check("a bad zip is refused", False)
        except ValueError:
            check("a bad zip is refused", True)
        check("describe names every path", "documents/t1/proj/proj/src/main.py" in docs.describe(saved))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_pace_control():
    print("\n=== Daemon: self-chosen pace ===")
    tmp = tempfile.mkdtemp()
    try:
        d = _daemon(tmp, ScriptedHost(), min_interval_seconds=20, max_interval_seconds=1800)
        d.running = True
        out = d.tools.execute("loop_control", {"action": "pace", "seconds": 30, "reason": "something is live"})
        check("pace sets the wake interval", d.pace and d.pace[0] == 30 and d._next_interval()[0] == 30, out)
        d.tools.execute("loop_control", {"action": "pace", "seconds": 1})
        check("pace is clamped to the minimum", d.pace[0] == 20)
        d.tools.execute("loop_control", {"action": "pace", "seconds": 99999})
        check("pace is clamped to the maximum", d.pace[0] == 1800)
        d.tools.execute("loop_control", {"action": "pace"})
        check("pace with no seconds returns to adaptive", d.pace is None)
        d.tools.execute("loop_control", {"action": "pace", "seconds": 30})
        d.request_rest(10, "tired")
        check("rest still overrides a pace", d._next_interval()[0] == 600)
        check("status reports the pace", d.status()["pace"]["seconds"] == 30)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_restart_continuity():
    print("\n=== Restart: clock, pace, letter, autostart, slab ===")
    tmp = tempfile.mkdtemp()
    try:
        b = DailyBudget(Path(tmp) / "b.json", 1_000_000, 1.0)
        b.spend(100_000, 0.5)
        check("the cost cap, when tighter, is what 'left' reports", b.cost_binds and b.left_text().startswith("$0.50 of $1.00"),
              b.left_text())
        b2 = DailyBudget(Path(tmp) / "b2.json", 1_000_000, 100.0)
        b2.spend(100_000, 0.5)
        check("otherwise it reports tokens", not b2.cost_binds and "900,000 tokens" in b2.left_text())

        d = _daemon(tmp, ScriptedHost(), min_interval_seconds=20, max_interval_seconds=1800)
        d.running = True
        asyncio.run(d.tick())
        asyncio.run(d.tick())
        view = d.ticks.tail(1)[0]["view"]
        check("the HUD carries a measured clock line in the operator's time and UTC",
              "⏲ now" in view and "(the operator's time)" in view and "UTC" in view and "tick 1 began" in view and "ran" in view,
              view[:400])
        check("the field header is in the operator's time zone", view.splitlines()[0].endswith(("night", "morning", "afternoon", "evening"))
              and "UTC" in view.splitlines()[0], view.splitlines()[0])
        d.set_pace(600, "watching")
        d._next_interval()
        check("the pace line says what rhythm she's on", d.pace_note.startswith("pace: you chose 10m 00s"), d.pace_note)
        d.budget.spend(10**12, 0)   # drain energy: a chosen pace gets stretched, and she's told
        d._next_interval()
        check("…and when energy stretches it", "stretches it" in d.pace_note, d.pace_note)
        d.stopped_at, d.stop_reason = time.time(), "cancelled"
        d.save()

        Path(d.workbench.root, "handoff").mkdir(exist_ok=True)
        Path(d.workbench.root, "handoff", "letter.md").write_text("Read this before anything else. — E.", encoding="utf-8")
        d.autostart_file.write_text("x")
        d2 = _daemon(tmp, ScriptedHost(), min_interval_seconds=20, max_interval_seconds=1800)
        check("a chosen pace survives a restart", d2.pace and d2.pace[0] == 600)
        d2._admit_handoff()
        it = d2.world.get("handoff-letter")
        check("after a restart the letter is the first thing in view: held and focused",
              it is not None and it.held and d2.world.focus_item == it.id and "Read this before anything else" in it.text)
        d2.wake_reason, d2.started_at = "start", time.time()
        check("she's told she is a new run, and how the last one ended",
              "new run of yourself" in d2._woke_line(30) and "went down under you" in d2._woke_line(30))
        check("a crash or deploy leaves the autostart mark", d2.autostart_file.exists())
        d2.request_stop("operator")
        check("a deliberate stop clears it", not d2.autostart_file.exists())

        from src.agi_loop.groupchat import Slab
        s = Slab(Path(tmp) / "slab.jsonl")
        e1 = s.write("k_os", "k_os", 550, "the seam line, credited to E.")
        e2 = s.write("supervisor", "supervisor", 510, "received.")
        s2 = Slab(Path(tmp) / "slab.jsonl")
        check("the slab numbers entries across minds and survives a restart",
              (e1["seq"], e2["seq"]) == (1, 2) and s2.seq == 2 and [e["author"] for e in s2.read()] == ["k_os", "supervisor"])
        check("reading since a number returns only what came after", [e["seq"] for e in s2.read(since=1)] == [2])
        check("entries carry wall time and the author's tick", e1["tick"] == 550 and "T" in e1["ts"])
        md = (Path(tmp) / "slab.md").read_text(encoding="utf-8")
        check("and the slab reads as a markdown document, in order", md.index("#1 ·") < md.index("#2 ·") and "k_os (tick 550)" in md)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_daemon_guards():
    print("\n=== Daemon: repetition guard ===")
    tmp = tempfile.mkdtemp()
    try:
        host = ScriptedHost()   # says the same thing every tick
        d = _daemon(tmp, host, stale_streak_limit=2, max_guard_rests=1, guard_rest_minutes=7)
        d.running = True
        for _ in range(3):
            asyncio.run(d.tick())
        check("repetition forces a rest", d.guard_rests == 1 and d.rest_request and d.rest_request[0] == 420)
        check("the body notices being made to stop", d.world.get("guard-rest") is not None)
        secs, reason = d._next_interval()
        check("rest overrides cadence", secs == 420 and "repeating" in reason)
        for _ in range(3):
            asyncio.run(d.tick())
        check("still repeating after max rests → stop", not d.running and "forced rests" in d.stop_reason)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_daemon_run_and_wake():
    print("\n=== Daemon: wall-time run, woken by a message ===")
    tmp = tempfile.mkdtemp()
    try:
        host = ScriptedHost()

        async def scenario():
            d = _daemon(tmp, host, base_interval_seconds=60, min_interval_seconds=60)
            set_daemon(d)
            d.start()
            await asyncio.sleep(0.3)
            first = d.world.tick
            phase = d.phase
            t0 = time.monotonic()
            d.post_message("wake up")
            while d.world.tick == first and time.monotonic() - t0 < 5:
                await asyncio.sleep(0.05)
            woke_in = time.monotonic() - t0
            reason = d.wake_reason
            await asyncio.sleep(0.3)
            second = d.world.tick
            t1 = time.monotonic()
            await asyncio.to_thread(d.post_message, "from a worker thread")
            while d.world.tick == second and time.monotonic() - t1 < 5:
                await asyncio.sleep(0.05)
            thread_woke_in = time.monotonic() - t1
            d.pause()
            await asyncio.sleep(0.2)
            paused_phase = d.phase
            d.stop("test")
            await asyncio.sleep(0.2)
            return first, phase, woke_in, reason, paused_phase, d, thread_woke_in

        first, phase, woke_in, reason, paused_phase, d, thread_woke_in = asyncio.run(scenario())
        check("first tick runs at start", first == 1)
        check("then it sleeps on wall time", phase == "sleeping", phase)
        check("a message wakes it early", woke_in < 2 and reason == "message", (woke_in, reason))
        check("a message from another thread wakes it too", thread_woke_in < 2, thread_woke_in)
        check("pause holds it", paused_phase == "paused", paused_phase)
        check("stop ends it", not d.running and d.phase == "stopped" and d.stop_reason == "test")

        from src.tools.agi_loop import AGILoopTool
        st = json.loads(AGILoopTool.execute({"action": "status"}))
        check("chat tool sees the loop", st["phase"] == "stopped")
        check("chat tool reads the field", AGILoopTool.execute({"action": "field"}).startswith("FIELD"))
        set_daemon(None)
        check("chat tool without a loop", json.loads(AGILoopTool.execute({"action": "status"}))["ok"] is False)
    finally:
        set_daemon(None)
        shutil.rmtree(tmp, ignore_errors=True)


def test_cache_llm_and_gate():
    print("\n=== Cache layout, the llm tool, the quiet gate ===")
    tmp = tempfile.mkdtemp()
    try:
        # Cache: history is append-only until it doubles, and breakpoints sit on system, history end, now.
        host = ScriptedHost()
        d = _daemon(tmp, host, history_window=2, quiet_gate=False)
        for _ in range(4):
            asyncio.run(d.tick())
        prev, last = host.calls[-2]["messages"], host.calls[-1]["messages"]
        strip = lambda ms: [{k: v for k, v in m.items() if k != "cache"} for m in ms]
        check("last tick's system + history is a prefix of this tick's",
              strip(last[:len(prev) - 1]) == strip(prev[:-1]))
        marks = [i for i, m in enumerate(last) if m.get("cache")]
        check("three breakpoints: system, end of history, this moment",
              marks == [0, len(last) - 2, len(last) - 1], marks)
        check("history grows to 2x the window before trimming", len(d.history) == 4, len(d.history))
        asyncio.run(d.tick())
        check("then trims back to the window", len(d.history) == 2, len(d.history))

        # The host turns marks into cache_control only where the provider needs explicit breakpoints.
        from web.app import _OrionLoopHost
        msgs = [{"role": "system", "content": "s", "cache": True}, {"role": "user", "content": "u"}]
        claude = _OrionLoopHost._cache_marks({"provider": "openrouter"}, "anthropic/claude-sonnet-5.5", msgs)
        check("Claude via OpenRouter gets cache_control",
              claude[0]["content"][0].get("cache_control") == {"type": "ephemeral"} and "cache" not in claude[0])
        gpt = _OrionLoopHost._cache_marks({"provider": "openrouter"}, "openai/gpt-5.5", msgs)
        check("auto-caching providers just lose the mark", gpt[0] == {"role": "system", "content": "s"})

        # The llm tool: a side call with only the prompt, charged to the tick, model by choice.
        class SideHost(ScriptedHost):
            async def side_complete(self, config, spec, messages, max_tokens):
                self.side = (spec, messages, max_tokens)
                return Completion(message={"role": "assistant", "content": "side answer"}, tokens=40,
                                  cost=0.0002, model=spec["openrouter"])
        host = SideHost([{"role": "assistant", "content": "", "tool_calls": [_call("llm", {"prompt": "sum 2+2"})]},
                         {"role": "assistant", "content": "done"}])
        d2 = _daemon(Path(tmp) / "llm", host, quiet_gate=False)
        check("llm tool offered", "llm" in d2.tools.names())
        asyncio.run(d2.tick())
        spec, side_msgs, cap = host.side
        check("default model is deepseek_reasoner", spec["openrouter"].startswith("deepseek/"), spec)
        check("side call sees only the prompt", side_msgs == [{"role": "user", "content": "sum 2+2"}], side_msgs)
        check("its answer comes back as the tool result", "side answer" in d2.ticks.tail(1)[0]["tool_calls"][0]["result"])
        check("its tokens are charged to the tick", d2.ticks.tail(1)[0]["tokens"] == 2 * 500 + 40)
        out = asyncio.run(d2.side_llm({"set_default": "deepseek_chat"}))
        check("the mind can switch its default", d2.llm_default() == "deepseek_chat", out)
        d2.save()
        check("and it survives a restart", LoopDaemon(host, d2.config, Path(tmp) / "llm").llm_default() == "deepseek_chat")
        check("unknown model is refused", asyncio.run(d2.side_llm({"prompt": "x", "model": "nope"})).startswith("Error"))

        # The gate: quiet timer wakes after an idle tick are slept through, a few at most.
        host = ScriptedHost()
        d3 = _daemon(Path(tmp) / "gate", host, gate_max_skips=2)
        asyncio.run(d3.tick())                      # start: always thinks
        d3.wake_reason = "timer"
        calls = len(host.calls)
        asyncio.run(d3.tick())
        asyncio.run(d3.tick())
        check("quiet timer wakes after an idle tick make no model call", len(host.calls) == calls, len(host.calls))
        check("…and are counted", d3.gated_streak == 2)
        asyncio.run(d3.tick())
        check("after gate_max_skips one is let through", len(host.calls) == calls + 1)
        check("and the mind is told what it slept through", "slept through 2 quiet wake" in host.calls[-1]["messages"][-1]["content"])
        d3.post_message("hello")
        d3.wake_reason = "timer"
        before = len(host.calls)
        asyncio.run(d3.tick())
        check("a message always gets a thought", len(host.calls) == before + 1)
        d3.tools.execute("loop_control", {"action": "gate", "on": False})
        d3.world.items.clear()
        before = len(host.calls)
        asyncio.run(d3.tick()); asyncio.run(d3.tick())
        check("with the gate off every wake thinks", len(host.calls) == before + 2)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_prediction()
    test_embedder()
    test_field_layout()
    test_capture_and_seeing()
    test_capacity_and_decay()
    test_mood_and_expectations()
    test_workbench_and_budget()
    test_config()
    test_daemon_tick()
    test_daemon_tasks_and_limits()
    test_multiple_loops()
    test_group_chat()
    test_long_messages()
    test_documents()
    test_pace_control()
    test_restart_continuity()
    test_daemon_guards()
    test_daemon_run_and_wake()
    test_cache_llm_and_gate()

    print(f"\n{'='*40}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL:
        sys.exit(1)
    else:
        print("All tests passed.")
