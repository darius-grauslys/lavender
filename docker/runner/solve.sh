#!/bin/bash
# One CI job: claim the oldest open agent-todo issue, run opencode on it in a
# fresh sandbox on an Agent-<uuid> branch, open a Draft MR (never merged), and
# report back on the issue.
# Runs on the host (shell runner). The GitLab token is read here and used
# only from the host; it is never passed into the sandbox.
#
# Issue labels: agent-todo -> agent-doing -> agent-review | agent-failed
set -euo pipefail

SANDBOX_DIR=${LAV_SANDBOX_DIR:-$(realpath "$(dirname "$0")/../sandbox")}
# Set by the ops stub, e.g. lavender.env; a bare name is looked up in SANDBOX_DIR.
PROJECT_ENV=${LAV_PROJECT_ENV:?LAV_PROJECT_ENV not set (the ops stub sets it)}
[[ $PROJECT_ENV == */* ]] || PROJECT_ENV=$SANDBOX_DIR/$PROJECT_ENV
# This machine's LLM settings, if any (see docker/AGENTS.md).
HOST_ENV=${LAV_HOST_ENV:-$HOME/.config/lavender/host.env}
AGENT_TIMEOUT=${AGENT_TIMEOUT:-45m}
OUT=${CI_PROJECT_DIR:-$PWD}/agent-run
ARTIFACTS_URL=${CI_JOB_URL:+$CI_JOB_URL/artifacts/browse/agent-run/}
mkdir -p "$OUT"

set -a
. "$PROJECT_ENV"
. "$GITLAB_TOKEN_FILE"
set +a

api() {  # api METHOD PATH [curl args...]
    curl -sSf -A lav-agent-ci/1 -H "PRIVATE-TOKEN: $GITLAB_TOKEN" -X "$1" \
        "https://$GITLAB_HOST/api/v4/projects/$GITLAB_PROJECT_ID$2" "${@:3}"
}
relabel() { api PUT "/issues/$iid" --data-urlencode "add_labels=$2" \
                --data-urlencode "remove_labels=$1" >/dev/null; }
note() { api POST "/issues/$iid/notes" --data-urlencode "body=$1" >/dev/null; }

# --- claim (parallel jobs share this host, so a file lock is enough) --------
exec 9>/tmp/lav-agent-claim.lock
flock 9
issue=$(api GET "/issues?state=opened&labels=agent-todo&order_by=created_at&sort=asc&per_page=1" \
        | jq -c '.[0] // empty')
if [ -z "$issue" ]; then
    echo "No open agent-todo issues."
    exit 0
fi
iid=$(jq -r .iid <<<"$issue")
title=$(jq -r .title <<<"$issue")
relabel agent-todo agent-doing
flock -u 9
# Every way out below reports on the issue first and sets reported=1. Any
# other exit (a command failing under set -e) would leave the issue on
# agent-doing with no word, so say so here; then tear the sandbox down.
reported=0
on_exit() {
    if [ "$reported" = 0 ]; then
        note "Agent run for #$iid stopped on an error in solve.sh.${CI_JOB_URL:+ Log: $CI_JOB_URL}" || true
        relabel agent-doing agent-failed || true
    fi
    [ -z "${C+x}" ] || "${C[@]}" down >/dev/null 2>&1 || true
}
trap on_exit EXIT
echo "Claimed #$iid: $title"
jq . <<<"$issue" >"$OUT/issue.json"

# --- sandbox ----------------------------------------------------------------
C=(docker compose -p "lav-agent-$GITLAB_PROJECT_ID-$iid"
   -f "$SANDBOX_DIR/compose.yml" --env-file "$PROJECT_ENV")
[ -f "$HOST_ENV" ] && C+=(--env-file "$HOST_ENV")
"${C[@]}" up -d --quiet-pull 2>&1 | tail -n 2
# The entrypoint logs this once the clone is complete.
for _ in $(seq 180); do
    "${C[@]}" logs sandbox 2>/dev/null | grep -q '^\(.*| \)\?\[sandbox\] cloned' && break
    sleep 1
done
sx() { "${C[@]}" exec -T sandbox "$@"; }

# Agent-<uuid>: AGENTS.md lets the agent edit .c/.h files only on branches
# named this way. The UUIDv5 is recomputable from the issue; <gen> moves past
# branches left by earlier runs, since lav-gitlab mr always creates a branch.
LAV_AGENT_NS=0941eb87-f57f-41fa-bb04-10621942e787
uuid5() { python3 -c 'import sys, uuid; print(uuid.uuid5(uuid.UUID(sys.argv[1]), sys.argv[2]))' "$@"; }
gen=0
while :; do
    branch=Agent-$(uuid5 "$LAV_AGENT_NS" "$GITLAB_HOST/$GITLAB_PROJECT_ID/issue/$iid/$gen")
    api GET "/repository/branches/$branch" >/dev/null 2>&1 || break
    gen=$((gen + 1))
done
sx git checkout -q -b "$branch"
base=$(sx git rev-parse HEAD)
# compile_commands.json is generated, so a fresh clone lacks it, and the
# graph scripts and clang tooling need it. The dry run takes about a second;
# without it the agent spends its run building one. Both outputs are
# gitignored.
sx make -e PLATFORM=sdl compile_commands_dry \
    || echo "warning: compile_commands_dry failed; the agent will lack compile_commands.json"

prompt="You are working on GitLab issue #$iid in the repository at /work/repo
(branch $branch is checked out).

Title: $title

$(jq -r '.description // ""' <<<"$issue")

Resolve the issue by editing the repository. Commit your work with git as you
go; the last commit message should summarise the whole change. Do not push and
do not open merge requests; that happens after you finish."

# --- run the agent ----------------------------------------------------------
# events.jsonl keeps every event; the job log gets one line per tool call or
# reply, live. -R + fromjson? so a malformed line can't kill jq (and with it
# the pipe into tee and opencode).
progress() {
    jq -R -r --unbuffered 'fromjson? | (
        if .type == "tool_use" then
            "[\(.part.tool)] \(.part.state.title // (.part.state.input | tostring))"
            + (if .part.state.status == "error" then "  (error)" else "" end)
        elif .type == "text" then "> \(.part.text)"
        elif .type == "error" then "! \(tostring)"
        else empty end
    ) | gsub("\\s+"; " ") | .[0:240]'
}
# Cancelling: the runner's SIGTERM reaches only the job shell (via su), which
# waits on this script and never passes it on, so a cancelled job sat in
# "canceling" until opencode finished. Instead, opencode runs in the
# background while we poll our own job's status; on cancel, exiting runs the
# EXIT trap, and tearing the stack down ends opencode. The TERM trap stays
# for a signal that does arrive (`wait` returns for it at once).
# A cancelled job uploads no artifacts, so point at the job log instead.
cancelled() {
    reported=1
    note "Agent run for #$iid was cancelled.${CI_JOB_URL:+ Log: $CI_JOB_URL}" || true
    relabel agent-doing agent-failed || true
    exit 143
}
trap cancelled TERM INT
rm -f "$OUT/opencode.rc"  # the build dir persists between jobs
set +e
{ sx timeout "$AGENT_TIMEOUT" opencode run --auto --format json "$prompt" \
      2>"$OUT/opencode.stderr"; echo $? >"$OUT/opencode.rc"; } \
    | tee "$OUT/events.jsonl" | progress &
agent=$!
job_cancelled() {
    [ -n "${CI_JOB_ID:-}" ] && api GET "/jobs/$CI_JOB_ID" 2>/dev/null \
        | jq -e '.status == "canceling" or .status == "canceled"' >/dev/null
}
while kill -0 "$agent" 2>/dev/null; do
    sleep 15 & wait $!
    job_cancelled && cancelled
done
wait "$agent"
rc=$(cat "$OUT/opencode.rc" 2>/dev/null || echo 1)
set -e
echo "opencode exited with $rc"

# first() stops jq itself: piping into `head -n 1` killed jq with SIGPIPE,
# and pipefail + set -e then ended the script (exit 141) before it reported.
session=$(jq -Rrn 'first(inputs | fromjson? | .sessionID // empty)' \
          "$OUT/events.jsonl" 2>/dev/null || true)
if [ -n "$session" ]; then
    sx opencode export "$session" >"$OUT/transcript.json" 2>/dev/null || true
fi

# Anything the agent left uncommitted still goes into the MR.
if [ -n "$(sx git status --porcelain)" ]; then
    sx git add -A
    sx git commit -q -m "Uncommitted changes left by the agent run"
fi

# --- report -----------------------------------------------------------------
if [ "$(sx git rev-list --count "$base..HEAD")" -eq 0 ]; then
    note "Agent run for #$iid ended (exit $rc) without changes.${ARTIFACTS_URL:+ Transcript: $ARTIFACTS_URL}"
    relabel agent-doing agent-failed
    reported=1
    exit 1
fi

message=$(sx git log --reverse --format='%B' "$base..HEAD")
last=$(sx git log -1 --format='%B')
# Agent MRs are never merged: the human reviews them, writes the change
# himself, then closes the MR. Draft blocks an accidental merge, and the
# description must not say "Closes", so the issue stays open until then.
description="For #$iid. Draft for review: never merge, rewrite by hand.

Opened by the lav-agent pipeline (opencode exit $rc).${ARTIFACTS_URL:+
Transcript: $ARTIFACTS_URL}"
mr_out=$(sx lav-gitlab mr --branch "$branch" --title "Draft: Resolve #$iid: $title" \
         --description "$description" --message "$message")
echo "$mr_out"
mr_url=$(grep -o 'https://[^ ]*merge_requests/[0-9]*' <<<"$mr_out" | tail -n 1)

note "$last

---
MR: $mr_url${ARTIFACTS_URL:+
Transcript: $ARTIFACTS_URL}"
relabel agent-doing agent-review
reported=1
