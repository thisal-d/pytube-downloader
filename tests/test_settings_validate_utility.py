"""Tests for utils/settings_validate_utility.py."""

import pytest

from utils.settings_validate_utility import SettingsValidateUtility


class TestValidateSimultaneousCount:
    def test_valid_count_in_range(self):
        assert SettingsValidateUtility.validate_simultaneous_count("5", with_range=True) is True

    def test_zero_out_of_range(self):
        assert SettingsValidateUtility.validate_simultaneous_count("0", with_range=True) is False

    def test_eleven_out_of_range(self):
        assert SettingsValidateUtility.validate_simultaneous_count("11", with_range=True) is False

    def test_valid_without_range(self):
        assert SettingsValidateUtility.validate_simultaneous_count("100", with_range=False) is True

    def test_non_numeric_returns_false(self):
        assert SettingsValidateUtility.validate_simultaneous_count("abc", with_range=True) is False


class TestValidateScaleValue:
    def test_valid_scale(self):
        assert SettingsValidateUtility.validate_scale_value("100%") is True
        assert SettingsValidateUtility.validate_scale_value("150%") is True
        assert SettingsValidateUtility.validate_scale_value("200%") is True

    def test_below_minimum(self):
        assert SettingsValidateUtility.validate_scale_value("99%") is False

    def test_above_maximum(self):
        assert SettingsValidateUtility.validate_scale_value("201%") is False

    def test_missing_percent_sign(self):
        assert SettingsValidateUtility.validate_scale_value("150") is False

    def test_non_numeric(self):
        assert SettingsValidateUtility.validate_scale_value("abc%") is False


class TestValidateOpacityValue:
    def test_valid_opacity(self):
        assert SettingsValidateUtility.validate_opacity_value("80%") is True
        assert SettingsValidateUtility.validate_opacity_value("100%") is True
        assert SettingsValidateUtility.validate_opacity_value("60%") is True

    def test_below_minimum(self):
        assert SettingsValidateUtility.validate_opacity_value("59%") is False

    def test_above_maximum(self):
        assert SettingsValidateUtility.validate_opacity_value("101%") is False

    def test_missing_percent_sign(self):
        assert SettingsValidateUtility.validate_opacity_value("80") is False


class TestValidateChunkSizeValue:
    def test_valid_kb(self):
        assert SettingsValidateUtility.validate_chunk_size_value("512KB") is True

    def test_valid_mb(self):
        assert SettingsValidateUtility.validate_chunk_size_value("5MB") is True

    def test_below_minimum(self):
        assert SettingsValidateUtility.validate_chunk_size_value("10KB") is False

    def test_above_maximum(self):
        assert SettingsValidateUtility.validate_chunk_size_value("12MB") is False

    def test_invalid_unit(self):
        assert SettingsValidateUtility.validate_chunk_size_value("100GB") is False

    def test_non_numeric(self):
        assert SettingsValidateUtility.validate_chunk_size_value("abcKB") is False
