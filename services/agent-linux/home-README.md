# This machine is yours

Ubuntu 24.04, headless. You are `supervisor`, with passwordless `sudo`.
`/home/supervisor` is a 30 GB persistent volume: everything here survives restarts.
Anything outside your home is rebuilt from the image on every deploy.

Outbound internet works (apt, pip, git, curl). Nothing can reach you from
the public internet. The loop talks to you over Fly's private network.

Every command you run through the loop is logged to `~/.agent/shell.log`.
The operator watches it from a web terminal.

Installed: python3, pip, venv, git, curl, wget, build-essential, nano, vim,
tmux, htop, jq, ripgrep, sqlite3, nodejs, npm.
