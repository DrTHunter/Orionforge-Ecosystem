"""Loop configuration (config/agi_loop.json). One model, no router."""

import json
import logging
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict

log = logging.getLogger(__name__)

LLM_MODELS: Dict[str, Dict[str, str]] = {
    "deepseek_chat":     {"openrouter": "deepseek/deepseek-v4.1-flash",  "provider": "deepseek",  "model": "deepseek-chat"},
    "deepseek_reasoner": {"openrouter": "deepseek/deepseek-v4-pro-0813", "provider": "deepseek",  "model": "deepseek-reasoner"},
    "kimi":              {"openrouter": "moonshotai/kimi-k3",            "provider": "",          "model": ""},
    "qwen":              {"openrouter": "qwen/qwen3.8-max-0902",         "provider": "",          "model": ""},
    "claude_haiku":      {"openrouter": "anthropic/claude-haiku-5.5",    "provider": "anthropic", "model": "claude-haiku-5-5"},
    "claude_sonnet":     {"openrouter": "anthropic/claude-sonnet-5.5",   "provider": "anthropic", "model": "claude-sonnet-5-5"},
    "claude_opus":       {"openrouter": "anthropic/claude-opus-5.5",     "provider": "anthropic", "model": "claude-opus-5-5"},
    "claude_fable":      {"openrouter": "anthropic/claude-fable-5.1",    "provider": "anthropic", "model": "claude-fable-5-1"},
    "gpt_mini":          {"openrouter": "openai/gpt-6-luna",             "provider": "openai",    "model": "gpt-6-luna"},
    "gpt":               {"openrouter": "openai/gpt-6.1-sol",            "provider": "openai",    "model": "gpt-6.1-sol"},
    "gpt_pro":           {"openrouter": "openai/gpt-6-astra",            "provider": "openai",    "model": "gpt-6-astra"},
    "gemini_flash":      {"openrouter": "google/gemini-3.8-flash",       "provider": "google_gemini", "model": "gemini-3.8-flash"},
    "gemini_pro":        {"openrouter": "google/gemini-3.1-pro-preview", "provider": "google_gemini", "model": "gemini-3.1-pro-preview"},
    "grok":              {"openrouter": "x-ai/grok-4.7",                 "provider": "xai",       "model": "grok-4.7"},
    "hermes":            {"openrouter": "nousresearch/hermes-4-405b",    "provider": "",          "model": ""},
}

# Slugs these choices used to default to. A saved config still carrying one gets the current default:
# it was never an operator's choice, just the default of its day.
RETIRED_LLM_SLUGS = {
    "deepseek/deepseek-chat", "deepseek/deepseek-r1-0528", "moonshotai/kimi-k2.5", "qwen/qwen3-max",
    "anthropic/claude-haiku-4.5", "openai/gpt-5.4-mini", "openai/gpt-5.5", "openai/gpt-5.5-pro",
    "google/gemini-3.5-flash", "x-ai/grok-4.3",
}


@dataclass
class LoopConfig:
    # Identity & model — one connection, one model, chosen here.
    agent: str = "supervisor"
    connection_id: str = ""            # "" = the agent's mapped/default connection
    model: str = ""                    # "" = the agent profile's model, else the connection's first
    temperature: float = 0.7
    max_output_tokens: int = 0         # 0 = the provider's default
    timezone: str = "UTC"   # the operator's clock: the HUD's main time, and what "morning" or "night" means

    # Wall-time cadence. Low energy slows it; surprise quickens it.
    base_interval_seconds: float = 120.0
    min_interval_seconds: float = 20.0
    max_interval_seconds: float = 1800.0
    max_rest_minutes: float = 240.0

    # Energy: a hard daily budget.
    daily_token_budget: int = 200_000
    daily_cost_cap: float = 2.00       # USD; 0 = tokens only
    max_tokens_per_tick: int = 30_000

    # Per-tick limits
    max_steps_per_tick: int = 4        # model ↔ tool round trips
    max_tool_calls_per_tick: int = 12
    history_window: int = 4            # earlier ticks carried as conversation (grows to 2× before trimming, for the cache)

    # The llm tool: a side call to another model, at the mind's choice. Each choice has an OpenRouter
    # slug and a native (provider, model) for when the loop's connection is that provider's own API.
    llm_models: Dict[str, Any] = field(default_factory=lambda: {k: dict(v) for k, v in LLM_MODELS.items()})
    llm_default: str = "deepseek_reasoner"
    cheap_max_tokens: int = 8000          # reasoners spend part of this thinking

    # The quiet gate: a timer wake that finds nothing new after an idle tick is slept through, no model call.
    quiet_gate: bool = True
    gate_max_skips: int = 3            # quiet wakes in a row before one is let through anyway

    # Inner world
    capacity_chars: int = 2400         # how much the field can hold at once
    capture_threshold: float = 0.45    # salience needed to pull attention involuntarily

    # Metacognitive guards
    stale_streak_limit: int = 3        # identical ticks before a forced rest
    guard_rest_minutes: float = 30.0
    max_guard_rests: int = 3           # forced rests per session before stopping
    error_streak_limit: int = 5
    rumination_ticks: int = 5          # ticks at one focus without acting before the body notices

    workbench: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoopConfig":
        out = cls()
        for f in fields(cls):
            if f.name not in data or data[f.name] is None:
                continue
            default = getattr(out, f.name)
            value = data[f.name]
            try:
                if isinstance(default, dict):
                    if not isinstance(value, dict):
                        raise TypeError("expected an object")
                    # Saved entries override the defaults; models added to the defaults later still appear.
                    value = {**default, **{str(k): dict(v) for k, v in value.items() if isinstance(v, dict)
                                           and not (k in default and v.get("openrouter") in RETIRED_LLM_SLUGS)}}
                elif isinstance(default, bool):
                    value = value if isinstance(value, bool) else str(value).lower() in ("1", "true", "yes", "on")
                elif isinstance(default, int):
                    value = int(float(value))
                elif isinstance(default, float):
                    value = float(value)
                else:
                    value = str(value)
            except (TypeError, ValueError):
                log.warning("[agi_loop] bad config value %s=%r — using default", f.name, value)
                continue
            setattr(out, f.name, value)
        out.min_interval_seconds = max(5.0, out.min_interval_seconds)
        out.max_interval_seconds = max(out.min_interval_seconds, out.max_interval_seconds)
        out.base_interval_seconds = min(max(out.base_interval_seconds, out.min_interval_seconds), out.max_interval_seconds)
        out.capacity_chars = max(600, out.capacity_chars)
        out.max_steps_per_tick = max(1, out.max_steps_per_tick)
        out.cheap_max_tokens = max(64, min(32000, out.cheap_max_tokens))
        out.gate_max_skips = max(0, out.gate_max_skips)
        return out

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def load(cls, path: Path) -> "LoopConfig":
        try:
            return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
        except FileNotFoundError:
            return cls()
        except Exception as exc:
            log.warning("[agi_loop] config unreadable (%s) — using defaults", exc)
            return cls()

    def save(self, path: Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
