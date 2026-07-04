"""Tests for utils/file_utility.py."""

from pathlib import Path

import pytest

from utils.file_utility import FileUtility


class TestCreateDirectory:
    def test_creates_directory(self, tmp_path):
        target = tmp_path / "new_dir" / "nested"
        FileUtility.create_directory(str(target))
        assert target.is_dir()

    def test_existing_directory_no_error(self, tmp_path):
        FileUtility.create_directory(str(tmp_path))
        assert tmp_path.is_dir()


class TestFormatPath:
    def test_strips_trailing_whitespace(self):
        result = FileUtility.format_path("  /some/path  ")
        assert result == str(Path("/some/path"))

    def test_returns_str(self):
        assert isinstance(FileUtility.format_path("/tmp"), str)


class TestIsAccessible:
    def test_accessible_path(self, tmp_path):
        assert FileUtility.is_accessible(str(tmp_path)) is True

    def test_inaccessible_path(self):
        assert FileUtility.is_accessible("/no/such/dir/xyz") is False


class TestIsReadable:
    def test_readable_text_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        assert FileUtility.is_readable(str(f)) is True

    def test_nonexistent_file(self, tmp_path):
        assert FileUtility.is_readable(str(tmp_path / "ghost.txt")) is False


class TestSanitizeFilename:
    @pytest.mark.parametrize(
        "input_url, expected_char",
        [
            ("video:title", "~"),
            ('video"title', "~"),
            ("video<title", "~"),
            ("video>title", "~"),
            ("video|title", "~"),
            ("video*title", "~"),
            ("video?title", "~"),
        ],
    )
    def test_replaces_invalid_chars(self, input_url, expected_char):
        result = FileUtility.sanitize_filename(input_url)
        assert expected_char in result

    def test_safe_name_unchanged(self):
        assert FileUtility.sanitize_filename("hello world") == "hello world"


class TestGetAvailableFileName:
    def test_nonexistent_file_returned_as_is(self, tmp_path):
        target = str(tmp_path / "video.mp4")
        assert FileUtility.get_available_file_name(target) == target

    def test_existing_file_gets_counter(self, tmp_path):
        target = tmp_path / "video.mp4"
        target.write_text("")
        result = FileUtility.get_available_file_name(str(target))
        assert result != str(target)
        assert "(0)" in result


class TestDeleteFiles:
    def test_deletes_all_files(self, tmp_path):
        (tmp_path / "a.txt").write_text("")
        (tmp_path / "b.txt").write_text("")
        FileUtility.delete_files(str(tmp_path))
        assert list(tmp_path.iterdir()) == []

    def test_keeps_specified_files(self, tmp_path):
        keep = tmp_path / "keep.txt"
        remove = tmp_path / "remove.txt"
        keep.write_text("")
        remove.write_text("")
        FileUtility.delete_files(str(tmp_path), files_to_keep=["keep.txt"])
        assert keep.exists()
        assert not remove.exists()
