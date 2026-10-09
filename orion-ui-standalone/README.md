# orion-ui-standalone — the app

This folder is the OrionForge web app: a FastAPI server with Jinja2 pages, the Soul Script engine modules (`src/`), the agent files, and the tests. It is what you run. Stable engine code is mirrored in `../engine/`.

For download and first-run instructions, see the [top-level README](../README.md). The short version:

```bash
# from the repository root
./start-local.sh            # macOS / Linux
.\start-local.ps1           # Windows
```

or by hand, from this folder:

```bash
pip install -r requirements.txt
python -m uvicorn web.app:app --host 127.0.0.1 --port 8989
```

Open **http://localhost:8989**.

---

## Folder structure

```
orion-ui-standalone/
├── web/                # FastAPI app: routes (app.py), auth, user data isolation, templates, static files
├── src/                # Engine modules
│   ├── directives/     # Soul Script parsing, storage, injection, manifest
│   ├── governance/     # Session-scoped directive tracking
│   ├── llm_client/     # OpenAI-compatible, Anthropic and Ollama clients
│   ├── memory/         # FAISS memory vault, chunking, PII guard, injection
│   ├── observability/  # Token metering and cost tracking
│   ├── policy/         # Boundary enforcement and risk classification
│   ├── routing/        # Optional multi-tier model router
│   ├── storage/        # Note loading
│   ├── tools/          # Tool implementations + registry
│   └── agi_loop/       # The optional continuously running loop
├── profiles/           # One YAML per agent: provider, model, tools, memory scopes
├── prompts/            # One base system prompt per agent (*.system.md)
├── directives/         # One Soul Script per agent (*.md), plus shared.md for all agents
├── notes/              # Optional per-agent notes injected at session start
├── config/             # Settings, model router, pricing, AGI loop config (secrets are git-ignored)
├── data/               # Runtime data: chats, memory vault, uploads (git-ignored except seed files)
├── mcp_server/         # MCP server: use your agents from Claude, ChatGPT, Gemini
├── scripts/            # Seeding scripts and the optional VS Code bridge
└── tests/              # Test suite
```

## Agents

| Agent | Files |
|---|---|
| **Supervisor** | `profiles/supervisor.yaml`, `prompts/supervisor.system.md`, `directives/supervisor.md` |
| **K-OS (sterile edition)** | `profiles/k_os.yaml`, `prompts/k_os.system.md`, `directives/k_os.md`. Copy these to make a new agent. |
| Example characters | Aristotle, Codex Animus, Dal'Varr, Janus, Kaelen, KAIROS, Kazara, Lux Umbra, M.A.R.I.S.-12, Marcus Aurelius, Obsidian, Seraphine |

A new agent needs a profile, a system prompt and a directive file that share an id. You can also create agents from the **Profiles** page.

## Pages

| Page | URL | What it does |
|---|---|---|
| Chat | `/chat` | Talk to an agent, with streaming and per-chat model selection |
| Profiles | `/profiles` | Create and edit agents, their system prompt, Soul Script, notes and avatar |
| Vault | `/vault` | Browse, search and edit persistent memories |
| Knowledge | `/knowledge` | Notes that can be attached to agents (always-on or retrieved) |
| Tools | `/tools` | Tool settings, memory profiles, email, web search, model router |
| Settings | `/settings` | Model connections, voice, image, timezone, skin |
| Pricing | `/pricing` | Per-model token prices used for cost tracking |
| Skins | `/skins` | UI themes |
| AGI Loop | `/agi-loop`, `/agi-loop?loop=k_os` | The optional loop for the Supervisor and K-OS |
| Group Chat | `/group-chat` | One room shared by the running loops and you |
| Connect | `/connect` | How to reach your agents over MCP |
| Wiki | `/about` | Project wiki built from the READMEs |

Store, plans, login and admin pages exist for multi-user hosted deployments. With no auth configured, the app runs in single-user local mode and those pages aren't needed.

## Local mode vs. hosted mode

- **Local mode (default).** No `config/auth.json` → no login. A single local user owns everything under `data/`. The AGI Loop, Group Chat and Admin links are shown in the sidebar.
- **Hosted mode (optional).** Configure Supabase in `config/auth.json` (see `config/auth.example.json`). Each user then gets an isolated data tree under `data/users/{user_id}/`, with copy-on-write overrides of the global agents. Admins come from the `ADMIN_EMAILS` / `ADMIN_USER_IDS` env vars, which are empty by default. Stripe billing is opt-in via its own env vars.
- **Analytics.** Off unless you set `GA_MEASUREMENT_ID` (and optionally `REDDIT_PIXEL_ID`).

## Optional services

These are set with env vars. Each has a Dockerfile in `../services/`.

| Variable | Service |
|---|---|
| `SEARXNG_URL` | SearXNG, for the `web_search` tool |
| `TTS_URL` | OpenedAI Speech, for text-to-speech |
| `WHISPER_URL` | Whisper, for speech-to-text |
| `SUPERVISOR_LINUX_URL` / `_TOKEN`, `KOS_LINUX_URL` / `_TOKEN` | A Linux sandbox for a loop (`services/agent-linux`) |

## Embeddings

Memory, Soul Script retrieval and the loop's field use `sentence-transformers` with `all-MiniLM-L6-v2` (384 dims, ~90 MB). The app loads it from the local cache only (`HF_HUB_OFFLINE=1` by default). The launch scripts download it once. If you run by hand on a new machine, set `HF_HUB_OFFLINE=0` for the first start.

## Tests

```bash
python -X utf8 -m tests.test_agi_loop       # ~1 min
python -X utf8 -m tests.test_torture        # several minutes, ~3.5k checks
python -X utf8 tests/run_all.py             # every suite
```

See [tests/README.md](tests/README.md).

## VS Code bridge (optional)

`scripts/orion_vscode_bridge.py` is a stdio MCP server with one tool, `orion_chat`. It forwards Copilot agent-mode prompts to your local app (default persona `supervisor`, override `k_os`). See [scripts/VSCODE_BRIDGE.md](scripts/VSCODE_BRIDGE.md).
