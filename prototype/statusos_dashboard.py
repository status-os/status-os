#!/usr/bin/env python3
"""
Status OS Dashboard - v0.1 Prototype

Local-only dashboard for the first Status OS issue:
"What can this device safely resume right now?"

No external dependencies.

Run from the prototype directory:
python statusos_dashboard.py --devices examples/devices.json --tasks examples/tasks.json
"""

import argparse
import html
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from statusos_broker import decide, ledger_event  # noqa: E402


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_results(devices, tasks):
    previous_hash = "GENESIS"
    rows = []
    for device in devices:
        for task in tasks:
            decision = decide(device, task)
            event = ledger_event(device, task, decision, previous_hash)
            previous_hash = event["event_hash"]
            rows.append({
                "device_id": device["device_id"],
                "device_type": device.get("device_type", "unknown"),
                "task_id": task["task_id"],
                "task_name": task["name"],
                "host_device": task.get("host_device", "unknown"),
                "task_state": task.get("state", "unknown"),
                "resume_mode": decision["mode"],
                "reason": decision["reason"],
                "event_hash": event["event_hash"],
            })
    return rows


def mode_class(mode):
    classes = {
        "native": "ok",
        "remote": "ok",
        "stream": "warn",
        "checkpoint": "warn",
        "view_only": "info",
        "stasis": "hold",
        "blocked": "bad",
    }
    return classes.get(mode, "info")


def render_html(rows):
    table_rows = []
    for row in rows:
        table_rows.append(f"""
        <tr>
          <td>{html.escape(row["device_id"])}</td>
          <td>{html.escape(row["device_type"])}</td>
          <td>{html.escape(row["task_name"])}</td>
          <td>{html.escape(row["task_state"])}</td>
          <td>{html.escape(row["host_device"])}</td>
          <td><span class="pill {mode_class(row["resume_mode"])}">{html.escape(row["resume_mode"])}</span></td>
          <td>{html.escape(row["reason"])}</td>
          <td><code>{html.escape(row["event_hash"][:16])}</code></td>
        </tr>
        """)

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Status OS Dashboard v0.1</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body {{
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      margin: 0;
      background: #0d1117;
      color: #e6edf3;
    }}
    header {{
      padding: 24px;
      border-bottom: 1px solid #30363d;
      background: #010409;
    }}
    main {{ padding: 24px; }}
    h1 {{ margin: 0 0 8px 0; font-size: 28px; }}
    p {{ margin: 0; color: #8b949e; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
      font-size: 14px;
    }}
    th, td {{
      border-bottom: 1px solid #30363d;
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: #c9d1d9;
      background: #161b22;
      position: sticky;
      top: 0;
    }}
    code {{ color: #a5d6ff; }}
    .pill {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 12px;
      text-transform: uppercase;
    }}
    .ok {{ background: #173b22; color: #7ee787; }}
    .warn {{ background: #3d2d0d; color: #d29922; }}
    .info {{ background: #0f2d45; color: #79c0ff; }}
    .hold {{ background: #32245a; color: #d2a8ff; }}
    .bad {{ background: #3d1517; color: #ff7b72; }}
    footer {{
      padding: 24px;
      color: #8b949e;
      border-top: 1px solid #30363d;
    }}
  </style>
</head>
<body>
  <header>
    <h1>Status OS Dashboard v0.1</h1>
    <p>What can this device safely resume right now?</p>
  </header>
  <main>
    <table>
      <thead>
        <tr>
          <th>Device</th>
          <th>Type</th>
          <th>Task</th>
          <th>Task State</th>
          <th>Host</th>
          <th>Resume</th>
          <th>Reason</th>
          <th>Ledger Hash</th>
        </tr>
      </thead>
      <tbody>
        {''.join(table_rows)}
      </tbody>
    </table>
  </main>
  <footer>
    Local-only prototype. No authentication. No remote execution.
  </footer>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    rows = []

    def do_GET(self):
        if self.path not in ["/", "/index.html"]:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        page = render_html(self.rows).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def log_message(self, fmt, *args):
        print("dashboard:", fmt % args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--devices", default="examples/devices.json")
    parser.add_argument("--tasks", default="examples/tasks.json")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    devices = load_json(args.devices)["devices"]
    tasks = load_json(args.tasks)["tasks"]
    DashboardHandler.rows = build_results(devices, tasks)

    server = HTTPServer((args.host, args.port), DashboardHandler)
    print(f"Status OS Dashboard running at http://{args.host}:{args.port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
