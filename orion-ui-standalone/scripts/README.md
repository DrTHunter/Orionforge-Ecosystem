# scripts/

Utility scripts for data seeding and maintenance. Run from the project root.

## Files

| File | Purpose |
|------|---------|
| `seed_memories.py` | Seeds the memory vault with test/example memories |
| `seed_ui_knowledge.py` | Seeds knowledge notes with UI documentation and help content |
| `orion_vscode_bridge.py` | Optional MCP bridge that routes VS Code Copilot Agent prompts into Orion Forge |

## seed_memories.py

Populates `data/memory/vault.jsonl` with sample memories for testing and bootstrapping.

### What's Seeded

Example data includes:
- Computer hardware specs (workstation, laptop, NAS, networking)
- Project state and priorities
- Bio facts and user preferences
- Example canon and register tier memories

### Usage

```bash
python scripts/seed_memories.py
```

Uses `VaultStore` from `src/memory/vault.py` to write properly formatted entries with full validation (PII guard, duplicate detection, write-gate).

## seed_ui_knowledge.py

Seeds the knowledge notes system (`data/user_notes/`) with structured documentation about the OrionForge UI  -  tool descriptions, feature guides, and help content that agents can reference via FAISS retrieval.

### Usage

```bash
python scripts/seed_ui_knowledge.py
```

Creates JSON knowledge note files with proper metadata for the knowledge editor and FAISS indexing pipeline.

## orion_vscode_bridge.py

Provides a minimal MCP server over stdio with one tool, `orion_chat`, which forwards prompts to `POST /api/chat/send`.

### Default Persona Policy

- Default agent: `supervisor`
- Allowed overrides: `k_os`

### Usage

```powershell
python scripts/orion_vscode_bridge.py
```

The bridge loads its settings from `config/vscode_bridge.json` and can also be overridden with `ORION_VSCODE_BRIDGE_*` environment variables.

### Model Selection (Default + Quick Switching)

The bridge supports a default model and a fallback model:

- `default_model_override`: first model to try
- `fallback_model_override`: second model if the first model fails with a retryable API error

Example in `config/vscode_bridge.json`:

```json
{
   "default_model_override": "deepseek-reasoner",
   "fallback_model_override": "gpt-5.2"
}
```

You can also set these at runtime with env vars:

```powershell
$env:ORION_VSCODE_BRIDGE_DEFAULT_MODEL="deepseek-reasoner"
$env:ORION_VSCODE_BRIDGE_FALLBACK_MODEL="gpt-5.2"
python scripts/orion_vscode_bridge.py
```

For per-request switching, pass `model_override` in the MCP `orion_chat` call.
Supported aliases:

- `deepseek-reasoner`
- `gpt-5.2`
- `claude-sonnet-latest`
- `claude-opus-latest`

Example overrides:

- `model_override: "claude-sonnet-latest"`
- `model_override: "claude-opus-latest"`

### Authentication Modes

The bridge supports three auth modes via `config/vscode_bridge.json` (`auth.mode`):

| Mode | Use case | How |
|------|----------|-----|
| `disabled` | Local app with `auth_enabled: false` | No credentials sent |
| `bridge_key` | Recommended for a remote/hosted server | Static key in `X-Bridge-Key` header |
| `bearer` | One-off testing | Short-lived Supabase JWT (expires) |

### Bridge Key Setup (Recommended)

A static bridge key authenticates the bridge as the owner account without
short-lived tokens. It is fully opt-in: when no key is set server-side, the
mechanism is inert and normal Supabase login is unchanged.

1. Generate a strong key (type this in your own terminal):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

2. Set the key on the server: put `ORION_BRIDGE_API_KEY` in the app's
   environment (or `.env`), or in `config/auth.json` under `bridge_api_key`.
   On a hosted server, set it as that host's secret and restart the app.

3. Point the bridge at the same key (in your terminal, not committed):

```powershell
$env:ORION_VSCODE_BRIDGE_AUTH_MODE="bridge_key"
$env:ORION_VSCODE_BRIDGE_KEY="<generated_key>"
python scripts/orion_vscode_bridge.py
```

#### Shared owner data (optional)

To make bridge calls share the same chats and memory vault as your browser
login, set `bridge_user_id` in `config/auth.json` (or `ORION_BRIDGE_API_KEY`
server env stays the same) to your Supabase user id. If left blank, the bridge
uses an isolated `__bridge__` data space.

#### Security notes

- Treat the bridge key like a password; anyone with it has full owner access.
- The key is compared in constant time. Only send it to a server over HTTPS (or to `127.0.0.1`).
- Remove it any time by unsetting `ORION_BRIDGE_API_KEY` and restarting the app.
