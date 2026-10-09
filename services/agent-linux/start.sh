#!/bin/bash
# Boot: give the volume to the agent user, start the web terminal, then the command server.
set -e

AGENT_USER="${AGENT_USER:-supervisor}"
HOME_DIR="/home/$AGENT_USER"

# First boot on a fresh volume: seed the home directory from the image.
if [ ! -f "$HOME_DIR/.bashrc" ]; then
    cp -an /etc/skel/. "$HOME_DIR/"
    sed "s/supervisor/$AGENT_USER/g" /opt/agent/README.md > "$HOME_DIR/README.md"
fi
mkdir -p "$HOME_DIR/.agent"
touch "$HOME_DIR/.agent/shell.log"
# Everything in the home is the mind's — except ~/library (read-only reference) and ~/hud (measurements
# written by root, below). Those stay root-owned across reboots.
find "$HOME_DIR" \( -path "$HOME_DIR/library" -o -path "$HOME_DIR/hud" \) -prune -o -exec chown -h "$AGENT_USER:$AGENT_USER" {} +

# The HUD writer: same server, HUD_ONLY mode, as root on :8081. It serves only POST /hud and /health —
# it runs no commands — so the mind's measurements come from a process the mind doesn't own.
HUD_ONLY=1 PORT=8081 HOME="$HOME_DIR" python3 /opt/agent/shell_server.py &

# Web terminal for the operator — no public IP, reach it with `fly proxy 7681 -a agent-linux`.
runuser -u "$AGENT_USER" -- env -u SHELL_TOKEN HOME="$HOME_DIR" ttyd -W -p 7681 -w "$HOME_DIR" bash -l &

# SHELL_TOKEN is inherited from the environment, never put on the command line (ps would show it).
exec runuser -u "$AGENT_USER" -- env -u HUD_ONLY HOME="$HOME_DIR" PORT=8080 python3 /opt/agent/shell_server.py
