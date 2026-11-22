"""Smoke test against the live deployment."""

import json
import sys
import time
import urllib.request


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: uv run python scripts/smoke.py <base_url>")
        return 2

    base_url = sys.argv[1].rstrip("/")
    health_url = f"{base_url}/health"

    for attempt in range(1, 13):
        try:
            with urllib.request.urlopen(health_url, timeout=30) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    print(f"OK: {health_url} -> 200 ({data})")
                    return 0
        except Exception as exc:
            print(f"Attempt {attempt}/12 failed: {exc}")
            time.sleep(10)

    print(f"FAIL: {health_url} did not return 200")
    return 1


if __name__ == "__main__":
    sys.exit(main())
