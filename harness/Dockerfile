# Dockerfile for the Lavender debugger sandbox.
# Extends the pre-existing localhost/lav-sandbox:latest image which has
# Ubuntu 24.04, Python 3.12.3, and the OpenGL/SDL2 libraries already installed.
#
# This Dockerfile adds:
#   - GDB (the GNU debugger)
#   - pygdbmi (Python GDB/MI interface)
#   - Xvfb (X virtual framebuffer for headless OpenGL)
#   - xauth (X authority management)
#   - strace (for debugging ptrace issues)
#
# The container must be run with:
#   --cap-add=SYS_PTRACE          (allow gdb to attach to processes)
#   --security-opt seccomp=unconfined  (allow ptrace syscalls)
#
# For ptrace to work in the container, you also need:
#   - The HOST kernel must have ptrace_scope=1 or lower (check with
#     `cat /proc/sys/kernel/yama/ptrace_scope`)
#   - On the host, run: sudo sysctl -w kernel.yama.ptrace_scope=0
#
# Usage:
#   docker build -t lav-sandbox-debug -f harness/Dockerfile .
#   docker run --cap-add=SYS_PTRACE --security-opt seccomp=unconfined \
#     -v /path/to/lavender:/work/lavender \
#     -it lav-sandbox-debug
#
# Or use docker-compose (see docker-compose.yml)

FROM localhost/lav-sandbox:latest

# Install GDB, Xvfb, xauth, strace, and Python build dependencies.
# apt-get is used because the base image is Ubuntu 24.04.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gdb \
    xvfb \
    xauth \
    strace \
    ltrace \
    iproute2 \
    procps \
    python3-pip \
    python3-venv \
    python3-dev \
    libcglm-dev \
    libpulse-dev \
    libasound2-dev \
    libxi6 \
    libxrandr2 \
    libxcursor1 \
    libxfixes3 \
    libxrender1 \
    libxss1 \
    libxxf86vm1 \
    libxinerama1 \
    && rm -rf /var/lib/apt/lists/*

# Install pygdbmi.
# Ubuntu 24.04 enforces PEP 668 (externally-managed-environment), so we
# use --break-system-packages or create a venv. For simplicity in the
# debug container, we use --break-system-packages.
RUN pip3 install --no-cache-dir --break-system-packages pygdbmi

# Set up the work directory.
# Mount your Lavender source here when running the container.
WORKDIR /work

# Set up the display environment for headless OpenGL.
# LIBGL_ALWAYS_SOFTWARE=1 is REQUIRED for Xvfb — there's no hardware GL
# in a headless container, so we must use Mesa's software rasterizer (swrast).
ENV DISPLAY=:99.0
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
ENV SDL_VIDEODRIVER=x11

# The container will run the harness launch script by default.
# See harness/container_entrypoint.sh for the startup sequence.
COPY harness/container_entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/container_entrypoint.sh

ENTRYPOINT ["/usr/local/bin/container_entrypoint.sh"]
CMD ["bash"]
