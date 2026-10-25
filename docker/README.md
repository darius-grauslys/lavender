# docker/

| Directory | Purpose |
|-----------|---------|
| `platform/` | Toolchain images for building Lavender per backend (`sdl/`, `no_gui/`, `nds/`). `nds/` is empty; NDS builds use `devkitpro/devkitarm`. |
| `runner/` | Host side of the agent CI. `solve.sh` is the GitLab Runner job: it claims an `agent-todo` issue, runs opencode on it in a fresh sandbox, and reports back with an MR. |
| `sandbox/` | The agent execution sandbox (opencode, headless SDL/OpenGL), plus an iron-proxy egress gateway that lets the agent reach its LLM servers and open GitLab merge requests and issues without seeing any key. |

`sandbox/Dockerfile` has two stages. `base` is `lav-sandbox` (~1 GB: toolchain
plus LLVM). `agent` is `lav-sandbox-agent`, a thin layer on top, so iterating on
the sandbox never reinstalls LLVM. `harness/Dockerfile` (the gdb/Xvfb debug
image) builds `FROM localhost/lav-sandbox`; build that tag with
`docker build --target base -t lav-sandbox docker/sandbox`.

## Sandbox

```
sandbox ──(internal network, no route out)──> iron-proxy ──> git.graslocal.com
                                                         └──> anuket (llama-swap, LLMs)
```

- The sandbox holds **no secrets**. iron-proxy adds the credentials itself, and
  only for the allowlisted paths (`configs.proxy_yaml` in `sandbox/compose.yml`):
  a `PRIVATE-TOKEN` header for the GitLab API, Basic auth for git
  clone/fetch, and a Bearer key for LLM servers that need one. Every other
  request gets a 403.
- The agent harness is **opencode** (pinned in the Dockerfile). Its config,
  `sandbox/opencode.json`, has one provider, anuket's llama-swap (model list
  taken from `http://anuket:8080/v1/models`; default
  `ternary-bonsai-qwen3.8-27B-PQ2_0-XTX`), with no API key. It speaks plain
  HTTP over Tailscale, through the proxy (`HTTP_PROXY`). A
  provider added there also needs an allowlist rule in `compose.yml`, plus a
  secrets rule if it takes a key. opencode tries to fetch from
  `registry.npmjs.org` at start; the proxy refuses that, and opencode carries on.
- **Headless graphics.** The entrypoint starts Xvfb on `:99` (1280x720,
  `LAV_XVFB_SCREEN` to change, `LAV_XVFB=0` to skip). Mesa's llvmpipe renders
  OpenGL 4.5 core on the CPU, so the SDL backend runs with no GPU or display
  on the host. Measured on this 4-core host: the SDL build runs at its 60 fps
  cap; a stress test (2,000 blended 32 px quads at 1280x720) also holds ~60 fps,
  and falls to ~15 fps only at 10,000 quads. `lav-screenshot [--crop W H] OUT.png`
  saves the display as a PNG for the agent to look at. SDL audio uses the
  `dummy` driver. Use `no_gui` when no rendering is needed.
- The stack targets one GitLab project at a time, chosen by an env file
  (`sandbox/lavender.env`, `sandbox/test-issues.env`). The proxy rules, clone
  URL and token all come from that file.
- At start the sandbox clones the project into `/work/repo`, through the proxy.
  Nothing from the host is mounted except the proxy's public CA certificate.
- There is no `git push`; the proxy refuses `git-receive-pack`. `lav-gitlab mr`
  sends the branch's committed changes through the GitLab commits API (which
  creates the branch server-side) and then opens an MR. `lav-gitlab issue`
  opens an issue.

### One-time setup

1. **Container DNS (podman).** The sandbox reaches the proxy by name, which
   needs podman's netavark backend with aardvark-dns. The older CNI backend has
   no DNS without extra plugins.

   ```sh
   sudo xbps-install aardvark-dns
   mkdir -p ~/.config/containers
   printf '[network]\nnetwork_backend = "netavark"\n' >> ~/.config/containers/containers.conf
   podman info --format '{{.Host.NetworkBackend}}'   # -> netavark
   ```

   If `docker` talks to a long-running podman API service (`DOCKER_HOST` set
   to `.../podman/podman.sock`), restart that service too. It keeps the
   backend it started with. Here it is a user runit service:
   `sv restart ~/.config/service/podman-api`. Check with
   `docker network create --internal t && podman network inspect t --format '{{.DNSEnabled}}'`,
   which should print `true`; then `docker network rm t`.

   Networks and containers created under CNI must be recreated afterwards.
   `compose up` recreates its own.
2. **GitLab token, per project.** In the project, go to Settings → Access tokens
   and create a *project* access token with role **Developer**, scopes `api` and
   `read_repository`, and a short expiry. Don't use a personal token: it carries
   your own role, and as Owner/Maintainer it can push to the protected branch.
   Save it where that project's env file (`GITLAB_TOKEN_FILE`) points:

   ```sh
   mkdir -p ~/.config/lavender
   printf 'GITLAB_TOKEN=%s\n' '<token>' > ~/.config/lavender/gitlab.env
   chmod 600 ~/.config/lavender/gitlab.env
   ```

