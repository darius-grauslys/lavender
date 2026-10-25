#!/bin/sh
# Generate the CA iron-proxy uses to intercept the sandbox's HTTPS traffic.
# Written outside the repo; the key is only ever mounted into iron-proxy.
set -e

dir="${HOME}/.config/lavender/iron-proxy"
mkdir -p "$dir"
chmod 700 "$dir"

if [ -f "$dir/ca.key" ]; then
    echo "CA already exists in $dir (delete it to regenerate)"
    exit 0
fi

openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes \
    -keyout "$dir/ca.key" -out "$dir/ca.crt" -days 825 \
    -subj "/CN=Lavender sandbox iron-proxy CA" \
    -addext "basicConstraints=critical,CA:TRUE" \
    -addext "keyUsage=critical,keyCertSign,cRLSign"
chmod 600 "$dir/ca.key"
chmod 644 "$dir/ca.crt"
echo "Wrote $dir/ca.crt and $dir/ca.key"
