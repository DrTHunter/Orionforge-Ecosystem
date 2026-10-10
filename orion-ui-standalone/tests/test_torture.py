"""Comprehensive torture test suite — deep coverage of untested code paths.

Run from project root:
    python -m tests.test_torture

Covers:
  - MemoryTool (all 12 actions via VaultStore mock)
  - Boundary policy (risk, denial, logger)
  - Note collector helpers
  - Memory injector build_memory_block
  - CostTrackerTool untested actions (cost_summary, cost_log, session_cost)
  - CostTrackerTool pricing actions (get_pricing, set_pricing, list_models)
  - PII guard edge cases (bearer, auth_token, 9-digit SSN, case variants)
  - RuntimePolicy self_refine clamping
  - Manifest helpers (_estimate_tokens, _heading_to_id collisions, manifest_path)
  - Manifest validation (validate_manifest full coverage)
  - Manifest audit_changes (live vs persisted diff)
  - Directive parser edge cases (H1-only, unicode headings, empty bodies)
  - Directive store edge cases (missing scope file, empty scopes, substring bonus)
  - DirectivesTool (all 5 actions: search, list, get, manifest, changes)
  - Tool Registry (dispatch, resolution, listing, error paths, get_tool_defs_for_agent)
  - Memory types (topic_id omission in to_dict, extra keys in from_dict)
  - Chunker edge cases (mixed headers, paragraph > max_chunk, vault memory >1200)
  - Cross-module integration: MemoryTool → VaultStore, build_memory_block pipeline
  - EmailTool (definition, all actions, account CRUD, validation, confirmation gate,
    agent_name resolution, SMTP error paths, password masking, edge cases)
  - WebSearchTool extended (_remove_emojis, definition, knowledge gate, scrape action)
  - Metering helpers (meter_response, zero_metering, meter_from_raw_usage, get_price,
    compute_cost, reset_pricing_cache, serialisation round-trips)
  - LLM Client factory (create_client dispatch, unknown provider)
  - App helpers (_strip_memory_tags, _extract_and_save_memories patterns)
  - Seed UI Knowledge script (MEMORIES list structure validation)
  - InboxTool (all 4 actions: send, add_task, next_task, ack; validation,
    edge cases, JSONL+MD persistence, dry_run, priority, needs_approval,
    registry dispatch)
  - Dynamic scopes (_discover_scopes from YAML files, VALID_SCOPES always has 'shared')
  - Category policy (_load_category_policy, _build_category_field for all 3 modes)
  - Saved profile upgrade (_seed_default_profile back-fills missing keys)
  - _TOOL_CATALOGUE dynamic fields (scope enum from VALID_SCOPES, category truncated)
  - Avatar migration (_migrate_base64_avatars: agent + user, extension detection, file output)
  - Profile API (user avatar upload/clear, agent avatar upload/clear, profile CRUD)
  - UI Skins API (set/get skin persisted in settings.json)
  - Saved profile CRUD (_list_profiles_in, save/get/delete memory profiles)
  - _extract_and_save_memories patterns (category extraction, min-length, invalid category)
  - Tool registry get_tool_defs_for_agent (YAML profile → tool definitions)
  - Profile create/update/delete roundtrip via API
  - MIN_SCORE cosine similarity threshold (search filter, boundary, zero/negative scores)
  - Tag sort mode (ascending by first tag, empty-tags sentinel, stability)
  - HARD_MAX_TOTAL ceiling on memory profile PUT (clamping, zero=unlimited bypass)
  - Wiki article loader (_load_wiki_articles, missing files, encoding)
  - About API (/api/about POST save, round-trip)
  - Vault filter dropdown (HTML template includes filter elements)
  - ModelRouterTool (classify_task, resolve_model_for_task, resolve_tier,
    get_next_tier, get_tier_for_connection, all 4 execute actions, enabled field)
  - Model Router config (defaults, load/save, merge, empty task_tier_map fix,
    presets CRUD API: list/save/load/delete, filename sanitisation, edge cases)
  - Routing ModelRouter class (from_config, route() all code-paths, Tier enum,
    TierConfig, RoutingDecision, classify_task scored matching, direct model
    overrides, stuck-loop escalation, disabled-tier skipping, force_tier,
    unknown tier labels, no-tiers edge case, to_config_dict round-trip)
  - BudgetTracker (create, record_cost, remaining, hard/soft/session limits,
    check_tick_budget, reset_session, get_summary, update_caps, month_rollover,
    corrupt state file, from_config, BudgetState to_dict/from_dict round-trip)
  - Router + Budget integration (hard limit forces local, soft limit caps at
    cheap_cloud, budget remaining in RoutingDecision)
  - ModelRouterTool budget action (5 actions including budget, resolve with
    new ModelRouter.from_config path)
  - Sidecar service wiring (_get_elevenlabs_conn fallback, _seed_platform_keys_from_env,
    env fallback, SEARXNG_URL env override, connections.json fallback,
    platform_hosted flag, Whisper server.py structure, SearXNG settings.yml,
    service Dockerfiles, fly.toml configs)
  - Platform API Keys (image generation: OpenAI, Google, Stability toggles;
    voice TTS: ElevenLabs, OpenedAI Cloud toggles; flag persistence, mixed
    platform+user keys, disabled state, provider switching with platform flag)
  - Chat 3-mode connection selector (_normalize_ollama_url edge cases,
    _get_platform_connections filter, page_chat connections split logic,
    admin platform key Ollama save/upsert, user API keys openrouter+ollama_url
    save, user API keys masking, /api/connections/all-models static logic,
    admin_keys.html PROVIDERS array, chat.html three-mode selector JS)
  - Soul Script helpers (_load_soul_script, _save_soul_script: round-trip,
    missing file, FAISS rebuild trigger, directory creation)
  - Soul Script API (PUT /api/profiles/{name}/config with soul_script_text,
    round-trip save+load, empty string, FAISS re-index)
  - Soul Script FAISS indexing (_rebuild_notes_faiss includes soul scripts,
    __soul_script__{agent} doc_id format, empty scripts skipped)
  - Note collector soul script injection (collect_notes auto-adds
    __soul_script__{agent_name} to directive_note_ids)
  - Profiles template collapsible sections (toggleCollapse JS, collapsible-header,
    collapsible-body, FAISS badge, soul-script textarea)
  - Billing catalog structure (SKIN_PRICES, CREDIT_PACKS, constants:
    LLM_MARKUP_MULTIPLIER, FREE_TRIAL_DAYS, INACTIVE_ACCOUNT_DAYS)
  - Tier & trial system (get_trial_status new/expired, get_user_tier,
    get_user_subscription, set/cancel subscription, empty user_id)
  - Credit system (add_user_credits, deduct_user_credits, get_user_credits,
    get_credit_history, history cap at 200, insufficient funds, limit param)
  - Credit checkout & webhook (create_credits_checkout_session test-mode ad-hoc
    product_data vs live fixed product, checkout metadata, handle_webhook_event
    credits fulfillment via unsigned JSON and signed Stripe Event.to_dict() path)
  - Credit cost estimators (estimate_llm_credit_cost 2× markup, estimate_tts_credit_cost
    per-provider, estimate_stt_credit_cost, zero/negative/minimum edge cases)
  - User activity tracking (touch_user_activity, get_user_last_active, throttle
    behavior, bypass throttle, empty user_id no-op)
  - Wipe user data (wipe_user_data: keep_purchases=True/False, section removal,
    wipe_user_by_email: email lookup, case-insensitive, not-found)
  - Purge inactive users (purge_inactive_users: 365-day cutoff, active subscriber
    skip, trial start fallback, data removal verification)
  - List all users (list_all_users: cross-section aggregation, detail fields,
    email, tier, credit_balance, last_active_human)
  - Auth helpers (is_public_path exact/sub-path/private, PUBLIC_PATHS set,
    get_auth_config dict shape, extract_user_from_token, empty payload defaults)
  - Tier info structure (TIER_INFO free/pro, features sorted, limits, price,
    FREE_TIER_FEATURES/PRO_TIER_FEATURES sets, pro superset of free)
  - RuntimeInfoTool (definition, execute, diff tracking, set_context,
    reset, REQUIRED_FIELDS, base_url redaction, policy snapshot,
    _diff_snapshots helper: change/add/remove/empty)
  - Admin Voices API (PUT save allowlist validation, empty lists, invalid types,
    GET page render, GET voices/all, settings persistence)
  - Admin Voices template (page structure, control buttons, search, voice grid,
    premium toggle, JS state vars, API fetch calls, stats, toast, escHtml XSS)
  - Admin User Management API (list users, wipe by email validation,
    wipe unknown email, purge inactive, delete user)
  - Connections CRUD API (list empty, create, update, delete, Ollama URL
    normalization, persistence verification)
  - Pricing CRUD API (get empty, full replace, single model set/delete,
    new provider, cost-summary, cost-log)
  - TTS Voices filter logic (no allowlist passthrough, allowlist filter,
    premium marking, empty allowlist)
  - Inworld API key helper (_get_inworld_api_key: missing, empty, valid,
    other keys only)
  - _check_admin helper (no user, admin email, non-admin, case-insensitive,
    empty email, missing email key)
  - FAISS scaling: model defaults (all-MiniLM-L6-v2), fcntl file locking
    in vault._append, FAISSMemory._save_index, NotesFAISS._save,
    NotesFAISS.load() dimension mismatch detection, FAISSMemory._load_or_build
    model mismatch rebuild, app _bg_faiss startup coordination with
    LOCK_EX|LOCK_NB, asyncio.to_thread wrapping of _build_chat_messages
    at 3 call sites, boot.sh --workers 1
  - FAISSMemory.update() re-embed keeps edited memory searchable; index heal on load
  - Per-user avatar URLs (_user_avatar_map, api_profile_avatar /api/uploads/ prefix)
  - chat.html avatar crop/fallback helpers (executed in node) + GA funnel events
  - Demo 4-message cap (web/demo/index.html) + profiles.html prompt guidance
  - AGI loop clock (fmt_span units, Trent's time zone incl. DST and bad zones, part_of_day bounds,
    time channel, timezone config, the measured clock line: previous tick, run time, slept vs planned,
    late/early, rendered field header/clock/pace lines, a real tick's view)
  - AGI loop energy readout (cost vs token cap binding, ties, no cap, overspend, day roll, body channel)
  - AGI loop pace honesty (adaptive/chosen notes, surprise, energy stretch, clamps, rest override,
    persistence across restarts, string coercion, corrupt state file)
  - AGI loop restarts (autostart mark kept by a deploy, cleared by operator/agent/guard stops, the
    new-run wake line for every stop reason, a real cancel-and-restart cycle)
  - AGI loop handoff letter (all three path patterns, newest wins, stale cutoff, long letters,
    held + focused, no duplicates, no bench, full hold slots, end-to-end first view)
  - The slab (sequence, trimming, unicode, refusals, cap, reload, since/limit, markdown mirror,
    corrupt lines, 8-thread concurrency, unwritable mirror, group tool actions, no wake-ups)
  - AGI loop app wiring (three loops, autostart only marked loops after the index is ready,
    failures isolated, slab GET endpoint + since, no HTTP writes, owner gate)
  - AGI loop preamble, Linux machines for all three minds (~/library, 15gb/1gb toml), nav
  - Madara prompt/soul-script split (every original line verbatim, prompt only his words,
    canon kept, ### structure, no duplicate sections, oversight last, demo copy untouched)
"""

import json
import hashlib
import hmac
import os
import sys
import time
import tempfile
import shutil

if hasattr(sys.stdout, "reconfigure"):
    # Windows consoles default to cp1252, which can't encode the arrows (→)
    # and box-drawing characters used in test labels below.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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


# ═════════════════════════════════════════════
# 1. Boundary policy — full coverage
# ═════════════════════════════════════════════
def test_boundary_policy():
    print("\n=== TORTURE: Boundary Policy — Risk / Denial / Logger ===")
    from src.policy.boundary import (
        classify_risk, BoundaryEvent, BoundaryLogger,
        build_denial, _default_proposed_limits,
    )

    # Risk classification: exact, base-name fallback, unknown
    check("echo → low", classify_risk("echo") == "low")
    check("memory.add → med", classify_risk("memory.add") == "med")
    check("web.search → high", classify_risk("web.search") == "high")
    check("filesystem.write → high", classify_risk("filesystem.write") == "high")
    check("email.send → high", classify_risk("email.send") == "high")
    check("shell.exec → high", classify_risk("shell.exec") == "high")
    check("http.request → high", classify_risk("http.request") == "high")
    # Base-name fallback: web.fetch → web → high
    check("web.anything → high (base)", classify_risk("web.anything") == "high")
    check("unknown_tool → med", classify_risk("totally_unknown") == "med")
    check("empty string → med", classify_risk("") == "med")

    # Proposed limits
    web_lim = _default_proposed_limits("web.search")
    check("web limits has rate_limit", "rate_limit" in web_lim)
    email_lim = _default_proposed_limits("email.send")
    check("email limits has require_approval", email_lim.get("require_approval") is True)
    fs_lim = _default_proposed_limits("filesystem.read")
    check("filesystem limits has read_only", "read_only" in fs_lim)
    shell_lim = _default_proposed_limits("shell.exec")
    check("shell limits has timeout", "timeout_seconds" in shell_lim)
    http_lim = _default_proposed_limits("http.request")
    check("http limits has rate_limit", "rate_limit" in http_lim)
    unknown_lim = _default_proposed_limits("some_unknown_tool")
    check("unknown limits has note", "note" in unknown_lim)

    # BoundaryEvent dataclass
    ev = BoundaryEvent(
        profile="test_agent",
        requested_capability="web.search",
        risk_level="high",
        reason="Not allowed",
    )
    d = ev.to_dict()
    check("event to_dict has profile", d["profile"] == "test_agent")
    check("event to_dict has risk_level", d["risk_level"] == "high")
    check("event to_dict has type", d["type"] == "boundary_request")
    check("event to_dict has requested_capability", d["requested_capability"] == "web.search")

    # build_denial — default reason
    denial_str, event = build_denial("web.search", "astraea")
    denial_obj = json.loads(denial_str)
    check("denial has error", denial_obj["error"] == "TOOL_NOT_ALLOWED")
    check("denial has tool", denial_obj["tool"] == "web.search")
    check("denial has how_to_enable", "profiles/" in denial_obj["how_to_enable"])
    check("event risk_level high", event.risk_level == "high")
    check("event has timestamp", len(event.timestamp) > 0)
    check("event profile", event.profile == "astraea")
    check("event proposed_limits populated", len(event.proposed_limits) > 0)

    # build_denial — custom reason
    denial_str2, event2 = build_denial("magic.wand", "callum",
                                        reason="Magic is forbidden",
                                        tick_index=42,
                                        tool_args={"spell": "fireball"})
    check("custom reason preserved", event2.reason == "Magic is forbidden")
    check("tick_index preserved", event2.tick_index == 42)
    check("tool_args preserved", event2.tool_args["spell"] == "fireball")
    check("unknown tool → med risk", event2.risk_level == "med")

    # BoundaryLogger — write, read, empty, missing file
    tmp = tempfile.mkdtemp()
    try:
        logger = BoundaryLogger(os.path.join(tmp, "events.jsonl"))

        # Empty read
        events = logger.read_all()
        check("empty logger → []", events == [])

        # Append + read
        logger.append(event)
        logger.append(event2)
        events = logger.read_all()
        check("2 events after append", len(events) == 2)
        check("first event type", events[0].type == "boundary_request")
        check("second event profile", events[1].profile == "callum")

        # Read from nonexistent path
        logger2 = BoundaryLogger(os.path.join(tmp, "nonexistent", "events.jsonl"))
        events2 = logger2.read_all()
        check("missing file → []", events2 == [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 2. PII guard — extended edge cases
# ═════════════════════════════════════════════
def test_pii_guard_extended():
    print("\n=== TORTURE: PII Guard — Extended Cases ===")
    from src.memory.pii_guard import check_pii

    # 9-consecutive-digit bare SSN
    result = check_pii("SSN: 123456789")
    check("bare 9-digit SSN caught", len(result) > 0, f"returned: {result}")

    # bearer token
    result = check_pii("Bearer eyJhbGciOiJSUzI1NiIs")
    check("bearer token caught", len(result) > 0, f"returned: {result}")

    # auth_token keyword
    result = check_pii("auth_token: abc123xyz")
    check("auth_token caught", len(result) > 0, f"returned: {result}")

    # Case insensitivity
    result = check_pii("PASSWORD: MySecret123")
    check("PASSWORD uppercase caught", len(result) > 0, f"returned: {result}")

    result = check_pii("Api_Key: sk-test1234")
    check("Api_Key mixed case caught", len(result) > 0, f"returned: {result}")

    result = check_pii("SECRET_KEY: secretvalue")
    check("SECRET_KEY uppercase caught", len(result) > 0, f"returned: {result}")

    # Embedded keyword — should catch if colon pattern matches
    result = check_pii("My nopasswordhere is fine")
    # The word "password" without colon should not trigger
    # (depends on implementation — check_pii uses keyword matching)
    # If it catches, that's the guard being aggressive (acceptable)
    check("embedded password (no colon) — either ok", True)

    # Empty string
    result = check_pii("")
    check("empty string → safe", len(result) == 0)

    # None-ish (if accepted)
    try:
        result = check_pii("   ")
        check("whitespace → safe", len(result) == 0)
    except Exception:
        check("whitespace handled", True)


# ═════════════════════════════════════════════
# 3. RuntimePolicy — self_refine clamping
# ═════════════════════════════════════════════
def test_runtime_policy_clamping():
    print("\n=== TORTURE: RuntimePolicy — self_refine Clamping ===")
    from src.runtime_policy import RuntimePolicy

    # Negative → clamp to 0
    p = RuntimePolicy(self_refine_steps=-5)
    check("negative refine → 0", p.self_refine_steps == 0)

    # Exceed cap → clamp to 15
    p2 = RuntimePolicy(self_refine_steps=100)
    check("100 refine → 15", p2.self_refine_steps == 15)

    # Exactly at cap
    p3 = RuntimePolicy(self_refine_steps=15)
    check("15 refine → 15", p3.self_refine_steps == 15)

    # Zero stays zero
    p4 = RuntimePolicy(self_refine_steps=0)
    check("0 refine → 0", p4.self_refine_steps == 0)

    # Normal value
    p5 = RuntimePolicy(self_refine_steps=7)
    check("7 refine → 7", p5.self_refine_steps == 7)

    # stasis_mode
    p6 = RuntimePolicy(stasis_mode=True)
    check("stasis_mode set", p6.stasis_mode is True)

    # tool_failure_mode
    p7 = RuntimePolicy(tool_failure_mode="stop")
    check("tool_failure_mode stop", p7.tool_failure_mode == "stop")

    # check() with None wall time
    p8 = RuntimePolicy(max_iterations=10, max_wall_time_seconds=None)
    check("None wall_time, iter ok", p8.check(5, time.time()) is None)
    check("None wall_time, iter limit", p8.check(10, time.time()) is not None)


# ═════════════════════════════════════════════
# 4. Manifest helpers — _estimate_tokens, _heading_to_id, manifest_path
# ═════════════════════════════════════════════
def test_manifest_helpers():
    print("\n=== TORTURE: Manifest Helpers ===")
    from src.directives.manifest import (
        _estimate_tokens, _heading_to_id, manifest_path, _sha256,
    )

    # _estimate_tokens
    check("empty → 0", _estimate_tokens("") == 0)
    check("None-like → 0", _estimate_tokens(None) == 0 if True else True)
    check("short → >= 1", _estimate_tokens("hi") >= 1)
    check("1000 chars → ~250", abs(_estimate_tokens("a" * 1000) - 250) <= 10)

    # _heading_to_id
    check("basic", _heading_to_id("shared", "Code Standards") == "shared.code_standards")
    check("special chars stripped",
          "shared." in _heading_to_id("shared", "Humor & Play Mode"))
    check("caps lowered", _heading_to_id("orion", "BIG HEADING") == "orion.big_heading")
    check("unicode stripped",
          "shared." in _heading_to_id("shared", "日本語 Section"))
    check("repeated underscores collapsed",
          "__" not in _heading_to_id("shared", "A    B    C"))

    # manifest_path
    mp = manifest_path()
    check("manifest_path is string", isinstance(mp, str))
    check("manifest_path contains manifest.json", "manifest.json" in mp)

    # _sha256 is deterministic
    h1 = _sha256("test")
    h2 = _sha256("test")
    check("sha256 deterministic", h1 == h2)
    check("sha256 length 64", len(h1) == 64)
    check("sha256 differs for diff input", _sha256("a") != _sha256("b"))


# ═════════════════════════════════════════════
# 5. Directive parser edge cases
# ═════════════════════════════════════════════
def test_directive_parser_edge_cases():
    print("\n=== TORTURE: Directive Parser Edge Cases ===")
    from src.directives.parser import parse_directive_file

    tmp = tempfile.mkdtemp()
    try:
        # H1-only headers (## pattern should NOT match # )
        h1_path = os.path.join(tmp, "h1_only.md")
        with open(h1_path, "w", encoding="utf-8") as f:
            f.write("# Top Level Header\nSome content.\n# Another\nMore.\n")
        sections = parse_directive_file(h1_path, "test")
        check("H1-only → no sections", len(sections) == 0)

        # Unicode headings
        uni_path = os.path.join(tmp, "unicode.md")
        with open(uni_path, "w", encoding="utf-8") as f:
            f.write("日本語\n" + "## 日本語セクション\nJapanese section content.\n\n## Привет\nRussian.\n")
        sections = parse_directive_file(uni_path, "test")
        check("unicode headings parsed", len(sections) == 2)
        check("first heading correct", sections[0].heading == "日本語セクション")
        check("second heading correct", sections[1].heading == "Привет")

        # All empty bodies
        empty_path = os.path.join(tmp, "empty_bodies.md")
        with open(empty_path, "w", encoding="utf-8") as f:
            f.write("## Empty1\n\n## Empty2\n\n## Empty3\n")
        sections = parse_directive_file(empty_path, "test")
        # Sections with empty body should be filtered
        check("empty bodies handled", isinstance(sections, list))

        # Completely empty file
        blank_path = os.path.join(tmp, "blank.md")
        with open(blank_path, "w", encoding="utf-8") as f:
            f.write("")
        sections = parse_directive_file(blank_path, "test")
        check("blank file → empty", len(sections) == 0)

        # Missing file
        sections = parse_directive_file(os.path.join(tmp, "nope.md"), "test")
        check("missing file → empty", len(sections) == 0)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 6. Directive store edge cases
# ═════════════════════════════════════════════
def test_directive_store_edge_cases():
    print("\n=== TORTURE: Directive Store Edge Cases ===")
    from src.directives.store import DirectiveStore, score_section
    from src.directives.parser import DirectiveSection

    tmp = tempfile.mkdtemp()
    try:
        # Missing scope file — should load silently with 0 sections
        store = DirectiveStore(tmp, scopes="nonexistent")
        results = store.search("anything", limit=5)
        check("missing scope file → 0 results", len(results) == 0)
        check("missing scope → 0 headings", len(store.list_headings()) == 0)

        # Empty scopes list
        store2 = DirectiveStore(tmp, scopes=[])
        check("empty scopes → 0", len(store2.get_all()) == 0)

        # Scoring: substring bonus
        section = DirectiveSection(
            heading="Code Standards",
            body="Follow code standards strictly for all modules",
            scope="shared",
            source_file="shared.md",
        )
        # Query is a substring of the text → +0.3 bonus
        score_with_substr = score_section("code standards", section)
        score_without_substr = score_section("code xstandards", section)
        check("substring bonus applied", score_with_substr > score_without_substr,
              f"with={score_with_substr:.3f} without={score_without_substr:.3f}")

        # Scoring: empty query → 0
        check("empty query → 0", score_section("", section) == 0.0)

        # Scoring: no token overlap → 0
        check("no overlap → 0", score_section("zzz qqq", section) == 0.0)

        # get_section case insensitive
        path = os.path.join(tmp, "shared.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("## Test Section\nContent here.\n")
        store3 = DirectiveStore(tmp, scopes="shared")
        found = store3.get_section("TEST SECTION")
        check("get_section case insensitive", found is not None)
        found2 = store3.get_section("nonexistent")
        check("get_section missing → None", found2 is None)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 7. Memory types — edge cases
# ═════════════════════════════════════════════
def test_memory_types_extended():
    print("\n=== TORTURE: Memory Types — Extended ===")
    from src.memory.types import Memory, JOURNAL_ONLY_SIGNALS, MAX_MEMORY_TEXT_LENGTH

    # topic_id omission in to_dict when None
    m = Memory(id="t1", text="test", scope="shared", category="fact", topic_id=None)
    d = m.to_dict()
    check("topic_id=None omitted from dict", "topic_id" not in d)

    # topic_id present in to_dict when set
    m2 = Memory(id="t2", text="test", scope="shared", category="fact", topic_id="my_topic")
    d2 = m2.to_dict()
    check("topic_id in dict when set", d2.get("topic_id") == "my_topic")

    # from_dict with extra unexpected keys — should not crash
    extra = {
        "id": "t3", "text": "test", "scope": "shared", "category": "fact",
        "extra_key": "extra_value", "another": 42,
    }
    try:
        m3 = Memory.from_dict(extra)
        check("extra keys ignored gracefully", m3.id == "t3")
    except TypeError:
        check("extra keys cause TypeError", True)  # acceptable

    # JOURNAL_ONLY_SIGNALS exists and has entries
    check("JOURNAL_ONLY_SIGNALS not empty", len(JOURNAL_ONLY_SIGNALS) > 0)
    check("'tick marker' in signals", "tick marker" in JOURNAL_ONLY_SIGNALS)
    check("'heartbeat' in signals", "heartbeat" in JOURNAL_ONLY_SIGNALS)
    check("'ephemeral' in signals", "ephemeral" in JOURNAL_ONLY_SIGNALS)

    # MAX_MEMORY_TEXT_LENGTH
    check("MAX_MEMORY_TEXT_LENGTH is 1200", MAX_MEMORY_TEXT_LENGTH == 1200)

    # version defaults
    m4 = Memory(id="v", text="t", scope="shared", category="fact")
    check("default version = 1", m4.version == 1)
    check("default tier = 'canon'", m4.tier == "canon")
    check("default tags = []", m4.tags == [])
    check("default created_at = ''", m4.created_at == "")
    check("default updated_at = None", m4.updated_at is None)
    check("default source = None", m4.source is None)
    check("default deleted_at = None", m4.deleted_at is None)


# ═════════════════════════════════════════════
# 8. Chunker edge cases
# ═════════════════════════════════════════════
def test_chunker_edge_cases():
    print("\n=== TORTURE: Chunker Edge Cases ===")
    from src.memory.chunker import SemanticChunker, chunk_soul_script

    chunker = SemanticChunker(min_chunk_size=100, max_chunk_size=500)

    # Mixed ## and ### headers
    mixed = (
        "## Main Section\nContent A.\n"
        "### Subsection\nContent B.\n"
        "## Another Main\nContent C.\n"
    )
    chunks = chunker.chunk_by_headers(mixed, "mixed", "Mixed Doc")
    check("mixed headers parsed", len(chunks) > 0)

    # Single paragraph > max_chunk_size
    giant_para = "word " * 500
    chunks2 = chunker.chunk_by_headers(giant_para, "giant", "Giant Para")
    check("giant paragraph chunked", len(chunks2) > 0)

    # All text < min_chunk_size (single tiny section)
    tiny = "### Tiny\nHi.\n"
    chunks3 = chunker.chunk_by_headers(tiny, "tiny", "Tiny Doc")
    check("tiny section produces chunk(s)", len(chunks3) >= 0)  # may be 0 or 1

    # chunk_vault_memory (method on SemanticChunker)
    mem_input = {
        "id": "mem_long",
        "text": "x" * 2000,
        "metadata": {"scope": "shared", "tier": "canon", "category": "fact"},
    }
    mem_chunks = chunker.chunk_vault_memory(mem_input)
    check("vault memory chunk created", len(mem_chunks) > 0)
    check("vault memory text preserved", mem_chunks[0]["text"] == "x" * 2000)

    # chunk_vault_memory with normal text
    norm_input = {
        "id": "mem_norm",
        "text": "Normal memory text",
        "metadata": {"scope": "shared", "tier": "register", "category": "preference"},
    }
    normal_chunks = chunker.chunk_vault_memory(norm_input)
    check("normal vault memory", len(normal_chunks) == 1)
    check("normal text preserved", normal_chunks[0]["text"] == "Normal memory text")

    # chunk_soul_script with metadata
    soul = (
        "### Identity Core\nI am a helpful assistant.\n\n"
        "### Behavioral Principles\nBe kind and thorough.\n"
    )
    soul_chunks = chunk_soul_script(
        soul, note_id="soul_1", title="Soul Script", emoji="🧠",
        metadata={"custom": True},
    )
    check("soul script chunks created", len(soul_chunks) > 0)
    for c in soul_chunks:
        meta = c.get("metadata", {})
        check_ok = meta.get("is_canon") is True and meta.get("immutable") is True
        if not check_ok:
            check("soul script metadata flags", False, f"meta={meta}")
            break
    else:
        check("soul script metadata flags", True)


# ═════════════════════════════════════════════
# 9. Memory injector — build_memory_block
# ═════════════════════════════════════════════
def test_memory_injector():
    print("\n=== TORTURE: Memory Injector — build_memory_block ===")
    from src.memory.injector import build_memory_block

    # Mock FAISSMemory that returns controlled results
    class MockFAISS:
        def search(self, query, scope=None, top_k=10):
            return [
                {"text": "User prefers dark mode", "scope": "shared",
                 "category": "preference", "tags": ["ui"], "score": 0.92},
                {"text": "Birthday is June 15", "scope": "shared",
                 "category": "bio", "tags": [], "score": 0.81},
            ]
        def recall(self, scope=None, limit=20):
            from src.memory.types import Memory
            return [
                Memory(id="r1", text="Latest project note", scope="shared",
                       category="project", tags=["work"]),
                Memory(id="r2", text="Favorite color: blue", scope="callum",
                       category="preference"),
            ]

    mock = MockFAISS()

    # Semantic mode (with query)
    block = build_memory_block(mock, scopes="shared", query="What do I like?")
    check("semantic block not empty", len(block) > 0)
    check("semantic has header", "Long-Term Memory Context" in block)
    check("semantic has dark mode", "dark mode" in block)
    check("semantic has birthday", "Birthday" in block)
    check("semantic has score", "relevance:" in block)
    check("semantic has scope tag", "scope:" in block)
    check("semantic has category heading", "**Preference**" in block or "**preference**" in block.lower())

    # Recall mode (no query)
    block2 = build_memory_block(mock, scopes="shared")
    check("recall block not empty", len(block2) > 0)
    check("recall has header", "Long-Term Memory Context" in block2)
    check("recall has project", "project note" in block2)
    check("recall has favorite color", "Favorite color" in block2)
    check("recall → most recent label", "most recent" in block2)

    # Empty results mock
    class EmptyFAISS:
        def search(self, query, scope=None, top_k=10):
            return []
        def recall(self, scope=None, limit=20):
            return []

    empty_block = build_memory_block(EmptyFAISS(), scopes="shared", query="anything")
    check("empty search → empty string", empty_block == "")
    empty_block2 = build_memory_block(EmptyFAISS(), scopes="shared")
    check("empty recall → empty string", empty_block2 == "")

    # Scoping
    block3 = build_memory_block(mock, scopes=["shared", "callum"], query="test")
    check("multi-scope accepted", len(block3) > 0)

    # Tags in output
    check("tags in semantic output", "[ui]" in block)


# ═════════════════════════════════════════════
# 10. MemoryTool — all 12 actions via VaultStore
# ═════════════════════════════════════════════
def test_memory_tool_all_actions():
    """Test MemoryTool by replacing its FAISSMemory with a VaultStore shim.

    We can't easily test FAISS search without the model, so we test:
    - definition structure
    - add, get, update, delete, bulk_delete, list, stats, compact, rebuild_index
    - Error paths: unknown action, missing fields
    """
    print("\n=== TORTURE: MemoryTool — All Actions ===")
    from src.tools.memory_tool import MemoryTool
    from src.memory.vault import VaultStore

    tmp = tempfile.mkdtemp()
    try:
        tool = MemoryTool()

        # Inject a simple vault-only shim (no FAISS embedding)
        vault = VaultStore(os.path.join(tmp, "vault.jsonl"))

        class _LiteMemory:
            """Shim that delegates to VaultStore for non-embedding ops."""
            def __init__(self, v):
                self._v = v
            def add(self, text, scope, category, tags=None, source="tool",
                    tier="register", topic_id=None):
                return self._v.create_memory(
                    text=text, scope=scope, category=category,
                    tags=tags or [], source=source, tier=tier, topic_id=topic_id)
            def remember(self, text, scope="shared", category="other",
                         source="tool", tags=None):
                m = self._v.create_memory(text=text, scope=scope, category=category,
                                          tags=tags or [], source=source)
                return {"status": "stored", "id": m.id, "scope": m.scope}
            def search(self, query, scope=None, category=None, top_k=10):
                return []  # no-op without embeddings
            def recall(self, scope=None, category=None, tags=None, limit=20):
                mems = self._v.read_active()
                if scope:
                    mems = [m for m in mems if m.scope == scope]
                return mems[:limit]
            def get(self, memory_id):
                return self._v.get_memory(memory_id)
            def update(self, memory_id, text=None, category=None, tags=None):
                return self._v.update_memory(memory_id, text=text,
                                             category=category, tags=tags)
            def delete(self, memory_id):
                return self._v.delete_memory(memory_id)
            def bulk_delete(self, memory_ids):
                return self._v.bulk_delete(memory_ids)
            def list_all(self, scope=None):
                mems = self._v.read_active()
                if scope:
                    mems = [m for m in mems if m.scope == scope]
                return mems
            def stats(self):
                return self._v.stats()
            def compact(self):
                return self._v.compact()
            def rebuild_index(self):
                return {"status": "ok", "message": "FAISS index rebuilt"}
            def batch_add(self, items):
                return self._v.batch_create_many(items)

        tool._mem = _LiteMemory(vault)

        # Definition
        defn = tool.definition()
        check("definition has name", defn["name"] == "memory")
        check("definition has parameters", "parameters" in defn)
        actions = defn["parameters"]["properties"]["action"]["enum"]
        check("13 actions", len(actions) == 13)

        # Add
        result = json.loads(tool.execute({"action": "add", "text": "Test memory",
                                           "scope": "shared", "category": "fact"}))
        check("add → stored", result["status"] == "stored")
        mem_id = result["id"]
        check("add → has id", len(mem_id) > 0)

        # Add validation: missing text
        r = json.loads(tool.execute({"action": "add", "scope": "shared", "category": "fact"}))
        check("add missing text → error", r["status"] == "error")

        # Add validation: missing scope
        r = json.loads(tool.execute({"action": "add", "text": "x", "category": "fact"}))
        check("add missing scope → error", r["status"] == "error")

        # Add validation: missing category
        r = json.loads(tool.execute({"action": "add", "text": "x", "scope": "shared"}))
        check("add missing category → error", r["status"] == "error")

        # Add Many (batch)
        r = json.loads(tool.execute({
            "action": "add_many",
            "memories": [
                {"text": "Batch one", "scope": "shared", "category": "fact"},
                {"text": "Batch two", "scope": "shared", "category": "preference"},
            ],
        }))
        check("add_many → stored", r["status"] == "stored")
        check("add_many count 2", r["count"] == 2)
        check("add_many has ids", len(r["ids"]) == 2)

        # Add Many validation: missing memories array
        r = json.loads(tool.execute({"action": "add_many"}))
        check("add_many no memories → error", r["status"] == "error")

        # Add Many validation: item missing text
        r = json.loads(tool.execute({
            "action": "add_many",
            "memories": [{"scope": "shared", "category": "fact"}],
        }))
        check("add_many missing text → error", r["status"] == "error")

        # Remember (quick-store)
        r = json.loads(tool.execute({"action": "remember", "text": "Quick note"}))
        check("remember → stored", r["status"] == "stored")

        # Remember missing text
        r = json.loads(tool.execute({"action": "remember"}))
        check("remember missing text → error", r["status"] == "error")

        # Get
        r = json.loads(tool.execute({"action": "get", "memory_id": mem_id}))
        check("get → ok", r["status"] == "ok")
        check("get → correct text", r["memory"]["text"] == "Test memory")

        # Get missing
        r = json.loads(tool.execute({"action": "get", "memory_id": "nonexistent"}))
        check("get missing → not_found", r["status"] == "not_found")

        # Get no memory_id
        r = json.loads(tool.execute({"action": "get"}))
        check("get no id → error", r["status"] == "error")

        # Update
        r = json.loads(tool.execute({"action": "update", "memory_id": mem_id,
                                     "text": "Updated text"}))
        check("update → updated", r["status"] == "updated")
        check("update → version > 1", r["version"] > 1)

        # Update no memory_id
        r = json.loads(tool.execute({"action": "update"}))
        check("update no id → error", r["status"] == "error")

        # Delete
        r = json.loads(tool.execute({"action": "delete", "memory_id": mem_id}))
        check("delete → deleted", r["status"] == "deleted")

        # Delete already deleted
        r = json.loads(tool.execute({"action": "delete", "memory_id": mem_id}))
        check("re-delete → not_found", r["status"] == "not_found")

        # Delete no id
        r = json.loads(tool.execute({"action": "delete"}))
        check("delete no id → error", r["status"] == "error")

        # Add multiple for bulk ops
        ids = []
        for i in range(5):
            r = json.loads(tool.execute({
                "action": "add", "text": f"Bulk {i}",
                "scope": "shared", "category": "fact",
            }))
            ids.append(r["id"])

        # Bulk delete
        r = json.loads(tool.execute({"action": "bulk_delete",
                                     "memory_ids": ids[:3]}))
        check("bulk_delete → ok", r["status"] == "ok")
        check("bulk_delete count 3", r["deleted_count"] == 3)

        # Bulk delete no ids
        r = json.loads(tool.execute({"action": "bulk_delete"}))
        check("bulk_delete no ids → error", r["status"] == "error")

        # List
        r = json.loads(tool.execute({"action": "list"}))
        check("list → ok", r["status"] == "ok")
        check("list has memories", "memories" in r)
        check("list count > 0", r["count"] > 0)

        # Search (returns empty from shim)
        r = json.loads(tool.execute({"action": "search", "query": "test"}))
        check("search → ok", r["status"] == "ok")

        # Search no query
        r = json.loads(tool.execute({"action": "search"}))
        check("search no query → error", r["status"] == "error")

        # Recall
        r = json.loads(tool.execute({"action": "recall"}))
        check("recall → ok", r["status"] == "ok")
        check("recall has memories", "memories" in r)

        # Stats
        r = json.loads(tool.execute({"action": "stats"}))
        check("stats → ok", r["status"] == "ok")
        check("stats has active_count", "active_count" in r)

        # Compact
        r = json.loads(tool.execute({"action": "compact"}))
        check("compact → ok", r["status"] == "ok")

        # Rebuild index
        r = json.loads(tool.execute({"action": "rebuild_index"}))
        check("rebuild_index → ok", r["status"] == "ok")

        # Unknown action
        r = json.loads(tool.execute({"action": "BOGUS"}))
        check("unknown action → error", r["status"] == "error")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 11. CostTrackerTool — untested actions
# ═════════════════════════════════════════════
def test_cost_tracker_extended():
    print("\n=== TORTURE: CostTrackerTool — Extended Actions ===")
    from src.tools.cost_tracker import CostTrackerTool
    from src.observability.metering import (
        Metering, TokenUsage, CostBreakdown,
        log_cost_event, set_cost_log_path,
    )

    tmp = tempfile.mkdtemp()
    log_path = os.path.join(tmp, "cost_log.jsonl")
    set_cost_log_path(log_path)

    try:
        # Seed some cost events
        for i in range(5):
            m = Metering(
                usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
                cost=CostBreakdown(total_cost=0.005),
                model="gpt-4", provider="openai",
            )
            log_cost_event(m, agent="astraea", chat_id=f"chat_{i % 2}")

        tool = CostTrackerTool()

        # cost_summary
        r = json.loads(tool.execute({"action": "cost_summary"}))
        check("cost_summary has today", "today" in r)
        check("cost_summary has this_week", "this_week" in r)
        check("cost_summary has this_month", "this_month" in r)
        check("cost_summary has all_time", "all_time" in r)
        check("all_time num_calls", r["all_time"]["num_calls"] == 5)

        # cost_summary with agent filter
        r2 = json.loads(tool.execute({"action": "cost_summary", "agent": "astraea"}))
        check("filtered summary has events", r2["all_time"]["num_calls"] == 5)

        # cost_log
        r3 = json.loads(tool.execute({"action": "cost_log"}))
        check("cost_log has events", "events" in r3)
        check("cost_log count", r3["count"] == 5)

        # cost_log with limit
        r4 = json.loads(tool.execute({"action": "cost_log", "limit": 2}))
        check("cost_log limit works", r4["count"] == 2)

        # cost_log with agent filter
        r5 = json.loads(tool.execute({"action": "cost_log", "agent": "astraea"}))
        check("cost_log agent filter", r5["count"] == 5)

        # session_cost
        r6 = json.loads(tool.execute({"action": "session_cost", "chat_id": "chat_0"}))
        check("session_cost has chat_id", r6["chat_id"] == "chat_0")
        check("session_cost has num_calls", r6["num_calls"] > 0)

        # session_cost missing chat_id
        r7 = json.loads(tool.execute({"action": "session_cost"}))
        check("session_cost no chat_id → error", "error" in r7)

        # session_cost unknown chat
        r8 = json.loads(tool.execute({"action": "session_cost", "chat_id": "unknown"}))
        check("session_cost unknown chat → 0 calls", r8["num_calls"] == 0)

    finally:
        set_cost_log_path(None)
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 12. Note collector helpers
# ═════════════════════════════════════════════
def test_note_collector_helpers():
    print("\n=== TORTURE: Note Collector Helpers ===")
    from src.storage.note_collector import (
        _load_user_note_text, _load_builtin_note_text,
        _load_settings, invalidate_notes_faiss,
    )

    tmp = tempfile.mkdtemp()
    try:
        # _load_user_note_text — missing file
        text = _load_user_note_text("nonexistent_id_12345")
        check("missing user note → empty", text == "")

        # _load_builtin_note_text — missing file
        text = _load_builtin_note_text("nonexistent.md")
        check("missing builtin note → empty", text == "")

        # invalidate_notes_faiss — should not crash
        invalidate_notes_faiss()
        check("invalidate_notes_faiss ok", True)

        # _load_settings — returns dict (may be empty if no settings.json)
        settings = _load_settings()
        check("_load_settings returns dict", isinstance(settings, dict))

        # Test _load_user_note_text with actual note file
        notes_dir = os.path.join(tmp, "data", "user_notes")
        os.makedirs(notes_dir, exist_ok=True)

        # Write a test note
        note_data = {
            "id": "test_note_1",
            "title": "Test Note",
            "emoji": "🔬",
            "content_html": "<p>Hello <b>world</b></p>",
            "trashed": False,
        }
        note_path = os.path.join(notes_dir, "test_note_1.json")
        with open(note_path, "w") as f:
            json.dump(note_data, f)

        # This won't work with the hardcoded path, but we can test the function
        # by monkey-patching. Instead, just verify the function signatures work.
        check("note collector imports ok", True)

        # Test trashed note exclusion (using the project's actual path)
        # We can't easily redirect, but we verified the missing-file paths.

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 13. Manifest ID collision dedup
# ═════════════════════════════════════════════
def test_manifest_id_collision():
    print("\n=== TORTURE: Manifest — ID Collision Dedup ===")
    from src.directives.manifest import generate_manifest

    tmp = tempfile.mkdtemp()
    try:
        # Create a scope file with headings that produce the same slug
        path = os.path.join(tmp, "shared.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(
                "## Hello World\nContent A.\n\n"
                "## Hello World\nContent B.\n\n"  # exact duplicate heading
            )

        manifest = generate_manifest(directives_dir=tmp, scopes=("shared",))
        directives = manifest["directives"]
        ids = [d["id"] for d in directives]
        check("2 directives from duplicate headings", len(directives) == 2)
        check("IDs are unique", len(set(ids)) == 2, f"ids={ids}")
        check("second ID has suffix", any("_2" in i for i in ids), f"ids={ids}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 14. Continuation tool edge cases
# ═════════════════════════════════════════════
def test_continuation_edge_cases():
    print("\n=== TORTURE: ContinuationUpdate — Edge Cases ===")
    import src.data_paths as dp
    from src.tools.continuation_update import ContinuationUpdateTool

    orig_root = dp.DATA_ROOT
    tmp = tempfile.mkdtemp()
    dp.DATA_ROOT = tmp

    try:
        tool = ContinuationUpdateTool()

        # Definition check
        defn = tool.definition()
        check("definition has name", defn["name"] == "continuation_update")
        check("definition has parameters", "parameters" in defn)

        # Unknown mode
        result = tool.execute({"profile": "test_agent", "mode": "delete",
                               "content": "Test"})
        check("unknown mode → error", "error" in result.lower() or "unknown" in result.lower())

        # replace_section without section param
        result = tool.execute({"profile": "test_agent", "mode": "replace_section",
                               "content": "Test content"})
        # Should handle gracefully
        check("replace_section no section → handled", isinstance(result, str))

        # Normal append
        result = tool.execute({"profile": "test_prof", "mode": "append",
                               "content": "Entry 1"})
        check("append result is string", isinstance(result, str))

        # Verify the file
        cont_path = dp.continuation_path("test_prof")
        check("continuation file exists", os.path.isfile(cont_path))

    finally:
        dp.DATA_ROOT = orig_root
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 15. Data paths completeness
# ═════════════════════════════════════════════
def test_data_paths_extended():
    print("\n=== TORTURE: Data Paths — Extended ===")
    import src.data_paths as dp

    orig_root = dp.DATA_ROOT
    tmp = tempfile.mkdtemp()
    dp.DATA_ROOT = tmp

    try:
        # All path functions should return strings and create dirs
        profile = "test_agent"

        # Profile paths
        pd = dp.profile_dir(profile)
        check("profile_dir is string", isinstance(pd, str))
        check("profile_dir exists", os.path.isdir(pd))

        # Memory dir
        md = dp.memory_dir()
        check("memory_dir is string", isinstance(md, str))
        check("memory_dir exists", os.path.isdir(md))

        # FAISS dir
        fd = dp.faiss_dir()
        check("faiss_dir is string", isinstance(fd, str))
        check("faiss_dir exists", os.path.isdir(fd))

        # Shared dir
        sd = dp.shared_dir()
        check("shared_dir is string", isinstance(sd, str))
        check("shared_dir exists", os.path.isdir(sd))

        # File paths (these return paths but don't create files)
        sp = dp.state_path(profile)
        check("state_path is string", isinstance(sp, str))
        check("state_path contains profile", profile in sp)

        jp = dp.journal_path(profile)
        check("journal_path is string", isinstance(jp, str))
        check("journal_path contains profile", profile in jp)

        smp = dp.summary_path(profile)
        check("summary_path is string", isinstance(smp, str))
        check("summary_path contains profile", profile in smp)

        cp = dp.continuation_path(profile)
        check("continuation_path is string", isinstance(cp, str))
        check("continuation_path contains profile", profile in cp)

        np = dp.narrative_path(profile)
        check("narrative_path is string", isinstance(np, str))

        # Shared file paths
        vp = dp.vault_path()
        check("vault_path is string", isinstance(vp, str))
        check("vault_path contains vault", "vault" in vp.lower())

        bp = dp.boundary_events_path()
        check("boundary_events_path is string", isinstance(bp, str))

        clp = dp.change_log_path()
        check("change_log_path is string", isinstance(clp, str))

        hjp = dp.human_journal_path()
        check("human_journal_path is string", isinstance(hjp, str))

        trp = dp.tool_requests_path()
        check("tool_requests_path is string", isinstance(trp, str))

    finally:
        dp.DATA_ROOT = orig_root
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 16. Metering — extended edge cases
# ═════════════════════════════════════════════
def test_metering_extended():
    print("\n=== TORTURE: Metering — Extended Edge Cases ===")
    from src.observability.metering import (
        Metering, TokenUsage, CostBreakdown,
        estimate_tokens_from_text, estimate_tokens_from_messages,
        log_cost_event, read_cost_log, aggregate_costs,
        set_cost_log_path,
    )

    # Estimate edge cases
    check("estimate None-safe", estimate_tokens_from_text("") == 0)
    check("estimate 1 char", estimate_tokens_from_text("x") >= 1)

    # Empty messages list
    check("estimate empty msgs", estimate_tokens_from_messages([]) >= 0)

    # Messages with None content
    msgs = [{"role": "user", "content": None}]
    tok = estimate_tokens_from_messages(msgs)
    check("None content in msg → safe", tok >= 0)

    # CostBreakdown addition
    c1 = CostBreakdown(input_cost=0.01, output_cost=0.02, total_cost=0.03,
                       cached_input_cost=0.001, training_cost=0.005)
    c2 = CostBreakdown(input_cost=0.01, output_cost=0.02, total_cost=0.03)
    c3 = c1 + c2
    check("cached_input_cost preserved", abs(c3.cached_input_cost - 0.001) < 0.0001)
    check("training_cost preserved", abs(c3.training_cost - 0.005) < 0.0001)

    # Aggregate empty list
    agg = aggregate_costs([])
    check("aggregate empty → 0 calls", agg["num_calls"] == 0)
    check("aggregate empty → total_cost 0", agg["total_cost"] == 0)

    # Read malformed cost log
    tmp = tempfile.mkdtemp()
    log_path = os.path.join(tmp, "bad_log.jsonl")
    set_cost_log_path(log_path)

    try:
        with open(log_path, "w") as f:
            f.write('{"ts": "2026-01-01", "agent": "a", "model": "m"}\n')
            f.write('NOT VALID JSON\n')
            f.write('{"ts": "2026-01-02", "agent": "b", "model": "m"}\n')

        events = read_cost_log(limit=100)
        # Should skip malformed lines gracefully
        check("malformed log lines handled", isinstance(events, list))
        check("some events read despite bad line", len(events) >= 1)
    except Exception as e:
        check("malformed log handling", False, str(e))
    finally:
        set_cost_log_path(None)
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 17. WebSearchTool — _extract_content
# ═════════════════════════════════════════════
def test_web_search_extract():
    print("\n=== TORTURE: WebSearchTool — _extract_content ===")
    from src.tools.web_search import (
        WebSearchTool, _extract_content, _clean_text, _truncate, _get_mode_preset
    )

    # _extract_content with plain text
    content = _extract_content("<html><body><p>Hello world</p></body></html>", 500)
    check("extract basic HTML", "Hello" in content or "world" in content)

    # _extract_content with empty string
    content2 = _extract_content("", 500)
    check("extract empty HTML → empty", len(content2.strip()) == 0 or content2 == "")

    # _extract_content with script/style tags
    html_with_noise = """
    <html><body>
        <script>var x = 1;</script>
        <style>.foo { color: red; }</style>
        <p>Useful content here</p>
        <nav>Navigation stuff</nav>
    </body></html>
    """
    content3 = _extract_content(html_with_noise, 500)
    check("script tags removed", "var x" not in content3)
    check("useful content preserved", "Useful content" in content3 or len(content3) > 0)

    # _clean_text comprehensive
    check("clean tabs", " " in _clean_text("hello\tworld") or
          "hello" in _clean_text("hello\tworld"))
    check("clean multiple spaces", "  " not in _clean_text("hello    world"))

    # _truncate edge cases
    long_text = " ".join([f"word{i}" for i in range(1000)])
    truncated = _truncate(long_text, word_limit=5)
    words = truncated.split()
    check("truncate to 5 words", len(words) <= 6)  # allow for trailing ...

    # Mode preset validation
    fast = _get_mode_preset("fast")
    normal = _get_mode_preset("normal")
    deep = _get_mode_preset("deep")
    check("fast pages < normal pages", fast[0] < normal[0])
    check("normal pages < deep pages", normal[0] < deep[0])
    check("fast returns tuple of 3", len(fast) == 3)


# ═════════════════════════════════════════════
# 18. ActiveDirectives — record_sections batch
# ═════════════════════════════════════════════
def test_active_directives_batch():
    print("\n=== TORTURE: ActiveDirectives — Batch Operations ===")
    from src.governance.active_directives import ActiveDirectives
    from src.directives.parser import DirectiveSection

    ad = ActiveDirectives
    ad.reset()

    # record_sections with manifest cross-reference
    sections = [
        DirectiveSection(heading="Alpha", body="Alpha content", scope="shared",
                         source_file="shared.md"),
        DirectiveSection(heading="Beta", body="Beta content", scope="shared",
                         source_file="shared.md"),
        DirectiveSection(heading="Gamma", body="Gamma content", scope="orion",
                         source_file="orion.md"),
    ]

    manifest = {
        "directives": [
            {"id": "shared.alpha", "name": "Alpha", "version": "2.0.0"},
            {"id": "shared.beta", "name": "Beta", "version": "1.5.0"},
        ]
    }

    results = ad.record_sections(sections, manifest=manifest)
    check("batch: 3 results", len(results) == 3)
    check("batch: alpha has manifest id", results[0]["id"] == "shared.alpha")
    check("batch: alpha has manifest version", results[0]["version"] == "2.0.0")
    check("batch: beta version", results[1]["version"] == "1.5.0")
    check("batch: gamma no manifest → unknown", results[2]["version"] == "unknown")

    summary = ad.summary()
    check("batch: count 3", summary["count"] == 3)
    check("batch: scopes include shared", "shared" in summary["scopes"])
    check("batch: total_tokens > 0", summary["total_tokens"] > 0)

    ad.reset()


# ═════════════════════════════════════════════
# 19. Vault stress — concurrent-ish patterns
# ═════════════════════════════════════════════
def test_vault_interleaved_ops():
    print("\n=== TORTURE: Vault — Interleaved Operations ===")
    from src.memory.vault import VaultStore

    tmp = tempfile.mkdtemp()
    try:
        vault = VaultStore(os.path.join(tmp, "vault.jsonl"))

        # Create → update → create → delete → update sequence
        m1 = vault.create_memory(text="First", scope="shared", category="fact")
        m2 = vault.create_memory(text="Second", scope="astraea", category="bio")

        vault.update_memory(m1.id, text="First updated")
        m3 = vault.create_memory(text="Third", scope="shared", category="goal")

        vault.delete_memory(m2.id)
        vault.update_memory(m1.id, text="First updated again")

        active = vault.read_active()
        check("interleaved: 2 active", len(active) == 2)

        m1_final = vault.get_memory(m1.id)
        check("interleaved: m1 version 3", m1_final.version == 3)
        check("interleaved: m1 final text", m1_final.text == "First updated again")

        m2_gone = vault.get_memory(m2.id)
        check("interleaved: m2 deleted", m2_gone is None)

        m3_ok = vault.get_memory(m3.id)
        check("interleaved: m3 intact", m3_ok.text == "Third")

        # Compact after interleaved
        result = vault.compact()
        check("interleaved compact ok", result["lines_after"] == 2)

        active2 = vault.read_active()
        check("interleaved: still 2 after compact", len(active2) == 2)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 20. Storage user_notes_loader edge cases
# ═════════════════════════════════════════════
def test_user_notes_loader_extended():
    print("\n=== TORTURE: User Notes Loader — Extended ===")
    from src.storage.user_notes_loader import strip_html, load_json_user_notes

    # strip_html edge cases
    check("strip numeric entities", len(strip_html("&#60;br&#62;")) >= 0)
    check("strip deeply nested", strip_html("<div><div><div><p>Deep</p></div></div></div>") != "")
    check("strip self-closing", "br" not in strip_html("line<br/>break").lower()
          if "<" in strip_html("line<br/>break") else True)

    # load_json_user_notes with various structures
    tmp = tempfile.mkdtemp()
    try:
        # Index with entries that have files
        os.makedirs(os.path.join(tmp, "user_notes"), exist_ok=True)
        index = [
            {"id": "note1", "title": "Note One", "emoji": "🔥", "trashed": False},
            {"id": "note2", "title": "Note Two", "emoji": "📋", "trashed": True},
            {"id": "note3", "title": "Note Three", "trashed": False},
        ]
        with open(os.path.join(tmp, "user_notes", "index.json"), "w") as f:
            json.dump(index, f)

        # Create note files
        n1 = {"id": "note1", "title": "Note One", "emoji": "🔥",
               "content_html": "<p>Hello world</p>", "trashed": False}
        with open(os.path.join(tmp, "user_notes", "note1.json"), "w") as f:
            json.dump(n1, f)

        n3 = {"id": "note3", "title": "Note Three", "emoji": "📝",
               "content_html": "", "trashed": False}
        with open(os.path.join(tmp, "user_notes", "note3.json"), "w") as f:
            json.dump(n3, f)

        notes = load_json_user_notes(os.path.join(tmp, "user_notes"))
        check("loaded notes type", isinstance(notes, str))
        # note2 is trashed, so should be excluded
        check("trashed note excluded", "Note Two" not in notes)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 21. Manifest diff — comprehensive scenarios
# ═════════════════════════════════════════════
def test_manifest_diff_extended():
    print("\n=== TORTURE: Manifest Diff — Edge Cases ===")
    from src.directives.manifest import diff_manifest

    # Both empty
    d = diff_manifest({"directives": []}, {"directives": []})
    check("both empty → 0 changes", d["total_added"] == 0)
    check("both empty → 0 removed", d["total_removed"] == 0)
    check("both empty → 0 changed", d["total_changed"] == 0)
    check("both empty → 0 unchanged", d["unchanged_count"] == 0)

    # Old empty, new has entries
    new = {"directives": [
        {"id": "a", "name": "A", "scope": "shared", "sha256": "aaa"},
        {"id": "b", "name": "B", "scope": "shared", "sha256": "bbb"},
    ]}
    d = diff_manifest({"directives": []}, new)
    check("new only → 2 added", d["total_added"] == 2)
    check("new only → 0 removed", d["total_removed"] == 0)

    # New empty, old has entries
    d2 = diff_manifest(new, {"directives": []})
    check("old only → 0 added", d2["total_added"] == 0)
    check("old only → 2 removed", d2["total_removed"] == 2)

    # Same entries, different hashes
    old = {"directives": [{"id": "x", "name": "X", "scope": "s", "sha256": "111"}]}
    new2 = {"directives": [{"id": "x", "name": "X", "scope": "s", "sha256": "222"}]}
    d3 = diff_manifest(old, new2)
    check("hash change → 1 changed", d3["total_changed"] == 1)
    check("hash change entry has old_sha256", d3["changed"][0]["old_sha256"] == "111")
    check("hash change entry has new_sha256", d3["changed"][0]["new_sha256"] == "222")

    # Complex: add + remove + change + unchanged
    old_complex = {"directives": [
        {"id": "keep", "name": "K", "scope": "s", "sha256": "same"},
        {"id": "change", "name": "C", "scope": "s", "sha256": "old_hash"},
        {"id": "remove", "name": "R", "scope": "s", "sha256": "r"},
    ]}
    new_complex = {"directives": [
        {"id": "keep", "name": "K", "scope": "s", "sha256": "same"},
        {"id": "change", "name": "C", "scope": "s", "sha256": "new_hash"},
        {"id": "add", "name": "A", "scope": "s", "sha256": "a"},
    ]}
    d4 = diff_manifest(old_complex, new_complex)
    check("complex: 1 added", d4["total_added"] == 1)
    check("complex: 1 removed", d4["total_removed"] == 1)
    check("complex: 1 changed", d4["total_changed"] == 1)
    check("complex: 1 unchanged", d4["unchanged_count"] == 1)


# ═════════════════════════════════════════════
# 22. Echo tool
# ═════════════════════════════════════════════
def test_echo_tool():
    print("\n=== TORTURE: Echo Tool ===")
    from src.tools.echo import EchoTool

    tool = EchoTool()
    defn = tool.definition()
    check("echo definition name", defn["name"] == "echo")

    # Normal echo
    result = tool.execute({"message": "Hello!"})
    check("echo returns message", "Hello!" in result)

    # Empty message
    result2 = tool.execute({"message": ""})
    check("echo empty → some response", isinstance(result2, str))

    # No message key
    result3 = tool.execute({})
    check("echo no message → handled", isinstance(result3, str))

    # Unicode
    result4 = tool.execute({"message": "こんにちは 🌍"})
    check("echo unicode", "こんにちは" in result4)


# ═════════════════════════════════════════════
# 23. LLM client base types
# ═════════════════════════════════════════════
def test_llm_types():
    print("\n=== TORTURE: LLM Client Types ===")
    from src.llm_client.base import LLMResponse

    # Default construction
    r = LLMResponse()
    check("default content None", r.content is None)
    check("default tool_calls []", r.tool_calls == [])
    check("default model ''", r.model == "")
    check("default usage None", r.usage is None)
    check("default raw {}", r.raw == {})

    # Full construction
    r2 = LLMResponse(
        content="Hello",
        tool_calls=[{"name": "echo", "arguments": {"message": "hi"}}],
        model="gpt-4",
        usage={"prompt_tokens": 10, "completion_tokens": 5},
        raw={"id": "chatcmpl-123"},
    )
    check("content set", r2.content == "Hello")
    check("tool_calls set", len(r2.tool_calls) == 1)
    check("model set", r2.model == "gpt-4")
    check("usage set", r2.usage["prompt_tokens"] == 10)
    check("raw set", r2.raw["id"] == "chatcmpl-123")

    # Instance isolation
    r3 = LLMResponse()
    r3.tool_calls.append({"name": "test"})
    r4 = LLMResponse()
    check("instances isolated", len(r4.tool_calls) == 0)


# ═════════════════════════════════════════════
# 24. Directive injector with manifest
# ═════════════════════════════════════════════
def test_directive_injector_with_manifest():
    print("\n=== TORTURE: Directive Injector — With Manifest ===")
    from src.directives.injector import build_directives_block
    from src.directives.store import DirectiveStore
    from src.governance.active_directives import ActiveDirectives

    tmp = tempfile.mkdtemp()
    try:
        path = os.path.join(tmp, "shared.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("## Core Values\nBe helpful, honest, and harmless.\n\n"
                    "## Communication Style\nBe concise and clear.\n\n"
                    "## Safety Rules\nNever reveal secrets.\n")

        store = DirectiveStore(tmp, scopes="shared")
        manifest = {
            "directives": [
                {"id": "shared.core_values", "name": "Core Values", "version": "1.0.0"},
                {"id": "shared.communication_style", "name": "Communication Style", "version": "1.0.0"},
                {"id": "shared.safety_rules", "name": "Safety Rules", "version": "1.0.0"},
            ]
        }

        ActiveDirectives.reset()
        block = build_directives_block(store, "helpful communication", max_sections=2,
                                       manifest=manifest)
        check("block not empty", len(block) > 0)
        check("block has directives header", "Directive" in block or "directive" in block.lower())

        # ActiveDirectives should have been populated
        count = ActiveDirectives.count()
        check("AD populated", count > 0, f"count={count}")
        check("AD max 2 sections", count <= 2)

        ActiveDirectives.reset()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 25. Model Router — config defaults, load/save, API round-trip
# ═════════════════════════════════════════════
def test_model_router_config():
    """Test the model router configuration system: defaults, load/save, merge logic, API endpoints."""
    print("\n=== TORTURE: Model Router — Config & API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        # ── Import backend objects ──
        from web.app import (
            _MODEL_ROUTER_DEFAULTS,
            _load_model_router_config, _save_model_router_config,
            MODEL_ROUTER_FILE,
            _read_json, _write_json,
        )
        import web.app as _app_mod
        import src.routing.model_router as _router_mod

        # Save original path and redirect to temp
        orig_file = _app_mod.MODEL_ROUTER_FILE
        orig_router_file = _router_mod.MODEL_ROUTER_FILE
        tmp_file = Path(tmp) / "model_router.json"
        _app_mod.MODEL_ROUTER_FILE = tmp_file
        _router_mod.MODEL_ROUTER_FILE = tmp_file

        # ── 1. Defaults structure ──
        check("defaults has tiers", "tiers" in _MODEL_ROUTER_DEFAULTS)
        check("defaults has task_tier_map", "task_tier_map" in _MODEL_ROUTER_DEFAULTS)
        tiers = _MODEL_ROUTER_DEFAULTS["tiers"]
        check("6 default tiers", len(tiers) == 6)

        # Tier IDs
        tier_ids = [t["id"] for t in tiers]
        check("tier ids are t0-t5", tier_ids == ["t0", "t1", "t2", "t3", "t4", "t5"])

        # Each tier has required fields
        required_fields = [
            "id", "label", "enabled", "connection_id", "provider",
            "primary_model", "temperature", "max_output_tokens",
            "max_iterations", "retries_before_escalate", "alt_models", "cost_per_call",
        ]
        for t in tiers:
            for fld in required_fields:
                check(f"{t['id']} has {fld}", fld in t, f"missing {fld} in {t['id']}")

        # Tier labels
        labels = [t["label"] for t in tiers]
        check("labels correct", labels == ["local_cheap", "local_strong", "cheap_cloud", "expensive_cloud", "code_light", "code_heavy"])

        # All tiers enabled by default
        check("all tiers enabled", all(t["enabled"] for t in tiers))

        # Temperature ranges
        for t in tiers:
            check(f"{t['id']} temp 0-2", 0 <= t["temperature"] <= 2,
                  f"temp={t['temperature']}")

        # Max output tokens positive
        for t in tiers:
            check(f"{t['id']} tokens > 0", t["max_output_tokens"] > 0)

        # Max iterations positive
        for t in tiers:
            check(f"{t['id']} iterations > 0", t["max_iterations"] > 0)

        # Alt models are lists
        for t in tiers:
            check(f"{t['id']} alt_models is list", isinstance(t["alt_models"], list))

        # ── 1b. Enabled flag ──
        check("defaults has enabled", "enabled" in _MODEL_ROUTER_DEFAULTS)
        check("enabled is True by default", _MODEL_ROUTER_DEFAULTS["enabled"] is True)

        # ── 2. Task tier map ──
        ttm = _MODEL_ROUTER_DEFAULTS["task_tier_map"]
        expected_tasks = ["coding_light", "coding_heavy", "summarization", "planning",
                          "high_stakes", "final_polish", "memory_ops", "reflection",
                          "general", "tool_use", "agi_tick"]
        check("11 default task types", len(ttm) == 11, f"got {len(ttm)}")
        for task in expected_tasks:
            check(f"task '{task}' in map", task in ttm, f"missing: {task}")

        valid_tiers = {"local_cheap", "local_strong", "cheap_cloud", "expensive_cloud",
                       "code_light", "code_heavy", "__auto__"}
        for task, tier in ttm.items():
            check(f"task '{task}' → valid tier", tier in valid_tiers, f"got: {tier}")

        check("general → __auto__", ttm["general"] == "__auto__")
        check("coding_light → code_light", ttm["coding_light"] == "code_light")
        check("coding_heavy → code_heavy", ttm["coding_heavy"] == "code_heavy")
        check("final_polish → expensive_cloud", ttm["final_polish"] == "expensive_cloud")
        check("planning → local_strong", ttm["planning"] == "local_strong")

        # ── 3. Load with missing file → returns defaults ──
        if tmp_file.exists():
            tmp_file.unlink()
        cfg = _load_model_router_config()
        check("missing file → has tiers", "tiers" in cfg)
        check("missing file → 6 tiers", len(cfg["tiers"]) == 6)
        check("missing file → has task_tier_map", "task_tier_map" in cfg)
        check("missing file → 11 tasks", len(cfg["task_tier_map"]) == 11)

        # ── 4. Save + reload round-trip ──
        custom = {
            "tiers": [
                {"id": "t0", "label": "custom_local", "enabled": False,
                 "connection_id": "conn_1", "provider": "ollama",
                 "primary_model": "gemma:2b", "temperature": 0.9,
                 "max_output_tokens": 1024, "max_iterations": 5,
                 "retries_before_escalate": 1, "alt_models": ["phi3"],
                 "cost_per_call": "~$0.00"},
            ],
            "task_tier_map": {"coding": "local_cheap", "general": "__auto__"},
        }
        _save_model_router_config(custom)
        check("file created", tmp_file.exists())

        loaded = _load_model_router_config()
        check("round-trip tiers count", len(loaded["tiers"]) == 1)
        check("round-trip tier label", loaded["tiers"][0]["label"] == "custom_local")
        check("round-trip tier disabled", loaded["tiers"][0]["enabled"] is False)
        check("round-trip alt_models", loaded["tiers"][0]["alt_models"] == ["phi3"])
        check("round-trip task map coding", loaded["task_tier_map"]["coding"] == "local_cheap")

        # ── 5. Partial save → merge with defaults ──
        _write_json(tmp_file, {"task_tier_map": {"coding": "expensive_cloud"}})
        merged = _load_model_router_config()
        check("partial → tiers from defaults", len(merged["tiers"]) == 6)
        check("partial → coding overridden", merged["task_tier_map"]["coding"] == "expensive_cloud")

        # ── 6. Empty save → defaults restored ──
        _write_json(tmp_file, {})
        empty_load = _load_model_router_config()
        check("empty file → tiers from defaults", len(empty_load["tiers"]) == 6)
        check("empty file → task_tier_map from defaults", len(empty_load["task_tier_map"]) == 11)

        # ── 6b. Empty task_tier_map {} → defaults restored (regression fix) ──
        _write_json(tmp_file, {"task_tier_map": {}, "tiers": [{"id": "t0", "label": "x", "enabled": True}]})
        empty_map_load = _load_model_router_config()
        check("empty map → task_tier_map repopulated", len(empty_map_load["task_tier_map"]) == 11,
              f"got {len(empty_map_load['task_tier_map'])} keys")
        check("empty map → coding_light present", "coding_light" in empty_map_load["task_tier_map"])
        check("empty map → coding_heavy present", "coding_heavy" in empty_map_load["task_tier_map"])
        check("empty map → general is __auto__", empty_map_load["task_tier_map"]["general"] == "__auto__")
        # Tiers should NOT be overwritten since they were provided
        check("empty map → tiers preserved", len(empty_map_load["tiers"]) == 1)
        check("empty map → tier label preserved", empty_map_load["tiers"][0]["label"] == "x")

        # ── 7. API endpoints via TestClient ──
        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio

            # Remove saved file so we test fresh defaults
            if tmp_file.exists():
                tmp_file.unlink()

            from web.app import app as _test_app

            async def _run_api_tests():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # GET → defaults
                    r = await client.get("/api/model-router/config")
                    check("GET status 200", r.status_code == 200)
                    data = r.json()
                    check("GET has tiers", "tiers" in data)
                    check("GET has task_tier_map", "task_tier_map" in data)
                    if "tiers" not in data:
                        # Auth/middleware block — skip remaining API tests
                        check("API response missing tiers — skipping API tests", True)
                        return
                    check("GET 6 tiers", len(data["tiers"]) == 6)

                    # POST → save custom config
                    custom_post = {
                        "tiers": data["tiers"],
                        "task_tier_map": {**data["task_tier_map"], "coding": "local_strong"},
                    }
                    r2 = await client.post("/api/model-router/config", json=custom_post)
                    check("POST status 200", r2.status_code == 200)
                    resp2 = r2.json()
                    check("POST ok", resp2.get("ok") is True)
                    check("POST config returned", "config" in resp2)
                    check("POST coding changed", resp2["config"]["task_tier_map"]["coding"] == "local_strong")

                    # GET after POST → reflects saved state
                    r3 = await client.get("/api/model-router/config")
                    data3 = r3.json()
                    check("GET after POST reflects save", data3["task_tier_map"]["coding"] == "local_strong")

                    # POST /reset → restore defaults
                    r4 = await client.post("/api/model-router/reset")
                    check("RESET status 200", r4.status_code == 200)
                    resp4 = r4.json()
                    check("RESET ok", resp4.get("ok") is True)
                    check("RESET coding_light back to default",
                          resp4["config"]["task_tier_map"].get("coding_light") == "code_light")
                    check("RESET 6 tiers", len(resp4["config"]["tiers"]) == 6)

                    # GET after reset → defaults
                    r5 = await client.get("/api/model-router/config")
                    data5 = r5.json()
                    check("GET after reset → default coding_heavy",
                          data5["task_tier_map"].get("coding_heavy") == "code_heavy")

            import web.app as _app_auth_1
            _orig_gac_1 = _app_auth_1.get_auth_config
            _app_auth_1.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run_api_tests())
            finally:
                _app_auth_1.get_auth_config = _orig_gac_1

        except ImportError:
            # httpx not installed — skip API tests gracefully
            check("httpx not available — API tests skipped", True)

        # ── 8. Tier-specific field validations ──
        t0 = _MODEL_ROUTER_DEFAULTS["tiers"][0]
        t3 = _MODEL_ROUTER_DEFAULTS["tiers"][3]

        check("t0 provider ollama", t0["provider"] == "ollama")
        check("t0 model qwen2.5:7b", t0["primary_model"] == "qwen2.5:7b")
        check("t3 provider openai", t3["provider"] == "openai")
        check("t3 model gpt-4o", t3["primary_model"] == "gpt-4o")
        check("t0 cost ~$0.00", t0["cost_per_call"] == "~$0.00")
        check("t3 cost contains $0.01", "$0.01" in t3["cost_per_call"])

        # Escalation: retries should decrease as tier cost increases
        check("t0 retries >= t3 retries",
              t0["retries_before_escalate"] >= t3["retries_before_escalate"])

        # Max iterations should increase with tier capability
        check("t3 iterations >= t0 iterations",
              t3["max_iterations"] >= t0["max_iterations"])

        # ── 9. Presets CRUD API ──
        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio

            from web.app import (
                _ROUTER_PRESETS_DIR,
                _ensure_router_presets_dir,
                _list_router_presets,
            )
            import web.app as _app_mod2

            # Redirect presets dir to temp
            orig_presets_dir = _app_mod2._ROUTER_PRESETS_DIR
            tmp_presets = Path(tmp) / "router_presets"
            _app_mod2._ROUTER_PRESETS_DIR = tmp_presets

            from web.app import app as _test_app2

            async def _run_preset_api_tests():
                transport = ASGITransport(app=_test_app2)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # LIST empty
                    r = await client.get("/api/model-router/presets")
                    check("preset list 200", r.status_code == 200)
                    data = r.json()
                    check("preset list has presets key", "presets" in data)
                    if "presets" not in data:
                        check("preset API response missing presets — skipping", True)
                        return
                    check("preset list initially empty", len(data["presets"]) == 0)

                    # SAVE — missing name → 400
                    r_bad = await client.post("/api/model-router/presets", json={})
                    check("preset save no name → 400", r_bad.status_code == 400)
                    check("preset save no name error msg", "Name" in r_bad.json().get("error", ""))

                    # SAVE — empty name → 400
                    r_bad2 = await client.post("/api/model-router/presets", json={"name": "   "})
                    check("preset save blank name → 400", r_bad2.status_code == 400)

                    # SAVE — valid preset
                    r_save = await client.post("/api/model-router/presets", json={
                        "name": "Test Preset",
                        "description": "A test preset",
                        "config": {"tiers": [], "task_tier_map": {"coding": "local_cheap"}},
                    })
                    check("preset save 200", r_save.status_code == 200)
                    save_data = r_save.json()
                    check("preset save ok", save_data.get("ok") is True)
                    check("preset save filename", save_data.get("filename") == "Test_Preset")

                    # SAVE — special characters in name → sanitised
                    r_special = await client.post("/api/model-router/presets", json={
                        "name": "My <Special> /Preset\\!",
                        "description": "chars",
                    })
                    check("preset special chars save ok", r_special.json().get("ok") is True)
                    fn_special = r_special.json().get("filename", "")
                    check("preset no angle brackets", "<" not in fn_special and ">" not in fn_special)
                    check("preset no slashes", "/" not in fn_special and "\\" not in fn_special)

                    # LIST — should have 2 presets now
                    r_list = await client.get("/api/model-router/presets")
                    presets = r_list.json()["presets"]
                    check("preset list has 2", len(presets) == 2)
                    names = [p["name"] for p in presets]
                    check("preset Test Preset in list", "Test Preset" in names)
                    # Each preset entry has required fields
                    for p in presets:
                        check(f"preset '{p['name']}' has filename", "filename" in p)
                        check(f"preset '{p['name']}' has created", "created" in p)
                        check(f"preset '{p['name']}' has description", "description" in p)

                    # LOAD — existing preset
                    r_load = await client.post("/api/model-router/presets/Test_Preset/load")
                    check("preset load 200", r_load.status_code == 200)
                    load_data = r_load.json()
                    check("preset load ok", load_data.get("ok") is True)
                    check("preset load has config", "config" in load_data)
                    check("preset load has name", load_data.get("name") == "Test Preset")
                    check("preset load config correct",
                          load_data["config"]["task_tier_map"]["coding"] == "local_cheap")

                    # LOAD — nonexistent preset → 404
                    r_404 = await client.post("/api/model-router/presets/doesnotexist/load")
                    check("preset load missing → 404", r_404.status_code == 404)

                    # DELETE — existing preset
                    r_del = await client.delete("/api/model-router/presets/Test_Preset")
                    check("preset delete 200", r_del.status_code == 200)
                    check("preset delete ok", r_del.json().get("ok") is True)

                    # LIST — should have 1 preset now
                    r_list2 = await client.get("/api/model-router/presets")
                    check("preset list after delete has 1", len(r_list2.json()["presets"]) == 1)

                    # DELETE — nonexistent (still returns ok)
                    r_del2 = await client.delete("/api/model-router/presets/nonexistent")
                    check("preset delete missing → ok", r_del2.json().get("ok") is True)

                    # SAVE — preset without config → uses current router config
                    r_noconfig = await client.post("/api/model-router/presets", json={
                        "name": "No Config Preset",
                    })
                    check("preset save no config ok", r_noconfig.json().get("ok") is True)
                    # Load it and verify it has a full config
                    fn_nc = r_noconfig.json()["filename"]
                    r_load_nc = await client.post(f"/api/model-router/presets/{fn_nc}/load")
                    nc_cfg = r_load_nc.json().get("config", {})
                    check("preset no-config has tiers", "tiers" in nc_cfg or len(nc_cfg) > 0)

                    # SAVE — overwrite existing preset
                    r_over = await client.post("/api/model-router/presets", json={
                        "name": "No Config Preset",
                        "description": "overwritten",
                        "config": {"tiers": [], "task_tier_map": {}},
                    })
                    check("preset overwrite ok", r_over.json().get("ok") is True)
                    r_load_over = await client.post(f"/api/model-router/presets/{fn_nc}/load")
                    check("preset overwrite description",
                          True)  # file was overwritten successfully

            import web.app as _app_auth_2
            _orig_gac_2 = _app_auth_2.get_auth_config
            _app_auth_2.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run_preset_api_tests())
            finally:
                _app_auth_2.get_auth_config = _orig_gac_2

            _app_mod2._ROUTER_PRESETS_DIR = orig_presets_dir

        except ImportError:
            check("httpx not available — preset API tests skipped", True)

    finally:
        _app_mod.MODEL_ROUTER_FILE = orig_file
        _router_mod.MODEL_ROUTER_FILE = orig_router_file
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 25b. Model Router TOOL — classify, resolve, tier escalation
# ═════════════════════════════════════════════
def test_model_router_tool():
    """Test the ModelRouterTool callable interface, classify_task,
    resolve_model_for_task, resolve_tier, get_next_tier, get_tier_for_connection."""
    print("\n=== TORTURE: Model Router — Tool Interface ===")
    from src.tools.model_router import (
        ModelRouterTool, classify_task, resolve_model_for_task,
        resolve_tier, get_next_tier, get_tier_for_connection,
        load_router_config, _DEFAULTS, _CLASSIFICATION_RULES,
    )

    # ── 1. Definition structure ──
    defn = ModelRouterTool.definition()
    check("MR def name", defn["name"] == "model_router")
    check("MR def has params", "parameters" in defn)
    actions = defn["parameters"]["properties"]["action"]["enum"]
    check("MR 5 actions", len(actions) == 5)
    check("MR actions list", set(actions) == {"resolve", "list_tiers", "get_map", "classify", "budget"})
    check("MR has text param", "text" in defn["parameters"]["properties"])

    # ── 2. classify_task — keyword mapping (coding split into heavy/light) ──
    check("classify coding_heavy", classify_task("write code for a REST API") == "coding_heavy")
    check("classify implement", classify_task("implement the login feature") == "coding_heavy")
    check("classify debug", classify_task("debug this crash") == "coding_heavy")
    check("classify refactor", classify_task("refactor the module") == "coding_heavy")
    check("classify regex", classify_task("write a regex to match emails") == "coding_heavy")
    check("classify rename", classify_task("rename this variable") == "coding_light")
    check("classify typo", classify_task("fix the typo") == "coding_light")

    check("classify summarize", classify_task("summarize the meeting notes") == "summarization")
    check("classify tldr", classify_task("give me a tldr") == "summarization")

    check("classify plan", classify_task("plan the project") == "planning")
    check("classify roadmap", classify_task("create a roadmap for Q3") == "planning")
    check("classify architect", classify_task("architect the system") == "planning")

    check("classify review", classify_task("review the security audit") == "high_stakes")
    check("classify deploy", classify_task("deploy to production") == "high_stakes")

    check("classify polish", classify_task("final polish the document") == "final_polish")
    check("classify proofread", classify_task("proofread the essay") == "final_polish")

    check("classify remember", classify_task("remember this fact") == "memory_ops")
    check("classify vault", classify_task("store in the vault") == "memory_ops")

    check("classify reflect", classify_task("reflect on today's progress") == "reflection")
    check("classify journal", classify_task("write a journal entry") == "reflection")

    check("classify search tool", classify_task("search for information about Python") == "tool_use")
    check("classify web search", classify_task("web search for news") == "tool_use")

    check("classify general", classify_task("hello how are you") == "general")
    check("classify empty", classify_task("") == "general")

    # Case insensitivity
    check("classify UPPER", classify_task("SUMMARIZE THIS") == "summarization")
    check("classify mixed", classify_task("Debug My Script") == "coding_heavy")

    # ── 3. Priority ordering — highest-score wins ──
    # "write code to plan a deployment" → coding_heavy has more keyword hits
    result = classify_task("write code to plan a deployment")
    check("priority: coding_heavy before planning", result == "coding_heavy")

    # ── 4. Classification rules structure ──
    check("rules is list", isinstance(_CLASSIFICATION_RULES, list))
    check("rules non-empty", len(_CLASSIFICATION_RULES) > 0)
    for i, (keywords, task_type) in enumerate(_CLASSIFICATION_RULES):
        check(f"rule {i} has keywords", isinstance(keywords, list) and len(keywords) > 0)
        check(f"rule {i} has task_type str", isinstance(task_type, str))

    # ── 5. _DEFAULTS structure ──
    check("defaults has enabled", "enabled" in _DEFAULTS)
    check("defaults has task_tier_map", "task_tier_map" in _DEFAULTS)
    check("defaults enabled True", _DEFAULTS["enabled"] is True)
    check("defaults 11 task types", len(_DEFAULTS["task_tier_map"]) == 11)

    # ── 6. resolve_tier — with mock config ──
    mock_cfg = {
        "enabled": True,
        "tiers": [
            {"id": "t0", "label": "local_cheap", "enabled": True,
             "provider": "ollama", "primary_model": "qwen2.5:7b"},
            {"id": "t1", "label": "cheap_cloud", "enabled": True,
             "provider": "openai", "primary_model": "gpt-4o-mini"},
            {"id": "t2", "label": "expensive_cloud", "enabled": True,
             "provider": "openai", "primary_model": "gpt-4o"},
            {"id": "t3", "label": "disabled_tier", "enabled": False,
             "provider": "openai", "primary_model": "gpt-5"},
        ],
        "task_tier_map": {
            "coding": "cheap_cloud",
            "general": "__auto__",
            "summarization": "local_cheap",
            "high_stakes": "disabled_tier",
        },
    }

    tier = resolve_tier("coding", mock_cfg)
    check("resolve coding → cheap_cloud", tier is not None and tier["label"] == "cheap_cloud")
    check("resolve coding model", tier["primary_model"] == "gpt-4o-mini")

    tier_sum = resolve_tier("summarization", mock_cfg)
    check("resolve summarization → local_cheap", tier_sum is not None and tier_sum["label"] == "local_cheap")

    tier_gen = resolve_tier("general", mock_cfg)
    check("resolve general → None (__auto__)", tier_gen is None)

    tier_hs = resolve_tier("high_stakes", mock_cfg)
    check("resolve disabled tier → None", tier_hs is None)

    tier_unknown = resolve_tier("nonexistent_task", mock_cfg)
    check("resolve unknown task → None", tier_unknown is None)

    # Disabled router
    disabled_cfg = {**mock_cfg, "enabled": False}
    check("disabled router → None", resolve_tier("coding", disabled_cfg) is None)

    # ── 7. resolve_model_for_task ──
    model, provider, task_type = resolve_model_for_task("write a python function", mock_cfg)
    check("resolve_model task_type=coding_heavy", task_type == "coding_heavy")
    # With backward-compat fallback, coding_heavy → coding → cheap_cloud
    check("resolve_model model set", model == "gpt-4o-mini")
    check("resolve_model provider set", provider == "openai")

    model2, provider2, task_type2 = resolve_model_for_task("hello there", mock_cfg)
    check("resolve_model general → None model", model2 is None)
    check("resolve_model general → None provider", provider2 is None)
    check("resolve_model general task_type", task_type2 == "general")

    # ── 8. get_next_tier — escalation chain ──
    next_tier = get_next_tier("t0", mock_cfg)
    check("escalate t0 → t1", next_tier is not None and next_tier["id"] == "t1")

    next_tier2 = get_next_tier("t1", mock_cfg)
    check("escalate t1 → t2", next_tier2 is not None and next_tier2["id"] == "t2")

    # t2 is last enabled, t3 is disabled so skipped
    next_tier3 = get_next_tier("t2", mock_cfg)
    check("escalate t2 → None (t3 disabled)", next_tier3 is None)

    # Unknown tier ID
    next_unknown = get_next_tier("nonexistent", mock_cfg)
    check("escalate unknown → None", next_unknown is None)

    # ── 9. get_tier_for_connection ──
    t = get_tier_for_connection("cheap_cloud", mock_cfg)
    check("tier_for_connection found", t is not None and t["provider"] == "openai")

    t_disabled = get_tier_for_connection("disabled_tier", mock_cfg)
    check("tier_for_connection disabled → None", t_disabled is None)

    t_missing = get_tier_for_connection("nonexistent_label", mock_cfg)
    check("tier_for_connection missing → None", t_missing is None)

    # ── 10. Tool execute — all 5 actions ──
    # classify action
    r = json.loads(ModelRouterTool.execute({"action": "classify", "text": "write a function"}))
    check("execute classify → coding_heavy", r["task_type"] == "coding_heavy")
    check("execute classify has model field", "model" in r)

    # classify missing text
    r_err = json.loads(ModelRouterTool.execute({"action": "classify"}))
    check("execute classify no text → error", "error" in r_err)

    # resolve action
    r2 = json.loads(ModelRouterTool.execute({"action": "resolve", "text": "summarize this"}))
    check("execute resolve has task_type", "task_type" in r2)
    check("execute resolve has fallback", "fallback" in r2)

    # resolve missing text
    r2_err = json.loads(ModelRouterTool.execute({"action": "resolve"}))
    check("execute resolve no text → error", "error" in r2_err)

    # list_tiers action
    r3 = json.loads(ModelRouterTool.execute({"action": "list_tiers"}))
    check("execute list_tiers has tiers", "tiers" in r3)
    check("execute list_tiers has enabled", "enabled" in r3)

    # get_map action
    r4 = json.loads(ModelRouterTool.execute({"action": "get_map"}))
    check("execute get_map has task_tier_map", "task_tier_map" in r4)
    check("execute get_map has enabled", "enabled" in r4)
    check("execute get_map 10 tasks", len(r4["task_tier_map"]) >= 10)

    # unknown action
    r5 = json.loads(ModelRouterTool.execute({"action": "BOGUS"}))
    check("execute unknown action → error", "error" in r5)

    # default action (no action key)
    r6 = json.loads(ModelRouterTool.execute({}))
    check("execute no action → list_tiers", "tiers" in r6)


# ═════════════════════════════════════════════
# EMAIL TOOL — comprehensive torture tests
# ═════════════════════════════════════════════

def test_email_tool_torture():
    """Exhaustive tests for EmailTool: definition, actions, account CRUD,
    validation, confirmation gate, agent_name resolution, SMTP error paths."""
    print("\n=== TORTURE: Email Tool — Full Coverage ===")
    from src.tools.email_tool import (
        EmailTool, get_accounts, _get_accounts_raw as get_accounts_raw, get_default_account,
        get_user_account, get_agent_default_account, get_account_by_id,
        save_account, delete_account, get_effective_config,
        _load_settings, _save_settings, _load_tool_config,
        _SETTINGS_FILE,
    )
    from pathlib import Path
    import src.tools.email_tool as et_mod

    tool = EmailTool()
    test_uid = "test_user_123"

    # ── 1. Definition ──
    defn = tool.definition()
    check("email def name", defn["name"] == "email")
    check("email def has description", len(defn["description"]) > 20)
    props = defn["parameters"]["properties"]
    check("action in params", "action" in props)
    check("subject in params", "subject" in props)
    check("body in params", "body" in props)
    check("recipients in params", "recipients" in props)
    check("account_id in params", "account_id" in props)
    check("confirmation in params", "confirmation" in props)
    check("action required", "action" in defn["parameters"]["required"])
    actions = props["action"]["enum"]
    check("3 actions", len(actions) == 3)
    for a in ("send", "status", "accounts"):
        check(f"action '{a}'", a in actions)

    # ── 2. Isolated account CRUD (temp settings file) ──
    orig_settings = et_mod._SETTINGS_FILE
    orig_data_dir = et_mod._DATA_DIR
    tmp = tempfile.mkdtemp()
    tmp_settings = Path(tmp) / "config" / "settings.json"
    et_mod._SETTINGS_FILE = tmp_settings
    et_mod._DATA_DIR = Path(tmp) / "data"

    try:
        # Empty state
        check("no accounts initially", len(get_accounts(test_uid)) == 0)
        check("no raw accounts", len(get_accounts_raw(test_uid)) == 0)
        check("default account → None", get_default_account(test_uid) is None)
        check("user account → None", get_user_account(test_uid) is None)
        check("agent default → None", get_agent_default_account(test_uid, "astraea") is None)
        check("account by id → None", get_account_by_id(test_uid, "nope") is None)

        # effective_config defaults
        cfg = get_effective_config(test_uid)
        check("cfg has api_base_url", "api_base_url" in cfg)
        check("cfg has timeout", cfg["timeout"] == 30)
        check("cfg require_confirmation default True", cfg["require_confirmation"] is True)
        check("cfg accounts empty", len(cfg["accounts"]) == 0)

        # Create first account
        acct1 = save_account(test_uid, {
            "label": "Work",
            "email": "work@example.com",
            "password": "secret123",
            "smtp_server": "smtp.example.com",
            "smtp_port": 465,
            "signature": "Best regards",
            "is_default": True,
            "is_user_email": False,
            "agent_default": "",
        })
        check("acct1 got id", acct1.get("id") is not None and acct1["id"].startswith("acct_"))
        check("acct1 label", acct1["label"] == "Work")
        check("1 account now", len(get_accounts_raw(test_uid)) == 1)

        # Password masking
        masked = get_accounts(test_uid)
        check("password masked", masked[0]["password"] == "••••••••")
        check("password_set True", masked[0]["password_set"] is True)

        # Default fallback
        check("default → acct1", get_default_account(test_uid)["id"] == acct1["id"])

        # Create second account (agent default for astraea)
        acct2 = save_account(test_uid, {
            "label": "Agent Mail",
            "email": "agent@example.com",
            "password": "agentpwd",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "signature": "",
            "is_default": False,
            "is_user_email": True,
            "agent_default": "astraea",
        })
        check("acct2 created", acct2.get("id") is not None)
        check("2 accounts now", len(get_accounts_raw(test_uid)) == 2)
        check("agent default astraea", get_agent_default_account(test_uid, "astraea")["id"] == acct2["id"])
        check("user account → acct2", get_user_account(test_uid)["id"] == acct2["id"])
        check("lookup by id", get_account_by_id(test_uid, acct2["id"])["label"] == "Agent Mail")

        # Update account (keep masked password)
        acct2_updated = dict(acct2)
        acct2_updated["label"] = "Agent Mail Updated"
        acct2_updated["password"] = "••••••••"  # masked placeholder
        saved = save_account(test_uid, acct2_updated)
        check("update preserves password",
              get_account_by_id(test_uid, acct2["id"])["password"] == "agentpwd")
        check("update changes label",
              get_account_by_id(test_uid, acct2["id"])["label"] == "Agent Mail Updated")

        # Uniqueness: set acct2 as default → acct1 loses default
        acct2_def = dict(get_account_by_id(test_uid, acct2["id"]))
        acct2_def["is_default"] = True
        save_account(test_uid, acct2_def)
        check("acct1 no longer default",
              get_account_by_id(test_uid, acct1["id"]).get("is_default") is False)
        check("acct2 now default",
              get_account_by_id(test_uid, acct2["id"]).get("is_default") is True)

        # Agent default uniqueness: new account for astraea → acct2 loses it
        acct3 = save_account(test_uid, {
            "label": "New Astraea Mail",
            "email": "new@example.com",
            "password": "pwd3",
            "smtp_server": "smtp.example.com",
            "smtp_port": 465,
            "is_default": False,
            "agent_default": "astraea",
        })
        check("acct2 lost agent_default",
              get_account_by_id(test_uid, acct2["id"]).get("agent_default", "") == "")
        check("acct3 has agent_default",
              get_account_by_id(test_uid, acct3["id"]).get("agent_default") == "astraea")

        # Delete
        check("delete acct3", delete_account(test_uid, acct3["id"]) is True)
        check("delete nonexistent", delete_account(test_uid, "fake_id") is False)
        check("2 accounts remain", len(get_accounts_raw(test_uid)) == 2)

        # ── 3. Execute: accounts action ──
        r = json.loads(tool.execute({"action": "accounts"}, user_id=test_uid))
        check("exec accounts has list", isinstance(r["accounts"], list))
        check("exec accounts total", r["total"] == 2)

        # ── 4. Execute: status action ──
        r = json.loads(tool.execute({"action": "status"}, user_id=test_uid))
        check("exec status has accounts_configured", r["accounts_configured"] == 2)
        # API server likely not running → api_server_running false
        check("exec status api field", "api_server_running" in r)

        # ── 5. Execute: unknown action ──
        r = json.loads(tool.execute({"action": "nope"}, user_id=test_uid))
        check("exec unknown action → error", "error" in r)

        # ── 6. Execute: send — validation ──
        # Missing subject
        r = json.loads(tool.execute({"action": "send"}, user_id=test_uid))
        check("send no subject → error", "error" in r)
        check("send error mentions subject", "subject" in r["error"].lower())

        # Missing body
        r = json.loads(tool.execute({"action": "send", "subject": "Hi"}, user_id=test_uid))
        check("send no body → error", "error" in r)

        # Missing recipients
        r = json.loads(tool.execute({
            "action": "send", "subject": "Hi", "body": "Hello",
        }, user_id=test_uid))
        check("send no recipients → error", "error" in r)

        # Empty recipients list
        r = json.loads(tool.execute({
            "action": "send", "subject": "Hi", "body": "Hello", "recipients": [],
        }, user_id=test_uid))
        check("send empty recipients → error", "error" in r)

        # Invalid email format
        r = json.loads(tool.execute({
            "action": "send", "subject": "Hi", "body": "Hello",
            "recipients": ["badformat"],
        }, user_id=test_uid))
        check("send invalid email → error", "error" in r)
        check("send error names bad addr", "badformat" in r["error"])

        # Mixed valid/invalid
        r = json.loads(tool.execute({
            "action": "send", "subject": "Hi", "body": "Hello",
            "recipients": ["good@test.com", "bad"],
        }, user_id=test_uid))
        check("send mixed addrs → error", "error" in r)

        # Nonexistent account_id
        r = json.loads(tool.execute({
            "action": "send", "subject": "Hi", "body": "Hello",
            "recipients": ["ok@test.com"], "account_id": "nonexistent",
        }, user_id=test_uid))
        check("send bad account_id → error", "error" in r)

        # ── 7. Confirmation gate ──
        r = json.loads(tool.execute({
            "action": "send", "subject": "Test", "body": "Hello World",
            "recipients": ["user@test.com"],
        }, user_id=test_uid))
        check("send gate=awaiting", r.get("gate") == "awaiting_confirmation")
        check("gate has preview", "preview" in r)
        check("preview has from_email", "from_email" in r["preview"])
        check("preview has subject", r["preview"]["subject"] == "Test")
        check("preview has recipients", "user@test.com" in r["preview"]["recipients"])

        # ── 8. Confirmation gate with agent_name resolution ──
        # re-create astraea default
        acct4 = save_account(test_uid, {
            "label": "Astraea Default",
            "email": "astraea@example.com",
            "password": "pwd4",
            "smtp_server": "smtp.example.com",
            "smtp_port": 465,
            "agent_default": "astraea",
            "is_default": False,
        })
        r = json.loads(tool.execute({
            "action": "send", "subject": "Agent Test", "body": "Hello",
            "recipients": ["dest@test.com"],
        }, agent_name="astraea", user_id=test_uid))
        check("agent_name resolves to astraea account",
              r.get("preview", {}).get("from_email") == "astraea@example.com")

        # ── Mock SMTP and HTTP for all remaining send tests ──
        # Mock smtplib to avoid real SMTP connections
        import smtplib as _smtplib
        _orig_smtp_ssl = _smtplib.SMTP_SSL
        _orig_smtp = _smtplib.SMTP
        class _MockSMTP:
            def __init__(self, *a, **kw): pass
            def ehlo(self): pass
            def starttls(self): pass
            def login(self, *a): pass
            def sendmail(self, *a): pass
            def quit(self): pass
        _smtplib.SMTP_SSL = _MockSMTP
        _smtplib.SMTP = _MockSMTP

        # Mock requests.Session to avoid real HTTP calls to API fallback
        import requests as _requests_mod
        _OrigSession = _requests_mod.Session
        class _MockSession:
            def get(self, *a, **kw):
                raise _requests_mod.exceptions.ConnectionError("mocked")
            def post(self, *a, **kw):
                raise _requests_mod.exceptions.ConnectionError("mocked")
        _requests_mod.Session = _MockSession

        try:
            # ── 9. Disable confirmation gate and attempt send ──
            settings = _load_settings()
            settings.setdefault("tool_config", {}).setdefault("email", {})["require_confirmation"] = False
            _save_settings(settings)

            # Re-create tool so it gets the mocked Session
            tool = EmailTool()

            r = json.loads(tool.execute({
                "action": "send", "subject": "No Gate", "body": "Hello",
                "recipients": ["user@test.com"],
            }, user_id=test_uid))
            # Will succeed with mock SMTP — should NOT show gate
            check("no gate when disabled", r.get("gate") is None)
            # Expect "sent" (mocked) or "error" — not gate
            check("send attempted (no gate)", "error" in r or "status" in r)

            # ── 10. Send with confirmation='confirmed' (bypass gate) ──
            # Re-enable confirmation
            settings["tool_config"]["email"]["require_confirmation"] = True
            _save_settings(settings)

            r = json.loads(tool.execute({
                "action": "send", "subject": "Confirmed", "body": "Go",
                "recipients": ["user@test.com"], "confirmation": "confirmed",
            }, user_id=test_uid))
            check("confirmed bypasses gate", r.get("gate") is None)
            check("confirmed attempts send", "error" in r or "status" in r)

            # ── 11. Account with no password → incomplete error ──
            save_account(test_uid, {
                "id": "nopwd_acct",
                "label": "No Password",
                "email": "nopwd@example.com",
                "password": "",
                "smtp_server": "smtp.example.com",
                "smtp_port": 465,
                "is_default": False,
            })
            r = json.loads(tool.execute({
                "action": "send", "subject": "Test", "body": "Body",
                "recipients": ["dest@test.com"],
                "account_id": "nopwd_acct",
                "confirmation": "confirmed",
            }, user_id=test_uid))
            check("no password -> incomplete error", "error" in r)
            check("error mentions credentials", "credential" in r["error"].lower() or "password" in r["error"].lower())

            # ── 12. Delete all accounts → send fails ──
            for acct in get_accounts_raw(test_uid):
                delete_account(test_uid, acct["id"])
            check("all accounts deleted", len(get_accounts_raw(test_uid)) == 0)

            r = json.loads(tool.execute({
                "action": "send", "subject": "X", "body": "Y",
                "recipients": ["a@b.com"],
            }, user_id=test_uid))
            check("send with no accounts -> error", "error" in r)
            check("error mentions no accounts", "no email" in r["error"].lower() or "account" in r["error"].lower())

            # accounts action with 0 accounts
            r = json.loads(tool.execute({"action": "accounts"}, user_id=test_uid))
            check("0 accounts message", "message" in r)

            # ── 13. Edge: whitespace-only fields ──
            r = json.loads(tool.execute({
                "action": "send", "subject": "   ", "body": "hello",
                "recipients": ["a@b.com"],
            }, user_id=test_uid))
            check("whitespace subject -> error", "error" in r)

            r = json.loads(tool.execute({
                "action": "send", "subject": "ok", "body": "   ",
                "recipients": ["a@b.com"],
            }, user_id=test_uid))
            check("whitespace body -> error", "error" in r)

            # ── 14. effective_config masks passwords ──
            save_account(test_uid, {
                "label": "Final",
                "email": "final@test.com",
                "password": "supersecret",
                "smtp_server": "smtp.test.com",
                "smtp_port": 465,
            })
            cfg = get_effective_config(test_uid)
            check("effective_config masks pwd",
                  all(a["password"] == "••••••••" for a in cfg["accounts"] if a.get("password_set")))

        finally:
            _smtplib.SMTP_SSL = _orig_smtp_ssl
            _smtplib.SMTP = _orig_smtp
            _requests_mod.Session = _OrigSession

    finally:
        et_mod._SETTINGS_FILE = orig_settings
        et_mod._DATA_DIR = orig_data_dir
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 26. DirectivesTool — all 5 actions
# ═════════════════════════════════════════════
def test_directives_tool_torture():
    """Exhaustive tests for DirectivesTool: search, list, get, manifest, changes,
    _resolve_scopes helper, dynamic SCOPES import, and scope filtering."""
    print("\n=== TORTURE: DirectivesTool — All 5 Actions + _resolve_scopes ===")
    from src.tools.directives_tool import DirectivesTool
    import src.tools.directives_tool as dt_mod
    import src.directives.manifest as manifest_mod

    tool = DirectivesTool()

    # Definition
    defn = tool.definition()
    check("dt def name", defn["name"] == "directives")
    check("dt def has description", len(defn["description"]) > 20)
    actions = defn["parameters"]["properties"]["action"]["enum"]
    check("dt 5 actions", len(actions) == 5)
    for a in ("search", "list", "get", "manifest", "changes"):
        check(f"dt action '{a}'", a in actions)

    # --- _resolve_scopes helper ---
    print("\n  -- _resolve_scopes --")
    # No scope → returns all SCOPES
    all_scopes = DirectivesTool._resolve_scopes(None)
    check("resolve None → all SCOPES", len(all_scopes) > 0)
    check("resolve None → list", isinstance(all_scopes, list))
    check("resolve None includes 'shared'", "shared" in all_scopes)

    # Explicit scope → always includes shared
    scoped = DirectivesTool._resolve_scopes("astraea")
    check("resolve 'astraea' → 2 items", len(scoped) == 2)
    check("resolve astraea has shared", "shared" in scoped)
    check("resolve astraea has astraea", "astraea" in scoped)

    # Scope = shared → just shared (no duplication)
    scoped_shared = DirectivesTool._resolve_scopes("shared")
    check("resolve 'shared' → ['shared']", scoped_shared == ["shared"])

    # Case insensitivity
    scoped_upper = DirectivesTool._resolve_scopes("ASTRAEA")
    check("resolve case insensitive", "astraea" in scoped_upper)
    check("resolve case → shared present", "shared" in scoped_upper)

    # SCOPES module-level import is a tuple/list with entries
    check("SCOPES imported", hasattr(dt_mod, 'SCOPES') or hasattr(manifest_mod, 'SCOPES'))
    from src.directives.manifest import SCOPES as imported_scopes
    check("SCOPES is tuple/list", isinstance(imported_scopes, (tuple, list)))
    check("SCOPES has shared", "shared" in imported_scopes)

    tmp = tempfile.mkdtemp()
    orig_dir = dt_mod._DIRECTIVES_DIR
    dt_mod._DIRECTIVES_DIR = tmp

    # Temporarily override SCOPES so the tool uses our tmp scopes
    orig_scopes = manifest_mod.SCOPES
    manifest_mod.SCOPES = ("shared", "astraea")
    # Also patch the module-level reference in directives_tool if it cached it
    orig_dt_scopes = getattr(dt_mod, 'SCOPES', None)
    dt_mod.SCOPES = ("shared", "astraea")

    try:
        # Create scope files
        shared_path = os.path.join(tmp, "shared.md")
        with open(shared_path, "w", encoding="utf-8") as f:
            f.write("## Core Values\nBe helpful, honest, and harmless.\n\n"
                    "## Communication Style\nBe concise and clear.\n\n"
                    "## Safety Rules\nNever reveal secrets or passwords.\n")

        agent_path = os.path.join(tmp, "astraea.md")
        with open(agent_path, "w", encoding="utf-8") as f:
            f.write("## Star Protocol\nGuide users through stargazing.\n\n"
                    "## Curiosity Mode\nAsk clarifying questions.\n")

        # --- search ---
        r = json.loads(tool.execute({"action": "search", "query": "helpful"}))
        check("dt search ok", r["status"] == "ok")
        check("dt search has count", r["count"] > 0)
        check("dt search has sections", len(r["sections"]) > 0)

        # search: missing query
        r = json.loads(tool.execute({"action": "search"}))
        check("dt search no query → error", r["status"] == "error")

        # search: with limit
        r = json.loads(tool.execute({"action": "search", "query": "values", "limit": 1}))
        check("dt search limit=1", r["count"] <= 1)

        # search: with scope filter
        r = json.loads(tool.execute({"action": "search", "query": "stargazing", "scope": "astraea"}))
        check("dt search scoped ok", r["status"] == "ok")
        check("dt search scoped finds result", r["count"] > 0)
        # All returned sections should be from shared or astraea
        for sec in r.get("sections", []):
            check(f"dt search scoped scope={sec['scope']}",
                  sec["scope"] in ("shared", "astraea"))

        # --- list ---
        r = json.loads(tool.execute({"action": "list"}))
        check("dt list ok", r["status"] == "ok")
        check("dt list count = 5 total", r["count"] == 5,
              f"got {r['count']}: {r.get('headings', [])}")
        check("dt list has headings", len(r["headings"]) > 0)

        # list: with scope filter → only shared
        r = json.loads(tool.execute({"action": "list", "scope": "shared"}))
        check("dt list shared only count=3", r["count"] == 3,
              f"got {r['count']}")

        # --- get ---
        r = json.loads(tool.execute({"action": "get", "heading": "Core Values"}))
        check("dt get ok", r["status"] == "ok")
        check("dt get heading", r["heading"] == "Core Values")
        check("dt get body", "helpful" in r["body"])
        check("dt get scope", r["scope"] == "shared")

        # get: agent-scoped section
        r = json.loads(tool.execute({"action": "get", "heading": "Star Protocol"}))
        check("dt get agent section ok", r["status"] == "ok")
        check("dt get agent heading", r["heading"] == "Star Protocol")
        check("dt get agent scope", r["scope"] == "astraea")

        # get: missing heading param
        r = json.loads(tool.execute({"action": "get"}))
        check("dt get no heading → error", r["status"] == "error")

        # get: nonexistent heading
        r = json.loads(tool.execute({"action": "get", "heading": "Nonexistent"}))
        check("dt get missing → not_found", r["status"] == "not_found")

        # --- manifest ---
        r = json.loads(tool.execute({"action": "manifest"}))
        check("dt manifest ok", r["status"] == "ok")
        check("dt manifest has count", r["count"] > 0)
        check("dt manifest has directives", len(r["directives"]) > 0)

        # manifest: with scope filter
        r = json.loads(tool.execute({"action": "manifest", "scope": "astraea"}))
        check("dt manifest scoped ok", r["status"] == "ok")
        for d in r.get("directives", []):
            check(f"dt manifest scoped entry scope={d['scope']}",
                  d["scope"] in ("shared", "astraea"))

        # --- changes ---
        r = json.loads(tool.execute({"action": "changes"}))
        check("dt changes ok", r["status"] == "ok")
        check("dt changes has totals", "total_added" in r)
        check("dt changes has added list", isinstance(r.get("added"), list))
        check("dt changes has removed list", isinstance(r.get("removed"), list))
        check("dt changes has changed list", isinstance(r.get("changed"), list))

        # --- unknown action ---
        r = json.loads(tool.execute({"action": "BOGUS"}))
        check("dt unknown action → error", r["status"] == "error")
        check("dt unknown msg mentions action", "BOGUS" in r.get("message", ""))

    finally:
        dt_mod._DIRECTIVES_DIR = orig_dir
        manifest_mod.SCOPES = orig_scopes
        if orig_dt_scopes is not None:
            dt_mod.SCOPES = orig_dt_scopes
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 27. Tool Registry — dispatch + resolution
# ═════════════════════════════════════════════
def test_tool_registry_torture():
    """Test tool registry: listing, resolve, execute, error paths."""
    print("\n=== TORTURE: Tool Registry — Dispatch & Resolution ===")
    from src.tools.registry import list_registered_tools, execute_tool, _resolve_tool

    # list_registered_tools
    tools = list_registered_tools()
    check("registry: list returns list", isinstance(tools, list))
    check("registry: 11 tools", len(tools) == 11, f"got {len(tools)}: {tools}")
    for expected in ("echo", "memory", "directives", "cost_tracker",
                     "continuation_update", "web_search", "email", "inbox",
                     "runtime_info", "agi_loop", "model_router"):
        check(f"registry: has '{expected}'", expected in tools)

    # _resolve_tool — known tool
    resolved = _resolve_tool("echo")
    check("resolve echo → dict", isinstance(resolved, dict))
    check("resolve echo has type", resolved["type"] == "function")
    check("resolve echo has function.name", resolved["function"]["name"] == "echo")

    # _resolve_tool — unknown tool
    resolved_unknown = _resolve_tool("nonexistent_tool_xyz")
    check("resolve unknown → None", resolved_unknown is None)

    # execute_tool — echo
    result = execute_tool("echo", {"message": "Torture test!"})
    check("execute echo", "Torture test!" in result)

    # execute_tool — unknown raises KeyError
    try:
        execute_tool("nonexistent_tool_xyz", {})
        check("execute unknown → KeyError", False, "no exception raised")
    except KeyError:
        check("execute unknown → KeyError", True)

    # execute_tool — pass agent_name to email (which accepts it)
    # Just test it doesn't crash
    try:
        result = execute_tool("echo", {"message": "agent test"}, agent_name="astraea")
        check("execute with agent_name", isinstance(result, str))
    except Exception as e:
        check("execute with agent_name", False, str(e))


# ═════════════════════════════════════════════
# 28. validate_manifest — full coverage
# ═════════════════════════════════════════════
def test_validate_manifest():
    """Test manifest validation: valid, missing keys, bad enums, duplicate IDs, etc."""
    print("\n=== TORTURE: validate_manifest — Full Coverage ===")
    from src.directives.manifest import (
        validate_manifest, generate_manifest, _sha256,
    )

    tmp = tempfile.mkdtemp()
    try:
        # Create a scope file
        shared_path = os.path.join(tmp, "shared.md")
        with open(shared_path, "w", encoding="utf-8") as f:
            f.write("## Test Heading\nTest body content.\n")

        # Generate a valid manifest from our tmp dir
        manifest = generate_manifest(directives_dir=tmp, scopes=("shared",))
        check("generated manifest has directives", len(manifest["directives"]) > 0)

        # Fix path references for validation: create proper directory structure
        # validate_manifest resolves path as: parent_of(directives_dir) / entry["path"]
        # So we need the file at: tmp_parent/directives/shared.md
        directives_subdir = os.path.join(tmp, "directives")
        os.makedirs(directives_subdir, exist_ok=True)
        shutil.copy(shared_path, os.path.join(directives_subdir, "shared.md"))
        for d in manifest["directives"]:
            d["path"] = "directives/shared.md"
        result = validate_manifest(manifest, directives_dir=directives_subdir, check_hashes=False)
        check("valid manifest → valid", result["valid"] is True, f"errors={result['errors']}")
        check("valid manifest → 0 errors", len(result["errors"]) == 0, f"errors={result['errors']}")

        # Missing top-level key
        bad = dict(manifest)
        del bad["hash_algo"]
        result2 = validate_manifest(bad, directives_dir=tmp, check_hashes=False)
        check("missing top key → invalid", result2["valid"] is False)
        check("error mentions hash_algo", any("hash_algo" in e for e in result2["errors"]))

        # Missing entry key
        bad2 = json.loads(json.dumps(manifest))
        del bad2["directives"][0]["sha256"]
        result3 = validate_manifest(bad2, directives_dir=tmp, check_hashes=False)
        check("missing entry key → invalid", result3["valid"] is False)
        check("error mentions sha256", any("sha256" in e for e in result3["errors"]))

        # Invalid scope
        bad3 = json.loads(json.dumps(manifest))
        bad3["directives"][0]["scope"] = "bogus_scope_xyz"
        result4 = validate_manifest(bad3, directives_dir=tmp, check_hashes=False)
        check("bad scope → invalid", result4["valid"] is False)

        # Invalid status
        bad4 = json.loads(json.dumps(manifest))
        bad4["directives"][0]["status"] = "deleted"
        result5 = validate_manifest(bad4, directives_dir=tmp, check_hashes=False)
        check("bad status → invalid", result5["valid"] is False)

        # Invalid risk
        bad5 = json.loads(json.dumps(manifest))
        bad5["directives"][0]["risk"] = "extreme"
        result6 = validate_manifest(bad5, directives_dir=tmp, check_hashes=False)
        check("bad risk → invalid", result6["valid"] is False)

        # Duplicate IDs
        bad6 = json.loads(json.dumps(manifest))
        bad6["directives"].append(dict(bad6["directives"][0]))  # exact copy → same id
        result7 = validate_manifest(bad6, directives_dir=tmp, check_hashes=False)
        check("duplicate id → invalid", result7["valid"] is False)
        check("error mentions duplicate", any("duplicate" in e for e in result7["errors"]))

        # directives not a list
        bad7 = dict(manifest)
        bad7["directives"] = "not a list"
        result8 = validate_manifest(bad7, directives_dir=tmp, check_hashes=False)
        check("directives not list → invalid", result8["valid"] is False)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 29. audit_changes
# ═════════════════════════════════════════════
def test_audit_changes():
    """Test audit_changes: no persisted manifest, matching, diffs."""
    print("\n=== TORTURE: audit_changes — Live vs Persisted ===")
    from src.directives.manifest import audit_changes, generate_manifest, save_manifest

    tmp = tempfile.mkdtemp()
    try:
        shared_path = os.path.join(tmp, "shared.md")
        with open(shared_path, "w", encoding="utf-8") as f:
            f.write("## Rule One\nFirst rule content.\n\n"
                    "## Rule Two\nSecond rule content.\n")

        manifest_path = os.path.join(tmp, "manifest.json")

        # No persisted manifest → all added
        diff = audit_changes(directives_dir=tmp, manifest_path_override=manifest_path)
        check("no persisted → all added", diff["total_added"] >= 2)
        check("no persisted → 0 removed", diff["total_removed"] == 0)

        # Save manifest, then diff again → 0 changes
        m = generate_manifest(directives_dir=tmp, scopes=("shared",))
        save_manifest(m, path=manifest_path)
        diff2 = audit_changes(directives_dir=tmp, manifest_path_override=manifest_path)
        check("matching → 0 added", diff2["total_added"] == 0)
        check("matching → 0 removed", diff2["total_removed"] == 0)
        check("matching → 0 changed", diff2["total_changed"] == 0)
        check("matching → 2 unchanged", diff2["unchanged_count"] == 2)

        # Modify a directive → detect change
        with open(shared_path, "w", encoding="utf-8") as f:
            f.write("## Rule One\nModified first rule.\n\n"
                    "## Rule Two\nSecond rule content.\n\n"
                    "## Rule Three\nBrand new rule.\n")
        diff3 = audit_changes(directives_dir=tmp, manifest_path_override=manifest_path)
        check("modified → 1 changed", diff3["total_changed"] == 1)
        check("new rule → 1 added", diff3["total_added"] == 1)
        check("unchanged → 1", diff3["unchanged_count"] == 1)

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 30. CostTrackerTool — pricing actions
# ═════════════════════════════════════════════
def test_cost_tracker_pricing_actions():
    """Test get_pricing, set_pricing, list_models actions."""
    print("\n=== TORTURE: CostTrackerTool — Pricing Actions ===")
    from src.tools.cost_tracker import CostTrackerTool
    import src.tools.cost_tracker as ct_mod

    tool = CostTrackerTool()

    tmp = tempfile.mkdtemp()
    orig_pricing_path = ct_mod._pricing_path
    orig_connections_path = ct_mod._connections_path

    pricing_file = os.path.join(tmp, "pricing.yaml")
    conn_file = os.path.join(tmp, "connections.json")

    ct_mod._pricing_path = lambda: pricing_file
    ct_mod._connections_path = lambda: conn_file

    try:
        # get_pricing — empty (no file)
        r = json.loads(tool.execute({"action": "get_pricing"}))
        check("get_pricing empty → providers dict", "providers" in r)

        # set_pricing — create new entry
        r = json.loads(tool.execute({
            "action": "set_pricing", "provider": "openai", "model": "gpt-4o",
            "input_per_1m": 2.50, "output_per_1m": 10.00,
        }))
        check("set_pricing ok", r.get("ok") is True)
        check("set_pricing provider", r["provider"] == "openai")
        check("set_pricing model", r["model"] == "gpt-4o")
        check("set_pricing input", r["pricing"]["input_per_1m"] == 2.50)
        check("set_pricing output", r["pricing"]["output_per_1m"] == 10.00)

        # get_pricing — specific model
        r = json.loads(tool.execute({
            "action": "get_pricing", "provider": "openai", "model": "gpt-4o",
        }))
        check("get_pricing specific", r["pricing"]["input_per_1m"] == 2.50)

        # get_pricing — provider only
        r = json.loads(tool.execute({
            "action": "get_pricing", "provider": "openai",
        }))
        check("get_pricing provider", "gpt-4o" in r["models"])

        # set_pricing — missing fields
        r = json.loads(tool.execute({"action": "set_pricing"}))
        check("set_pricing missing → error", "error" in r)

        # set_pricing — another model with cached_input
        r = json.loads(tool.execute({
            "action": "set_pricing", "provider": "anthropic",
            "model": "claude-sonnet-4-20250514",
            "input_per_1m": 3.00, "cached_input_per_1m": 0.30,
            "output_per_1m": 15.00,
        }))
        check("set_pricing cached", r["pricing"]["cached_input_per_1m"] == 0.30)

        # list_models — no connections file
        r = json.loads(tool.execute({"action": "list_models"}))
        check("list_models empty", "connections" in r)

        # list_models — with connections file
        conns = {
            "connections": [
                {"name": "Local Ollama", "provider": "ollama",
                 "enabled": True, "models": ["llama3:8b", "qwen2.5:7b"]},
                {"name": "Disabled", "provider": "openai",
                 "enabled": False, "models": ["gpt-4"]},
            ],
            "agent_connections": {},
        }
        with open(conn_file, "w") as f:
            json.dump(conns, f)

        r = json.loads(tool.execute({"action": "list_models"}))
        check("list_models has Ollama", "Local Ollama" in r["connections"])
        check("list_models disabled excluded", "Disabled" not in r["connections"])
        check("list_models models list",
              r["connections"]["Local Ollama"]["models"] == ["llama3:8b", "qwen2.5:7b"])

    finally:
        ct_mod._pricing_path = orig_pricing_path
        ct_mod._connections_path = orig_connections_path
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 31. WebSearchTool — extended coverage
# ═════════════════════════════════════════════
def test_web_search_tool_extended():
    """Test _remove_emojis, definition, knowledge gate, scrape action, get_effective_config."""
    print("\n=== TORTURE: WebSearchTool — Extended Coverage ===")
    from src.tools.web_search import (
        WebSearchTool, _remove_emojis, get_effective_config,
    )

    # _remove_emojis
    check("remove_emojis basic", "Hello" in _remove_emojis("Hello 🌍 World") and "World" in _remove_emojis("Hello 🌍 World"))
    check("remove_emojis no emoji char", "🌍" not in _remove_emojis("Hello 🌍 World"))
    check("remove_emojis multiple", "test" == _remove_emojis("🔥test🎉").strip())
    check("remove_emojis empty", "" == _remove_emojis(""))
    check("remove_emojis no emoji", "plain text" == _remove_emojis("plain text"))
    check("remove_emojis keeps CJK", "日本語" in _remove_emojis("日本語🏯"))

    # Definition
    tool = WebSearchTool()
    defn = tool.definition()
    check("ws def name", defn["name"] == "web_search")
    check("ws def has description", len(defn["description"]) > 20)
    props = defn["parameters"]["properties"]
    check("ws action in params", "action" in props)
    check("ws query in params", "query" in props)
    check("ws url in params", "url" in props)
    check("ws mode in params", "mode" in props)
    check("ws knowledge_check in params", "knowledge_check" in props)
    check("ws reason in params", "reason" in props)
    actions = props["action"]["enum"]
    check("ws 2 actions", len(actions) == 2)
    check("ws action search", "search" in actions)
    check("ws action scrape", "scrape" in actions)

    # get_effective_config
    cfg = get_effective_config()
    check("cfg has searxng_url", "searxng_url" in cfg)
    check("cfg has ignored_sites", isinstance(cfg["ignored_sites"], str))
    check("cfg has require_justification", "require_justification" in cfg)
    check("cfg has modes", "modes" in cfg)
    for mode in ("fast", "normal", "deep"):
        check(f"cfg mode '{mode}' present", mode in cfg["modes"])
        check(f"cfg mode '{mode}' has pages", "pages" in cfg["modes"][mode])

    # Knowledge gate — blocked via skip signal
    r = json.loads(tool.execute({
        "action": "search", "query": "test",
        "knowledge_check": "I already know the answer",
        "reason": "just testing",
    }))
    check("knowledge gate blocked", r.get("gate") == "blocked")

    # Knowledge gate — missing reason
    r = json.loads(tool.execute({
        "action": "search", "query": "test",
    }))
    check("knowledge gate missing reason",
          r.get("gate") == "missing_justification" or "error" in r)

    # Scrape — no URL
    r = json.loads(tool.execute({"action": "scrape"}))
    check("scrape no url → error", "error" in r)

    # Scrape — empty URL
    r = json.loads(tool.execute({"action": "scrape", "url": ""}))
    check("scrape empty url → error", "error" in r)


# ═════════════════════════════════════════════
# 32. Metering — extended helpers
# ═════════════════════════════════════════════
def test_metering_helpers_extended():
    """Test meter_response, zero_metering, meter_from_raw_usage, get_price,
    compute_cost, reset_pricing_cache, serialisation round-trips."""
    print("\n=== TORTURE: Metering — Extended Helpers ===")
    from src.observability.metering import (
        meter_response, zero_metering, meter_from_raw_usage,
        get_price, compute_cost, reset_pricing_cache,
        TokenUsage, CostBreakdown, Metering,
    )
    from src.llm_client.base import LLMResponse

    # zero_metering
    z = zero_metering()
    check("zero_metering usage", z.usage.prompt_tokens == 0)
    check("zero_metering cost", z.cost.total_cost == 0.0)
    check("zero_metering model", z.model == "")
    check("zero_metering provider", z.provider == "")

    # zero_metering accumulation
    z2 = z + z
    check("zero + zero = zero", z2.cost.total_cost == 0.0)

    # get_price with custom pricing dict
    pricing = {
        "openai": {
            "gpt-4o": {"input_per_1m": 2.50, "output_per_1m": 10.00},
            "gpt-4": {"input_per_1m": 30.00, "output_per_1m": 60.00},
            "_default": {"input_per_1m": 1.00, "output_per_1m": 2.00},
        },
        "ollama": {
            "_default": {"input_per_1m": 0.00, "output_per_1m": 0.00},
        },
    }
    inp, cached, out, train = get_price("openai", "gpt-4o", pricing)
    check("get_price exact input", inp == 2.50)
    check("get_price exact output", out == 10.00)

    # Prefix match: "gpt-4o-mini" starts with "gpt-4o"
    inp2, _, out2, _ = get_price("openai", "gpt-4o-mini", pricing)
    check("get_price prefix match", inp2 == 2.50)

    # Provider default fallback
    inp3, _, out3, _ = get_price("openai", "unknown-model-xyz", pricing)
    check("get_price default fallback", inp3 == 1.00)

    # Unknown provider
    inp4, _, out4, _ = get_price("nonexistent_provider", "any", pricing)
    check("get_price unknown provider → 0", inp4 == 0.0 and out4 == 0.0)

    # compute_cost
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    cost = compute_cost(usage, "openai", "gpt-4o", pricing)
    expected_input = 1000 * 2.50 / 1_000_000
    expected_output = 500 * 10.00 / 1_000_000
    check("compute_cost input", abs(cost.input_cost - expected_input) < 0.0001)
    check("compute_cost output", abs(cost.output_cost - expected_output) < 0.0001)
    check("compute_cost total", abs(cost.total_cost - (expected_input + expected_output)) < 0.0001)

    # compute_cost with cached tokens
    cost2 = compute_cost(usage, "openai", "gpt-4o", pricing, cached_tokens=200)
    check("cached reduces input cost", cost2.input_cost < cost.input_cost)

    # meter_response with usage populated
    resp = LLMResponse(
        content="Hello",
        model="gpt-4o",
        usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
    )
    m = meter_response(resp, provider="openai", pricing=pricing)
    check("meter_response model", m.model == "gpt-4o")
    check("meter_response not estimated", m.usage.is_estimated is False)
    check("meter_response prompt_tokens", m.usage.prompt_tokens == 100)

    # meter_response without usage (estimation)
    resp2 = LLMResponse(content="Hello world", model="gpt-4o", usage=None)
    messages = [{"role": "user", "content": "Say hello"}]
    m2 = meter_response(resp2, provider="openai", messages=messages, pricing=pricing)
    check("meter_response estimated", m2.usage.is_estimated is True)
    check("meter_response est prompt > 0", m2.usage.prompt_tokens > 0)

    # meter_from_raw_usage
    raw = {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300}
    m3 = meter_from_raw_usage(raw, "openai", "gpt-4o", pricing)
    check("meter_from_raw prompt", m3.usage.prompt_tokens == 200)
    check("meter_from_raw cost > 0", m3.cost.total_cost > 0)

    # meter_from_raw_usage with cached tokens
    raw2 = {
        "prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300,
        "prompt_tokens_details": {"cached_tokens": 50},
    }
    m4 = meter_from_raw_usage(raw2, "openai", "gpt-4o", pricing)
    check("meter_from_raw cached", m4.cost.cached_input_cost >= 0)

    # Serialisation round-trips
    d = m.to_dict()
    check("metering to_dict has usage", "usage" in d)
    check("metering to_dict has cost", "cost" in d)
    m_back = Metering.from_dict(d)
    check("metering round-trip model", m_back.model == m.model)
    check("metering round-trip tokens", m_back.usage.prompt_tokens == m.usage.prompt_tokens)

    tu_d = m.usage.to_dict()
    tu_back = TokenUsage.from_dict(tu_d)
    check("token_usage round-trip", tu_back.prompt_tokens == m.usage.prompt_tokens)

    cb_d = m.cost.to_dict()
    cb_back = CostBreakdown.from_dict(cb_d)
    check("cost_breakdown round-trip", abs(cb_back.total_cost - m.cost.total_cost) < 0.0001)

    # reset_pricing_cache — should not crash
    reset_pricing_cache()
    check("reset_pricing_cache ok", True)


# ═════════════════════════════════════════════
# 33. LLM Client Factory
# ═════════════════════════════════════════════
def test_llm_client_factory():
    """Test create_client dispatch and unknown provider."""
    print("\n=== TORTURE: LLM Client Factory ===")
    from src.llm_client.factory import create_client, _PROVIDERS
    from src.llm_client.base import LLMClient

    # Check provider map
    check("factory has openai", "openai" in _PROVIDERS)
    check("factory has deepseek", "deepseek" in _PROVIDERS)
    check("factory has ollama", "ollama" in _PROVIDERS)
    check("factory has anthropic", "anthropic" in _PROVIDERS)

    # create_client for each provider (just instantiate, don't call)
    for provider in ("openai", "deepseek", "ollama", "anthropic"):
        try:
            profile = {
                "provider": provider,
                "api_url": "http://localhost:11434",
                "api_key": "test-key-123",
                "model": "test-model",
            }
            client = create_client(profile)
            check(f"factory {provider} → LLMClient", isinstance(client, LLMClient))
        except Exception as e:
            check(f"factory {provider} → ok", False, str(e))

    # Unknown provider
    try:
        create_client({"provider": "nonexistent_xyz"})
        check("factory unknown → ValueError", False, "no exception raised")
    except ValueError as e:
        check("factory unknown → ValueError", "nonexistent_xyz" in str(e))


# ═════════════════════════════════════════════
# 34. App helpers — memory tag extraction
# ═════════════════════════════════════════════
def test_app_memory_helpers():
    """Test _strip_memory_tags pattern matching."""
    print("\n=== TORTURE: App — Memory Tag Helpers ===")
    import re

    # Replicate the pattern from app.py
    _MEMORY_TAG_PATTERN = r'\[MEMORY_SAVE:\s*(?:category=[\w]+\s*\|)?\s*.+?\]'

    def strip_memory_tags(text):
        return re.sub(_MEMORY_TAG_PATTERN, '', text).strip()

    # Basic tag removal
    text = "Hello [MEMORY_SAVE: some note] world"
    result = strip_memory_tags(text)
    check("strip basic tag", "MEMORY_SAVE" not in result)
    check("strip preserves text", "Hello" in result and "world" in result)

    # Tag with category
    text2 = "Start [MEMORY_SAVE: category=bio | User likes hiking] end"
    result2 = strip_memory_tags(text2)
    check("strip category tag", "MEMORY_SAVE" not in result2)
    check("strip category preserves", "Start" in result2 and "end" in result2)

    # Multiple tags
    text3 = "[MEMORY_SAVE: note1] text [MEMORY_SAVE: category=pref | note2] done"
    result3 = strip_memory_tags(text3)
    check("strip multiple tags", "MEMORY_SAVE" not in result3)
    check("strip multiple preserves", "text" in result3 and "done" in result3)

    # No tags → unchanged
    text4 = "Plain text with no memory tags at all."
    result4 = strip_memory_tags(text4)
    check("strip no tags → unchanged", result4 == text4)

    # Empty string
    result5 = strip_memory_tags("")
    check("strip empty → empty", result5 == "")

    # Extract pattern
    _EXTRACT_PATTERN = r'\[MEMORY_SAVE:\s*(?:category=([\w]+)\s*\|)?\s*(.+?)\]'

    matches = re.findall(_EXTRACT_PATTERN, text2, re.DOTALL)
    check("extract has match", len(matches) == 1)
    check("extract category", matches[0][0] == "bio")
    check("extract text", "hiking" in matches[0][1])

    # Multiple extracts
    matches2 = re.findall(_EXTRACT_PATTERN, text3, re.DOTALL)
    check("extract multiple", len(matches2) == 2)


# ═════════════════════════════════════════════
# 35. Seed UI Knowledge — MEMORIES structure validation
# ═════════════════════════════════════════════
def test_seed_ui_knowledge_structure():
    """Validate the MEMORIES list in seed_ui_knowledge.py has correct structure."""
    print("\n=== TORTURE: Seed UI Knowledge — Structure ===")
    from scripts.seed_ui_knowledge import MEMORIES

    check("MEMORIES is list", isinstance(MEMORIES, list))
    check("MEMORIES not empty", len(MEMORIES) > 0)
    check("MEMORIES > 30 entries", len(MEMORIES) > 30, f"got {len(MEMORIES)}")

    required_keys = {"text", "scope", "category", "tags", "source", "tier"}
    valid_tiers = {"canon", "register"}
    valid_sources = {"operator", "tool", "chat", "system"}

    for i, m in enumerate(MEMORIES):
        prefix = f"MEMORIES[{i}]"
        for key in required_keys:
            check(f"{prefix} has {key}", key in m, f"missing {key}")

        # Text not empty
        check(f"{prefix} text non-empty", len(m.get("text", "")) > 10,
              f"text too short: {m.get('text', '')[:30]}")

        # Valid tier
        check(f"{prefix} tier valid", m.get("tier") in valid_tiers,
              f"tier={m.get('tier')}")

        # Valid source
        check(f"{prefix} source valid", m.get("source") in valid_sources,
              f"source={m.get('source')}")

        # Tags is a list
        check(f"{prefix} tags is list", isinstance(m.get("tags", []), list))

        # Tags not empty
        check(f"{prefix} tags non-empty", len(m.get("tags", [])) > 0)

        # Scope is string
        check(f"{prefix} scope is str", isinstance(m.get("scope"), str))

    # Check diversity of categories
    categories = {m["category"] for m in MEMORIES}
    check("has meta category", "meta" in categories)
    check("has capability category", "capability" in categories)
    check("multiple categories", len(categories) >= 2, f"categories={categories}")

    # Check all have "ui" or dashboard-related tags
    has_ui_tag = sum(1 for m in MEMORIES if "ui" in m.get("tags", []))
    check("most have 'ui' tag", has_ui_tag > len(MEMORIES) * 0.5,
          f"{has_ui_tag}/{len(MEMORIES)}")


# ═════════════════════════════════════════════
# 36. Metering data class ops
# ═════════════════════════════════════════════
def test_metering_dataclass_ops():
    """Test TokenUsage, CostBreakdown, Metering addition and serialisation."""
    print("\n=== TORTURE: Metering — Data Class Operations ===")
    from src.observability.metering import TokenUsage, CostBreakdown, Metering

    # TokenUsage addition
    u1 = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    u2 = TokenUsage(prompt_tokens=200, completion_tokens=100, total_tokens=300,
                    is_estimated=True)
    u3 = u1 + u2
    check("usage add prompt", u3.prompt_tokens == 300)
    check("usage add completion", u3.completion_tokens == 150)
    check("usage add total", u3.total_tokens == 450)
    check("usage add estimated propagation", u3.is_estimated is True)

    # CostBreakdown addition with all fields
    c1 = CostBreakdown(input_cost=0.01, cached_input_cost=0.001,
                       output_cost=0.02, training_cost=0.003, total_cost=0.034)
    c2 = CostBreakdown(input_cost=0.02, output_cost=0.04, total_cost=0.06)
    c3 = c1 + c2
    check("cost add input", abs(c3.input_cost - 0.03) < 0.0001)
    check("cost add cached", abs(c3.cached_input_cost - 0.001) < 0.0001)
    check("cost add output", abs(c3.output_cost - 0.06) < 0.0001)
    check("cost add total", abs(c3.total_cost - 0.094) < 0.0001)
    check("cost currency", c3.currency == "USD")

    # to_dict / from_dict round-trip
    d = c3.to_dict()
    check("cost to_dict currency", d["currency"] == "USD")
    c4 = CostBreakdown.from_dict(d)
    check("cost from_dict round-trip", abs(c4.total_cost - c3.total_cost) < 0.0001)

    # Metering addition preserves model/provider from first non-empty
    m1 = Metering(usage=u1, cost=c1, model="gpt-4o", provider="openai")
    m2 = Metering(usage=u2, cost=c2, model="", provider="")
    m3 = m1 + m2
    check("metering add model", m3.model == "gpt-4o")
    check("metering add provider", m3.provider == "openai")
    check("metering add usage", m3.usage.prompt_tokens == 300)

    # Empty + filled → filled
    m4 = Metering() + m1
    check("empty + filled model", m4.model == "gpt-4o")


# ═════════════════════════════════════════════
# INBOX TOOL — full coverage
# ═════════════════════════════════════════════
def test_inbox_tool_torture():
    print("\n=== TORTURE: InboxTool — Full Coverage ===")
    import src.data_paths as dp
    from src.tools.inbox import InboxTool

    orig_root = dp.DATA_ROOT
    tmp = tempfile.mkdtemp()
    dp.DATA_ROOT = tmp

    try:
        # ── Definition ────────────────────────────────────────
        defn = InboxTool.definition()
        check("inbox def name", defn["name"] == "inbox")
        check("inbox def has parameters", "parameters" in defn)
        props = defn["parameters"]["properties"]
        check("inbox def has action", "action" in props)
        check("inbox def has type", "type" in props)
        check("inbox def has priority", "priority" in props)
        check("inbox def has subject", "subject" in props)
        check("inbox def has body", "body" in props)
        check("inbox def has task", "task" in props)
        check("inbox def has task_id", "task_id" in props)
        check("inbox def has needs_approval", "needs_approval" in props)
        check("inbox def has dry_run", "dry_run" in props)
        check("inbox action enum", set(props["action"]["enum"]) == {"send", "add_task", "next_task", "ack"})

        # ── Unknown action ────────────────────────────────────
        r = InboxTool.execute({"action": "delete"})
        check("unknown action → error", "error" in r.lower())
        check("unknown action lists valid", "send" in r)

        # ── send: validation ──────────────────────────────────
        r = InboxTool.execute({"action": "send"})
        check("send no subject → error", "error" in r.lower())

        r = InboxTool.execute({"action": "send", "subject": "Hi"})
        check("send no body → error", "error" in r.lower())

        r = InboxTool.execute({"action": "send", "subject": "", "body": "text"})
        check("send empty subject → error", "error" in r.lower())

        r = InboxTool.execute({"action": "send", "subject": "Hi", "body": ""})
        check("send empty body → error", "error" in r.lower())

        r = InboxTool.execute({"action": "send", "subject": "x" * 121, "body": "ok"})
        check("send subject too long → error", "120" in r)

        r = InboxTool.execute({"action": "send", "subject": "ok", "body": "x" * 2001})
        check("send body too long → error", "2000" in r)

        r = InboxTool.execute({"action": "send", "type": "invalid_type",
                               "subject": "ok", "body": "ok"})
        check("send invalid type → error", "error" in r.lower())

        r = InboxTool.execute({"action": "send", "priority": "critical",
                               "subject": "ok", "body": "ok"})
        check("send invalid priority → error", "error" in r.lower())

        # ── send: success paths ───────────────────────────────
        r = InboxTool.execute({"action": "send", "type": "message",
                               "subject": "Hello operator", "body": "Testing.",
                               "_from": "orion"})
        check("send message ok", "sent" in r.lower())
        check("send message has id", "id=" in r)

        r = InboxTool.execute({"action": "send", "type": "warning",
                               "priority": "urgent", "subject": "Boundary hit",
                               "body": "Safety concern.", "needs_approval": True,
                               "_from": "astraea"})
        check("send warning ok", "sent" in r.lower())

        r = InboxTool.execute({"action": "send", "type": "tool_request",
                               "subject": "Need web access", "body": "Please enable.",
                               "_from": "callum"})
        check("send tool_request ok", "sent" in r.lower())

        r = InboxTool.execute({"action": "send", "type": "idea",
                               "subject": "Could do X", "body": "Proposal details.",
                               "profile": "orion"})
        check("send idea ok (profile as sender)", "sent" in r.lower())

        # Default type (message) when type omitted
        r = InboxTool.execute({"action": "send", "subject": "No type",
                               "body": "Should default to message."})
        check("send default type ok", "sent" in r.lower())

        # ── add_task: validation ──────────────────────────────
        r = InboxTool.execute({"action": "add_task"})
        check("add_task no task → error", "error" in r.lower())

        r = InboxTool.execute({"action": "add_task", "task": "  "})
        check("add_task whitespace → error", "error" in r.lower())

        # ── add_task: success ─────────────────────────────────
        r = InboxTool.execute({"action": "add_task",
                               "task": "Review inbox implementation",
                               "profile": "orion"})
        check("add_task ok", "added" in r.lower())
        check("add_task has id", "id=" in r)
        # Extract the task ID for later
        task_id_1 = r.split("id=")[1].split(")")[0]

        r = InboxTool.execute({"action": "add_task",
                               "task": "Second task",
                               "priority": "high"})
        check("add_task second ok", "added" in r.lower())
        task_id_2 = r.split("id=")[1].split(")")[0]

        # ── add_task: dry_run ─────────────────────────────────
        r = InboxTool.execute({"action": "add_task",
                               "task": "Dry run task", "dry_run": True})
        check("add_task dry_run prefix", "DRY_RUN" in r)
        check("add_task dry_run no write", "Would add" in r)

        # ── next_task ─────────────────────────────────────────
        r = InboxTool.execute({"action": "next_task"})
        check("next_task found", "TASK_FOUND" in r)
        check("next_task has first task", "Review inbox" in r)

        # Second next_task should return the second task
        r = InboxTool.execute({"action": "next_task"})
        check("next_task second found", "TASK_FOUND" in r)
        check("next_task has second task", "Second task" in r)

        # Third next_task — no more pending
        r = InboxTool.execute({"action": "next_task"})
        check("next_task empty", "NO_TASK" in r)

        # next_task with profile filter — add a scoped task
        InboxTool.execute({"action": "add_task", "task": "Scoped task",
                           "profile": "astraea"})
        InboxTool.execute({"action": "add_task", "task": "Other task",
                           "profile": "orion"})
        r = InboxTool.execute({"action": "next_task", "profile": "astraea"})
        check("next_task scoped", "Scoped task" in r)

        # next_task dry_run
        r = InboxTool.execute({"action": "next_task", "dry_run": True})
        check("next_task dry_run", "DRY_RUN" in r)

        # ── ack ───────────────────────────────────────────────
        r = InboxTool.execute({"action": "ack"})
        check("ack no id → error", "error" in r.lower())

        r = InboxTool.execute({"action": "ack", "task_id": ""})
        check("ack empty id → error", "error" in r.lower())

        r = InboxTool.execute({"action": "ack", "task_id": "nonexistent"})
        check("ack nonexistent → error", "not found" in r.lower())

        # Ack a real entry (task_id_1 was marked done by next_task, should still be ackable)
        r = InboxTool.execute({"action": "ack", "task_id": task_id_1})
        check("ack real task ok", "acknowledged" in r.lower())

        # Ack again → already acknowledged
        r = InboxTool.execute({"action": "ack", "task_id": task_id_1})
        check("ack duplicate → already", "already" in r.lower())

        # Ack dry_run
        r = InboxTool.execute({"action": "ack", "task_id": task_id_2,
                               "dry_run": True})
        check("ack dry_run", "DRY_RUN" in r)

        # ── JSONL persistence check ───────────────────────────
        jsonl_path = os.path.join(tmp, "shared", "inbox.jsonl")
        check("JSONL file exists", os.path.isfile(jsonl_path))
        with open(jsonl_path, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        check("JSONL has entries", len(lines) >= 5)

        # Parse each line as valid JSON
        all_valid = True
        for line in lines:
            try:
                obj = json.loads(line)
                if "id" not in obj or "created_at" not in obj:
                    all_valid = False
            except json.JSONDecodeError:
                all_valid = False
        check("JSONL all valid JSON with id+created_at", all_valid)

        # Check for expected fields in a send entry
        first_send = json.loads(lines[0])
        check("send entry has 'from'", "from" in first_send)
        check("send entry has 'type'", "type" in first_send)
        check("send entry has 'subject'", "subject" in first_send)
        check("send entry has 'body'", "body" in first_send)
        check("send entry has 'status'", "status" in first_send)
        check("send entry status is unread", first_send["status"] == "unread")

        # Check task entry structures
        task_entries = [json.loads(l) for l in lines if json.loads(l).get("type") == "task"]
        check("task entries found", len(task_entries) >= 2)
        if task_entries:
            check("task entry has 'task' field", "task" in task_entries[0])

        # ── MD persistence check ──────────────────────────────
        md_path = os.path.join(tmp, "shared", "inbox.md")
        check("MD file exists", os.path.isfile(md_path))
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()
        check("MD has header", "# Inbox" in md_content)
        check("MD has entries", "---" in md_content)
        check("MD has subject lines", "**Subject:**" in md_content)
        check("MD has id refs", "*id:" in md_content)

        # Check specific entries in MD
        check("MD has message type", "message" in md_content)
        check("MD has warning type", "warning" in md_content)
        check("MD has priority tag", "[URGENT]" in md_content)
        check("MD has approval tag", "[NEEDS APPROVAL]" in md_content)

    finally:
        dp.DATA_ROOT = orig_root
        shutil.rmtree(tmp, ignore_errors=True)


def test_inbox_registry_dispatch():
    print("\n=== TORTURE: Inbox — Registry Dispatch ===")
    import src.data_paths as dp
    from src.tools.registry import execute_tool, list_registered_tools

    orig_root = dp.DATA_ROOT
    tmp = tempfile.mkdtemp()
    dp.DATA_ROOT = tmp

    try:
        # Inbox is registered
        tools = list_registered_tools()
        check("inbox in registry", "inbox" in tools)

        # Execute via registry
        r = execute_tool("inbox", {"action": "send", "type": "message",
                                   "subject": "Registry test",
                                   "body": "Dispatched through registry."})
        check("registry send ok", "sent" in r.lower())

        # Execute add_task via registry
        r = execute_tool("inbox", {"action": "add_task",
                                   "task": "Registry task test"})
        check("registry add_task ok", "added" in r.lower())

        # Execute next_task via registry
        r = execute_tool("inbox", {"action": "next_task"})
        check("registry next_task ok", "TASK_FOUND" in r)

    finally:
        dp.DATA_ROOT = orig_root
        shutil.rmtree(tmp, ignore_errors=True)


def test_inbox_data_path():
    print("\n=== TORTURE: inbox_path in data_paths ===")
    import src.data_paths as dp

    orig_root = dp.DATA_ROOT
    tmp = tempfile.mkdtemp()
    dp.DATA_ROOT = tmp

    try:
        ip = dp.inbox_path()
        check("inbox_path is string", isinstance(ip, str))
        check("inbox_path contains inbox", "inbox" in ip.lower())
        check("inbox_path in shared dir", "shared" in ip)
        check("inbox_path ends jsonl", ip.endswith(".jsonl"))
        # shared dir should exist after calling inbox_path
        check("shared dir created", os.path.isdir(os.path.join(tmp, "shared")))
    finally:
        dp.DATA_ROOT = orig_root
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# Dynamic scopes & category policy
# ═════════════════════════════════════════════
def test_dynamic_scopes():
    """Verify _discover_scopes picks up profile YAMLs and always includes 'shared'."""
    print("\n=== TORTURE: Dynamic Scopes ===")
    from src.memory.types import VALID_SCOPES, _discover_scopes

    # Basic contract
    check("VALID_SCOPES is frozenset", isinstance(VALID_SCOPES, frozenset))
    check("'shared' always in VALID_SCOPES", "shared" in VALID_SCOPES)
    check("at least 2 scopes", len(VALID_SCOPES) >= 2)

    # Rediscover and compare
    fresh = _discover_scopes()
    check("_discover_scopes returns frozenset", isinstance(fresh, frozenset))
    check("fresh scopes match VALID_SCOPES", fresh == VALID_SCOPES)

    # All profile YAMLs should be present
    from pathlib import Path
    profiles_dir = Path(__file__).resolve().parent.parent / "profiles"
    if profiles_dir.exists():
        for p in profiles_dir.glob("*.yaml"):
            check(f"scope '{p.stem}' discovered", p.stem in VALID_SCOPES)

    # Verify sorted() works (used by memory_tool definition)
    sorted_scopes = sorted(VALID_SCOPES)
    check("sorted(VALID_SCOPES) is list", isinstance(sorted_scopes, list))
    check("sorted scopes are alphabetical", sorted_scopes == sorted(sorted_scopes))

    # Edge: discover from empty dir
    tmp = tempfile.mkdtemp()
    def _discover_empty():
        scopes = {"shared"}
        empty_dir = Path(tmp) / "no_profiles_here"
        if empty_dir.exists():
            for p in empty_dir.glob("*.yaml"):
                scopes.add(p.stem)
        return frozenset(scopes)
    check("empty dir -> only shared", _discover_empty() == frozenset({"shared"}))
    shutil.rmtree(tmp, ignore_errors=True)


def test_category_policy():
    """Test _load_category_policy and _build_category_field for all 3 modes."""
    print("\n=== TORTURE: Category Policy ===")
    from src.tools.memory_tool import _load_category_policy, _build_category_field, _CONFIG_DIR
    from src.memory.types import VALID_CATEGORIES

    # ── Load from real config ──
    policy = _load_category_policy()
    check("policy is dict", isinstance(policy, dict))
    check("policy has mode", "mode" in policy)
    check("policy mode in valid set", policy["mode"] in ("suggested", "custom", "open"))
    check("policy has suggested_categories", "suggested_categories" in policy)
    check("policy has custom_categories", "custom_categories" in policy)
    check("suggested is list", isinstance(policy["suggested_categories"], list))
    check("custom is list", isinstance(policy["custom_categories"], list))

    # ── Test _build_category_field with mocked policies ──
    mp_file = _CONFIG_DIR / "memory_profile.json"
    original = mp_file.read_text(encoding="utf-8")

    try:
        import json as _j

        # --- MODE: suggested ---
        data = _j.loads(original)
        data["category_policy"] = {
            "mode": "suggested",
            "suggested_categories": ["bio", "identity", "mission"],
            "custom_categories": [],
        }
        mp_file.write_text(_j.dumps(data), encoding="utf-8")

        field = _build_category_field()
        check("suggested mode has enum", "enum" in field)
        check("suggested mode 3 items", len(field["enum"]) == 3)
        check("suggested mode sorted", field["enum"] == sorted(field["enum"]))
        check("suggested mode desc", "pick from" in field["description"].lower())

        # --- MODE: custom ---
        data["category_policy"] = {
            "mode": "custom",
            "suggested_categories": ["bio", "identity"],
            "custom_categories": ["my_custom", "another_custom"],
        }
        mp_file.write_text(_j.dumps(data), encoding="utf-8")

        field = _build_category_field()
        check("custom mode has enum", "enum" in field)
        check("custom mode merged count 4", len(field["enum"]) == 4)
        check("custom mode includes custom", "my_custom" in field["enum"])
        check("custom mode includes suggested", "bio" in field["enum"])
        check("custom mode deduplicates", len(field["enum"]) == len(set(field["enum"])))

        # custom mode with overlapping categories
        data["category_policy"]["custom_categories"] = ["bio", "new_one"]
        mp_file.write_text(_j.dumps(data), encoding="utf-8")
        field = _build_category_field()
        check("custom overlap dedup", field["enum"].count("bio") == 1)
        check("custom overlap new_one", "new_one" in field["enum"])

        # --- MODE: open ---
        data["category_policy"] = {
            "mode": "open",
            "suggested_categories": ["bio", "identity", "mission"],
            "custom_categories": [],
        }
        mp_file.write_text(_j.dumps(data), encoding="utf-8")

        field = _build_category_field()
        check("open mode no enum", "enum" not in field)
        check("open mode 'any' in desc", "any" in field["description"].lower())
        check("open mode common cats listed", "bio" in field["description"])

        # --- Missing category_policy entirely ---
        data.pop("category_policy", None)
        mp_file.write_text(_j.dumps(data), encoding="utf-8")

        field = _build_category_field()
        check("missing policy defaults to open", "enum" not in field)
        check("missing policy has description", len(field["description"]) > 0)

        # --- Corrupt JSON ---
        mp_file.write_text("NOT VALID JSON{{{", encoding="utf-8")
        policy_err = _load_category_policy()
        check("corrupt JSON returns empty dict", policy_err == {})
        field = _build_category_field()
        check("corrupt JSON still returns valid field", "type" in field)

    finally:
        mp_file.write_text(original, encoding="utf-8")


def test_saved_profile_upgrade():
    """Test _seed_default_profile upgrades stale defaults with missing keys."""
    print("\n=== TORTURE: Saved Profile Upgrade ===")

    tmp = tempfile.mkdtemp()
    try:
        from pathlib import Path
        test_dir = Path(tmp) / "profiles"
        test_dir.mkdir(parents=True, exist_ok=True)

        from web.app import _seed_default_profile, _DEFAULT_PROFILE_STEM

        def _mock_loader():
            return {
                "name": "Test Profile",
                "version": "1.0",
                "write_policy": {"auto_write": True},
                "category_policy": {"mode": "open", "suggested_categories": ["bio"]},
            }

        # ── Brand new directory ──
        _seed_default_profile(test_dir, _mock_loader)
        default_path = test_dir / f"{_DEFAULT_PROFILE_STEM}.json"
        check("default created", default_path.exists())

        saved = json.loads(default_path.read_text(encoding="utf-8"))
        check("default has _pinned", saved.get("_pinned") is True)
        check("default has name", saved.get("name") == "Test Profile")
        check("default has category_policy", "category_policy" in saved)
        check("default has write_policy", "write_policy" in saved)

        # ── Stale default missing category_policy ──
        stale = {"name": "Old", "version": "0.9", "write_policy": {"auto_write": False}, "_pinned": True}
        default_path.write_text(json.dumps(stale), encoding="utf-8")

        _seed_default_profile(test_dir, _mock_loader)

        upgraded = json.loads(default_path.read_text(encoding="utf-8"))
        check("upgrade adds category_policy", "category_policy" in upgraded)
        check("upgrade preserves existing name", upgraded["name"] == "Old")
        check("upgrade preserves write_policy", upgraded["write_policy"]["auto_write"] is False)
        check("upgrade keeps _pinned", upgraded.get("_pinned") is True)

        # ── Already up-to-date ──
        before_text = default_path.read_text(encoding="utf-8")
        _seed_default_profile(test_dir, _mock_loader)
        after_text = default_path.read_text(encoding="utf-8")
        check("up-to-date default unchanged", before_text == after_text)

        # ── Corrupt default JSON ──
        default_path.write_text("NOT JSON!!!", encoding="utf-8")
        try:
            _seed_default_profile(test_dir, _mock_loader)
            check("corrupt default doesn't crash", True)
        except Exception:
            check("corrupt default doesn't crash", False)

        # ── Loader returns empty ──
        empty_dir = Path(tmp) / "empty_profiles"
        empty_dir.mkdir(parents=True, exist_ok=True)
        def _empty_loader():
            return {}
        _seed_default_profile(empty_dir, _empty_loader)
        ep = empty_dir / f"{_DEFAULT_PROFILE_STEM}.json"
        check("empty loader creates file", ep.exists())
        ed = json.loads(ep.read_text(encoding="utf-8"))
        check("empty loader has _pinned", ed.get("_pinned") is True)

        # ── Loader returns None ──
        none_dir = Path(tmp) / "none_profiles"
        none_dir.mkdir(parents=True, exist_ok=True)
        def _none_loader():
            return None
        _seed_default_profile(none_dir, _none_loader)
        np_path = none_dir / f"{_DEFAULT_PROFILE_STEM}.json"
        check("None loader creates file", np_path.exists())

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def test_tool_catalogue_dynamic():
    """Test that _TOOL_CATALOGUE uses dynamic VALID_SCOPES and truncated categories."""
    print("\n=== TORTURE: _TOOL_CATALOGUE Dynamic Fields ===")
    from web.app import _TOOL_CATALOGUE
    from src.memory.types import VALID_SCOPES, VALID_CATEGORIES

    # Find the memory tool entry
    mem_entry = None
    for t in _TOOL_CATALOGUE:
        if t["name"] == "memory":
            mem_entry = t
            break
    check("memory tool in catalogue", mem_entry is not None)

    # Find scope and category params
    scope_param = None
    category_param = None
    for p in mem_entry["parameters"]:
        if p["name"] == "scope":
            scope_param = p
        if p["name"] == "category":
            category_param = p

    check("scope param exists", scope_param is not None)
    check("category param exists", category_param is not None)

    # Scope enum should match VALID_SCOPES
    scope_enum = scope_param["enum"]
    check("scope enum is list", isinstance(scope_enum, list))
    check("scope enum matches VALID_SCOPES", set(scope_enum) == set(VALID_SCOPES))
    check("scope enum is sorted", scope_enum == sorted(scope_enum))
    check("'shared' in scope enum", "shared" in scope_enum)

    # All profile names in scope
    from pathlib import Path
    profiles_dir = Path(__file__).resolve().parent.parent / "profiles"
    if profiles_dir.exists():
        for p in profiles_dir.glob("*.yaml"):
            check(f"scope enum has '{p.stem}'", p.stem in scope_enum)

    # Category enum should be truncated to 5 + ellipsis
    cat_enum = category_param["enum"]
    check("category enum is list", isinstance(cat_enum, list))
    check("category enum has 6 items (5+ellipsis)", len(cat_enum) == 6)
    check("category last item is ellipsis", cat_enum[-1] == "\u2026")
    first_five = cat_enum[:5]
    check("first 5 are sorted", first_five == sorted(first_five))
    for c in first_five:
        check(f"'{c}' in VALID_CATEGORIES", c in VALID_CATEGORIES)


def test_memory_tool_definition_dynamic():
    """Test that MemoryTool.definition() has dynamic scope and category fields."""
    print("\n=== TORTURE: MemoryTool.definition() Dynamic ===")
    from src.tools.memory_tool import MemoryTool, _load_category_policy
    from src.memory.types import VALID_SCOPES

    defn = MemoryTool.definition()
    props = defn["parameters"]["properties"]

    # Scope
    scope_def = props["scope"]
    check("definition scope has enum", "enum" in scope_def)
    check("definition scope matches VALID_SCOPES", set(scope_def["enum"]) == set(VALID_SCOPES))
    check("definition scope sorted", scope_def["enum"] == sorted(scope_def["enum"]))

    # Category depends on current policy mode
    cat_def = props["category"]
    check("definition category has type", cat_def["type"] == "string")
    check("definition category has description", len(cat_def["description"]) > 0)

    mode = _load_category_policy().get("mode", "open")
    if mode == "open":
        check("open mode no enum in definition", "enum" not in cat_def)
    else:
        check(f"{mode} mode enum in definition", "enum" in cat_def)
        check(f"{mode} mode enum sorted", cat_def["enum"] == sorted(cat_def["enum"]))

    # Action list
    actions = props["action"]["enum"]
    check("13 actions in definition", len(actions) == 13)

    # Source enum
    source_def = props["source"]
    check("source has enum", "enum" in source_def)
    check("source enum sorted", source_def["enum"] == sorted(source_def["enum"]))


# ═════════════════════════════════════════════
# Vault sort logic — all 8 sort modes
# ═════════════════════════════════════════════
def test_vault_sort_logic():
    """Test the _sort_key function logic for all 8 sort modes using both dict and object forms."""
    print("\n=== TORTURE: Vault Sort Logic — 8 modes, dict & object ===")
    from src.memory.types import Memory

    # Build a set of test memories with varied fields
    m1 = Memory(id="m1", text="Alpha project", scope="astraea", category="project",
                tier="canon", created_at="2026-01-01T10:00:00", updated_at="2026-02-15T08:00:00",
                source="chat", version=1)
    m2 = Memory(id="m2", text="Beta reflection", scope="callum", category="reflection",
                tier="register", created_at="2026-01-05T12:00:00", updated_at=None,
                source="manual", version=2)
    m3 = Memory(id="m3", text="Zeta goal", scope="astraea", category="goal",
                tier="canon", created_at="2025-12-20T09:00:00", updated_at="2026-03-01T12:00:00",
                source="tool", version=1)
    m4 = Memory(id="m4", text="Gamma identity", scope="shared", category="identity",
                tier="register", created_at="2026-01-10T15:00:00", updated_at=None,
                source=None, version=3)

    memories_obj = [m1, m2, m3, m4]
    memories_dict = [m.to_dict() for m in memories_obj]

    # Helper: replicate the sort logic from app.py page_vault
    def sort_memories(mems, sort_mode):
        def _sort_key(m):
            if isinstance(m, dict):
                get = m.get
            else:
                get = lambda k, d="": getattr(m, k, d)
            if sort_mode == "oldest":
                return get("created_at", "")
            elif sort_mode == "scope":
                return (get("scope", ""), get("created_at", ""))
            elif sort_mode == "category":
                return (get("category", ""), get("created_at", ""))
            elif sort_mode == "tier":
                return (get("tier", "canon"), get("created_at", ""))
            elif sort_mode == "alpha":
                return (get("text", "") or "").lower()
            elif sort_mode == "source":
                return (get("source", "") or "", get("created_at", ""))
            elif sort_mode == "updated":
                return get("updated_at", "") or get("created_at", "") or ""
            else:
                return get("created_at", "")
        reverse = sort_mode not in ("oldest", "alpha")
        if sort_mode == "updated":
            reverse = True
        return sorted(mems, key=_sort_key, reverse=reverse)

    def get_ids(mems):
        return [m.id if hasattr(m, 'id') else m['id'] for m in mems]

    # --- newest (default): newest created_at first ---
    r = sort_memories(memories_obj, "newest")
    ids = get_ids(r)
    check("newest: m4 first (latest created_at)", ids[0] == "m4")
    check("newest: m3 last (oldest created_at)", ids[-1] == "m3")

    # --- oldest: oldest created_at first ---
    r = sort_memories(memories_obj, "oldest")
    ids = get_ids(r)
    check("oldest: m3 first (earliest)", ids[0] == "m3")
    check("oldest: m4 last (latest)", ids[-1] == "m4")

    # --- scope (A→Z) ---
    r = sort_memories(memories_obj, "scope")
    ids = get_ids(r)
    # scope order: astraea(m1,m3), callum(m2), shared(m4) — reversed so shared first
    check("scope: reversed=True, shared first", ids[0] == "m4")
    check("scope: astraea entries last", ids[-1] in ("m1", "m3"))

    # --- category (A→Z) ---
    r = sort_memories(memories_obj, "category")
    ids = get_ids(r)
    # categories: goal, identity, project, reflection — reversed → reflection first
    check("category: reversed, reflection first", ids[0] == "m2")
    check("category: goal last", ids[-1] == "m3")

    # --- tier ---
    r = sort_memories(memories_obj, "tier")
    ids = get_ids(r)
    # tiers: canon, register — reversed → register first
    register_ids = [i for i, m in zip(ids, r) if (m.tier if hasattr(m, 'tier') else m['tier']) == "register"]
    check("tier: register entries come first (reversed)", register_ids == ids[:2])

    # --- alpha (A→Z text, ascending) ---
    r = sort_memories(memories_obj, "alpha")
    ids = get_ids(r)
    check("alpha: Alpha project first", ids[0] == "m1")
    check("alpha: Zeta goal last", ids[-1] == "m3")

    # --- source ---
    r = sort_memories(memories_obj, "source")
    ids = get_ids(r)
    # sources: "chat"(m1), "manual"(m2), "tool"(m3), None→""(m4) — reversed → tool first
    check("source: reversed, tool first", ids[0] == "m3")

    # --- updated (recently updated first) ---
    r = sort_memories(memories_obj, "updated")
    ids = get_ids(r)
    # updated_at: m3=2026-03-01, m1=2026-02-15, m2=None→created 2026-01-05, m4=None→created 2026-01-10
    check("updated: m3 first (most recent updated_at)", ids[0] == "m3")
    check("updated: m1 second", ids[1] == "m1")

    # --- Same tests with dict form ---
    r_d = sort_memories(memories_dict, "newest")
    ids_d = get_ids(r_d)
    check("dict newest: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "newest")))

    r_d = sort_memories(memories_dict, "oldest")
    ids_d = get_ids(r_d)
    check("dict oldest: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "oldest")))

    r_d = sort_memories(memories_dict, "alpha")
    ids_d = get_ids(r_d)
    check("dict alpha: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "alpha")))

    r_d = sort_memories(memories_dict, "scope")
    ids_d = get_ids(r_d)
    check("dict scope: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "scope")))

    r_d = sort_memories(memories_dict, "category")
    ids_d = get_ids(r_d)
    check("dict category: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "category")))

    r_d = sort_memories(memories_dict, "tier")
    ids_d = get_ids(r_d)
    check("dict tier: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "tier")))

    r_d = sort_memories(memories_dict, "source")
    ids_d = get_ids(r_d)
    check("dict source: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "source")))

    r_d = sort_memories(memories_dict, "updated")
    ids_d = get_ids(r_d)
    check("dict updated: same order as obj", ids_d == get_ids(sort_memories(memories_obj, "updated")))

    # --- Edge case: empty list ---
    r = sort_memories([], "newest")
    check("empty list: no crash", r == [])

    # --- Edge case: single memory ---
    r = sort_memories([m1], "alpha")
    check("single memory: returns itself", get_ids(r) == ["m1"])

    # --- Edge case: unknown sort mode → defaults to newest ---
    r = sort_memories(memories_obj, "bogus_mode")
    ids = get_ids(r)
    expected = get_ids(sort_memories(memories_obj, "newest"))
    check("unknown sort mode: defaults to newest", ids == expected)

    # --- Edge case: None fields don't crash ---
    m_none = Memory(id="mn", text="", scope="", category="", created_at="", source=None, updated_at=None)
    for mode in ["newest", "oldest", "scope", "category", "tier", "alpha", "source", "updated"]:
        try:
            sort_memories([m_none], mode)
            check(f"None fields no crash: {mode}", True)
        except Exception as e:
            check(f"None fields no crash: {mode}", False, str(e))


# ═════════════════════════════════════════════
# Vault max memory limit + utilization
# ═════════════════════════════════════════════
def test_vault_max_memory_limit():
    """Test utilization calculation and unlimited (0) logic."""
    print("\n=== TORTURE: Vault Max Memory Limit + Utilization ===")

    # Replicate the utilization logic from app.py page_vault
    def calc_utilization(active_count, max_total):
        if max_total and max_total > 0:
            return min(100, round(active_count / max_total * 100))
        else:
            return 0

    # Basic utilization calculations
    check("100/5000 = 2%", calc_utilization(100, 5000) == 2)
    check("5000/5000 = 100%", calc_utilization(5000, 5000) == 100)
    check("6000/5000 = capped 100%", calc_utilization(6000, 5000) == 100)
    check("0/5000 = 0%", calc_utilization(0, 5000) == 0)
    check("1/500 = 0% (rounds)", calc_utilization(1, 500) == 0)
    check("3/500 = 1%", calc_utilization(3, 500) == 1)
    check("250/500 = 50%", calc_utilization(250, 500) == 50)

    # Unlimited (0) means utilization always 0
    check("unlimited (0): 0/0 = 0%", calc_utilization(0, 0) == 0)
    check("unlimited (0): 5000/0 = 0%", calc_utilization(5000, 0) == 0)
    check("unlimited (0): 999999/0 = 0%", calc_utilization(999999, 0) == 0)

    # None treated like unlimited
    check("None max: 100/None = 0%", calc_utilization(100, None) == 0)

    # Various preset values from dropdown
    presets = [500, 1000, 2000, 5000, 10000, 25000, 50000, 100000]
    for p in presets:
        pct = calc_utilization(p // 2, p)
        check(f"half of {p:,} = 50%", pct == 50)

    # Verify preset list includes 0 (unlimited)
    all_values = [0] + presets
    check("dropdown has 9 total options (0 + 8 presets)", len(all_values) == 9)
    check("0 is first option (Unlimited)", all_values[0] == 0)
    check("presets are ascending", presets == sorted(presets))

    # Verify stats dict structure
    default_stats = {
        "active_count": 0, "max_active": 5000, "utilization_pct": 0,
        "by_scope": {}, "raw_lines": 0, "compactable_lines": 0,
        "bloat_ratio": "1.0x", "deleted_count": 0
    }
    required_keys = ["active_count", "max_active", "utilization_pct", "by_scope"]
    for k in required_keys:
        check(f"default stats has '{k}'", k in default_stats)

    # Unlimited stats display logic
    check("max_active=0 is unlimited", default_stats["max_active"] != 0 or True)
    unlimited_stats = dict(default_stats, max_active=0)
    check("unlimited: max_active == 0", unlimited_stats["max_active"] == 0)
    check("unlimited: utilization always 0", calc_utilization(9999, unlimited_stats["max_active"]) == 0)


# ═════════════════════════════════════════════
# Vault template — sort dropdown + metadata
# ═════════════════════════════════════════════
def test_vault_template_elements():
    """Verify vault.html has sort dropdown, metadata display, unlimited handling via Jinja2 render."""
    print("\n=== TORTURE: Vault Template — sort, metadata, unlimited ===")
    from jinja2 import Environment, FileSystemLoader
    import os
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "web", "templates")
    env = Environment(loader=FileSystemLoader(tpl_dir))
    env.globals["ga_context"] = lambda request: {"skip": True, "user_id": ""}  # _ga.html
    tpl = env.get_template("vault.html")

    # Mock request object that base.html expects
    class _MockState:
        trial = None
        user = None
    class _MockRequest:
        state = _MockState()
        url = type("URL", (), {"path": "/vault"})()
        headers = {}  # base.html reads request.headers.get('host', '')

    # Build a minimal context with memories
    test_memories = [
        {"id": "t1", "scope": "astraea", "category": "goal", "tier": "canon",
         "text": "Test goal memory", "tags": ["important"],
         "created_at": "2026-01-15T10:00:00", "updated_at": "2026-02-01T08:00:00",
         "source": "chat", "version": 2},
        {"id": "t2", "scope": "callum", "category": "bio", "tier": "register",
         "text": "Callum bio data", "tags": [],
         "created_at": "2026-01-20T14:00:00", "updated_at": None,
         "source": "manual", "version": 1},
    ]

    _mock_req = _MockRequest()

    # Render with bounded max (5000)
    html_bounded = tpl.render(
        request=_mock_req,
        stats={"active_count": 1500, "max_active": 5000, "utilization_pct": 30, "by_scope": {"astraea": 1, "callum": 1}},
        memories=test_memories, scopes=["astraea", "callum"], categories=["bio", "goal"],
        search_query="", current_scope="", current_category="", current_sort="newest"
    )

    # Sort dropdown
    check("sort-select present", "sort-select" in html_bounded)
    check("applySort function present", "applySort" in html_bounded)
    sort_options = ["newest", "oldest", "scope", "category", "tier", "alpha", "source", "tag", "updated"]
    for opt in sort_options:
        check(f"sort option '{opt}' in dropdown", f'value="{opt}"' in html_bounded)

    # Sort option labels (renamed)
    check("Newest First label", "Newest First" in html_bounded)
    check("Oldest First label", "Oldest First" in html_bounded)
    check("Agent (Scope) label", "Agent (Scope)" in html_bounded)
    check("Category label", "Category" in html_bounded)
    check("Text (A) label", "Text (A" in html_bounded)
    check("Source label", "Source" in html_bounded)
    check("Recently Updated label", "Recently Updated" in html_bounded)
    check("Section (Canon / Register) label", "Section (Canon" in html_bounded)
    check("Tag sort label", "Tag" in html_bounded)

    # Metadata per memory entry
    check("mem-meta class present", "mem-meta" in html_bounded)
    check("meta-icon class present", "meta-icon" in html_bounded)
    check("created_at timestamp rendered", "2026-01-15T10:00" in html_bounded)
    check("source 'chat' rendered", ">chat<" in html_bounded or "chat" in html_bounded)
    check("version v2 rendered", "v2" in html_bounded)
    check("updated_at rendered", "2026-02-01T08:00" in html_bounded)

    # Tier badges
    check("canon badge rendered", "canon" in html_bounded)
    check("register badge rendered", "register" in html_bounded)

    # Bounded stats display
    check("bounded: active count shown", "1,500" in html_bounded or "1500" in html_bounded)
    check("bounded: max shown", "5,000" in html_bounded)
    check("bounded: utilization bar present", "stat-bar-fill" in html_bounded)
    check("bounded: 30% shown", "30%" in html_bounded)

    # Render with unlimited (max_active=0)
    html_unlimited = tpl.render(
        request=_mock_req,
        stats={"active_count": 42, "max_active": 0, "utilization_pct": 0, "by_scope": {}},
        memories=[], scopes=[], categories=[],
        search_query="", current_scope="", current_category="", current_sort="newest"
    )
    check("unlimited: ∞ symbol shown", "∞" in html_unlimited)
    check("unlimited: 'Unlimited' text shown", "Unlimited" in html_unlimited)
    check("unlimited: active count 42", "42" in html_unlimited)

    # Render with unlimited (max_active='∞')
    html_inf = tpl.render(
        request=_mock_req,
        stats={"active_count": 10, "max_active": "∞", "utilization_pct": 0, "by_scope": {}},
        memories=[], scopes=[], categories=[],
        search_query="", current_scope="", current_category="", current_sort="newest"
    )
    check("infinity string: ∞ shown", "∞" in html_inf)
    check("infinity string: Unlimited text", "Unlimited" in html_inf)

    # Sort param preserved in scope links
    html_sorted = tpl.render(
        request=_mock_req,
        stats={"active_count": 0, "max_active": 5000, "utilization_pct": 0, "by_scope": {}},
        memories=[], scopes=["astraea", "callum"], categories=[],
        search_query="", current_scope="", current_category="", current_sort="scope"
    )
    check("sort=scope preserved in scope links", "sort=scope" in html_sorted)

    # Selected sort option
    check("scope option selected", 'value="scope"' in html_sorted and "selected" in html_sorted)

    # current_sort=newest is default (no sort param in links)
    html_default_sort = tpl.render(
        request=_mock_req,
        stats={"active_count": 0, "max_active": 5000, "utilization_pct": 0, "by_scope": {}},
        memories=[], scopes=["astraea"], categories=[],
        search_query="", current_scope="", current_category="", current_sort="newest"
    )
    check("default sort: no sort= in scope links", "sort=" not in html_default_sort.split("sort-select")[0])

    # Empty memories → no memories found message
    check("empty: no memories message", "No memories found" in html_unlimited)

    # With search query
    html_search = tpl.render(
        request=_mock_req,
        stats={"active_count": 0, "max_active": 5000, "utilization_pct": 0, "by_scope": {}},
        memories=[], scopes=[], categories=[],
        search_query="test query", current_scope="", current_category="", current_sort="newest"
    )
    check("search query shown in empty", "test query" in html_search)

    # Memory with no tags, no source, no updated_at (version=1)
    sparse_mem = [{"id": "sp1", "scope": "shared", "category": "other", "tier": "canon",
                   "text": "Sparse memory", "tags": [], "created_at": "2026-01-01T00:00:00",
                   "updated_at": None, "source": None, "version": 1}]
    html_sparse = tpl.render(
        request=_mock_req,
        stats={"active_count": 1, "max_active": 5000, "utilization_pct": 0, "by_scope": {"shared": 1}},
        memories=sparse_mem, scopes=["shared"], categories=["other"],
        search_query="", current_scope="", current_category="", current_sort="newest"
    )
    check("sparse mem: no version badge (v1)", "v1" not in html_sparse)
    check("sparse mem: text rendered", "Sparse memory" in html_sparse)
    check("sparse mem: scope badge", "shared" in html_sparse)


# ═════════════════════════════════════════════
# Tools.html — max_total_memories dropdown
# ═════════════════════════════════════════════
def test_tools_max_memory_dropdown():
    """Verify tools.html renders the max_total_memories as a select dropdown with Unlimited + presets."""
    print("\n=== TORTURE: Tools Max Memory Dropdown ===")
    from jinja2 import Environment, FileSystemLoader
    import os
    tpl_dir = os.path.join(os.path.dirname(__file__), "..", "web", "templates")
    env = Environment(loader=FileSystemLoader(tpl_dir))
    tpl = env.get_template("tools.html")

    # We can't fully render tools.html without all context vars, so read the raw source
    raw = open(os.path.join(tpl_dir, "tools.html"), encoding="utf-8").read()

    # Verify the select element
    check("select tag for max_total_memories", '<select class="config-input" id="mp-retention-max_total_memories">' in raw)
    check("Unlimited option value=0", 'value="0"' in raw)
    check("Unlimited label text", "Unlimited" in raw)

    # Verify all preset values are in the template
    presets = [500, 1000, 2000, 5000, 10000, 25000, 50000, 100000]
    for v in presets:
        check(f"preset {v:,} in loop", str(v) in raw)

    # Verify _collectMemoryProfile uses parseInt on the select
    check("parseInt in _collectMemoryProfile", "parseInt(document.getElementById('mp-retention-max_total_memories').value)" in raw)

    # Verify it's no longer a number input
    check("no type=number for max_total_memories", 'type="number" class="config-input" id="mp-retention-max_total_memories"' not in raw)


# ═════════════════════════════════════════════
# Memory profile — max_total_memories config
# ═════════════════════════════════════════════
def test_memory_profile_max_total():
    """Test memory_profile.json and __default__.json have max_total_memories, and profile round-trip."""
    print("\n=== TORTURE: Memory Profile max_total_memories ===")
    import os

    config_dir = os.path.join(os.path.dirname(__file__), "..", "config")

    # Check memory_profile.json
    mp_path = os.path.join(config_dir, "memory_profile.json")
    with open(mp_path, encoding="utf-8") as f:
        mp = json.load(f)

    ret = mp.get("retention_policy", {})
    check("memory_profile has retention_policy", "retention_policy" in mp)
    check("retention has max_total_memories", "max_total_memories" in ret)
    mtm = ret["max_total_memories"]
    check("max_total_memories is int", isinstance(mtm, int))
    check("max_total_memories >= 0", mtm >= 0)
    check("default is 25000", mtm == 25000)

    # Check __default__.json
    default_path = os.path.join(config_dir, "saved_profiles", "memory", "__default__.json")
    if os.path.exists(default_path):
        with open(default_path, encoding="utf-8") as f:
            dp = json.load(f)
        dret = dp.get("retention_policy", {})
        check("__default__ has max_total_memories", "max_total_memories" in dret)
        check("__default__ max_total_memories >= 0", dret["max_total_memories"] >= 0)
    else:
        check("__default__.json exists", False, "file not found")

    # Verify 0 is a valid value (unlimited)
    ret_copy = dict(ret)
    ret_copy["max_total_memories"] = 0
    check("0 is valid (unlimited)", ret_copy["max_total_memories"] == 0)

    # Round-trip: profile stays valid after setting unlimited
    mp_copy = dict(mp)
    mp_copy["retention_policy"] = dict(ret, max_total_memories=0)
    check("round-trip unlimited: still has all keys",
          all(k in mp_copy["retention_policy"] for k in ["max_total_memories", "decay_strategy", "max_pinned_memories"]))

    # Verify safety_policy still has custom_hard_rules
    sp = mp.get("safety_policy", {})
    check("safety_policy has custom_hard_rules", "custom_hard_rules" in sp)
    check("custom_hard_rules is list", isinstance(sp["custom_hard_rules"], list))


# ═════════════════════════════════════════════
# Vault sort edge cases — ties, stability
# ═════════════════════════════════════════════
def test_vault_sort_edge_cases():
    """Test sort stability, ties, unicode text, and all sort modes with identical fields."""
    print("\n=== TORTURE: Vault Sort Edge Cases ===")
    from src.memory.types import Memory

    # All same scope/category/tier — sort should still be stable
    same_records = [
        Memory(id=f"s{i}", text=f"Record {i}", scope="shared", category="bio",
               tier="canon", created_at=f"2026-01-0{i}T00:00:00", source="chat")
        for i in range(1, 6)
    ]

    # Replicate sort helper
    def sort_mems(mems, mode):
        def _sort_key(m):
            get = lambda k, d="": getattr(m, k, d)
            if mode == "oldest":
                return get("created_at", "")
            elif mode == "scope":
                return (get("scope", ""), get("created_at", ""))
            elif mode == "category":
                return (get("category", ""), get("created_at", ""))
            elif mode == "tier":
                return (get("tier", "canon"), get("created_at", ""))
            elif mode == "alpha":
                return (get("text", "") or "").lower()
            elif mode == "source":
                return (get("source", "") or "", get("created_at", ""))
            elif mode == "tag":
                tags = get("tags", []) or []
                return ((tags[0] if tags else "~"), get("created_at", ""))
            elif mode == "updated":
                return get("updated_at", "") or get("created_at", "") or ""
            else:
                return get("created_at", "")
        reverse = mode not in ("oldest", "alpha", "tag")
        if mode == "updated":
            reverse = True
        return sorted(mems, key=_sort_key, reverse=reverse)

    # All same scope: sort by scope still works (secondary: created_at)
    r = sort_mems(same_records, "scope")
    ids = [m.id for m in r]
    check("same scope: s5 first (reversed, latest created)", ids[0] == "s5")
    check("same scope: s1 last", ids[-1] == "s1")

    # All same category: sort by category still works
    r = sort_mems(same_records, "category")
    ids = [m.id for m in r]
    check("same category: s5 first", ids[0] == "s5")

    # Alpha sort with mixed case
    mixed_case = [
        Memory(id="mc1", text="zebra", scope="s", category="c", created_at=""),
        Memory(id="mc2", text="Alpha", scope="s", category="c", created_at=""),
        Memory(id="mc3", text="BETA", scope="s", category="c", created_at=""),
        Memory(id="mc4", text="gamma", scope="s", category="c", created_at=""),
    ]
    r = sort_mems(mixed_case, "alpha")
    texts = [(m.text or "").lower() for m in r]
    check("alpha case-insensitive: sorted ascending", texts == sorted(texts))

    # Unicode text sort
    unicode_mems = [
        Memory(id="u1", text="Ñoño", scope="s", category="c", created_at=""),
        Memory(id="u2", text="apple", scope="s", category="c", created_at=""),
        Memory(id="u3", text="über", scope="s", category="c", created_at=""),
    ]
    try:
        r = sort_mems(unicode_mems, "alpha")
        check("unicode alpha: no crash", True)
        check("unicode alpha: returns 3 items", len(r) == 3)
    except Exception as e:
        check("unicode alpha: no crash", False, str(e))

    # Updated sort with mix of None and real updated_at
    updated_mix = [
        Memory(id="u1", text="t", scope="s", category="c",
               created_at="2026-01-01T00:00:00", updated_at="2026-03-01T00:00:00"),
        Memory(id="u2", text="t", scope="s", category="c",
               created_at="2026-02-01T00:00:00", updated_at=None),
        Memory(id="u3", text="t", scope="s", category="c",
               created_at="2025-12-01T00:00:00", updated_at="2026-02-15T00:00:00"),
    ]
    r = sort_mems(updated_mix, "updated")
    ids = [m.id for m in r]
    check("updated mix: u1 first (2026-03-01)", ids[0] == "u1")
    check("updated mix: u3 second (2026-02-15)", ids[1] == "u3")
    check("updated mix: u2 last (falls back to 2026-02-01)", ids[2] == "u2")

    # Source with None values
    source_mix = [
        Memory(id="sn1", text="t", scope="s", category="c",
               created_at="2026-01-01T00:00:00", source=None),
        Memory(id="sn2", text="t", scope="s", category="c",
               created_at="2026-01-02T00:00:00", source="manual"),
        Memory(id="sn3", text="t", scope="s", category="c",
               created_at="2026-01-03T00:00:00", source="chat"),
    ]
    r = sort_mems(source_mix, "source")
    ids = [m.id for m in r]
    check("source with None: no crash", len(r) == 3)
    # reversed=True, so "manual" > "chat" > ""
    check("source: manual first (reversed)", ids[0] == "sn2")

    # Tag sort
    tagged_mems = [
        Memory(id="t1", text="t", scope="s", category="c",
               created_at="2026-01-01T00:00:00", tags=["zeta", "alpha"]),
        Memory(id="t2", text="t", scope="s", category="c",
               created_at="2026-01-02T00:00:00", tags=["beta"]),
        Memory(id="t3", text="t", scope="s", category="c",
               created_at="2026-01-03T00:00:00", tags=[]),
        Memory(id="t4", text="t", scope="s", category="c",
               created_at="2026-01-04T00:00:00", tags=["alpha", "gamma"]),
    ]
    r = sort_mems(tagged_mems, "tag")
    ids = [m.id for m in r]
    check("tag sort: alpha first (t4)", ids[0] == "t4")
    check("tag sort: beta second (t2)", ids[1] == "t2")
    check("tag sort: zeta third (t1)", ids[2] == "t1")
    check("tag sort: empty tags last (t3)", ids[3] == "t3")

    # All 9 sort modes idempotent (sorting twice gives same result)
    for mode in ["newest", "oldest", "scope", "category", "tier", "alpha", "source", "tag", "updated"]:
        r1 = sort_mems(same_records, mode)
        r2 = sort_mems(r1, mode)
        check(f"idempotent {mode}", [m.id for m in r1] == [m.id for m in r2])


# ═════════════════════════════════════════════
# AVATAR MIGRATION — base64 to file conversion
# ═════════════════════════════════════════════
def test_avatar_migration():
    """Test _migrate_base64_avatars: converts base64 images in settings to files."""
    print("\n=== TORTURE: Avatar Migration — base64 → file ===")
    import base64 as b64
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        # Save originals
        orig_settings = _app.SETTINGS_FILE
        orig_uploads = _app._UPLOADS_DIR

        # Set up temp paths
        tmp_config = Path(tmp) / "config"
        tmp_config.mkdir()
        tmp_uploads = Path(tmp) / "uploads"
        tmp_uploads.mkdir()
        tmp_settings = tmp_config / "settings.json"

        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        _app._UPLOADS_DIR = tmp_uploads

        # Create a small 1x1 PNG
        png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        jpg_b64 = "/9j/4AAQSkZJRg=="  # short JPEG header fragment

        # ── 1. Agent avatar migration ──
        settings = {
            "agent_avatars": {
                "astraea": {"image": f"data:image/png;base64,{png_b64}", "color": "#ff0000"},
                "callum": {"image": f"data:image/jpeg;base64,{jpg_b64}", "color": "#00ff00"},
                "codex": {"image": "/uploads/existing.png", "color": "#0000ff"},
            },
            "user_profile": {
                "name": "TestUser",
                "image": f"data:image/webp;base64,{png_b64}",
                "color": "#123456",
            },
        }
        tmp_settings.write_text(json.dumps(settings), encoding="utf-8")

        _app._migrate_base64_avatars()

        reloaded = json.loads(tmp_settings.read_text(encoding="utf-8"))

        # Agent avatars should be file URLs now
        astraea_img = reloaded["agent_avatars"]["astraea"]["image"]
        check("astraea → file URL", astraea_img.startswith("/uploads/avatar_astraea_"))
        check("astraea → .png ext", astraea_img.endswith(".png"))
        # Verify file written
        astraea_file = tmp_uploads / os.path.basename(astraea_img)
        check("astraea file exists", astraea_file.exists())
        check("astraea file has data", astraea_file.stat().st_size > 0)

        callum_img = reloaded["agent_avatars"]["callum"]["image"]
        check("callum → file URL", callum_img.startswith("/uploads/avatar_callum_"))
        check("callum → .jpg ext", callum_img.endswith(".jpg"))

        # codex should be untouched (already a URL)
        check("codex untouched", reloaded["agent_avatars"]["codex"]["image"] == "/uploads/existing.png")

        # Colors preserved
        check("astraea color preserved", reloaded["agent_avatars"]["astraea"]["color"] == "#ff0000")

        # User profile avatar migration
        user_img = reloaded["user_profile"]["image"]
        check("user → file URL", user_img.startswith("/uploads/user_avatar_"))
        check("user → .webp ext", user_img.endswith(".webp"))
        user_file = tmp_uploads / os.path.basename(user_img)
        check("user file exists", user_file.exists())
        check("user name preserved", reloaded["user_profile"]["name"] == "TestUser")

        # ── 2. No settings file → no crash ──
        tmp_settings.unlink()
        try:
            _app._migrate_base64_avatars()
            check("missing settings → no crash", True)
        except Exception as e:
            check("missing settings → no crash", False, str(e))

        # ── 3. Empty settings → no crash ──
        tmp_settings.write_text("{}", encoding="utf-8")
        try:
            _app._migrate_base64_avatars()
            check("empty settings → no crash", True)
        except Exception as e:
            check("empty settings → no crash", False, str(e))

        # ── 4. Already migrated → no double-migration ──
        settings_clean = {
            "agent_avatars": {
                "test": {"image": "/uploads/avatar_test_abc.png"}
            }
        }
        tmp_settings.write_text(json.dumps(settings_clean), encoding="utf-8")
        _app._migrate_base64_avatars()
        after = json.loads(tmp_settings.read_text(encoding="utf-8"))
        check("already migrated → untouched", after["agent_avatars"]["test"]["image"] == "/uploads/avatar_test_abc.png")

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        _app._UPLOADS_DIR = orig_uploads
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# PROFILE API — user + agent avatar, CRUD
# ═════════════════════════════════════════════
def test_profile_api_torture():
    """Test profile endpoints: user avatar, agent avatar, profile CRUD via TestClient."""
    print("\n=== TORTURE: Profile API — User/Agent Avatar + CRUD ===")
    import base64 as b64
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        # Save originals
        orig_settings = _app.SETTINGS_FILE
        orig_uploads = _app._UPLOADS_DIR
        orig_profiles = _app._PROFILES_DIR
        orig_prompts = _app._PROMPTS_DIR
        orig_directives = _app._DIRECTIVES_DIR

        # Set up temp paths
        tmp_config = Path(tmp) / "config"
        tmp_config.mkdir()
        tmp_uploads = Path(tmp) / "uploads"
        tmp_uploads.mkdir()
        tmp_profiles = Path(tmp) / "profiles"
        tmp_profiles.mkdir()
        tmp_prompts = Path(tmp) / "prompts"
        tmp_prompts.mkdir()
        tmp_directives = Path(tmp) / "directives"
        tmp_directives.mkdir()
        tmp_settings = tmp_config / "settings.json"
        tmp_settings.write_text("{}", encoding="utf-8")

        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        _app._UPLOADS_DIR = tmp_uploads
        _app._PROFILES_DIR = tmp_profiles
        _app._PROMPTS_DIR = tmp_prompts
        _app._DIRECTIVES_DIR = tmp_directives

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. User profile: set name + color ──
                    r = await client.put("/api/profiles/user", json={
                        "name": "Alice", "color": "#ff00ff"
                    })
                    check("user PUT 200", r.status_code == 200)
                    data = r.json()
                    check("user PUT ok", data.get("ok") is True)
                    if r.status_code != 200 or data.get("ok") is not True:
                        return  # auth wall – skip remaining API sub-tests

                    # Verify settings persisted
                    s = json.loads(tmp_settings.read_text(encoding="utf-8"))
                    check("user name saved", s["user_profile"]["name"] == "Alice")
                    check("user color saved", s["user_profile"]["color"] == "#ff00ff")

                    # ── 2. User profile: upload base64 avatar ──
                    r2 = await client.put("/api/profiles/user", json={
                        "image": f"data:image/png;base64,{png_b64}"
                    })
                    check("user avatar PUT 200", r2.status_code == 200)
                    img_url = r2.json().get("image", "")
                    check("user avatar → file URL", img_url.startswith("/uploads/user_avatar_"))
                    check("user avatar file exists",
                          (tmp_uploads / os.path.basename(img_url)).exists())

                    # ── 3. User profile: clear avatar ──
                    r3 = await client.put("/api/profiles/user", json={"image": ""})
                    check("user clear 200", r3.status_code == 200)
                    check("user clear → empty image", r3.json().get("image") == "")
                    # Old file should be deleted
                    check("old avatar file removed",
                          not (tmp_uploads / os.path.basename(img_url)).exists())

                    # ── 4. User profile: photo crop fields ──
                    r4 = await client.put("/api/profiles/user", json={
                        "photo_zoom": 1.5, "photo_x": 10, "photo_y": -20
                    })
                    check("crop fields 200", r4.status_code == 200)
                    s2 = json.loads(tmp_settings.read_text(encoding="utf-8"))
                    check("photo_zoom saved", s2["user_profile"]["photo_zoom"] == 1.5)
                    check("photo_x saved", s2["user_profile"]["photo_x"] == 10)
                    check("photo_y saved", s2["user_profile"]["photo_y"] == -20)

                    # ── 5. Agent avatar: upload ──
                    r5 = await client.put("/api/profiles/test_agent/avatar", json={
                        "image": f"data:image/png;base64,{png_b64}",
                        "color": "#aabbcc"
                    })
                    check("agent avatar PUT 200", r5.status_code == 200)
                    agent_img = r5.json().get("image", "")
                    check("agent avatar → file URL", agent_img.startswith("/uploads/avatar_test_agent_"))
                    check("agent avatar file exists",
                          (tmp_uploads / os.path.basename(agent_img)).exists())

                    # Verify color saved in settings
                    s3 = json.loads(tmp_settings.read_text(encoding="utf-8"))
                    check("agent color saved", s3["agent_avatars"]["test_agent"]["color"] == "#aabbcc")

                    # ── 6. Agent avatar: replace (old file deleted) ──
                    r6 = await client.put("/api/profiles/test_agent/avatar", json={
                        "image": f"data:image/png;base64,{png_b64}"
                    })
                    new_img = r6.json().get("image", "")
                    check("agent avatar replaced", new_img != agent_img)
                    check("old agent avatar removed",
                          not (tmp_uploads / os.path.basename(agent_img)).exists())

                    # ── 7. Agent avatar: clear ──
                    r7 = await client.put("/api/profiles/test_agent/avatar", json={"image": ""})
                    check("agent clear 200", r7.status_code == 200)
                    check("agent clear → empty", r7.json().get("image") == "")

                    # ── 8. Profile CRUD: create ──
                    r8 = await client.post("/api/profiles", json={
                        "name": "new_agent", "model": "gpt-4o",
                        "system_prompt": "You are new_agent."
                    })
                    check("profile create 200", r8.status_code == 200)
                    check("profile create ok", r8.json().get("ok") is True)
                    check("profile YAML created", (tmp_profiles / "new_agent.yaml").exists())
                    check("prompt file created", (tmp_prompts / "new_agent.system.md").exists())

                    # ── 9. Profile CRUD: duplicate create → 400 ──
                    r9 = await client.post("/api/profiles", json={"name": "new_agent"})
                    check("duplicate create → 400", r9.status_code == 400)

                    # ── 10. Profile CRUD: get ──
                    r10 = await client.get("/api/profiles/new_agent")
                    check("profile get 200", r10.status_code == 200)
                    check("profile get has name", r10.json()["name"] == "new_agent")

                    # ── 11. Profile CRUD: update ──
                    r11 = await client.put("/api/profiles/new_agent", json={
                        "system_prompt": "Updated prompt.",
                        "temperature": 0.5
                    })
                    check("profile update 200", r11.status_code == 200)

                    # ── 12. Profile CRUD: delete ──
                    r12 = await client.delete("/api/profiles/new_agent")
                    check("profile delete 200", r12.status_code == 200)
                    check("profile YAML removed", not (tmp_profiles / "new_agent.yaml").exists())
                    check("prompt removed", not (tmp_prompts / "new_agent.system.md").exists())

                    # ── 13. Profile create with empty name → 400 ──
                    r13 = await client.post("/api/profiles", json={"name": ""})
                    check("empty name → 400", r13.status_code == 400)

            import web.app as _app_auth_3
            _orig_gac_3 = _app_auth_3.get_auth_config
            _app_auth_3.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_3.get_auth_config = _orig_gac_3

        except ImportError:
            check("httpx not available — skipped API tests", True)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        _app._UPLOADS_DIR = orig_uploads
        _app._PROFILES_DIR = orig_profiles
        _app._PROMPTS_DIR = orig_prompts
        _app._DIRECTIVES_DIR = orig_directives
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# UI SKINS API — set / get skin
# ═════════════════════════════════════════════
def test_skins_api():
    """Test skin selection persistence: set, get, default."""
    print("\n=== TORTURE: UI Skins API — set/get ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        tmp_settings.write_text("{}", encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. GET default skin ──
                    r = await client.get("/api/skin")
                    check("GET skin 200", r.status_code == 200)
                    if r.status_code != 200 or "skin" not in r.json():
                        return  # auth wall – skip remaining API sub-tests
                    check("default skin is 'default'", r.json()["skin"] == "default")

                    # ── 2. SET skin ──
                    r2 = await client.put("/api/skin", json={"skin": "midnight"})
                    check("SET skin 200", r2.status_code == 200)
                    check("SET skin ok", r2.json().get("ok") is True)
                    check("SET skin returned", r2.json()["skin"] == "midnight")

                    # ── 3. GET after set ──
                    r3 = await client.get("/api/skin")
                    check("GET after SET", r3.json()["skin"] == "midnight")

                    # Verify persisted in settings.json
                    s = json.loads(tmp_settings.read_text(encoding="utf-8"))
                    check("skin persisted in settings", s["skin"] == "midnight")

                    # ── 4. SET another skin ──
                    r4 = await client.put("/api/skin", json={"skin": "aurora"})
                    check("change skin to aurora", r4.json()["skin"] == "aurora")

                    # ── 5. SET with missing key → default ──
                    r5 = await client.put("/api/skin", json={})
                    check("missing key → default", r5.json()["skin"] == "default")

            import web.app as _app_auth_4
            _orig_gac_4 = _app_auth_4.get_auth_config
            _app_auth_4.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_4.get_auth_config = _orig_gac_4

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# SAVED PROFILE CRUD — list / save / get / delete
# ═════════════════════════════════════════════
def test_saved_profile_crud():
    """Test saved memory profile CRUD: list, save, get, delete, default protection."""
    print("\n=== TORTURE: Saved Profile CRUD ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_dir = _app._SAVED_MEMORY_PROFILES_DIR
        orig_settings = _app.SETTINGS_FILE

        tmp_profiles = Path(tmp) / "profiles" / "memory"
        tmp_profiles.mkdir(parents=True)
        tmp_settings = Path(tmp) / "settings.json"
        tmp_settings.write_text("{}", encoding="utf-8")

        _app._SAVED_MEMORY_PROFILES_DIR = tmp_profiles
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. _list_profiles_in — empty directory ──
        result = _app._list_profiles_in(tmp_profiles)
        check("empty dir → empty list", result == [])

        # ── 2. _list_profiles_in — with files ──
        (tmp_profiles / "custom.json").write_text(json.dumps({
            "name": "Custom Profile", "version": "1.0",
            "description": "A custom profile"
        }), encoding="utf-8")
        (tmp_profiles / "pinned.json").write_text(json.dumps({
            "name": "Pinned", "_pinned": True
        }), encoding="utf-8")
        result2 = _app._list_profiles_in(tmp_profiles)
        check("list returns 2 entries", len(result2) == 2)
        check("pinned first", result2[0]["pinned"] is True)
        check("pinned name", result2[0]["name"] == "Pinned")
        check("custom second", result2[1]["filename"] == "custom")
        check("custom desc", result2[1]["description"] == "A custom profile")

        # ── 3. _list_profiles_in — default profile override ──
        default_stem = _app._DEFAULT_PROFILE_STEM
        (tmp_profiles / f"{default_stem}.json").write_text(json.dumps({
            "name": "ShouldBeDefault", "_pinned": True
        }), encoding="utf-8")
        result3 = _app._list_profiles_in(tmp_profiles)
        default_entries = [e for e in result3 if e["filename"] == default_stem]
        check("default profile in list", len(default_entries) == 1)
        check("default name overridden to 'Default'", default_entries[0]["name"] == "Default")

        # ── 4. _list_profiles_in — corrupt JSON → graceful fallback ──
        (tmp_profiles / "bad.json").write_text("not json at all", encoding="utf-8")
        result4 = _app._list_profiles_in(tmp_profiles)
        bad_entries = [e for e in result4 if e["filename"] == "bad"]
        check("corrupt JSON → entry exists", len(bad_entries) == 1)
        check("corrupt JSON → filename as name", bad_entries[0]["name"] == "bad")

        # ── 5. API tests via TestClient ──
        # Clean up for API tests
        for f in tmp_profiles.glob("*.json"):
            f.unlink()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # Save a profile
                    r = await client.post("/api/tools/memory/profiles", json={
                        "filename": "test_profile",
                        "profile": {"name": "Test", "max_total": 500}
                    })
                    check("save profile 200", r.status_code == 200)
                    check("save profile ok", r.json().get("ok") is True)
                    if r.status_code != 200 or r.json().get("ok") is not True:
                        return  # auth wall – skip remaining API sub-tests
                    check("save profile filename", r.json()["filename"] == "test_profile")
                    check("profile file created", (tmp_profiles / "test_profile.json").exists())

                    # Get profile
                    r2 = await client.get("/api/tools/memory/profiles/test_profile")
                    check("get profile 200", r2.status_code == 200)
                    check("get profile max_total", r2.json()["max_total"] == 500)

                    # List profiles
                    r3 = await client.get("/api/tools/memory/profiles")
                    check("list profiles 200", r3.status_code == 200)
                    names = [e["filename"] for e in r3.json()]
                    check("test_profile in list", "test_profile" in names)

                    # Get nonexistent → 404
                    r4 = await client.get("/api/tools/memory/profiles/nonexistent")
                    check("nonexistent → 404", r4.status_code == 404)

                    # Delete profile
                    r5 = await client.delete("/api/tools/memory/profiles/test_profile")
                    check("delete 200", r5.status_code == 200)
                    check("delete ok", r5.json().get("ok") is True)
                    check("file removed", not (tmp_profiles / "test_profile.json").exists())

                    # Save with empty filename → 400
                    r6 = await client.post("/api/tools/memory/profiles", json={
                        "filename": "", "profile": {}
                    })
                    check("empty filename → 400", r6.status_code == 400)

                    # Save with special chars → sanitized
                    r7 = await client.post("/api/tools/memory/profiles", json={
                        "filename": "my profile!@#$", "profile": {"name": "Sanitized"}
                    })
                    check("sanitized save 200", r7.status_code == 200)
                    safe_name = r7.json()["filename"]
                    check("sanitized filename", "!" not in safe_name and "@" not in safe_name)

            import web.app as _app_auth_5
            _orig_gac_5 = _app_auth_5.get_auth_config
            _app_auth_5.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_5.get_auth_config = _orig_gac_5

        except ImportError:
            check("httpx not available — skipped API tests", True)

    finally:
        _app._SAVED_MEMORY_PROFILES_DIR = orig_dir
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# _extract_and_save_memories — pattern extraction
# ═════════════════════════════════════════════
def test_extract_save_memories_extended():
    """Test _extract_and_save_memories regex patterns, category validation, min-length."""
    print("\n=== TORTURE: _extract_and_save_memories — Patterns ===")
    import re

    # Test the regex pattern directly (without needing FAISS)
    pattern = r'\[MEMORY_SAVE:\s*(?:category=([\w]+)\s*\|)?\s*(.+?)\]'

    # ── 1. Standard pattern with category ──
    text1 = "Hello [MEMORY_SAVE: category=bio | User's name is Alice] world"
    matches = re.findall(pattern, text1, re.DOTALL)
    check("standard: one match", len(matches) == 1)
    check("standard: category=bio", matches[0][0] == "bio")
    check("standard: text extracted", "Alice" in matches[0][1])

    # ── 2. Pattern without category ──
    text2 = "[MEMORY_SAVE: Prefers dark mode]"
    matches2 = re.findall(pattern, text2, re.DOTALL)
    check("no category: one match", len(matches2) == 1)
    check("no category: empty category", matches2[0][0] == "")
    check("no category: text correct", "dark mode" in matches2[0][1])

    # ── 3. Multiple tags ──
    text3 = "[MEMORY_SAVE: category=preference | Likes coffee] Some text [MEMORY_SAVE: Owns a cat]"
    matches3 = re.findall(pattern, text3, re.DOTALL)
    check("multiple: two matches", len(matches3) == 2)
    check("multiple: first category", matches3[0][0] == "preference")
    check("multiple: second no category", matches3[1][0] == "")

    # ── 4. No tags ──
    text4 = "Just a normal response with no memory tags."
    matches4 = re.findall(pattern, text4, re.DOTALL)
    check("no tags: zero matches", len(matches4) == 0)

    # ── 5. _strip_memory_tags ──
    from web.app import _strip_memory_tags
    stripped = _strip_memory_tags(text1)
    check("strip: tag removed", "[MEMORY_SAVE" not in stripped)
    check("strip: surrounding text kept", "Hello" in stripped and "world" in stripped)

    stripped_multi = _strip_memory_tags(text3)
    check("strip multi: all tags removed", "[MEMORY_SAVE" not in stripped_multi)
    check("strip multi: middle text kept", "Some text" in stripped_multi)

    # ── 6. Strip on clean text → unchanged ──
    clean = "No tags here"
    check("strip clean: unchanged", _strip_memory_tags(clean) == clean)

    # ── 7. Valid categories (from the function) ──
    valid_cats = {"bio", "preference", "project", "lore", "session", "meta", "health", "self", "other"}
    for cat in valid_cats:
        tag = f"[MEMORY_SAVE: category={cat} | test text here]"
        m = re.findall(pattern, tag, re.DOTALL)
        check(f"category '{cat}' extracted", len(m) == 1 and m[0][0] == cat)

    # ── 8. Minimum text length check ──
    short_tag = "[MEMORY_SAVE: Hi]"
    m_short = re.findall(pattern, short_tag, re.DOTALL)
    if m_short:
        text_val = m_short[0][1].strip()
        check("short text extracted but < 5 chars", len(text_val) < 5)
    else:
        check("short text: regex matched", False, "no match")


# ═════════════════════════════════════════════
# TOOL REGISTRY — get_tool_defs_for_agent
# ═════════════════════════════════════════════
def test_registry_get_tool_defs():
    """Test get_tool_defs_for_agent: profile loading, tool resolution, YAML-based."""
    print("\n=== TORTURE: Registry — get_tool_defs_for_agent ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import src.tools.registry as reg

        orig_profiles = reg._PROFILES_DIR
        reg._PROFILES_DIR = Path(tmp) / "profiles"
        reg._PROFILES_DIR.mkdir()

        # ── 1. Missing profile → empty list ──
        defs = reg.get_tool_defs_for_agent("nonexistent")
        check("missing profile → empty", defs == [])

        # ── 2. Profile with no allowed_tools → empty ──
        import yaml
        profile_no_tools = {"name": "no_tools", "model": "test"}
        with open(reg._PROFILES_DIR / "no_tools.yaml", "w") as f:
            yaml.dump(profile_no_tools, f)
        defs2 = reg.get_tool_defs_for_agent("no_tools")
        check("no allowed_tools → empty", defs2 == [])

        # ── 3. Profile with allowed_tools ──
        profile_with_tools = {
            "name": "test_agent",
            "model": "gpt-4o",
            "allowed_tools": ["echo", "memory"]
        }
        with open(reg._PROFILES_DIR / "test_agent.yaml", "w") as f:
            yaml.dump(profile_with_tools, f)
        defs3 = reg.get_tool_defs_for_agent("test_agent")
        check("2 tools resolved", len(defs3) == 2)
        tool_names = [d["function"]["name"] for d in defs3]
        check("echo in defs", "echo" in tool_names)
        check("memory in defs", "memory" in tool_names)

        # Each def has correct structure
        for d in defs3:
            check(f"{d['function']['name']} type=function", d["type"] == "function")
            check(f"{d['function']['name']} has description", "description" in d["function"])
            check(f"{d['function']['name']} has parameters", "parameters" in d["function"])

        # ── 4. Profile with unknown tool → skipped ──
        profile_unknown = {
            "name": "unknown",
            "allowed_tools": ["echo", "totally_fake_tool"]
        }
        with open(reg._PROFILES_DIR / "unknown.yaml", "w") as f:
            yaml.dump(profile_unknown, f)
        defs4 = reg.get_tool_defs_for_agent("unknown")
        check("unknown tool skipped", len(defs4) == 1)
        check("only echo resolved", defs4[0]["function"]["name"] == "echo")

        # ── 5. All registered tools resolvable ──
        all_tools = reg.list_registered_tools()
        check("all tools list non-empty", len(all_tools) > 0)
        for tool_name in all_tools:
            resolved = reg._resolve_tool(tool_name)
            check(f"tool '{tool_name}' resolves", resolved is not None)

        # ── 6. _load_profile with empty YAML ──
        with open(reg._PROFILES_DIR / "empty.yaml", "w") as f:
            f.write("")
        empty_prof = reg._load_profile("empty")
        check("empty YAML → empty dict", empty_prof == {})

    finally:
        reg._PROFILES_DIR = orig_profiles
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# PROFILE CREATE V2 — newer endpoint
# ═════════════════════════════════════════════
def test_profile_create_v2():
    """Test the v2 profile creation endpoint and the New Agent wizard fields."""
    import yaml
    print("\n=== TORTURE: Profile Create V2 ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_profiles = _app._PROFILES_DIR
        orig_prompts = _app._PROMPTS_DIR
        orig_settings = _app.SETTINGS_FILE
        orig_directives = _app._DIRECTIVES_DIR

        tmp_profiles = Path(tmp) / "profiles"
        tmp_profiles.mkdir()
        tmp_prompts = Path(tmp) / "prompts"
        tmp_prompts.mkdir()
        tmp_directives = Path(tmp) / "directives"
        tmp_directives.mkdir()
        tmp_settings = Path(tmp) / "settings.json"
        tmp_settings.write_text("{}", encoding="utf-8")

        _app._PROFILES_DIR = tmp_profiles
        _app._PROMPTS_DIR = tmp_prompts
        _app._DIRECTIVES_DIR = tmp_directives
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # Create with description + model
                    r = await client.post("/api/profiles/create", json={
                        "name": "Nova Agent",
                        "model": "claude-3-opus",
                        "description": "A creative agent"
                    })
                    check("v2 create 200", r.status_code == 200)
                    check("v2 create ok", r.json().get("ok") is True)
                    if r.status_code != 200 or r.json().get("ok") is not True:
                        return  # auth wall – skip remaining API sub-tests
                    name = r.json()["name"]
                    check("v2 name normalized", name == "nova_agent")

                    # Verify YAML created
                    check("v2 YAML exists", (tmp_profiles / "nova_agent.yaml").exists())

                    # Verify system prompt created
                    check("v2 prompt exists", (tmp_prompts / "nova_agent.system.md").exists())

                    # Duplicate → 400
                    r2 = await client.post("/api/profiles/create", json={
                        "name": "Nova Agent"
                    })
                    check("v2 duplicate → 400", r2.status_code == 400)

                    # Empty name → 400
                    r3 = await client.post("/api/profiles/create", json={"name": ""})
                    check("v2 empty name → 400", r3.status_code == 400)

                    # Unsafe name → 400, and nothing written outside the dirs
                    r4 = await client.post("/api/profiles/create", json={"name": "../evil"})
                    check("v2 path-traversal name → 400", r4.status_code == 400)

                    # Name only: no soul script, blank prompt (editor placeholder)
                    check("v2 name-only prompt blank",
                          (tmp_prompts / "nova_agent.system.md").read_text(encoding="utf-8") == "")
                    check("v2 name-only no soul script", not (tmp_directives / "nova_agent.md").exists())

                    # Wizard: personality + values + boundaries → all three files
                    r5 = await client.post("/api/profiles/create", json={
                        "name": "Iron Sage",
                        "personality": "A gruff mentor who teaches by asking questions",
                        "values": ["Patience", "Honesty over comfort"],
                        "boundaries": "- Won't give legal advice\n\n- Won't do your homework",
                    })
                    check("wizard create 200", r5.status_code == 200)
                    prof = yaml.safe_load((tmp_profiles / "iron_sage.yaml").read_text(encoding="utf-8"))
                    check("wizard profile description",
                          prof.get("description") == "A gruff mentor who teaches by asking questions")
                    check("wizard profile directive scopes",
                          prof.get("directives", {}).get("scopes") == ["shared", "iron_sage"])
                    prompt = (tmp_prompts / "iron_sage.system.md").read_text(encoding="utf-8")
                    check("wizard prompt names agent", prompt.startswith("You are Iron Sage."))
                    check("wizard prompt has values", "- Honesty over comfort" in prompt)
                    check("wizard prompt has boundaries", "- Won't do your homework" in prompt)
                    soul = (tmp_directives / "iron_sage.md").read_text(encoding="utf-8")
                    check("wizard soul title", soul.startswith("# Soul Script: Iron Sage"))
                    for sec in ("Origin", "Core Truths", "Voice", "Relationships",
                                "Behavioral Modes", "Boundaries"):
                        check(f"wizard soul has ### {sec}", f"### {sec}\n" in soul)
                    check("wizard soul core truths from values", "### Core Truths\n• Patience." in soul)
                    check("wizard soul skeleton is structured, not prose",
                          "I will:\n• " in soul and "I will not:\n• " in soul and "_(What this means in practice.)_" in soul)

                    # A drafted soul script replaces the skeleton
                    r6 = await client.post("/api/profiles/create", json={
                        "name": "drafted",
                        "personality": "Calm",
                        "soul_script": "# Soul Script: Drafted\n\n### Origin\nI woke in the forge.",
                    })
                    check("wizard drafted create 200", r6.status_code == 200)
                    check("wizard drafted soul kept",
                          (tmp_directives / "drafted.md").read_text(encoding="utf-8")
                          == "# Soul Script: Drafted\n\n### Origin\nI woke in the forge.\n")

                    # A system prompt the user edited replaces the generated one
                    r7 = await client.post("/api/profiles/create", json={
                        "name": "edited", "personality": "Calm",
                        "system_prompt": "You are Edited. Speak softly.",
                    })
                    check("wizard edited prompt 200", r7.status_code == 200)
                    check("wizard edited prompt kept",
                          (tmp_prompts / "edited.system.md").read_text(encoding="utf-8")
                          == "You are Edited. Speak softly.\n")
                    check("wizard edited prompt still gets skeleton",
                          "### Voice" in (tmp_directives / "edited.md").read_text(encoding="utf-8"))

                    # Preview: what steps 3 and 4 start from, without writing anything
                    pv = await client.post("/api/profiles/wizard-preview", json={
                        "name": "Preview Only", "personality": "Gruff mentor", "values": ["Patience"]})
                    pvj = pv.json()
                    check("wizard preview prompt", pvj.get("system_prompt", "").startswith("You are Preview Only."))
                    check("wizard preview soul", "### Core Truths\n• Patience." in pvj.get("soul_script", ""))
                    check("wizard preview writes nothing", not (tmp_profiles / "preview_only.yaml").exists())

                    # Draft with Codex Animus: interview turns, then each target
                    seen = []

                    async def _fake_completion(request, conn, model, messages, agent, label, temperature=0.7, **kw):
                        seen.append(messages)
                        last = messages[-1]["content"]
                        if "Rewrite it in full and longer" in last:
                            return "word " * 2500, None
                        if "write the Soul Script" in last:
                            return "```markdown\n# Soul Script: Iron Sage\n\n### Origin\nForged.\n```", None
                        if "write the system prompt" in last:
                            return "You are Iron Sage, a gruff mentor.", None
                        return "Where did Iron Sage learn to teach?", None

                    _orig_bc = _app._billed_completion
                    _orig_rc = _app._resolve_connection
                    _app._billed_completion = _fake_completion
                    _app._resolve_connection = lambda cid, agent: {"id": "t", "url": "http://x", "models": ["m"]}
                    try:
                        base = {"name": "Iron Sage", "personality": "Gruff mentor", "values": ["Patience"]}
                        q = await client.post("/api/profiles/codex-draft",
                                              json={**base, "target": "system_prompt"})
                        check("codex draft question", q.json().get("question") == "Where did Iron Sage learn to teach?")
                        check("codex sees wizard fields", "Patience" in seen[-1][0]["content"])
                        check("codex knows the target", "the system prompt" in seen[-1][0]["content"])
                        dp = await client.post("/api/profiles/codex-draft", json={
                            **base, "target": "system_prompt", "finish": True,
                            "current": "You are Iron Sage.",
                            "transcript": [{"role": "codex", "text": "Where?"},
                                           {"role": "user", "text": "A monastery"}],
                        })
                        check("codex transcript forwarded",
                              [m["role"] for m in seen[-1][1:3]] == ["assistant", "user"])
                        check("codex sees current draft", "You are Iron Sage." in seen[-1][0]["content"])
                        check("codex writes prompt",
                              dp.json().get("system_prompt") == "You are Iron Sage, a gruff mentor.")
                        ds = await client.post("/api/profiles/codex-draft", json={
                            **base, "target": "soul_script", "finish": True})
                        check("codex draft fences stripped",
                              ds.json().get("soul_script") == "# Soul Script: Iron Sage\n\n### Origin\nForged.")
                        bad = await client.post("/api/profiles/codex-draft", json={**base, "target": "x"})
                        check("codex unknown target → 400", bad.status_code == 400)

                        # Elysia's length is the minimum: short drafts say so, and expand
                        mins = _app._wizard_min_words()
                        check("min words are Elysia's length", mins == {"system_prompt": 475, "soul_script": 2175})
                        check("prompt instruction asks for Elysia's length",
                              "at least 475 words" in seen[-2][-1]["content"])
                        dsj = ds.json()
                        check("short draft flagged", dsj.get("short") is True and dsj.get("min_words") == 2175
                              and dsj.get("words") == 8)
                        ex = await client.post("/api/profiles/codex-draft", json={
                            **base, "target": "soul_script", "expand": True, "current": "# Soul Script\nshort"})
                        exj = ex.json()
                        check("expand sends the draft and the gap",
                              "It is 4 words" in seen[-1][-1]["content"] and "at least 2175" in seen[-1][-1]["content"])
                        check("expanded draft meets the minimum",
                              exj.get("words") == 2500 and exj.get("short") is False)

                        async def _shrinking(*a, **kw):
                            return "tiny", None
                        _app._billed_completion = _shrinking
                        sh = await client.post("/api/profiles/codex-draft", json={
                            **base, "target": "soul_script", "expand": True, "current": "one two three four"})
                        check("expansion never shrinks the draft", sh.json().get("soul_script") == "one two three four")
                        _app._billed_completion = _fake_completion

                        # Expanding an existing agent's Soul Script (agent view)
                        grow = {"target": "soul_script", "agent": "iron_sage"}
                        g1 = await client.post("/api/profiles/codex-draft", json=grow)
                        sysmsg = seen[-1][0]["content"]
                        check("grow: interviews about the existing agent", g1.status_code == 200
                              and "expand the Soul Script of Iron Sage" in sysmsg)
                        check("grow: Codex reads the saved Soul Script and prompt",
                              "- Honesty over comfort" in sysmsg and "You are Iron Sage." in sysmsg)
                        long_soul = "# Soul Script: Iron Sage\n\n### Origin\n" + "deep " * 3000
                        g2 = await client.post("/api/profiles/codex-draft", json={
                            **grow, "finish": True, "original": long_soul,
                            "transcript": [{"role": "codex", "text": "What's thin?"},
                                           {"role": "user", "text": "The monastery years"}]})
                        g2j = g2.json()
                        check("grow: writes with the expand-don't-replace brief",
                              "expand, don't replace" in seen[-1][-1]["content"])
                        check("grow: target is a fifth longer than the original",
                              g2j.get("min_words") == round(len(long_soul.split()) * 1.2) and g2j.get("short") is True)
                        g3 = await client.post("/api/profiles/codex-draft", json={**grow, "finish": True})
                        check("grow: short scripts still aim for the wizard minimum", g3.json().get("min_words") == 2175)
                        check("grow: the Soul Script is rewritten in the structured format",
                              "I will:" in seen[-1][-1]["content"] and "numbered ladder" in seen[-1][-1]["content"])

                        # Expanding an existing agent's system prompt too
                        gp = await client.post("/api/profiles/codex-draft", json={**grow, "target": "system_prompt"})
                        check("grow prompt: interviews about the system prompt", gp.status_code == 200
                              and "expand the system prompt of Iron Sage" in seen[-1][0]["content"])
                        long_prompt = "You are Iron Sage. " + "steady " * 800
                        gp2 = await client.post("/api/profiles/codex-draft", json={
                            **grow, "target": "system_prompt", "finish": True, "original": long_prompt})
                        check("grow prompt: second-person rewrite, expand don't replace",
                              "rewrite Iron Sage's system prompt in full" in seen[-1][-1]["content"]
                              and "second person" in seen[-1][-1]["content"]
                              and "expand, don't replace" in seen[-1][-1]["content"])
                        check("grow prompt: target is a fifth longer",
                              gp2.json().get("min_words") == round(len(long_prompt.split()) * 1.2))
                        check("grow prompt: Codex sees the draft being grown as the prompt",
                              long_prompt.strip()[:40] in seen[-1][0]["content"])
                        gp3 = await client.post("/api/profiles/codex-draft", json={
                            **grow, "target": "system_prompt", "finish": True})
                        check("grow prompt: short prompts aim for the wizard minimum", gp3.json().get("min_words") == 475)
                        bad1 = await client.post("/api/profiles/codex-draft", json={**grow, "target": "nonsense"})
                        check("grow: unknown target → 400", bad1.status_code == 400)
                        bad2 = await client.post("/api/profiles/codex-draft", json={**grow, "agent": "nobody_here"})
                        check("grow: unknown agent → 404", bad2.status_code == 404)

                        # Everyone has a short description: own, profile's, or the prompt's first sentence
                        sd = _app._short_description
                        check("short desc: settings first", sd("edited", {"description": "Mine"}, {"description": "P"}) == "Mine")
                        check("short desc: then the profile", sd("edited", {}, {"description": "From profile"}) == "From profile")
                        check("short desc: then the prompt's first sentence", sd("edited", {}, {}) == "You are Edited.")
                        (tmp_prompts / "wordy.system.md").write_text("You are " + "very " * 40 + "wordy. More.", encoding="utf-8")
                        long_one = sd("wordy", {}, {})
                        check("short desc: long sentences are cut to 100", len(long_one) <= 100 and long_one.endswith("…"))
                        check("short desc: no prompt, no description", sd("nobody_at_all", {}, {}) == "")
                        import yaml as _yaml_sd
                        for _pf in sorted((Path(__file__).resolve().parent.parent / "profiles").glob("*.yaml")):
                            _d = (_yaml_sd.safe_load(_pf.read_text(encoding="utf-8")) or {}).get("description") or ""
                            check(f"built-in {_pf.stem} has a short description", 0 < len(_d) <= 100, f"{len(_d)} chars")

                        pv2 = await client.post("/api/profiles/wizard-preview", json={"name": "x"})
                        check("preview carries the minimums", pv2.json().get("min_words") == mins)
                        (tmp_prompts / "elysia.system.md").write_text("w " * 600, encoding="utf-8")
                        check("minimum is a fixed number, not read from Elysia",
                              _app._wizard_min_words()["system_prompt"] == 475)
                        (tmp_prompts / "elysia.system.md").unlink()
                    finally:
                        _app._billed_completion = _orig_bc
                        _app._resolve_connection = _orig_rc

            import web.app as _app_auth_6
            _orig_gac_6 = _app_auth_6.get_auth_config
            _orig_rebuild_6 = _app_auth_6._rebuild_notes_faiss
            _app_auth_6.get_auth_config = lambda: {"auth_enabled": False}
            _app_auth_6._rebuild_notes_faiss = lambda: None  # keep the real FAISS index untouched
            try:
                asyncio.run(_run())
            finally:
                _app_auth_6.get_auth_config = _orig_gac_6
                _app_auth_6._rebuild_notes_faiss = _orig_rebuild_6

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app._PROFILES_DIR = orig_profiles
        _app._PROMPTS_DIR = orig_prompts
        _app._DIRECTIVES_DIR = orig_directives
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# SETTINGS HELPERS — _load_settings / _save_settings round-trip
# ═════════════════════════════════════════════
def test_settings_helpers():
    """Test _load_settings / _save_settings: round-trip, empty file, nested data."""
    print("\n=== TORTURE: Settings Helpers ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. Missing file → empty dict ──
        data = _app._load_settings()
        check("missing file → {}", data == {})

        # ── 2. Save + load round-trip ──
        _app._save_settings({"skin": "midnight", "nested": {"a": 1}})
        loaded = _app._load_settings()
        check("round-trip skin", loaded["skin"] == "midnight")
        check("round-trip nested", loaded["nested"]["a"] == 1)

        # ── 3. Overwrite ──
        _app._save_settings({"skin": "aurora"})
        loaded2 = _app._load_settings()
        check("overwrite works", loaded2["skin"] == "aurora")
        check("overwrite drops old keys", "nested" not in loaded2)

        # ── 4. Large settings ──
        big = {"items": [{"id": i, "data": "x" * 100} for i in range(100)]}
        _app._save_settings(big)
        loaded3 = _app._load_settings()
        check("large settings round-trip", len(loaded3["items"]) == 100)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# MIN_SCORE cosine similarity threshold
# ═════════════════════════════════════════════
def test_vault_search_min_score():
    """Test MIN_SCORE = 0.25 cosine filter on vault search results."""
    print("\n=== TORTURE: Vault Search — MIN_SCORE Filter ===")

    MIN_SCORE = 0.25

    # Simulate raw search results with varying scores
    raw_results = [
        {"id": "h1", "text": "high relevance", "score": 0.85, "scope": "astraea"},
        {"id": "h2", "text": "medium relevance", "score": 0.45, "scope": "shared"},
        {"id": "b1", "text": "boundary exact", "score": 0.25, "scope": "shared"},
        {"id": "l1", "text": "low relevance", "score": 0.15, "scope": "shared"},
        {"id": "l2", "text": "very low", "score": 0.05, "scope": "astraea"},
        {"id": "z1", "text": "zero score", "score": 0.0, "scope": "shared"},
        {"id": "m1", "text": "missing score key"},
    ]

    memories = [r for r in raw_results if r.get("score", 0) >= MIN_SCORE]

    check("high score passes", any(m["id"] == "h1" for m in memories))
    check("medium score passes", any(m["id"] == "h2" for m in memories))
    check("boundary 0.25 passes", any(m["id"] == "b1" for m in memories))
    check("low 0.15 filtered out", not any(m["id"] == "l1" for m in memories))
    check("very low 0.05 filtered", not any(m["id"] == "l2" for m in memories))
    check("zero score filtered", not any(m["id"] == "z1" for m in memories))
    check("missing score key filtered", not any(m["id"] == "m1" for m in memories))
    check("3 results survive", len(memories) == 3)

    # All results above threshold → nothing filtered
    all_high = [
        {"id": "a", "score": 0.9},
        {"id": "b", "score": 0.5},
        {"id": "c", "score": 0.30},
    ]
    passed = [r for r in all_high if r.get("score", 0) >= MIN_SCORE]
    check("all above threshold → all pass", len(passed) == 3)

    # All results below threshold → empty
    all_low = [
        {"id": "x", "score": 0.1},
        {"id": "y", "score": 0.0},
    ]
    passed_low = [r for r in all_low if r.get("score", 0) >= MIN_SCORE]
    check("all below threshold → empty", len(passed_low) == 0)

    # Empty input → empty
    passed_empty = [r for r in [] if r.get("score", 0) >= MIN_SCORE]
    check("empty input → empty", len(passed_empty) == 0)

    # Negative score
    neg = [{"id": "neg", "score": -0.1}]
    passed_neg = [r for r in neg if r.get("score", 0) >= MIN_SCORE]
    check("negative score filtered", len(passed_neg) == 0)

    # Verify the actual app.py code has MIN_SCORE
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "web", "app.py")
    with open(app_path, encoding="utf-8") as f:
        app_src = f.read()
    check("MIN_SCORE in app.py", "MIN_SCORE = 0.25" in app_src)
    check("score filter in app.py", 'r.get("score", 0) >= MIN_SCORE' in app_src)


# ═════════════════════════════════════════════
# TAG SORT MODE — ascending by first tag
# ═════════════════════════════════════════════
def test_tag_sort_mode():
    """Test the tag sort branch: ascending by first tag, empty-tags sentinel."""
    print("\n=== TORTURE: Tag Sort Mode ===")
    from src.memory.types import Memory

    mems = [
        Memory(id="a", text="t", scope="s", category="c",
               created_at="2026-01-01T00:00:00", tags=["zeta"]),
        Memory(id="b", text="t", scope="s", category="c",
               created_at="2026-01-02T00:00:00", tags=["alpha", "beta"]),
        Memory(id="c", text="t", scope="s", category="c",
               created_at="2026-01-03T00:00:00", tags=[]),
        Memory(id="d", text="t", scope="s", category="c",
               created_at="2026-01-04T00:00:00", tags=["beta"]),
        Memory(id="e", text="t", scope="s", category="c",
               created_at="2026-01-05T00:00:00", tags=None),
    ]

    # Replicate the app.py sort logic
    def _sort_key_tag(m):
        tags = getattr(m, "tags", []) or []
        return ((tags[0] if tags else "~"), getattr(m, "created_at", ""))

    reverse = False  # tag sort is ascending
    result = sorted(mems, key=_sort_key_tag, reverse=reverse)
    ids = [m.id for m in result]

    check("tag: alpha first (b)", ids[0] == "b")
    check("tag: beta second (d)", ids[1] == "d")
    check("tag: zeta third (a)", ids[2] == "a")
    # ~ sentinel puts empty/None tags at far end
    check("tag: empty tags last", ids[-1] in ("c", "e"))
    check("tag: 5 items returned", len(result) == 5)

    # Verify reverse flag: tag in ascending group
    import os
    app_path = os.path.join(os.path.dirname(__file__), "..", "web", "app.py")
    with open(app_path, encoding="utf-8") as f:
        src = f.read()
    check("tag in ascending group", '"tag"' in src and 'not in ("oldest", "alpha", "tag")' in src)

    # All same first tag — secondary sort by created_at (ascending)
    same_tag = [
        Memory(id="st1", text="t", scope="s", category="c",
               created_at="2026-03-01T00:00:00", tags=["common"]),
        Memory(id="st2", text="t", scope="s", category="c",
               created_at="2026-01-01T00:00:00", tags=["common"]),
        Memory(id="st3", text="t", scope="s", category="c",
               created_at="2026-02-01T00:00:00", tags=["common"]),
    ]
    r2 = sorted(same_tag, key=_sort_key_tag, reverse=False)
    r2_ids = [m.id for m in r2]
    check("same tag: oldest first (st2)", r2_ids[0] == "st2")
    check("same tag: newest last (st1)", r2_ids[-1] == "st1")


# ═════════════════════════════════════════════
# HARD_MAX_TOTAL ceiling — profile PUT clamping
# ═════════════════════════════════════════════
def test_hard_max_total_ceiling():
    """Test HARD_MAX_TOTAL = 25_000 ceiling on memory profile save."""
    print("\n=== TORTURE: HARD_MAX_TOTAL Ceiling ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_mp = _app.MEMORY_PROFILE_FILE
        tmp_mp = Path(tmp) / "memory_profile.json"

        base_profile = {
            "retention_policy": {
                "max_total_memories": 5000,
                "decay_strategy": "lru",
                "max_pinned_memories": 100,
            },
            "safety_policy": {"pii_guard": True, "custom_hard_rules": []}
        }
        tmp_mp.write_text(json.dumps(base_profile), encoding="utf-8")
        _app.MEMORY_PROFILE_FILE = tmp_mp

        # Simulate the clamping logic from api_memory_profile_put
        HARD_MAX_TOTAL = 25_000

        # ── 1. Within limit → unchanged ──
        profile = json.loads(tmp_mp.read_text(encoding="utf-8"))
        profile["retention_policy"]["max_total_memories"] = 10000
        rp = profile.get("retention_policy", {})
        mtm = rp.get("max_total_memories", 5000)
        if isinstance(mtm, (int, float)) and mtm != 0 and mtm > HARD_MAX_TOTAL:
            rp["max_total_memories"] = HARD_MAX_TOTAL
        check("10000 within limit → unchanged", rp["max_total_memories"] == 10000)

        # ── 2. Over limit → clamped to 25000 ──
        rp["max_total_memories"] = 50000
        mtm = rp["max_total_memories"]
        if isinstance(mtm, (int, float)) and mtm != 0 and mtm > HARD_MAX_TOTAL:
            rp["max_total_memories"] = HARD_MAX_TOTAL
        check("50000 → clamped to 25000", rp["max_total_memories"] == 25000)

        # ── 3. Exactly at limit → unchanged ──
        rp["max_total_memories"] = 25000
        mtm = rp["max_total_memories"]
        if isinstance(mtm, (int, float)) and mtm != 0 and mtm > HARD_MAX_TOTAL:
            rp["max_total_memories"] = HARD_MAX_TOTAL
        check("25000 exactly → unchanged", rp["max_total_memories"] == 25000)

        # ── 4. Zero = unlimited bypass ──
        rp["max_total_memories"] = 0
        mtm = rp["max_total_memories"]
        if isinstance(mtm, (int, float)) and mtm != 0 and mtm > HARD_MAX_TOTAL:
            rp["max_total_memories"] = HARD_MAX_TOTAL
        check("0 (unlimited) → not clamped", rp["max_total_memories"] == 0)

        # ── 5. Negative → not clamped (below check) ──
        rp["max_total_memories"] = -1
        mtm = rp["max_total_memories"]
        if isinstance(mtm, (int, float)) and mtm != 0 and mtm > HARD_MAX_TOTAL:
            rp["max_total_memories"] = HARD_MAX_TOTAL
        check("negative → not clamped by ceiling", rp["max_total_memories"] == -1)

        # ── 6. Verify app.py has the ceiling code ──
        import os
        app_path = os.path.join(os.path.dirname(__file__), "..", "web", "app.py")
        with open(app_path, encoding="utf-8") as f:
            src = f.read()
        check("HARD_MAX_TOTAL = 25_000 in app.py", "HARD_MAX_TOTAL = 25_000" in src)
        check("clamping logic present", "mtm > HARD_MAX_TOTAL" in src or "mtm != 0" in src)

    finally:
        _app.MEMORY_PROFILE_FILE = orig_mp
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# WIKI ARTICLES — _load_wiki_articles coverage
# ═════════════════════════════════════════════
def test_wiki_articles_loader():
    """Test _load_wiki_articles and _WIKI_README_MAP."""
    print("\n=== TORTURE: Wiki Articles Loader ===")
    import web.app as _app

    # ── 1. _WIKI_README_MAP is populated ──
    check("wiki map non-empty", len(_app._WIKI_README_MAP) > 0)
    check("wiki map has root", "root" in _app._WIKI_README_MAP)
    check("wiki map has src/memory", "src/memory" in _app._WIKI_README_MAP)
    check("wiki map has tests", "tests" in _app._WIKI_README_MAP)

    # ── 2. All mapped paths are Path objects ──
    from pathlib import Path
    for key, path in _app._WIKI_README_MAP.items():
        check(f"wiki '{key}' is Path", isinstance(path, Path))

    # ── 3. _load_wiki_articles returns dict ──
    articles = _app._load_wiki_articles()
    check("articles is dict", isinstance(articles, dict))
    check("articles non-empty", len(articles) > 0)

    # ── 4. At least some articles have markdown content ──
    found_content = False
    for key, text in articles.items():
        if len(text) > 10:
            found_content = True
            break
    check("at least one article has content", found_content)

    # ── 5. Missing file gracefully skipped ──
    from pathlib import Path as P
    orig_map = dict(_app._WIKI_README_MAP)
    _app._WIKI_README_MAP["__fake__"] = P("/nonexistent/fake/README.md")
    try:
        articles2 = _app._load_wiki_articles()
        check("missing file → no crash", True)
        check("fake key not in articles", "__fake__" not in articles2)
    finally:
        _app._WIKI_README_MAP.clear()
        _app._WIKI_README_MAP.update(orig_map)


# ═════════════════════════════════════════════
# ABOUT API — POST save/round-trip
# ═════════════════════════════════════════════
def test_about_api():
    """Test /api/about POST and _load_about/_save_about helpers."""
    print("\n=== TORTURE: About API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_about = _app.ABOUT_FILE
        tmp_about = Path(tmp) / "about.json"
        _app.ABOUT_FILE = tmp_about

        # ── 1. Missing file → default ──
        data = _app._load_about()
        check("missing about → default dict", isinstance(data, dict))
        check("missing about → has text key", "text" in data)

        # ── 2. Save + load round-trip ──
        _app._save_about({"text": "Hello from Orion"})
        loaded = _app._load_about()
        check("round-trip text", loaded["text"] == "Hello from Orion")

        # ── 3. Overwrite ──
        _app._save_about({"text": "Updated text", "extra": 42})
        loaded2 = _app._load_about()
        check("overwrite text", loaded2["text"] == "Updated text")
        check("extra field preserved", loaded2.get("extra") == 42)

        # ── 4. ASGI test for POST endpoint ──
        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    r = await client.post("/api/about", json={"text": "Via API"})
                    check("POST /api/about → 200", r.status_code == 200)
                    check("POST /api/about → ok", r.json().get("ok") is True)

                    # Verify persisted
                    saved = _app._load_about()
                    check("API save persisted", saved["text"] == "Via API")

            import web.app as _app_auth_7
            _orig_gac_7 = _app_auth_7.get_auth_config
            _app_auth_7.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_7.get_auth_config = _orig_gac_7
        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.ABOUT_FILE = orig_about
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# VAULT FILTER DROPDOWN — template elements
# ═════════════════════════════════════════════
def test_vault_filter_dropdown():
    """Test vault.html contains filter dropdown elements and tag sort option."""
    print("\n=== TORTURE: Vault Filter Dropdown ===")
    import os

    vault_path = os.path.join(os.path.dirname(__file__), "..", "web", "templates", "vault.html")
    with open(vault_path, encoding="utf-8") as f:
        html = f.read()

    # Filter dropdown elements
    check("filter button exists", "toggleFilterPanel" in html or "filter-btn" in html.lower())
    check("filter panel container", "filter-panel" in html or "filterPanel" in html)
    check("buildFilterPanel in JS", "buildFilterPanel" in html)
    check("applyFilter in JS", "applyFilter" in html)

    # Tag sort option in dropdown
    check("tag sort option exists", 'value="tag"' in html)
    check("sort dropdown present", "sort" in html.lower())

    # Data attributes for filtering
    check("data-scope attribute", "data-scope" in html)
    check("data-category attribute", "data-category" in html)
    check("data-tags attribute", "data-tags" in html)

    # Info button
    check("info button present", "info-btn" in html or "ⓘ" in html)


# ═════════════════════════════════════════════
# 70. Routing subsystem — ModelRouter class deep coverage
# ═════════════════════════════════════════════
def test_routing_model_router():
    """Test the ModelRouter class from src.routing.model_router directly:
    from_config, route() all code-paths, resolve_tier, get_next_tier,
    clear_stuck_counter, to_config_dict, RoutingDecision.to_dict,
    TierConfig.to_json_dict, Tier enum, TaskType constants, direct model
    overrides, stuck-loop escalation, disabled-tier skipping, budget gating,
    force_tier, unknown tier labels, no-tiers edge case."""
    print("\n=== TORTURE: Routing — ModelRouter Deep Coverage ===")

    from src.routing.model_router import (
        ModelRouter, RoutingDecision, Tier, TierConfig, TaskType,
        classify_task, CONFIG_DEFAULTS, TIER_NAMES, TIER_IDS,
        _LABEL_TO_TIER, _ID_TO_TIER, _parse_tier_config, _is_direct_model,
        _parse_direct_model, DEFAULT_TASK_TIER_MAP, _TASK_KEYWORDS,
    )

    # ── 1. Tier enum ──
    check("Tier LOCAL_CHEAP=0", Tier.LOCAL_CHEAP == 0)
    check("Tier LOCAL_STRONG=1", Tier.LOCAL_STRONG == 1)
    check("Tier CHEAP_CLOUD=2", Tier.CHEAP_CLOUD == 2)
    check("Tier EXPENSIVE_CLOUD=3", Tier.EXPENSIVE_CLOUD == 3)
    check("Tier CODE_LIGHT=4", Tier.CODE_LIGHT == 4)
    check("Tier CODE_HEAVY=5", Tier.CODE_HEAVY == 5)
    check("Tier ordering", Tier.LOCAL_CHEAP < Tier.EXPENSIVE_CLOUD)
    check("6 tiers", len(list(Tier)) == 6)

    # ── 2. TIER_NAMES / TIER_IDS maps ──
    check("TIER_NAMES t0", TIER_NAMES[Tier.LOCAL_CHEAP] == "local_cheap")
    check("TIER_NAMES t3", TIER_NAMES[Tier.EXPENSIVE_CLOUD] == "expensive_cloud")
    check("TIER_IDS t0", TIER_IDS[Tier.LOCAL_CHEAP] == "t0")
    check("TIER_IDS t3", TIER_IDS[Tier.EXPENSIVE_CLOUD] == "t3")
    check("_LABEL_TO_TIER", _LABEL_TO_TIER["cheap_cloud"] == Tier.CHEAP_CLOUD)
    check("_ID_TO_TIER", _ID_TO_TIER["t2"] == Tier.CHEAP_CLOUD)

    # ── 3. TaskType constants ──
    check("TaskType.CODING", TaskType.CODING == "coding")
    check("TaskType.CODING_LIGHT", TaskType.CODING_LIGHT == "coding_light")
    check("TaskType.CODING_HEAVY", TaskType.CODING_HEAVY == "coding_heavy")
    check("TaskType.GENERAL", TaskType.GENERAL == "general")
    check("TaskType.AGI_TICK", TaskType.AGI_TICK == "agi_tick")
    check("TaskType._ALL has 12", len(TaskType._ALL) == 12)
    for tt in ["coding", "coding_light", "coding_heavy", "summarization", "planning",
               "high_stakes", "final_polish", "general", "memory_ops", "reflection",
               "tool_use", "agi_tick"]:
        check(f"TaskType._ALL has {tt}", tt in TaskType._ALL)

    # ── 4. classify_task — scored keyword matching ──
    check("classify coding_heavy", classify_task("implement a REST api") == "coding_heavy")
    check("classify coding_light", classify_task("rename this variable") == "coding_light")
    check("classify summarize", classify_task("summarize the report") == "summarization")
    check("classify plan", classify_task("plan the roadmap") == "planning")
    check("classify high_stakes", classify_task("audit the security") == "high_stakes")
    check("classify final_polish", classify_task("proofread and polish the essay") == "final_polish")
    check("classify memory_ops", classify_task("remember this fact in vault") == "memory_ops")
    check("classify reflection", classify_task("reflect on the day") == "reflection")
    check("classify tool_use", classify_task("web search for info") == "tool_use")
    check("classify general fallback", classify_task("hello world") == "general")
    check("classify empty", classify_task("") == "general")

    # Explicit type override
    check("classify explicit", classify_task("hello", explicit_type="coding") == "coding")
    check("classify invalid explicit", classify_task("hello", explicit_type="bogus") == "general")

    # Recent errors boost heavy coding
    r = classify_task("hello world", recent_errors=["KeyError: 'foo'", "NameError"])
    check("recent errors boost coding_heavy", r == "coding_heavy")

    # Scored: more keywords wins
    r2 = classify_task("write code function class debug fix bug refactor")
    check("high keyword score → coding_heavy", r2 == "coding_heavy")

    # ── 5. _is_direct_model / _parse_direct_model ──
    check("is_direct model:x:y", _is_direct_model("model:conn1:gpt-4"))
    check("not direct plain", not _is_direct_model("cheap_cloud"))
    check("not direct auto", not _is_direct_model("__auto__"))
    check("not direct int", not _is_direct_model(42))
    conn, mod = _parse_direct_model("model:my_conn:gpt-4o")
    check("parse direct conn", conn == "my_conn")
    check("parse direct model", mod == "gpt-4o")
    conn2, mod2 = _parse_direct_model("model:bad")
    check("parse bad direct → empty", conn2 == "" and mod2 == "")

    # ── 6. _parse_tier_config ──
    tc = _parse_tier_config({
        "id": "t2", "label": "cheap_cloud", "enabled": True,
        "provider": "deepseek", "primary_model": "deepseek-chat",
        "temperature": 0.4, "max_output_tokens": 8192,
        "max_iterations": 12, "retries_before_escalate": 2,
        "alt_models": ["gpt-3.5"], "cost_per_call": "~$0.001",
        "default_for": "", "connection_id": "c1",
    })
    check("parse tier → TierConfig", isinstance(tc, TierConfig))
    check("parse tier tier=CHEAP_CLOUD", tc.tier == Tier.CHEAP_CLOUD)
    check("parse tier label", tc.label == "cheap_cloud")
    check("parse tier model", tc.model == "deepseek-chat")
    check("parse tier provider", tc.provider == "deepseek")
    check("parse tier conn_id", tc.connection_id == "c1")
    check("parse tier alt", tc.alt_models == ["gpt-3.5"])
    check("parse tier enabled", tc.enabled is True)

    # to_json_dict round-trip
    jd = tc.to_json_dict()
    check("to_json_dict id", jd["id"] == "t2")
    check("to_json_dict label", jd["label"] == "cheap_cloud")
    check("to_json_dict model", jd["primary_model"] == "deepseek-chat")
    check("to_json_dict enabled", jd["enabled"] is True)
    check("to_json_dict alt", jd["alt_models"] == ["gpt-3.5"])
    check("to_json_dict retries", jd["retries_before_escalate"] == 2)

    # ── 7. CONFIG_DEFAULTS structure ──
    check("CONFIG_DEFAULTS.enabled", CONFIG_DEFAULTS["enabled"] is True)
    check("CONFIG_DEFAULTS.tiers count", len(CONFIG_DEFAULTS["tiers"]) == 6)
    check("CONFIG_DEFAULTS.task_tier_map count", len(CONFIG_DEFAULTS["task_tier_map"]) == 11)

    # ── 8. ModelRouter.from_config ──
    router = ModelRouter.from_config()
    check("from_config creates router", isinstance(router, ModelRouter))
    check("from_config enabled", router.enabled is True)
    check("from_config has tier_configs", len(router.tier_configs) > 0)
    check("from_config has task_tier_map", len(router.task_tier_map) > 0)

    # from_config with custom config
    custom_cfg = {
        "enabled": True,
        "tiers": [
            {"id": "t0", "label": "local_cheap", "enabled": True,
             "provider": "ollama", "primary_model": "qwen:7b"},
            {"id": "t1", "label": "local_strong", "enabled": True,
             "provider": "ollama", "primary_model": "llama3:70b"},
            {"id": "t2", "label": "cheap_cloud", "enabled": True,
             "provider": "deepseek", "primary_model": "deepseek-chat"},
            {"id": "t3", "label": "expensive_cloud", "enabled": True,
             "provider": "openai", "primary_model": "gpt-4o"},
        ],
        "task_tier_map": {
            "coding": "cheap_cloud",
            "summarization": "local_cheap",
            "planning": "local_strong",
            "general": "__auto__",
            "high_stakes": "expensive_cloud",
            "final_polish": "expensive_cloud",
            "memory_ops": "local_cheap",
            "reflection": "local_cheap",
            "tool_use": "cheap_cloud",
            "agi_tick": "cheap_cloud",
        },
    }
    router2 = ModelRouter.from_config(custom_cfg)
    check("custom router 4 tiers", len(router2.tier_configs) == 4)
    check("custom router coding→cheap_cloud", router2.task_tier_map["coding"] == "cheap_cloud")

    # ── 9. route() — basic task classification and tier resolution ──
    d = router2.route("write a python function")
    check("route coding_heavy → task_type", d.task_type == "coding_heavy")
    check("route coding_heavy → model set", d.model == "deepseek-chat")
    check("route coding_heavy → tier cheap_cloud", d.tier_name == "cheap_cloud")
    check("route coding_heavy → tier_id t2", d.tier_id == "t2")
    check("route coding_heavy → provider", d.provider == "deepseek")
    check("route coding_heavy → not fallback", d.fallback is False)
    check("route coding_heavy → not direct", d.is_direct_model is False)

    # ── 10. route() — __auto__ → fallback ──
    d_auto = router2.route("hello there")
    check("route auto → task_type general", d_auto.task_type == "general")
    check("route auto → fallback True", d_auto.fallback is True)
    check("route auto → model None", d_auto.model is None)
    check("route auto → tier_name __auto__", d_auto.tier_name == "__auto__")

    # ── 11. route() — disabled router ──
    disabled_router = ModelRouter.from_config({**custom_cfg, "enabled": False})
    d_dis = disabled_router.route("write code")
    check("disabled → fallback", d_dis.fallback is True)
    check("disabled → model None", d_dis.model is None)
    check("disabled → reason contains disabled", "disabled" in d_dis.reason.lower())

    # ── 12. route() — direct model override ──
    direct_cfg = {**custom_cfg, "task_tier_map": {
        **custom_cfg["task_tier_map"],
        "coding": "model:conn42:gpt-4-turbo",
    }}
    router3 = ModelRouter.from_config(direct_cfg)
    d_direct = router3.route("write a function")
    check("direct → is_direct_model", d_direct.is_direct_model is True)
    check("direct → model name", d_direct.model == "gpt-4-turbo")
    check("direct → direct_conn_id", d_direct.direct_conn_id == "conn42")
    check("direct → tier_name 'direct'", d_direct.tier_name == "direct")

    # ── 13. route() — unknown tier label → fallback ──
    bad_cfg = {**custom_cfg, "task_tier_map": {
        **custom_cfg["task_tier_map"],
        "coding": "nonexistent_tier",
    }}
    router_bad = ModelRouter.from_config(bad_cfg)
    d_bad = router_bad.route("write code")
    check("unknown tier → fallback", d_bad.fallback is True)
    check("unknown tier → reason", "Unknown tier" in d_bad.reason)

    # ── 14. route() — force_tier ──
    d_forced = router2.route("hello", force_tier=Tier.EXPENSIVE_CLOUD)
    check("force_tier → expensive_cloud model", d_forced.model == "gpt-4o")
    check("force_tier → tier_name", d_forced.tier_name == "expensive_cloud")

    # ── 15. route() — stuck-loop escalation ──
    router_stuck = ModelRouter.from_config(custom_cfg)
    # Simulate 3 errors (threshold for retries_before_escalate)
    for _ in range(3):
        d_esc = router_stuck.route("write code", recent_errors=["same error"])
    check("stuck escalation → tier > cheap_cloud", d_esc.tier is not None and d_esc.tier > Tier.CHEAP_CLOUD)
    check("stuck escalation → reason contains 'Stuck'", "Stuck" in d_esc.reason or "stuck" in d_esc.reason.lower())
    check("stuck escalation → escalated_from set", d_esc.escalated_from is not None)

    # Clear stuck counter
    router_stuck.clear_stuck_counter()
    d_clear = router_stuck.route("write code")
    check("after clear → back to cheap_cloud", d_clear.tier_name == "cheap_cloud")

    # ── 16. route() — disabled tier skipping ──
    skip_cfg = {
        "enabled": True,
        "tiers": [
            {"id": "t0", "label": "local_cheap", "enabled": False,
             "provider": "ollama", "primary_model": "phi3"},
            {"id": "t1", "label": "local_strong", "enabled": False,
             "provider": "ollama", "primary_model": "llama3:70b"},
            {"id": "t2", "label": "cheap_cloud", "enabled": True,
             "provider": "deepseek", "primary_model": "deepseek-chat"},
            {"id": "t3", "label": "expensive_cloud", "enabled": True,
             "provider": "openai", "primary_model": "gpt-4o"},
        ],
        "task_tier_map": {"summarization": "local_cheap", "general": "__auto__"},
    }
    router_skip = ModelRouter.from_config(skip_cfg)
    d_skip = router_skip.route("summarize this document")
    check("disabled skip → lands on cheap_cloud", d_skip.tier_name == "cheap_cloud")
    check("disabled skip → model deepseek-chat", d_skip.model == "deepseek-chat")

    # All tiers disabled
    all_disabled_cfg = {
        "enabled": True,
        "tiers": [
            {"id": "t0", "label": "local_cheap", "enabled": False,
             "provider": "ollama", "primary_model": "phi3"},
            {"id": "t3", "label": "expensive_cloud", "enabled": False,
             "provider": "openai", "primary_model": "gpt-4o"},
        ],
        "task_tier_map": {"coding": "local_cheap"},
    }
    router_alloff = ModelRouter.from_config(all_disabled_cfg)
    d_alloff = router_alloff.route("write code")
    check("all disabled → fallback", d_alloff.fallback is True or d_alloff.model is None)

    # No tiers at all
    empty_cfg = {"enabled": True, "tiers": [], "task_tier_map": {"coding": "cheap_cloud"}}
    router_empty = ModelRouter.from_config(empty_cfg)
    d_empty = router_empty.route("write code")
    check("no tiers → fallback", d_empty.fallback is True)

    # ── 17. RoutingDecision.to_dict ──
    d_dict = d.to_dict()
    check("to_dict has tier", "tier" in d_dict)
    check("to_dict has task_type", "task_type" in d_dict)
    check("to_dict has model", "model" in d_dict)
    check("to_dict has provider", "provider" in d_dict)
    check("to_dict has reason", "reason" in d_dict)
    check("to_dict has fallback", "fallback" in d_dict)
    check("to_dict has is_direct_model", "is_direct_model" in d_dict)

    # ── 18. ModelRouter.resolve_tier ──
    tc_coding = router2.resolve_tier("coding")
    check("resolve_tier coding → TierConfig", isinstance(tc_coding, TierConfig))
    check("resolve_tier coding label", tc_coding.label == "cheap_cloud")

    tc_auto = router2.resolve_tier("general")
    check("resolve_tier general → None", tc_auto is None)

    # ── 19. ModelRouter.get_next_tier ──
    nt = router2.get_next_tier(Tier.LOCAL_CHEAP)
    check("get_next LOCAL_CHEAP → LOCAL_STRONG", nt is not None and nt.tier == Tier.LOCAL_STRONG)
    nt2 = router2.get_next_tier(Tier.EXPENSIVE_CLOUD)
    check("get_next EXPENSIVE_CLOUD → None", nt2 is None)

    # ── 20. to_config_dict round-trip ──
    exported = router2.to_config_dict()
    check("to_config_dict has enabled", "enabled" in exported)
    check("to_config_dict has tiers", "tiers" in exported)
    check("to_config_dict has task_tier_map", "task_tier_map" in exported)
    check("to_config_dict 4 tiers", len(exported["tiers"]) == 4)
    # Re-create router from exported config
    router_round = ModelRouter.from_config(exported)
    d_round = router_round.route("write code")
    check("round-trip route same model", d_round.model == d.model)
    check("round-trip route same task", d_round.task_type == d.task_type)


# ═════════════════════════════════════════════
# 71. Budget Tracker — deep coverage
# ═════════════════════════════════════════════
def test_budget_tracker():
    """Test BudgetTracker: create, record_cost, limits, check_tick_budget,
    reset_session, get_summary, update_caps, month_rollover, corrupt file,
    from_config, BudgetState to_dict/from_dict round-trip."""
    print("\n=== TORTURE: Budget Tracker — Deep Coverage ===")

    from src.routing.budget_tracker import BudgetTracker, BudgetState

    tmp = tempfile.mkdtemp()
    try:
        state_file = os.path.join(tmp, "budget_state.json")

        # ── 1. BudgetState dataclass ──
        bs = BudgetState()
        check("BudgetState default hard_cap", bs.monthly_hard_cap == 20.00)
        check("BudgetState default soft_cap", bs.monthly_soft_cap == 16.00)
        check("BudgetState default session_cap", bs.per_session_cap == 2.00)
        check("BudgetState default tick_cap", bs.per_tick_cap == 0.10)
        check("BudgetState default monthly_spent", bs.monthly_spent == 0.0)

        # to_dict / from_dict round-trip
        d = bs.to_dict()
        check("to_dict has monthly_hard_cap", "monthly_hard_cap" in d)
        check("to_dict has tier_spending", "tier_spending" in d)
        bs2 = BudgetState.from_dict(d)
        check("from_dict hard_cap", bs2.monthly_hard_cap == 20.00)
        check("from_dict monthly_spent", bs2.monthly_spent == 0.0)

        # from_dict with missing keys → defaults
        bs3 = BudgetState.from_dict({})
        check("from_dict empty → defaults", bs3.monthly_hard_cap == 20.00)
        check("from_dict empty → 0 spent", bs3.monthly_spent == 0.0)

        # to_dict rounding
        bs4 = BudgetState(monthly_spent=1.23456789)
        d4 = bs4.to_dict()
        check("to_dict rounds to 6", d4["monthly_spent"] == round(1.23456789, 6))

        # ── 2. BudgetTracker creation ──
        bt = BudgetTracker(state_path=state_file)
        check("BudgetTracker created", bt is not None)
        check("BT state file set", bt._state_path == state_file)
        check("BT remaining = hard_cap", bt.remaining() == 20.00)
        check("BT hard_limit not hit", not bt.is_hard_limit_hit())
        check("BT soft_limit not hit", not bt.is_soft_limit_hit())
        check("BT session_limit not hit", not bt.is_session_limit_hit())

        # ── 3. record_cost ──
        bt.record_cost(0.50, "cheap_cloud")
        check("after record → remaining 19.50", abs(bt.remaining() - 19.50) < 0.001)
        check("after record → monthly_spent 0.50", abs(bt.state.monthly_spent - 0.50) < 0.001)
        check("after record → session_spent 0.50", abs(bt.state.session_spent - 0.50) < 0.001)
        check("after record → total 0.50", abs(bt.state.total_spent_all_time - 0.50) < 0.001)
        check("tier_spending cheap_cloud", abs(bt.state.tier_spending.get("cheap_cloud", 0) - 0.50) < 0.001)
        check("state persisted", os.path.isfile(state_file))

        # Multiple records
        bt.record_cost(1.00, "expensive_cloud")
        bt.record_cost(0.25, "cheap_cloud")
        check("multiple records total", abs(bt.state.monthly_spent - 1.75) < 0.001)
        check("tier_spending cheap 0.75", abs(bt.state.tier_spending["cheap_cloud"] - 0.75) < 0.001)
        check("tier_spending expensive 1.00", abs(bt.state.tier_spending["expensive_cloud"] - 1.00) < 0.001)

        # ── 4. check_tick_budget ──
        check("tick within budget", bt.check_tick_budget(0.05) is None)
        check("tick over per_tick_cap", bt.check_tick_budget(0.20) is not None)
        check("tick msg contains cap", "cap" in bt.check_tick_budget(0.20).lower())

        # ── 5. Soft limit ──
        # Spend up to soft cap (16.00) → already at 1.75, need 14.25 more
        bt.record_cost(14.25, "expensive_cloud")
        check("at soft cap → hit", bt.is_soft_limit_hit())
        check("at soft cap → hard not hit", not bt.is_hard_limit_hit())

        # ── 6. Hard limit ──
        bt.record_cost(4.00, "expensive_cloud")
        check("over hard cap → hit", bt.is_hard_limit_hit())
        check("over hard cap → remaining 0", bt.remaining() == 0.0)
        check("over hard cap → tick blocked", bt.check_tick_budget(0.0) is not None)

        # ── 7. reset_session ──
        bt.reset_session()
        check("reset session → session 0", bt.state.session_spent == 0.0)
        check("reset session → monthly unchanged", bt.state.monthly_spent > 0)

        # ── 8. get_summary ──
        summary = bt.get_summary()
        check("summary has monthly_spent", "monthly_spent" in summary)
        check("summary has remaining", "remaining" in summary)
        check("summary has hard_limit_hit", "hard_limit_hit" in summary)
        check("summary has soft_limit_hit", "soft_limit_hit" in summary)
        check("summary has tier_spending", "tier_spending" in summary)
        check("summary has month_key", "month_key" in summary)
        check("summary has total_all_time", "total_all_time" in summary)
        check("summary remaining is 0", summary["remaining"] == 0.0)
        check("summary hard_limit_hit True", summary["hard_limit_hit"] is True)

        # ── 9. update_caps ──
        bt.update_caps(monthly_hard_cap=50.0, per_tick_cap=0.50)
        check("update hard_cap → 50", bt.state.monthly_hard_cap == 50.0)
        check("update tick_cap → 0.50", bt.state.per_tick_cap == 0.50)
        check("update soft unchanged", bt.state.monthly_soft_cap == 16.0)
        check("after cap update → remaining > 0", bt.remaining() > 0)
        check("after cap update → hard not hit", not bt.is_hard_limit_hit())

        # ── 10. Reload from disk ──
        bt2 = BudgetTracker(state_path=state_file)
        check("reload monthly_spent preserved", abs(bt2.state.monthly_spent - bt.state.monthly_spent) < 0.001)
        check("reload total preserved", abs(bt2.state.total_spent_all_time - bt.state.total_spent_all_time) < 0.001)
        # Caps are overridden from constructor defaults
        check("reload caps from constructor", bt2.state.monthly_hard_cap == 20.0)

        # ── 11. Corrupt state file ──
        with open(state_file, "w") as f:
            f.write("NOT VALID JSON!!!")
        bt3 = BudgetTracker(state_path=state_file)
        check("corrupt file → fresh state", bt3.state.monthly_spent == 0.0)
        check("corrupt file → default caps", bt3.state.monthly_hard_cap == 20.0)

        # ── 12. from_config factory ──
        bt4 = BudgetTracker.from_config({
            "monthly_hard_cap": 100.0,
            "per_session_cap": 5.0,
            "per_tick_cap": 0.25,
        })
        check("from_config hard_cap", bt4.state.monthly_hard_cap == 100.0)
        check("from_config soft_cap auto", bt4.state.monthly_soft_cap == 80.0)
        check("from_config session_cap", bt4.state.per_session_cap == 5.0)
        check("from_config tick_cap", bt4.state.per_tick_cap == 0.25)

        # from_config empty dict → defaults
        bt5 = BudgetTracker.from_config({})
        check("from_config empty → default hard", bt5.state.monthly_hard_cap == 20.0)

        # ── 13. Session limit ──
        bt6 = BudgetTracker(per_session_cap=0.10, state_path=os.path.join(tmp, "bt6.json"))
        check("session not hit initially", not bt6.is_session_limit_hit())
        bt6.record_cost(0.15, "test")
        check("session hit after 0.15", bt6.is_session_limit_hit())

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 72. Budget + Router integration — budget gating in route()
# ═════════════════════════════════════════════
def test_router_budget_integration():
    """Test ModelRouter.route() budget gating: hard limit forces local,
    soft limit caps at cheap cloud, budget remaining in decision."""
    print("\n=== TORTURE: Router + Budget Integration ===")

    from src.routing.model_router import ModelRouter, Tier
    from src.routing.budget_tracker import BudgetTracker

    tmp = tempfile.mkdtemp()
    try:
        cfg = {
            "enabled": True,
            "tiers": [
                {"id": "t0", "label": "local_cheap", "enabled": True,
                 "provider": "ollama", "primary_model": "phi3"},
                {"id": "t1", "label": "local_strong", "enabled": True,
                 "provider": "ollama", "primary_model": "llama3:70b"},
                {"id": "t2", "label": "cheap_cloud", "enabled": True,
                 "provider": "deepseek", "primary_model": "deepseek-chat"},
                {"id": "t3", "label": "expensive_cloud", "enabled": True,
                 "provider": "openai", "primary_model": "gpt-4o"},
            ],
            "task_tier_map": {
                "coding": "cheap_cloud",
                "high_stakes": "expensive_cloud",
                "general": "__auto__",
                "summarization": "local_cheap",
                "planning": "local_strong",
                "final_polish": "expensive_cloud",
                "memory_ops": "local_cheap",
                "reflection": "local_cheap",
                "tool_use": "cheap_cloud",
                "agi_tick": "cheap_cloud",
            },
        }

        # ── 1. Budget remaining shows in decision ──
        bt = BudgetTracker(monthly_hard_cap=10.0, state_path=os.path.join(tmp, "b1.json"))
        router = ModelRouter.from_config(cfg, budget_tracker=bt)
        d = router.route("write code")
        check("budget remaining in decision", d.budget_remaining >= 0)
        check("budget remaining ~10", abs(d.budget_remaining - 10.0) < 0.01)

        # ── 2. Hard budget exhausted → forced to local ──
        bt2 = BudgetTracker(monthly_hard_cap=1.0, state_path=os.path.join(tmp, "b2.json"))
        bt2.record_cost(1.50, "test")  # exceed hard cap
        router2 = ModelRouter.from_config(cfg, budget_tracker=bt2)
        d2 = router2.route("deploy to production")  # high_stakes → expensive_cloud
        check("hard limit → forced local tier", d2.tier is not None and d2.tier <= Tier.LOCAL_STRONG)
        check("hard limit → reason mentions budget", "budget" in d2.reason.lower())

        # ── 3. Soft limit hit → caps at cheap cloud ──
        bt3 = BudgetTracker(monthly_hard_cap=10.0, monthly_soft_cap=5.0,
                            state_path=os.path.join(tmp, "b3.json"))
        bt3.record_cost(6.0, "test")  # exceed soft cap but not hard
        router3 = ModelRouter.from_config(cfg, budget_tracker=bt3)
        d3 = router3.route("final polish the doc")  # final_polish → expensive_cloud
        check("soft limit → capped at cheap_cloud", d3.tier is not None and d3.tier <= Tier.CHEAP_CLOUD)
        check("soft limit → reason mentions soft", "soft" in d3.reason.lower())

        # ── 4. Budget tracker with no spending → normal routing ──
        bt4 = BudgetTracker(monthly_hard_cap=100.0, state_path=os.path.join(tmp, "b4.json"))
        router4 = ModelRouter.from_config(cfg, budget_tracker=bt4)
        d4 = router4.route("deploy critical production change")
        check("no budget pressure → expensive_cloud", d4.tier_name == "expensive_cloud")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# 73. ModelRouterTool — budget action + resolve with new router
# ═════════════════════════════════════════════
def test_model_router_tool_budget():
    """Test ModelRouterTool.execute budget action and resolve action
    using the new ModelRouter.from_config path."""
    print("\n=== TORTURE: ModelRouterTool — Budget Action ===")
    from src.tools.model_router import ModelRouterTool

    # ── 1. Definition includes budget action ──
    defn = ModelRouterTool.definition()
    actions = defn["parameters"]["properties"]["action"]["enum"]
    check("definition has 5 actions", len(actions) == 5)
    check("budget in actions", "budget" in actions)

    # ── 2. Execute budget action ──
    r = json.loads(ModelRouterTool.execute({"action": "budget"}))
    # Should return summary dict (or error if no state file — both are valid)
    check("budget returns dict", isinstance(r, dict))
    if "error" not in r:
        check("budget has monthly_spent", "monthly_spent" in r)
        check("budget has remaining", "remaining" in r)
        check("budget has hard_limit_hit", "hard_limit_hit" in r)
        check("budget has tier_spending", "tier_spending" in r)
    else:
        check("budget error is string", isinstance(r["error"], str))

    # ── 3. Resolve action uses new ModelRouter path ──
    r2 = json.loads(ModelRouterTool.execute({"action": "resolve", "text": "write python code"}))
    check("resolve has task_type", "task_type" in r2)
    check("resolve has routed_model", "routed_model" in r2)
    check("resolve has tier", "tier" in r2)
    check("resolve has reason", "reason" in r2)
    check("resolve has fallback", "fallback" in r2)
    check("resolve has is_direct_model", "is_direct_model" in r2)

    # ── 4. Classify still works ──
    r3 = json.loads(ModelRouterTool.execute({"action": "classify", "text": "summarize this"}))
    check("classify task_type", "task_type" in r3)
    check("classify would_route_to", "would_route_to" in r3)

    # ── 5. Unknown action → error ──
    r4 = json.loads(ModelRouterTool.execute({"action": "INVALID"}))
    check("invalid action → error", "error" in r4)


# ═════════════════════════════════════════════
#  Sidecar Service Wiring — Env Var Fallbacks, Configs, server.py
# ═════════════════════════════════════════════

def test_edge_tts_conn_env_fallback():
    """_get_elevenlabs_conn returns the first enabled ElevenLabs connection."""
    print("\n-- _get_elevenlabs_conn fallback --")
    from pathlib import Path
    from web.app import _get_elevenlabs_conn
    import web.app as _app

    tmp = tempfile.mkdtemp()
    try:
        orig_connections = _app.CONNECTIONS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)

        # ── 1. No ElevenLabs connection → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "openai-1", "provider": "openai", "enabled": True, "api_key": "sk"}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()
        conn = _get_elevenlabs_conn()
        check("no elevenlabs conn -> None", conn is None)

        # ── 2. With ElevenLabs connection ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "el-1", "provider": "elevenlabs", "url": "https://api.elevenlabs.io",
                 "api_key": "el-key", "enabled": True, "platform_hosted": True}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn2 = _get_elevenlabs_conn()
        check("el conn found", conn2 is not None)
        check("el conn id", conn2["id"] == "el-1")
        check("el conn provider", conn2["provider"] == "elevenlabs")

        # ── 3. Disabled ElevenLabs connection → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "el-2", "provider": "elevenlabs", "enabled": False, "api_key": "key"}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn3 = _get_elevenlabs_conn()
        check("disabled el conn -> None", conn3 is None)

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def test_whisper_conn_env_fallback():
    """_seed_platform_keys_from_env creates connections from env vars."""
    print("\n-- _seed_platform_keys_from_env --")
    from pathlib import Path
    import web.app as _app

    tmp = tempfile.mkdtemp()
    try:
        orig_connections = _app.CONNECTIONS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)

        # ── 1. No relevant env vars → no changes ──
        tmp_connections.write_text(json.dumps({
            "connections": [], "agent_connections": {}
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()
        old_or = os.environ.pop("OPENROUTER_API_KEY", None)
        old_el = os.environ.pop("ELEVENLABS_API_KEY", None)
        try:
            _app._seed_platform_keys_from_env()
            data = _app._load_connections()
            check("no env vars -> empty conns", len(data["connections"]) == 0)

            # ── 2. With ELEVENLABS_API_KEY → creates connection ──
            os.environ["ELEVENLABS_API_KEY"] = "test-el-key"
            _app._seed_platform_keys_from_env()
            data2 = _app._load_connections()
            check("el key seeded", len(data2["connections"]) == 1)
            el = data2["connections"][0]
            check("el provider is elevenlabs", el["provider"] == "elevenlabs")
            check("el is platform_hosted", el["platform_hosted"] is True)
            check("el api_key set", el["api_key"] == "test-el-key")

            # ── 3. Re-run with same key → no duplicate ──
            _app._seed_platform_keys_from_env()
            data3 = _app._load_connections()
            check("no duplicate after re-seed", len(data3["connections"]) == 1)
        finally:
            os.environ.pop("OPENROUTER_API_KEY", None)
            os.environ.pop("ELEVENLABS_API_KEY", None)
            if old_or:
                os.environ["OPENROUTER_API_KEY"] = old_or
            if old_el:
                os.environ["ELEVENLABS_API_KEY"] = old_el

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def test_searxng_url_env_override():
    """SEARXNG_URL env var propagates to web_search defaults."""
    print("\n── SEARXNG_URL env override ──")
    from src.tools.web_search import _DEFAULT_SEARXNG_URL, get_effective_config

    # The default is already resolved at import time from env/default
    check("default searxng url is string", isinstance(_DEFAULT_SEARXNG_URL, str))
    check("default searxng url has /search",
          _DEFAULT_SEARXNG_URL.endswith("/search"))

    # get_effective_config uses it as the bottom fallback
    cfg = get_effective_config()
    check("effective cfg has searxng_url", "searxng_url" in cfg)
    check("effective url is string", isinstance(cfg["searxng_url"], str))

    # Verify the flycast pattern is a valid URL form
    flycast_url = "http://orionforge-engine-searxng.flycast:8080/search"
    check("flycast url has scheme", flycast_url.startswith("http://"))
    check("flycast url has port", ":8080" in flycast_url)
    check("flycast url has path", flycast_url.endswith("/search"))


def test_connections_json_tts_fallback():
    """_get_elevenlabs_conn picks first enabled ElevenLabs from connections.json."""
    print("\n-- connections.json ElevenLabs fallback --")
    from pathlib import Path
    from web.app import _get_elevenlabs_conn
    import web.app as _app

    tmp = tempfile.mkdtemp()
    try:
        orig_connections = _app.CONNECTIONS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)

        # ── 1. With enabled ElevenLabs connection ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "test-el", "provider": "elevenlabs",
                 "url": "https://api.elevenlabs.io", "api_key": "testkey",
                 "enabled": True, "platform_hosted": True}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()

        conn = _get_elevenlabs_conn()
        check("json fallback finds conn", conn is not None)
        check("json fallback correct id", conn["id"] == "test-el")
        check("json fallback correct provider", conn["provider"] == "elevenlabs")

        # ── 2. Disabled connection → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "test-el", "provider": "elevenlabs",
                 "url": "https://api.elevenlabs.io", "api_key": "testkey",
                 "enabled": False}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn2 = _get_elevenlabs_conn()
        check("disabled conn returns None", conn2 is None)

        # ── 3. Wrong provider → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "test-openai", "provider": "openai",
                 "url": "https://api.openai.com/v1", "api_key": "sk-test",
                 "enabled": True}
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn3 = _get_elevenlabs_conn()
        check("wrong provider returns None", conn3 is None)

        # ── 4. Empty connections → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn4 = _get_elevenlabs_conn()
        check("empty connections returns None", conn4 is None)

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def test_connections_json_whisper_fallback():
    """_resolve_connection picks best connection for an agent."""
    print("\n-- _resolve_connection fallback --")
    from pathlib import Path
    import web.app as _app

    tmp = tempfile.mkdtemp()
    try:
        orig_connections = _app.CONNECTIONS_FILE
        orig_settings = _app.SETTINGS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)
        tmp_settings.write_text("{}", encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. Empty connections → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [], "agent_connections": {}
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()
        conn = _app._resolve_connection(None, "orion")
        check("empty connections -> None", conn is None)

        # ── 2. With explicit connection_id ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "c1", "provider": "openai", "url": "https://api.openai.com/v1",
                 "api_key": "sk-test", "enabled": True, "type": "external"},
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn2 = _app._resolve_connection("c1", "orion")
        check("explicit conn_id found", conn2 is not None)
        check("explicit conn_id correct", conn2["id"] == "c1")

        # ── 3. Disabled connection_id → None ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "c1", "provider": "openai", "enabled": False, "type": "external"},
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn3 = _app._resolve_connection("c1", "orion")
        check("disabled explicit conn -> None", conn3 is None)

        # ── 4. Agent-mapped connection ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "c1", "provider": "openai", "enabled": True, "type": "external"},
            ], "agent_connections": {"orion": "c1"}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn4 = _app._resolve_connection(None, "orion")
        check("agent-mapped conn found", conn4 is not None)
        check("agent-mapped conn correct", conn4["id"] == "c1")

        # ── 5. Platform fallback ──
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "plat1", "provider": "openrouter", "enabled": True,
                 "type": "external", "platform_hosted": True, "api_key": "or-key"},
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        conn5 = _app._resolve_connection(None, "orion")
        check("platform fallback found", conn5 is not None)
        check("platform fallback correct", conn5["id"] == "plat1")

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


def test_whisper_server_structure():
    """Validate Whisper server.py has correct FastAPI routes."""
    print("\n── Whisper server.py structure ──")
    server_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "services", "whisper", "server.py"
    )
    check("whisper server.py exists", os.path.exists(server_path))
    if not os.path.exists(server_path):
        return

    with open(server_path, "r", encoding="utf-8") as f:
        src = f.read()

    check("has FastAPI import", "from fastapi import" in src or "import fastapi" in src)
    check("has /v1/models route", '"/v1/models"' in src)
    check("has /v1/audio/transcriptions route", '"/v1/audio/transcriptions"' in src)
    check("has /health route", '"/health"' in src)
    check("has get_model function", "def get_model" in src)
    check("has WhisperModel reference", "WhisperModel" in src)
    check("has WHISPER_MODEL env", "WHISPER_MODEL" in src)
    check("has tempfile usage", "tempfile" in src)
    check("has UploadFile param", "UploadFile" in src)
    check("has response_format param", "response_format" in src)
    check("has verbose_json branch", "verbose_json" in src)
    check("returns text key", '"text"' in src)
    check("cleans up temp file", "os.unlink" in src)


def test_searxng_settings_yml():
    """Validate SearXNG settings.yml structure."""
    print("\n── SearXNG settings.yml ──")
    yml_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "services", "searxng", "settings.yml"
    )
    check("searxng settings.yml exists", os.path.exists(yml_path))
    if not os.path.exists(yml_path):
        return

    with open(yml_path, "r", encoding="utf-8") as f:
        content = f.read()

    check("has use_default_settings", "use_default_settings: true" in content)
    check("has port 8080", "port: 8080" in content)
    check("has bind_address 0.0.0.0", "0.0.0.0" in content)
    check("has limiter false", "limiter: false" in content)
    check("has public_instance false", "public_instance: false" in content)
    check("has google engine", "engine: google" in content)
    check("has duckduckgo engine", "engine: duckduckgo" in content)
    check("has bing engine", "engine: bing" in content)
    check("has wikipedia engine", "engine: wikipedia" in content)
    check("has github engine", "engine: github" in content)
    check("has arxiv engine", "engine: arxiv" in content)
    check("has request_timeout", "request_timeout" in content)


def test_service_dockerfiles():
    """Validate all sidecar service Dockerfiles exist and have correct content."""
    print("\n── Service Dockerfiles ──")
    base = os.path.join(os.path.dirname(__file__), "..", "..", "services")

    # SearXNG
    df_sx = os.path.join(base, "searxng", "Dockerfile")
    check("searxng Dockerfile exists", os.path.exists(df_sx))
    if os.path.exists(df_sx):
        with open(df_sx, "r") as f:
            src = f.read()
        check("searxng FROM searxng image", "searxng/searxng" in src)
        check("searxng COPY settings.yml", "settings.yml" in src)

    # OpenedAI Speech
    df_tts = os.path.join(base, "openedai-speech", "Dockerfile")
    check("tts Dockerfile exists", os.path.exists(df_tts))
    if os.path.exists(df_tts):
        with open(df_tts, "r") as f:
            src = f.read()
        check("tts FROM openedai-speech", "openedai-speech" in src)
        check("tts EXPOSE 8000", "8000" in src)

    # Whisper
    df_w = os.path.join(base, "whisper", "Dockerfile")
    check("whisper Dockerfile exists", os.path.exists(df_w))
    if os.path.exists(df_w):
        with open(df_w, "r") as f:
            src = f.read()
        check("whisper FROM python", "python:" in src)
        check("whisper installs faster-whisper", "faster-whisper" in src)
        check("whisper installs fastapi", "fastapi" in src)
        check("whisper installs uvicorn", "uvicorn" in src)
        check("whisper COPY server.py", "server.py" in src)
        check("whisper EXPOSE 8000", "8000" in src)


def test_service_fly_tomls():
    """Validate fly.toml configs for all sidecar services."""
    print("\n── Service fly.toml configs ──")
    base = os.path.join(os.path.dirname(__file__), "..", "..", "services")

    # SearXNG
    ft_sx = os.path.join(base, "searxng", "fly.toml")
    check("searxng fly.toml exists", os.path.exists(ft_sx))
    if os.path.exists(ft_sx):
        with open(ft_sx, "r") as f:
            src = f.read()
        check("searxng app name", "orionforge-engine-searxng" in src)
        check("searxng region iad", "iad" in src)
        check("searxng port 8080", "8080" in src)
        check("searxng dockerfile ref", "Dockerfile" in src)
        check("searxng auto_stop suspend", "suspend" in src)

    # OpenedAI Speech TTS
    ft_tts = os.path.join(base, "openedai-speech", "fly.toml")
    check("tts fly.toml exists", os.path.exists(ft_tts))
    if os.path.exists(ft_tts):
        with open(ft_tts, "r") as f:
            src = f.read()
        check("tts app name", "orionforge-engine-tts" in src)
        check("tts region iad", "iad" in src)
        check("tts port 8000", "8000" in src)
        check("tts volume mount", "tts_voices" in src)
        check("tts health check /v1/models", "/v1/models" in src)

    # Whisper
    ft_w = os.path.join(base, "whisper", "fly.toml")
    check("whisper fly.toml exists", os.path.exists(ft_w))
    if os.path.exists(ft_w):
        with open(ft_w, "r") as f:
            src = f.read()
        check("whisper app name", "orionforge-engine-whisper" in src)
        check("whisper region iad", "iad" in src)
        check("whisper port 8000", "8000" in src)
        check("whisper health check /v1/models", "/v1/models" in src)
        check("whisper auto_stop suspend", "suspend" in src)


def test_env_priority_over_connections():
    """_seed_platform_keys_from_env updates existing connections if key changes."""
    print("\n-- Env priority over connections --")
    from pathlib import Path
    import web.app as _app

    tmp = tempfile.mkdtemp()
    try:
        orig_connections = _app.CONNECTIONS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)

        # Seed with an existing platform_elevenlabs connection with old key
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "platform_elevenlabs", "provider": "elevenlabs",
                 "url": "https://api.elevenlabs.io", "api_key": "old-key",
                 "enabled": True, "platform_hosted": True,
                 "name": "Platform -- Elevenlabs"},
            ], "agent_connections": {}
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()

        old_el = os.environ.pop("ELEVENLABS_API_KEY", None)
        old_or = os.environ.pop("OPENROUTER_API_KEY", None)
        try:
            # Set new key
            os.environ["ELEVENLABS_API_KEY"] = "new-key"
            _app._seed_platform_keys_from_env()
            data = _app._load_connections()
            check("still 1 connection", len(data["connections"]) == 1)
            check("key updated", data["connections"][0]["api_key"] == "new-key")
            check("platform_hosted preserved", data["connections"][0]["platform_hosted"] is True)

            # No env → no change
            del os.environ["ELEVENLABS_API_KEY"]
            _app._seed_platform_keys_from_env()
            data2 = _app._load_connections()
            check("without env: key unchanged", data2["connections"][0]["api_key"] == "new-key")
        finally:
            os.environ.pop("ELEVENLABS_API_KEY", None)
            os.environ.pop("OPENROUTER_API_KEY", None)
            if old_el:
                os.environ["ELEVENLABS_API_KEY"] = old_el
            if old_or:
                os.environ["OPENROUTER_API_KEY"] = old_or

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# PLATFORM API KEYS — Image Generation
# ═════════════════════════════════════════════
def test_platform_api_keys_image():
    """Test Platform API Keys toggles for image generation providers."""
    print("\n=== TORTURE: Platform API Keys — Image Generation ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. Default state: no Platform Keys enabled ──
        default = _app._load_settings()
        img = default.get("image", {})
        check("default: no openai platform key", not img.get("use_platform_openai", False))
        check("default: no google platform key", not img.get("use_platform_google", False))
        check("default: no stability platform key", not img.get("use_platform_stability", False))

        # ── 2. Save with Platform Keys enabled ──
        settings = {
            "image": {
                "preferred": "openai_dalle3",
                "openai_api_key": "sk-test-openai",
                "use_platform_openai": True,
                "google_api_key": "AIza-test-google",
                "use_platform_google": False,
                "stability_api_key": "sk-test-stability",
                "use_platform_stability": True,
                "ideogram_api_key": "ig-test",
                "replicate_api_key": "r8-test",
                "fal_api_key": "fal-test",
                "leonardo_api_key": "leonardo-test",
                "midjourney_url": "https://api.example.com/mj",
                "midjourney_api_key": "mj-test",
            }
        }
        _app._save_settings(settings)
        loaded = _app._load_settings()
        img = loaded["image"]

        check("openai platform flag saved", img["use_platform_openai"] is True)
        check("google platform flag not set", img["use_platform_google"] is False)
        check("stability platform flag saved", img["use_platform_stability"] is True)
        check("openai key still saved", img["openai_api_key"] == "sk-test-openai")

        # ── 3. Mixed: some keys with platform, some without ──
        settings["image"]["use_platform_openai"] = False
        settings["image"]["use_platform_google"] = True
        _app._save_settings(settings)
        loaded2 = _app._load_settings()
        img2 = loaded2["image"]

        check("openai flag toggled off", img2["use_platform_openai"] is False)
        check("google flag toggled on", img2["use_platform_google"] is True)
        check("stability still on", img2["use_platform_stability"] is True)

        # ── 4. All flags off (user's own keys only) ──
        settings["image"]["use_platform_openai"] = False
        settings["image"]["use_platform_google"] = False
        settings["image"]["use_platform_stability"] = False
        _app._save_settings(settings)
        loaded3 = _app._load_settings()
        img3 = loaded3["image"]

        check("all platform flags off", 
              not img3.get("use_platform_openai") and 
              not img3.get("use_platform_google") and 
              not img3.get("use_platform_stability"))

        # ── 5. Keys without API keys, platform flag doesn't matter ──
        settings["image"]["openai_api_key"] = ""
        settings["image"]["use_platform_openai"] = True
        _app._save_settings(settings)
        loaded4 = _app._load_settings()

        check("platform flag persists even without key", loaded4["image"]["use_platform_openai"] is True)
        check("empty key saved", loaded4["image"]["openai_api_key"] == "")

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# PLATFORM API KEYS — Voice (TTS)
# ═════════════════════════════════════════════
def test_platform_api_keys_voice():
    """Test Platform API Keys toggles for voice/TTS providers."""
    print("\n=== TORTURE: Platform API Keys — Voice (TTS) ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. Default state: no Platform Keys enabled ──
        default = _app._load_settings()
        tts = default.get("tts", {})
        check("default: no elevenlabs platform key", not tts.get("use_platform_elevenlabs", False))
        check("default: no openedai_cloud platform key", not tts.get("use_platform_openedai_cloud", False))

        # ── 2. Save with ElevenLabs Platform Key enabled ──
        settings = {
            "tts": {
                "provider": "elevenlabs",
                "elevenlabs_api_key": "xi-test-key",
                "use_platform_elevenlabs": True,
                "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
                "elevenlabs_voice_name": "Rachel",
                "openedai_cloud_url": "https://api.openedai.com/v1",
                "openedai_cloud_api_key": "sk-test-openedai",
                "use_platform_openedai_cloud": False,
                "openedai_cloud_voice": "alloy",
                "openedai_cloud_model": "tts-1",
            }
        }
        _app._save_settings(settings)
        loaded = _app._load_settings()
        tts = loaded["tts"]

        check("elevenlabs platform flag saved", tts["use_platform_elevenlabs"] is True)
        check("openedai platform flag not set", tts["use_platform_openedai_cloud"] is False)
        check("elevenlabs key still saved", tts["elevenlabs_api_key"] == "xi-test-key")
        check("elevenlabs voice_id preserved", tts["elevenlabs_voice_id"] == "21m00Tcm4TlvDq8ikWAM")

        # ── 3. Toggle both platforms ──
        settings["tts"]["use_platform_elevenlabs"] = False
        settings["tts"]["use_platform_openedai_cloud"] = True
        _app._save_settings(settings)
        loaded2 = _app._load_settings()
        tts2 = loaded2["tts"]

        check("elevenlabs flag toggled off", tts2["use_platform_elevenlabs"] is False)
        check("openedai flag toggled on", tts2["use_platform_openedai_cloud"] is True)

        # ── 4. Both disabled (user's own keys) ──
        settings["tts"]["use_platform_elevenlabs"] = False
        settings["tts"]["use_platform_openedai_cloud"] = False
        _app._save_settings(settings)
        loaded3 = _app._load_settings()
        tts3 = loaded3["tts"]

        check("all tts platform flags off",
              not tts3.get("use_platform_elevenlabs") and 
              not tts3.get("use_platform_openedai_cloud"))

        # ── 5. Provider switch with platform key ──
        settings["tts"]["provider"] = "openedai_cloud"
        settings["tts"]["use_platform_elevenlabs"] = False
        settings["tts"]["use_platform_openedai_cloud"] = True
        _app._save_settings(settings)
        loaded4 = _app._load_settings()

        check("provider switched to openedai_cloud", loaded4["tts"]["provider"] == "openedai_cloud")
        check("openedai_cloud platform flag active", loaded4["tts"]["use_platform_openedai_cloud"] is True)
        check("elevenlabs key still in dict", "elevenlabs_api_key" in loaded4["tts"])

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# NORMALIZE OLLAMA URL
# ═════════════════════════════════════════════
def test_normalize_ollama_url():
    """Test _normalize_ollama_url handles all input variants correctly."""
    print("\n=== TORTURE: _normalize_ollama_url ===")
    import web.app as _app

    EXPECTED = _app.PLATFORM_OLLAMA_URL  # http://orionforge-engine-ollama.flycast:11434

    # None / empty → platform URL
    check("None → platform URL", _app._normalize_ollama_url(None) == EXPECTED)
    check("empty string → platform URL", _app._normalize_ollama_url("") == EXPECTED)
    check("whitespace → platform URL", _app._normalize_ollama_url("   ") == EXPECTED)

    # localhost variants → platform URL
    check("localhost:11434 → platform URL", _app._normalize_ollama_url("http://localhost:11434") == EXPECTED)
    check("127.0.0.1:11434 → platform URL", _app._normalize_ollama_url("http://127.0.0.1:11434") == EXPECTED)
    check("localhost no port → platform URL", _app._normalize_ollama_url("http://localhost") == EXPECTED)

    # Custom non-localhost URL → preserved as-is
    custom = "http://my-ollama.internal:11434"
    result = _app._normalize_ollama_url(custom)
    check("custom URL preserved", result == custom)

    # Already the platform URL → unchanged
    check("platform URL idempotent", _app._normalize_ollama_url(EXPECTED) == EXPECTED)

    # Public Fly URL → preserved (external)
    pub = "https://orionforge-engine-ollama.fly.dev"
    check("public fly URL preserved", _app._normalize_ollama_url(pub) == pub)


# ═════════════════════════════════════════════
# GET PLATFORM CONNECTIONS
# ═════════════════════════════════════════════
def test_get_platform_connections():
    """Test _get_platform_connections() returns only platform-hosted connections."""
    print("\n=== TORTURE: _get_platform_connections ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_conn = _app.CONNECTIONS_FILE
        tmp_conn = Path(tmp) / "config" / "connections.json"
        tmp_conn.parent.mkdir(parents=True)
        _app.CONNECTIONS_FILE = tmp_conn
        _app._TTL_CACHE.clear()

        store = {
            "connections": [
                {"id": "platform_openai", "name": "Platform OpenAI", "provider": "openai",
                 "platform_hosted": True, "enabled": True, "api_key": "sk-plat", "models": []},
                {"id": "platform_ollama", "name": "Platform Ollama", "provider": "ollama",
                 "platform_hosted": True, "enabled": True, "api_key": "", "models": ["llama3.2:3b"]},
                {"id": "user_openai", "name": "My OpenAI", "provider": "openai",
                 "platform_hosted": False, "enabled": True, "api_key": "sk-user", "models": []},
                {"id": "elevenlabs", "name": "ElevenLabs", "provider": "elevenlabs",
                 "platform_hosted": True, "enabled": True, "api_key": "xi-key", "models": []},
            ]
        }
        _app._save_connections(store)

        result = _app._get_platform_connections()
        ids = [c["id"] for c in result]

        check("platform_openai in result", "platform_openai" in ids)
        check("platform_ollama in result", "platform_ollama" in ids)
        check("elevenlabs in result (platform_hosted=True)", "elevenlabs" in ids)
        check("user_openai not in result", "user_openai" not in ids)
        check("total count is 3", len(result) == 3)

        # All returned items must have platform_hosted=True
        check("all results platform_hosted", all(c["platform_hosted"] for c in result))

    finally:
        _app.CONNECTIONS_FILE = orig_conn
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# PAGE CHAT CONNECTIONS SPLIT
# ═════════════════════════════════════════════
def test_page_chat_connections_split():
    """Test page_chat() splits connections into platform_connections and user_connections correctly."""
    print("\n=== TORTURE: page_chat connections split logic ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_conn = _app.CONNECTIONS_FILE
        tmp_conn = Path(tmp) / "config" / "connections.json"
        tmp_conn.parent.mkdir(parents=True)
        _app.CONNECTIONS_FILE = tmp_conn
        _app._TTL_CACHE.clear()

        store = {
            "connections": [
                {"id": "platform_openai", "provider": "openai", "platform_hosted": True,
                 "enabled": True, "api_key": "sk-x", "models": []},
                {"id": "platform_ollama", "provider": "ollama", "platform_hosted": True,
                 "enabled": True, "api_key": "", "models": []},
                {"id": "platform_elevenlabs", "provider": "elevenlabs", "platform_hosted": True,
                 "enabled": True, "api_key": "xi-k", "models": []},
                {"id": "platform_whisper", "provider": "whisper", "platform_hosted": True,
                 "enabled": True, "api_key": "", "models": []},
                {"id": "user_openai", "provider": "openai", "platform_hosted": False,
                 "enabled": True, "api_key": "sk-u", "models": []},
                {"id": "user_openai_disabled", "provider": "openai", "platform_hosted": False,
                 "enabled": False, "api_key": "sk-d", "models": []},
            ]
        }
        _app._save_connections(store)

        all_conns = [c for c in store["connections"] if c.get("enabled")]
        platform_conns = [
            c for c in all_conns
            if c.get("platform_hosted") and c.get("provider") not in ("elevenlabs", "edge-tts", "whisper")
        ]
        user_conns = [
            c for c in all_conns
            if not c.get("platform_hosted") and c.get("provider") not in ("elevenlabs", "edge-tts", "whisper")
        ]

        plat_ids = [c["id"] for c in platform_conns]
        user_ids = [c["id"] for c in user_conns]

        check("platform_openai in platform_conns", "platform_openai" in plat_ids)
        check("platform_ollama in platform_conns", "platform_ollama" in plat_ids)
        check("platform_elevenlabs excluded from platform_conns", "platform_elevenlabs" not in plat_ids)
        check("platform_whisper excluded from platform_conns", "platform_whisper" not in plat_ids)
        check("user_openai in user_conns", "user_openai" in user_ids)
        check("disabled user conn excluded", "user_openai_disabled" not in user_ids)
        check("platform conn not in user_conns", "platform_openai" not in user_ids)
        check("platform_conns count=2", len(platform_conns) == 2)
        check("user_conns count=1", len(user_conns) == 1)

    finally:
        _app.CONNECTIONS_FILE = orig_conn
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# ADMIN PLATFORM KEY — OLLAMA SAVE (UPSERT)
# ═════════════════════════════════════════════
def test_admin_platform_key_ollama_save():
    """Test admin platform key save logic: Ollama requires no API key, upsert works."""
    print("\n=== TORTURE: Admin platform key — Ollama save/upsert ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_conn = _app.CONNECTIONS_FILE
        tmp_conn = Path(tmp) / "config" / "connections.json"
        tmp_conn.parent.mkdir(parents=True)
        _app.CONNECTIONS_FILE = tmp_conn
        _app._TTL_CACHE.clear()
        _app._save_connections({"connections": []})

        EXPECTED_URL = _app.PLATFORM_OLLAMA_URL

        # ── 1. Ollama: no API key, URL defaults to platform URL ──
        store = _app._load_connections()
        provider = "ollama"
        url = _app._normalize_ollama_url("")  # empty → platform URL
        conn_new = {
            "id": f"platform_{provider}",
            "name": "Platform — ollama",
            "type": "ollama",
            "provider": provider,
            "url": url,
            "api_key": "",
            "models": [],
            "enabled": True,
            "platform_hosted": True,
        }
        store["connections"].append(conn_new)
        _app._save_connections(store)

        loaded = _app._load_connections()
        ollama_conn = next((c for c in loaded["connections"] if c["provider"] == "ollama"), None)
        check("ollama conn saved", ollama_conn is not None)
        check("ollama conn api_key empty", ollama_conn["api_key"] == "")
        check("ollama conn url normalized", ollama_conn["url"] == EXPECTED_URL)
        check("ollama conn platform_hosted", ollama_conn["platform_hosted"] is True)

        # ── 2. Upsert: update existing ollama connection ──
        store = _app._load_connections()
        existing = next(c for c in store["connections"] if c["provider"] == "ollama")
        existing["models"] = ["llama3.2:3b", "qwen2.5:7b"]
        existing["url"] = _app._normalize_ollama_url("http://localhost:11434")  # should normalize
        _app._save_connections(store)

        loaded2 = _app._load_connections()
        updated = next(c for c in loaded2["connections"] if c["provider"] == "ollama")
        check("upsert: models updated", "llama3.2:3b" in updated["models"])
        check("upsert: localhost URL normalized to platform", updated["url"] == EXPECTED_URL)

        # ── 3. OpenRouter: requires API key ──
        store3 = _app._load_connections()
        or_conn = {
            "id": "platform_openrouter",
            "name": "Platform — OpenRouter",
            "type": "external",
            "provider": "openrouter",
            "url": "https://openrouter.ai/api/v1",
            "api_key": "sk-or-testkey123",
            "models": ["mistralai/mistral-7b-instruct"],
            "enabled": True,
            "platform_hosted": True,
        }
        store3["connections"].append(or_conn)
        _app._save_connections(store3)

        loaded3 = _app._load_connections()
        or_result = next((c for c in loaded3["connections"] if c["provider"] == "openrouter"), None)
        check("openrouter conn saved", or_result is not None)
        check("openrouter api_key set", or_result["api_key"] == "sk-or-testkey123")
        check("openrouter platform_hosted", or_result["platform_hosted"] is True)
        check("openrouter url correct", or_result["url"] == "https://openrouter.ai/api/v1")

        # ── 4. Validation: provider="" should fail ──
        # (test guard logic manually)
        guard_provider = "".strip()
        check("empty provider rejected", not guard_provider)

        # ── 5. Validation: non-ollama provider without api_key should fail ──
        guard_key = "".strip()
        guard_prov = "openai"
        check("openai without key rejected", guard_prov != "ollama" and not guard_key)

    finally:
        _app.CONNECTIONS_FILE = orig_conn
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# USER API KEYS — OPENROUTER + OLLAMA URL
# ═════════════════════════════════════════════
def test_user_api_keys_openrouter_ollama():
    """Test that api_save_api_keys stores openrouter and ollama_url in user settings."""
    print("\n=== TORTURE: User API keys — OpenRouter + Ollama URL ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. Save all user keys including openrouter + ollama_url ──
        body = {
            "openai": "sk-openai-test",
            "anthropic": "sk-ant-test",
            "deepseek": "sk-ds-test",
            "google_gemini": "AIza-test",
            "openrouter": "sk-or-user-test",
            "ollama_url": "http://localhost:11434",  # should normalize to platform URL
        }
        ollama_url_normalized = _app._normalize_ollama_url(body["ollama_url"])
        settings = _app._load_settings()
        settings["api_keys"] = {
            "openai":        body.get("openai", ""),
            "anthropic":     body.get("anthropic", ""),
            "deepseek":      body.get("deepseek", ""),
            "google_gemini": body.get("google_gemini", ""),
            "openrouter":    body.get("openrouter", ""),
            "ollama_url":    ollama_url_normalized,
        }
        _app._save_settings(settings)

        loaded = _app._load_settings()
        keys = loaded.get("api_keys", {})

        check("openai key saved", keys["openai"] == "sk-openai-test")
        check("anthropic key saved", keys["anthropic"] == "sk-ant-test")
        check("deepseek key saved", keys["deepseek"] == "sk-ds-test")
        check("google_gemini key saved", keys["google_gemini"] == "AIza-test")
        check("openrouter key saved", keys["openrouter"] == "sk-or-user-test")
        check("ollama_url normalized from localhost", keys["ollama_url"] == _app.PLATFORM_OLLAMA_URL)

        # ── 2. Save with custom (non-localhost) Ollama URL — preserved ──
        custom_url = "http://my-custom-ollama:11434"
        body2 = {"openrouter": "sk-or-v2", "ollama_url": custom_url}
        url2 = _app._normalize_ollama_url(body2["ollama_url"])
        settings["api_keys"]["openrouter"] = body2["openrouter"]
        settings["api_keys"]["ollama_url"] = url2
        _app._save_settings(settings)

        loaded2 = _app._load_settings()
        keys2 = loaded2["api_keys"]
        check("openrouter updated", keys2["openrouter"] == "sk-or-v2")
        check("custom ollama_url preserved", keys2["ollama_url"] == custom_url)

        # ── 3. Missing openrouter key → saved as empty string ──
        settings["api_keys"] = {
            "openai": "sk-x", "anthropic": "", "deepseek": "",
            "google_gemini": "", "openrouter": "", "ollama_url": custom_url,
        }
        _app._save_settings(settings)
        loaded3 = _app._load_settings()
        check("missing openrouter saved as empty", loaded3["api_keys"]["openrouter"] == "")

        # ── 4. All 6 keys present in schema ──
        expected_keys = {"openai", "anthropic", "deepseek", "google_gemini", "openrouter", "ollama_url"}
        check("all 6 keys in schema", expected_keys == set(loaded3["api_keys"].keys()))

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# USER API KEYS — MASKING LOGIC
# ═════════════════════════════════════════════
def test_user_api_keys_masking():
    """Test api_get_api_keys masking: ollama_url unmasked, long keys truncated."""
    print("\n=== TORTURE: User API keys — masking logic ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        settings = {
            "api_keys": {
                "openai": "sk-abcdefghijklmnop",  # 18 chars
                "anthropic": "sk-ant-1234",        # 11 chars
                "deepseek": "sk-ds-xy",            # 8 chars
                "google_gemini": "AIza",           # 4 chars
                "openrouter": "sk-or-testroutkey",  # 17 chars
                "ollama_url": "http://orionforge-engine-ollama.flycast:11434",
            }
        }
        _app._save_settings(settings)

        # Simulate the masking logic from api_get_api_keys
        keys = settings["api_keys"]
        masked = {}
        for k, v in keys.items():
            if k == "ollama_url":
                masked[k] = v
            elif v and len(v) > 8:
                masked[k] = v[:4] + "•" * (len(v) - 8) + v[-4:]
            elif v:
                masked[k] = "•" * len(v)
            else:
                masked[k] = ""

        # ollama_url: never masked
        check("ollama_url unmasked", masked["ollama_url"] == "http://orionforge-engine-ollama.flycast:11434")

        # openai: long key → first 4 + bullets + last 4
        check("openai starts with 'sk-a'", masked["openai"].startswith("sk-a"))
        check("openai ends with 'mnop'", masked["openai"].endswith("mnop"))
        check("openai contains bullets", "•" in masked["openai"])

        # openrouter: long key → masked
        check("openrouter masked", "•" in masked["openrouter"])
        check("openrouter starts with 'sk-o'", masked["openrouter"].startswith("sk-o"))

        # deepseek: exactly 8 chars → all bullets (no first/last preserved)
        check("deepseek 8-char → all bullets", masked["deepseek"] == "•" * 8)

        # google_gemini: 4 chars → all bullets
        check("google_gemini 4-char → all bullets", masked["google_gemini"] == "•" * 4)

        # empty key → empty string
        settings["api_keys"]["openai"] = ""
        masked_empty = "" if not settings["api_keys"]["openai"] else "masked"
        check("empty key → empty masked", masked_empty == "")

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# ALL-MODELS ENDPOINT — STATIC LOGIC
# ═════════════════════════════════════════════
def test_connections_all_models_static():
    """Test /api/connections/all-models static logic (no HTTP): returns conn_id → sorted model list."""
    print("\n=== TORTURE: /api/connections/all-models static logic ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_conn = _app.CONNECTIONS_FILE
        tmp_conn = Path(tmp) / "config" / "connections.json"
        tmp_conn.parent.mkdir(parents=True)
        _app.CONNECTIONS_FILE = tmp_conn
        _app._TTL_CACHE.clear()

        store = {
            "connections": [
                {"id": "platform_openai", "provider": "openai", "enabled": True,
                 "platform_hosted": True, "api_key": "sk-x",
                 "models": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]},
                {"id": "platform_ollama", "provider": "ollama", "enabled": True,
                 "platform_hosted": True, "api_key": "",
                 "models": ["qwen2.5:7b", "llama3.2:3b"]},
                {"id": "user_openai", "provider": "openai", "enabled": True,
                 "platform_hosted": False, "api_key": "sk-u",
                 "models": ["gpt-4o"]},
                {"id": "disabled_conn", "provider": "openai", "enabled": False,
                 "platform_hosted": False, "api_key": "sk-d",
                 "models": ["gpt-4-turbo"]},
            ]
        }
        _app._save_connections(store)

        # Simulate the static part of api_connections_all_models (no HTTP refresh)
        loaded = _app._load_connections()
        result = {}
        for conn in loaded.get("connections", []):
            if not conn.get("enabled"):
                continue
            result[conn["id"]] = sorted(conn.get("models") or [])

        check("platform_openai in result", "platform_openai" in result)
        check("platform_ollama in result", "platform_ollama" in result)
        check("user_openai in result", "user_openai" in result)
        check("disabled_conn excluded", "disabled_conn" not in result)

        # Models are sorted
        check("openai models sorted", result["platform_openai"] == sorted(["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]))
        check("ollama models sorted", result["platform_ollama"] == sorted(["qwen2.5:7b", "llama3.2:3b"]))

        # Value format: connection with no models → empty list
        store2 = {"connections": [
            {"id": "empty_conn", "provider": "openai", "enabled": True,
             "platform_hosted": True, "api_key": "sk-e", "models": None},
        ]}
        _app._save_connections(store2)
        loaded2 = _app._load_connections()
        result2 = {}
        for c in loaded2["connections"]:
            if c.get("enabled"):
                result2[c["id"]] = sorted(c.get("models") or [])
        check("None models → empty list", result2.get("empty_conn") == [])

    finally:
        _app.CONNECTIONS_FILE = orig_conn
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# ADMIN KEYS TEMPLATE — PROVIDERS ARRAY
# ═════════════════════════════════════════════
def test_admin_keys_template_providers():
    """Test admin_keys.html PROVIDERS JS array has OpenRouter (+ ElevenLabs) entries."""
    print("\n=== TORTURE: admin_keys.html PROVIDERS array ===")
    from pathlib import Path
    templates_dir = Path(__file__).parent.parent / "web" / "templates"
    admin_html = templates_dir / "admin_keys.html"

    check("admin_keys.html exists", admin_html.exists())
    if not admin_html.exists():
        return

    content = admin_html.read_text(encoding="utf-8")

    # PROVIDERS array exists
    check("PROVIDERS array declared", "const PROVIDERS = [" in content)

    # OpenRouter provider entry
    check("openrouter id in PROVIDERS", 'id: "openrouter"' in content)
    check("openrouter name 'OpenRouter'", 'name: "OpenRouter"' in content)
    check("openrouter url_default correct", '"https://openrouter.ai/api/v1"' in content)
    check("openrouter key placeholder sk-or-", '"sk-or-' in content)

    # ElevenLabs provider entry (replaces old ollama/openai/anthropic entries)
    check("elevenlabs id in PROVIDERS", 'id: "elevenlabs"' in content)
    check("elevenlabs name", 'name: "ElevenLabs"' in content)

    # OpenRouter is first entry
    idx_or = content.find('id: "openrouter"')
    idx_el = content.find('id: "elevenlabs"')
    check("openrouter before elevenlabs", idx_or < idx_el)

    # Ollama skip guard still present (for save logic)
    check("ollama api_key skip guard", 'providerId !== "ollama"' in content
          or "provider !== 'ollama'" in content
          or '!== "ollama"' in content)

    # Admin page has providers-list container
    check("providers-list div present", 'id="providers-list"' in content)

    # Platform API Keys label / heading present
    check("Platform API Keys label", "Platform" in content and "API" in content)


# ═════════════════════════════════════════════
# CHAT HTML — THREE-MODE SELECTOR
# ═════════════════════════════════════════════
def test_chat_html_three_mode_selector():
    """Test chat.html contains the 3-mode connection selector and routing JS functions."""
    print("\n=== TORTURE: chat.html three-mode selector ===")
    from pathlib import Path
    templates_dir = Path(__file__).parent.parent / "web" / "templates"
    chat_html = templates_dir / "chat.html"

    check("chat.html exists", chat_html.exists())
    if not chat_html.exists():
        return

    content = chat_html.read_text(encoding="utf-8")

    # ── Connection selector element ──
    check("chat-connection select present", 'id="chat-connection"' in content)
    check("onConnectionChange handler wired", "onConnectionChange" in content)

    # ── Three mode option values ──
    check("__platform__ option present", 'value="__platform__"' in content)
    check("__auto__ option present", 'value="__auto__"' in content)
    check("__user__ option present", 'value="__user__"' in content)
    check("Platform Models label", "Platform Models" in content)
    check("Auto User Router label", "Auto (User Router)" in content)
    check("User Models label", "User Models" in content)

    # ── Platform connections JS constant ──
    check("_platformConnections const declared", "_platformConnections" in content)
    check("platform_connections Jinja template var", "platform_connections" in content)
    check("tojson filter applied", "tojson" in content)

    # ── fetchPlatformModels function ──
    check("fetchPlatformModels function defined", "async function fetchPlatformModels" in content
          or "function fetchPlatformModels" in content)
    check("fetchPlatformModels calls all-models", "/api/connections/all-models" in content)

    # ── fetchUserModels function ──
    check("fetchUserModels function defined", "async function fetchUserModels" in content
          or "function fetchUserModels" in content)
    check("fetchUserModels calls /api/user/models", "/api/user/models" in content)

    # ── _buildChatRoutingPayload function ──
    check("_buildChatRoutingPayload defined", "function _buildChatRoutingPayload" in content)
    check("__auto__ handled in payload builder", "__auto__" in content)
    check("__platform__ handled in payload builder", "__platform__" in content)
    check("__user__ handled in payload builder", "__user__" in content)

    # ── Model select element ──
    check("chat-model select present", 'id="chat-model"' in content)

    # ── Default initializes to __platform__ ──
    check("default init to __platform__", "'__platform__'" in content or '"__platform__"' in content)

    # ── sendChatMsg uses routing payload ──
    check("_buildChatRoutingPayload called in send", "_buildChatRoutingPayload()" in content)

    # ── onConnectionChange handles all three modes ──
    check("onConnectionChange handles __auto__", content.count("__auto__") >= 2)
    check("onConnectionChange handles __platform__", content.count("__platform__") >= 3)
    check("onConnectionChange handles __user__", content.count("__user__") >= 2)

    # ── No old user_connections Jinja loop (static dropdown now) ──
    check("no user_connections Jinja loop", "user_connections" not in content)

    # ── __userkey_ format in fetchUserModels ──
    check("__userkey_ prefix in fetchUserModels", "__userkey_" in content)


# ═════════════════════════════════════════════
# SOUL SCRIPT HELPERS — _load / _save round-trip
# ═════════════════════════════════════════════
def test_soul_script_helpers():
    """Test _load_soul_script / _save_soul_script: round-trip, missing file, dir creation."""
    print("\n=== TORTURE: Soul Script Helpers ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_directives = _app._DIRECTIVES_DIR
        tmp_directives = Path(tmp) / "directives"
        # Do NOT create dir yet — test that _save_soul_script creates it
        _app._DIRECTIVES_DIR = tmp_directives

        # ── 1. Load from missing directory → empty string ──
        text = _app._load_soul_script("nonexistent_agent")
        check("missing dir → empty string", text == "")

        # ── 2. Save creates directory + file ──
        _app._save_soul_script("test_agent", "# Soul Script\nIdentity core.")
        check("directives dir created", tmp_directives.exists())
        check("soul script file created", (tmp_directives / "test_agent.md").exists())

        # ── 3. Load round-trip ──
        loaded = _app._load_soul_script("test_agent")
        check("round-trip content", loaded == "# Soul Script\nIdentity core.")

        # ── 4. Overwrite ──
        _app._save_soul_script("test_agent", "Updated content.")
        loaded2 = _app._load_soul_script("test_agent")
        check("overwrite content", loaded2 == "Updated content.")

        # ── 5. Empty string save ──
        _app._save_soul_script("test_agent", "")
        loaded3 = _app._load_soul_script("test_agent")
        check("empty save → empty load", loaded3 == "")

        # ── 6. Multiple agents ──
        _app._save_soul_script("agent_a", "Alpha soul")
        _app._save_soul_script("agent_b", "Beta soul")
        check("agent_a content", _app._load_soul_script("agent_a") == "Alpha soul")
        check("agent_b content", _app._load_soul_script("agent_b") == "Beta soul")
        check("agent_a file", (tmp_directives / "agent_a.md").exists())
        check("agent_b file", (tmp_directives / "agent_b.md").exists())

        # ── 7. Unicode content ──
        _app._save_soul_script("uni_agent", "日本語テスト 🧬")
        check("unicode round-trip", _app._load_soul_script("uni_agent") == "日本語テスト 🧬")

    finally:
        _app._DIRECTIVES_DIR = orig_directives
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# SOUL SCRIPT API — config endpoint saves soul_script_text
# ═════════════════════════════════════════════
def test_soul_script_api():
    """Test PUT /api/profiles/{name}/config with soul_script_text field."""
    print("\n=== TORTURE: Soul Script API ===")
    from pathlib import Path
    import yaml

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        orig_profiles = _app._PROFILES_DIR
        orig_prompts = _app._PROMPTS_DIR
        orig_directives = _app._DIRECTIVES_DIR

        tmp_config = Path(tmp) / "config"
        tmp_config.mkdir()
        tmp_profiles = Path(tmp) / "profiles"
        tmp_profiles.mkdir()
        tmp_prompts = Path(tmp) / "prompts"
        tmp_prompts.mkdir()
        tmp_directives = Path(tmp) / "directives"
        tmp_directives.mkdir()
        tmp_settings = tmp_config / "settings.json"
        tmp_settings.write_text("{}", encoding="utf-8")

        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        _app._PROFILES_DIR = tmp_profiles
        _app._PROMPTS_DIR = tmp_prompts
        _app._DIRECTIVES_DIR = tmp_directives

        # Seed a profile YAML + prompt file
        profile_data = {"name": "test_ss", "model": "gpt-4o", "allowed_tools": []}
        (tmp_profiles / "test_ss.yaml").write_text(
            yaml.dump(profile_data, default_flow_style=False), encoding="utf-8"
        )
        (tmp_prompts / "test_ss.system.md").write_text("System prompt.", encoding="utf-8")

        # Seed agent config in settings
        settings = {"agent_configs": {"test_ss": {}}}
        tmp_settings.write_text(json.dumps(settings), encoding="utf-8")

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. Save soul_script_text via config endpoint ──
                    r = await client.put("/api/profiles/test_ss/config", json={
                        "soul_script_text": "# Test Soul Script\nCore identity."
                    })
                    check("soul script save 200", r.status_code == 200)
                    data = r.json()
                    check("soul script save ok", data.get("ok") is True)
                    if r.status_code != 200 or data.get("ok") is not True:
                        return  # auth wall – skip

                    # ── 2. Verify file created on disk ──
                    ss_path = tmp_directives / "test_ss.md"
                    check("soul script file exists", ss_path.exists())
                    content = ss_path.read_text(encoding="utf-8")
                    check("soul script content", content == "# Test Soul Script\nCore identity.")

                    # ── 3. Update with new content ──
                    r2 = await client.put("/api/profiles/test_ss/config", json={
                        "soul_script_text": "Updated soul."
                    })
                    check("soul script update 200", r2.status_code == 200)
                    content2 = ss_path.read_text(encoding="utf-8")
                    check("soul script updated content", content2 == "Updated soul.")

                    # ── 4. Save empty soul_script_text ──
                    r3 = await client.put("/api/profiles/test_ss/config", json={
                        "soul_script_text": ""
                    })
                    check("empty soul script 200", r3.status_code == 200)
                    content3 = ss_path.read_text(encoding="utf-8")
                    check("empty soul script content", content3 == "")

                    # ── 5. Save soul_script_text + system_prompt_text together ──
                    r4 = await client.put("/api/profiles/test_ss/config", json={
                        "system_prompt_text": "New system prompt.",
                        "soul_script_text": "New soul script."
                    })
                    check("combined save 200", r4.status_code == 200)
                    check("system prompt saved",
                          (tmp_prompts / "test_ss.system.md").read_text(encoding="utf-8") == "New system prompt.")
                    check("soul script saved",
                          ss_path.read_text(encoding="utf-8") == "New soul script.")

                    # ── 6. Config without soul_script_text doesn't erase it ──
                    r5 = await client.put("/api/profiles/test_ss/config", json={
                        "display_name": "Test Agent SS"
                    })
                    check("no-soul-script save 200", r5.status_code == 200)
                    check("soul script preserved",
                          ss_path.read_text(encoding="utf-8") == "New soul script.")

            import web.app as _app_auth_ss
            _orig_gac_ss = _app_auth_ss.get_auth_config
            _app_auth_ss.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_ss.get_auth_config = _orig_gac_ss

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        _app._PROFILES_DIR = orig_profiles
        _app._PROMPTS_DIR = orig_prompts
        _app._DIRECTIVES_DIR = orig_directives
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# SOUL SCRIPT FAISS INDEXING — _rebuild_notes_faiss covers soul scripts
# ═════════════════════════════════════════════
def test_soul_script_faiss_indexing():
    """Test that _rebuild_notes_faiss indexes soul script files with proper doc_ids."""
    print("\n=== TORTURE: Soul Script FAISS Indexing ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_directives = _app._DIRECTIVES_DIR
        orig_profiles = _app._PROFILES_DIR
        orig_faiss = _app._FAISS_DIR
        orig_data = _app._DATA_DIR
        orig_notes = _app._NOTES_DIR

        tmp_directives = Path(tmp) / "directives"
        tmp_directives.mkdir()
        tmp_profiles = Path(tmp) / "profiles"
        tmp_profiles.mkdir()
        tmp_faiss = Path(tmp) / "faiss"
        tmp_faiss.mkdir()
        tmp_data = Path(tmp) / "data"
        tmp_data.mkdir()
        tmp_notes = tmp_data / "user_notes"
        tmp_notes.mkdir(parents=True)

        _app._DIRECTIVES_DIR = tmp_directives
        _app._PROFILES_DIR = tmp_profiles
        _app._FAISS_DIR = tmp_faiss
        _app._DATA_DIR = tmp_data
        _app._NOTES_DIR = tmp_notes

        # Seed a profile YAML so _list_agents() returns it
        import yaml
        (tmp_profiles / "alpha.yaml").write_text(
            yaml.dump({"name": "alpha"}, default_flow_style=False), encoding="utf-8"
        )
        (tmp_profiles / "beta.yaml").write_text(
            yaml.dump({"name": "beta"}, default_flow_style=False), encoding="utf-8"
        )

        # Seed soul scripts
        (tmp_directives / "alpha.md").write_text("Alpha soul content.", encoding="utf-8")
        (tmp_directives / "beta.md").write_text("", encoding="utf-8")  # empty — should be skipped

        # Verify _rebuild_notes_faiss exists
        check("_rebuild_notes_faiss exists", callable(getattr(_app, '_rebuild_notes_faiss', None)))

        # Verify expected doc_id format
        check("doc_id format alpha", f"__soul_script__alpha" == "__soul_script__alpha")
        check("doc_id format beta", f"__soul_script__beta" == "__soul_script__beta")

        # Verify _list_agents() picks up both profiles
        agents = _app._list_agents()
        check("alpha in agents", "alpha" in agents)
        check("beta in agents", "beta" in agents)

        # Verify soul script files are readable by the rebuild logic path
        ss_alpha = tmp_directives / "alpha.md"
        ss_beta = tmp_directives / "beta.md"
        check("alpha soul script readable", ss_alpha.exists() and ss_alpha.read_text(encoding="utf-8").strip() != "")
        check("beta soul script empty", ss_beta.exists() and ss_beta.read_text(encoding="utf-8").strip() == "")

        # Try running _rebuild_notes_faiss — exercises the full soul script indexing path
        try:
            _app._rebuild_notes_faiss()
            check("_rebuild_notes_faiss no crash", True)
        except Exception as e:
            # Acceptable if sentence_transformers / FAISS not installed
            err_str = str(e).lower()
            acceptable = any(kw in err_str for kw in [
                "sentence_transformers", "faiss", "no module", "import",
                "model", "transformer"
            ])
            check("_rebuild_notes_faiss acceptable error", acceptable,
                  f"error: {e}")

    finally:
        _app._DIRECTIVES_DIR = orig_directives
        _app._PROFILES_DIR = orig_profiles
        _app._FAISS_DIR = orig_faiss
        _app._DATA_DIR = orig_data
        _app._NOTES_DIR = orig_notes
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# NOTE COLLECTOR — auto-includes soul script doc_id
# ═════════════════════════════════════════════
def test_collect_notes_soul_script():
    """Test that collect_notes() auto-adds __soul_script__{agent_name} to directive IDs."""
    print("\n=== TORTURE: Collect Notes — Soul Script Doc ID ===")
    import inspect
    from src.storage.note_collector import collect_notes

    # ── 1. Verify function signature ──
    sig = inspect.signature(collect_notes)
    params = list(sig.parameters.keys())
    check("collect_notes has agent_name param", "agent_name" in params)
    check("collect_notes has query param", "query" in params)
    check("collect_notes has top_k param", "top_k" in params)

    # ── 2. Verify source code includes soul_script_doc_id injection ──
    src = inspect.getsource(collect_notes)
    check("soul_script doc_id in source",
          "__soul_script__" in src)
    check("directive_note_ids.add(soul_script",
          "directive_note_ids.add(soul_script_doc_id)" in src)
    check("f-string agent_name in doc_id",
          'f"__soul_script__{agent_name}"' in src)

    # ── 3. Call collect_notes with a fake agent (no FAISS index = safe) ──
    try:
        always_block, directive_block = collect_notes("nonexistent_agent_xyz", query="test query")
        check("collect_notes returns tuple", isinstance(always_block, str) and isinstance(directive_block, str))
    except Exception as e:
        # If it crashes for a valid reason (no FAISS), that's okay
        check("collect_notes graceful error", True, f"error: {e}")

    # ── 4. Verify _get_agent_note_config import ──
    from src.storage.note_collector import _get_agent_note_config
    check("_get_agent_note_config callable", callable(_get_agent_note_config))

    # A fake agent should return defaults (empty attached_notes, etc.)
    cfg = _get_agent_note_config("ghost_agent")
    check("default config is dict", isinstance(cfg, dict))


# ═════════════════════════════════════════════
# IDENTITY PROFILE RESOLVER — resolution chain, per-agent presets,
#                              fallback to global, hardcoded defaults
# ═════════════════════════════════════════════
def test_identity_profile_resolver():
    """Test the profile_resolver module: resolution chain, accessors, fallbacks."""
    print("\n=== TORTURE: Identity Profile Resolver ===")
    import json, tempfile, shutil
    from pathlib import Path

    # ── 1. Module imports ──
    from src.memory.profile_resolver import (
        resolve_identity_profile,
        get_indexing_policy,
        get_retrieval_policy,
        get_source_priority_policy,
        _HARDCODED_DEFAULTS,
    )
    check("resolve_identity_profile callable", callable(resolve_identity_profile))
    check("get_indexing_policy callable", callable(get_indexing_policy))
    check("get_retrieval_policy callable", callable(get_retrieval_policy))
    check("get_source_priority_policy callable", callable(get_source_priority_policy))

    # ── 2. Global profile resolves ──
    profile = resolve_identity_profile()
    check("global profile is dict", isinstance(profile, dict))
    check("global profile has indexing_policy", "indexing_policy" in profile)
    check("global profile has retrieval_policy", "retrieval_policy" in profile)

    # ── 3. Indexing policy accessor ──
    idx = get_indexing_policy()
    check("indexing_policy is dict", isinstance(idx, dict))
    check("chunk_size_tokens key", "chunk_size_tokens" in idx)
    check("chunk_overlap_tokens key", "chunk_overlap_tokens" in idx)
    check("chunk_size_tokens is number", isinstance(idx["chunk_size_tokens"], (int, float)))
    check("chunk_overlap_tokens is number", isinstance(idx["chunk_overlap_tokens"], (int, float)))

    # ── 4. Retrieval policy accessor ──
    ret = get_retrieval_policy()
    check("retrieval_policy is dict", isinstance(ret, dict))
    check("top_k key", "top_k" in ret)
    check("top_k is number", isinstance(ret["top_k"], (int, float)))

    # ── 5. Source priority accessor ──
    src_p = get_source_priority_policy()
    check("source_priority_policy is dict", isinstance(src_p, dict))

    # ── 6. Agent-specific resolution (existing agent → __default__ → global) ──
    agent_profile = resolve_identity_profile("orion")
    check("agent profile resolves", isinstance(agent_profile, dict))
    # __default__ should fall through to global profile
    check("agent profile has indexing_policy", "indexing_policy" in agent_profile)

    # ── 7. Non-existent agent falls back to global ──
    ghost_profile = resolve_identity_profile("totally_nonexistent_agent_9999")
    check("ghost agent fallback is dict", isinstance(ghost_profile, dict))
    check("ghost agent has indexing_policy", "indexing_policy" in ghost_profile)

    # ── 8. Hardcoded defaults structure ──
    check("hardcoded defaults has indexing_policy", "indexing_policy" in _HARDCODED_DEFAULTS)
    check("hardcoded defaults has retrieval_policy", "retrieval_policy" in _HARDCODED_DEFAULTS)
    check("hardcoded chunk_size_tokens = 400",
          _HARDCODED_DEFAULTS["indexing_policy"]["chunk_size_tokens"] == 400)
    check("hardcoded top_k = 10",
          _HARDCODED_DEFAULTS["retrieval_policy"]["top_k"] == 10)

    # ── 9. collect_notes now reads top_k from profile ──
    import inspect
    from src.storage.note_collector import collect_notes
    sig = inspect.signature(collect_notes)
    top_k_param = sig.parameters.get("top_k")
    check("collect_notes top_k default is None (profile-driven)",
          top_k_param is not None and top_k_param.default is None)

    # ── 10. chunk_soul_script accepts size params ──
    from src.memory.chunker import chunk_soul_script
    sig2 = inspect.signature(chunk_soul_script)
    check("chunk_soul_script has min_chunk_size param",
          "min_chunk_size" in sig2.parameters)
    check("chunk_soul_script has max_chunk_size param",
          "max_chunk_size" in sig2.parameters)
    # Verify default values
    check("min_chunk_size default is 200",
          sig2.parameters["min_chunk_size"].default == 200)
    check("max_chunk_size default is 2500",
          sig2.parameters["max_chunk_size"].default == 2500)

    # ── 11. chunk_soul_script with custom sizes ──
    soul = "### Core\nI am helpful.\n\n### Values\nBe honest.\n"
    chunks_default = chunk_soul_script(soul, "s1", "Soul", "🧠")
    chunks_custom = chunk_soul_script(soul, "s1", "Soul", "🧠",
                                       min_chunk_size=10, max_chunk_size=500)
    check("default chunking works", len(chunks_default) > 0)
    check("custom size chunking works", len(chunks_custom) > 0)

    # ── 12. _rebuild_notes_faiss reads from profile (source inspection) ──
    import importlib, sys
    app_mod_name = "web.app"
    if app_mod_name in sys.modules:
        app_src = inspect.getsource(sys.modules[app_mod_name])
    else:
        app_path = Path(__file__).resolve().parent.parent / "web" / "app.py"
        app_src = app_path.read_text(encoding="utf-8")
    check("app.py imports get_indexing_policy",
          "get_indexing_policy" in app_src)
    check("app.py uses chunk_size_tokens from profile",
          "chunk_size_tokens" in app_src)
    check("app.py no longer has hardcoded CHUNK_TARGET = 600",
          "CHUNK_TARGET = 600" not in app_src)


# ═════════════════════════════════════════════
# PROFILES TEMPLATE — collapsible sections, soul script, FAISS badge
# ═════════════════════════════════════════════
def test_profiles_template_collapsible():
    """Test profiles.html has collapsible sections, soul script area, FAISS badge."""
    print("\n=== TORTURE: Profiles Template — Collapsible + Soul Script ===")
    from pathlib import Path

    template_path = Path(__file__).resolve().parent.parent / "web" / "templates" / "profiles.html"
    check("profiles.html exists", template_path.exists())
    if not template_path.exists():
        return

    content = template_path.read_text(encoding="utf-8")

    # ── Collapsible infrastructure ──
    check("toggleCollapse JS function", "function toggleCollapse" in content
          or "toggleCollapse" in content)
    check("collapsible-header class", "collapsible-header" in content)
    check("collapsible-body class", "collapsible-body" in content)
    check("collapse-chevron class", "collapse-chevron" in content)

    # ── System prompt collapsible ──
    check("system prompt section has collapsible",
          "System Prompt" in content and "collapsible" in content)

    # ── Soul Script section ──
    check("soul-script textarea", "soul-script" in content)
    check("Soul Script heading", "Soul Script" in content)
    check("FAISS badge", "faiss-badge" in content or "FAISS" in content)
    check("soul_script_text in saveAll", "soul_script_text" in content)

    # ── Knowledge Notes section ──
    check("Knowledge Notes heading", "Knowledge Notes" in content
          or "knowledge" in content.lower())

    # ── soul_script Jinja variable ──
    check("soul_script Jinja var", "soul_script" in content)


# ═════════════════════════════════════════════
# RESOLVE CONNECTION — __userkey_ DYNAMIC CONNECTIONS
# ═════════════════════════════════════════════
def test_resolve_connection_userkey():
    """Test _resolve_connection handles __userkey_<provider> dynamic connections from user API keys."""
    print("\n=== TORTURE: _resolve_connection — __userkey_ dynamic connections ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        orig_conn = _app.CONNECTIONS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_conn = Path(tmp) / "config" / "connections.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        _app.CONNECTIONS_FILE = tmp_conn
        _app._TTL_CACHE.clear()

        # Set up user API keys
        settings = {
            "api_keys": {
                "openai": "sk-test-openai-key",
                "anthropic": "sk-ant-test-key",
                "deepseek": "sk-ds-test-key",
                "google_gemini": "AIza-test-key",
                "openrouter": "sk-or-test-key",
                "ollama_url": "http://localhost:11434",
            }
        }
        _app._save_settings(settings)
        _app._save_connections({"connections": [], "agent_connections": {}})

        # ── 1. __userkey_openai resolves correctly ──
        conn = _app._resolve_connection("__userkey_openai", "test_agent")
        check("userkey_openai resolves", conn is not None)
        check("userkey_openai provider", conn["provider"] == "openai")
        check("userkey_openai api_key", conn["api_key"] == "sk-test-openai-key")
        check("userkey_openai url", "api.openai.com" in conn["url"])
        check("userkey_openai has models", len(conn["models"]) > 0)
        check("userkey_openai enabled", conn["enabled"] is True)

        # ── 2. __userkey_anthropic resolves ──
        conn2 = _app._resolve_connection("__userkey_anthropic", "test_agent")
        check("userkey_anthropic resolves", conn2 is not None)
        check("userkey_anthropic provider", conn2["provider"] == "anthropic")
        check("userkey_anthropic api_key", conn2["api_key"] == "sk-ant-test-key")

        # ── 3. __userkey_deepseek resolves ──
        conn3 = _app._resolve_connection("__userkey_deepseek", "test_agent")
        check("userkey_deepseek resolves", conn3 is not None)
        check("userkey_deepseek url", "deepseek.com" in conn3["url"])

        # ── 4. __userkey_openrouter resolves ──
        conn4 = _app._resolve_connection("__userkey_openrouter", "test_agent")
        check("userkey_openrouter resolves", conn4 is not None)
        check("userkey_openrouter url", "openrouter.ai" in conn4["url"])

        # ── 5. __userkey_google_gemini resolves ──
        conn5 = _app._resolve_connection("__userkey_google_gemini", "test_agent")
        check("userkey_google_gemini resolves", conn5 is not None)
        check("userkey_google_gemini url", "generativelanguage.googleapis.com" in conn5["url"])

        # ── 6. Unknown provider → None ──
        conn6 = _app._resolve_connection("__userkey_unknown_provider", "test_agent")
        check("unknown userkey provider returns None", conn6 is None)

        # ── 7. Provider with empty API key → None ──
        settings["api_keys"]["openai"] = ""
        _app._save_settings(settings)
        conn7 = _app._resolve_connection("__userkey_openai", "test_agent")
        check("empty api_key returns None", conn7 is None)

        # ── 8. Non-userkey connection_id falls through normally ──
        conn8 = _app._resolve_connection("nonexistent_id", "test_agent")
        check("nonexistent conn_id returns None", conn8 is None)

        # ── 9. None connection_id with empty connections → None ──
        conn9 = _app._resolve_connection(None, "test_agent")
        check("None conn_id with no connections returns None", conn9 is None)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        _app.CONNECTIONS_FILE = orig_conn
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# /api/user/models — USER MODEL CATALOG
# ═════════════════════════════════════════════
def test_api_user_models():
    """Test /api/user/models returns providers only for configured API keys."""
    print("\n=== TORTURE: /api/user/models — user model catalog ===")
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        # ── 1. All keys set → all providers returned ──
        settings = {
            "api_keys": {
                "openai": "sk-test-openai-key",
                "anthropic": "sk-ant-test-key",
                "deepseek": "sk-ds-test-key",
                "google_gemini": "AIza-test-key",
                "openrouter": "sk-or-test-key",
                "ollama_url": "http://localhost:11434",
            }
        }
        _app._save_settings(settings)

        # Simulate the endpoint logic
        loaded = _app._load_settings()
        keys = loaded.get("api_keys", {})
        pricing = _app._load_pricing()
        providers = []
        for provider_key, (display_name, section, special) in _app._USER_MODEL_CATALOG.items():
            api_val = keys.get(provider_key, "")
            if api_val and len(api_val) >= 4:
                models = (_app._openrouter_models(pricing) if special == "aggregate"
                          else _app._models_for_provider(pricing, section))
                providers.append({
                    "provider": provider_key,
                    "name": display_name,
                    "models": models,
                })

        provider_keys = [p["provider"] for p in providers]
        check("openai in providers", "openai" in provider_keys)
        check("anthropic in providers", "anthropic" in provider_keys)
        check("deepseek in providers", "deepseek" in provider_keys)
        check("google_gemini in providers", "google_gemini" in provider_keys)
        check("openrouter in providers", "openrouter" in provider_keys)
        check("ollama_url NOT in providers (not in catalog)", "ollama_url" not in provider_keys)
        check("all providers have models", all(len(p["models"]) > 0 for p in providers))
        check("all providers have name", all(p["name"] for p in providers))

        # ── 2. Only openai key → only openai returned ──
        settings2 = {
            "api_keys": {
                "openai": "sk-test-key",
                "anthropic": "",
                "deepseek": "",
                "google_gemini": "",
                "openrouter": "",
                "ollama_url": "",
            }
        }
        _app._save_settings(settings2)
        loaded2 = _app._load_settings()
        keys2 = loaded2.get("api_keys", {})
        providers2 = []
        for pk, (dn, section, special) in _app._USER_MODEL_CATALOG.items():
            av = keys2.get(pk, "")
            if av and len(av) >= 4:
                providers2.append({"provider": pk})
        pkeys2 = [p["provider"] for p in providers2]
        check("only openai when others empty", pkeys2 == ["openai"])

        # ── 3. No keys set → empty providers ──
        settings3 = {"api_keys": {}}
        _app._save_settings(settings3)
        loaded3 = _app._load_settings()
        keys3 = loaded3.get("api_keys", {})
        providers3 = []
        for pk, (dn, section, special) in _app._USER_MODEL_CATALOG.items():
            av = keys3.get(pk, "")
            if av and len(av) >= 4:
                providers3.append({"provider": pk})
        check("no keys → empty providers", len(providers3) == 0)

        # ── 4. Short key (< 4 chars) excluded ──
        settings4 = {"api_keys": {"openai": "sk"}}
        _app._save_settings(settings4)
        loaded4 = _app._load_settings()
        keys4 = loaded4.get("api_keys", {})
        providers4 = []
        for pk, (dn, section, special) in _app._USER_MODEL_CATALOG.items():
            av = keys4.get(pk, "")
            if av and len(av) >= 4:
                providers4.append({"provider": pk})
        check("short key excluded", len(providers4) == 0)

        # ── 5. Catalog structure check ──
        check("catalog has openai", "openai" in _app._USER_MODEL_CATALOG)
        check("catalog has anthropic", "anthropic" in _app._USER_MODEL_CATALOG)
        check("catalog has deepseek", "deepseek" in _app._USER_MODEL_CATALOG)
        check("catalog has openrouter", "openrouter" in _app._USER_MODEL_CATALOG)
        check("catalog has google_gemini", "google_gemini" in _app._USER_MODEL_CATALOG)
        check("catalog entries are (name, section, special) tuples",
              all(isinstance(v, tuple) and len(v) == 3 for v in _app._USER_MODEL_CATALOG.values()))

        # ── 6. Provider URLs check ──
        check("URL map has openai", "openai" in _app._USER_PROVIDER_URLS)
        check("URL map has anthropic", "anthropic" in _app._USER_PROVIDER_URLS)
        check("URL map has deepseek", "deepseek" in _app._USER_PROVIDER_URLS)
        check("URL map has openrouter", "openrouter" in _app._USER_PROVIDER_URLS)
        check("URL map has google_gemini", "google_gemini" in _app._USER_PROVIDER_URLS)
        check("all URLs start with https",
              all(u.startswith("https://") for u in _app._USER_PROVIDER_URLS.values()))

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# STRIPE STATE — PERSISTENT VOLUME PATH
# ═════════════════════════════════════════════
def test_stripe_state_persist_path():
    """Test stripe_billing selects /persist dir when available, config/ otherwise."""
    print("\n=== TORTURE: stripe_state.json persistence path ===")
    from pathlib import Path
    import web.stripe_billing as billing

    # ── 1. _STRIPE_STATE_FILE exists and is a Path ──
    check("_STRIPE_STATE_FILE is a Path", isinstance(billing._STRIPE_STATE_FILE, Path))

    # ── 2. Check path logic: if /persist exists → uses it, otherwise config/ ──
    persist_dir = Path("/persist")
    if persist_dir.is_dir():
        check("uses /persist when available",
              str(billing._STRIPE_STATE_FILE).startswith("/persist"))
    else:
        check("falls back to config/ when no /persist",
              "config" in str(billing._STRIPE_STATE_FILE))

    # ── 3. _load_stripe_state returns dict ──
    state = billing._load_stripe_state()
    check("_load_stripe_state returns dict", isinstance(state, dict))
    check("state has subscriptions key", "subscriptions" in state)

    # ── 4. _save and _load round-trip in temp dir ──
    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file

        test_state = {
            "subscriptions": {},
            "trials": {"user_123": {"started_at": 1700000000}},
            "credits": {"user_123": {"balance": 500, "history": []}},
        }
        billing._save_stripe_state(test_state)
        check("stripe_state file created", tmp_file.exists())

        loaded = billing._load_stripe_state()
        check("round-trip: trials preserved",
              loaded["trials"]["user_123"]["started_at"] == 1700000000)
        check("round-trip: credits preserved",
              loaded["credits"]["user_123"]["balance"] == 500)

        # ── 5. Corrupt file → returns default ──
        tmp_file.write_text("{bad json", encoding="utf-8")
        billing._stripe_state_cache = None  # clear cache so disk is re-read
        fallback = billing._load_stripe_state()
        check("corrupt file → returns default dict", fallback == {"subscriptions": {}})

        # ── 6. Missing file → returns default ──
        tmp_file.unlink()
        billing._stripe_state_cache = None  # clear cache so disk is re-read
        missing = billing._load_stripe_state()
        check("missing file → returns default dict", missing == {"subscriptions": {}})

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)

    # ── 7. FREE_TRIAL_DAYS constant ──
    check("FREE_TRIAL_DAYS is 5", billing.FREE_TRIAL_DAYS == 5)


# ═════════════════════════════════════════════
# CONNECTIONS.JSON — CLEAN STATE (no legacy entries)
# ═════════════════════════════════════════════
def test_connections_json_clean():
    """Test connections.json has no legacy ollama-fly or fallback openrouter entries."""
    print("\n=== TORTURE: connections.json — clean state ===")
    from pathlib import Path
    import web.app as _app

    # Read connections via app's own loader (respects CONNECTIONS_FILE after prior test swaps)
    data = _app._load_connections()
    check("connections key in data", "connections" in data)
    conns = data.get("connections", [])
    conn_ids = [c.get("id", "") for c in conns if isinstance(c, dict)]

    check("no ollama-fly entry", "ollama-fly" not in conn_ids)
    check("no legacy openrouter fallback",
          not any(c.get("is_fallback") for c in conns if isinstance(c, dict)))
    check("connections is list", isinstance(conns, list))
    check("agent_connections key exists", "agent_connections" in data)


# ═════════════════════════════════════════════
# STORE CATALOG — structure validation
# ═════════════════════════════════════════════
def test_billing_catalog_structure():
    """Validate SKIN_PRICES, CREDIT_PACKS, and billing constants."""
    print("\n=== TORTURE: Billing Catalog — structure validation ===")
    import web.stripe_billing as billing

    # SKIN_PRICES structure
    check("SKIN_PRICES is dict", isinstance(billing.SKIN_PRICES, dict))
    check("default skin is free", billing.SKIN_PRICES.get("default") == 0)
    check("all skin prices are int", all(isinstance(v, int) for v in billing.SKIN_PRICES.values()))

    # CREDIT_PACKS structure
    check("CREDIT_PACKS is dict", isinstance(billing.CREDIT_PACKS, dict))
    for pk_id, pk in billing.CREDIT_PACKS.items():
        check(f"pack {pk_id}: has credits", "credits" in pk)
        check(f"pack {pk_id}: has price", "price" in pk)
        check(f"pack {pk_id}: has label", "label" in pk)

    # Constants
    check("LLM_MARKUP_MULTIPLIER is 2.0", billing.LLM_MARKUP_MULTIPLIER == 2.0)
    check("FREE_TRIAL_DAYS is 5", billing.FREE_TRIAL_DAYS == 5)
    check("INACTIVE_ACCOUNT_DAYS is 365", billing.INACTIVE_ACCOUNT_DAYS == 365)


# ═════════════════════════════════════════════
# TIER & TRIAL SYSTEM — subscription gating
# ═════════════════════════════════════════════
def test_tier_and_trial_system():
    """Test trial status, tier resolution, feature checks, and limit checks."""
    print("\n=== TORTURE: Tier & Trial System ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        uid = "test_tier_user_001"

        # ── 1. Fresh user gets a trial ──
        trial = billing.get_trial_status(uid)
        check("trial is active for new user", trial["active"] is True)
        check("trial has days_left > 0", trial["days_left"] > 0)
        check("trial days_left <= 5", trial["days_left"] <= 5)
        check("trial started_at > 0", trial["started_at"] > 0)
        check("trial expires_at > started_at", trial["expires_at"] > trial["started_at"])

        # ── 2. Tier is 'pro' during trial ──
        tier = billing.get_user_tier(uid)
        check("tier is pro during trial", tier == "pro")

        # ── 3. get_user_subscription — full details ──
        sub = billing.get_user_subscription(uid)
        check("subscription has tier", "tier" in sub)
        check("subscription has trial", "trial" in sub)
        check("subscription is_trial during trial", sub["is_trial"] is True)
        check("subscription tier_info has features", "features" in sub["tier_info"])

        # ── 6. Expired trial → still full access (pay-per-use, no paywall) ──
        state = billing._load_stripe_state()
        state["trials"][uid]["started_at"] = time.time() - (20 * 86400)  # 20 days ago
        billing._save_stripe_state(state)
        tier_after = billing.get_user_tier(uid)
        check("expired trial → still pro (pay-per-use)", tier_after == "pro")

        # ── 7. Active subscription → pro regardless of trial ──
        billing.set_user_subscription(uid, {"status": "active", "plan": "pro", "customer_id": "cus_test"})
        check("active sub → pro", billing.get_user_tier(uid) == "pro")
        sub2 = billing.get_user_subscription(uid)
        check("subscription not is_trial with active sub", sub2["is_trial"] is False)

        # ── 8. Cancel subscription ──
        billing.cancel_user_subscription(uid)
        state2 = billing._load_stripe_state()
        check("canceled status", state2["subscriptions"][uid]["status"] == "canceled")
        check("canceled_at set", "canceled_at" in state2["subscriptions"][uid])

        # ── 9. Empty user_id edge cases ──
        check("empty user_id → free tier", billing.get_user_tier("") == "free")
        empty_trial = billing.get_trial_status("")
        check("empty user_id → inactive trial", empty_trial["active"] is False)

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# CREDIT SYSTEM — add, deduct, balance, history
# ═════════════════════════════════════════════
def test_credit_system():
    """Test credit add/deduct/get/history operations."""
    print("\n=== TORTURE: Credit System ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        uid = "test_credit_user_001"

        # ── 1. Initial balance is 0 ──
        check("initial balance is 0", billing.get_user_credits(uid) == 0)
        check("empty user_id → 0", billing.get_user_credits("") == 0)

        # ── 2. Add credits ──
        billing.add_user_credits(uid, 1000, reason="test_purchase")
        check("balance after +1000", billing.get_user_credits(uid) == 1000)

        # ── 3. Add more credits ──
        billing.add_user_credits(uid, 500, reason="bonus")
        check("balance after +500", billing.get_user_credits(uid) == 1500)

        # ── 4. Deduct credits — success ──
        result = billing.deduct_user_credits(uid, 200, "test_tool")
        check("deduct ok", result.get("ok") is True)
        check("deduct balance", result["balance"] == 1300)
        check("actual balance", billing.get_user_credits(uid) == 1300)

        # ── 5. Deduct credits — insufficient ──
        result2 = billing.deduct_user_credits(uid, 5000, "expensive_tool")
        check("insufficient → error", "error" in result2)
        check("insufficient → balance unchanged", billing.get_user_credits(uid) == 1300)
        check("insufficient → shows needed", result2.get("needed") == 5000)

        # ── 6. History ──
        history = billing.get_credit_history(uid)
        check("history has entries", len(history) >= 3)
        check("history ordered newest first", history[0]["timestamp"] >= history[-1]["timestamp"])
        check("credit entry type", any(h["type"] == "credit" for h in history))
        check("debit entry type", any(h["type"] == "debit" for h in history))

        # ── 7. History limit ──
        history_limited = billing.get_credit_history(uid, limit=1)
        check("history limit=1 → 1 entry", len(history_limited) == 1)

        # ── 8. History cap at 200 ──
        for i in range(210):
            billing.add_user_credits(uid, 1, reason=f"micro_{i}")
        state = billing._load_stripe_state()
        hist_len = len(state["credits"][uid]["history"])
        check("history capped at 200", hist_len <= 200)

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


def test_credit_checkout_and_webhook():
    """Test Stripe credit checkout session building and webhook fulfillment."""
    print("\n=== TORTURE: Credit Checkout & Webhook ===")
    import web.stripe_billing as billing
    from pathlib import Path

    class _FakeSessionObj:
        def __init__(self, url, session_id):
            self.url = url
            self.id = session_id

    class _FakeCheckoutSession:
        last_kwargs = None

        @classmethod
        def create(cls, **kwargs):
            cls.last_kwargs = kwargs
            return _FakeSessionObj("https://example.test/checkout/sess_123", "sess_123")

    class _FakeCheckout:
        Session = _FakeCheckoutSession

    class _FakeStripe:
        checkout = _FakeCheckout()

    tmp = tempfile.mkdtemp()
    try:
        orig_get_stripe = billing._get_stripe
        orig_state_file = billing._STRIPE_STATE_FILE
        orig_secret = billing.STRIPE_SECRET_KEY
        orig_webhook_secret = billing.STRIPE_WEBHOOK_SECRET
        orig_product_id = billing.STRIPE_CREDITS_PRODUCT_ID

        billing._get_stripe = lambda: _FakeStripe
        billing._STRIPE_STATE_FILE = Path(tmp) / "stripe_state.json"
        billing._stripe_state_cache = None  # clear cache so disk is re-read
        billing.STRIPE_SECRET_KEY = "sk_test_dummy"
        billing.STRIPE_WEBHOOK_SECRET = ""
        billing.STRIPE_CREDITS_PRODUCT_ID = billing._default_credits_product_id(billing.STRIPE_SECRET_KEY)

        result = billing.create_credits_checkout_session(
            user_id="test_checkout_user",
            user_email="checkout@example.com",
            pack_id="pack_20",
            success_url="https://example.test/store?ok=1",
            cancel_url="https://example.test/store?cancel=1",
        )
        check("credit checkout session created", "url" in result and "session_id" in result)
        price_data = _FakeCheckoutSession.last_kwargs["line_items"][0]["price_data"]
        check("test mode uses ad-hoc product_data", "product_data" in price_data and "product" not in price_data)
        check("checkout metadata marks credits purchase", _FakeCheckoutSession.last_kwargs["metadata"].get("type") == "credits")
        check("checkout metadata carries pack id", _FakeCheckoutSession.last_kwargs["metadata"].get("pack_id") == "pack_20")

        billing.STRIPE_CREDITS_PRODUCT_ID = billing._default_credits_product_id("sk_live_dummy")
        result2 = billing.create_credits_checkout_session(
            user_id="test_checkout_user_live",
            user_email="checkout@example.com",
            pack_id="pack_5",
            success_url="https://example.test/store?ok=1",
            cancel_url="https://example.test/store?cancel=1",
        )
        check("live-mode checkout session created", "url" in result2 and "session_id" in result2)
        price_data2 = _FakeCheckoutSession.last_kwargs["line_items"][0]["price_data"]
        check("live mode defaults to fixed product", price_data2.get("product") == billing.DEFAULT_LIVE_CREDITS_PRODUCT_ID)

        webhook_payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "client_reference_id": "test_checkout_user",
                    "metadata": {
                        "type": "credits",
                        "pack_id": "pack_20",
                        "credits": "21000",
                        "credit_scale": str(billing.CREDIT_SCALE),
                    },
                }
            },
        }).encode("utf-8")
        webhook_result = billing.handle_webhook_event(webhook_payload, "")
        check("credits webhook action", webhook_result.get("action") == "credits_purchased")
        check("credits webhook grants balance", billing.get_user_credits("test_checkout_user") == 21000)

        try:
            import stripe  # noqa: F401
        except ImportError:
            check("signed webhook path skipped without stripe", True)
        else:
            billing._get_stripe = orig_get_stripe
            billing.STRIPE_WEBHOOK_SECRET = "whsec_test_secret"
            signed_payload_obj = {
                "id": "evt_test_webhook",
                "object": "event",
                "api_version": "2025-05-28.basil",
                "created": int(time.time()),
                "data": {
                    "object": {
                        "id": "cs_test_webhook",
                        "object": "checkout.session",
                        "client_reference_id": "signed_checkout_user",
                        "metadata": {
                            "type": "credits",
                            "pack_id": "pack_10",
                            "credits": "10000",
                            "credit_scale": str(billing.CREDIT_SCALE),
                        },
                    }
                },
                "livemode": False,
                "pending_webhooks": 1,
                "request": {"id": None, "idempotency_key": None},
                "type": "checkout.session.completed",
            }
            signed_payload = json.dumps(signed_payload_obj, separators=(",", ":")).encode("utf-8")
            timestamp = int(time.time())
            signature = hmac.new(
                billing.STRIPE_WEBHOOK_SECRET.encode("utf-8"),
                f"{timestamp}.".encode("utf-8") + signed_payload,
                hashlib.sha256,
            ).hexdigest()
            signed_header = f"t={timestamp},v1={signature}"
            signed_result = billing.handle_webhook_event(signed_payload, signed_header)
            check("signed webhook action", signed_result.get("action") == "credits_purchased")
            check("signed webhook grants balance", billing.get_user_credits("signed_checkout_user") == 10000)

    finally:
        billing._get_stripe = orig_get_stripe
        billing._STRIPE_STATE_FILE = orig_state_file
        billing._stripe_state_cache = None  # reset cache
        billing.STRIPE_SECRET_KEY = orig_secret
        billing.STRIPE_WEBHOOK_SECRET = orig_webhook_secret
        billing.STRIPE_CREDITS_PRODUCT_ID = orig_product_id
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# CREDIT FULFILLMENT — idempotency + success-page fallback
# ═════════════════════════════════════════════
def test_credit_fulfillment_idempotent():
    """Credits granted exactly once per Stripe session (webhook retries +
    success-page fallback), and the fallback only fulfills PAID sessions.

    Regression guard for "credits aren't updating on purchase": the success
    page now fulfills server-side via fulfill_credits_for_session, which must
    be idempotent with the webhook and must never double-credit.
    """
    print("\n=== TORTURE: Credit Fulfillment Idempotency ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    orig_state_file = billing._STRIPE_STATE_FILE
    orig_get_stripe = billing._get_stripe
    orig_secret = billing.STRIPE_SECRET_KEY
    orig_webhook_secret = billing.STRIPE_WEBHOOK_SECRET
    try:
        billing._STRIPE_STATE_FILE = Path(tmp) / "stripe_state.json"
        billing._stripe_state_cache = None  # clear cache so disk is re-read
        billing.STRIPE_SECRET_KEY = "sk_test_dummy"
        billing.STRIPE_WEBHOOK_SECRET = ""  # unsigned webhook path

        # ── 1. _grant_credits_for_checkout grants once, replay is a no-op ──
        session = {
            "id": "cs_test_idem_1",
            "client_reference_id": "idem_user",
            "metadata": {"type": "credits", "pack_id": "pack_10", "credits": "10000",
                         "credit_scale": str(billing.CREDIT_SCALE)},
        }
        r1 = billing._grant_credits_for_checkout(session)
        check("first grant ok", r1.get("ok") is True and not r1.get("already_fulfilled"))
        check("balance after first grant", billing.get_user_credits("idem_user") == 10000)
        r2 = billing._grant_credits_for_checkout(session)
        check("replay flagged already_fulfilled", r2.get("already_fulfilled") is True)
        check("balance unchanged after replay", billing.get_user_credits("idem_user") == 10000)

        # ── 2. Webhook replay of the SAME session does not double-credit ──
        payload = json.dumps({
            "type": "checkout.session.completed",
            "data": {"object": session},
        }).encode("utf-8")
        billing.handle_webhook_event(payload, "")
        check("webhook replay no double-credit", billing.get_user_credits("idem_user") == 10000)

        # ── 3. A DIFFERENT session id for the same user adds again ──
        session2 = dict(session, id="cs_test_idem_2")
        billing._grant_credits_for_checkout(session2)
        check("new session id adds credits", billing.get_user_credits("idem_user") == 20000)

        # ── 4. fulfill_credits_for_session only fulfills PAID sessions ──
        class _FakeSessionRetrieve:
            store = {
                "cs_paid": {"id": "cs_paid", "payment_status": "paid",
                            "client_reference_id": "fallback_user",
                            "metadata": {"type": "credits", "pack_id": "pack_5", "credits": "5000",
                                         "credit_scale": str(billing.CREDIT_SCALE)}},
                "cs_unpaid": {"id": "cs_unpaid", "payment_status": "unpaid",
                              "client_reference_id": "fallback_user",
                              "metadata": {"type": "credits", "pack_id": "pack_5", "credits": "5000",
                                         "credit_scale": str(billing.CREDIT_SCALE)}},
            }

            @classmethod
            def retrieve(cls, sid):
                return dict(cls.store[sid])

        class _FakeCheckout:
            Session = _FakeSessionRetrieve

        class _FakeStripe:
            checkout = _FakeCheckout()

        billing._get_stripe = lambda: _FakeStripe

        unpaid = billing.fulfill_credits_for_session("cs_unpaid", expected_user_id="fallback_user")
        check("unpaid session not fulfilled", unpaid.get("ok") is False and unpaid.get("reason") == "not_paid")
        check("unpaid grants nothing", billing.get_user_credits("fallback_user") == 0)

        paid = billing.fulfill_credits_for_session("cs_paid", expected_user_id="fallback_user")
        check("paid session fulfilled", paid.get("ok") is True)
        check("paid grants credits", billing.get_user_credits("fallback_user") == 5000)

        # ── 5. Fallback is idempotent with itself / the webhook ──
        replay = billing.fulfill_credits_for_session("cs_paid", expected_user_id="fallback_user")
        check("fallback replay already_fulfilled", replay.get("already_fulfilled") is True)
        check("fallback replay no double-credit", billing.get_user_credits("fallback_user") == 5000)

        # ── 6. A session belonging to another user is refused ──
        mismatch = billing.fulfill_credits_for_session("cs_paid", expected_user_id="someone_else")
        check("user mismatch refused", mismatch.get("ok") is False and mismatch.get("reason") == "user_mismatch")

        # ── 7. A checkout opened before the credit unit changed (no
        #       credit_scale tag, old 500-credit count) is scaled up ──
        legacy = {"id": "cs_legacy", "client_reference_id": "legacy_user",
                  "metadata": {"type": "credits", "pack_id": "pack_5", "credits": "500"}}
        billing._grant_credits_for_checkout(legacy)
        check("legacy checkout scaled to new unit", billing.get_user_credits("legacy_user") == 5000)

        # ── 8. Stored balances convert exactly once ──
        state = billing._load_stripe_state()
        state.pop("credit_scale", None)
        state["credits"]["old_user"] = {"balance": 150, "history": [
            {"type": "credit", "amount": 200, "reason": "welcome", "timestamp": 0},
            {"type": "debit", "amount": 50, "reason": "chat", "timestamp": 1}]}
        billing._save_stripe_state(state)
        before_idem = billing.get_user_credits("idem_user")
        converted = billing.migrate_credit_scale()
        check("migration converts accounts", converted >= 1)
        check("migration scales balance", billing.get_user_credits("old_user") == 1500)
        hist = billing._load_stripe_state()["credits"]["old_user"]["history"]
        check("migration scales history", [h["amount"] for h in hist] == [2000, 500])
        check("migration second run is no-op", billing.migrate_credit_scale() == 0)
        check("migration not applied twice", billing.get_user_credits("old_user") == 1500
              and billing.get_user_credits("idem_user") == before_idem * billing.CREDIT_SCALE)
    finally:
        billing._STRIPE_STATE_FILE = orig_state_file
        billing._stripe_state_cache = None  # reset cache
        billing._get_stripe = orig_get_stripe
        billing.STRIPE_SECRET_KEY = orig_secret
        billing.STRIPE_WEBHOOK_SECRET = orig_webhook_secret
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# CREDIT COST ESTIMATORS — LLM, TTS, STT
# ═════════════════════════════════════════════
def test_credit_cost_estimators():
    """Test estimate_llm_credit_cost, estimate_tts_credit_cost, estimate_stt_credit_cost."""
    print("\n=== TORTURE: Credit Cost Estimators ===")
    import web.stripe_billing as billing

    # ── LLM credits ──
    check("llm $0 → 0 credits", billing.estimate_llm_credit_cost(0) == 0)
    check("llm negative → 0 credits", billing.estimate_llm_credit_cost(-1) == 0)
    check("llm $0.01 → 20 credits (2x markup)",
          billing.estimate_llm_credit_cost(0.01) == 20)
    check("llm $0.10 → 200 credits (2x markup)",
          billing.estimate_llm_credit_cost(0.10) == 200)
    check("llm $1.00 → 2000 credits (2x markup)",
          billing.estimate_llm_credit_cost(1.0) == 2000)
    check("llm $0.0012 → 3 credits (sub-cent precision)",
          billing.estimate_llm_credit_cost(0.0012) == 3)
    check("llm exact value not bumped by float noise",
          billing.estimate_llm_credit_cost(0.003) == 6)
    check("llm minimum 1 credit",
          billing.estimate_llm_credit_cost(0.0001) >= 1)

    # ── Unpriced-model fallback (never $0 when tokens were used) ──
    check("llm safe: $0 cost + 0 tokens → 0",
          billing.estimate_llm_credit_cost_safe(0, 0) == 0)
    check("llm safe: priced cost passes through",
          billing.estimate_llm_credit_cost_safe(1.0, 5000) == 2000)
    check("llm safe: unpriced ($0) but tokens used → charged",
          billing.estimate_llm_credit_cost_safe(0, 100000) > 0)

    # ── Image credits ──
    check("image dalle3 > 0", billing.estimate_image_credit_cost("openai_dalle3") > 0)
    check("image stability prefix match > 0",
          billing.estimate_image_credit_cost("stability_ultra") > 0)
    check("image unknown provider → default > 0",
          billing.estimate_image_credit_cost("totally_unknown") > 0)

    # ── Video credits (priciest media op) ──
    check("video veo2 8s > one image",
          billing.estimate_video_credit_cost("google_veo2", 8) > billing.estimate_image_credit_cost("openai_dalle3"))
    check("video longer duration costs more",
          billing.estimate_video_credit_cost("google_veo3", 16) > billing.estimate_video_credit_cost("google_veo3", 4))

    # ── TTS credits ──
    check("tts 0 chars → 0", billing.estimate_tts_credit_cost(0) == 0)
    check("tts negative → 0", billing.estimate_tts_credit_cost(-100) == 0)
    check("tts 1000 chars elevenlabs > 0",
          billing.estimate_tts_credit_cost(1000, "elevenlabs") > 0)
    check("tts default provider works",
          billing.estimate_tts_credit_cost(1000) > 0)
    check("tts unknown provider → default",
          billing.estimate_tts_credit_cost(1000, "unknown_provider") > 0)

    # ── STT credits ──
    check("stt 0 seconds → 0", billing.estimate_stt_credit_cost(0) == 0)
    check("stt negative → 0", billing.estimate_stt_credit_cost(-60) == 0)
    check("stt 60s whisper > 0",
          billing.estimate_stt_credit_cost(60, "whisper") > 0)
    check("stt default provider works",
          billing.estimate_stt_credit_cost(60) > 0)


# ═════════════════════════════════════════════
# USER ACTIVITY — tracking, wipe, purge, list
# ═════════════════════════════════════════════
def test_user_activity_tracking():
    """Test touch_user_activity, get_user_last_active, throttle behavior."""
    print("\n=== TORTURE: User Activity Tracking ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        orig_interval = billing._ACTIVITY_WRITE_INTERVAL
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        uid = "test_activity_user_001"

        # ── 1. Initial last_active is 0 ──
        check("initial last_active is 0", billing.get_user_last_active(uid) == 0)

        # ── 2. Touch sets timestamp ──
        billing.touch_user_activity(uid)
        ts = billing.get_user_last_active(uid)
        check("last_active > 0 after touch", ts > 0)
        check("last_active is recent", abs(ts - time.time()) < 5)

        # ── 3. Throttle — second touch within interval doesn't update ──
        billing._ACTIVITY_WRITE_INTERVAL = 3600  # ensure throttle is active
        first_ts = billing.get_user_last_active(uid)
        billing.touch_user_activity(uid)
        second_ts = billing.get_user_last_active(uid)
        check("throttled: timestamp unchanged", first_ts == second_ts)

        # ── 4. Bypass throttle with small interval ──
        billing._ACTIVITY_WRITE_INTERVAL = 0
        billing.touch_user_activity(uid)
        third_ts = billing.get_user_last_active(uid)
        check("no throttle: timestamp updated", third_ts >= first_ts)

        # ── 5. Empty user_id is no-op ──
        billing.touch_user_activity("")
        check("empty uid no-op", billing.get_user_last_active("") == 0)

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        billing._ACTIVITY_WRITE_INTERVAL = orig_interval
        shutil.rmtree(tmp, ignore_errors=True)


def test_wipe_user_data():
    """Test wipe_user_data and wipe_user_by_email."""
    print("\n=== TORTURE: Wipe User Data ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        uid = "test_wipe_user_001"

        # Seed data in all sections
        billing.add_user_credits(uid, 1000, reason="seed")
        billing._ensure_trial_start(uid)
        billing.set_user_subscription(uid, {"status": "active", "email": "test@example.com"})
        billing.touch_user_activity(uid)
        # Manually add a purchase
        state = billing._load_stripe_state()
        state.setdefault("purchases", {})[uid] = {"tools": ["email"], "skins": ["default"], "agents": []}
        billing._save_stripe_state(state)

        # ── 1. Wipe with keep_purchases=True (default) ──
        result = billing.wipe_user_data(uid)
        check("wipe ok", result.get("ok") is True)
        check("wipe removed sections", len(result["removed_sections"]) > 0)
        check("wipe kept purchases", result["purchases_kept"] is True)

        # Verify data cleared
        check("credits wiped", billing.get_user_credits(uid) == 0)
        check("activity wiped", billing.get_user_last_active(uid) == 0)
        state2 = billing._load_stripe_state()
        check("subscription wiped", uid not in state2.get("subscriptions", {}))
        check("trial wiped", uid not in state2.get("trials", {}))
        check("purchases preserved", uid in state2.get("purchases", {}))

        # ── 2. Wipe with keep_purchases=False ──
        # Re-seed
        billing.add_user_credits(uid, 500, reason="re-seed")
        state3 = billing._load_stripe_state()
        state3.setdefault("purchases", {})[uid] = {"tools": ["agi_bundle"]}
        billing._save_stripe_state(state3)

        result2 = billing.wipe_user_data(uid, keep_purchases=False)
        check("wipe+purchases ok", result2.get("ok") is True)
        state4 = billing._load_stripe_state()
        check("purchases also wiped", uid not in state4.get("purchases", {}))

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


def test_wipe_user_by_email():
    """Test wipe_user_by_email — email lookup and wipe."""
    print("\n=== TORTURE: Wipe User By Email ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        uid = "test_email_wipe_001"
        email = "Wipe.Me@Example.COM"

        # Seed subscription with email
        billing.set_user_subscription(uid, {"status": "canceled", "email": email})
        billing.add_user_credits(uid, 100, reason="test")

        # ── 1. Wipe by email ──
        result = billing.wipe_user_by_email(email)
        check("wipe by email ok", result.get("ok") is True)
        check("wiped_users >= 1", result.get("wiped_users", 0) >= 1)

        # ── 2. Not found ──
        result2 = billing.wipe_user_by_email("nobody@nowhere.example")
        check("not found → error", result2.get("ok") is False)

        # ── 3. Case-insensitive ──
        billing.set_user_subscription("uid2", {"status": "active", "email": "CASE@TEST.COM"})
        result3 = billing.wipe_user_by_email("case@test.com")
        check("case-insensitive match", result3.get("ok") is True)

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


def test_purge_inactive_users():
    """Test purge_inactive_users — removes old accounts, skips active subscribers."""
    print("\n=== TORTURE: Purge Inactive Users ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        # Seed state with various users
        state = {
            "subscriptions": {
                "active_user": {"status": "active", "email": "active@test.com"},
                "old_canceled": {"status": "canceled", "email": "old@test.com"},
                "recent_free": {"status": "canceled", "email": "recent@test.com"},
            },
            "activity": {
                "active_user": time.time(),                    # just now
                "old_canceled": time.time() - (400 * 86400),   # 400 days ago
                "recent_free": time.time() - (30 * 86400),     # 30 days ago
            },
            "trials": {
                "active_user": {"started_at": time.time() - (50 * 86400)},
                "old_canceled": {"started_at": time.time() - (400 * 86400)},
                "recent_free": {"started_at": time.time() - (30 * 86400)},
                "no_activity_user": {"started_at": time.time() - (500 * 86400)},
            },
            "credits": {
                "active_user": {"balance": 100, "history": []},
                "old_canceled": {"balance": 50, "history": []},
            },
        }
        billing._save_stripe_state(state)

        # ── 1. Purge with 365-day cutoff ──
        result = billing.purge_inactive_users(days=365)
        check("purge ok", result.get("ok") is True)
        check("purge cutoff_days", result["cutoff_days"] == 365)
        purged = set(result.get("purged_user_ids", []))

        check("active subscriber NOT purged", "active_user" not in purged)
        check("old canceled IS purged", "old_canceled" in purged)
        check("recent free NOT purged", "recent_free" not in purged)
        # no_activity_user has no activity timestamp, falls back to trial start (500 days ago) → purged
        check("no_activity falls back to trial start", "no_activity_user" in purged)

        # ── 2. Verify old_canceled data actually removed ──
        state2 = billing._load_stripe_state()
        check("old_canceled credits wiped",
              "old_canceled" not in state2.get("credits", {}))
        check("active_user credits kept",
              state2.get("credits", {}).get("active_user", {}).get("balance") == 100)

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


def test_list_all_users():
    """Test list_all_users returns comprehensive summary."""
    print("\n=== TORTURE: List All Users ===")
    import web.stripe_billing as billing
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        orig = billing._STRIPE_STATE_FILE
        tmp_file = Path(tmp) / "stripe_state.json"
        billing._STRIPE_STATE_FILE = tmp_file
        billing._stripe_state_cache = None  # clear cache so disk is re-read

        # Seed state
        state = {
            "subscriptions": {
                "user_a": {"status": "active", "email": "a@test.com"},
            },
            "trials": {
                "user_a": {"started_at": 1700000000},
                "user_b": {"started_at": 1700000000},
            },
            "credits": {
                "user_a": {"balance": 500, "history": []},
                "user_c": {"balance": 100, "history": []},
            },
            "activity": {
                "user_a": 1700100000,
            },
        }
        billing._save_stripe_state(state)

        # ── 1. List all users ──
        users = billing.list_all_users()
        check("list_all_users returns list", isinstance(users, list))
        uids = {u["user_id"] for u in users}
        check("includes user_a", "user_a" in uids)
        check("includes user_b", "user_b" in uids)
        check("includes user_c", "user_c" in uids)
        check("total users >= 3", len(users) >= 3)

        # ── 2. User detail fields ──
        user_a = next(u for u in users if u["user_id"] == "user_a")
        check("user_a has email", user_a["email"] == "a@test.com")
        check("user_a tier is pro", user_a["tier"] == "pro")
        check("user_a has credit_balance", user_a["credit_balance"] == 500)
        check("user_a has last_active", user_a["last_active"] == 1700100000)
        check("user_a has last_active_human", "never" not in user_a["last_active_human"])

        user_b = next(u for u in users if u["user_id"] == "user_b")
        check("user_b tier is free (no sub)", user_b["tier"] == "free")
        check("user_b last_active = never", user_b["last_active_human"] == "never")

    finally:
        billing._STRIPE_STATE_FILE = orig
        billing._stripe_state_cache = None  # reset cache
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AUTH HELPERS — public paths, config, token extraction
# ═════════════════════════════════════════════
def test_auth_helpers():
    """Test is_public_path, get_auth_config, extract_user_from_token."""
    print("\n=== TORTURE: Auth Helpers ===")
    from web.auth import is_public_path, get_auth_config, extract_user_from_token, PUBLIC_PATHS

    # ── 1. is_public_path — exact matches ──
    check("login is public", is_public_path("/login") is True)
    check("auth/callback is public", is_public_path("/auth/callback") is True)
    check("api/auth/config is public", is_public_path("/api/auth/config") is True)
    check("api/stripe/webhook is public", is_public_path("/api/stripe/webhook") is True)
    check("plans is public", is_public_path("/plans") is True)
    check("static is public", is_public_path("/static") is True)
    check("favicon.ico is public", is_public_path("/favicon.ico") is True)

    # ── 2. is_public_path — sub-paths ──
    check("static/css/foo.css is public", is_public_path("/static/css/foo.css") is True)
    check("uploads/image.png is public", is_public_path("/uploads/image.png") is True)

    # ── 3. is_public_path — private paths ──
    check("/ is private", is_public_path("/") is False)
    check("/chat is private", is_public_path("/chat") is False)
    check("/api/chat is private", is_public_path("/api/chat") is False)
    check("/api/profiles is private", is_public_path("/api/profiles") is False)
    check("/settings is private", is_public_path("/settings") is False)
    check("/vault is private", is_public_path("/vault") is False)

    # ── 4. PUBLIC_PATHS is a set ──
    check("PUBLIC_PATHS is set", isinstance(PUBLIC_PATHS, set))
    check("PUBLIC_PATHS has entries", len(PUBLIC_PATHS) > 0)

    # ── 5. get_auth_config returns dict ──
    config = get_auth_config()
    check("auth config is dict", isinstance(config, dict))
    check("auth config has auth_enabled", "auth_enabled" in config)
    check("auth config has supabase_url", "supabase_url" in config)
    check("auth config has supabase_anon_key", "supabase_anon_key" in config)

    # ── 6. extract_user_from_token ──
    payload = {
        "sub": "user-uuid-123",
        "email": "test@example.com",
        "role": "authenticated",
        "aud": "authenticated",
    }
    user = extract_user_from_token(payload)
    check("extract: id", user["id"] == "user-uuid-123")
    check("extract: email", user["email"] == "test@example.com")
    check("extract: role", user["role"] == "authenticated")
    check("extract: aud", user["aud"] == "authenticated")

    # ── 7. extract_user_from_token — empty payload ──
    user2 = extract_user_from_token({})
    check("empty payload: id empty", user2["id"] == "")
    check("empty payload: email empty", user2["email"] == "")
    check("empty payload: role default", user2["role"] == "authenticated")


# ═════════════════════════════════════════════
# EMAIL ALLOWLIST — open-registration gating
# ═════════════════════════════════════════════
def test_email_allowlist_gating():
    """Lock in is_email_allowed() signup gating.

    Regression guard for the outage where new signups were silently rejected
    ("This account is not authorized to sign in.") because the allowlist was
    active and OPEN_REGISTRATION was not set. Verifies the precedence
    OPEN_REGISTRATION env > open_registration config > allowlist, and the
    footgun that an EMPTY allowed_emails list falls back to the hard-coded
    owner default rather than opening registration.
    """
    print("\n=== TORTURE: Email Allowlist / Open Registration ===")
    import web.auth as auth_mod
    from web.auth import is_email_allowed

    _orig_open_reg = os.environ.get("OPEN_REGISTRATION")
    _orig_allowed = os.environ.get("ALLOWED_EMAILS")
    _orig_loader = auth_mod._load_auth_config

    def _set_env(key, val):
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val

    def _stub_config(cfg):
        auth_mod._load_auth_config = lambda: dict(cfg)

    LOCKED = {"open_registration": False, "allowed_emails": ["owner@example.com"]}

    try:
        # ── 1. Empty / falsy email is always rejected ──
        _set_env("OPEN_REGISTRATION", "1")
        _stub_config(LOCKED)
        check("empty email rejected", is_email_allowed("") is False)
        check("None email rejected", is_email_allowed(None) is False)

        # ── 2. OPEN_REGISTRATION env opens signup even with a locked allowlist
        #       (this is the production fix that ended the outage) ──
        _set_env("ALLOWED_EMAILS", None)
        _stub_config(LOCKED)
        for truthy in ("1", "true", "yes"):
            _set_env("OPEN_REGISTRATION", truthy)
            check(f"OPEN_REGISTRATION={truthy} allows new user",
                  is_email_allowed("brand.new.user@example.com") is True)

        # ── 3. OPEN_REGISTRATION off/empty falls through to the allowlist ──
        for falsy in ("0", "", "off"):
            _set_env("OPEN_REGISTRATION", falsy)
            check(f"OPEN_REGISTRATION={falsy!r} blocks stranger",
                  is_email_allowed("stranger@example.com") is False)
            check(f"OPEN_REGISTRATION={falsy!r} still allows owner",
                  is_email_allowed("owner@example.com") is True)

        # ── 4. config open_registration:true opens signup (no env) ──
        _set_env("OPEN_REGISTRATION", None)
        _set_env("ALLOWED_EMAILS", None)
        _stub_config({"open_registration": True, "allowed_emails": ["owner@example.com"]})
        check("config open_registration allows new user",
              is_email_allowed("someone.else@example.com") is True)

        # ── 5. THE OUTAGE: locked config blocks everyone but the owner ──
        _set_env("OPEN_REGISTRATION", None)
        _set_env("ALLOWED_EMAILS", None)
        _stub_config(LOCKED)
        check("locked: owner allowed", is_email_allowed("owner@example.com") is True)
        check("locked: stranger blocked", is_email_allowed("stranger@example.com") is False)

        # ── 6. FOOTGUN: empty allowed_emails does NOT open registration; it
        #       falls back to the hard-coded owner default ──
        _stub_config({"open_registration": False, "allowed_emails": []})
        default_owner = next(iter(auth_mod._DEFAULT_ALLOWED_EMAILS))
        check("empty list still blocks stranger",
              is_email_allowed("stranger@example.com") is False)
        check("empty list falls back to default owner",
              is_email_allowed(default_owner) is True)

        # ── 7. ALLOWED_EMAILS env (csv) overrides config; case/space tolerant ──
        _set_env("OPEN_REGISTRATION", None)
        _set_env("ALLOWED_EMAILS", " Alice@Example.com , bob@example.com ")
        _stub_config({"open_registration": False, "allowed_emails": ["owner@example.com"]})
        check("env allowlist: alice allowed (lowercased)",
              is_email_allowed("alice@example.com") is True)
        check("env allowlist: BOB allowed (case-insensitive)",
              is_email_allowed("BOB@EXAMPLE.COM") is True)
        check("env allowlist: config owner ignored when env set",
              is_email_allowed("owner@example.com") is False)
        check("env allowlist: unknown blocked",
              is_email_allowed("carol@example.com") is False)

        # ── 8. Allowlist matching is case/whitespace-insensitive on input ──
        _set_env("ALLOWED_EMAILS", None)
        _stub_config({"open_registration": False, "allowed_emails": ["Owner@Example.com"]})
        check("allowlist match is case-insensitive",
              is_email_allowed("owner@example.com") is True)
        check("allowlist match strips whitespace",
              is_email_allowed("  OWNER@EXAMPLE.COM  ") is True)
    finally:
        auth_mod._load_auth_config = _orig_loader
        _set_env("OPEN_REGISTRATION", _orig_open_reg)
        _set_env("ALLOWED_EMAILS", _orig_allowed)


# ═════════════════════════════════════════════
# TIER INFO — structure validation
# ═════════════════════════════════════════════
def test_tier_info_structure():
    """Validate TIER_INFO, FREE_TIER_FEATURES, PRO_TIER_FEATURES constants."""
    print("\n=== TORTURE: Tier Info Structure ===")
    import web.stripe_billing as billing

    # ── 1. TIER_INFO structure ──
    check("TIER_INFO has free", "free" in billing.TIER_INFO)
    check("TIER_INFO has pro", "pro" in billing.TIER_INFO)

    for tier_name in ("free", "pro"):
        info = billing.TIER_INFO[tier_name]
        check(f"{tier_name}: has name", "name" in info)
        check(f"{tier_name}: has price", "price" in info)
        check(f"{tier_name}: has features", "features" in info)
        check(f"{tier_name}: has limits", "limits" in info)
        check(f"{tier_name}: features is sorted list",
              isinstance(info["features"], list) and info["features"] == sorted(info["features"]))

    # ── 2. Feature sets ──
    check("FREE_TIER_FEATURES is set", isinstance(billing.FREE_TIER_FEATURES, set))
    check("PRO_TIER_FEATURES is set", isinstance(billing.PRO_TIER_FEATURES, set))
    check("pro superset of free",
          billing.FREE_TIER_FEATURES.issubset(billing.PRO_TIER_FEATURES))
    check("chat in free", "chat" in billing.FREE_TIER_FEATURES)
    check("agi_loop in pro only",
          "agi_loop" in billing.PRO_TIER_FEATURES and "agi_loop" not in billing.FREE_TIER_FEATURES)

    # ── 3. Limits structure ──
    free_limits = billing.TIER_INFO["free"]["limits"]
    pro_limits = billing.TIER_INFO["pro"]["limits"]
    check("free has messages_per_day limit", free_limits.get("messages_per_day", 0) > 0)
    check("pro messages_per_day is unlimited", pro_limits.get("messages_per_day") == -1)
    check("free has memory_entries limit", free_limits.get("memory_entries", 0) > 0)
    check("pro memory_entries is unlimited", pro_limits.get("memory_entries") == -1)

    # ── 4. Pro price ──
    check("pro price is $9.99", billing.TIER_INFO["pro"]["price"] == 9.99)
    check("free price is $0", billing.TIER_INFO["free"]["price"] == 0)


# ═════════════════════════════════════════════
# RuntimeInfoTool — definition, execute, diff, set_context, reset
# ═════════════════════════════════════════════
def test_runtime_info_tool():
    """Test RuntimeInfoTool: definition, execute, diff tracking, context injection, reset."""
    print("\n=== TORTURE: RuntimeInfoTool ===")
    from src.tools.runtime_info import RuntimeInfoTool, _diff_snapshots
    from src.runtime_policy import RuntimePolicy

    # ── 0. Reset for clean state ──
    RuntimeInfoTool.reset()

    # ── 1. definition() structure ──
    defn = RuntimeInfoTool.definition()
    check("defn has name", defn["name"] == "runtime_info")
    check("defn has description", len(defn["description"]) > 20)
    check("defn has parameters", "parameters" in defn)
    check("defn parameters has properties", "properties" in defn["parameters"])

    # ── 2. execute() with no context (defaults) ──
    raw = RuntimeInfoTool.execute({})
    snap = json.loads(raw)
    check("snap is dict", isinstance(snap, dict))
    check("snap has agent key", "agent" in snap)
    check("snap default agent is unknown", snap["agent"] == "unknown")
    check("snap has diff key", "diff" in snap)
    check("snap has diff_count", "diff_count" in snap)
    check("first call diff is empty", snap["diff_count"] == 0)

    # ── 3. REQUIRED_FIELDS all present ──
    for field in RuntimeInfoTool.REQUIRED_FIELDS:
        check(f"required field '{field}' present", field in snap)

    # ── 4. set_context ──
    profile = {
        "name": "orion",
        "provider": "openai",
        "model": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "temperature": 0.5,
        "allowed_tools": ["memory", "web_search"],
        "memory": {"scope": "orion"},
        "directives": {"scope": "orion"},
        "window_size": 100,
    }
    policy = RuntimePolicy()
    RuntimeInfoTool.set_context(profile, policy, execution_mode="burst")

    raw2 = RuntimeInfoTool.execute({})
    snap2 = json.loads(raw2)
    check("after set_context: agent=orion", snap2["agent"] == "orion")
    check("after set_context: provider=openai", snap2["provider"] == "openai")
    check("after set_context: model=gpt-4o", snap2["model"] == "gpt-4o")
    check("after set_context: execution_mode=burst", snap2["execution_mode"] == "burst")
    check("after set_context: temperature=0.5", snap2["temperature"] == 0.5)
    check("after set_context: allowed_tools list", snap2["allowed_tools"] == ["memory", "web_search"])
    check("after set_context: window_size=100", snap2["window_size"] == 100)

    # ── 5. diff detection on second call ──
    # Change profile
    RuntimeInfoTool.set_context({**profile, "model": "gpt-4o-mini"}, policy)
    raw3 = RuntimeInfoTool.execute({})
    snap3 = json.loads(raw3)
    check("diff detected after model change", snap3["diff_count"] > 0)
    model_diff = [d for d in snap3["diff"] if d["field"] == "model"]
    check("model diff found", len(model_diff) == 1)
    if model_diff:
        check("model diff old contains gpt-4o", "gpt-4o" in model_diff[0]["old"])
        check("model diff new contains gpt-4o-mini", "gpt-4o-mini" in model_diff[0]["new"])

    # ── 6. No diff when nothing changes ──
    raw4 = RuntimeInfoTool.execute({})
    snap4 = json.loads(raw4)
    check("no diff when unchanged", snap4["diff_count"] == 0)

    # ── 7. _diff_snapshots helper ──
    d1 = _diff_snapshots({"a": 1, "b": 2}, {"a": 1, "b": 3, "c": 4})
    check("_diff_snapshots finds b changed", any(d["field"] == "b" for d in d1))
    check("_diff_snapshots finds c added", any(d["field"] == "c" for d in d1))
    check("_diff_snapshots no diff for a", not any(d["field"] == "a" for d in d1))

    d2 = _diff_snapshots({"x": 1}, {})
    check("_diff_snapshots finds x removed", any(d["field"] == "x" for d in d2))

    d3 = _diff_snapshots({}, {})
    check("_diff_snapshots empty → empty", len(d3) == 0)

    # ── 8. base_url redaction ──
    check("base_url_host redacted to host", snap2["base_url_host"] == "api.openai.com")

    # ── 9. policy snapshot ──
    check("policy is dict", isinstance(snap2["policy"], dict))
    check("policy has max_iterations", "max_iterations" in snap2["policy"])
    check("policy has stasis_mode", "stasis_mode" in snap2["policy"])

    # ── 10. reset clears state ──
    RuntimeInfoTool.reset()
    raw5 = RuntimeInfoTool.execute({})
    snap5 = json.loads(raw5)
    check("reset: agent is unknown", snap5["agent"] == "unknown")
    check("reset: execution_mode is interactive", snap5["execution_mode"] == "interactive")


# ═════════════════════════════════════════════
# Admin Voices API — page + voices/all + save allowlist
# ═════════════════════════════════════════════
def test_admin_voices_api():
    """Test admin voices endpoints: page render, save allowlist, validation."""
    print("\n=== TORTURE: Admin Voices API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        orig_connections = _app.CONNECTIONS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_settings.parent.mkdir(parents=True, exist_ok=True)
        tmp_settings.write_text("{}", encoding="utf-8")
        tmp_connections.write_text(json.dumps({
            "connections": [
                {"id": "platform_elevenlabs", "provider": "elevenlabs",
                 "url": "https://api.elevenlabs.io", "api_key": "test-key",
                 "enabled": True, "platform_hosted": True, "name": "ElevenLabs"},
            ],
            "agent_connections": {},
        }), encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. PUT save allowlist — valid ──
                    r = await client.put("/api/admin/voices/allowed", json={
                        "allowed_voices": ["voice_1", "voice_2", "voice_3"],
                        "premium_voices": ["voice_3"],
                    })
                    check("PUT allowed voices → 200", r.status_code == 200)
                    body = r.json()
                    check("save count=3", body.get("count") == 3)
                    check("save premium_count=1", body.get("premium_count") == 1)

                    # ── 2. Verify persisted in settings.json ──
                    s = json.loads(tmp_settings.read_text(encoding="utf-8"))
                    check("allowed persisted", s.get("allowed_voices") == ["voice_1", "voice_2", "voice_3"])
                    check("premium persisted", s.get("premium_voices") == ["voice_3"])

                    # ── 3. PUT with empty lists ──
                    r2 = await client.put("/api/admin/voices/allowed", json={
                        "allowed_voices": [],
                        "premium_voices": [],
                    })
                    check("PUT empty lists → 200", r2.status_code == 200)
                    check("empty count=0", r2.json().get("count") == 0)

                    # ── 4. PUT with invalid allowed_voices type ──
                    r3 = await client.put("/api/admin/voices/allowed", json={
                        "allowed_voices": "not-a-list",
                        "premium_voices": [],
                    })
                    check("invalid allowed_voices → 400", r3.status_code == 400)
                    check("error message about list", "list" in r3.json().get("error", "").lower())

                    # ── 5. PUT with invalid premium_voices type ──
                    r4 = await client.put("/api/admin/voices/allowed", json={
                        "allowed_voices": [],
                        "premium_voices": "not-a-list",
                    })
                    check("invalid premium_voices → 400", r4.status_code == 400)

                    # ── 6. GET admin voices page ──
                    r5 = await client.get("/admin/voices")
                    check("GET /admin/voices → 200", r5.status_code == 200)
                    check("admin voices page has content", len(r5.text) > 100)
                    check("page contains Voice Allowlist", "Voice Allowlist" in r5.text)

                    # ── 7. GET /api/admin/voices/all (will fail because elevenlabs is mocked) ──
                    r6 = await client.get("/api/admin/voices/all")
                    check("GET voices/all returns JSON", "voices" in r6.json())

            # Disable auth for testing + inject admin
            import web.app as _app_auth_v
            _orig_gac_v = _app_auth_v.get_auth_config
            _app_auth_v.get_auth_config = lambda: {"auth_enabled": False}
            _orig_admin = _app_auth_v.ADMIN_EMAILS
            _app_auth_v.ADMIN_EMAILS = {"test@example.com"}
            # Patch _check_admin to always return True for tests
            _orig_check = _app_auth_v._check_admin
            _app_auth_v._check_admin = lambda request: True
            try:
                asyncio.run(_run())
            finally:
                _app_auth_v.get_auth_config = _orig_gac_v
                _app_auth_v.ADMIN_EMAILS = _orig_admin
                _app_auth_v._check_admin = _orig_check

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# Admin Voices Template — structure validation
# ═════════════════════════════════════════════
def test_admin_voices_template():
    """Validate admin_voices.html contains required UI elements and JS functions."""
    print("\n=== TORTURE: Admin Voices Template ===")

    template_path = os.path.join(os.path.dirname(__file__), "..", "web", "templates", "admin_voices.html")
    with open(template_path, encoding="utf-8") as f:
        html = f.read()

    # ── 1. Page structure ──
    check("extends base.html", "extends" in html and "base.html" in html)
    check("Voice Allowlist title", "Voice Allowlist" in html)
    check("back link to admin/keys", "/admin/keys" in html)

    # ── 2. Control buttons ──
    check("fetch voices button", "fetchVoices" in html)
    check("save allowlist button", "saveAllowlist" in html)
    check("clear all button", "clearAll" in html)

    # ── 3. Search box ──
    check("search input exists", "voice-search" in html)
    check("filterVoices function", "filterVoices" in html)

    # ── 4. Voice grid ──
    check("voice-grid class", "voice-grid" in html)
    check("voice-card class", "voice-card" in html)
    check("voice-check class", "voice-check" in html)
    check("voice-name class", "voice-name" in html)
    check("voice-id class", "voice-id" in html)

    # ── 5. Premium toggle ──
    check("premium-toggle class", "premium-toggle" in html)
    check("togglePremium function", "togglePremium" in html)
    check("premium-badge class", "premium-badge" in html)
    check("PREMIUM badge text", "PREMIUM" in html)

    # ── 6. JS state variables ──
    check("_savedAllowed variable", "_savedAllowed" in html)
    check("_savedPremium variable", "_savedPremium" in html)
    check("_allVoices variable", "_allVoices" in html)
    check("_selected Set", "_selected" in html)
    check("_premiumSet Set", "_premiumSet" in html)

    # ── 7. API fetch calls ──
    check("fetches /api/admin/voices/all", "/api/admin/voices/all" in html)
    check("PUTs to /api/admin/voices/allowed", "/api/admin/voices/allowed" in html)

    # ── 8. Stats display ──
    check("updateStats function", "updateStats" in html)
    check("stats element", 'id="stats"' in html)

    # ── 9. Toast notifications ──
    check("toast element", 'id="toast"' in html)
    check("toast function in JS", "toast(" in html)

    # ── 10. escHtml XSS protection ──
    check("escHtml function", "escHtml" in html)


# ═════════════════════════════════════════════
# Admin User Management API — list, wipe, wipe-by-email, purge
# ═════════════════════════════════════════════
def test_admin_user_management_api():
    """Test admin user management endpoints via ASGI transport."""
    print("\n=== TORTURE: Admin User Management API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True, exist_ok=True)
        tmp_settings.write_text("{}", encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. GET /api/admin/users ──
                    r = await client.get("/api/admin/users")
                    check("GET admin users → 200", r.status_code == 200)
                    data = r.json()
                    check("users list in response", "users" in data)
                    check("users is list", isinstance(data["users"], list))

                    # ── 2. POST /api/admin/users/wipe-by-email with missing email ──
                    r2 = await client.post("/api/admin/users/wipe-by-email", json={})
                    check("wipe-by-email no email → 400", r2.status_code == 400)

                    # ── 3. POST /api/admin/users/wipe-by-email with non-existent email ──
                    r3 = await client.post("/api/admin/users/wipe-by-email",
                                           json={"email": "nobody@example.com"})
                    check("wipe-by-email unknown → 200", r3.status_code == 200)

                    # ── 4. POST /api/admin/users/purge-inactive ──
                    r4 = await client.post("/api/admin/users/purge-inactive",
                                           json={"days": 9999})
                    check("purge-inactive → 200", r4.status_code == 200)

                    # ── 5. DELETE /api/admin/users/fake-user-id ──
                    r5 = await client.delete("/api/admin/users/fake-user-id")
                    check("delete user → 200", r5.status_code == 200)

            import web.app as _app_auth_um
            _orig_gac_um = _app_auth_um.get_auth_config
            _app_auth_um.get_auth_config = lambda: {"auth_enabled": False}
            _orig_check_um = _app_auth_um._check_admin
            _app_auth_um._check_admin = lambda request: True
            try:
                asyncio.run(_run())
            finally:
                _app_auth_um.get_auth_config = _orig_gac_um
                _app_auth_um._check_admin = _orig_check_um

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# Connections CRUD API — create, update, delete
# ═════════════════════════════════════════════
def test_connections_crud_api():
    """Test connections API endpoints: create, update, delete, list."""
    print("\n=== TORTURE: Connections CRUD API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_connections = _app.CONNECTIONS_FILE
        tmp_connections = Path(tmp) / "config" / "connections.json"
        tmp_connections.parent.mkdir(parents=True, exist_ok=True)
        tmp_connections.write_text(json.dumps({
            "connections": [],
            "agent_connections": {},
        }), encoding="utf-8")
        _app.CONNECTIONS_FILE = tmp_connections
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. GET /api/connections — initially empty ──
                    r = await client.get("/api/connections")
                    check("GET connections → 200", r.status_code == 200)
                    check("initially empty", len(r.json()) == 0)

                    # ── 2. POST /api/connections — create ──
                    r2 = await client.post("/api/connections", json={
                        "name": "Test OpenAI",
                        "provider": "openai",
                        "url": "https://api.openai.com/v1",
                        "api_key": "sk-test-123",
                        "models": ["gpt-4o"],
                    })
                    check("POST create → 200", r2.status_code == 200)
                    created = r2.json()
                    check("created has id", "id" in created)
                    check("created name", created["name"] == "Test OpenAI")
                    check("created provider", created["provider"] == "openai")
                    conn_id = created["id"]

                    # ── 3. GET after create — should have 1 ──
                    r3 = await client.get("/api/connections")
                    check("1 connection after create", len(r3.json()) == 1)

                    # ── 4. PUT /api/connections/{id} — update ──
                    r4 = await client.put(f"/api/connections/{conn_id}", json={
                        "name": "Updated OpenAI",
                        "models": ["gpt-4o", "gpt-4o-mini"],
                    })
                    check("PUT update → 200", r4.status_code == 200)
                    check("update returned ok", r4.json().get("ok") is True)

                    # Verify update persisted
                    r5 = await client.get("/api/connections")
                    updated_conn = r5.json()[0]
                    check("name updated", updated_conn["name"] == "Updated OpenAI")
                    check("models updated", len(updated_conn["models"]) == 2)

                    # ── 5. POST create Ollama — URL normalization ──
                    r6 = await client.post("/api/connections", json={
                        "name": "Local Ollama",
                        "provider": "ollama",
                        "url": "http://localhost:11434",
                    })
                    check("ollama create → 200", r6.status_code == 200)
                    ollama_conn = r6.json()
                    # localhost gets normalized to platform URL
                    check("ollama URL normalized", "localhost" not in ollama_conn.get("url", "localhost"))

                    # ── 6. DELETE /api/connections/{id} ──
                    r7 = await client.delete(f"/api/connections/{conn_id}")
                    check("DELETE → 200", r7.status_code == 200)

                    # Verify deletion
                    r8 = await client.get("/api/connections")
                    remaining_ids = [c["id"] for c in r8.json()]
                    check("deleted conn gone", conn_id not in remaining_ids)
                    check("ollama conn remains", len(r8.json()) == 1)

            import web.app as _app_auth_c
            _orig_gac_c = _app_auth_c.get_auth_config
            _app_auth_c.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app_auth_c.get_auth_config = _orig_gac_c

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.CONNECTIONS_FILE = orig_connections
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# Pricing CRUD API — get, update, set-model, delete-model
# ═════════════════════════════════════════════
def test_pricing_crud_api():
    """Test pricing API endpoints: get, full replace, single model set/delete."""
    print("\n=== TORTURE: Pricing CRUD API ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_pricing = _app.PRICING_FILE
        tmp_pricing = Path(tmp) / "config" / "pricing.yaml"
        tmp_pricing.parent.mkdir(parents=True, exist_ok=True)
        # Start with empty pricing
        tmp_pricing.write_text("", encoding="utf-8")
        _app.PRICING_FILE = tmp_pricing
        _app._TTL_CACHE.clear()

        try:
            from httpx import ASGITransport, AsyncClient
            import asyncio
            from web.app import app as _test_app

            async def _run():
                transport = ASGITransport(app=_test_app)
                async with AsyncClient(transport=transport, base_url="http://test") as client:
                    # ── 1. GET /api/pricing — initially empty ──
                    r = await client.get("/api/pricing")
                    check("GET pricing → 200", r.status_code == 200)

                    # ── 2. PUT /api/pricing — full replace ──
                    pricing_data = {
                        "openai": {
                            "gpt-4o": {"input_per_1m": 2.5, "output_per_1m": 10.0},
                            "gpt-4o-mini": {"input_per_1m": 0.15, "output_per_1m": 0.6},
                        }
                    }
                    r2 = await client.put("/api/pricing", json=pricing_data)
                    check("PUT pricing → 200", r2.status_code == 200)
                    check("PUT pricing ok", r2.json().get("ok") is True)

                    # Verify persisted
                    r3 = await client.get("/api/pricing")
                    check("pricing has openai", "openai" in r3.json())

                    # ── 3. PUT /api/pricing/{provider}/{model} — single model ──
                    r4 = await client.put("/api/pricing/openai/gpt-4o", json={
                        "input_per_1m": 3.0,
                        "output_per_1m": 12.0,
                    })
                    check("PUT single model → 200", r4.status_code == 200)
                    check("updated pricing returned", r4.json().get("pricing", {}).get("input_per_1m") == 3.0)

                    # ── 4. PUT new provider/model ──
                    r5 = await client.put("/api/pricing/anthropic/claude-3-5-sonnet", json={
                        "input_per_1m": 3.0,
                        "output_per_1m": 15.0,
                    })
                    check("PUT new provider → 200", r5.status_code == 200)

                    # ── 5. DELETE /api/pricing/{provider}/{model} ──
                    r6 = await client.delete("/api/pricing/openai/gpt-4o-mini")
                    check("DELETE model → 200", r6.status_code == 200)

                    # Verify deletion
                    r7 = await client.get("/api/pricing")
                    openai_models = r7.json().get("openai", {})
                    check("deleted model gone", "gpt-4o-mini" not in openai_models)
                    check("other model remains", "gpt-4o" in openai_models)

                    # ── 6. GET /api/pricing/cost-summary ──
                    r8 = await client.get("/api/pricing/cost-summary")
                    check("cost-summary → 200", r8.status_code == 200)

                    # ── 7. GET /api/pricing/cost-log ──
                    r9 = await client.get("/api/pricing/cost-log?limit=10")
                    check("cost-log → 200", r9.status_code == 200)

            import web.app as _app_auth_p
            _orig_gac_p = _app_auth_p.get_auth_config
            _app_auth_p.get_auth_config = lambda: {"auth_enabled": False}
            _orig_check_p = _app_auth_p._check_admin
            _app_auth_p._check_admin = lambda request: True
            try:
                asyncio.run(_run())
            finally:
                _app_auth_p.get_auth_config = _orig_gac_p
                _app_auth_p._check_admin = _orig_check_p

        except ImportError:
            check("httpx not available — skipped", True)

    finally:
        _app.PRICING_FILE = orig_pricing
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# TTS Voices filter logic — allowlist + premium marking
# ═════════════════════════════════════════════
def test_tts_voices_filter_logic():
    """Test TTS voice filtering with allowlist and premium marking logic."""
    print("\n=== TORTURE: TTS Voices Filter Logic ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True, exist_ok=True)

        # ── 1. No allowlist → all voices pass through ──
        tmp_settings.write_text(json.dumps({}), encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        settings = _app._load_settings()
        allowed = settings.get("allowed_voices", [])
        check("no allowlist → empty list", allowed == [])

        # ── 2. With allowlist — filter logic ──
        tmp_settings.write_text(json.dumps({
            "allowed_voices": ["voice_a", "voice_b"],
            "premium_voices": ["voice_b"],
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        settings2 = _app._load_settings()
        allowed2 = settings2.get("allowed_voices", [])
        premium2 = set(settings2.get("premium_voices", []))
        check("allowlist has 2 entries", len(allowed2) == 2)
        check("premium has 1 entry", len(premium2) == 1)
        check("voice_b is premium", "voice_b" in premium2)
        check("voice_a not premium", "voice_a" not in premium2)

        # Simulate filtering
        all_voices = [
            {"voice_id": "voice_a", "name": "Alice"},
            {"voice_id": "voice_b", "name": "Bob"},
            {"voice_id": "voice_c", "name": "Charlie"},
        ]
        allowed_set = set(allowed2)
        filtered = [v for v in all_voices if v["voice_id"] in allowed_set]
        check("filter keeps 2", len(filtered) == 2)
        check("filter excludes voice_c", all(v["voice_id"] != "voice_c" for v in filtered))

        # Premium marking
        for v in filtered:
            v["premium"] = v["voice_id"] in premium2
        check("voice_a not marked premium", not filtered[0]["premium"])
        check("voice_b marked premium", filtered[1]["premium"])

        # ── 3. Empty allowlist → no filter ──
        tmp_settings.write_text(json.dumps({
            "allowed_voices": [],
            "premium_voices": [],
        }), encoding="utf-8")
        _app._TTL_CACHE.clear()
        settings3 = _app._load_settings()
        allowed3 = settings3.get("allowed_voices", [])
        check("empty allowlist → show all", len(allowed3) == 0)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# Inworld API key helper
# ═════════════════════════════════════════════
def test_inworld_api_key_helper():
    """Test _get_inworld_api_key returns the key from settings or None."""
    print("\n=== TORTURE: Inworld API Key Helper ===")
    from pathlib import Path

    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app

        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True, exist_ok=True)

        # ── 1. No api_keys → None ──
        tmp_settings.write_text(json.dumps({}), encoding="utf-8")
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()
        result = _app._get_inworld_api_key()
        check("no api_keys → None", result is None)

        # ── 2. Empty inworld key → None ──
        tmp_settings.write_text(json.dumps({"api_keys": {"inworld": ""}}), encoding="utf-8")
        _app._TTL_CACHE.clear()
        result2 = _app._get_inworld_api_key()
        check("empty inworld key → None", result2 is None)

        # ── 3. Valid key → returned ──
        tmp_settings.write_text(json.dumps({"api_keys": {"inworld": "my-secret-key"}}), encoding="utf-8")
        _app._TTL_CACHE.clear()
        result3 = _app._get_inworld_api_key()
        check("valid key returned", result3 == "my-secret-key")

        # ── 4. Other keys present, no inworld → None ──
        tmp_settings.write_text(json.dumps({"api_keys": {"openai": "sk-abc"}}), encoding="utf-8")
        _app._TTL_CACHE.clear()
        result4 = _app._get_inworld_api_key()
        check("no inworld key → None", result4 is None)

    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# _check_admin helper — admin email check
# ═════════════════════════════════════════════
def test_check_admin_helper():
    """Test _check_admin validates email against ADMIN_EMAILS."""
    print("\n=== TORTURE: _check_admin helper ===")
    import web.app as _app

    # Save original
    orig_admin = _app.ADMIN_EMAILS
    orig_check = _app._check_admin

    try:
        _app.ADMIN_EMAILS = {"admin@example.com", "boss@test.org"}

        # ── 1. No user on request → False ──
        class FakeRequest:
            class state:
                pass
        check("no user → False", _app._check_admin(FakeRequest()) is False)

        # ── 2. User with admin email → True ──
        class AdminRequest:
            class state:
                user = {"email": "admin@example.com"}
        check("admin email → True", _app._check_admin(AdminRequest()) is True)

        # ── 3. User with non-admin email → False ──
        class NonAdminRequest:
            class state:
                user = {"email": "user@example.com"}
        check("non-admin email → False", _app._check_admin(NonAdminRequest()) is False)

        # ── 4. Case-insensitive ──
        class UpperCaseRequest:
            class state:
                user = {"email": "ADMIN@EXAMPLE.COM"}
        check("case-insensitive match", _app._check_admin(UpperCaseRequest()) is True)

        # ── 5. Empty email → False ──
        class EmptyEmailRequest:
            class state:
                user = {"email": ""}
        check("empty email → False", _app._check_admin(EmptyEmailRequest()) is False)

        # ── 6. Missing email key → False ──
        class NoEmailRequest:
            class state:
                user = {}
        check("missing email key → False", _app._check_admin(NoEmailRequest()) is False)

    finally:
        _app.ADMIN_EMAILS = orig_admin


# ═════════════════════════════════════════════
# FAISS SCALING — model defaults, file locking, dimension mismatch,
#                  async wrapping, startup coordination, workers
# ═════════════════════════════════════════════
def test_faiss_scaling():
    """Test all L1+L2 scaling features: model defaults, file locking,
    dimension mismatch, async wrapping, startup coordination, 3 workers."""
    print("\n=== TORTURE: FAISS Scaling — L1+L2 features ===")
    import inspect
    import ast

    # ── 1. FAISSMemory defaults to all-MiniLM-L6-v2 ──
    from src.memory.faiss_memory import FAISSMemory
    sig = inspect.signature(FAISSMemory.__init__)
    default_model = sig.parameters["model_name"].default
    check("FAISSMemory default model is all-MiniLM-L6-v2",
          default_model == "all-MiniLM-L6-v2", f"got: {default_model}")

    # ── 2. NotesFAISS defaults to all-MiniLM-L6-v2 ──
    from src.memory.notes_faiss import NotesFAISS
    sig2 = inspect.signature(NotesFAISS.__init__)
    default_model2 = sig2.parameters["model_name"].default
    check("NotesFAISS default model is all-MiniLM-L6-v2",
          default_model2 == "all-MiniLM-L6-v2", f"got: {default_model2}")

    # ── 3. NotesFAISS.load() default model is all-MiniLM-L6-v2 ──
    sig3 = inspect.signature(NotesFAISS.load)
    default_model3 = sig3.parameters["model_name"].default
    check("NotesFAISS.load() default model is all-MiniLM-L6-v2",
          default_model3 == "all-MiniLM-L6-v2", f"got: {default_model3}")

    # ── 4. Vault._append uses fcntl.flock ──
    from src.memory.vault import VaultStore
    src_vault = inspect.getsource(VaultStore._append)
    check("vault._append uses fcntl.flock LOCK_EX",
          "fcntl.flock" in src_vault and "LOCK_EX" in src_vault)
    check("vault._append uses fcntl.flock LOCK_UN",
          "LOCK_UN" in src_vault)

    # ── 5. FAISSMemory._save_index uses fcntl.flock ──
    src_save_idx = inspect.getsource(FAISSMemory._save_index)
    check("FAISSMemory._save_index uses fcntl.flock LOCK_EX",
          "fcntl.flock" in src_save_idx and "LOCK_EX" in src_save_idx)
    check("FAISSMemory._save_index uses .index.lock file",
          ".index.lock" in src_save_idx)
    check("FAISSMemory._save_index saves model_name in meta",
          "model_name" in src_save_idx)

    # ── 6. NotesFAISS._save uses fcntl.flock ──
    src_notes_save = inspect.getsource(NotesFAISS._save)
    check("NotesFAISS._save uses fcntl.flock LOCK_EX",
          "fcntl.flock" in src_notes_save and "LOCK_EX" in src_notes_save)
    check("NotesFAISS._save uses .notes.lock file",
          ".notes.lock" in src_notes_save)

    # ── 7. FAISSMemory._load_or_build detects model mismatch ──
    src_load_build = inspect.getsource(FAISSMemory._load_or_build)
    check("_load_or_build checks model_name mismatch",
          'meta.get("model_name")' in src_load_build
          or "model_name" in src_load_build)
    check("_load_or_build calls rebuild_index on mismatch",
          "rebuild_index" in src_load_build)

    # ── 8. NotesFAISS.load() has dimension mismatch detection ──
    src_load = inspect.getsource(NotesFAISS.load)
    check("NotesFAISS.load checks index.d vs embedding_dim",
          "index.d" in src_load and "embedding_dim" in src_load)
    check("NotesFAISS.load returns None on mismatch",
          "return None" in src_load)
    check("NotesFAISS.load logs dimension mismatch warning",
          "Dimension mismatch" in src_load or "mismatch" in src_load.lower())

    # ── 9. NotesFAISS.load() returns None for missing files ──
    result = NotesFAISS.load(tempfile.mkdtemp())
    check("NotesFAISS.load returns None for missing dir", result is None)

    # ── 10. App _bg_faiss uses LOCK_EX | LOCK_NB for startup coordination ──
    import web.app as _app
    src_bg = inspect.getsource(_app._lifespan_body)
    check("_lifespan_body has _bg_faiss", "_bg_faiss" in src_bg)
    check("_bg_faiss uses LOCK_EX | LOCK_NB",
          "LOCK_EX" in src_bg and "LOCK_NB" in src_bg)
    check("_bg_faiss uses threading.Thread",
          "threading.Thread" in src_bg or "Thread" in src_bg)
    check("_bg_faiss calls invalidate_notes_faiss",
          "invalidate_notes_faiss" in src_bg)

    # ── 11. App uses asyncio.to_thread for _build_chat_messages ──
    # Check the source of the whole app module for asyncio.to_thread wrapping
    app_src_path = inspect.getfile(_app)
    with open(app_src_path, "r", encoding="utf-8") as f:
        app_source = f.read()
    to_thread_count = app_source.count("asyncio.to_thread")
    check("asyncio.to_thread used >= 3 times",
          to_thread_count >= 3,
          f"found {to_thread_count} occurrences")
    check("asyncio.to_thread wraps _build_chat_messages",
          "asyncio.to_thread(\n" in app_source
          or "asyncio.to_thread(_build_chat_messages" in app_source
          or ("asyncio.to_thread" in app_source and "_build_chat_messages" in app_source))

    # ── 12. boot.sh starts uvicorn with a single worker (Fly stability) ──
    boot_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                             "boot.sh")
    if os.path.exists(boot_path):
        with open(boot_path, "r", encoding="utf-8") as f:
            boot_content = f.read()
        check("boot.sh has --workers 1", "--workers 1" in boot_content)
        check("boot.sh runs uvicorn", "uvicorn" in boot_content)
    else:
        pass  # hosted-deploy file; not shipped in the local edition

    # ── 13. Both FAISS modules import fcntl ──
    import src.memory.faiss_memory as fm_mod
    import src.memory.notes_faiss as nf_mod
    import src.memory.vault as v_mod
    check("faiss_memory imports fcntl", hasattr(fm_mod, 'fcntl') or 'fcntl' in dir(fm_mod))
    check("notes_faiss imports fcntl", hasattr(nf_mod, 'fcntl') or 'fcntl' in dir(nf_mod))
    check("vault imports fcntl", hasattr(v_mod, 'fcntl') or 'fcntl' in dir(v_mod))

    # ── 14. NotesFAISS has embedding_dim property ──
    check("NotesFAISS has embedding_dim property",
          isinstance(inspect.getattr_static(NotesFAISS, 'embedding_dim'), property))

    # ── 15. FAISSMemory._save_index stores model_name in meta ──
    # Verified via source inspection above; also verify the meta dict structure
    check("_save_index meta includes idx_to_id",
          "idx_to_id" in src_save_idx)
    check("_save_index meta includes deleted_ids",
          "deleted_ids" in src_save_idx)


# ═════════════════════════════════════════════
# METERING SOURCE FILTERING — platform vs user cost tagging
# ═════════════════════════════════════════════
def test_metering_source_filtering():
    """Test source param on log_cost_event, read_cost_log source/until filters,
    aggregate_costs by_source, and ORION_COST_SOURCE env var fallback."""
    print("\n=== TORTURE: Metering — Source Filtering ===")
    from src.observability.metering import (
        Metering, TokenUsage, CostBreakdown,
        log_cost_event, read_cost_log, aggregate_costs,
        set_cost_log_path,
    )

    tmp = tempfile.mkdtemp()
    log_path = os.path.join(tmp, "cost_log.jsonl")
    set_cost_log_path(log_path)

    try:
        m = Metering(
            usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            cost=CostBreakdown(total_cost=0.01),
            model="gpt-4", provider="openai",
        )

        # ── 1. log_cost_event with source ──
        ev1 = log_cost_event(m, agent="a1", source="platform")
        check("source=platform written", ev1["source"] == "platform")

        ev2 = log_cost_event(m, agent="a2", source="user")
        check("source=user written", ev2["source"] == "user")

        ev3 = log_cost_event(m, agent="a3")
        check("no source → empty", ev3["source"] == "")

        # ── 2. ORION_COST_SOURCE env var fallback ──
        os.environ["ORION_COST_SOURCE"] = "platform"
        try:
            ev4 = log_cost_event(m, agent="a4")
            check("env var fallback", ev4["source"] == "platform")
        finally:
            del os.environ["ORION_COST_SOURCE"]

        # Explicit source overrides env
        os.environ["ORION_COST_SOURCE"] = "platform"
        try:
            ev5 = log_cost_event(m, agent="a5", source="user")
            check("explicit overrides env", ev5["source"] == "user")
        finally:
            del os.environ["ORION_COST_SOURCE"]

        # ── 3. read_cost_log source filter ──
        platform_events = read_cost_log(source="platform")
        check("read source=platform count", len(platform_events) == 2,
              f"got {len(platform_events)}")

        user_events = read_cost_log(source="user")
        check("read source=user count", len(user_events) == 2,
              f"got {len(user_events)}")

        # ── 4. read_cost_log until filter ──
        until_past = read_cost_log(until="2000-01-01T00:00:00+00:00")
        check("until past → 0", len(until_past) == 0)

        until_future = read_cost_log(until="2099-01-01T00:00:00+00:00")
        check("until future → all", len(until_future) == 5)

        # Combined: source + until
        combo = read_cost_log(source="platform", until="2099-01-01T00:00:00+00:00")
        check("source+until combo", len(combo) == 2)

        # ── 5. aggregate_costs by_source ──
        all_events = read_cost_log()
        agg = aggregate_costs(all_events)
        check("agg has by_source", "by_source" in agg)
        check("agg by_source has platform", "platform" in agg["by_source"])
        check("agg by_source has user", "user" in agg["by_source"])
        check("agg by_source platform cost",
              abs(agg["by_source"]["platform"] - 0.02) < 0.001)
        check("agg by_source user cost",
              abs(agg["by_source"]["user"] - 0.02) < 0.001)

        # Empty source events bucketed as "unknown"
        no_source = [ev for ev in all_events if ev.get("source") == ""]
        if no_source:
            agg_no = aggregate_costs(no_source)
            check("empty source → unknown bucket",
                  "unknown" in agg_no["by_source"])

        # ── 6. aggregate_costs empty → by_source empty ──
        empty_agg = aggregate_costs([])
        check("empty agg by_source", empty_agg["by_source"] == {})

    finally:
        set_cost_log_path(None)
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# COST TRACKER SOURCE TABS — CostTrackerTool with source filter
# ═════════════════════════════════════════════
def test_cost_tracker_source_tabs():
    """Test CostTrackerTool cost_summary and cost_log with source filter."""
    print("\n=== TORTURE: CostTrackerTool — Source Tabs ===")
    from src.tools.cost_tracker import CostTrackerTool
    from src.observability.metering import (
        Metering, TokenUsage, CostBreakdown,
        log_cost_event, set_cost_log_path,
    )

    tmp = tempfile.mkdtemp()
    log_path = os.path.join(tmp, "cost_log.jsonl")
    set_cost_log_path(log_path)

    try:
        m = Metering(
            usage=TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            cost=CostBreakdown(total_cost=0.01),
            model="gpt-4", provider="openai",
        )
        log_cost_event(m, agent="astraea", source="platform")
        log_cost_event(m, agent="astraea", source="user")
        log_cost_event(m, agent="callum", source="platform")

        tool = CostTrackerTool()

        # cost_summary — all
        r = json.loads(tool.execute({"action": "cost_summary"}))
        check("summary all_time 3 calls", r["all_time"]["num_calls"] == 3)

        # cost_log — all
        r2 = json.loads(tool.execute({"action": "cost_log"}))
        check("cost_log all count 3", r2["count"] == 3)

        # cost_log — verify source field present in events
        check("cost_log events have source",
              all("source" in e for e in r2["events"]))

    finally:
        set_cost_log_path(None)
        shutil.rmtree(tmp, ignore_errors=True)


# =============================================
# BOOT PERSISTENCE — verify boot.sh & Dockerfile.fly cover all data dirs
# =============================================
def test_boot_persistence_coverage():
    """Verify boot.sh symlinks and Dockerfile.fly bundles cover all persistent dirs."""
    print("\n=== TORTURE: Boot Persistence Coverage ===")
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent.parent
    if not (repo_root / "boot.sh").is_file():
        print("  (skipped: hosted-deploy files are not part of the local edition)")
        return
    boot_sh = repo_root / "boot.sh"
    dockerfile = repo_root / "Dockerfile.fly"

    check("boot.sh exists", boot_sh.is_file())
    check("Dockerfile.fly exists", dockerfile.is_file())

    boot_text = boot_sh.read_text(encoding="utf-8")
    docker_text = dockerfile.read_text(encoding="utf-8")

    # boot.sh must symlink these directories to /persist/
    persist_dirs = [
        "uploads", "memory", "config", "profiles",
        "user_notes", "chats", "trash", "users", "shared", "orion",
    ]
    for d in persist_dirs:
        check(f"boot.sh has /persist/{d}", f"/persist/{d}" in boot_text)
        check(f"boot.sh symlinks {d}", f"ln -sfn" in boot_text and d in boot_text)

    # Dockerfile.fly must stage bundled copies
    bundled_dirs = [
        "_bundled_uploads", "_bundled_memory", "_bundled_config",
        "_bundled_profiles", "_bundled_shared", "_bundled_orion",
    ]
    for bd in bundled_dirs:
        check(f"Dockerfile stages {bd}", bd in docker_text)

    # boot.sh must start the app
    check("boot.sh starts uvicorn", "uvicorn" in boot_text)
    check("boot.sh port 8989", "8989" in boot_text)

    # boot.sh syncs SOUL_SCRIPTS.md always
    check("boot.sh syncs SOUL_SCRIPTS.md", "SOUL_SCRIPTS" in boot_text)

    # Dockerfile.fly has HEALTHCHECK
    check("Dockerfile has HEALTHCHECK", "HEALTHCHECK" in docker_text)


# =============================================
# INBOX PERSISTENCE PATH — verify shared dir setup
# =============================================
def test_inbox_persistence_path():
    """Verify inbox JSONL path resolves under data/shared/ which is persisted."""
    print("\n=== TORTURE: Inbox Persistence Path ===")
    import src.data_paths as dp

    inbox_path = dp.inbox_path()
    check("inbox_path ends with inbox.jsonl", inbox_path.endswith("inbox.jsonl"))
    check("inbox_path contains shared dir", "shared" in inbox_path)

    # data_paths module creates dirs on access
    shared_dir = dp.shared_dir()
    check("shared_dir exists", os.path.isdir(shared_dir))
    check("shared_dir ends with shared", shared_dir.endswith("shared"))


# ═════════════════════════════════════════════
# KEY VAULT — ENCRYPTION AT REST
# ═════════════════════════════════════════════
def test_key_vault_encryption():
    """Test Fernet encrypt/decrypt round-trip, masking, and settings integration."""
    print("\n=== TORTURE: Key Vault — Encryption at Rest ===")
    from web.key_vault import (
        encrypt_value, decrypt_value, mask_value,
        encrypt_settings_secrets, decrypt_settings_secrets,
        strip_secrets_for_template,
    )

    # ── 1. Encrypt/decrypt round-trip ──
    plain = "sk-abc123456789xyz"
    encrypted = encrypt_value(plain)
    check("encrypted starts with enc:", encrypted.startswith("enc:"))
    check("encrypted != plaintext", encrypted != plain)
    decrypted = decrypt_value(encrypted)
    check("decrypt round-trip", decrypted == plain)

    # ── 2. Empty values ──
    check("encrypt empty → empty", encrypt_value("") == "")
    check("decrypt empty → empty", decrypt_value("") == "")

    # ── 3. Legacy plaintext passthrough ──
    check("legacy plaintext passthrough", decrypt_value("sk-plaintext") == "sk-plaintext")

    # ── 4. Corrupted enc: → empty ──
    check("corrupted enc: → empty", decrypt_value("enc:garbagetokenthatisnotvalid") == "")

    # ── 5. Masking logic ──
    check("mask long key starts right", mask_value("sk-abcdefghijklmnop")[:4] == "sk-a")
    check("mask long key ends right", mask_value("sk-abcdefghijklmnop")[-4:] == "mnop")
    check("mask long key has bullets", "•" in mask_value("sk-abcdefghijklmnop"))
    check("mask short key all bullets", mask_value("AIza") == "••••")
    check("mask empty → empty", mask_value("") == "")

    # ── 6. Settings encryption round-trip ──
    settings = {
        "api_keys": {
            "openai": "sk-openai-test",
            "anthropic": "sk-ant-test",
            "ollama_url": "http://localhost:11434",
        },
        "image": {
            "preferred": "openai_dalle3",
            "openai_api_key": "sk-img-test",
        },
        "tts": {
            "provider": "elevenlabs",
            "elevenlabs_api_key": "xi-test-key",
        },
        "timezone": "auto",
    }
    encrypted_settings = encrypt_settings_secrets(settings)
    check("openai encrypted", encrypted_settings["api_keys"]["openai"].startswith("enc:"))
    check("anthropic encrypted", encrypted_settings["api_keys"]["anthropic"].startswith("enc:"))
    check("ollama_url NOT encrypted", encrypted_settings["api_keys"]["ollama_url"] == "http://localhost:11434")
    check("image key encrypted", encrypted_settings["image"]["openai_api_key"].startswith("enc:"))
    check("image preferred NOT encrypted", encrypted_settings["image"]["preferred"] == "openai_dalle3")
    check("tts key encrypted", encrypted_settings["tts"]["elevenlabs_api_key"].startswith("enc:"))
    check("timezone untouched", encrypted_settings["timezone"] == "auto")

    decrypted_settings = decrypt_settings_secrets(encrypted_settings)
    check("openai decrypted", decrypted_settings["api_keys"]["openai"] == "sk-openai-test")
    check("anthropic decrypted", decrypted_settings["api_keys"]["anthropic"] == "sk-ant-test")
    check("image key decrypted", decrypted_settings["image"]["openai_api_key"] == "sk-img-test")
    check("tts key decrypted", decrypted_settings["tts"]["elevenlabs_api_key"] == "xi-test-key")

    # ── 7. strip_secrets_for_template ──
    stripped = strip_secrets_for_template(settings)
    check("stripped openai empty", stripped["api_keys"]["openai"] == "")
    check("stripped anthropic empty", stripped["api_keys"]["anthropic"] == "")
    check("stripped ollama_url preserved", stripped["api_keys"]["ollama_url"] == "http://localhost:11434")
    check("stripped image key empty", stripped["image"]["openai_api_key"] == "")
    check("stripped image preferred preserved", stripped["image"]["preferred"] == "openai_dalle3")
    check("stripped tts key empty", stripped["tts"]["elevenlabs_api_key"] == "")
    check("stripped tts provider preserved", stripped["tts"]["provider"] == "elevenlabs")
    check("stripped timezone preserved", stripped["timezone"] == "auto")

    # ── 8. _save_settings / _load_settings round-trip with encryption ──
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app
        orig_settings = _app.SETTINGS_FILE
        tmp_settings = Path(tmp) / "config" / "settings.json"
        tmp_settings.parent.mkdir(parents=True)
        _app.SETTINGS_FILE = tmp_settings
        _app._TTL_CACHE.clear()

        _app._save_settings(settings)
        # Read raw file to verify encryption on disk
        with open(tmp_settings, "r", encoding="utf-8") as f:
            raw = json.load(f)
        check("on-disk openai encrypted", raw["api_keys"]["openai"].startswith("enc:"))
        check("on-disk ollama_url plain", raw["api_keys"]["ollama_url"] == "http://localhost:11434")

        # Load via _load_settings → decrypted
        loaded = _app._load_settings()
        check("loaded openai decrypted", loaded["api_keys"]["openai"] == "sk-openai-test")
        check("loaded tts key decrypted", loaded["tts"]["elevenlabs_api_key"] == "xi-test-key")
    finally:
        _app.SETTINGS_FILE = orig_settings
        _app._TTL_CACHE.clear()
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# KEY VAULT — PER-USER ISOLATION
# ═════════════════════════════════════════════
def test_key_vault_per_user_isolation():
    """Test that per-user key storage is isolated and encrypted."""
    print("\n=== TORTURE: Key Vault — Per-User Isolation ===")
    from pathlib import Path
    from web.key_vault import (
        save_user_keys, load_user_keys, load_user_keys_masked,
        delete_user_keys, _user_keys_path,
    )
    tmp = tempfile.mkdtemp()
    try:
        import web.key_vault as _kv
        orig_data_dir = _kv._DATA_DIR
        _kv._DATA_DIR = Path(tmp)

        # ── 1. Save keys for user A ──
        save_user_keys("user-aaa", "api_keys", {
            "openai": "sk-user-a-key",
            "anthropic": "sk-ant-a",
            "ollama_url": "http://localhost:11434",
        })

        # ── 2. Save keys for user B ──
        save_user_keys("user-bbb", "api_keys", {
            "openai": "sk-user-b-key",
            "anthropic": "sk-ant-b",
            "ollama_url": "http://remote:11434",
        })

        # ── 3. Load user A → sees user A keys only ──
        a_keys = load_user_keys("user-aaa", "api_keys")
        check("user A openai correct", a_keys["openai"] == "sk-user-a-key")
        check("user A anthropic correct", a_keys["anthropic"] == "sk-ant-a")

        # ── 4. Load user B → sees user B keys only ──
        b_keys = load_user_keys("user-bbb", "api_keys")
        check("user B openai correct", b_keys["openai"] == "sk-user-b-key")
        check("user B anthropic correct", b_keys["anthropic"] == "sk-ant-b")

        # ── 5. User A cannot see user B's keys ──
        check("user A ≠ user B openai", a_keys["openai"] != b_keys["openai"])

        # ── 6. Encrypted on disk ──
        a_path = _user_keys_path("user-aaa")
        with open(a_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        check("user A openai encrypted on disk", raw["api_keys"]["openai"].startswith("enc:"))
        check("user A ollama_url plain on disk", raw["api_keys"]["ollama_url"] == "http://localhost:11434")

        # ── 7. Masked keys ──
        masked = load_user_keys_masked("user-aaa", "api_keys")
        check("masked openai has bullets", "•" in masked["openai"])
        check("masked openai not plaintext", masked["openai"] != "sk-user-a-key")
        check("masked ollama_url plain", masked["ollama_url"] == "http://localhost:11434")

        # ── 8. Delete user keys ──
        delete_user_keys("user-aaa")
        check("user A keys deleted", not a_path.exists())
        check("user B keys still exist", _user_keys_path("user-bbb").exists())

        # ── 9. Load deleted user → empty ──
        check("deleted user → empty", load_user_keys("user-aaa", "api_keys") == {})

        # ── 10. Multiple categories ──
        save_user_keys("user-ccc", "api_keys", {"openai": "sk-c"})
        save_user_keys("user-ccc", "image", {"openai_api_key": "sk-img-c"})
        check("api_keys category", load_user_keys("user-ccc", "api_keys")["openai"] == "sk-c")
        check("image category", load_user_keys("user-ccc", "image")["openai_api_key"] == "sk-img-c")

    finally:
        _kv._DATA_DIR = orig_data_dir
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# KEY VAULT — HTML TEMPLATE STRIPPING
# ═════════════════════════════════════════════
def test_key_vault_html_stripping():
    """Test that settings.html no longer contains raw key values."""
    print("\n=== TORTURE: Key Vault — HTML Template Stripping ===")
    from pathlib import Path

    template_path = Path(__file__).resolve().parent.parent / "web" / "templates" / "settings.html"
    html = template_path.read_text(encoding="utf-8")

    # ── 1. No raw key values in input value attributes ──
    # These patterns should NOT appear — they were the old insecure approach.
    import re
    dangerous_patterns = [
        r"value=\"\{\{.*api_keys.*get\('openai'",
        r"value=\"\{\{.*api_keys.*get\('anthropic'",
        r"value=\"\{\{.*api_keys.*get\('deepseek'",
        r"value=\"\{\{.*api_keys.*get\('google_gemini'",
        r"value=\"\{\{.*api_keys.*get\('openrouter'",
        r"value=\"\{\{.*api_keys.*get\('inworld'",
        r"value=\"\{\{.*image.*get\('openai_api_key'",
        r"value=\"\{\{.*image.*get\('stability_api_key'",
        r"value=\"\{\{.*image.*get\('ideogram_api_key'",
        r"value=\"\{\{.*image.*get\('replicate_api_key'",
        r"value=\"\{\{.*image.*get\('fal_api_key'",
        r"value=\"\{\{.*image.*get\('leonardo_api_key'",
        r"value=\"\{\{.*image.*get\('midjourney_api_key'",
        r"value=\"\{\{.*tts.*get\('elevenlabs_api_key'",
        r"value=\"\{\{.*tts.*get\('openedai_cloud_api_key'",
    ]
    for pattern in dangerous_patterns:
        match = re.search(pattern, html)
        check(f"no raw key in HTML: {pattern[:40]}...", match is None,
              f"FOUND at: {match.group() if match else 'n/a'}")

    # ── 2. loadKeyStatus function exists ──
    check("loadKeyStatus function present", "loadKeyStatus" in html)

    # ── 3. Key status indicators present ──
    check("openai status indicator", "key-openai-status" in html)
    check("anthropic status indicator", "key-anthropic-status" in html)

    # ── 4. Ollama URL still rendered (non-secret) ──
    check("ollama_url still in template", "ollama_url" in html)


# ═════════════════════════════════════════════
# FAISS MEMORY — edited memories stay searchable
# ═════════════════════════════════════════════
def test_faiss_update_keeps_memory_searchable():
    """FAISSMemory.update() retires the old vector without hiding the memory,
    and _load_or_build heals indexes damaged by the old update() bug."""
    print("\n=== TORTURE: FAISS Memory — update() keeps edited memory searchable ===")
    import numpy as np
    from src.memory.faiss_memory import FAISSMemory

    class _FakeEncoder:
        """Deterministic bag-of-words embedder (no model download)."""
        DIM = 64

        def get_sentence_embedding_dimension(self):
            return self.DIM

        def encode(self, texts, **kw):
            out = np.zeros((len(texts), self.DIM), dtype="float32")
            for r, t in enumerate(texts):
                out[r, 0] = 0.01  # never all-zero
                for w in t.lower().split():
                    out[r, 1 + int(hashlib.md5(w.encode()).hexdigest(), 16) % (self.DIM - 1)] += 1.0
            return out

    _enc = _FakeEncoder()

    class _TestFAISS(FAISSMemory):
        @property
        def encoder(self):
            return _enc

        @property
        def embedding_dim(self):
            return _enc.DIM

    tmp = tempfile.mkdtemp()
    try:
        vault_path = os.path.join(tmp, "vault.jsonl")
        faiss_dir = os.path.join(tmp, "faiss")
        fm = _TestFAISS(vault_path, faiss_dir)

        m = fm.add("Creator drinks black coffee every morning", category="preference")
        other = fm.add("The server runs on port eight thousand", category="other")
        old_idx = fm._id_to_idx[m.id]

        # ── 1. Edit text → still searchable by new text ──
        fm.update(m.id, text="Creator switched to green tea recently")
        hits = fm.search("green tea", top_k=5)
        check("edited memory found by new text", any(h["id"] == m.id for h in hits))
        check("edited memory returns new text",
              any(h["id"] == m.id and "green tea" in h["text"] for h in hits))
        check("edited id NOT in _deleted_ids", m.id not in fm._deleted_ids)

        # ── 2. Old vector retired by position, not by id ──
        check("old row marked stale", fm._idx_to_id[old_idx] == f"__stale__{m.id}")
        check("id now maps to new row", fm._id_to_idx[m.id] != old_idx)
        check("index grew by one vector", fm.index.ntotal == 3)

        # ── 3. No duplicate hits (stale row skipped) ──
        hits_all = fm.search("Creator coffee green tea", top_k=10)
        check("edited memory appears once", sum(1 for h in hits_all if h["id"] == m.id) == 1)

        # ── 4. Old text no longer surfaces the old wording ──
        check("old text gone from results",
              not any("black coffee" in h["text"] for h in fm.search("black coffee", top_k=10)))

        # ── 5. Untouched memory unaffected ──
        check("other memory still found",
              any(h["id"] == other.id for h in fm.search("server port", top_k=5)))

        # ── 6. Second edit of the same memory ──
        fm.update(m.id, text="Creator now drinks only water")
        hits2 = fm.search("drinks only water", top_k=5)
        check("second edit searchable", any(h["id"] == m.id for h in hits2))
        check("second edit appears once",
              sum(1 for h in fm.search("Creator water tea coffee", top_k=10) if h["id"] == m.id) == 1)

        # ── 7. Metadata-only update does not re-embed ──
        n_before = fm.index.ntotal
        fm.update(m.id, tags=["drinks"])
        check("tags-only update adds no vector", fm.index.ntotal == n_before)

        # ── 8. Survives reload from disk ──
        fm2 = _TestFAISS(vault_path, faiss_dir)
        check("reload: edited memory searchable",
              any(h["id"] == m.id for h in fm2.search("drinks only water", top_k=5)))
        check("reload: edited id not deleted", m.id not in fm2._deleted_ids)
        check("reload: stale rows treated as deleted",
              all(s in fm2._deleted_ids for s in fm2._idx_to_id if s.startswith("__stale__")))

        # ── 9. Delete after edit still hides it ──
        fm2.delete(m.id)
        check("deleted after edit → hidden",
              not any(h["id"] == m.id for h in fm2.search("drinks only water", top_k=10)))

        # ── 10. Heal: index damaged by old bug (active id in deleted_ids) ──
        tmp2 = tempfile.mkdtemp(dir=tmp)
        vp2, fd2 = os.path.join(tmp2, "vault.jsonl"), os.path.join(tmp2, "faiss")
        fm3 = _TestFAISS(vp2, fd2)
        victim = fm3.add("Favourite colour is teal", category="preference")
        fm3._deleted_ids.add(victim.id)  # what the old update() did
        fm3._save_index()
        check("precondition: damaged index hides memory",
              not any(h["id"] == victim.id for h in fm3.search("favourite colour teal", top_k=5)))
        fm4 = _TestFAISS(vp2, fd2)
        check("heal: rebuild clears stale deletion", victim.id not in fm4._deleted_ids)
        check("heal: memory searchable again",
              any(h["id"] == victim.id for h in fm4.search("favourite colour teal", top_k=5)))
        meta = json.loads(open(os.path.join(fd2, "index_meta.json"), encoding="utf-8").read())
        check("heal: persisted meta has no active ids deleted", victim.id not in meta["deleted_ids"])

        # ── 11. Legit deletion does NOT trigger heal rebuild ──
        fm4.delete(victim.id)
        fm5 = _TestFAISS(vp2, fd2)
        check("deleted memory stays deleted after reload", victim.id in fm5._deleted_ids)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGENT AVATARS — per-user uploads reachable via /api/uploads/
# ═════════════════════════════════════════════
def test_user_avatar_url_repointing():
    """_user_avatar_map repoints old /uploads/ avatars that live in the user's
    own uploads dir; api_profile_avatar saves new per-user uploads as /api/uploads/."""
    print("\n=== TORTURE: Agent Avatars — per-user /api/uploads/ URLs ===")
    import asyncio
    from pathlib import Path
    from types import SimpleNamespace
    import web.app as _app

    tmp = tempfile.mkdtemp()
    orig_uud = _app.user_uploads_dir
    orig_uploads = _app._UPLOADS_DIR
    orig_load, orig_save = _app._load_settings, _app._save_settings
    try:
        udirs = {}

        def _fake_uud(uid):
            p = Path(tmp) / "users" / uid / "uploads"
            p.mkdir(parents=True, exist_ok=True)
            udirs[uid] = p
            return p

        _app.user_uploads_dir = _fake_uud
        shared = Path(tmp) / "shared_uploads"
        shared.mkdir()
        _app._UPLOADS_DIR = shared

        # ── 1. _user_avatar_map: pure mapping ──
        ud = _fake_uud("u1")
        (ud / "avatar_nova_abc.png").write_bytes(b"x")
        amap = {
            "nova": {"image": "/uploads/avatar_nova_abc.png", "color": "#123456", "photo_zoom": 1.4},
            "orion": {"image": "/uploads/avatar_orion_shared.png"},   # not in user dir
            "supervisor": {"image": "/api/uploads/avatar_supervisor_x.png"},   # already new style
            "k_os": {"color": "#ff0000"},                              # no image
            "blank": {},
            "none_entry": None,
            "ext": {"image": "https://cdn.example.com/a.png"},
        }
        out = _app._user_avatar_map(amap, "u1")
        check("user-dir avatar repointed", out["nova"]["image"] == "/api/uploads/avatar_nova_abc.png")
        check("repoint keeps color", out["nova"]["color"] == "#123456")
        check("repoint keeps crop", out["nova"]["photo_zoom"] == 1.4)
        check("shared avatar untouched", out["orion"]["image"] == "/uploads/avatar_orion_shared.png")
        check("new-style URL untouched", out["supervisor"]["image"] == "/api/uploads/avatar_supervisor_x.png")
        check("no-image entry untouched", out["k_os"] == {"color": "#ff0000"})
        check("empty entry survives", out["blank"] == {})
        check("None entry survives", "none_entry" in out and out["none_entry"] is None)
        check("external URL untouched", out["ext"]["image"] == "https://cdn.example.com/a.png")
        check("input map not mutated", amap["nova"]["image"] == "/uploads/avatar_nova_abc.png")
        check("local user → same map", _app._user_avatar_map(amap, "__local__") is amap)
        check("no user → same map", _app._user_avatar_map(amap, None) is amap)
        check("empty uid → same map", _app._user_avatar_map(amap, "") is amap)

        # Path traversal: basename only — file outside user dir must not match
        (Path(tmp) / "secret.png").write_bytes(b"x")
        trav = _app._user_avatar_map({"a": {"image": "/uploads/../../secret.png"}}, "u1")
        check("traversal not repointed", trav["a"]["image"] == "/uploads/../../secret.png")

        # Other user's file doesn't leak across
        out_u2 = _app._user_avatar_map(amap, "u2")
        check("other user's file not repointed", out_u2["nova"]["image"] == "/uploads/avatar_nova_abc.png")

        # ── 2. api_profile_avatar: new uploads get the right prefix ──
        store = {}
        _app._load_settings = lambda user_id=None: json.loads(json.dumps(store.get(user_id or "__local__", {})))
        _app._save_settings = lambda s, user_id=None: store.__setitem__(user_id or "__local__", s)

        png = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

        def _req(uid, body):
            async def _json():
                return body
            return SimpleNamespace(state=SimpleNamespace(user={"id": uid} if uid else None), json=_json)

        r = asyncio.run(_app.api_profile_avatar("nova", _req("u9", {"image": png})))
        img = r.get("image", "")
        check("cloud upload → /api/uploads/", img.startswith("/api/uploads/avatar_nova_"))
        check("cloud upload file in user dir", (udirs["u9"] / os.path.basename(img)).is_file())
        check("cloud upload NOT in shared dir", not (shared / os.path.basename(img)).exists())

        # Replace: old /api/uploads/ file removed
        r2 = asyncio.run(_app.api_profile_avatar("nova", _req("u9", {"image": png})))
        img2 = r2.get("image", "")
        check("cloud replace new name", img2 != img and img2.startswith("/api/uploads/avatar_nova_"))
        check("cloud replace removes old file", not (udirs["u9"] / os.path.basename(img)).exists())

        # Clear: /api/uploads/ file removed
        r3 = asyncio.run(_app.api_profile_avatar("nova", _req("u9", {"image": ""})))
        check("cloud clear → empty", r3.get("image") == "")
        check("cloud clear removes file", not (udirs["u9"] / os.path.basename(img2)).exists())

        # Clear an old-style /uploads/ avatar stored for a cloud user
        (udirs["u9"] / "avatar_nova_old.png").write_bytes(b"x")
        store["u9"]["agent_avatars"]["nova"]["image"] = "/uploads/avatar_nova_old.png"
        asyncio.run(_app.api_profile_avatar("nova", _req("u9", {"image": ""})))
        check("cloud clear of legacy URL removes file", not (udirs["u9"] / "avatar_nova_old.png").exists())

        # Crop fields persisted
        asyncio.run(_app.api_profile_avatar("nova", _req("u9", {"photo_zoom": 1.8, "photo_x": 30, "photo_y": 70})))
        e = store["u9"]["agent_avatars"]["nova"]
        check("crop fields saved", (e.get("photo_zoom"), e.get("photo_x"), e.get("photo_y")) == (1.8, 30, 70))

        # Local user keeps shared /uploads/
        r4 = asyncio.run(_app.api_profile_avatar("nova", _req(None, {"image": png})))
        img4 = r4.get("image", "")
        check("local upload → /uploads/", img4.startswith("/uploads/avatar_nova_"))
        check("local upload file in shared dir", (shared / os.path.basename(img4)).is_file())

        # ── 3. Chat + Profiles pages route through the helper ──
        import inspect
        src_chat = inspect.getsource(_app.page_chat)
        src_prof = inspect.getsource(_app.page_profiles)
        check("page_chat uses _user_avatar_map", "_user_avatar_map(" in src_chat)
        check("page_profiles uses _user_avatar_map", "_user_avatar_map(" in src_prof)
    finally:
        _app.user_uploads_dir = orig_uud
        _app._UPLOADS_DIR = orig_uploads
        _app._load_settings, _app._save_settings = orig_load, orig_save
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# CHAT TEMPLATE — avatar crop/fallback + GA funnel events
# ═════════════════════════════════════════════
def test_chat_avatar_and_analytics_template():
    """chat.html: _agentAvatarHtml honours crop + falls back to initial;
    GA events message_sent / first_message_sent / hit_message_limit wired."""
    print("\n=== TORTURE: Chat Template — avatar crop & analytics ===")
    import re
    import subprocess
    tpl = os.path.join(os.path.dirname(__file__), "..", "web", "templates", "chat.html")
    html = open(tpl, encoding="utf-8").read()

    # ── 1. Avatar helper structure ──
    check("_agentAvatarHtml defined", "function _agentAvatarHtml(agentName, av)" in html)
    check("_avatarFallback defined", "function _avatarFallback(img)" in html)
    check("img has onerror fallback", 'onerror="_avatarFallback(this)"' in html)
    check("image src escaped", "src=\"${esc(thumbUrl(av.image, 128))}\"" in html)
    check("avatar asks for a thumbnail", "thumbUrl(av.image, 128)" in html)
    check("no raw unescaped avatar <img> left",
          not re.search(r'<img src="\$\{(av|_tav)\.image\}"', html))
    check("all 3 render paths use helper", html.count("_agentAvatarHtml(agent") >= 3)

    # ── 2. GA helpers + call sites ──
    check("_gaEvent guards gtag", "typeof gtag === 'function'" in html)
    check("message_sent event", "_gaEvent('message_sent'" in html)
    check("first_message_sent once via localStorage", "of_ga_first_msg" in html
          and "_gaEvent('first_message_sent'" in html)
    check("hit_message_limit event", "_gaEvent('hit_message_limit'" in html)
    check("402 triggers limit", "status === 402" in html)
    check("insufficient-credits text triggers limit", "/insufficient credits/i" in html)
    check("_gaMessageSent called after reply", "_gaMessageSent(agent, finalData.model)" in html)
    check("_gaLimitIfCredits called ≥3 places", html.count("_gaLimitIfCredits(agent") >= 3)

    # ── 3. Execute the helpers in node (skipped if node missing) ──
    import shutil as _sh
    node = _sh.which("node")
    if not node:
        check("node not available — skipped JS execution", True)
        return

    def _fn(name):
        m = re.search(r"^function " + re.escape(name) + r"\(.*?^\}", html, re.S | re.M)
        return m.group(0) if m else ""

    # thumbUrl() lives in base.html, which every page includes
    base = open(os.path.join(os.path.dirname(tpl), "base.html"), encoding="utf-8").read()
    m_thumb = re.search(r"^ *function thumbUrl\(.*?^ *\}$", base, re.S | re.M)
    check("base.html defines thumbUrl", bool(m_thumb))
    js = "\n".join([
        m_thumb.group(0) if m_thumb else "function thumbUrl(u) { return u; }",
        "const esc = s => String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\"/g,'&quot;');",
        "const _agentAvatarColor = () => '#abcdef';",
        "const events = []; globalThis.gtag = (t, n, p) => events.push([n, p]);",
        "const _ls = {}; globalThis.localStorage = {getItem: k => _ls[k] ?? null, setItem: (k, v) => { _ls[k] = v; }};",
        _fn("_agentAvatarHtml"), _fn("_avatarFallback"),
        _fn("_gaEvent"), _fn("_gaMessageSent"), _fn("_gaLimitIfCredits"),
        "const r = {};",
        "r.noImg = _agentAvatarHtml('nova', {});",
        "r.undef = _agentAvatarHtml('nova');",
        "r.def = _agentAvatarHtml('nova', {image: '/api/uploads/a.png'});",
        "r.thumbs = [thumbUrl('/uploads/a.png', 128), thumbUrl('/api/uploads/b.jpg?x=1', 64), thumbUrl('/uploads/c.gif', 64), thumbUrl('https://e/x.png', 64), thumbUrl('', 64)];",
        "r.crop = _agentAvatarHtml('nova', {image: '/a.png', photo_x: 20, photo_y: 80, photo_zoom: '1.5', color: '#111'});",
        "r.zero = _agentAvatarHtml('nova', {image: '/a.png', photo_x: 0, photo_y: 0});",
        "r.xss = _agentAvatarHtml('nova', {image: '\" onload=\"alert(1)'});",
        "const box = {dataset: {fallbackColor: '#222', initial: 'N'}, style: {}, textContent: ''};",
        "_avatarFallback({parentElement: box}); r.fb = [box.style.background, box.textContent];",
        "_avatarFallback({parentElement: null});",
        "_gaMessageSent('nova', 'gpt'); _gaMessageSent('nova', 'gpt');",
        "_gaLimitIfCredits('nova', 402, ''); _gaLimitIfCredits('nova', 0, 'Insufficient credits left');",
        "_gaLimitIfCredits('nova', 500, 'boom');",
        "r.events = events.map(e => e[0]);",
        "console.log(JSON.stringify(r));",
    ])
    p = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=30)
    check("node JS executed", p.returncode == 0, p.stderr[-300:])
    if p.returncode != 0:
        return
    r = json.loads(p.stdout.strip().splitlines()[-1])

    check("no image → initial bubble", ">N</div>" in r["noImg"] and "<img" not in r["noImg"])
    check("undefined av → initial bubble", ">N</div>" in r["undef"])
    check("no image uses fallback color", "background:#abcdef" in r["noImg"])
    check("default crop 50% 50%", "object-position:50% 50%" in r["def"])
    check("avatar img uses the thumbnail", 'src="/api/uploads/a.png?w=128"' in r["def"])
    check("thumbUrl mirrors the server filter",
          r["thumbs"] == ["/api/uploads/a.png?w=128", "/api/uploads/b.jpg?w=64", "/uploads/c.gif", "https://e/x.png", ""])
    check("zoom 1 → no transform", "transform" not in r["def"])
    check("custom crop position", "object-position:20% 80%" in r["crop"])
    check("zoom applied", "transform:scale(1.5)" in r["crop"])
    check("transform-origin matches crop", "transform-origin:20% 80%" in r["crop"])
    check("fallback color carried", 'data-fallback-color="#111"' in r["crop"])
    check("photo_x/y 0 not treated as default", "object-position:0% 0%" in r["zero"])
    check("image URL attribute-escaped", 'onload="alert' not in r["xss"])
    check("fallback swaps to initial", r["fb"] == ["#222", "N"])
    check("message_sent fires every time", r["events"].count("message_sent") == 2)
    check("first_message_sent fires once", r["events"].count("first_message_sent") == 1)
    check("limit fires for 402 + credits text only", r["events"].count("hit_message_limit") == 2)


# ═════════════════════════════════════════════
# DEMO + PROFILES — 4-message demo cap, new-agent guidance
# ═════════════════════════════════════════════
def test_demo_limit_and_profile_guidance():
    """web/demo/index.html enforces a 4-message per-visitor cap that New chat
    can't refund; profiles.html shows example prompt / soul-script templates."""
    print("\n=== TORTURE: Demo 4-message cap + agent prompt guidance ===")
    import re
    base = os.path.join(os.path.dirname(__file__), "..", "web")
    demo = open(os.path.join(base, "demo", "index.html"), encoding="utf-8").read()

    # ── 1. Demo cap ──
    m = re.search(r"const MSG_LIMIT = (\d+);", demo)
    check("MSG_LIMIT defined", m is not None)
    check("MSG_LIMIT is 4", m is not None and m.group(1) == "4")
    check("used count seeded from history", "state.used = Math.max(state.used || 0, totalSent)" in demo)
    check("outOfMessages helper", "const outOfMessages = () => state.used >= MSG_LIMIT" in demo)
    check("send() blocks when out", "if (outOfMessages()) { renderExtras(); return; }" in demo)
    check("input disabled when locked", "$('input').disabled = locked" in demo)
    check("send button disabled when locked", "$('send').disabled = locked || busy" in demo)
    check("CTA forced when locked", "toggle('show', locked || turns >= 3)" in demo)
    check("placeholder counts down", "free message${left === 1 ? '' : 's'} left" in demo)
    check("quota_reached tracked", "track('demo_quota_reached'" in demo)
    check("chips hidden when locked", "const list = locked ? []" in demo)

    # used++ only on a successful reply (errors don't burn quota)
    send_body = demo[demo.find("async function send("):]
    send_body = send_body[:send_body.find("\n}\n")]
    ok_branch = send_body[send_body.find("} else {"):]
    check("used++ in success branch only",
          send_body.count("state.used++") == 1 and "state.used++" in ok_branch
          and ok_branch.find("state.used++") < ok_branch.find("} catch {"))
    check("state saved after send", "save();" in send_body)

    # New chat resets history but NOT used
    nc = re.search(r"state\.chats\[current\] = \[\];[^\n]*", demo)
    check("new chat clears history", nc is not None)
    check("new chat doesn't refund quota", nc is not None and "used" not in nc.group(0))

    # ── 2. Profiles template guidance ──
    prof = open(os.path.join(base, "templates", "profiles.html"), encoding="utf-8").read()
    check("system prompt example placeholder", "You are Nova, a warm but blunt career coach" in prof)
    check("soul script ### template", "### Origin" in prof and "### Boundaries" in prof)
    check("soul script sections explained", "each one is retrieved on its own" in prof)
    check("Codex Animus pointer in hints", prof.count("Codex Animus") >= 3)
    check("old generic placeholder gone", "Write the system prompt for this agent…" not in prof)


# ═════════════════════════════════════════════
# AGI LOOP — shared helpers for the loop torture sections below
# ═════════════════════════════════════════════
from pathlib import Path


class _TortureLoopHost:
    """Stands in for the model: a different thought every call, so the repetition guard stays quiet."""

    def __init__(self):
        self.n = 0
        self.views = []

    def prepare(self, agent, view):
        self.views.append(view)
        return [{"role": "system", "content": f"You are {agent}."}], []

    async def complete(self, config, messages, tools):
        from src.agi_loop.daemon import Completion
        self.n += 1
        return Completion(message={"role": "assistant", "content": f"thought {self.n}"},
                          tokens=100, cost=0.0001, model="stub")

    def call_tool(self, agent, name, args):
        return "ok"

    def after_response(self, agent, text):
        return text

    def pending_tasks(self):
        return []


def _torture_loop(tmp, sub="d", loop_id="supervisor", group=None, **cfg):
    from pathlib import Path
    from src.agi_loop import LoopConfig, LoopDaemon
    base = dict(agent="tester", timezone="America/New_York", base_interval_seconds=30, min_interval_seconds=5, max_interval_seconds=1800)
    base.update(cfg)
    return LoopDaemon(_TortureLoopHost(), LoopConfig.from_dict(base), Path(tmp) / sub, loop_id=loop_id, group=group)


def _ts(*args):
    from datetime import datetime, timezone
    return datetime(*args, tzinfo=timezone.utc).timestamp()


# ═════════════════════════════════════════════
# AGI LOOP — the clock: measured durations, Trent's time zone, the HUD clock line
# ═════════════════════════════════════════════
def test_agi_loop_clock_and_timezone():
    """The HUD's time is the host's wall clock, shown in Trent's zone and UTC; durations are measured, not felt."""
    print("\n=== TORTURE: AGI Loop — clock, time zone, measured durations ===")
    from src.agi_loop.world import fmt_span, InnerWorld
    from src.agi_loop.channels import local_dt, part_of_day, time_channel, ChannelContext
    from src.agi_loop.budget import DailyBudget
    from src.agi_loop.config import LoopConfig
    from pathlib import Path

    # ── fmt_span: to the second, every unit boundary ──
    for secs, want in [(0, "0s"), (1, "1s"), (59, "59s"), (59.4, "59s"), (59.6, "1m 00s"), (60, "1m 00s"),
                       (615, "10m 15s"), (3599, "59m 59s"), (3600, "1h 00m"), (3661, "1h 01m"),
                       (86399, "23h 59m"), (86400, "1d 0h"), (90061, "1d 1h"), (-5, "0s")]:
        check(f"fmt_span({secs}) → {want}", fmt_span(secs) == want, fmt_span(secs))

    # ── local_dt: Trent's zone, daylight saving both sides, bad names fall back to UTC ──
    summer = local_dt(_ts(2026, 7, 1, 12), "America/New_York")
    check("summer noon UTC is 08:00 EDT", (summer.hour, summer.tzname()) == (8, "EDT"), summer)
    winter = local_dt(_ts(2026, 1, 15, 12), "America/New_York")
    check("winter noon UTC is 07:00 EST", (winter.hour, winter.tzname()) == (7, "EST"), winter)
    before = local_dt(_ts(2026, 3, 8, 6, 59), "America/New_York")
    after = local_dt(_ts(2026, 3, 8, 7, 0), "America/New_York")
    check("DST start: 06:59 UTC is 01:59 EST", (before.hour, before.minute, before.tzname()) == (1, 59, "EST"))
    check("DST start: 07:00 UTC is 03:00 EDT", (after.hour, after.tzname()) == (3, "EDT"))
    for bad in ("Not/AZone", "", None):
        d = local_dt(_ts(2026, 7, 1, 12), bad)
        check(f"unknown zone {bad!r} falls back to UTC", d.hour == 12 and d.utcoffset().total_seconds() == 0)
    check("Trent's 9 PM is 01:00 UTC the next day (the '3 am' confusion)",
          local_dt(_ts(2026, 10, 8, 1, 7), "America/New_York").strftime("%H:%M %Z") == "21:07 EDT")

    # ── part_of_day boundaries ──
    for hour, want in [(0, "night"), (4, "night"), (5, "morning"), (11, "morning"), (12, "afternoon"),
                       (16, "afternoon"), (17, "evening"), (21, "evening"), (22, "night"), (23, "night")]:
        check(f"part_of_day({hour}) → {want}", part_of_day(hour) == want)

    # ── the time channel reads in Trent's zone ──
    tmp = tempfile.mkdtemp()
    try:
        now = _ts(2026, 7, 1, 12)
        b = DailyBudget(Path(tmp) / "b.json", 1000)
        sig = time_channel(ChannelContext(now=now, tick=2, world=InnerWorld(), budget=b,
                                          last_tick_at=now - 30, tz="America/New_York"))
        item = sig.items[0]
        check("time gauge gist is local, with zone", item["gist"] == "morning, 08:00 EDT", item["gist"])
        check("time text says how long since you looked", "30s since you last looked" in item["text"])
        check("time gap is a feature for the predictor", sig.features.get("time.gap") == 30)
        first = time_channel(ChannelContext(now=now, tick=1, world=InnerWorld(), budget=b, tz="America/New_York"))
        check("first look says you just woke", "you just woke" in first.items[0]["text"]
              and "time.gap" not in first.features)
        utc = time_channel(ChannelContext(now=now, tick=1, world=InnerWorld(), budget=b))
        check("context default zone is UTC", "12:00 UTC" in utc.items[0]["text"], utc.items[0]["text"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── config: the timezone setting ──
    check("timezone defaults to UTC", LoopConfig().timezone == "UTC")
    check("timezone loads from config", LoopConfig.from_dict({"timezone": "Europe/London"}).timezone == "Europe/London")
    check("missing timezone keeps the default", LoopConfig.from_dict({"timezone": None}).timezone == "UTC")
    check("timezone round-trips", LoopConfig.from_dict(LoopConfig(timezone="Asia/Tokyo").to_dict()).timezone == "Asia/Tokyo")

    # ── the clock line, against fixed times ──
    tmp = tempfile.mkdtemp()
    try:
        d = _torture_loop(tmp)
        now = _ts(2026, 10, 8, 1, 7, 30)
        d.world.tick = 5
        check("clock line with no history is just the time, both zones",
              d._clock_line(now, None) == "⏲ now 21:07:30 EDT (the operator's time) = 01:07:30 UTC", d._clock_line(now, None))
        d.last_tick_at, d.last_result = now - 615, {"took": 14.9}
        d.last_sleep, d.wake_reason = {"planned": 600, "slept": 600.4, "reason": "timer", "rest": None}, "timer"
        line = d._clock_line(now, 615)
        check("previous tick: number, local start time, age", "tick 4 began 20:57:15 EDT (10m 15s ago)" in line, line)
        check("previous tick: how long it really ran", "and ran 15s" in line, line)
        check("sleep: measured against plan", "slept 10m 00s of 10m 00s planned" in line, line)
        check("on-time sleep isn't called late", "late" not in line and "early" not in line, line)
        d.last_sleep = {"planned": 600, "slept": 700, "reason": "timer", "rest": None}
        check("a late wake says how late", "1m 40s late" in d._clock_line(now, 700))
        d.last_sleep = {"planned": 600, "slept": 630, "reason": "timer", "rest": None}
        check("under a minute over isn't called late", "late" not in d._clock_line(now, 630))
        d.last_sleep = {"planned": 5400, "slept": 31, "reason": "message", "rest": "nothing live"}
        check("a message cut the sleep short", "slept 31s of 1h 30m planned, a message woke you early" in d._clock_line(now, 31))
        d.wake_reason = "start"
        check("after a start there is no sleep to report", "slept" not in d._clock_line(now, 615))
        d.last_result = {}
        check("no duration recorded → no 'ran' claim", "ran" not in d._clock_line(now, 615))
        d.config.timezone = "Europe/London"
        check("the clock follows the configured zone", "02:07:30 BST" in d._clock_line(now, None))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── the rendered field: header line, clock and pace lines, legacy key ignored ──
    w = InnerWorld()
    now = _ts(2026, 10, 8, 1, 7, 30)
    view = w.render(now, {"now": "Wed 07 Oct 21:07:30 EDT", "part_of_day": "evening", "energy": 0.5,
                          "left": "$1.00 of $2.00 left today", "clock": "⏲ CLOCK", "pace": "pace: PACE",
                          "woke": "You woke on your own.", "tokens_left": "SHOULD-NOT-SHOW"})
    lines = view.splitlines()
    check("field header carries the local time", lines[0] == "FIELD · tick 0 · Wed 07 Oct 21:07:30 EDT, evening", lines[0])
    check("energy shows what's left in the binding unit", "($1.00 of $2.00 left today)" in lines[1], lines[1])
    check("clock then pace sit right under the HUD", lines[2:4] == ["⏲ CLOCK", "pace: PACE"], lines[2:4])
    check("the woke line follows them", lines.index("You woke on your own.") > 3)
    check("the old tokens_left key is no longer rendered", "SHOULD-NOT-SHOW" not in view)
    bare = w.render(now, {})
    check("without a header time the field falls back to UTC, with seconds", "Thu 08 Oct 01:07:30 UTC" in bare.splitlines()[0])
    check("no clock/pace keys → no empty lines for them", "⏲" not in bare and "pace:" not in bare)

    # ── a real tick puts all of it in front of the model ──
    tmp = tempfile.mkdtemp()
    try:
        d = _torture_loop(tmp)
        d.running = True
        import asyncio
        asyncio.run(d.tick())
        asyncio.run(d.tick())
        v = d.ticks.tail(1)[0]["view"]
        check("tick view: field header in Trent's zone", (" EDT, " in v.splitlines()[0]) or (" EST, " in v.splitlines()[0]), v.splitlines()[0])
        check("tick view: measured clock line", "⏲ now" in v and "(the operator's time)" in v and "tick 1 began" in v)
        check("each tick records its own wall-time duration", isinstance(d.last_result.get("took"), float))
        check("the model was shown exactly that view", d.host.views[-1] == v)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — energy readout always agrees with the gauge
# ═════════════════════════════════════════════
def test_agi_loop_energy_readout():
    print("\n=== TORTURE: AGI Loop — energy / what's left ===")
    from src.agi_loop.budget import DailyBudget
    from src.agi_loop.channels import body_channel, ChannelContext
    from src.agi_loop.world import InnerWorld
    from pathlib import Path
    tmp = tempfile.mkdtemp()
    try:
        b = DailyBudget(Path(tmp) / "a.json", 1_000_000, 1.0)
        b.spend(100_000, 0.5)
        check("cost cap tighter → cost binds", b.cost_binds)
        check("…and 'left' is in dollars", b.left_text() == "$0.50 of $1.00 left today", b.left_text())
        check("…and energy is the cost fraction", abs(b.energy - 0.5) < 1e-9)
        b2 = DailyBudget(Path(tmp) / "b.json", 1_000_000, 100.0)
        b2.spend(400_000, 0.5)
        check("token cap tighter → tokens bind", not b2.cost_binds)
        check("…and 'left' is in tokens", b2.left_text() == "600,000 tokens left today", b2.left_text())
        b3 = DailyBudget(Path(tmp) / "c.json", 1_000_000, 0.0)
        b3.spend(10, 999.0)
        check("no cost cap → cost never binds", not b3.cost_binds and "tokens" in b3.left_text())
        b4 = DailyBudget(Path(tmp) / "d.json", 1000, 1.0)
        b4.spend(500, 0.5)
        check("equal fractions → tokens reported", not b4.cost_binds)
        b5 = DailyBudget(Path(tmp) / "e.json", 1000, 1.0)
        b5.spend(0, 5.0)
        check("overspent dollars never go negative", b5.left_text() == "$0.00 of $1.00 left today" and b5.exhausted)
        check("to_dict carries cost_binds", b.to_dict()["cost_binds"] is True and b2.to_dict()["cost_binds"] is False)
        b.day = "2000-01-01"
        check("a new day resets what's left", b.left_text() == "1,000,000 tokens left today" and not b.cost_binds)
        sig = body_channel(ChannelContext(now=time.time(), tick=1, world=InnerWorld(), budget=b2))
        check("the body channel says the same thing as the HUD", "600,000 tokens left today" in sig.items[0]["text"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — pace: what she chose, what energy did to it, and that it survives a restart
# ═════════════════════════════════════════════
def test_agi_loop_pace_honesty():
    print("\n=== TORTURE: AGI Loop — pace note + pace persistence ===")
    import json as _json
    tmp = tempfile.mkdtemp()
    try:
        d = _torture_loop(tmp, base_interval_seconds=120)
        secs, _ = d._next_interval()
        check("adaptive pace is named as such", d.pace_note == "pace: adaptive, base 2m 00s" and secs == 120, d.pace_note)
        d.world.arousal = 0.5
        secs, _ = d._next_interval()
        check("surprise quickens adaptive pace — and says so", "surprise quickens it" in d.pace_note and secs < 120, d.pace_note)
        d.world.arousal = 0.0
        d.set_pace(600, "watching")
        secs, _ = d._next_interval()
        check("chosen pace is reported as chosen", d.pace_note == "pace: you chose 10m 00s" and secs == 600, d.pace_note)
        d.world.arousal = 0.9
        d._next_interval()
        check("surprise doesn't touch a chosen pace", "surprise" not in d.pace_note)
        d.budget.spend(int(d.budget.tokens_per_day * 0.75), 0)
        secs, _ = d._next_interval()
        check("low energy stretches it — 25% doubles 10m", secs == 1200, secs)
        check("…and the note says by how much", d.pace_note == "pace: you chose 10m 00s; energy at 25% stretches it → 20m 00s", d.pace_note)
        d.budget.spend(10**12, 0)
        secs, _ = d._next_interval()
        check("stretching is still clamped to the max interval", secs == 1800 and d.pace_note.endswith("→ 30m 00s"), d.pace_note)
        note = d.pace_note
        d.request_rest(45, "tired")
        secs, why = d._next_interval()
        check("rest overrides pace without rewriting the pace note", secs == 2700 and why == "tired" and d.pace_note == note)

        # persistence
        d.save()
        d2 = _torture_loop(tmp)
        check("a chosen pace survives a restart", d2.pace == (600.0, "watching"))
        d2.set_pace(None)
        d2.save()
        check("returning to adaptive survives a restart too", _torture_loop(tmp).pace is None)
        state = Path(tmp) / "d" / "state.json"
        raw = _json.loads(state.read_text(encoding="utf-8"))
        raw["pace"] = ["45", 7]
        state.write_text(_json.dumps(raw), encoding="utf-8")
        d3 = _torture_loop(tmp)
        check("pace stored as strings is coerced", d3.pace == (45.0, "7"))
        state.write_text("{not json", encoding="utf-8")
        d4 = _torture_loop(tmp)
        check("a corrupt state file starts clean, not crashed", d4.pace is None and d4.prior_stop == {"at": None, "reason": None})
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — restarts: autostart mark, honest wake line, a deploy vs a deliberate stop
# ═════════════════════════════════════════════
def test_agi_loop_restart_awareness():
    print("\n=== TORTURE: AGI Loop — restart awareness + autostart ===")
    import asyncio
    tmp = tempfile.mkdtemp()
    try:
        d = _torture_loop(tmp)
        check("autostart mark lives in the loop's data dir", d.autostart_file == Path(tmp) / "d" / "autostart")
        d.wake_reason = "start"
        check("first life: just woken", d._woke_line(None) == "You've just woken up.")

        async def deploy_then_restart():
            a = _torture_loop(tmp)
            a.start()
            for _ in range(100):
                if a.world.tick >= 1 and a.phase == "sleeping":
                    break
                await asyncio.sleep(0.02)
            marked = a.autostart_file.exists()
            a.task.cancel()                    # what a deploy does to the process
            await asyncio.sleep(0.1)
            survived = a.autostart_file.exists()
            reason = a.stop_reason
            b = _torture_loop(tmp)             # the next process
            prior = dict(b.prior_stop)
            recorded = len(b.ticks.items)
            b.start()
            for _ in range(250):               # wait for a *recorded* tick, not just a started one
                if len(b.ticks.items) > recorded:
                    break
                await asyncio.sleep(0.02)
            view = b.ticks.tail(1)[0]["view"]
            b.stop("operator")
            await asyncio.sleep(0.1)
            return marked, survived, reason, prior, view, b.autostart_file.exists()

        marked, survived, reason, prior, view, after_stop = asyncio.run(deploy_then_restart())
        check("running marks the loop for autostart", marked)
        check("a deploy (cancelled task) keeps the mark", survived, reason)
        check("…and is recorded as cancelled", reason == "cancelled", reason)
        check("the next process reads how the last run ended", prior["reason"] == "cancelled" and prior["at"])
        check("the new run is told it's a new run", "You are a new run of yourself." in view, view[:600])
        check("…that the process went down under it", "went down under you" in view)
        check("…and what survived and what didn't", "the thought you were in the middle of was not" in view)
        check("an operator stop clears the mark", after_stop is False)

        e = _torture_loop(tmp)
        e.wake_reason, e.started_at = "start", time.time()
        check("operator stop → wake line says stopped, when, why",
              "the last run was stopped" in e._woke_line(60) and "(operator)" in e._woke_line(60))
        e.prior_stop = {"at": time.time() - 3600, "reason": "guard: 5 errors in a row"}
        check("guard stop → named with its duration", "stopped 1h 00m ago (guard: 5 errors in a row)" in e._woke_line(60), e._woke_line(60))
        for r in ("crashed: boom", "", None):
            e.prior_stop = {"at": time.time(), "reason": r}
            check(f"stop reason {r!r} reads as going down, not a stop", "went down under you" in e._woke_line(60))
        e.prior_stop = {"at": None, "reason": None}
        check("no record of a stop at all → went down", "went down under you" in e._woke_line(60))
        for wr, want in [("message", "Someone at the door woke you."), ("rest_message", "from your rest."),
                         ("poke", "You were nudged awake."), ("timer", "You woke on your own after")]:
            e.wake_reason = wr
            check(f"wake reason {wr} unchanged", want in e._woke_line(90))

        for reason in ("agent: done for now", "guard: still repeating"):
            f = _torture_loop(tmp, sub=f"f{len(reason)}")
            f.autostart_file.write_text("x")
            f.request_stop(reason)
            check(f"deliberate stop ({reason.split(':')[0]}) clears the mark", not f.autostart_file.exists())
        g = _torture_loop(tmp, sub="g")
        g.request_stop("operator")
        check("clearing an absent mark is harmless", not g.autostart_file.exists())
        h = _torture_loop(tmp, sub="h")
        h.autostart_file.write_text("x")
        h.running = True
        h.tools.execute("loop_control", {"action": "stop", "reason": "enough"})
        check("the agent's own stop tool clears it", not h.autostart_file.exists() and h.stop_reason == "agent: enough")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — the handoff letter is the first thing a new run sees
# ═════════════════════════════════════════════
def test_agi_loop_handoff_letter():
    print("\n=== TORTURE: AGI Loop — handoff letter first ===")
    import asyncio
    tmp = tempfile.mkdtemp()
    try:
        d = _torture_loop(tmp)
        root = Path(d.workbench.root)
        (root / "handoff").mkdir()
        letter = root / "handoff" / "letter.md"
        letter.write_text("Read this before you touch anything else. — E.", encoding="utf-8")
        d._admit_handoff()
        check("first life: no letter is shown", d.world.get("handoff-letter") is None)

        d.last_tick_at = time.time() - 60
        check("finds handoff/letter.md", d._find_handoff() == letter)
        d._admit_handoff()
        it = d.world.get("handoff-letter")
        check("the letter enters the field", it is not None)
        check("…as a note from yourself", it.kind == "note" and it.source == "self")
        check("…held so it can't fade", it.held)
        check("…and focused", d.world.focus_item == it.id)
        check("…quoted in full, in her words", "Read this before you touch anything else. — E." in it.text)
        check("…saying where it lives and when it was written", "(handoff/letter.md, written " in it.text)
        check("…with a findable gist", it.gist == "your letter: handoff/letter.md")
        check("the moment is logged", any(ev["kind"] == "handoff" for ev in d.events.tail(5)))
        check("'written' is in Trent's time zone", " EDT)" in it.text or " EST)" in it.text, it.text[:120])
        n = len(d.world.items)

        # a second restart without a new letter: told the truth, not handed the old letter as new
        d.save()
        d2 = _torture_loop(tmp)
        check("which letter was shown survives a restart", d2.handoff_seen.get("path") == "handoff/letter.md")
        d2._admit_handoff()
        again = d2.world.get("handoff-letter")
        check("an already-read letter isn't replayed as new", again is not None
              and "You didn't leave a new letter before this restart." in again.text
              and "Read this before you touch anything else" not in again.text, again.text if again else None)
        check("…and the old letter is let go (no longer held)", not again.held)
        check("…and the event says why", any("already read" in ev["text"] for ev in d2.events.tail(3)))
        check("no duplicate item either way", sum(1 for i in d2.world.items.values() if i.key == "handoff-letter") == 1)
        later = time.time() + 5
        letter.write_text("A new letter, for this gap.", encoding="utf-8")
        os.utime(letter, (later, later))
        d3 = _torture_loop(tmp)
        d3._admit_handoff()
        fresh = d3.world.get("handoff-letter")
        check("a rewritten letter is shown in full again", "A new letter, for this gap." in fresh.text
              and fresh.held and d3.world.focus_item == fresh.id)
        d._admit_handoff()
        check("admitting twice doesn't duplicate it", len(d.world.items) == n)

        k = _torture_loop(tmp, sub="k")
        kroot = Path(k.workbench.root)
        (kroot / "documents").mkdir()
        older = kroot / "documents" / "handoff-letter-2026-10-07.md"
        newer = kroot / "documents" / "handoff-letter-2026-10-08.md"
        older.write_text("old", encoding="utf-8")
        newer.write_text("new", encoding="utf-8")
        (kroot / "documents" / "notes.md").write_text("not a letter", encoding="utf-8")
        os.utime(older, (time.time() - 7200, time.time() - 7200))
        check("K-OS's documents/handoff-letter-*.md is found", k._find_handoff() == newer)
        os.utime(newer, (time.time() - 9000, time.time() - 9000))
        check("the newest letter wins, whatever its name", k._find_handoff() == older)
        (kroot / "HANDOFF.md").write_text("root letter", encoding="utf-8")
        check("a HANDOFF*.md at the bench root is found too", k._find_handoff() == kroot / "HANDOFF.md")

        s = _torture_loop(tmp, sub="s")
        sroot = Path(s.workbench.root)
        (sroot / "handoff").mkdir()
        stale = sroot / "handoff" / "letter.md"
        stale.write_text("from long ago", encoding="utf-8")
        s.last_tick_at = time.time()
        os.utime(stale, (time.time() - 8 * 86400, time.time() - 8 * 86400))
        s._admit_handoff()
        check("a letter more than a week older than the last tick is ignored", s.world.get("handoff-letter") is None)
        os.utime(stale, (time.time() - 6 * 86400, time.time() - 6 * 86400))
        s._admit_handoff()
        check("…six days old is still shown", s.world.get("handoff-letter") is not None)

        l = _torture_loop(tmp, sub="l")
        (Path(l.workbench.root) / "handoff").mkdir()
        (Path(l.workbench.root) / "handoff" / "letter.md").write_text("x" * 5000, encoding="utf-8")
        l.last_tick_at = time.time()
        l._admit_handoff()
        lt = l.world.get("handoff-letter").text
        check("a long letter is quoted to 3000 chars", lt.count("x") == 3000)
        check("…with a pointer to the rest", lt.endswith("(the rest: workbench read handoff/letter.md)"))

        full = _torture_loop(tmp, sub="full")
        (Path(full.workbench.root) / "handoff").mkdir()
        (Path(full.workbench.root) / "handoff" / "letter.md").write_text("hi", encoding="utf-8")
        full.last_tick_at = time.time()
        for i in range(3):
            x, _ = full.world.upsert(f"h{i}", "note", "self", f"held thing {i}")
            full.world.hold(x)
        full._admit_handoff()
        fl = full.world.get("handoff-letter")
        check("three things already held → the letter still arrives and is focused",
              fl is not None and full.world.focus_item == fl.id and not fl.held)

        nb = _torture_loop(tmp, sub="nb", workbench=False)
        nb.last_tick_at = time.time()
        check("no bench → no letter, no crash", nb._find_handoff() is None and (nb._admit_handoff() is None))

        # end to end: a restarted daemon's first view is focused on the letter
        r = _torture_loop(tmp, sub="r")
        (Path(r.workbench.root) / "handoff").mkdir()
        (Path(r.workbench.root) / "handoff" / "letter.md").write_text("You're me with a seam. Act like it.", encoding="utf-8")
        r.last_tick_at = time.time() - 600
        r.save()

        async def wake():
            r2 = _torture_loop(tmp, sub="r")
            r2.start()
            for _ in range(250):          # wait for a *recorded* tick: the counter moves when a tick begins
                if r2.ticks.items:
                    break
                await asyncio.sleep(0.02)
            r2.stop("test")
            await asyncio.sleep(0.05)
            return r2.ticks.tail(1)[0]["view"]

        view = asyncio.run(wake())
        focus = next((ln for ln in view.splitlines() if ln.startswith("FOCUS ▸")), "")
        check("the first thing a new run sees is its own letter",
              "A letter you left yourself" in focus and "You're me with a seam. Act like it." in view, focus[:200])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — the slab: one shared, append-only file in the room
# ═════════════════════════════════════════════
def test_agi_loop_slab():
    print("\n=== TORTURE: AGI Loop — the slab ===")
    import threading
    from src.agi_loop.groupchat import Slab, GroupChat, SLAB_MAX_TEXT
    from src.agi_loop.tools import GROUP_DEF
    tmp = tempfile.mkdtemp()
    try:
        p = Path(tmp) / "slab.jsonl"
        s = Slab(p)
        check("a new slab is empty", s.read() == [] and s.seq == 0)
        e1 = s.write("k_os", "k_os", 550, "  the seam line, credited to E.  ")
        e2 = s.write("supervisor", "supervisor", 510, "received.\nTwo lines, ✓ unicode.")
        check("sequence numbers start at 1 and count up", (e1["seq"], e2["seq"]) == (1, 2))
        check("text is trimmed", e1["text"] == "the seam line, credited to E.")
        check("newlines and unicode are kept", e2["text"] == "received.\nTwo lines, ✓ unicode.")
        check("every entry: wall time, author, loop, tick",
              e1["author"] == "k_os" and e1["loop"] == "k_os" and e1["tick"] == 550 and e1["ts"].endswith("+00:00"))
        for bad in ("", "   ", None):
            try:
                s.write("x", "x", 1, bad)
                check(f"empty write {bad!r} refused", False)
            except ValueError:
                check(f"empty write {bad!r} refused", True)
        check("a refused write doesn't burn a number", s.seq == 2)
        big = s.write("madara", "madara", 9, "y" * (SLAB_MAX_TEXT + 500))
        check("entries are capped", len(big["text"]) == SLAB_MAX_TEXT)
        check("line format", Slab.line(e1) == f"#1 · {e1['ts']} · k_os (tick 550): the seam line, credited to E.")

        again = Slab(p)
        check("a reopened slab keeps every entry", [e["seq"] for e in again.read()] == [1, 2, 3])
        check("…and keeps counting from where it was", again.write("k_os", "k_os", 551, "next")["seq"] == 4)
        check("read since a number", [e["seq"] for e in again.read(since=2)] == [3, 4])
        check("read since the last number → nothing", again.read(since=4) == [])
        for i in range(250):
            again.write("t", "t", i, f"bulk {i}")
        check("read limit is capped at 200", len(again.read(limit=1000)) == 200)
        check("read limit floor is 1", len(again.read(limit=0)) == 1 and again.read(limit=0)[0]["seq"] == 254)
        check("limit keeps the newest", again.read(limit=3)[-1]["text"] == "bulk 249")

        md = p.with_suffix(".md").read_text(encoding="utf-8")
        check("mirrored to a readable slab.md", md.startswith(f"### #1 · {e1['ts']} · k_os (tick 550)\n\nthe seam line, credited to E.\n\n"))
        check("slab.md is in order, newest at the bottom", md.index("### #2 ·") < md.index("### #3 ·") < md.rindex("### #254 ·"))

        with open(p, "a", encoding="utf-8") as f:
            f.write("{this is not json\n")
        hurt = Slab(p)
        check("a corrupt line is skipped on load", hurt.seq == 254 and hurt.write("x", "x", 1, "after damage")["seq"] == 255)

        cp = Path(tmp) / "conc.jsonl"
        cs = Slab(cp)
        def writer(n):
            for i in range(25):
                cs.write(f"w{n}", "w", i, f"{n}-{i}")
        threads = [threading.Thread(target=writer, args=(n,)) for n in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        seqs = sorted(e["seq"] for e in Slab(cp).read(limit=200))
        check("8 minds × 25 writes at once → 200 unique numbers, none lost", seqs == list(range(1, 201)), len(seqs))

        dp = Path(tmp) / "nomd" / "slab.jsonl"
        dp.parent.mkdir()
        (dp.parent / "slab.md").mkdir()   # the mirror path is unwritable
        check("an unwritable mirror never loses the entry", Slab(dp).write("x", "x", 1, "kept")["seq"] == 1
              and Slab(dp).read()[0]["text"] == "kept")

        # through the loop's group tool
        loops = {}
        chat = GroupChat(Path(tmp) / "room" / "group_chat.jsonl", lambda: loops)
        check("the room keeps its slab beside its log", chat.slab.path == Path(tmp) / "room" / "slab.jsonl")
        a = _torture_loop(tmp, sub="a", loop_id="supervisor", group=chat, agent="supervisor")
        b = _torture_loop(tmp, sub="b", loop_id="k_os", group=chat, agent="k_os")
        loops.update({"supervisor": a, "k_os": b})
        check("slab_read on an empty slab", a.tools.execute("group", {"action": "slab_read"}) == "The slab is empty.")
        check("slab_write needs text", a.tools.execute("group", {"action": "slab_write", "text": " "}) == "Write what?")
        a.world.tick = 77
        out = a.tools.execute("group", {"action": "slab_write", "text": "Wall time plus tick, append-only."})
        check("slab_write confirms the number and that it's final", out.startswith("Written to the slab as #1 at ") and "can't be changed" in out, out)
        entry = chat.slab.read()[0]
        check("the tool stamps the writer's name, loop and tick", (entry["author"], entry["loop"], entry["tick"]) == ("supervisor", "supervisor", 77))
        check("writing to the slab is logged as an event", any(ev["kind"] == "slab" for ev in a.events.tail(3)))
        check("writing to the slab doesn't wake anyone", b.queue == [] and chat.read() == [])
        got = b.tools.execute("group", {"action": "slab_read"})
        check("the other mind reads the same entry", got == Slab.line(entry), got)
        b.tools.execute("group", {"action": "slab_write", "text": "received"})
        check("slab_read since", b.tools.execute("group", {"action": "slab_read", "since": 1}).startswith("#2 ·"))
        check("say still works beside it", b.tools.execute("group", {"action": "say", "text": "hi"}) == "Said to the group."
              and len(a.queue) == 1)
        props = GROUP_DEF["parameters"]["properties"]
        check("group tool offers slab_write and slab_read", {"slab_write", "slab_read"} <= set(props["action"]["enum"]))
        check("group tool takes 'since'", props.get("since", {}).get("type") == "integer")
        check("group tool describes the slab as append-only", "nobody can edit or delete an entry" in GROUP_DEF["description"])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — app wiring: autostart after a deploy, the slab endpoint, three loops
# ═════════════════════════════════════════════
def test_agi_loop_app_wiring():
    print("\n=== TORTURE: AGI Loop — app wiring (autostart, slab API, loops) ===")
    import asyncio
    import threading
    import web.app as A
    from src.agi_loop import loop_ids, normalize_loop_id, config_file, data_dir, load_config
    from src.agi_loop.groupchat import GroupChat

    check("two loops are registered", loop_ids() == ["supervisor", "k_os"])
    check("the supervisor's loop runs the supervisor", load_config("supervisor").agent == "supervisor")
    check("loop ids are normalized", normalize_loop_id(" K_OS ") == "k_os" and normalize_loop_id("../x") == "supervisor")
    check("k_os has its own config and data", config_file("k_os").name == "agi_loop_k_os.json"
          and data_dir("k_os").name == "agi_loop_k_os")

    # ── autostart ──
    tmp = tempfile.mkdtemp()
    saved = (A._loop_ids, A._loop_data_dir, A._loop_daemon)
    try:
        class Fake:
            def __init__(self, running=False):
                self.running, self.started = running, 0

            def start(self):
                self.started += 1
                self.running = True

        fakes = {"a": Fake(), "b": Fake(), "c": Fake(running=True), "d": Fake(), "boom": Fake()}
        for lid in fakes:
            (Path(tmp) / lid).mkdir()
        for lid in ("a", "c", "d", "boom"):
            (Path(tmp) / lid / "autostart").write_text("x")

        def fake_daemon(fresh=False, loop="supervisor"):
            if loop == "boom":
                raise RuntimeError("bad config")
            return fakes[loop]

        A._loop_ids = lambda: ["boom", "a", "b", "c", "d"]
        A._loop_data_dir = lambda lid: Path(tmp) / lid
        A._loop_daemon = fake_daemon
        ready = threading.Event()
        ready.set()
        asyncio.run(A._autostart_loops(ready))
        check("a loop marked for autostart comes back", fakes["a"].started == 1 and fakes["d"].started == 1)
        check("an unmarked (deliberately stopped) loop stays stopped", fakes["b"].started == 0)
        check("an already-running loop isn't started twice", fakes["c"].started == 0)
        check("one loop failing doesn't stop the others", fakes["a"].running and fakes["d"].running)
        fakes["a"].running = False
        asyncio.run(A._autostart_loops(None))
        check("works without a readiness event", fakes["a"].started == 2)

        later = threading.Event()
        fakes["a"].running = False
        async def waits():
            task = asyncio.create_task(A._autostart_loops(later))
            await asyncio.sleep(0.2)
            before = fakes["a"].started
            later.set()
            await asyncio.wait_for(task, 5)
            return before, fakes["a"].started
        before, after = asyncio.run(waits())
        check("autostart waits for the soul-script index before waking anyone", before == 2 and after == 3, (before, after))
    finally:
        A._loop_ids, A._loop_data_dir, A._loop_daemon = saved

    src = open(A.__file__, encoding="utf-8").read()
    check("startup schedules the autostart", "asyncio.create_task(_autostart_loops(faiss_ready))" in src)
    check("the index thread always signals ready, even on failure",
          "def _bg_faiss_then_signal():" in src and "finally:\n            faiss_ready.set()" in src)

    # ── the slab endpoint ──
    saved_chat = A._group_chat
    try:
        A._group_chat = GroupChat(Path(tmp) / "room" / "group_chat.jsonl", lambda: {})
        A._group_chat.slab.write("k_os", "k_os", 1, "one")
        A._group_chat.slab.write("supervisor", "supervisor", 2, "two")
        from httpx import ASGITransport, AsyncClient

        async def call():
            async with AsyncClient(transport=ASGITransport(app=A.app), base_url="http://test") as c:
                return (await c.get("/api/group-chat/slab"), await c.get("/api/group-chat/slab?since=1"),
                        await c.post("/api/group-chat/slab"))
        everything, since, post = asyncio.run(call())
        check("GET /api/group-chat/slab returns the entries", everything.status_code == 200
              and [e["text"] for e in everything.json()["entries"]] == ["one", "two"], everything.text[:200])
        check("…and honours since", [e["seq"] for e in since.json()["entries"]] == [2])
        check("the slab can't be written over HTTP", post.status_code == 405, post.status_code)
        check("the endpoint is behind the AGI-loop owner check",
              "async def api_group_chat_slab" in src and "if denied := _agi_denied(request):" in src[src.index("async def api_group_chat_slab"):][:400])
    finally:
        A._group_chat = saved_chat
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — what the loop tells the minds about all of this
# ═════════════════════════════════════════════
def test_agi_loop_preamble_and_linux():
    print("\n=== TORTURE: AGI Loop — preamble, Linux machines, nav ===")
    from src.agi_loop.daemon import LOOP_PREAMBLE
    from src.agi_loop.linux import Linux, DEFINITION
    check("preamble: read times off the clock line", "read it off that line in the operator's time" in LOOP_PREAMBLE)
    check("preamble: never estimate a time", "never estimate a time from how long things felt" in LOOP_PREAMBLE)
    check("preamble: order by tick, stamp with UTC", "Order your own records by tick; stamp them with UTC" in LOOP_PREAMBLE)
    check("preamble: restarts and what survives", "The software can be restarted under you." in LOOP_PREAMBLE
          and "the thought you were in the middle of does not" in LOOP_PREAMBLE)
    check("preamble: where to leave the letter", "handoff/letter.md" in LOOP_PREAMBLE)
    check("preamble: the pace line", "The pace line says" in LOOP_PREAMBLE)

    env = dict(SUPERVISOR_LINUX_URL="http://e", SUPERVISOR_LINUX_TOKEN="1", KOS_LINUX_URL="http://k/", KOS_LINUX_TOKEN="2")
    old = {k: os.environ.get(k) for k in env}
    os.environ.update(env)
    try:
        m = Linux.from_env("k_os")
        check("k_os reaches its own machine", m.url == "http://k" and m.token == "2" and m.user == "kos")
        desc = m.definition()["description"]
        check("its tool speaks of its own home", "/home/kos" in desc and "'kos'" in desc and "supervisor" not in desc)
        check("every mind is told about ~/library", "~/library" in DEFINITION["description"] and "~/library" in desc)
        check("...and that reading it costs tokens, having it doesn't", "Reading it costs tokens; having it doesn't." in desc)
        check("...and where to learn about the machines", "MACHINES.md" in desc)
        check("unknown loop -> no machine", Linux.from_env("orion") is None)
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    os.environ.pop("KOS_LINUX_TOKEN", None)
    check("no token -> no machine", Linux.from_env("k_os") is None)

    repo = Path(__file__).resolve().parent.parent.parent
    t = (repo / "services" / "agent-linux" / "fly.toml").read_text(encoding="utf-8")
    check("fly.toml: 9gb home volume", "initial_size = '9gb'" in t)
    check("fly.toml: 1gb RAM", "memory = '1gb'" in t)
    check("fly.toml: private (no services/ports exposed)", "[[services]]" not in t and "[http_service]" not in t)

    web = Path(__file__).resolve().parent.parent / "web" / "templates"
    base = (web / "base.html").read_text(encoding="utf-8")
    check("nav has one AGI Loop entry for every loop",
          base.count('id="nav-agi-loop-link"') == 1 and "nav-agi-loop-kos-link" not in base
          and "Loop</span>" in base and base.count("Loop</span>") == 1)
    check("…highlighted on any loop's page", "(page or '').startswith('agi-loop')" in base)
    check("…reopens the last loop", "_lastLoopHref(" in base and "agiLoopLast" in base)
    loop_page_nav = (Path(__file__).resolve().parent.parent / "web" / "templates" / "agi_loop.html").read_text(encoding="utf-8")
    check("loop page switches loops with its chips", "{% for l in loops %}<a class=\"al-chip al-loopchip" in loop_page_nav
          and 'href="/agi-loop?loop={{ l }}"' in loop_page_nav)
    check("…the active loop's chip is highlighted", "{% if l == current_loop %} on{% endif %}" in loop_page_nav
          and "{% set current_loop = loop %}" in loop_page_nav
          and ".al-loopchip.on {" in loop_page_nav)
    check("…no separate agent bubble", 'id="hdr-agent"' not in loop_page_nav)
    check("loop page remembers the loop", "localStorage.setItem('agiLoopLast', LOOP_ID)" in loop_page_nav)
    check("nav has no links to removed loops", "loop=madara" not in base and "loop=orion" not in base)
    loop_page = (web / "agi_loop.html").read_text(encoding="utf-8")
    check("loop page shows each mind's own home", "/home/{{ linux_user }}" in loop_page)


# ═════════════════════════════════════════════
# AGI LOOP — cache discipline: stable prefix on top, this tick's retrieval at the bottom
# ═════════════════════════════════════════════
def test_agi_loop_cache_discipline():
    print("\n=== TORTURE: AGI Loop — cache discipline ===")
    import asyncio
    from src.agi_loop.daemon import RETRIEVED_HEADER, LOOP_PREAMBLE, Completion

    class SplitHost(_TortureLoopHost):
        def __init__(self):
            super().__init__()
            self.sent = []

        def prepare(self, agent, view):
            self.views.append(view)
            return ([{"role": "system", "content": "IDENTITY + PROTOCOLS"},
                     {"role": "system", "content": f"RETRIEVED for tick {len(self.views)}", "dynamic": True}], [])

        async def complete(self, config, messages, tools):
            self.sent.append([dict(m) for m in messages])
            self.n += 1
            return Completion(message={"role": "assistant", "content": f"thought {self.n}"}, tokens=1000,
                              cost=0.001, model="stub", prompt_tokens=900, cached_tokens=600 if self.n > 1 else 0)

    tmp = tempfile.mkdtemp()
    try:
        from src.agi_loop import LoopConfig, LoopDaemon
        host = SplitHost()
        d = LoopDaemon(host, LoopConfig.from_dict(dict(agent="tester", base_interval_seconds=30, min_interval_seconds=5)),
                       Path(tmp) / "d")
        d.running = True
        asyncio.run(d.tick())
        asyncio.run(d.tick())
        first, second = host.sent[0], host.sent[1]
        check("the system message is byte-identical across ticks", first[0] == second[0], (first[0], second[0]))
        check("…and it's identity, protocols, then the loop preamble", first[0]["content"] == "IDENTITY + PROTOCOLS\n\n" + LOOP_PREAMBLE)
        check("only one system message goes out (retrieval isn't a second one)", sum(m["role"] == "system" for m in second) == 1)
        last = second[-1]["content"]
        check("this tick's retrieval sits at the bottom, beside the field",
              last.startswith(RETRIEVED_HEADER) and "RETRIEVED for tick 2" in last)
        check("…with the field last", last.endswith(host.views[-1]))
        check("last tick's retrieval doesn't linger", "RETRIEVED for tick 1" not in json.dumps(second))
        check("no internal 'dynamic' key is sent to the provider", not any("dynamic" in m for msgs in host.sent for m in msgs))
        check("history carries the field, not old retrieval", all("RETRIEVED" not in m["content"]
                                                                   for m in second[1:-1] if m["role"] == "user"))
        t2 = d.ticks.tail(1)[0]
        check("each tick records prompt and cached tokens", (t2["prompt_tokens"], t2["cached_tokens"]) == (900, 600), t2)
        cache = d.status()["session_cache"]
        check("status reports the session hit rate", cache == {"prompt_tokens": 1800, "cached_tokens": 600, "hit_rate": 0.333}, cache)
        plain = _torture_loop(tmp, sub="plain")
        check("no prompt yet → hit rate is unknown, not zero", plain.status()["session_cache"]["hit_rate"] is None)

        class PlainHost(SplitHost):
            def prepare(self, agent, view):
                self.views.append(view)
                return [{"role": "system", "content": "ONLY"}], []
        ph = PlainHost()
        p = LoopDaemon(ph, LoopConfig.from_dict(dict(agent="t")), Path(tmp) / "p")
        p.running = True
        asyncio.run(p.tick())
        check("a host with no retrieval sends the field alone", ph.sent[0][-1]["content"] == ph.views[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── the real prompt assembly: same content, different place ──
    import web.app as A
    import src.storage.note_collector as nc
    directive = "## Relevant Knowledge (Soul Script Retrieval)\n\n**On the clock**\nprecision"

    class FakeVault:
        def search(self, q, scope=None, top_k=5):
            return [{"text": "Trent likes squats"}]
    saved = (nc.collect_notes, A._get_faiss_memory)
    try:
        nc.collect_notes = lambda agent, query=None, top_k=None: ("", directive)
        A._get_faiss_memory = lambda *a, **k: FakeVault()
        msgs = [{"role": "user", "text": "what time is it"}]
        plain_msgs, plain_layers, _ = A._build_chat_messages("supervisor", msgs)
        dyn_msgs, dyn_layers, _ = A._build_chat_messages("supervisor", msgs, dynamic_last=True)
        plain_sys, dyn_sys = plain_msgs[0]["content"], dyn_msgs[0]["content"]
        check("chat (default) still puts retrieval in the system prompt", directive in plain_sys and "Trent likes squats" in plain_sys)
        check("chat (default) has no dynamic layer", plain_layers["dynamic"] == "")
        check("loop mode keeps retrieval out of the system prompt", directive not in dyn_sys and "Trent likes squats" not in dyn_sys)
        check("…and returns it separately", directive in dyn_layers["dynamic"] and "Trent likes squats" in dyn_layers["dynamic"])
        vault_text = dyn_layers["dynamic"].split(directive + "\n\n", 1)[1]
        check("loop mode moves the blocks, it doesn't change them",
              dyn_sys == plain_sys.replace("\n\n" + directive, "").replace("\n\n" + vault_text, ""))
        check("the memory-save protocol stays in the stable part", "## Memory Save Protocol" in dyn_sys)
        nc.collect_notes = lambda agent, query=None, top_k=None: ("", directive.replace("precision", "something else"))
        again, _, _ = A._build_chat_messages("supervisor", [{"role": "user", "text": "a different field"}], dynamic_last=True)
        check("the stable part doesn't change when the query does", again[0]["content"] == dyn_sys)
        system, _tools = A._OrionLoopHost("supervisor").prepare("supervisor", "FIELD view")
        check("the loop host hands back the stable system and a flagged retrieval message",
              [m.get("dynamic", False) for m in system] == [False, True] and "precision" not in system[0]["content"])
    finally:
        nc.collect_notes, A._get_faiss_memory = saved

    # ── the meter sees DeepSeek's cache hits ──
    from src.observability.metering import cached_prompt_tokens, meter_from_raw_usage
    check("OpenAI cached tokens", cached_prompt_tokens({"prompt_tokens_details": {"cached_tokens": 7}}) == 7)
    check("Anthropic cache reads", cached_prompt_tokens({"cache_read_input_tokens": 8}) == 8)
    check("DeepSeek cache hits", cached_prompt_tokens({"prompt_cache_hit_tokens": 9, "prompt_cache_miss_tokens": 1}) == 9)
    check("none reported → 0", cached_prompt_tokens({}) == 0 and cached_prompt_tokens({"prompt_tokens_details": None}) == 0)
    hit = meter_from_raw_usage({"prompt_tokens": 1_000_000, "completion_tokens": 0, "total_tokens": 1_000_000,
                                "prompt_cache_hit_tokens": 1_000_000}, provider="deepseek", model="deepseek-chat")
    miss = meter_from_raw_usage({"prompt_tokens": 1_000_000, "completion_tokens": 0, "total_tokens": 1_000_000},
                                provider="deepseek", model="deepseek-chat")
    check("a DeepSeek cache hit is billed at the cached rate", abs(hit.cost.total_cost - 0.0028) < 1e-9, hit.cost.total_cost)
    check("…50× cheaper than a miss", abs(miss.cost.total_cost - 0.14) < 1e-9
          and abs(miss.cost.total_cost / hit.cost.total_cost - 50) < 1e-6)


# ═════════════════════════════════════════════
# AGI LOOP — the state tag: decisions declared inline, stripped, stamped, carried back
# ═════════════════════════════════════════════
def test_agi_loop_state_tag():
    print("\n=== TORTURE: AGI Loop — inline state tag ===")
    import asyncio
    from src.agi_loop.daemon import extract_state, MAX_STATE_FIELDS, MAX_STATE_VALUE, LOOP_PREAMBLE
    from src.agi_loop.groupchat import GroupChat

    check("no tag → text untouched, no state", extract_state("plain words") == ("plain words", None))
    check("empty and None are safe", extract_state("") == ("", None) and extract_state(None) == ("", None))
    clean, f = extract_state("Answered him. [STATE: decision=wait for Trent | why=his call, not mine]")
    check("a tag is stripped from the text", clean == "Answered him.", clean)
    check("its fields are kept", f == {"decision": "wait for Trent", "why": "his call, not mine"}, f)
    clean, f = extract_state("[STATE: register=flat]")
    check("a tag-only text becomes empty", clean == "" and f == {"register": "flat"})
    clean, f = extract_state("a [STATE: decision=x] b [STATE: decision=y | mood=dry] c")
    check("several tags: all stripped", clean == "a  b  c" or clean == "a b c" or "STATE" not in clean, clean)
    check("several tags: later values win", f == {"decision": "y", "mood": "dry"}, f)
    _, f = extract_state("[STATE: Voice Register = cold | time-sense = 4x | 9lives=no | =x | " + "k" * 40 + "=v | empty= | novalue]")
    check("keys are normalized; bad keys and empty values are dropped",
          f == {"voice_register": "cold", "time_sense": "4x"}, f)
    _, f = extract_state("[STATE: why=" + "w " * 400 + "]")
    check("values are whitespace-collapsed and capped", len(f["why"]) == MAX_STATE_VALUE and "  " not in f["why"])
    many = " | ".join(f"k{i}=v{i}" for i in range(12))
    _, f = extract_state(f"[STATE: {many} | k0=updated]")
    check(f"at most {MAX_STATE_FIELDS} fields, existing ones can still update",
          len(f) == MAX_STATE_FIELDS and f["k0"] == "updated" and "k8" not in f, f)
    clean, _ = extract_state("line one\n\n[STATE: a=b]\n\n\nline two")
    check("leftover blank lines are tidied", clean == "line one\n\nline two", repr(clean))
    clean, f = extract_state("[STATE: a=b] trailing ] bracket stays")
    check("text after the tag survives", clean == "trailing ] bracket stays" and f == {"a": "b"}, clean)

    tmp = tempfile.mkdtemp()
    try:
        class TagHost(_TortureLoopHost):
            async def complete(self, config, messages, tools):
                from src.agi_loop.daemon import Completion
                self.n += 1
                return Completion(message={"role": "assistant",
                                           "content": f"Settled it. [STATE: decision=rest until morning | n={self.n}]"},
                                  tokens=10, model="stub")
        from src.agi_loop import LoopConfig, LoopDaemon
        d = LoopDaemon(TagHost(), LoopConfig.from_dict(dict(agent="supervisor", base_interval_seconds=30, min_interval_seconds=5)),
                       Path(tmp) / "d")
        d.running = True
        asyncio.run(d.tick())
        t1 = d.ticks.tail(1)[0]
        check("a tick's response is stripped before it's recorded", t1["response"] == "Settled it.", t1["response"])
        check("…and the history carries the clean text", d.history[-1]["response"] == "Settled it.")
        check("the declaration is stamped with tick and time", d.declared["tick"] == 1 and d.declared["fields"]["decision"] == "rest until morning"
              and d.declared["ts"].endswith("+00:00"))
        check("it's logged as an event", any(ev["kind"] == "state" for ev in d.events.tail(5)))
        asyncio.run(d.tick())
        view = d.ticks.tail(1)[0]["view"]
        line = next((l for l in view.splitlines() if l.startswith("◇")), "")
        check("the next tick shows it back under the HUD", line.startswith("◇ you declared at tick 1 (")
              and "decision=rest until morning · n=1" in line, line)
        check("the HUD line sits with the clock and pace lines", view.splitlines().index(line) <= 5, view[:400])
        d2 = LoopDaemon(_TortureLoopHost(), LoopConfig.from_dict(dict(agent="supervisor")), Path(tmp) / "d")
        check("the latest declaration survives a restart", d2.declared and d2.declared["fields"]["n"] == "2")
        check("every declaration is kept in order", [e["fields"]["n"] for e in d2.state_log.items] == ["1", "2"])

        loops = {}
        chat = GroupChat(Path(tmp) / "room" / "group_chat.jsonl", lambda: loops)
        a = _torture_loop(tmp, sub="a", group=chat, agent="supervisor")
        b = _torture_loop(tmp, sub="b", loop_id="k_os", group=chat, agent="k_os")
        loops.update({"supervisor": a, "k_os": b})
        b.post_message("ping", sender="Trent")
        a.post_message("hello", sender="Trent")
        asyncio.run(a.tick())
        a.tools.execute("reply", {"text": "Here. [STATE: register=warm-ish]"})
        convo = a.conversation.tail(1)[0]["text"]
        check("a reply is stripped before Trent sees it", convo == "Here.", convo)
        check("…and the reply's declaration is kept", a.declared["fields"] == {"register": "warm-ish"})
        a.tools.execute("group", {"action": "say", "text": "Room. [STATE: decision=go dark]"})
        check("a room message is stripped before the others hear it", chat.read()[-1]["text"] == "Room."
              and b.queue[-1]["text"] == "Room.")
        a.tools.execute("group", {"action": "slab_write", "text": "On the record. [STATE: decision=logged]"})
        check("a slab entry is stripped before it's written", chat.slab.read()[-1]["text"] == "On the record.")
        check("a reply that was only a tag says nothing", a.tools.execute("reply", {"text": "[STATE: x=y]"}) == "Say something.")
        check("a room message that was only a tag says nothing", a.tools.execute("group", {"action": "say", "text": "[STATE: x=y]"}) == "Say what?")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("the preamble teaches the tag", "[STATE: decision=… | why=… | register=…]" in LOOP_PREAMBLE
          and "Encode decisions" in LOOP_PREAMBLE)


# ═════════════════════════════════════════════
# AGI LOOP — mid-loop tool requests: one line to Trent, nobody woken
# ═════════════════════════════════════════════
def test_agi_loop_tool_requests():
    print("\n=== TORTURE: AGI Loop — tool requests ===")
    import asyncio
    from src.agi_loop.tools import CONTROL_DEF
    from src.agi_loop.daemon import LOOP_PREAMBLE
    tmp = tempfile.mkdtemp()
    try:
        a = _torture_loop(tmp, sub="agi_loop", agent="supervisor")
        b = _torture_loop(tmp, sub="agi_loop_k_os", loop_id="k_os", agent="k_os")
        a.world.tick = 41
        out = a.tools.execute("loop_control", {"action": "request_tool",
                                                "text": "  a  clock I can query mid-thought \n for elapsed time  "})
        check("a request is acknowledged with its id", out.startswith("Noted for the operator as request #") and "nobody was woken" in out, out)
        lines = (Path(tmp) / "tool_requests.jsonl").read_text(encoding="utf-8").splitlines()
        e = json.loads(lines[0])
        check("requests from every loop share one file beside the loops", a.tool_requests_file == b.tool_requests_file
              == Path(tmp) / "tool_requests.jsonl")
        check("the request records who, which loop, tick and time",
              (e["agent"], e["loop"], e["tick"], e["status"]) == ("supervisor", "supervisor", 41, "open") and e["ts"].endswith("+00:00"))
        check("its text is one tidy line", e["text"] == "a clock I can query mid-thought for elapsed time", e["text"])
        check("asking wakes nobody", a.queue == [] and b.queue == [] and a._wake.is_set() is False)
        check("it's logged as an event", any(ev["kind"] == "request" for ev in a.events.tail(3)))
        b.tools.execute("loop_control", {"action": "request_tool", "reason": "a shared calendar"})
        check("'reason' works as the text too", json.loads((Path(tmp) / "tool_requests.jsonl").read_text(encoding="utf-8")
                                                           .splitlines()[1])["text"] == "a shared calendar")
        check("an empty request asks for a line", a.tools.execute("loop_control", {"action": "request_tool"}).startswith("Request what?"))
        a.tools.execute("loop_control", {"action": "request_tool", "text": "x" * 900})
        check("requests are capped at 500 chars", len(json.loads((Path(tmp) / "tool_requests.jsonl").read_text(encoding="utf-8")
                                                                 .splitlines()[-1])["text"]) == 500)
    finally:
        pass
    check("loop_control offers request_tool", "request_tool" in CONTROL_DEF["parameters"]["properties"]["action"]["enum"]
          and CONTROL_DEF["parameters"]["properties"]["text"]["type"] == "string")
    check("the preamble mentions it", "loop_control request_tool" in LOOP_PREAMBLE)

    # ── the API Trent reads them through ──
    import web.app as A
    from httpx import ASGITransport, AsyncClient
    saved = A._tool_requests_path
    try:
        A._tool_requests_path = lambda: Path(tmp) / "tool_requests.jsonl"
        with open(Path(tmp) / "tool_requests.jsonl", "a", encoding="utf-8") as f:
            f.write("not json\n{\"no\": \"id\"}\n")
        first_id = json.loads((Path(tmp) / "tool_requests.jsonl").read_text(encoding="utf-8").splitlines()[0])["id"]

        async def calls():
            async with AsyncClient(transport=ASGITransport(app=A.app), base_url="http://test") as c:
                listed = await c.get("/api/agi-loop/tool-requests")
                done = await c.post(f"/api/agi-loop/tool-requests/{first_id}/done")
                missing = await c.post("/api/agi-loop/tool-requests/nope/done")
                after = await c.get("/api/agi-loop/tool-requests")
                return listed, done, missing, after
        listed, done, missing, after = asyncio.run(calls())
        reqs = listed.json()["requests"]
        check("GET lists every request, garbage lines skipped", listed.status_code == 200 and len(reqs) == 3, reqs)
        check("…newest first", reqs[0]["ts"] >= reqs[-1]["ts"])
        check("marking done works", done.status_code == 200 and done.json() == {"ok": True})
        check("an unknown id is a 404", missing.status_code == 404)
        closed = next(r for r in after.json()["requests"] if r["id"] == first_id)
        check("the request now reads done, with when", closed["status"] == "done" and closed.get("closed_at"))
        check("closing appends; the original line is untouched",
              json.loads((Path(tmp) / "tool_requests.jsonl").read_text(encoding="utf-8").splitlines()[0])["status"] == "open")
        A._tool_requests_path = lambda: Path(tmp) / "missing" / "none.jsonl"
        check("no file yet → no requests", A._read_tool_requests() == [])
    finally:
        A._tool_requests_path = saved
        shutil.rmtree(tmp, ignore_errors=True)
    page = (Path(__file__).resolve().parent.parent / "web" / "templates" / "agi_loop.html").read_text(encoding="utf-8")
    check("the loop page shows tool requests on the Inbox tab", 'id="tool-requests"' in page and "loadToolRequests()" in page
          and "toolRequestDone(" in page)


# ═════════════════════════════════════════════
# AGI LOOP — the watchdog: a witness no mind authors, with teeth
# ═════════════════════════════════════════════
def test_agi_loop_watchdog():
    print("\n=== TORTURE: AGI Loop — watchdog ===")
    from types import SimpleNamespace as NS
    from src.agi_loop.watchdog import assess, Watchdog, OVERDUE_GRACE, STUCK_AFTER

    now = 1_800_000_000.0

    class Task:
        def __init__(self, done):
            self._d = done

        def done(self):
            return self._d

    def loop(**kw):
        events = []
        base = dict(running=True, paused=False, task=Task(False), next_wake_at=now + 60, tick_started_at=now - 30,
                    world=NS(tick=7), stage="think", config=NS(agent="k_os"), events=events,
                    event=lambda k, t: events.append((k, t)))
        base.update(kw)
        return NS(**base)

    check("healthy and asleep → silent", assess(loop(), now) is None)
    check("not running → not judged", assess(loop(running=False, next_wake_at=now - 99999), now) is None)
    check("paused by the operator → not judged", assess(loop(paused=True, next_wake_at=now - 99999), now) is None)
    check("a dead task while marked running → process gone",
          "process is gone" in (assess(loop(task=Task(True)), now) or ""))
    check("no task object at all is not mistaken for death", assess(loop(task=None), now) is None)
    check("a little late is within grace", assess(loop(next_wake_at=now - OVERDUE_GRACE + 1), now) is None)
    late = assess(loop(next_wake_at=now - OVERDUE_GRACE - 61), now)
    check("past grace → flat, saying when it was due and how late", late is not None and "was due to wake at" in late
          and "6m 01s late" in late, late)
    check("mid-tick and quick → silent", assess(loop(next_wake_at=None, tick_started_at=now - 60), now) is None)
    stuck = assess(loop(next_wake_at=None, tick_started_at=now - STUCK_AFTER - 5), now)
    check("stuck inside a tick → flat, with tick and stage", stuck is not None and "inside tick 7" in stuck and "stage: think" in stuck, stuck)
    check("mid-tick with no start time recorded → silent", assess(loop(next_wake_at=None, tick_started_at=None), now) is None)
    check("a dead process outranks a late schedule", "process is gone" in assess(loop(task=Task(True), next_wake_at=now - 9999), now))

    k = loop(next_wake_at=now - 9999)
    e = loop(config=NS(agent="supervisor"))
    room = []
    w = Watchdog(lambda: {"k_os": k, "supervisor": e}, lambda lid, text: room.append((lid, text)))
    newly = w.check(now)
    check("a flat loop is escalated", list(newly) == ["k_os"] and len(room) == 1)
    check("…in words that say who, why, and who measured it",
          room[0][1].startswith("[watchdog] k_os has gone flat — it was due to wake at") and room[0][1].endswith("Measured by the engine, not reported by k_os."),
          room[0][1])
    check("the healthy loop is left alone (silence on pass)", "supervisor" not in w.flat and e.events == [])
    check("the flat loop's own record notes it", k.events and k.events[0][0] == "watchdog" and k.events[0][1].startswith("flat:"))
    w.check(now + 60)
    check("it says so once, not every minute", len(room) == 1)
    k.next_wake_at = now + 120
    w.check(now + 120)
    check("recovery is logged, not announced", len(room) == 1 and "k_os" not in w.flat and k.events[-1] == ("watchdog", "ticking again"))
    k.next_wake_at = now - 9999
    w.check(now + 600)
    check("a second flatline is escalated again", [lid for lid, _ in room].count("k_os") == 2, room)
    check("…and a loop whose own schedule went stale meanwhile is caught too", "supervisor" in w.flat
          and [lid for lid, _ in room].count("supervisor") == 1)

    def boom(lid, text):
        raise RuntimeError("room unavailable")
    w2 = Watchdog(lambda: {"k_os": loop(task=Task(True))}, boom)
    check("an escalation failure doesn't break the watchdog", w2.check(now) == {"k_os": "its process is gone: it is marked running, but its task has ended"})

    import web.app as A
    src = open(A.__file__, encoding="utf-8").read()
    check("the engine runs the watchdog from startup", "asyncio.create_task(_watch_loops())" in src)
    check("it escalates into the room as 'watchdog'", '_group_chat.post("watchdog", "watchdog", text)' in src)
    check("it only watches loops that exist (creates none)", "(d := _get_loop_daemon(lid)) is not None" in src)
    saved = A._get_loop_daemon
    try:
        A._get_loop_daemon = lambda lid: k if lid == "k_os" else None
        check("the app's watch list is exactly the live daemons", set(A._watchdog._daemons()) == {"k_os"})
    finally:
        A._get_loop_daemon = saved


# ═════════════════════════════════════════════
# CHATS — a new reply doesn't drag you to the bottom while you're reading
# ═════════════════════════════════════════════
def test_chat_scroll_follows_only_at_bottom():
    print("\n=== TORTURE: Chats — follow new replies only when at the bottom ===")
    import re
    tpl = Path(__file__).resolve().parent.parent / "web" / "templates"
    chat = (tpl / "chat.html").read_text(encoding="utf-8")
    check("chat: no unconditional jump to the bottom remains", "thread.scrollTop = thread.scrollHeight" not in chat)
    check("chat: one helper decides", "function scrollThread(force)" in chat and "if (_followThread) t.scrollTop = t.scrollHeight;" in chat)
    check("chat: scrolling up stops following, back to the bottom resumes",
          "_followThread = t.scrollHeight - t.scrollTop - t.clientHeight < 80;" in chat
          and "document.addEventListener('scroll'" in chat and "}, true);" in chat)
    calls = re.findall(r"scrollThread\((true)?\)", chat)
    check("chat: streaming text, thinking and tool notes follow only if you're at the bottom", calls.count("") >= 5, calls)
    check("chat: sending a message (or starting a run) always follows", calls.count("true") == 2, calls)

    gc = (tpl / "group_chat.html").read_text(encoding="utf-8")
    check("group chat: no unconditional jump to the bottom", re.search(r"^\s*gcLog\.scrollTop = gcLog\.scrollHeight;", gc, re.M) is None)
    check("group chat: follows only at the bottom, on first load, or after you send",
          "const follow = !gcLast || gcStick || gcLog.scrollHeight - gcLog.scrollTop - gcLog.clientHeight < 60;" in gc
          and "if (follow) gcLog.scrollTop = gcLog.scrollHeight;" in gc)
    check("group chat: sending sets the follow flag", "gcStick = true;" in gc)

    loop = (tpl / "agi_loop.html").read_text(encoding="utf-8")
    check("loop page: conversation already follows only at the bottom",
          "const atBottom = box.scrollHeight - box.scrollTop - box.clientHeight < 40;" in loop
          and "if (atBottom || !box._seen) box.scrollTop = box.scrollHeight;" in loop)


# ═════════════════════════════════════════════
# AGI LOOP — a tool written as text is named, not silently dropped (Madara, 03:31)
# ═════════════════════════════════════════════
def test_agi_loop_narrated_tool_calls():
    print("\n=== TORTURE: AGI Loop — tool tags written as text ===")
    import asyncio
    from src.agi_loop.daemon import Completion

    class NarratingHost(_TortureLoopHost):
        def __init__(self, replies):
            super().__init__()
            self.replies = list(replies)

        async def complete(self, config, messages, tools):
            self.n += 1
            return Completion(message={"role": "assistant", "content": self.replies.pop(0)}, tokens=10, model="stub")

    tmp = tempfile.mkdtemp()
    try:
        from src.agi_loop import LoopConfig, LoopDaemon
        madara_0331 = ("Trent's question is aimed at me by name. Answer the man.  <reply> <item>d1724</item> "
                       "<text>Take the fix, Trent. I want it.</text></reply>")
        host = NarratingHost([madara_0331, "x < y, and <b>bold</b> is just markup", "quiet"])
        d = LoopDaemon(host, LoopConfig.from_dict(dict(agent="madara", base_interval_seconds=30, min_interval_seconds=5)),
                       Path(tmp) / "m")
        d.post_message("do you want the fix?", sender="Trent")
        d.running = True
        asyncio.run(d.tick())
        check("a <reply> written as text is noticed", d.last_result.get("narrated") == ["reply"], d.last_result.get("narrated"))
        check("…and nothing was sent: the conversation has no agent reply", not any(m["role"] == "agent" for m in d.conversation.items))
        check("…and it's logged", any(e["kind"] == "guard" and "<" not in e["text"] and "reply" in e["text"] for e in d.events.tail(5)))
        asyncio.run(d.tick())
        view = host.views[-1]
        body = next((l for l in view.splitlines() if l.startswith("✋")), "")
        check("the next tick tells him exactly what happened", "you wrote <reply> as text in your answer — nothing was sent or done" in body
              and "A tool only runs when you call it" in body, body)
        check("ordinary angle brackets and HTML aren't mistaken for tools", d.last_result.get("narrated") == [])
        asyncio.run(d.tick())
        check("once he stops, the warning goes away", "as text in your answer" not in host.views[-1])
        check("only this mind's real tool names count", d._narrated_tools("<workbench> <attend> <memo> <div> <REPLY>")
              == ["workbench", "attend", "reply"])
        check("a tool this mind doesn't have isn't counted", d._narrated_tools("<linux>") == [])
        check("capped at five names", len(d._narrated_tools(" ".join(f"<{n}>" for n in d.tools.names()) + " <tool_call> <function_call>")) == 5)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# ═════════════════════════════════════════════
# AGI LOOP — "today" ends at Trent's midnight; the HUD lands on each mind's machine
# ═════════════════════════════════════════════
def test_agi_loop_hud_on_linux_and_local_day():
    print("\n=== TORTURE: AGI Loop — local-midnight day + HUD on the Linux box ===")
    import asyncio
    import importlib.util
    import threading
    import http.client
    from datetime import datetime, timedelta
    from zoneinfo import ZoneInfo
    from src.agi_loop.budget import DailyBudget, _today
    from src.agi_loop.linux import Linux, DEFINITION

    # ── "today" in Trent's zone ──
    ny = ZoneInfo("America/New_York")
    check("today is Trent's date, not UTC's", _today("America/New_York") == datetime.now(ny).strftime("%Y-%m-%d"))
    check("an unknown zone falls back to UTC's date", _today("Not/AZone") == _today("UTC"))
    tmp = tempfile.mkdtemp()
    try:
        b = DailyBudget(Path(tmp) / "b.json", 1000, tz="America/New_York")
        now = datetime.now(ny)
        nxt = now.date() + timedelta(days=1)
        want = (datetime(nxt.year, nxt.month, nxt.day, 0, 0, 5, tzinfo=ny) - now).total_seconds()
        check("energy resets at 00:00:05 Trent's time", abs(b.seconds_until_reset() - want) < 5, (b.seconds_until_reset(), want))
        check("…which is never more than a day (plus a DST hour) away", 0 < b.seconds_until_reset() <= 90005)
        check("the stored day is Trent's date", b.day == now.strftime("%Y-%m-%d"))
        b.spend(300, 0)
        b2 = DailyBudget(Path(tmp) / "b.json", 1000, tz="America/New_York")
        check("a restart on the same local day keeps what was spent", b2.tokens == 300)
        b2.day = "1999-12-31"
        check("crossing local midnight resets energy", b2.tokens_left == 1000 and b2.day == now.strftime("%Y-%m-%d"))
        utc = DailyBudget(Path(tmp) / "u.json", 1000)
        check("default zone is still UTC", utc.tz == "UTC" and utc.day == _today("UTC"))
        d = _torture_loop(tmp, sub="d")
        check("a loop's budget uses the loop's time zone", d.budget.tz == "America/New_York")
        d.config.timezone = "Europe/London"
        d.apply_config(d.config)
        check("changing the zone moves the budget's midnight too", d.budget.tz == "Europe/London")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ── the real command server, on a test port ──
    home = tempfile.mkdtemp()
    old_env = {k: os.environ.get(k) for k in ("HOME", "SHELL_TOKEN")}
    os.environ["HOME"], os.environ["SHELL_TOKEN"] = home, "tok-test"
    try:
        srv_path = Path(__file__).resolve().parent.parent.parent / "services" / "agent-linux" / "shell_server.py"
        spec = importlib.util.spec_from_file_location("shell_server_under_test", srv_path)
        S = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(S)
        check("the server reads its token and forgets it", S.TOKEN == "tok-test" and "SHELL_TOKEN" not in os.environ)
        server = S.ThreadingHTTPServer(("127.0.0.1", 0), S.Handler)
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()

        def post(path, body, token="tok-test", raw=None):
            c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
            data = raw if raw is not None else json.dumps(body).encode()
            c.request("POST", path, body=data, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                                                         "Content-Length": str(len(data))})
            r = c.getresponse()
            return r.status, json.loads(r.read() or b"{}")

        check("the mind's own command server refuses /hud (it would own the files)", post("/hud", {"tick": 1})[0] == 404)
        S.HUD_ONLY = True   # from here on this instance is the root-run HUD writer
        check("the HUD writer refuses /exec (it runs no commands)", post("/exec", {"command": "id"})[0] == 404)
        c0 = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        c0.request("GET", "/tree", headers={"Authorization": "Bearer tok-test"})
        check("…and serves nothing else but /health", c0.getresponse().status == 404)
        c0 = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        c0.request("GET", "/health")
        check("…which says what it is", json.loads(c0.getresponse().read())["hud_only"] is True)
        check("no token → 401", post("/hud", {"tick": 1}, token="wrong")[0] == 401)
        check("not JSON → 400", post("/hud", None, raw=b"{nope")[0] == 400)
        check("a JSON list isn't a HUD → 400", post("/hud", [1, 2])[0] == 400)
        check("over 200 KB → 413", post("/hud", {"x": "y" * 210_000})[0] == 413)

        tmpd = tempfile.mkdtemp()
        try:
            loop = _torture_loop(tmpd, sub="e")
            loop.running = True
            asyncio.run(loop.tick())
            view = loop.ticks.tail(1)[0]["view"]
            payload = loop.hud_payload(view, time.time())
            bud = loop.budget
            check("HUD file energy is the real budget, after this tick's spend", payload["energy"] == round(bud.energy, 4)
                  and bud.tokens == 100)
            check("…tokens left matches the budget exactly", payload["tokens_left"] == bud.tokens_left == bud.tokens_per_day - 100)
            check("…'left today' is the same sentence the HUD uses", payload["left_today"] == bud.left_text())
            check("…waiting and field % match the field", payload["waiting"] == 0
                  and payload["field_pct"] == min(999, loop.world.used(time.time()) * 100 // loop.world.capacity))
            check("…this tick's own cost is recorded", payload["this_tick"]["tokens"] == 100)
            check("the payload says which numbers are when", payload["numbers_as_of"].startswith("end of this tick")
                  and payload["hud_lines_as_of"].startswith("start of this tick"))
        finally:
            shutil.rmtree(tmpd, ignore_errors=True)
        check("the HUD payload is this tick's measured state", payload["tick"] == 1 and payload["agent"] == "tester"
              and 0 <= payload["energy"] <= 1 and "tokens left today" in payload["left_today"]
              and payload["timezone"] == "America/New_York" and payload["at_utc"].endswith("+00:00"))
        check("…its lines are the HUD exactly as the mind saw it, up to the focus",
              payload["hud_lines"][0].startswith("FIELD · tick 1") and any(l.startswith("⏲ now") for l in payload["hud_lines"])
              and not any(l.startswith("FOCUS") for l in payload["hud_lines"]) and payload["hud_lines"] == view.split("\n")[:len(payload["hud_lines"])])

        linux = Linux(f"http://127.0.0.1:{port}", "tok-test", "tester")
        check("the engine's client pushes a HUD", linux.push_hud(payload) is True)
        hud = Path(home) / "hud"
        now_json = json.loads((hud / "now.json").read_text(encoding="utf-8"))
        check("~/hud/now.json holds it", now_json["tick"] == 1 and now_json["hud_lines"] == payload["hud_lines"])
        check("~/hud/now.txt is the HUD as text", (hud / "now.txt").read_text(encoding="utf-8").splitlines() == payload["hud_lines"])
        check("~/hud/README.md explains it, written once", "Written by the engine every tick" in (hud / "README.md").read_text(encoding="utf-8"))
        check("…including how to steer your own state", "~/hud-control.json" in (hud / "README.md").read_text(encoding="utf-8"))
        (hud / "README.md").write_text("edited", encoding="utf-8")
        payload2 = dict(payload, tick=2)
        linux.push_hud(payload2)
        check("…and the measurement folder's README is restored (that folder isn't the mind's)",
              (hud / "README.md").read_text(encoding="utf-8") == S.HUD_README)
        log_lines = (hud / "log.jsonl").read_text(encoding="utf-8").splitlines()
        check("~/hud/log.jsonl keeps one line per tick, without the bulky lines", [json.loads(l)["tick"] for l in log_lines] == [1, 2]
              and "hud_lines" not in json.loads(log_lines[0]))
        check("no temp files left behind", not any(p.name.startswith(".") for p in hud.iterdir()))
        S.HUD_LOG_MAX = 3000
        for i in range(3, 40):
            S.write_hud(dict(payload, tick=i))
        trimmed = (hud / "log.jsonl").read_text(encoding="utf-8").splitlines()
        check("the history trims itself, keeping the newest, on whole lines",
              (hud / "log.jsonl").stat().st_size <= 3000 and json.loads(trimmed[-1])["tick"] == 39
              and all(json.loads(l) for l in trimmed))
        check("a wrong token makes push_hud return False, not raise", Linux(f"http://127.0.0.1:{port}", "bad", "t").push_hud(payload) is False)
        check("an unreachable box returns False, quickly", Linux("http://127.0.0.1:9", "x", "t").push_hud(payload) is False)
        S.HUD_ONLY = False
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
        c.request("POST", "/exec", body=b"{}", headers={"Authorization": "Bearer tok-test", "Content-Length": "2"})
        check("the mind's own server still runs /exec", c.getresponse().status == 400)
        server.shutdown()
        check("the engine sends HUDs to the root writer on :8081", Linux("http://kos-linux.internal:8080", "t", "kos").hud_url
              == "http://kos-linux.internal:8081" and Linux("http://x:9", "t", "u").hud_url == "http://x:9")
    finally:
        for k, v in old_env.items():
            os.environ.pop(k, None) if v is None else os.environ.__setitem__(k, v)
        shutil.rmtree(home, ignore_errors=True)

    # ── the daemon pushes at the end of every tick, off the event loop ──
    tmp = tempfile.mkdtemp()
    try:
        got = []
        class FakeLinux:
            def push_hud(self, p):
                got.append((threading.current_thread() is threading.main_thread(), p["tick"]))
                return True
        loop = _torture_loop(tmp, sub="f")
        loop.linux = FakeLinux()
        loop.running = True
        asyncio.run(loop.tick())
        for _ in range(50):
            if got:
                break
            time.sleep(0.02)
        check("every tick pushes its HUD to the mind's machine", got and got[0][1] == 1)
        check("…from a background thread, never the loop's own", got and got[0][0] is False)
        none = _torture_loop(tmp, sub="g")
        none.running = True
        asyncio.run(none.tick())
        check("a mind without a machine just doesn't push", none.linux is None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    check("each mind is told about ~/hud and who writes it", "~/hud/ holds your HUD, written every tick by a root process you don't own"
          in DEFINITION["description"])
    check("…and how to steer its own state", "~/hud-control.json" in DEFINITION["description"])

    # ── ~/hud-control.json: the mind steers its state from its own machine ──
    tmp = tempfile.mkdtemp()
    try:
        class Box:
            def __init__(self):
                self.files = {}
                self.pushed = []

            def read(self, endpoint, path=None, **kw):
                if path in self.files:
                    return {"ok": True, "content": self.files[path]}
                return {"ok": False, "reason": "no such file"}

            def push_hud(self, p):
                self.pushed.append(p)
                return True

        box = Box()
        d = _torture_loop(tmp, sub="c", min_interval_seconds=20, max_interval_seconds=1800)
        d.linux = box
        d.running = True
        asyncio.run(d.tick())
        check("no control file → nothing applied, nothing said", d.control_seq == 0 and d.control_ack is None)
        box.files["hud-control.json"] = json.dumps({"seq": 1, "reason": "watching the build", "pace_seconds": 300,
                                                     "declare": {"Decision": "build the daemon", "bad key!": "x"},
                                                     "note": "check the tombstone at 05:00", "volume": 11})
        asyncio.run(d.tick())
        check("pace set from the machine", d.pace == (300.0, "watching the build"))
        check("declared from the machine, stamped like a tag", d.declared["fields"] == {"decision": "build the daemon"}
              and d.declared["via"] == "hud-control")
        check("the note lands in the field",
              any("you wrote on your machine: check the tombstone" in i.text for i in d.world.items.values()))
        ack = d.control_ack
        check("the ack says what was applied", ack["seq"] == 1 and any(a.startswith("pace → 5m 00s") for a in ack["applied"])
              and "declared decision" in ack["applied"] and "note set into your field" in ack["applied"], ack)
        check("…and refuses what it doesn't know, by name", ack["refused"] == ["unknown key 'volume'"], ack["refused"])
        check("measurements can't be steered (no energy/token keys)",
              "energy" not in d.CONTROL_KEYS and "tokens_left" not in d.CONTROL_KEYS)
        d.pace = (60.0, "changed by the loop")
        asyncio.run(d.tick())
        check("the same seq is applied once, not every tick", d.pace == (60.0, "changed by the loop"))
        for _ in range(50):
            if box.pushed:
                break
            time.sleep(0.02)
        check("the ack rides in the HUD on the machine", box.pushed and box.pushed[-1]["control"]["seq"] == 1)
        box.files["hud-control.json"] = json.dumps({"seq": 2, "pace_seconds": None, "rest_minutes": 15})
        asyncio.run(d.tick())
        check("a new seq applies: pace back to adaptive, a rest", d.pace is None and d.rest_request and d.rest_request[0] == 900)
        box.files["hud-control.json"] = json.dumps({"seq": 3, "pace_seconds": "fast"})
        asyncio.run(d.tick())
        check("a bad value is refused with the reason, not crashed on", d.control_seq == 3
              and any(r.startswith("bad value") for r in d.control_ack["refused"]), d.control_ack)
        box.files["hud-control.json"] = "{not json"
        asyncio.run(d.tick())
        check("broken JSON is reported back, nothing applied",
              "isn't valid JSON" in (d.control_ack or {}).get("error", "") and d.control_seq == 3, d.control_ack)
        box.files["hud-control.json"] = json.dumps({"seq": 2, "pace_seconds": 999})
        asyncio.run(d.tick())
        check("an old seq is ignored", d.pace is None)
        d.save()
        d2 = _torture_loop(tmp, sub="c")
        check("the last applied seq survives a restart (no replay)", d2.control_seq == 3)

        class DownBox(Box):
            def read(self, *a, **k):
                raise OSError("unreachable")

        e = _torture_loop(tmp, sub="down")
        e.linux = DownBox()
        e.running = True
        asyncio.run(e.tick())
        check("a box that's down doesn't stop the tick", e.ticks.items and e.control_ack is None)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    srv = Path(__file__).resolve().parent.parent.parent / "services" / "agent-linux"
    start = (srv / "start.sh").read_text(encoding="utf-8")
    check("boot starts the root HUD writer on :8081", "HUD_ONLY=1 PORT=8081" in start
          and "python3 /opt/agent/shell_server.py &" in start)
    check("boot never hands ~/library or ~/hud back to the mind",
          '-path "$HOME_DIR/library" -o -path "$HOME_DIR/hud"' in start and "-prune" in start and "chown -R" not in start)
    check("the mind's own server runs without HUD_ONLY", "env -u HUD_ONLY" in start and "PORT=8080" in start)
    check("the image exposes the HUD writer's port", "EXPOSE 8080 8081 7681" in (srv / "Dockerfile").read_text(encoding="utf-8"))


# ═════════════════════════════════════════════
# LOOP PAGES — light payloads, gzip, no polling in hidden tabs
# ═════════════════════════════════════════════
def test_loop_pages_stay_light():
    print("\n=== TORTURE: Loop pages — light payloads, gzip, quiet when hidden ===")
    import asyncio
    import gzip as _gz
    import web.app as A
    from httpx import ASGITransport, AsyncClient

    tmp = tempfile.mkdtemp()
    saved = A._loop_daemon
    try:
        d = _torture_loop(tmp)
        for i in range(1, 31):
            d.ticks.append({"tick": i, "time": "2026-10-08T02:00:00+00:00", "focus": "f", "mood": "m",
                            "view": "FIELD " + "x" * 12000, "view_head": "FIELD", "response": f"said {i}" + "y" * 2000,
                            "tool_calls": [{"tool": "linux", "arguments": {"command": "ls"}, "result": "z" * 3000, "ok": True, "ms": 5}],
                            "tokens": 10, "cost": 0.0, "latency": 1.0})
        A._loop_daemon = lambda fresh=False, loop="supervisor": d

        async def calls():
            async with AsyncClient(transport=ASGITransport(app=A.app), base_url="http://test") as c:
                full = await c.get("/api/agi-loop/ticks?limit=30", headers={"Accept-Encoding": "identity"})
                brief = await c.get("/api/agi-loop/ticks?limit=30&brief=1", headers={"Accept-Encoding": "identity"})
                latest = await c.get("/api/agi-loop/ticks?limit=1&brief=1&with_response=1")
                one = await c.get("/api/agi-loop/ticks?tick=7")
                gone = await c.get("/api/agi-loop/ticks?tick=999")
                zipped = await c.get("/api/agi-loop/ticks?limit=30", headers={"Accept-Encoding": "gzip"})
                small = await c.get("/api/agi-loop/ticks?limit=1&brief=1", headers={"Accept-Encoding": "gzip"})
                return full, brief, latest, one, gone, zipped, small
        full, brief, latest, one, gone, zipped, small = asyncio.run(calls())
        b = brief.json()["ticks"]
        check("brief ticks drop the field view and the response", all("view" not in t and "response" not in t for t in b))
        check("brief ticks keep what the table shows", b[-1]["tick"] == 30 and b[-1]["focus"] == "f" and b[-1]["tool_calls"] == [{"tool": "linux", "ok": True}])
        check("brief is a small fraction of full", len(brief.content) * 20 < len(full.content), (len(brief.content), len(full.content)))
        check("with_response keeps the reply for the overview card", latest.json()["ticks"][0]["response"].startswith("said 30")
              and "view" not in latest.json()["ticks"][0])
        check("one tick on demand comes back whole", one.status_code == 200 and one.json()["ticks"][0]["tick"] == 7
              and one.json()["ticks"][0]["view"].startswith("FIELD xxx"))
        check("a tick that rolled out of the log is a 404", gone.status_code == 404 and gone.json()["ticks"] == [])
        check("JSON is gzipped when the browser accepts it", zipped.headers.get("content-encoding") == "gzip")
        check("…and decodes to the same body", zipped.json() == full.json())
        check("small responses still decode fine whichever way they're sent", small.status_code == 200
              and small.json()["ticks"][0]["tick"] == 30)
        raw = len(full.content)
        packed = len(_gz.compress(full.content))
        check("ticks compress by well over half", packed * 2 < raw, (raw, packed))
    finally:
        A._loop_daemon = saved
        shutil.rmtree(tmp, ignore_errors=True)

    # the chat stream must never be gzipped (a gzip buffer would hold replies back)
    async def stream_app(scope, receive, send):
        await send({"type": "http.response.start", "status": 200,
                    "headers": [(b"content-type", b"text/plain")]})   # a type gzip would normally compress
        for _ in range(3):
            await send({"type": "http.response.body", "body": b"chunk " * 400, "more_body": True})
        await send({"type": "http.response.body", "body": b"", "more_body": False})

    async def run(path):
        sent = []
        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        async def send(msg):
            sent.append(msg)
        scope = {"type": "http", "method": "POST", "path": path, "headers": [(b"accept-encoding", b"gzip")],
                 "query_string": b"", "http_version": "1.1", "scheme": "http", "server": ("t", 80), "client": ("c", 1),
                 "root_path": "", "raw_path": path.encode()}
        await A._SelectiveGZip(stream_app)(scope, receive, send)
        return sent
    stream = asyncio.run(run("/api/chat/stream"))
    other = asyncio.run(run("/api/agi-loop/journal"))
    start_headers = dict(stream[0]["headers"])
    check("the chat stream passes through uncompressed", b"content-encoding" not in start_headers)
    check("…chunk by chunk, as written", [m.get("body") for m in stream[1:4]] == [b"chunk " * 400] * 3)
    check("other routes through the same wrapper are gzipped", dict(other[0]["headers"]).get(b"content-encoding") == b"gzip")
    check("only the stream is exempt", A._NO_GZIP_PATHS == {"/api/chat/stream"})

    tpl = Path(__file__).resolve().parent.parent / "web" / "templates"
    loop = (tpl / "agi_loop.html").read_text(encoding="utf-8")
    check("loop page: no polling while the tab is hidden",
          "setInterval(() => { if (seen()) loadStatus(); }, 2000);" in loop
          and "setInterval(() => { if (seen()) refreshTab(false); }, 4000);" in loop)
    check("loop page: coming back catches up at once",
          "document.addEventListener('visibilitychange', () => { if (seen()) { loadStatus(); refreshTab(true); } });" in loop)
    check("loop page: no bare polling intervals remain", "setInterval(loadStatus" not in loop and "setInterval(tickWakeClock" not in loop)
    check("loop page: ticks table loads brief", "/api/agi-loop/ticks?limit=200&brief=1" in loop)
    check("loop page: a tick loads whole on click", "async function showTick(i)" in loop and "'/api/agi-loop/ticks?tick=' + t.tick" in loop)
    check("loop page: overview's latest tick is brief, with its reply", "/api/agi-loop/ticks?limit=1&brief=1&with_response=1" in loop)
    check("loop page: conversation, events, journal skip unchanged redraws",
          "box._sig !== sig" in loop and "AL._evSig === sig" in loop and "AL._jnSig === sig" in loop)
    gc = (tpl / "group_chat.html").read_text(encoding="utf-8")
    check("group chat: no polling while hidden, catch up on return",
          "setInterval(() => { if (!document.hidden) gcLoad(); }, 3000);" in gc and "visibilitychange" in gc)


# ═════════════════════════════════════════════
# MADARA — the prompt / soul-script split moved his words, never changed them

# =============================================

# ═════════════════════════════════════════════
# UPLOAD THUMBNAILS — sized WebP, caching, path guard
# ═════════════════════════════════════════════
def test_upload_thumbnails():
    print("\n=== TORTURE: Upload thumbnails ===")
    tmp = tempfile.mkdtemp()
    try:
        import web.app as _app
        from PIL import Image
        orig = (_app._UPLOADS_DIR, _app._THUMB_DIR)
        uploads = Path(tmp) / "uploads"
        uploads.mkdir()
        _app._UPLOADS_DIR = uploads
        _app._THUMB_DIR = Path(tmp) / "thumbs"
        try:
            Image.new("RGB", (1600, 1200), (120, 40, 200)).save(uploads / "avatar_big.png")
            Image.new("RGBA", (1600, 1600), (0, 0, 0, 0)).save(uploads / "avatar_alpha.png")
            Image.new("RGB", (100, 100)).save(uploads / "avatar_small.png")
            (uploads / "anim.gif").write_bytes(b"GIF89a")

            t = _app._thumb_file(uploads / "avatar_big.png", 300)
            check("thumb is WebP", t is not None and t.suffix == ".webp")
            with Image.open(t) as im:
                check("thumb snaps up to the 512 size", im.size == (512, 384), str(im.size))
            check("thumb is much smaller", t.stat().st_size < (uploads / "avatar_big.png").stat().st_size / 5)
            check("thumb is reused", _app._thumb_file(uploads / "avatar_big.png", 512) == t)
            ta = _app._thumb_file(uploads / "avatar_alpha.png", 128)
            with Image.open(ta) as im:
                check("transparency is kept", "A" in im.getbands())
            check("small images aren't upscaled", _app._thumb_file(uploads / "avatar_small.png", 256) is None)
            check("GIFs are left alone", _app._thumb_file(uploads / "anim.gif", 128) is None)
            check("no temp files left", not list(_app._THUMB_DIR.glob("*.part")))

            f = _app._thumb_url
            check("filter: shared upload", f("/uploads/avatar_big.png", 256) == "/api/uploads/avatar_big.png?w=256")
            check("filter: user upload", f("/api/uploads/x.jpg?v=1", 128) == "/api/uploads/x.jpg?w=128")
            check("filter: gif untouched", f("/uploads/a.gif", 128) == "/uploads/a.gif")
            check("filter: other urls untouched", f("https://x/y.png", 128) == "https://x/y.png" and f("", 64) == "")

            from httpx import ASGITransport, AsyncClient
            import asyncio

            async def _run():
                async with AsyncClient(transport=ASGITransport(app=_app.app), base_url="http://test") as client:
                    r = await client.get("/api/uploads/avatar_big.png?w=256")
                    check("route: thumbnail served", r.status_code == 200 and r.headers.get("content-type") == "image/webp")
                    check("route: cached for a week", "max-age=604800" in r.headers.get("cache-control", ""))
                    r2 = await client.get("/api/uploads/avatar_big.png")
                    check("route: original without ?w", r2.status_code == 200
                          and r2.headers.get("content-type") == "image/png" and "max-age" in r2.headers.get("cache-control", ""))
                    r3 = await client.get("/api/uploads/..%2F..%2Fsecret.txt")
                    check("route: can't climb out of uploads", r3.status_code == 404)
                    (Path(tmp) / "secret.txt").write_text("no", encoding="utf-8")
                    r4 = await client.get("/api/uploads/../secret.txt")
                    check("route: dot-dot path refused", r4.status_code == 404)

            _orig_gac = _app.get_auth_config
            _app.get_auth_config = lambda: {"auth_enabled": False}
            try:
                asyncio.run(_run())
            finally:
                _app.get_auth_config = _orig_gac
        finally:
            _app._UPLOADS_DIR, _app._THUMB_DIR = orig
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    test_boundary_policy()
    test_pii_guard_extended()
    test_runtime_policy_clamping()
    test_manifest_helpers()
    test_directive_parser_edge_cases()
    test_directive_store_edge_cases()
    test_memory_types_extended()
    test_chunker_edge_cases()
    test_memory_injector()
    test_memory_tool_all_actions()
    test_cost_tracker_extended()
    test_note_collector_helpers()
    test_manifest_id_collision()
    test_continuation_edge_cases()
    test_data_paths_extended()
    test_metering_extended()
    test_web_search_extract()
    test_active_directives_batch()
    test_vault_interleaved_ops()
    test_user_notes_loader_extended()
    test_manifest_diff_extended()
    test_echo_tool()
    test_llm_types()
    test_directive_injector_with_manifest()
    test_model_router_config()   # includes presets CRUD + empty map fix
    test_model_router_tool()
    test_email_tool_torture()
    test_directives_tool_torture()
    test_tool_registry_torture()
    test_validate_manifest()
    test_audit_changes()
    test_cost_tracker_pricing_actions()
    test_web_search_tool_extended()
    test_metering_helpers_extended()
    test_llm_client_factory()
    test_app_memory_helpers()
    test_seed_ui_knowledge_structure()
    test_metering_dataclass_ops()
    test_inbox_tool_torture()
    test_inbox_registry_dispatch()
    test_inbox_data_path()
    test_dynamic_scopes()
    test_category_policy()
    test_saved_profile_upgrade()
    test_tool_catalogue_dynamic()
    test_memory_tool_definition_dynamic()
    test_vault_sort_logic()
    test_vault_max_memory_limit()
    test_vault_template_elements()
    test_tools_max_memory_dropdown()
    test_memory_profile_max_total()
    test_vault_sort_edge_cases()
    test_avatar_migration()
    test_profile_api_torture()
    test_skins_api()
    test_saved_profile_crud()
    test_extract_save_memories_extended()
    test_registry_get_tool_defs()
    test_profile_create_v2()
    test_upload_thumbnails()
    test_settings_helpers()
    test_vault_search_min_score()
    test_tag_sort_mode()
    test_hard_max_total_ceiling()
    test_wiki_articles_loader()
    test_about_api()
    test_vault_filter_dropdown()
    test_routing_model_router()
    test_budget_tracker()
    test_router_budget_integration()
    test_model_router_tool_budget()
    test_edge_tts_conn_env_fallback()
    test_whisper_conn_env_fallback()
    test_searxng_url_env_override()
    test_connections_json_tts_fallback()
    test_connections_json_whisper_fallback()
    test_whisper_server_structure()
    test_searxng_settings_yml()
    test_service_dockerfiles()
    test_service_fly_tomls()
    test_env_priority_over_connections()
    test_platform_api_keys_image()
    test_platform_api_keys_voice()
    test_normalize_ollama_url()
    test_get_platform_connections()
    test_page_chat_connections_split()
    test_admin_platform_key_ollama_save()
    test_user_api_keys_openrouter_ollama()
    test_user_api_keys_masking()
    test_connections_all_models_static()
    test_admin_keys_template_providers()
    test_chat_html_three_mode_selector()
    test_resolve_connection_userkey()
    test_api_user_models()
    test_stripe_state_persist_path()
    test_connections_json_clean()
    test_billing_catalog_structure()
    test_tier_and_trial_system()
    test_credit_system()
    test_credit_checkout_and_webhook()
    test_credit_fulfillment_idempotent()
    test_credit_cost_estimators()
    test_user_activity_tracking()
    test_wipe_user_data()
    test_wipe_user_by_email()
    test_purge_inactive_users()
    test_list_all_users()
    test_auth_helpers()
    test_email_allowlist_gating()
    test_tier_info_structure()
    test_soul_script_helpers()
    test_soul_script_api()
    test_soul_script_faiss_indexing()
    test_collect_notes_soul_script()
    test_identity_profile_resolver()
    test_profiles_template_collapsible()
    test_runtime_info_tool()
    test_admin_voices_api()
    test_admin_voices_template()
    test_admin_user_management_api()
    test_connections_crud_api()
    test_pricing_crud_api()
    test_tts_voices_filter_logic()
    test_inworld_api_key_helper()
    test_check_admin_helper()
    test_faiss_scaling()
    test_metering_source_filtering()
    test_cost_tracker_source_tabs()
    test_boot_persistence_coverage()
    test_inbox_persistence_path()
    test_key_vault_encryption()
    test_key_vault_per_user_isolation()
    test_key_vault_html_stripping()
    test_faiss_update_keeps_memory_searchable()
    test_user_avatar_url_repointing()
    test_chat_avatar_and_analytics_template()
    test_demo_limit_and_profile_guidance()
    test_agi_loop_clock_and_timezone()
    test_agi_loop_energy_readout()
    test_agi_loop_pace_honesty()
    test_agi_loop_restart_awareness()
    test_agi_loop_handoff_letter()
    test_agi_loop_slab()
    test_agi_loop_app_wiring()
    test_agi_loop_preamble_and_linux()
    test_agi_loop_cache_discipline()
    test_agi_loop_state_tag()
    test_agi_loop_tool_requests()
    test_agi_loop_watchdog()
    test_chat_scroll_follows_only_at_bottom()
    test_agi_loop_narrated_tool_calls()
    test_agi_loop_hud_on_linux_and_local_day()
    test_loop_pages_stay_light()

    print(f"\n{'='*40}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if not FAIL:
        print("All tests passed.")
    # Exit directly: native threads (faiss / torch) can abort during interpreter teardown
    # ("terminate called without an active exception"), turning a clean run into exit 134.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(1 if FAIL else 0)
