#!/usr/bin/env python3
"""
Status OS Agent - Genesis Prototype

Reports local device capability as JSON.
No external dependencies required.
"""

import argparse
import json
import os
import platform
import socket
import subprocess
from pathlib import Path


def run(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True).strip()
    except Exception:
        return None


def ram_mb():
    meminfo = Path("/proc/meminfo")
    if meminfo.exists():
        for line in meminfo.read_text().splitlines():
            if line.startswith("MemTotal:"):
                kb = int(line.split()[1])
                return kb // 1024

    try:
        if hasattr(os, "sysconf"):
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            return int((pages * page_size) / (1024 * 1024))
    except Exception:
        pass

    return None


def cpu_threads():
    return os.cpu_count() or 1


def display_guess():
    return {"width": None, "height": None}


def gpu_guess():
    lspci = run(["sh", "-lc", "command -v lspci >/dev/null && lspci | grep -Ei 'vga|3d|display' | head -n 3"])
    if not lspci:
        return "unknown"
    lower = lspci.lower()
    if "nvidia" in lower or "amd" in lower or "radeon" in lower:
        return "dedicated_or_integrated"
    if "intel" in lower:
        return "integrated"
    return "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", help="Write JSON output to file")
    parser.add_argument("--device-id", default=socket.gethostname())
    args = parser.parse_args()

    data = {
        "device_id": args.device_id,
        "device_type": "unknown",
        "hostname": socket.gethostname(),
        "os": platform.system().lower(),
        "os_release": platform.release(),
        "kernel": platform.version(),
        "cpu_arch": platform.machine(),
        "cpu_threads": cpu_threads(),
        "ram_mb": ram_mb(),
        "gpu_class": gpu_guess(),
        "display": {"width": None, "height": None},
        "input": {"keyboard": True, "pointer": True, "touch": False, "gamepad": False},
        "network": {"latency_ms": None, "bandwidth_mbps": None},
        "trust": {"owner_verified": False, "disk_encrypted": None},
        "features": {
            "remote_desktop": False,
            "stream_decode": True,
            "stream_host": False,
            "checkpoint_restore": False
        }
    }

    output = json.dumps(data, indent=2)
    if args.out:
        Path(args.out).write_text(output + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
