ARG VARIANT="3.9"
FROM --platform=linux/amd64 mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

USER vscode

RUN curl -sSf https://rye.astral.sh/get | RYE_VERSION="0.44.0" RYE_INSTALL_OPTION="--yes" bash
ENV PATH=/home/vscode/.rye/shims:$PATH

RUN echo "[[ -d .venv ]] && source .venv/bin/activate || export PATH=\$PATH" >> /home/vscode/.bashrc