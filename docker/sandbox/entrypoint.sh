#!/bin/sh
set -e
if [ -f /etc/lav-proxy/ca.crt ]; then
    cp /etc/lav-proxy/ca.crt /usr/local/share/ca-certificates/lav-proxy.crt
    update-ca-certificates >/dev/null
fi

# Virtual display for the SDL backend (software GL via llvmpipe).
# LAV_XVFB=0 skips it, e.g. for no_gui-only work.
if [ "${LAV_XVFB:-1}" = 1 ] && [ -n "$DISPLAY" ]; then
    n=${DISPLAY#:}; n=${n%%.*}
    Xvfb ":$n" -screen 0 "${LAV_XVFB_SCREEN:-1280x720x24}" -nolisten tcp \
        >/tmp/xvfb.log 2>&1 &
    i=0
    while [ ! -e "/tmp/.X11-unix/X$n" ] && [ $i -lt 50 ]; do
        sleep 0.1; i=$((i + 1))
    done
    [ -e "/tmp/.X11-unix/X$n" ] || { echo "[sandbox] Xvfb failed:"; cat /tmp/xvfb.log; }
fi

if [ -n "$LAV_REPO_URL" ] && [ ! -d /work/repo/.git ]; then
    git clone --quiet ${LAV_REPO_BRANCH:+--branch "$LAV_REPO_BRANCH"} \
        "$LAV_REPO_URL" /work/repo
    echo "[sandbox] cloned $LAV_REPO_URL -> /work/repo ($(git -C /work/repo rev-parse --abbrev-ref HEAD))"
fi
exec "$@"
