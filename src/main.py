"""Unified CLI entry point."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Ensure project root is in sys.path so 'python src/main.py' and 'python -m src.main' both work
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Fix Windows console encoding for Unicode output
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from src.config import validate_paths
from src.exceptions import ZycusAppError


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Zycus AI Support Suite — Technical Operations Platform"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("eval", help="Run independent evaluation harness")

    triage = sub.add_parser("triage", help="Triage support ticket")
    triage.add_argument("--input", required=False, help="JSON string or file path")
    triage.add_argument("--subject", required=False, help="Ticket subject line")
    triage.add_argument("--body", required=False, help="Ticket body text")
    triage.add_argument("--product", required=False, help="Product name")

    health = sub.add_parser("account-health", help="Generate TAM account health brief")
    health.add_argument("--account-id", required=True, help="Account ID (e.g. ACC-3336)")

    sub.add_parser("ui", help="Launch Streamlit Web UI")
    sub.add_parser("api", help="Launch FastAPI REST server")
    return parser


def _load_json(value: str) -> dict:
    path = Path(value)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return json.loads(value)


def main() -> int:
    validate_paths()
    args = _parser().parse_args()

    if args.command == "eval":
        from src.evaluation import run_evaluation
        report = run_evaluation()
        print(report.model_dump_json(indent=2))
        return 0

    if args.command == "triage":
        from src.triage import triage_ticket
        if args.input:
            payload = _load_json(args.input)
        elif args.subject or args.body:
            payload = {
                "subject": args.subject,
                "body": args.body,
                "product": args.product,
            }
        else:
            print("Error: Provide --input (JSON) or --subject / --body.", file=sys.stderr)
            return 1
        print(triage_ticket(payload).model_dump_json(indent=2))
        return 0

    if args.command == "account-health":
        from src.account_health import summarize_account_health
        print(summarize_account_health(args.account_id).model_dump_json(indent=2))
        return 0

    if args.command == "ui":
        return subprocess.call([sys.executable, "-m", "streamlit", "run", "app.py"])

    if args.command == "api":
        return subprocess.call([
            sys.executable, "-m", "uvicorn",
            "src.api:app", "--host", "127.0.0.1", "--port", "8000"
        ])

    _parser().print_help()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ZycusAppError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
