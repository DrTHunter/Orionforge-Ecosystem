FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        sudo ca-certificates curl wget git nano vim less tmux htop jq ripgrep unzip zip sqlite3 \
        build-essential python3 python3-pip python3-venv nodejs npm ttyd iproute2 iputils-ping dnsutils \
    && rm -rf /var/lib/apt/lists/*

# One image, one machine per loop: build with --build-arg AGENT_USER=kos for K-OS's box.
ARG AGENT_USER=supervisor
ENV AGENT_USER=${AGENT_USER}

# ubuntu:24.04 ships a uid-1000 'ubuntu' user — drop it so the agent gets 1000.
RUN userdel -r ubuntu 2>/dev/null || true \
    && useradd -m -u 1000 -s /bin/bash ${AGENT_USER} \
    && echo "${AGENT_USER} ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/${AGENT_USER} && chmod 440 /etc/sudoers.d/${AGENT_USER}

COPY shell_server.py start.sh /opt/agent/
COPY home-README.md /opt/agent/README.md
RUN chmod +x /opt/agent/start.sh

ENV PYTHONUNBUFFERED=1
EXPOSE 8080 8081 7681
CMD ["/opt/agent/start.sh"]
