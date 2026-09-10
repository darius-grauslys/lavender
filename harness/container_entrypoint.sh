#!/bin/bash
# container_entrypoint.sh — Entry point for the Lavender debugger container.
#
# This script:
# 1. Starts Xvfb (X virtual framebuffer) on DISPLAY=:99.0
# 2. Sets up X authorization
# 3. Starts PulseAudio (for SDL2 audio in the container)
# 4. Execs into the command (default: bash)
#
# The key insight: by running the GDB-attached process approach INSIDE the
# container with SYS_PTRACE, we avoid the pygdbmi subprocess/GDI issue
# entirely. The program runs natively (gets a proper display via Xvfb,
# proper audio via PulseAudio), and GDB attaches to it via ptrace — which
# is allowed with --cap-add=SYS_PTRACE and --security-opt seccomp=unconfined.

set -e

# ---------------------------------------------------------------------------
# 1. Start Xvfb (X virtual framebuffer) for headless OpenGL.
# ---------------------------------------------------------------------------
DISPLAY_NUM=99
export DISPLAY=":${DISPLAY_NUM}.0"

# Start Xvfb in the background.
# -screen 0 1920x1080x24 matches the Lavender game's default resolution.
# -ac disables access control (avoids X authorization issues).
if command -v Xvfb >/dev/null 2>&1; then
    echo "[entrypoint] Starting Xvfb on DISPLAY=${DISPLAY}..."
    Xvfb :${DISPLAY_NUM} -screen 0 1920x1080x24 -ac -nolisten tcp &
    XVFB_PID=$!
    echo "[entrypoint] Xvfb started (PID=${XVFB_PID})"

    # Wait for Xvfb to be ready.
    for i in $(seq 1 10); do
        if [ -e "/tmp/.X11-unix/X${DISPLAY_NUM}" ]; then
            echo "[entrypoint] Xvfb is ready"
            break
        fi
        sleep 0.5
    done
else
    echo "[entrypoint] WARNING: Xvfb not found — OpenGL context may fail"
    echo "[entrypoint] Set DISPLAY manually or install xvfb"
fi

# ---------------------------------------------------------------------------
# 2. Start PulseAudio (for SDL2 audio subsystem).
#    SDL2 expects a running PulseAudio or ALSA server. In the container,
#    we start PulseAudio in system mode.
# ---------------------------------------------------------------------------
if command -v pulseaudio >/dev/null 2>&1; then
    echo "[entrypoint] Starting PulseAudio..."
    pulseaudio --start --system --disown 2>/dev/null || \
        echo "[entrypoint] PulseAudio start failed (non-fatal)"
fi

# ---------------------------------------------------------------------------
# 3. Verify the environment.
# ---------------------------------------------------------------------------
# Ensure software GL rendering is enabled (Xvfb has no hardware GL).
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe

echo "[entrypoint] Environment:"
echo "  DISPLAY=${DISPLAY}"
echo "  SDL_VIDEODRIVER=${SDL_VIDEODRIVER:-unset}"
echo "  LIBGL_ALWAYS_SOFTWARE=${LIBGL_ALWAYS_SOFTWARE}"
echo "  MESA_LOADER_DRIVER_OVERRIDE=${MESA_LOADER_DRIVER_OVERRIDE:-unset}"
echo "  GDB: $(which gdb 2>/dev/null || echo 'not found')"
echo "  Python: $(python3 --version 2>&1)"
if python3 -c "import pygdbmi" 2>/dev/null; then
    echo "  pygdbmi: available"
else
    echo "  pygdbmi: NOT found"
fi

# ---------------------------------------------------------------------------
# 4. Exec into the command (default: bash).
#    Using exec replaces the shell process so signals are properly forwarded.
# ---------------------------------------------------------------------------
echo "[entrypoint] Ready. Running: $@"

exec "$@"
