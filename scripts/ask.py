"""CLI client to ask SecureCodeCoach questions (streaming SSE or --json) and print timing/cost."""

import argparse
import json
import time

import httpx


def main() -> None:
    parser = argparse.ArgumentParser(description="Ask SecureCodeCoach a question.")
    parser.add_argument("question", help="The question to ask")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument(
        "--json", action="store_true", dest="as_json", help="Non-streaming JSON mode"
    )
    args = parser.parse_args()

    endpoint = args.url.rstrip("/") + "/v1/chat"
    payload = {"message": args.question, "stream": not args.as_json}
    t0 = time.monotonic()

    try:
        if args.as_json:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(endpoint, json=payload)
            elapsed = time.monotonic() - t0
            if resp.status_code != 200:
                print(f"HTTP {resp.status_code}: {resp.text}")
                return
            data = resp.json()
            print(data["answer"])
            fb = "YES" if data["fallback_used"] else "no"
            print(
                f"\n--- {data['provider']} / {data['model']}: total {elapsed:.2f} s\n"
                f"    tokens in={data['tokens_in']} out={data['tokens_out']}  "
                f"cost Rs {data['cost_inr']:.6f}  attempts={data['attempts']}  fallback={fb}"
            )
            return

        first_word_at: float | None = None
        done_meta: dict | None = None
        current_event = ""

        with (
            httpx.Client(timeout=60.0) as client,
            client.stream("POST", endpoint, json=payload) as resp,
        ):
            if resp.status_code != 200:
                resp.read()
                print(f"HTTP {resp.status_code}: {resp.text}")
                return
            for line in resp.iter_lines():
                if line.startswith("event:"):
                    current_event = line[6:].strip()
                elif line.startswith("data:"):
                    data = json.loads(line[5:].strip())
                    if current_event == "done":
                        done_meta = data
                    elif current_event == "error":
                        print(f"\n[STREAM ERROR] {data.get('detail')}")
                    elif "delta" in data:
                        if first_word_at is None:
                            first_word_at = time.monotonic() - t0
                        print(data["delta"], end="", flush=True)
                elif line == "":
                    current_event = ""

        total = time.monotonic() - t0
        print()
        if done_meta:
            fb = "YES" if done_meta["fallback_used"] else "no"
            fw = f"{first_word_at:.2f} s" if first_word_at is not None else "n/a"
            print(
                f"\n--- {done_meta['provider']} / {done_meta['model']}: "
                f"first words after {fw}, total {total:.2f} s\n"
                f"    tokens in={done_meta['tokens_in']} out={done_meta['tokens_out']}  "
                f"cost Rs {done_meta['cost_inr']:.6f}  "
                f"attempts={done_meta['attempts']}  fallback={fb}"
            )
    except httpx.ConnectError:
        print(f"ConnectError: is the API running at {args.url}?")


if __name__ == "__main__":
    main()
