"""Tests for utils/value_convert_utility.py."""

from utils.value_convert_utility import ValueConvertUtility


class TestConvertTime:
    def test_seconds_only(self):
        assert ValueConvertUtility.convert_time(45) == "0:45"

    def test_minutes_and_seconds(self):
        assert ValueConvertUtility.convert_time(90) == "1:30"

    def test_hours_minutes_seconds(self):
        assert ValueConvertUtility.convert_time(3661) == "1:01:01"

    def test_zero(self):
        assert ValueConvertUtility.convert_time(0) == "0:00"

    def test_exactly_one_hour(self):
        assert ValueConvertUtility.convert_time(3600) == "1:00:00"

    def test_pads_seconds(self):
        assert ValueConvertUtility.convert_time(65) == "1:05"


class TestConvertSize:
    def test_bytes(self):
        assert ValueConvertUtility.convert_size(500, 0) == "500 B"

    def test_kilobytes(self):
        assert ValueConvertUtility.convert_size(1024, 0) == "1 KB"

    def test_megabytes(self):
        result = ValueConvertUtility.convert_size(1024 * 1024, 2)
        assert "MB" in result

    def test_gigabytes(self):
        result = ValueConvertUtility.convert_size(1024**3, 2)
        assert "GB" in result

    def test_decimal_points(self):
        result = ValueConvertUtility.convert_size(1500, 2)
        assert "." in result


class TestMBKBToBytes:
    def test_mb_conversion(self):
        assert ValueConvertUtility.MB_KB_to_Bytes("2MB") == 2 * 1024 * 1024

    def test_kb_conversion(self):
        assert ValueConvertUtility.MB_KB_to_Bytes("512KB") == 512 * 1024

    def test_unknown_unit_returns_zero(self):
        assert ValueConvertUtility.MB_KB_to_Bytes("10GB") == 0
