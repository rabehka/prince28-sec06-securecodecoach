"""Tests for security data loading."""

import json
from pathlib import Path

import pytest

from securecodecoach.data_loader import load_security_records


def test_load_security_records(tmp_path):
    data_file = tmp_path / "records.json"
    records = [{"id": 1, "name": "SQL Injection"}]

    data_file.write_text(json.dumps(records), encoding="utf-8")

    result = load_security_records(data_file)

    assert result == records
    assert len(result) == 1


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_security_records(Path("missing.json"))


def test_invalid_structure(tmp_path):
    data_file = tmp_path / "records.json"
    data_file.write_text('{"name": "SQL Injection"}', encoding="utf-8")

    with pytest.raises(ValueError):
        load_security_records(data_file)
