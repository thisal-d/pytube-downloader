"""Tests for utils/date_time_utility.py."""

import re

from utils.date_time_utility import DateTimeUtility


class TestGetCurrentDateTime:
    def test_returns_string(self):
        result = DateTimeUtility.get_current_date_time()
        assert isinstance(result, str)

    def test_format_matches_pattern(self):
        result = DateTimeUtility.get_current_date_time()
        pattern = r"^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$"
        assert re.match(pattern, result), f"Unexpected format: {result!r}"

    def test_year_is_current_year(self):
        import datetime

        result = DateTimeUtility.get_current_date_time()
        current_year = str(datetime.datetime.now().year)
        assert result.startswith(current_year)
