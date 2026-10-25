# Lavender sandbox images. Two stages:
#
#   base   lav-sandbox: Ubuntu 24.04 + make/bear/git + SDL2/GLEW/cglm +
#          clang/clangd/lld 21 + Python. ~1 GB, mostly LLVM. Originally
#          ~/Projects/LangGraph/lav_pipelines/docker/Dockerfile; that pipeline
#          (and harness/Dockerfile) use it with /lavender ro + /project rw.
#   agent  lav-sandbox-agent: base + Xvfb (headless GL), opencode, the
#          entrypoint and the lav-gitlab / lav-screenshot helpers.
#          This is what compose.yml runs. Changing it only rebuilds the
#          last few layers, never LLVM.
#
# Build (podman or docker), from the repo root:
#   docker build --target base  -t lav-sandbox       docker/sandbox
#   docker build --target agent -t lav-sandbox-agent docker/sandbox
#
# Security properties of the agent sandbox (see compose.yml):
#   - No secrets in the container. GitLab access goes through iron-proxy,
#     which injects the token on the host side.
#   - Only network route is the proxy, on an internal-only network.
#   - The repo is cloned from GitLab into /work/repo at start; nothing on
#     the host is mounted, and the proxy refuses git pushes.

# ==========================================================================
# base
# ==========================================================================
FROM ubuntu:24.04 AS base

LABEL maintainer="Lavender Pipeline Runner"
LABEL description="Sandboxed agent execution environment for Lavender game projects"

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# --------------------------------------------------------------------------
# 1. System packages: build essentials + SDL2 + GL dependencies
# --------------------------------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
        # Core build tools
        make \
        bear \
        git \
        wget \
        gnupg \
        ca-certificates \
        software-properties-common \
        # SDL2 + graphics libraries (needed to link Lavender SDL platform)
        libsdl2-dev \
        libglew-dev \
        libgl-dev \
        # cglm (header-only math library)
        libcglm-dev \
        # Python for Lavender tools
        python3 \
        python3-pip \
        python3-venv \
        # Performance metrics utilities (perf_summary.sh)
        bc \
        gawk \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# 2. LLVM/Clang 21 from apt.llvm.org (matches host Void Linux clang-21)
# --------------------------------------------------------------------------
RUN wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key \
        | tee /etc/apt/trusted.gpg.d/apt.llvm.org.asc \
    && echo "deb http://apt.llvm.org/noble/ llvm-toolchain-noble-21 main" \
        > /etc/apt/sources.list.d/llvm-21.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        clang-21 \
        clangd-21 \
        lld-21 \
    && rm -rf /var/lib/apt/lists/*

# Symlink clang-21 / clangd-21 so they're on PATH without version suffix
RUN ln -sf /usr/bin/clang-21   /usr/local/bin/clang-21 \
    && ln -sf /usr/bin/clangd-21 /usr/local/bin/clangd-21 \
    && ln -sf /usr/bin/clang-21  /usr/local/bin/clang \
    && ln -sf /usr/bin/clangd-21 /usr/local/bin/clangd \
    && ln -sf /usr/bin/lld-21    /usr/local/bin/lld \
    && ln -sf /usr/bin/ld.lld-21 /usr/local/bin/ld.lld

# --------------------------------------------------------------------------
# 3. Python packages for Lavender tools
# --------------------------------------------------------------------------
RUN pip3 install --no-cache-dir --break-system-packages \
        Pillow \
        lsprotocol \
        pygls

# --------------------------------------------------------------------------
# 4. Mount points (created as empty dirs, populated at runtime)
# --------------------------------------------------------------------------

# Lavender engine — mounted read-only at runtime
RUN mkdir -p /lavender
# Game project — mounted read-write at runtime
RUN mkdir -p /project

# --------------------------------------------------------------------------
# 5. Environment
# --------------------------------------------------------------------------
ENV LAVENDER_DIR=/lavender
ENV PYTHONUNBUFFERED=1

# Default working directory is the game project
WORKDIR /project

# Keep the container alive for `podman exec` / `docker exec` commands.
# STOPSIGNAL SIGKILL: `sleep` as PID 1 ignores SIGTERM, which causes
# `podman stop` to hang for 10+ seconds waiting for the grace period to
# expire before falling back to SIGKILL.  There is no state to flush in
# a sandbox, so skip the grace period entirely.
STOPSIGNAL SIGKILL
CMD ["sleep", "infinity"]

# ==========================================================================
# agent
# ==========================================================================
FROM base AS agent

# Headless graphics: Xvfb gives SDL an X display; Mesa's llvmpipe (already
# in base via libgl/libsdl2) renders GL 4.5 core on the CPU. No host GPU or
# display needed. The entrypoint starts Xvfb.
RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb \
        xauth \
    && rm -rf /var/lib/apt/lists/*

# opencode, the agent harness. Single static binary; its provider SDKs are
# bundled, so it needs no npm access at runtime.
ARG OPENCODE_VERSION=1.18.19
ARG OPENCODE_SHA256=7bb35487c55f9957f5d91ae60be6fa49fc8f74629c210c1719ed75fdbf7e2bd9
RUN wget -qO /tmp/opencode.tgz \
        https://github.com/anomalyco/opencode/releases/download/v${OPENCODE_VERSION}/opencode-linux-x64.tar.gz \
    && echo "${OPENCODE_SHA256}  /tmp/opencode.tgz" | sha256sum -c - \
    && tar -xzf /tmp/opencode.tgz -C /usr/local/bin opencode \
    && rm /tmp/opencode.tgz

ENV DISPLAY=:99 \
    LIBGL_ALWAYS_SOFTWARE=1 \
    GALLIUM_DRIVER=llvmpipe \
    SDL_VIDEODRIVER=x11 \
    SDL_AUDIODRIVER=dummy
# opencode would otherwise reach out to models.dev, npm, its update server
# and LSP download sites; the proxy blocks all of those anyway.
ENV OPENCODE_DISABLE_AUTOUPDATE=1 \
    OPENCODE_DISABLE_MODELS_FETCH=1 \
    OPENCODE_DISABLE_SHARE=1 \
    OPENCODE_DISABLE_LSP_DOWNLOAD=1 \
    OPENCODE_DISABLE_DEFAULT_PLUGINS=1

RUN mkdir -p /work

COPY entrypoint.sh /usr/local/bin/lav-sandbox-entrypoint
COPY lav-gitlab /usr/local/bin/lav-gitlab
COPY lav-screenshot /usr/local/bin/lav-screenshot
RUN chmod +x /usr/local/bin/lav-sandbox-entrypoint /usr/local/bin/lav-gitlab \
        /usr/local/bin/lav-screenshot

WORKDIR /work

ENTRYPOINT ["/usr/local/bin/lav-sandbox-entrypoint"]
CMD ["sleep", "infinity"]
