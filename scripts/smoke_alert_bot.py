#!/usr/bin/env python3
"""Local smoke test for alert-bot webhooks.

Usage:
  python scripts/smoke_alert_bot.py --url http://127.0.0.1:8088/webhook/alertmanager --payload examples/alertmanager-firing.json
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="POST a demo payload to alert-bot.")
    parser.add_argument("--url", required=True, help="Webhook URL, for example http://127.0.0.1:8088/webhook/alertmanager")
    parser.add_argument("--payload", required=True, help="Path to JSON payload")
    parser.add_argument("--secret", default="", help="Optional X-Webhook-Secret header value")
    args = parser.parse_args()

    payload = Path(args.payload).read_text(encoding="utf-8")
    request = urllib.request.Request(
        args.url,
        data=payload.encode("utf-8"),
        headers={"Content-Type": "application/json", **({"X-Webhook-Secret": args.secret} if args.secret else {})},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=10) as response:  # noqa: S310 - intentional local smoke test.
        print(response.status)
        print(response.read().decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
