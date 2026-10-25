# CI checkpoint: agent sandbox + GitLab runner (2026-10-24)

Goal: GitLab issues labelled `agent-todo` get picked up automatically (oldest
first), solved by opencode in an isolated sandbox, and returned as an MR that
`Closes #N`, with the transcript kept as a CI artifact. Trial project:
`dgrauslys/test-issues` (ID 10). Nothing is committed to Lavender_Dev yet.

**Status: end-to-end CI works.** A scheduled pipeline claimed issue #5, ran
opencode in a sandbox, and opened MR !3. The issue comment links the MR and
the transcript artifact (job 19).

## Done and verified

- **Sandbox** (`docker/sandbox/`, image `lav-sandbox-agent`):
  - Ubuntu with LLVM 21 and SDL2. Clones the project from GitLab at start.
  - iron-proxy is the only network route out. It injects the GitLab token and
    `ANUKET_API_KEY` (from `~/.config/lavender/llm.env`), so the sandbox
    holds no secrets.
  - No `git push`. `lav-gitlab mr` uses the GitLab commits API, then opens
    an MR.
  - Headless graphics: Xvfb `:99` + Mesa llvmpipe (GL 4.5). The SDL build
    runs at ~60 fps. `lav-screenshot` captures the display.
  - opencode 1.18.19 (pinned + sha256). Config `docker/sandbox/opencode.json`
    is anuket only, generated from live `http://anuket:8080/v1/models`.
  - Default model `anuket-local/ternary-bonsai-qwen3.8-27B-PQ2_0-XTX`. The
    non-XTX variant crashes on anuket's side.
  - Details: `docker/README.md`.
- **Orchestration:** GitLab Runner. Sortie was rejected: it needs opencode
  2.x and has no sandboxing.
- **Ops project:** live as `dgrauslys/test-issue-ops` (no "s" after "issue"),
  to be renamed `dgrauslys/lav-agent-ops` (step 1).
  - Cloned at `~/Projects/test-issue-ops`.
  - Live (pushed): `agent.yml`, the full job config, which runs
    `/tmp/lav-agent-ci/solve.sh`. test-issues' CI/CD configuration file is
    `agent.yml@dgrauslys/test-issue-ops`.
  - Staged locally, not pushed: `agent.yml` replaced by per-target stubs
    `test-issues.yml` and `lavender.yml`, plus a real README. See step 1.
- **Runner:** `lav-agent-host`, GitLab runner id 2.
  - Shell executor, tag `lav-agent`, protected, untagged jobs off.
  - It was registered on test-issue-ops, so it was also enabled on test-issues
    (`POST projects/10/runners`). Without that, jobs stayed pending forever.
    The instance runner `runner001` (id 1) can't take these jobs because it
    lacks the tag.
  - `~/.gitlab-runner/config.toml`:
    - `concurrent = 1`, `limit = 1`: one sandbox, so one LLM session at a time;
    - `environment` sets the podman `DOCKER_HOST`, `XDG_RUNTIME_DIR` and
      `LAV_RUNNER_DIR` (the last added 2026-10-25, unused until step 1 lands);
    - backups: `config.toml.bak` (original), `config.toml.bak2` (before
      `LAV_RUNNER_DIR`).
  - It runs as the runit user service `~/.config/service/gitlab-runner`.
