# docker/AGENTS.md

How to adapt the agent sandbox (`sandbox/`) and runner (`runner/`) to the
machine they run on. Background and setup steps are in `README.md`; this
file covers what differs from host to host.

## Rule: the repo stays host-neutral

Nothing under `docker/` names a particular machine: no hostnames, IPs,
tailnet names, usernames or tokens. Everything host-specific lives outside
the repo, in `~/.config/lavender/` of the user that runs the containers
(`gitlab-runner` on a runner host). If a setup seems to need a host name in
a repo file, add a variable with a neutral default instead.

## Host files

All in `~/.config/lavender/`:

| File | Holds | Needed |
|------|-------|--------|
| `host.env` | This machine's LLM settings (below) | Only to change a default |
| `llm.env` | `LLM_API_KEY=...`, sent to the LLM server as a Bearer token (chmod 600) | Only if the server wants a key |
| `gitlab*.env` | `GITLAB_TOKEN=...`; the project env file's `GITLAB_TOKEN_FILE` names which (chmod 600) | Yes |
| `iron-proxy/ca.{crt,key}` | The proxy's CA, from `sandbox/gen-ca.sh` | Yes |
| `opencode.json` (any name) | A replacement opencode config, if `LAV_OPENCODE_JSON` points at it | No |
| `models.json` | Models an issue may pick with a `model::` label, and their limits (below) | Only to offer more than one model |

## `host.env`

A compose env file, read after the project env file
(`sandbox/lavender.env`, …), so its values win. `runner/solve.sh` adds it
automatically when it exists (`LAV_HOST_ENV` overrides the path). By hand:

```sh
C="docker compose -f docker/sandbox/compose.yml --env-file docker/sandbox/lavender.env --env-file ~/.config/lavender/host.env"
```

| Variable | Default | Meaning |
|----------|---------|---------|
| `LAV_LLM_HOST` | `host.docker.internal` (this machine) | Host of the OpenAI-compatible LLM server. The proxy allows only this host. |
| `LAV_LLM_PORT` | `8080` | Its port (llama-server's default). |
| `LAV_LLM_MODEL` | `default` | The model opencode asks for, unless the issue picks another. llama-server serving one model accepts any name; llama-swap needs a real one. |
| `LAV_LLM_THINKING` | `max` | Thinking level for issues without a `thinking::` label: `off`, `low`, `medium`, `high` or `max`. |
| `LAV_LLM_ONE_MODEL` | `0` | `1` if the server holds one model at a time (llama-swap swapping big models). The runner then skips issues whose model differs from the one already running, and a later job takes them. |
| `LAV_MODELS_JSON` | `~/.config/lavender/models.json` | Where `models.json` is. |
| `LAV_LLM_CONTEXT` | `0` (unknown) | Tokens per request the server accepts: llama-server's `-c` divided by `--parallel` (its `n_ctx` per slot). opencode compacts the session before it gets there. With `0` it compacts only after the server rejects a request, and `opencode run` then exits 1. |
| `LAV_LLM_OUTPUT` | `32000` | Most tokens per reply. opencode also keeps this much free when deciding to compact. |
| `LAV_OPENCODE_JSON` | `sandbox/opencode.json` | A replacement opencode config, e.g. listing several models. |
| `LAV_LLM_PROVIDER` | `local` | The provider id in that config; the runner asks opencode for `<provider>/<model>`. |

Example, for an LLM server elsewhere on a tailnet:

```sh
LAV_LLM_HOST=llm-box.example-tailnet.ts.net
LAV_LLM_MODEL=qwen3-27b
LAV_LLM_CONTEXT=131072
```

## Model and thinking level per issue

An issue picks them with labels; without one, `host.env` decides.

- `model::<id>`: `LAV_LLM_MODEL`, or any model listed in `models.json`. An
  unknown model fails the run with a comment that lists the ones offered.
- `thinking::<level>`: how much the model may think per reply.

| Level | Sent with each request | Effect |
|-------|------------------------|--------|
| `off` | `chat_template_kwargs: {enable_thinking: false}` | No thinking |
| `low` | `thinking_budget_tokens: 1024` | Thinking capped at 1024 tokens |
| `medium` | `thinking_budget_tokens: 4096` | 4096 |
| `high` | `thinking_budget_tokens: 16384` | 16384 |
| `max` | nothing | Unrestricted (the server's default) |

The levels are opencode variants in `sandbox/opencode.json`; the budgets are
set there. They are llama-server request fields, checked against
llama-server with `--jinja` and a Qwen3 chat template. `reasoning_effort`
and `reasoning_budget` were not honoured per request there.

`models.json` maps each extra model to its limits, as for `LAV_LLM_CONTEXT`
and `LAV_LLM_OUTPUT` (output defaults to 32000):

```json
{
  "qwen3-27b": { "context": 131072 },
  "qwen3-8b": { "context": 65536, "output": 16000 }
}
```

List the default model there too to keep its limits in one place.

The runner's `limit` still caps runs at once. Runs beyond the server's free
slots (llama-server's `--parallel`) work, but wait for a slot on every
request.

## Picking `LAV_LLM_HOST`

opencode reaches the server through iron-proxy, so the name must resolve
**inside the proxy container** to an address the proxy will dial. The proxy
refuses loopback (`127.0.0.0/8`): a 502 whose proxy log says
`denied by upstream_deny_cidrs` means the name resolved to it. Private and
Tailscale ranges are allowed.

- **Server on the same machine (the default).** Docker maps
  `host.docker.internal` to the host's bridge address. The server must listen
  there, not only on `127.0.0.1`: use `--host 0.0.0.0` (or llama-swap's
  `--listen :8080`), and if a firewall is on, allow the Docker bridge
  networks (`172.16.0.0/12`) to reach the port.
  (Podman with pasta maps it to `169.254.1.2` instead, which also reaches the
  host.)
- **Server on another machine:** its DNS name, as containers resolve it.
- **Don't use this machine's own short hostname.** Ubuntu maps it to
  `127.0.1.1` in `/etc/hosts`, and Docker's DNS returns that inside
  containers too. On a tailnet, use the full MagicDNS name
  (`<host>.<tailnet>.ts.net`) instead: it resolves to the Tailscale IP
  everywhere, this machine included.

## A replacement `opencode.json`

Start from `sandbox/opencode.json`. Keep `baseURL` as
`http://{env:LAV_LLM_HOST}:{env:LAV_LLM_PORT}/v1`: opencode fills those in
from the container's environment, and a URL hard-coded to another host is
refused by the proxy. Leave out API keys (the proxy adds `LLM_API_KEY`).
Keep the `variants` too, on every model an issue can pick: opencode ignores a
variant a model lacks, so its `thinking::` label would do nothing.
To list the server's models: `curl -s http://<host>:<port>/v1/models | jq -r '.data[].id'`.

## Checking a host

```sh
$C up -d
$C exec -T sandbox opencode run "Reply with exactly the word: pong"
$C logs iron-proxy | grep chat/completions | tail -3
$C down
```

- `"action":"allow","status_code":200`: working.
- `denied by upstream_deny_cidrs`: see *Picking `LAV_LLM_HOST`*.
- `secret_unavailable ... LLM_API_KEY`: `llm.env` is missing, has no
  `LLM_API_KEY=` line, or was created after `up` (compose reads env files when
  it creates a container: `$C up -d --force-recreate iron-proxy`).
- A 502 the proxy logs as `allow` came from the server itself (e.g.
  llama-swap failing to load the model): check the server's logs.
