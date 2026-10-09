"""Memory / identity profiles are per user, with the global files as defaults.

Run from project root:
    python -m pytest tests/test_memory_profiles_per_user.py
"""

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def env(tmp_path, monkeypatch):
    import web.app as app
    import src.request_context as rc
    import src.memory.profile_resolver as resolver
    import src.tools.memory_tool as memory_tool

    cfg = tmp_path / "config"
    ident_dir = cfg / "saved_profiles" / "identity"
    mem_dir = cfg / "saved_profiles" / "memory"
    ident_dir.mkdir(parents=True)
    mem_dir.mkdir(parents=True)
    (cfg / "identity_profile.json").write_text(json.dumps({"retrieval_policy": {"top_k": 10}}))
    (cfg / "memory_profile.json").write_text(json.dumps(
        {"retention_policy": {"max_total_memories": 5000}, "category_policy": {"mode": "open"}}))
    (mem_dir / "builtin.json").write_text(json.dumps({"name": "Built-in"}))

    monkeypatch.setattr(rc, "_DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(app, "IDENTITY_PROFILE_FILE", cfg / "identity_profile.json")
    monkeypatch.setattr(app, "MEMORY_PROFILE_FILE", cfg / "memory_profile.json")
    monkeypatch.setattr(app, "_SAVED_IDENTITY_PROFILES_DIR", ident_dir)
    monkeypatch.setattr(app, "_SAVED_MEMORY_PROFILES_DIR", mem_dir)
    monkeypatch.setattr(resolver, "_GLOBAL_IDENTITY_FILE", cfg / "identity_profile.json")
    monkeypatch.setattr(resolver, "_SAVED_IDENTITY_DIR", ident_dir)
    monkeypatch.setattr(memory_tool, "_CONFIG_DIR", cfg)
    return app, rc, resolver, memory_tool, cfg, mem_dir


def _as(rc, uid):
    return rc.current_user_id.set(uid)


def test_active_profiles_are_per_user(env):
    app, rc, resolver, memory_tool, cfg, _ = env
    tok = _as(rc, "alice")
    try:
        # Starts from the global default
        assert app._load_memory_profile()["retention_policy"]["max_total_memories"] == 5000
        p = app._load_memory_profile()
        p["retention_policy"]["max_total_memories"] = 42
        p["category_policy"]["mode"] = "custom"
        app._save_memory_profile(p)
        ip = app._load_identity_profile()
        ip["retrieval_policy"]["top_k"] = 3
        app._save_identity_profile(ip)

        assert app._load_memory_profile()["retention_policy"]["max_total_memories"] == 42
        assert memory_tool._load_category_policy()["mode"] == "custom"
        assert resolver.get_retrieval_policy()["top_k"] == 3
    finally:
        rc.current_user_id.reset(tok)

    tok = _as(rc, "bob")
    try:
        # Bob still sees the defaults
        assert app._load_memory_profile()["retention_policy"]["max_total_memories"] == 5000
        assert memory_tool._load_category_policy()["mode"] == "open"
        assert resolver.get_retrieval_policy()["top_k"] == 10
    finally:
        rc.current_user_id.reset(tok)

    # The global defaults were never touched
    assert json.loads((cfg / "memory_profile.json").read_text())["retention_policy"]["max_total_memories"] == 5000
    assert json.loads((cfg / "identity_profile.json").read_text())["retrieval_policy"]["top_k"] == 10


def test_indexing_policy_ignores_user_overrides(env):
    app, rc, resolver, *_ = env
    tok = _as(rc, "alice")
    try:
        app._save_identity_profile({"indexing_policy": {"chunk_size_tokens": 50}})
        assert resolver.get_retrieval_policy() == resolver._HARDCODED_DEFAULTS["retrieval_policy"]
        # The shared soul-script index keeps the global chunking
        assert resolver.get_indexing_policy() != {"chunk_size_tokens": 50}
    finally:
        rc.current_user_id.reset(tok)


def test_saved_presets_are_per_user(env):
    app, rc, _, _, _, mem_dir = env
    tok = _as(rc, "alice")
    try:
        r = app._save_preset(mem_dir, {"filename": "mine", "profile": {"name": "Alice's"}}, {})
        assert r.status_code == 200
        names = {e["filename"]: e for e in app._list_profiles_in(mem_dir)}
        assert "mine" in names and not names["mine"]["pinned"]
        assert names["builtin"]["pinned"]  # shared defaults read-only for users
        assert app._delete_preset(mem_dir, "builtin").status_code == 403
        assert (mem_dir / "builtin.json").exists()
        assert not (mem_dir / "mine.json").exists()  # saved to Alice's folder, not the shared one
    finally:
        rc.current_user_id.reset(tok)

    tok = _as(rc, "bob")
    try:
        names = [e["filename"] for e in app._list_profiles_in(mem_dir)]
        assert "mine" not in names and "builtin" in names
        assert app._get_preset(mem_dir, "mine").status_code == 404
    finally:
        rc.current_user_id.reset(tok)

    tok = _as(rc, "alice")
    try:
        assert app._delete_preset(mem_dir, "mine").status_code == 200
        assert "mine" not in [e["filename"] for e in app._list_profiles_in(mem_dir)]
    finally:
        rc.current_user_id.reset(tok)


def test_local_mode_edits_global_defaults(env):
    app, rc, _, _, cfg, mem_dir = env
    tok = _as(rc, "__local__")
    try:
        app._save_memory_profile({"retention_policy": {"max_total_memories": 7}})
        assert json.loads((cfg / "memory_profile.json").read_text())["retention_policy"]["max_total_memories"] == 7
        assert not app._list_profiles_in(mem_dir)[0]["pinned"]  # local owner manages shared presets
    finally:
        rc.current_user_id.reset(tok)