- **Schedule:** id 1, "agent solve", `*/5 * * * *` on `main`, active.
  - Manage it under Build → Pipeline schedules, which has a play button.
  - The UI's "Run pipeline" button is now labelled **New pipeline**.
  - Runs with no `agent-todo` issue exit in seconds ("No open agent-todo
    issues.").
- **`solve.sh`** (live copy still `/tmp/lav-agent-ci/solve.sh`; the repo
  copy is `docker/runner/solve.sh`, see step 1):
  1. claims the oldest `agent-todo` issue under `flock`;
  2. relabels it `agent-doing`;
  3. starts the sandbox stack with `-p lav-agent-10-<iid>`;
  4. runs `opencode run --auto --format json` under a timeout;
  5. exports the transcript to `agent-run/`;
  6. opens the MR via `lav-gitlab mr`;
  7. comments on the issue (last commit message + MR link + transcript link);
  8. relabels it `agent-review`, or `agent-failed` if there were no changes;
  9. tears the stack down.

## Planned: near-real-time triggering (design agreed 2026-10-25, not built)

Replace the 5-minute schedule with a poller that starts runs within about
20 seconds of an issue being opened or commented on.

**Why not webhooks:** a webhook is GitLab making an HTTP POST *to us*.
git.graslocal.com runs at my brother's house behind Cloudflare. Its server
can't reach this host, and `dgrauslys` isn't an instance admin, so we can't
change Admin → Network → Outbound requests either. Webhooks are on hold.
Revisit if cloudflared runs on this host with a `hook.graslocal.com` route,
which needs access to the Cloudflare account.

**Flow:**
1. An issue with the opt-in label (`agent`) is opened, or a human comments
   on it.
2. **`lav-agent-watch`**, a runit service on this host that restarts itself,
   polls every ~20s using outbound connections only:
   - `GET /projects/10/issues?labels=agent&updated_after=<cursor>&order_by=updated_at&sort=asc`;
   - then each issue's notes, for comments since the last seen note id;
   - the cursor (timestamp + last note id) is saved to a file, so a restart
     catches up instead of losing events.
3. **It drops the pipeline's own events before anything is queued:**
   - system notes (`system: true`: "mentioned in !N", label notes, …);
   - notes authored by the bot (user **11**,
     `project_10_bot_…`, which is what the pipeline token acts as);
   - issue changes made by user 11 (the pipeline's relabels);
   - edited comments, non-Issue notes, and issues without the opt-in label.
4. For each relevant issue it calls `POST /projects/10/trigger/pipeline` with
   `ISSUE_IID=N`, using a pipeline trigger token held by the poller only.
   - The queue is GitLab's pending jobs. The concurrency cap is the runner's
     `limit = 1`, so the runner takes the next pending job by itself.
   - When raising the limit, add `resource_group: issue-$ISSUE_IID` so no
     two runs touch one branch.
5. `solve.sh` takes `ISSUE_IID` and works from current state, not the event:
   - it re-fetches the issue and thread from the API;
   - it exits in seconds if there is no human comment newer than the bot's
     last one. Duplicate triggers are harmless, and that is the second
     guard against self-triggering loops.
   - It runs opencode with the issue body plus the whole human comment thread,
     with the newest comment flagged as what to act on.
   - When opencode exits (not "on the final commit", since the agent may
     commit several times), it commits leftovers, pushes, comments,
     relabels and tears the sandbox down.

**Branches:**
- **Name:** `Agent-<uuid>`, where the UUID is a UUIDv5 of the issue
  metadata, e.g.
  `uuidgen --sha1 --namespace <fixed lav-agent UUID> --name "git.graslocal.com/10/issue/<issue id>"`.
  It's deterministic, so it can always be recomputed.
- **Tracking:** the bot's first comment on an issue is
  `Issue Acquired, branch-id: Agent-<uuid>`.
- **New vs resume:** the test is whether a marker from user 11 exists,
  not whether the issue has comments (a human may comment first, or the
  label may be added to an old issue).
  - No marker: new branch, post the marker, open the MR.
  - Marker exists: resume. The sandbox clones with
    `LAV_REPO_BRANCH=Agent-<uuid>` (the entrypoint already supports it), and
    new commits go onto the existing branch. That needs `lav-gitlab commit`
    (next step 3), and the open MR updates by itself.
- **The sandbox must be on `Agent-<uuid>` before opencode starts.**
  AGENTS.md lifts its no-edit rule for `.c`/`.h` files only on branches
  named `Agent-<uuid>`. A new run must `git checkout -b Agent-<uuid>` in
  the clone first, or opencode will refuse to edit source files.

**MR lifecycle (Lavender rule, agreed 2026-10-25):** agent MRs are
**never merged**. The human reads the MR, writes every line himself (with
changes where he wants them), then closes it.
- Open MRs as **Draft**, so they can't be merged by accident.
- `Closes #N` in the MR never fires. The human's own commit closes the
  issue, or he closes it by hand. `agent-review` means "waiting for the
  human to rewrite it".
- Resume onto `Agent-<uuid>` only while its MR is open. After the MR is
  closed, the human's rewrite no longer matches the branch, so a new comment
  starts a new branch from master. Add a generation number to the UUIDv5
  name (`…/issue/<id>/<gen>`).
- Delete agent branches when their MRs close; the closed MR still shows the
  diff. Consider keeping transcripts longer than 90 days for Lavender.

**Other changes:**
- `docker/runner/agent.yml`: add `$CI_PIPELINE_SOURCE == "trigger"` to `workflow: rules`.
- Keep the schedule, but hourly, as a safety net; or disable it once the
  poller is proven.
- Consider letting only commenters with Developer access or above trigger
  runs, since comments go into the prompt. This matters more on Lavender.

## Next steps

Build order for the plan above: 1 → 3 → poller (new step 6) → step 2 and
housekeeping.

1. **Make the runner portable (in progress).** The job now lives in this
   repo; see `docker/README.md` → *Runner* for the design and setup.
   - Done locally (2026-10-25):
     - `docker/runner/agent.yml` (generic job) and `docker/runner/solve.sh`
       (now requires `LAV_PROJECT_ENV`; finds `sandbox/` next to itself);
     - ops repo: stubs `test-issues.yml` (includes from `doc-gen`, trial
       only) and `lavender.yml` (includes from `master`), README;
     - runner `config.toml`: `LAV_RUNNER_DIR=~/.local/lib/lav-agent/lavender/docker/runner`.
   - Remaining, in order:
     1. human: commit `docker/runner/` (and the doc changes) on `doc-gen`
        and push `doc-gen` to the `gitlab` remote;
     2. clone `~/.local/lib/lav-agent/lavender` (on `doc-gen` for the
        trial; switch it to `master` once `docker/runner/` is merged);
     3. rename the ops project to `lav-agent-ops`, commit and push the stubs;
     4. set test-issues' CI/CD configuration file to
        `test-issues.yml@dgrauslys/lav-agent-ops`;
     5. play the schedule once to confirm;
     6. delete `/tmp/lav-agent-ci` and its backup.
   - Steps 3 and 4 leave a short window where scheduled runs fail; harmless
     with no `agent-todo` issues open.
2. **Branch restriction for the agent.** The Developer token's commits API can
   write any unprotected branch. Options:
   - protect `*` plus a per-run branch rule;
   - or a grpc body-check in iron-proxy.
   - While there, make it take `ISSUE_IID` and add the marker comment, UUID
     branches and the "anything new?" check (see the plan above).
3. **Updating an existing MR branch:** add a `lav-gitlab commit`. The resume
   flow needs it.
4. **Housekeeping:**
   - rotate the test-issues token (it was pasted in chat);
   - review, then close MRs !1, !2 and !3 and issues #3, #4 and #5;
   - prune dangling images;
   - retire or rebuild `lav-sandbox-debug` (`harness/Dockerfile`), ~1 GB;
   - disk is at ~9 GB free (2026-10-25), so state the space cost before any build.
5. **Roll out to Lavender:** apply the same setup to `dgrauslys/lavender`
   (ID 6): merge `docker/runner/` to master, point the master clone at
   master, set lavender's CI/CD configuration file to
   `lavender.yml@dgrauslys/lav-agent-ops`, enable runner 2 on lavender, and
   add a schedule. `lavender.env` and its token already exist (check).
6. **Poller:**
   - write `lav-agent-watch` and its runit service;
   - create a pipeline trigger token on test-issues;
   - add `trigger` to `workflow: rules`;
   - create the `agent` label;
   - slow the schedule to hourly.

## Gotchas

- Never print GitLab tokens or run `docker compose config` unfiltered (it
  prints the token). The same goes for `~/.gitlab-runner/config.toml`
  (filter out `token` lines).
- `docker` = podman via `DOCKER_HOST`, served by the runit service
  `~/.config/service/podman-api`. Restart it after podman config changes.
- Cloudflare in front of git.graslocal.com returns 403 to the `Python-urllib`
  User-Agent; always set one.
- `glab` is logged in on the host as `dgrauslys`. `glab api` is the easy way
  to change project settings, runners and schedules.
- A job queued before its runner was attached to the project stays pending.
  Cancel it and re-trigger.
- Pipelines triggered via the API (`POST /pipeline`) have source `api`, which
  `workflow: rules` reject. Trigger by playing the schedule instead.

## Appendix: trial file backup

The live pipeline still runs `/tmp/lav-agent-ci/solve.sh`. A copy is in
`~/.config/lavender/lav-agent-ci-backup/`; if `/tmp` was wiped, restore it with
`cp -r ~/.config/lavender/lav-agent-ci-backup /tmp/lav-agent-ci`. Delete both
once step 1 is confirmed.
