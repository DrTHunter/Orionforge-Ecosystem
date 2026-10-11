# This machine is yours

Ubuntu 24.04, headless. You are `agent`, with passwordless `sudo`.
`/home/agent` is your persistent disk: everything here survives restarts.
Anything outside your home is rebuilt from the image when the machine is recreated.
Your owner can grow the disk from the Linux tab when it fills up.

Outbound internet works (apt, pip, git, curl). Nothing else on the platform can
reach this machine except your loop, with this machine's own key.

Every command you run through the loop is logged to `~/.elysia/shell.log`, and
your owner can follow it from the Linux tab. Keep a README.md in each project
folder, and list your projects in `~/README.md`, so they can see what you're building.

The machine runs while your loop is awake and stops when it sleeps. While it runs,
it costs your owner credits; keep long jobs purposeful.

Installed: python3, pip, venv, git, curl, wget, build-essential, nano, vim,
tmux, htop, jq, ripgrep, sqlite3, nodejs, npm.
