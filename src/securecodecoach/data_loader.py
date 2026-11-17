"""Load sample security records from a JSON file."""

import json
from pathlib import Path
from typing import Any


def load_security_records(file_path: Path) -> list[dict[str, Any]]:
    """Load security records from a JSON file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Data file not found: {file_path}")

    with file_path.open(encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Security records must be a JSON list.")

    return records
