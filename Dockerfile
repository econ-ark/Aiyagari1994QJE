# Aiyagari (1994 QJE) REMARK
#
#   docker build -t aiyagari1994qje .
#   docker run --rm -v "$PWD/results:/app/results" aiyagari1994qje
#
# The executed notebooks land in ./results. Python packages are pinned in uv.lock.

FROM python:3.9.23-slim-bookworm@sha256:7bffea15bcc3d7fb87cf10a027986203e4281e078fa2f5b234c30fca291f0834

COPY --from=ghcr.io/astral-sh/uv:0.8.13 /uv /uvx /usr/local/bin/

# git: dolark is installed from a pinned commit on GitHub
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

ENV UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Build the environments first, so that editing a notebook does not rebuild them
COPY pyproject.toml uv.lock .python-version setup_envs.sh ./
RUN ./setup_envs.sh

COPY . .

CMD ["./reproduce.sh"]
