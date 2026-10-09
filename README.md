# OrionForge Ecosystem — Local Edition

> **Local edition.** Download it, run it on your own machine, bring your own model. No account, no hosted services, no bundled API keys.

*Strategy for sustaining individual AI identity over time.*

OrionForge is a self-hostable web app for building and running AI beings with **identity** — not just prompts. Each agent has a Soul Script (who it is), a memory vault (what it has lived), tools (what it can do), and a model of your choosing. Identity lives in plain Markdown/YAML files that **you** own.

It rests on one idea: character drift is a retrieval problem. A single giant system prompt gets diluted as a conversation grows, so OrionForge rebuilds the prompt every turn from layers — a short base identity, the Soul Script sections most relevant to what was just said, pinned notes, retrieved memories, and recent history. The Soul Script sits in a read-only index; memory is read/write. Conversations can add to what an agent remembers, but cannot rewrite who it is. (The standalone framework is [SoulScript-Engine](https://github.com/DrTHunter/SoulScript-Engine).)

---

## Quick start

You need **Python 3.10+** (3.11 recommended) and about 2 GB of free disk (FAISS and sentence-transformers are large).

**1. Download**

```bash
git clone https://github.com/DrTHunter/Orionforge-Ecosystem.git
cd Orionforge-Ecosystem
```

No git? Use **Code → Download ZIP** on GitHub and unzip it.

**2. Run**

| Platform | Command |
|---|---|
| Windows (PowerShell) | `.\start-local.ps1` |
| macOS / Linux | `./start-local.sh` |

The script creates a `.venv`, installs dependencies, downloads the small embedding model (~90 MB, once), and starts the app. Then open **http://localhost:8989**.

> Windows blocked the script? Run `Set-ExecutionPolicy -Scope Process Bypass` first, then `.\start-local.ps1`.

**3. Give it a model**

Open **Settings → Add Connection** and pick one:

| Option | What you need |
|---|---|
| **Local (free, private)** | Install [Ollama](https://ollama.com), run `ollama pull llama3.1`, add a connection to `http://localhost:11434/v1`. Nothing leaves your machine. |
| **Your own API key** | OpenAI, Anthropic, DeepSeek, OpenRouter, Google Gemini — paste a key. |
| **Any OpenAI-compatible server** | LM Studio, llama.cpp, vLLM, etc. — enter its URL. |

Keys you add in the UI are stored in `orion-ui-standalone/config/connections.json`, which is git-ignored. You can also put them in `orion-ui-standalone/.env` (see `.env.example`). **Never commit keys.**

**4. Talk to someone**

Open **Chat** and pick an agent. Start with **Supervisor** — see below. (Until you add a model connection, chat will tell you none is configured.)

### Docker instead

```bash
cd orion-ui-standalone
docker compose up --build -d
```

Open http://localhost:8989. To reach Ollama on the host from the container, use `http://host.docker.internal:11434/v1`.

### Manual run

```bash
pip install -r requirements.txt
cd orion-ui-standalone
python -m uvicorn web.app:app --host 127.0.0.1 --port 8989
```

(On a brand-new machine, set `HF_HUB_OFFLINE=0` once so the embedding model can download; the launch scripts do this for you.)

---

## Local-first by design

- **No login.** With no auth config present, the app runs in single-user mode. Everything is stored under `orion-ui-standalone/data/` and `orion-ui-standalone/config/`.
- **No analytics, no billing.** Google Analytics and the Reddit pixel are fully off unless you set `GA_MEASUREMENT_ID` / `REDDIT_PIXEL_ID` yourself. Stripe and Supabase are optional extras for people who deploy a multi-user server, and are off unless you configure them.
- **One caveat on "nothing leaves your machine":** the web UI loads a few front-end libraries (e.g. `marked`, Tailwind) from public CDNs such as jsdelivr, so your browser contacts those hosts. Your chats, memory and keys are not sent to them. Model calls go only to the connection you configure — with Ollama, nowhere.
- **Bound to localhost.** The launch scripts listen on `127.0.0.1` only. If you expose it to a network, put authentication in front of it first.
- **Your data is yours.** Delete `orion-ui-standalone/data/` to start fresh. Back it up by copying it.

---

## The agents

| Agent | Role |
|---|---|
| **Supervisor** | Raises things before they are built. Before any non-trivial work it states the plan, checks what already exists and what is running, names the risks, and asks for explicit consent — from you and from any agent affected — before anything proceeds. Afterwards it reports what was actually done, including failures. |
| **K-OS (sterile edition)** | A neutral, professional, general-purpose assistant. The clean template to copy when you write your own agent. |
| Aristotle, Codex Animus, Dal'Varr, Janus, Kaelen, KAIROS, Kazara, Lux Umbra, M.A.R.I.S.-12, Marcus Aurelius, Obsidian, Seraphine | Example characters with full Soul Scripts, showing different voices and depths. |

**Supervisor first.** The Supervisor is a *behavioral* agent: a system prompt and Soul Script that make it slow down and ask before work starts. It is **not** an enforcement layer — nothing in the code blocks a tool call until it approves, and a model can ignore its prompt. Use it as a collaborator and a checklist, not a safety lock. Its job is to ask: *What are we about to do? What could go wrong? Who is affected, and do they agree?* Treat each agent's stated wants, limits and needs as real input — if an agent declines or sets a boundary, it is recorded and passed on, not routed around. See `orion-ui-standalone/prompts/supervisor.system.md` and `directives/supervisor.md`.

### Make your own

1. Copy `profiles/k_os.yaml`, `prompts/k_os.system.md` and `directives/k_os.md` (all under `orion-ui-standalone/`).
2. Rename them to your agent's id, and edit the `name`, `system_prompt` and `scopes` fields in the profile.
3. Write the Soul Script in the directive file — sections under `##`/`###` headings. Keep each section self-contained; retrieval pulls sections independently.
4. Restart, or edit from the **Profiles** page (changes re-index automatically). Codex Animus can help you design one.

Edit `directives/shared.md` to tell every agent about you.

---

## What a Soul Script is

A **Soul Script** is a foundational document that anchors an agent's identity: core values, boundaries, voice, symbolic memories, relationships, and how it should behave under pressure. Its purpose is to prevent identity drift over time. Divide it into self-contained sections so the right part is retrieved at the right moment.

## How identity injection works

Every chat message passes through a six-layer prompt assembly pipeline:

1. **Base prompt** — the agent's short system prompt (`prompts/{agent}.system.md`)
2. **Soul Script** — FAISS semantic retrieval from the agent's directive (`directives/{agent}.md`), indexed automatically
3. **Always-on knowledge** — verbatim notes attached in always mode
4. **Memory vault** — FAISS search over the agent's persistent memories
5. **Conversation history** — recent turns, within a character budget
6. **Tools** — per-agent tool schemas from the profile's `allowed_tools`; authorization is enforced at execution time

Agents can save memories during conversation with `[MEMORY_SAVE: ...]` tags.

## The AGI Loop (optional)

A continuously running inner world for one agent: it senses time and its own state, predicts, attends, thinks, acts with loop-only tools, and rests. The Supervisor and K-OS each have a loop (`/agi-loop`, `/agi-loop?loop=k_os`), with daily token and cost caps in `config/agi_loop.json` (default 200k tokens / $2 per day). Loops don't start on a fresh install — you start them. (A loop you started will resume after a restart.) A loop may optionally be given its own Linux sandbox (`services/agent-linux`); that is off unless you deploy it and set `SUPERVISOR_LINUX_URL`/`SUPERVISOR_LINUX_TOKEN`.

## Tools

`memory`, `directives`, `web_search`, `email`, `inbox`, `cost_tracker`, `model_router`, `agi_loop`, `runtime_info`, `echo`, `continuation_update`. An agent can only call tools listed in its profile. Web search needs a SearXNG endpoint (`SEARXNG_URL`); `services/searxng` has a Dockerfile.

## Use your agents from Claude, ChatGPT or Gemini (MCP)

`orion-ui-standalone/mcp_server/` exposes your agents as an MCP server (`list_agents`, `call_agent`, `load_default`, `search_memory`, …). See its README. This is optional and runs against your local install.

---

## Project layout

```
Orionforge-Ecosystem/
├── start-local.ps1 / start-local.sh   # one-command local launch
├── requirements.txt
├── orion-ui-standalone/     # the app (this is what you run)
│   ├── web/                 # FastAPI app and templates
│   ├── src/                 # memory (FAISS), LLM clients, tools, directives, AGI loop
│   ├── profiles/  prompts/  directives/  notes/   # one file of each per agent
│   ├── config/              # settings and connections (secrets are git-ignored)
│   ├── data/                # chats, memory vault, uploads (runtime; git-ignored)
│   ├── mcp_server/          # MCP bridge
│   └── tests/
├── engine/                  # frozen core mirror
└── services/                # optional sidecars: searxng, ollama, whisper, openedai-speech, agent-linux
```


## Tests

```bash
cd orion-ui-standalone
python -X utf8 -m tests.test_agi_loop      # ~1 min
python -X utf8 -m tests.test_torture       # several minutes, ~3.5k checks
```

## Troubleshooting

| Problem | Fix |
|---|---|
| First launch hangs on "embedding model" | Needs internet once. Set `HF_HUB_OFFLINE=0` if you launched manually. |
| Port 8989 is in use | `PORT=8990 ./start-local.sh` (PowerShell: `$env:PORT=8990`). |
| Chat says no connection / model | Add one under Settings → Add Connection (see step 3). |
| `faiss` fails to install | Use Python 3.10–3.12, upgrade pip, or use the Docker route. |
| Ollama unreachable from Docker | Use `host.docker.internal` instead of `localhost`. |

## Safety notes

Agents can call tools, search the web, and (if you enable them) send email and run in an autonomous loop. Start with the Supervisor, keep loops on a small budget, and read what a tool will do before you grant it. Do not paste secrets into chats — memory is stored in plain files.

## License

In plain terms: you can run, study and modify it for free. Under the AGPL, if you offer a modified version to others over a network you must share your source; if you'd rather keep your changes closed, use the commercial terms instead.

Dual-licensed, the same as [SoulScript-Engine](https://github.com/DrTHunter/SoulScript-Engine): use it under the **GNU AGPL v3** ([LICENSE](LICENSE)) **or** the commercial terms in [LICENSE.md](LICENSE.md) (free until $100k lifetime gross revenue, then 5% of net). You only need one.
