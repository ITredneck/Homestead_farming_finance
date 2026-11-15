# syntax=docker/dockerfile:1
# The Homestead Finance app image. Build context: the repository root, because the
# image needs backend/ and frontend/. CI builds one image per architecture with the
# home-assistant/builder actions; see .github/workflows/image.yml.

# ---- Frontend: built once, on the build machine's own architecture ----
FROM --platform=$BUILDPLATFORM node:24-alpine AS frontend
WORKDIR /src/frontend
RUN corepack enable
COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

# ---- App: Home Assistant's Python base image (Alpine, s6-overlay v3) ----
# A fixed, dated tag: the Supervisor no longer passes BUILD_FROM, and builds stay reproducible.
FROM ghcr.io/home-assistant/base-python:3.14-alpine3.24-2026.11.0

COPY --from=ghcr.io/astral-sh/uv:0.10.12 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /opt/homestead_finance
# Dependencies first, so code changes don't reinstall them.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/src ./src
RUN uv sync --frozen --no-dev --no-editable && rm -rf src

COPY --from=frontend /src/frontend/dist /opt/homestead_finance/static
COPY docker/rootfs /
# Windows checkouts don't keep the executable bit, so set it here.
RUN chmod a+x \
    /etc/s6-overlay/s6-rc.d/homestead-finance/run \
    /etc/s6-overlay/s6-rc.d/homestead-finance/finish

ARG BUILD_VERSION=dev
ENV PATH="/opt/venv/bin:${PATH}" \
    HF_DATA_DIR=/data \
    HF_STATIC_DIR=/opt/homestead_finance/static \
    HF_VERSION=${BUILD_VERSION}

LABEL org.opencontainers.image.title="Homestead Finance" \
      org.opencontainers.image.description="Farm finance and records for homesteads" \
      org.opencontainers.image.source="https://github.com/ITredneck/Homestead_farming_finance" \
      org.opencontainers.image.licenses="AGPL-3.0-or-later"
