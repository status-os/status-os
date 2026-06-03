#!/usr/bin/env python3
"""
Status OS Anchor - v0.2 Prototype

Local Status Anchor service/CLI.

Purpose:
- keep a persistent local device registry,
- register devices from JSON manifests,
- list known devices,
- run broker decisions against registered devices,
- write tamper-evident event rows into SQLite.

No external dependencies.
"""

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from statusos_broker import decide  # noqa: E402


SCHEMA = """
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    device_type TEXT,
    os TEXT,
    cpu_arch TEXT,
    cpu_threads INTEGER,
    ram_mb INTEGER,
    gpu_class TEXT,
    manifest_json TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS state_events (
    event_hash TEXT PRIMARY KEY,
    previous_hash TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    device_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL
);
"""


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(SCHEMA)
    return conn


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def extract_devices(payload):
    if "devices" in payload:
        return payload["devices"]
    return [payload]


def register_device(conn, device):
    conn.execute(
        """
        INSERT INTO devices (
            device_id, device_type, os, cpu_arch, cpu_threads, ram_mb,
            gpu_class, manifest_json, updated_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(device_id) DO UPDATE SET
            device_type=excluded.device_type,
            os=excluded.os,
            cpu_arch=excluded.cpu_arch,
            cpu_threads=excluded.cpu_threads,
            ram_mb=excluded.ram_mb,
            gpu_class=excluded.gpu_class,
            manifest_json=excluded.manifest_json,
            updated_at_utc=excluded.updated_at_utc
        """,
        (
            device.get("device_id"),
            device.get("device_type"),
            device.get("os"),
            device.get("cpu_arch"),
            device.get("cpu_threads"),
            device.get("ram_mb"),
            device.get("gpu_class"),
            json.dumps(device, sort_keys=True),
            utcnow(),
        ),
    )


def list_devices(conn):
    rows = conn.execute(
        """
        SELECT device_id, device_type, os, cpu_arch, cpu_threads, ram_mb, gpu_class, updated_at_utc
        FROM devices
        ORDER BY device_id
        """
    ).fetchall()

    return [
        {
            "device_id": row[0],
            "device_type": row[1],
            "os": row[2],
            "cpu_arch": row[3],
            "cpu_threads": row[4],
            "ram_mb": row[5],
            "gpu_class": row[6],
            "updated_at_utc": row[7],
        }
        for row in rows
    ]


def load_registered_device_manifests(conn):
    rows = conn.execute("SELECT manifest_json FROM devices ORDER BY device_id").fetchall()
    return [json.loads(row[0]) for row in rows]


def previous_event_hash(conn):
    row = conn.execute(
        "SELECT event_hash FROM state_events ORDER BY timestamp_utc DESC, rowid DESC LIMIT 1"
    ).fetchone()
    return row[0] if row else "GENESIS"


def event_hash(event):
    compact = json.dumps(event, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(compact.encode("utf-8")).hexdigest()


def write_event(conn, device_id, task_id, decision, reason):
    prev = previous_event_hash(conn)
    event = {
        "previous_hash": prev,
        "timestamp_utc": utcnow(),
        "device_id": device_id,
        "task_id": task_id,
        "decision": decision,
        "reason": reason,
    }
    h = event_hash(event)
    conn.execute(
        """
        INSERT INTO state_events (
            event_hash, previous_hash, timestamp_utc, device_id, task_id, decision, reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (h, prev, event["timestamp_utc"], device_id, task_id, decision, reason),
    )
    return h


def run_decisions(conn, tasks_path):
    tasks = load_json(tasks_path)["tasks"]
    devices = load_registered_device_manifests(conn)

    results = []
    for device in devices:
        device_result = {"device_id": device["device_id"], "tasks": []}
        for task in tasks:
            decision = decide(device, task)
            h = write_event(
                conn,
                device["device_id"],
                task["task_id"],
                decision["mode"],
                decision["reason"],
            )
            device_result["tasks"].append(
                {
                    "task_id": task["task_id"],
                    "task_name": task["name"],
                    "resume_mode": decision["mode"],
                    "reason": decision["reason"],
                    "event_hash": h,
                }
            )
        results.append(device_result)

    return {"results": results}


def show_events(conn, limit):
    rows = conn.execute(
        """
        SELECT timestamp_utc, device_id, task_id, decision, reason, event_hash, previous_hash
        FROM state_events
        ORDER BY timestamp_utc DESC, rowid DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    return [
        {
            "timestamp_utc": row[0],
            "device_id": row[1],
            "task_id": row[2],
            "decision": row[3],
            "reason": row[4],
            "event_hash": row[5],
            "previous_hash": row[6],
        }
        for row in rows
    ]


def main():
    parser = argparse.ArgumentParser(description="Status OS Anchor v0.2")
    parser.add_argument("--db", default="statusos_anchor.db", help="SQLite DB path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize local Status Anchor database")

    reg = sub.add_parser("register-device", help="Register one or more devices from JSON")
    reg.add_argument("--file", required=True, help="Device JSON file. Supports single device or {devices:[...]}")

    sub.add_parser("list-devices", help="List registered devices")

    dec = sub.add_parser("decide", help="Run broker decisions against registered devices")
    dec.add_argument("--tasks", required=True, help="Task manifest JSON file")

    ev = sub.add_parser("events", help="Show latest state events")
    ev.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    conn = connect(args.db)

    if args.command == "init":
        conn.commit()
        print(json.dumps({"status": "ok", "db": args.db, "message": "Status Anchor initialized"}, indent=2))

    elif args.command == "register-device":
        payload = load_json(args.file)
        devices = extract_devices(payload)
        for device in devices:
            if not device.get("device_id"):
                raise SystemExit("Device missing device_id")
            register_device(conn, device)
        conn.commit()
        print(json.dumps({"status": "ok", "registered": [d["device_id"] for d in devices]}, indent=2))

    elif args.command == "list-devices":
        print(json.dumps({"devices": list_devices(conn)}, indent=2))

    elif args.command == "decide":
        result = run_decisions(conn, args.tasks)
        conn.commit()
        print(json.dumps(result, indent=2))

    elif args.command == "events":
        print(json.dumps({"events": show_events(conn, args.limit)}, indent=2))


if __name__ == "__main__":
    main()
