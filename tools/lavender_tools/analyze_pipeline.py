"""analyze_pipeline.py — Pipeline execution analysis and schema validation.

Provides three analysis functions consumed by lav_ai_app.py:
  * analyze_run(project_root, run_id)
  * analyze_node(project_root, run_id, node_id)
  * validate_schema(project_root)
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_iso(ts: str) -> datetime:
    """Parse ISO-8601 timestamp, forgiving missing tz."""
    ts = ts.strip()
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    # Handle compact format like 20260503T181208Z
    if "T" in ts and "-" not in ts[:8]:
        ts = f"{ts[:4]}-{ts[4:6]}-{ts[6:]}"
    try:
        return datetime.fromisoformat(ts)
    except ValueError:
        # Fallback: try to parse with common formats
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z",
                    "%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
            try:
                return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        raise


def _find_latest_run(dotlavender: Path) -> dict | None:
    """Walk pipeline_state/*/latest_run.json and return the most recent one."""
    candidates: list[tuple[datetime, dict]] = []
    state_dir = dotlavender / "pipeline_state"
    if not state_dir.is_dir():
        return None
    for sub in state_dir.iterdir():
        lr = sub / "latest_run.json"
        if lr.is_file():
            try:
                data = json.loads(lr.read_text())
                ts = data.get("timestamp", "")
                candidates.append((_parse_iso(ts), data))
            except Exception:
                continue
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def _load_agent_logs(dotlavender: Path, run_prefix: str) -> list[dict]:
    """Load all agent log JSONs whose filename starts with run_prefix (first 8 chars)."""
    logs_dir = dotlavender / "agent_logs"
    if not logs_dir.is_dir():
        return []
    records = []
    for f in logs_dir.iterdir():
        if not f.is_file() or not f.suffix == ".json":
            continue
        if not f.name.startswith(run_prefix):
            continue
        try:
            records.append(json.loads(f.read_text()))
        except json.JSONDecodeError as exc:
            logger.warning("Skipping corrupted agent log %s: %s", f, exc)
            continue
        except Exception:
            continue
    return records


def _load_tool_history(dotlavender: Path, run_id: str) -> list[dict]:
    """Load all tool-history manifests and filter records by matching run_id."""
    th_dir = dotlavender / "tool-history"
    if not th_dir.is_dir():
        return []
    records: list[dict] = []
    for f in th_dir.iterdir():
        if not f.is_file() or not f.suffix == ".json":
            continue
        try:
            manifest = json.loads(f.read_text())
        except Exception:
            continue
        for block in manifest:
            for rec in block.get("block", []):
                ctx = rec.get("pipeline_context", {})
                rec_run_id = ctx.get("run_id", "")
                # Match exact or sub-run prefix
                if rec_run_id == run_id or rec_run_id.startswith(run_id + "/"):
                    records.append(rec)
    return records


def _find_nearest_log(dotlavender: Path, target_dt: datetime) -> Path | None:
    """Find the pipeline__*.log file with timestamp nearest to target_dt."""
    logs_dir = dotlavender / "logs"
    if not logs_dir.is_dir():
        return None
    best: tuple[float, Path | None] = (float("inf"), None)
    for f in logs_dir.iterdir():
        if not f.is_file() or not f.name.startswith("pipeline__") or not f.suffix == ".log":
            continue
        m = re.search(r"__(\d{8}T\d{6}Z)", f.name)
        if not m:
            continue
        try:
            fts = _parse_iso(m.group(1))
        except Exception:
            continue
        diff = abs((fts - target_dt).total_seconds())
        if diff < best[0]:
            best = (diff, f)
    return best[1]


def _log_timestamps(log_path: Path) -> tuple[datetime | None, datetime | None]:
    """Return (first_timestamp, last_timestamp) from a pipeline log file."""
    first = last = None
    if not log_path.is_file():
        return None, None
    for line in log_path.read_text().splitlines():
        m = re.match(r"(\d{2}:\d{2}:\d{2})", line)
        if m:
            t = m.group(1)
            # We don't have the date in the line, but we can get it from the filename
            # For ordering purposes within the same day, the time string is enough.
            # We'll return the raw time string as a proxy and let the caller handle it.
            if first is None:
                first = t
            last = t
    return first, last


def _guess_literal_type(value_str: str) -> str:
    """Guess the JSON type of a literal from a condition expression."""
    v = value_str.strip()
    if v.lower() == "true" or v.lower() == "false":
        return "boolean"
    if v == "null":
        return "null"
    if v.startswith('"') and v.endswith('"'):
        return "string"
    if v.startswith("'") and v.endswith("'"):
        return "string"
    if v.startswith("[") and v.endswith("]"):
        return "array"
    if v.startswith("{") and v.endswith("}"):
        return "object"
    try:
        int(v)
        return "integer"
    except ValueError:
        pass
    try:
        float(v)
        return "number"
    except ValueError:
        pass
    return "unknown"


def _extract_state_keys(condition: str) -> list[tuple[str, str | None, str, str]]:
    """Parse a condition string and extract (state_key, property, operator, literal)."""
    results = []
    # Pattern: $state.key[.property]  op  literal
    pattern = re.compile(
        r"\$state\.(\w+)(?:\.(\w+))?\s*([=<>!]+)\s*(.+?)(?=\s*(?:&&|\|\||$))"
    )
    for m in pattern.finditer(condition):
        key = m.group(1)
        prop = m.group(2)
        op = m.group(3).strip()
        literal = m.group(4).strip()
        results.append((key, prop, op, literal))
    return results


# ---------------------------------------------------------------------------
# analyze_run
# ---------------------------------------------------------------------------

def analyze_run(project_root: str, run_id: str = "") -> dict:
    """Analyze a pipeline execution run and return a structured report."""
    root = Path(project_root)
    dotlavender = root / ".lavender"
    if not dotlavender.is_dir():
        return {
            "tool": "analyze_pipeline_run",
            "error": f"No .lavender directory in {root}",
            "run_id": "",
            "pipeline_id": "unknown",
            "status": "unknown",
            "duration": {
                "start_iso": "",
                "end_iso": "",
                "total_seconds": 0.0,
            },
            "cost": {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "api_calls": 0,
            },
            "nodes": {},
            "anomalies": [],
        }

    # Resolve run_id
    latest_run = None
    if not run_id:
        latest = _find_latest_run(dotlavender)
        if latest:
            run_id = latest.get("run_id", "")
            latest_run = latest
        else:
            # No latest_run.json, try agent_logs
            agent_logs = _load_agent_logs(dotlavender, "")
            if not agent_logs:
                return {
                    "error": "No pipeline run data found",
                    "run_id": "",
                    "nodes": {},
                    "anomalies": [],
                    "cost": {},
                    "duration": {},
                }
            run_id = ""

    run_prefix = run_id[:8]

    # Load latest_run for this run_id if available
    state_dir = dotlavender / "pipeline_state"
    if state_dir.is_dir():
        for sub in state_dir.iterdir():
            lr = sub / "latest_run.json"
            if lr.is_file():
                try:
                    data = json.loads(lr.read_text())
                    if data.get("run_id") == run_id:
                        latest_run = data
                        break
                except Exception:
                    continue

    status = latest_run.get("status", "unknown") if latest_run else "unknown"
    pipeline_id = latest_run.get("pipeline_id", "unknown") if latest_run else "unknown"

    # Load agent logs
    agent_logs = _load_agent_logs(dotlavender, run_prefix)
    # Filter to those belonging to this run or its sub-runs
    filtered_agent_logs = [
        log for log in agent_logs
        if log.get("run_id", "").startswith(run_id)
    ]

    # Load tool history
    tool_history = _load_tool_history(dotlavender, run_id)

    # Find nearest log file
    run_ts = latest_run.get("timestamp", "") if latest_run else ""
    if run_ts:
        try:
            target_dt = _parse_iso(run_ts)
        except Exception:
            target_dt = datetime.now(timezone.utc)
    else:
        target_dt = datetime.now(timezone.utc)

    nearest_log = _find_nearest_log(dotlavender, target_dt)
    log_first = log_last = None
    if nearest_log:
        log_first, log_last = _log_timestamps(nearest_log)

    # Duration bounds
    timestamps: list[datetime] = []
    for log in filtered_agent_logs:
        ts = log.get("timestamp", "")
        if ts:
            try:
                timestamps.append(_parse_iso(ts))
            except Exception:
                continue

    # Also try to get date from log filename for first/last times
    if nearest_log:
        m = re.search(r"__(\d{8}T\d{6}Z)", nearest_log.name)
        if m:
            log_date_str = m.group(1)[:8]  # YYYYMMDD
            if log_first:
                try:
                    h, mi, s = log_first.split(":")
                    timestamps.append(datetime(int(log_date_str[:4]), int(log_date_str[4:6]),
                                               int(log_date_str[6:8]), int(h), int(mi), int(s),
                                               tzinfo=timezone.utc))
                except Exception:
                    pass
            if log_last:
                try:
                    h, mi, s = log_last.split(":")
                    timestamps.append(datetime(int(log_date_str[:4]), int(log_date_str[4:6]),
                                               int(log_date_str[6:8]), int(h), int(mi), int(s),
                                               tzinfo=timezone.utc))
                except Exception:
                    pass

    start_iso = end_iso = ""
    total_seconds = 0.0
    if timestamps:
        timestamps.sort()
        start_iso = timestamps[0].isoformat()
        end_iso = timestamps[-1].isoformat()
        total_seconds = (timestamps[-1] - timestamps[0]).total_seconds()

    # Cost aggregation
    total_tokens = prompt_tokens = completion_tokens = api_calls = 0
    for log in filtered_agent_logs:
        usage = log.get("usage", {})
        pt = usage.get("prompt_tokens", 0) or 0
        ct = usage.get("completion_tokens", 0) or 0
        tt = usage.get("total_tokens", 0) or 0
        prompt_tokens += pt
        completion_tokens += ct
        total_tokens += tt if tt else (pt + ct)
        api_calls += 1

    # Node aggregation
    nodes: dict[str, dict] = {}
    node_files: dict[str, set[str]] = defaultdict(set)

    # Group tool-history by node_id
    for rec in tool_history:
        node_id = rec.get("pipeline_context", {}).get("node_id", "unknown")
        fpath = rec.get("record", {}).get("file", "")
        if fpath:
            node_files[node_id].add(fpath)

    for log in filtered_agent_logs:
        node_id = log.get("node_id", "unknown")
        if node_id not in nodes:
            nodes[node_id] = {
                "type": "agent" if log.get("agent") else "mcp_tool",
                "invocations": 0,
                "first_seen": "",
                "last_seen": "",
                "cycle_counts": defaultdict(int),
                "tokens": {"prompt": 0, "completion": 0, "total": 0},
                "acceptance_rate": 0.0,
                "tools_used": defaultdict(int),
                "files_impacted": [],
            }
        n = nodes[node_id]
        n["invocations"] += 1
        ts = log.get("timestamp", "")
        if ts:
            if not n["first_seen"] or ts < n["first_seen"]:
                n["first_seen"] = ts
            if not n["last_seen"] or ts > n["last_seen"]:
                n["last_seen"] = ts
        cycle = log.get("cycle", 0)
        n["cycle_counts"][str(cycle)] += 1
        usage = log.get("usage", {})
        pt = usage.get("prompt_tokens", 0) or 0
        ct = usage.get("completion_tokens", 0) or 0
        tt = usage.get("total_tokens", 0) or 0
        n["tokens"]["prompt"] += pt
        n["tokens"]["completion"] += ct
        n["tokens"]["total"] += tt if tt else (pt + ct)
        passed = log.get("acceptance_passed", True)
        # Running acceptance rate (proportion passed)
        current_passed = n["acceptance_rate"] * (n["invocations"] - 1)
        n["acceptance_rate"] = (current_passed + (1.0 if passed else 0.0)) / n["invocations"]

    # Determine node types better: if it doesn't have agent logs, but has tool-history, mark as mcp_tool
    for node_id in node_files:
        if node_id not in nodes:
            nodes[node_id] = {
                "type": "mcp_tool",
                "invocations": 0,
                "first_seen": "",
                "last_seen": "",
                "tools_used": defaultdict(int),
                "files_impacted": [],
            }
        nodes[node_id]["files_impacted"] = sorted(node_files[node_id])

    # Infer tools_used for MCP tool nodes from callee-chain in tool-history
    for rec in tool_history:
        node_id = rec.get("pipeline_context", {}).get("node_id", "unknown")
        chain = rec.get("callee-chain", [])
        if chain:
            tool_name = Path(chain[0]).stem
            if node_id in nodes:
                nodes[node_id]["tools_used"][tool_name] += 1

    # Convert defaultdicts to dicts
    for n in nodes.values():
        if "cycle_counts" in n:
            n["cycle_counts"] = dict(n["cycle_counts"])
        if "tools_used" in n:
            n["tools_used"] = dict(n["tools_used"])

    # Anomaly detection
    anomalies: list[dict] = []
    max_cycles_default = 3

    for node_id, n in nodes.items():
        invocations = n.get("invocations", 0)
        # stuck_cycle_counter
        cycle_counts = n.get("cycle_counts", {})
        for cycle_val, count in cycle_counts.items():
            if count > max_cycles_default:
                anomalies.append({
                    "type": "stuck_cycle_counter",
                    "severity": "critical",
                    "node_id": node_id,
                    "detail": f"Cycle {cycle_val} occurred {count} times (>{max_cycles_default})",
                })

        # excessive_iterations
        if invocations > 2 * max_cycles_default:
            anomalies.append({
                "type": "excessive_iterations",
                "severity": "critical",
                "node_id": node_id,
                "detail": f"Node invoked {invocations} times (>{2 * max_cycles_default})",
            })

        # cost_spike
        node_total = n.get("tokens", {}).get("total", 0)
        if total_tokens > 0 and node_total > 0.8 * total_tokens:
            anomalies.append({
                "type": "cost_spike",
                "severity": "warning",
                "node_id": node_id,
                "detail": f"Node consumed {node_total}/{total_tokens} tokens ({node_total/total_tokens:.1%})",
            })

    # empty_context: check agent logs where user_message_length is 0 or preview is empty-ish
    for log in filtered_agent_logs:
        preview = log.get("user_message_preview", "")
        length = log.get("user_message_length", len(preview))
        node_id = log.get("node_id", "unknown")
        if length == 0 or (isinstance(preview, str) and preview.strip() in ("", "{}", "[]", "null")):
            anomalies.append({
                "type": "empty_context",
                "severity": "high",
                "node_id": node_id,
                "detail": f"Empty user_message at {log.get('timestamp','')}",
            })

    return {
        "tool": "analyze_pipeline_run",
        "run_id": run_id,
        "pipeline_id": pipeline_id,
        "status": status,
        "duration": {
            "start_iso": start_iso,
            "end_iso": end_iso,
            "total_seconds": total_seconds,
        },
        "cost": {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "api_calls": api_calls,
        },
        "nodes": nodes,
        "anomalies": anomalies,
    }


# ---------------------------------------------------------------------------
# analyze_node
# ---------------------------------------------------------------------------

def analyze_node(project_root: str, run_id: str, node_id: str) -> dict:
    """Deep-dive analysis of a specific pipeline node."""
    root = Path(project_root)
    dotlavender = root / ".lavender"
    if not dotlavender.is_dir():
        return {
            "tool": "analyze_pipeline_node",
            "error": f"No .lavender directory in {root}",
            "run_id": run_id,
            "node_id": node_id,
            "invocations": [],
            "summary": {
                "total_invocations": 0,
                "total_tokens": 0,
                "cycle_histogram": {},
                "unique_files_impacted": [],
            },
        }

    run_prefix = run_id[:8]
    agent_logs = _load_agent_logs(dotlavender, run_prefix)
    filtered_agent_logs = [
        log for log in agent_logs
        if log.get("run_id", "").startswith(run_id) and log.get("node_id") == node_id
    ]
    filtered_agent_logs.sort(key=lambda x: x.get("timestamp", ""))

    tool_history = _load_tool_history(dotlavender, run_id)
    node_tool_history = [rec for rec in tool_history
                         if rec.get("pipeline_context", {}).get("node_id") == node_id]

    # Map timestamps to impacted files (within a 5-second window)
    files_by_time: dict[str, list[str]] = defaultdict(list)
    for rec in node_tool_history:
        ts = rec.get("timestamp", "")
        fpath = rec.get("record", {}).get("file", "")
        if ts and fpath:
            files_by_time[ts].append(fpath)

    invocations: list[dict] = []
    total_tokens = 0
    cycle_histogram: dict[str, int] = defaultdict(int)

    for log in filtered_agent_logs:
        ts = log.get("timestamp", "")
        usage = log.get("usage", {})
        pt = usage.get("prompt_tokens", 0) or 0
        ct = usage.get("completion_tokens", 0) or 0
        tt = usage.get("total_tokens", 0) or 0
        total_tokens += tt if tt else (pt + ct)
        cycle = log.get("cycle", 0)
        cycle_histogram[str(cycle)] += 1

        response_preview = log.get("raw_response_preview", "")[:200]
        # Gather files impacted near this timestamp
        impacted: set[str] = set()
        if ts:
            try:
                dt_ts = _parse_iso(ts)
                for rec_ts, files in files_by_time.items():
                    try:
                        dt_rec = _parse_iso(rec_ts)
                        if abs((dt_ts - dt_rec).total_seconds()) <= 5:
                            impacted.update(files)
                    except Exception:
                        continue
            except Exception:
                pass

        invocations.append({
            "timestamp": ts,
            "cycle": cycle,
            "tokens": {
                "prompt": pt,
                "completion": ct,
                "total": tt if tt else (pt + ct),
            },
            "acceptance_passed": log.get("acceptance_passed", True),
            "acceptance_errors": log.get("acceptance_errors", []),
            "response_preview": response_preview,
            "files_impacted": sorted(impacted),
        })

    unique_files: set[str] = set()
    for rec in node_tool_history:
        fpath = rec.get("record", {}).get("file", "")
        if fpath:
            unique_files.add(fpath)

    return {
        "tool": "analyze_pipeline_node",
        "run_id": run_id,
        "node_id": node_id,
        "invocations": invocations,
        "summary": {
            "total_invocations": len(invocations),
            "total_tokens": total_tokens,
            "cycle_histogram": dict(cycle_histogram),
            "unique_files_impacted": sorted(unique_files),
        },
    }


# ---------------------------------------------------------------------------
# validate_schema
# ---------------------------------------------------------------------------

def validate_schema(project_root: str) -> dict:
    """Static pre-flight validation of pipeline JSON schemas."""
    root = Path(project_root)
    pipelines_dir = root / ".lavender" / "pipelines"
    if not pipelines_dir.is_dir():
        # Fallback: treat root itself as the pipelines directory
        has_pipeline_files = False
        if root.is_dir():
            try:
                has_pipeline_files = any(
                    f.name.startswith("pipeline__") and f.suffix == ".json"
                    for f in root.iterdir()
                )
            except Exception:
                pass
        if has_pipeline_files:
            pipelines_dir = root
        else:
            return {
                "tool": "validate_pipeline_schema",
                "error": f"No .lavender/pipelines directory in {root}",
                "pipelines_checked": 0,
                "checks": [],
                "summary": {
                    "passed": 0,
                    "warnings": 0,
                    "errors": 0,
                },
            }

    # Collect all pipeline JSON files
    pipeline_files: list[Path] = []
    for f in pipelines_dir.iterdir():
        if f.is_file() and f.suffix == ".json":
            pipeline_files.append(f)
    sub_dir = pipelines_dir / "sub"
    if sub_dir.is_dir():
        for f in sub_dir.iterdir():
            if f.is_file() and f.suffix == ".json":
                pipeline_files.append(f)

    checks: list[dict] = []
    passed = warnings = errors = 0

    for pf in pipeline_files:
        try:
            data = json.loads(pf.read_text())
        except Exception as exc:
            checks.append({
                "pipeline": pf.name,
                "check": "parse_json",
                "status": "error",
                "detail": str(exc),
            })
            errors += 1
            continue

        pipeline = data.get("pipeline", {})
        pipeline_id = pipeline.get("id", pf.stem)
        state_schema = pipeline.get("state_schema", {})
        nodes = pipeline.get("nodes", [])
        edges = pipeline.get("edges", [])

        # 1. MCP tool node with multiple output keys
        for node in nodes:
            if node.get("type") == "mcp_tool":
                outputs = node.get("outputs", [])
                if len(outputs) > 1:
                    checks.append({
                        "pipeline": pipeline_id,
                        "check": f"mcp_tool_node_outputs:{node.get('id','')}",
                        "status": "warning",
                        "detail": f"MCP tool node '{node.get('id')}' has {len(outputs)} output keys; tool must return a JSON dict.",
                    })
                    warnings += 1
                else:
                    passed += 1

        # 2. Condition expression type checking
        condition_sources: list[tuple[str, str]] = []
        for edge in edges:
            cond = edge.get("condition", "")
            if cond:
                condition_sources.append((f"edge:{edge.get('from','')}->{edge.get('to','')}", cond))
        for node in nodes:
            pre = node.get("preconditions", [])
            for cond in pre:
                if isinstance(cond, str):
                    condition_sources.append((f"node_precondition:{node.get('id','')}", cond))

        for src, cond in condition_sources:
            extracted = _extract_state_keys(cond)
            if not extracted:
                continue
            for key, prop, op, literal in extracted:
                schema_entry = state_schema.get(key, {})
                declared_type = schema_entry.get("type", "unknown")
                literal_type = _guess_literal_type(literal)

                # If property is .length, expected type should support length
                if prop == "length":
                    if declared_type not in ("array", "string", "object", "unknown"):
                        checks.append({
                            "pipeline": pipeline_id,
                            "check": f"condition_type:{src}",
                            "status": "warning",
                            "detail": f"Key '{key}' is type '{declared_type}' but '.length' used; expected array/string/object.",
                        })
                        warnings += 1
                    else:
                        passed += 1
                    continue

                # Simple type compatibility mapping
                compatible = False
                if literal_type == declared_type:
                    compatible = True
                elif declared_type == "integer" and literal_type == "number":
                    compatible = True
                elif declared_type == "number" and literal_type == "integer":
                    compatible = True
                elif declared_type == "array" and literal == "[]":
                    compatible = True
                elif declared_type == "object" and literal == "{}":
                    compatible = True
                elif declared_type == "unknown":
                    compatible = True

                if not compatible:
                    checks.append({
                        "pipeline": pipeline_id,
                        "check": f"condition_type:{src}",
                        "status": "warning",
                        "detail": f"Key '{key}' is type '{declared_type}' but compared to {literal_type} literal '{literal}'.",
                    })
                    warnings += 1
                else:
                    passed += 1

        # 3. Cycle edge checks
        for edge in edges:
            if edge.get("type") == "cycle":
                # Verify it has max_cycles
                if "max_cycles" not in edge:
                    checks.append({
                        "pipeline": pipeline_id,
                        "check": f"cycle_edge:{edge.get('from','')}->{edge.get('to','')}",
                        "status": "warning",
                        "detail": "Cycle edge missing max_cycles attribute.",
                    })
                    warnings += 1
                else:
                    checks.append({
                        "pipeline": pipeline_id,
                        "check": f"cycle_edge:{edge.get('from','')}->{edge.get('to','')}",
                        "status": "passed",
                        "detail": "Cycle edge has max_cycles.",
                    })
                    passed += 1

        # 4. Agent convergence.progress_key validation
        for node in nodes:
            if node.get("type") == "agent":
                convergence = node.get("convergence", {})
                progress_key = convergence.get("progress_key", "")
                if progress_key:
                    m = re.match(r"\$state\.(\w+)", progress_key)
                    if m:
                        key = m.group(1)
                        if key not in state_schema:
                            checks.append({
                                "pipeline": pipeline_id,
                                "check": f"convergence_progress_key:{node.get('id','')}",
                                "status": "error",
                                "detail": f"progress_key '{progress_key}' references undefined state key '{key}'.",
                            })
                            errors += 1
                        else:
                            checks.append({
                                "pipeline": pipeline_id,
                                "check": f"convergence_progress_key:{node.get('id','')}",
                                "status": "passed",
                                "detail": f"progress_key '{progress_key}' references valid state key '{key}'.",
                            })
                            passed += 1
                    else:
                        checks.append({
                            "pipeline": pipeline_id,
                            "check": f"convergence_progress_key:{node.get('id','')}",
                            "status": "warning",
                            "detail": f"progress_key '{progress_key}' does not match $state.<key> pattern.",
                        })
                        warnings += 1

    return {
        "tool": "validate_pipeline_schema",
        "pipelines_checked": len(pipeline_files),
        "checks": checks,
        "summary": {
            "passed": passed,
            "warnings": warnings,
            "errors": errors,
        },
    }
