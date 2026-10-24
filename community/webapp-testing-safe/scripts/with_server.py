#!/usr/bin/env python3
"""Run one or more local servers without invoking a command shell.

Modified derivative of composio-community/awesome-codex-skills webapp-testing,
2026-10-24. Server commands are JSON arrays and execute with shell=False.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
from typing import Sequence


def parse_argv(raw: str) -> list[str]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise argparse.ArgumentTypeError(f"invalid JSON command: {exc}") from exc
    if not isinstance(value, list) or not value:
        raise argparse.ArgumentTypeError("command must be a non-empty JSON array")
    if not all(isinstance(part, str) and part for part in value):
        raise argparse.ArgumentTypeError("every command element must be a non-empty string")
    return value


def wait_for_port(host: str, port: int, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.25)
    return False


def start_process(argv: Sequence[str]) -> subprocess.Popen[bytes]:
    kwargs: dict[str, object] = {
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "shell": False,
    }
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(list(argv), **kwargs)


def stop_process_tree(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
            shell=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=5)
        except (ProcessLookupError, subprocess.TimeoutExpired):
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Start local servers safely, wait for their ports, run a command, then stop them."
    )
    parser.add_argument(
        "--server-json",
        action="append",
        type=parse_argv,
        required=True,
        help='Server argv as JSON, for example ["npm","run","dev"]',
    )
    parser.add_argument(
        "--port",
        action="append",
        type=int,
        required=True,
        help="Local port for the corresponding server",
    )
    parser.add_argument("--host", default="127.0.0.1", help="Readiness host")
    parser.add_argument("--timeout", type=float, default=30.0, help="Seconds per server")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after readiness")
    args = parser.parse_args()

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    if len(args.server_json) != len(args.port):
        parser.error("the number of --server-json and --port arguments must match")
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if any(port < 1 or port > 65535 for port in args.port):
        parser.error("ports must be between 1 and 65535")

    processes: list[subprocess.Popen[bytes]] = []
    try:
        for argv, port in zip(args.server_json, args.port):
            process = start_process(argv)
            processes.append(process)
            if not wait_for_port(args.host, port, args.timeout):
                raise RuntimeError(f"server did not become ready on {args.host}:{port}")
        return subprocess.run(command, shell=False, check=False).returncode
    finally:
        for process in reversed(processes):
            stop_process_tree(process)


if __name__ == "__main__":
    sys.exit(main())
