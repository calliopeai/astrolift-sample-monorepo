"""Exercise both real service entrypoints without Docker or cloud access."""

import json
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    processes = []
    try:
        for directory, identity in (("api", "mono-api"), ("web", "mono-web")):
            with socket.socket() as reservation:
                reservation.bind(("127.0.0.1", 0))
                port = reservation.getsockname()[1]
            process = subprocess.Popen(
                [sys.executable, str(ROOT / "apps" / directory / "server.py")],
                env={"PORT": str(port)},
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            processes.append(process)
            origin = f"http://127.0.0.1:{port}"
            deadline = time.monotonic() + 5
            while True:
                if process.poll() is not None:
                    raise AssertionError("Fixture service exited before readiness")
                try:
                    with urllib.request.urlopen(
                        origin + "/health", timeout=1
                    ) as response:
                        payload = json.loads(response.read())
                        if response.status != 200 or payload != {
                            "status": "ok",
                            "service": identity,
                        }:
                            raise AssertionError("Unexpected fixture health contract")
                        if response.headers.get("X-Astrolift-Fixture-App") != identity:
                            raise AssertionError("Incorrect fixture identity header")
                    break
                except urllib.error.URLError:
                    if time.monotonic() >= deadline:
                        raise AssertionError("Fixture readiness timed out") from None
                    time.sleep(0.05)
            for path in ("/", "/health"):
                request = urllib.request.Request(origin + path, method="HEAD")
                with urllib.request.urlopen(request, timeout=1) as response:
                    if response.status != 200 or response.read():
                        raise AssertionError("HEAD returned a body or unhealthy status")
                    if response.headers.get("X-Astrolift-Fixture-App") != identity:
                        raise AssertionError("HEAD selected the wrong app")
            try:
                urllib.request.urlopen(origin + "/not-found", timeout=1)
            except urllib.error.HTTPError as error:
                if error.code != 404 or error.read():
                    raise AssertionError(
                        "Unknown fixture route must return an empty 404"
                    ) from None
            else:
                raise AssertionError("Unknown fixture route was accepted")
        if any(process.poll() is not None for process in processes):
            raise AssertionError("Both services must remain independently available")
    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    check()
    print(
        "PASS: both real service entrypoints, health/identity HEAD checks and empty 404s"
    )
