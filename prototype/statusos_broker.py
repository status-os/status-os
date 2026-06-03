#!/usr/bin/env python3
"""
Status OS Broker - Genesis Prototype

Given device capabilities and task manifests, decide how each task may resume.
No external dependencies required.
"""

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def has_input(device, requirements):
    required = requirements.get("input", {})
    device_input = device.get("input", {})
    for key, needed in required.items():
        if needed and not device_input.get(key, False):
            return False, f"missing input: {key}"
    return True, "input ok"


def display_ok(device, requirements):
    display = device.get("display", {})
    w = display.get("width") or 0
    h = display.get("height") or 0
    min_w = requirements.get("display_min_width", 0)
    min_h = requirements.get("display_min_height", 0)
    if w < min_w or h < min_h:
        return False, f"display too small: {w}x{h}, needs {min_w}x{min_h}"
    return True, "display ok"


def ram_ok(device, requirements):
    ram = device.get("ram_mb") or 0
    needed = requirements.get("ram_mb_min", 0)
    if ram < needed:
        return False, f"ram too low: {ram} MB, needs {needed} MB"
    return True, "ram ok"


def gpu_ok(device, requirements):
    if not requirements.get("gpu_required", False):
        return True, "gpu not required"
    gpu = (device.get("gpu_class") or "").lower()
    if "dedicated" in gpu:
        return True, "dedicated gpu ok"
    return False, f"gpu insufficient: {device.get('gpu_class')}"


def network_ok(device, requirements):
    latency = device.get("network", {}).get("latency_ms")
    max_latency = requirements.get("latency_ms_max")
    if latency is None or max_latency is None:
        return True, "latency unknown"
    if latency > max_latency:
        return False, f"latency too high: {latency} ms, max {max_latency} ms"
    return True, "latency ok"


def decide(device, task):
    requirements = task.get("requirements", {})
    allowed = set(task.get("allowed_resume_modes", []))
    features = device.get("features", {})
    reasons = []

    native_ok = True
    for check in [ram_ok, display_ok, gpu_ok, network_ok, has_input]:
        ok, reason = check(device, requirements)
        reasons.append(reason)
        if not ok:
            native_ok = False

    if "native" in allowed and native_ok:
        return {"mode": "native", "reason": "device satisfies task requirements"}

    if "stream" in allowed and features.get("stream_decode", False):
        net, net_reason = network_ok(device, requirements)
        if net:
            return {"mode": "stream", "reason": "task remains on host; device can decode stream"}
        reasons.append(net_reason)

    if "remote" in allowed and features.get("remote_desktop", False):
        net, net_reason = network_ok(device, requirements)
        if net:
            return {"mode": "remote", "reason": "task remains on host; device can remote-control it"}
        reasons.append(net_reason)

    if "view_only" in allowed:
        return {"mode": "view_only", "reason": "full resume blocked; safe status viewing allowed"}

    if "stasis" in allowed:
        return {"mode": "stasis", "reason": "task preserved on current host"}

    return {"mode": "blocked", "reason": "; ".join(reasons)}


def event_hash(event):
    compact = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(compact.encode("utf-8")).hexdigest()


def ledger_event(device, task, decision, previous_hash="GENESIS"):
    event = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "device_id": device["device_id"],
        "task_id": task["task_id"],
        "decision": decision["mode"],
        "reason": decision["reason"],
        "previous_hash": previous_hash,
    }
    event["event_hash"] = event_hash(event)
    return event


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", required=True)
    parser.add_argument("--tasks", required=True)
    parser.add_argument("--ledger-out", default=None)
    args = parser.parse_args()

    devices = load_json(args.devices)["devices"]
    tasks = load_json(args.tasks)["tasks"]

    previous_hash = "GENESIS"
    report = {"results": []}
    ledger = []

    for device in devices:
        device_result = {"device_id": device["device_id"], "tasks": []}
        for task in tasks:
            decision = decide(device, task)
            device_result["tasks"].append({
                "task_id": task["task_id"],
                "task_name": task["name"],
                "resume_mode": decision["mode"],
                "reason": decision["reason"]
            })
            event = ledger_event(device, task, decision, previous_hash)
            previous_hash = event["event_hash"]
            ledger.append(event)
        report["results"].append(device_result)

    print(json.dumps(report, indent=2))

    if args.ledger_out:
        out = Path(args.ledger_out)
        with out.open("a", encoding="utf-8") as f:
            for event in ledger:
                f.write(json.dumps(event, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
