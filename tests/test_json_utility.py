"""Tests for utils/json_utility.py."""

import json
import os
from pathlib import Path

import pytest

from utils.json_utility import JsonUtility


class TestReadFromFile:
    def test_reads_valid_json(self, tmp_path):
        f = tmp_path / "data.json"
        f.write_text('{"key": "value"}', encoding="utf-8")
        result = JsonUtility.read_from_file(str(f))
        assert result == {"key": "value"}

    def test_raises_on_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            JsonUtility.read_from_file(str(f))

    def test_raises_on_missing_file(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            JsonUtility.read_from_file(str(tmp_path / "ghost.json"))


class TestWriteToFile:
    def test_writes_json(self, tmp_path):
        f = tmp_path / "out.json"
        JsonUtility.write_to_file(str(f), {"a": 1})
        data = json.loads(f.read_text(encoding="utf-8"))
        assert data == {"a": 1}

    def test_writes_sorted_keys(self, tmp_path):
        f = tmp_path / "sorted.json"
        JsonUtility.write_to_file(str(f), {"z": 1, "a": 2})
        raw = f.read_text(encoding="utf-8")
        assert raw.index('"a"') < raw.index('"z"')


class TestConvertListsToTuples:
    def test_top_level_list(self):
        data = {"colors": [1, 2, 3]}
        result = JsonUtility.convert_lists_to_tuples(data)
        assert result["colors"] == (1, 2, 3)

    def test_nested_list(self):
        data = {"parent": {"child": [4, 5, 6]}}
        result = JsonUtility.convert_lists_to_tuples(data)
        assert result["parent"]["child"] == (4, 5, 6)

    def test_deeply_nested_list(self):
        data = {"level1": {"level2": {"level3": [7, 8]}}}
        result = JsonUtility.convert_lists_to_tuples(data)
        assert result["level1"]["level2"]["level3"] == (7, 8)

    def test_non_list_values_unchanged(self):
        data = {"name": "test", "count": 42}
        result = JsonUtility.convert_lists_to_tuples(data)
        assert result["name"] == "test"
        assert result["count"] == 42