3. **Protect the default branch.** In Settings → Repository → Protected
   branches, set "Allowed to push and merge" to Maintainers. The commits API
   can write to any branch the token's role may push to, so this is what stops
   the agent from committing straight to the default branch.
4. **Proxy CA.** Run `sh docker/sandbox/gen-ca.sh`. This writes
   `~/.config/lavender/iron-proxy/ca.{crt,key}`.
5. **LLM keys.** Put keys for the LLM servers in `~/.config/lavender/llm.env`
   (chmod 600), e.g. `ANUKET_API_KEY=...`. Only iron-proxy reads it.

### Use

```sh
C="docker compose -f docker/sandbox/compose.yml --env-file docker/sandbox/lavender.env"
$C up -d --build
$C exec sandbox bash

# inside the sandbox, on a local branch with committed work:
lav-gitlab mr --branch agent/fix-foo --title "Fix foo" --description "..."
lav-gitlab issue --title "Foo is broken" --description "..." --labels bug

# opencode, interactive or one-shot:
$C exec -it sandbox opencode
$C exec -T sandbox opencode run "Build PLATFORM=sdl and screenshot the title screen"

# the SDL backend, headless (LAVENDER_DIR is /work/repo):
make -e PLATFORM=sdl && ./build/sdl/repo & sleep 5; lav-screenshot --crop 256 192 /tmp/s.png
```

To add a project, copy an env file and change its path, ID and token file. Each
env file sets its own `COMPOSE_PROJECT_NAME`, so several stacks can run at once.

The MR's base is the merge-base with the project's default branch on GitLab.
Each `lav-gitlab mr` creates a new branch. Updating an existing MR branch is not
supported yet.

> **Don't run `compose config` where others can see the output.** It reads the
> token file and prints the token.

Cloudflare sits in front of git.graslocal.com and returns 403 to Python's
default `Python-urllib` User-Agent. Any HTTP client in the sandbox must set its
own (lav-gitlab sends `lav-gitlab/1`). A 403 that the proxy log shows as
`allow` came from upstream, not from iron-proxy.

The proxy's audit log records every request (host, method, path, allowed or
denied): `$C logs iron-proxy`.

## Runner

The agent CI: GitLab issues labelled `agent-todo` are picked up oldest first,
solved by opencode in a fresh sandbox, and returned as an MR. Lavender
MRs from the agent are never merged; see the `Agent-<uuid>` exception in
`AGENTS.md`.

```
target project (schedule) ─> stub <target>.yml in dgrauslys/lav-agent-ops
                               └─ include: docker/runner/agent.yml @ lavender master
                                    └─ shell runner on this host: $LAV_RUNNER_DIR/solve.sh
                                         └─ sandbox stack (docker/sandbox/, <target>.env)
```

- `runner/agent.yml` is the job. A target never uses it directly: its CI/CD
  configuration file is a stub in `dgrauslys/lav-agent-ops`, which includes
  this file and sets `LAV_PROJECT_ENV` (an env file in `sandbox/`).
- `runner/solve.sh` is the job script. It runs **on the host**, not in the
  sandbox, and is the only part that holds the GitLab token.
- Because the job runs on the host, nothing the agent can write may change
  what runs:
  - the stub lives in another project, so GitLab reads it from that project's
    default branch, never from an agent branch;
  - the include is pinned to lavender `master`, which the agent's Developer
    token can't push to;
  - `LAV_RUNNER_DIR` points at a dedicated master clone, never a working
    tree, so checking out an agent branch for review changes nothing.

### Runner setup

1. Install GitLab Runner and register it with tag `lav-agent`, the shell
   executor, protected, and untagged jobs off. Enable it on every target
   project, not only on the project it was registered on; a job queued
   before that stays pending forever.
2. In `~/.gitlab-runner/config.toml`, set `concurrent = 1` and `limit = 1`
   (one sandbox, so one LLM session at a time), and:

   ```toml
   environment = ["DOCKER_HOST=unix:///run/user/1000/podman/podman.sock",
                  "XDG_RUNTIME_DIR=/run/user/1000",
                  "LAV_RUNNER_DIR=/home/<you>/.local/lib/lav-agent/lavender/docker/runner"]
   ```
3. Make the master clone that `LAV_RUNNER_DIR` points into, and update it
   only deliberately (`git -C … pull`):

   ```sh
   git clone -b master https://git.graslocal.com/dgrauslys/lavender ~/.local/lib/lav-agent/lavender
   ```
4. In the target project: set the CI/CD configuration file to
   `<target>.yml@dgrauslys/lav-agent-ops`, then add a pipeline schedule on the
   default branch.
