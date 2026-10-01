"""Tests for GhostBSD version parsing and upgrade classification."""

import sys
import unittest
from unittest.mock import MagicMock

# backend imports GTK and bectl at module level; neither is needed for the version logic.
for module_name in ('gi', 'gi.repository', 'bectl'):
    sys.modules.setdefault(module_name, MagicMock())

from update_station.backend import parse_version, classify_upgrade  # noqa: E402  pylint: disable=wrong-import-position


class ParseVersionTest(unittest.TestCase):
    """Tests for parse_version()."""

    def test_patch_level(self):
        self.assertEqual(parse_version('26.1-R15.0p13'), (26, 1, 15, 0))

    def test_release_without_suffix(self):
        self.assertEqual(parse_version('26.2-R15.1'), (26, 2, 15, 1))

    def test_prerelease_suffixes(self):
        self.assertEqual(parse_version('26.2-R15.1a1'), (26, 2, 15, 1))
        self.assertEqual(parse_version('26.2-R15.1b1'), (26, 2, 15, 1))
        self.assertEqual(parse_version('26.2-R15.1rc2'), (26, 2, 15, 1))

    def test_legacy_month_release(self):
        self.assertEqual(parse_version('25.02-R14.3p8'), (25, 2, 14, 3))

    def test_surrounding_whitespace(self):
        self.assertEqual(parse_version(' 26.1-R15.0p13\n'), (26, 1, 15, 0))

    def test_invalid(self):
        self.assertEqual(parse_version(''), ())
        self.assertEqual(parse_version('26.1'), ())
        self.assertEqual(parse_version('R15.0p13'), ())
        self.assertEqual(parse_version('26.1-R15.0x1'), ())
        self.assertEqual(parse_version('26.1-R15.0p13 extra'), ())


class ClassifyUpgradeTest(unittest.TestCase):
    """Tests for classify_upgrade()."""

    def test_freebsd_minor_change(self):
        self.assertEqual(classify_upgrade('26.1-R15.0p13', '26.2-R15.1p2'), 'minor')

    def test_freebsd_minor_change_from_prerelease(self):
        self.assertEqual(classify_upgrade('26.1-R15.0p13', '26.2-R15.1b1'), 'minor')

    def test_ghostbsd_release_change(self):
        self.assertEqual(classify_upgrade('26.2-R15.1p2', '26.3-R15.1p5'), 'release')

    def test_ghostbsd_year_change(self):
        self.assertEqual(classify_upgrade('26.3-R15.1p9', '27.1-R15.1p9'), 'release')

    def test_patch_level_only(self):
        self.assertEqual(classify_upgrade('26.2-R15.1p2', '26.2-R15.1p3'), 'none')

    def test_suffix_only(self):
        self.assertEqual(classify_upgrade('26.2-R15.1b1', '26.2-R15.1'), 'none')
        self.assertEqual(classify_upgrade('26.2-R15.1', '26.2-R15.1p1'), 'none')

    def test_same_version(self):
        self.assertEqual(classify_upgrade('26.2-R15.1p2', '26.2-R15.1p2'), 'none')

    def test_remote_older(self):
        self.assertEqual(classify_upgrade('26.2-R15.1p2', '26.1-R15.0p13'), 'none')
        self.assertEqual(classify_upgrade('26.3-R15.1p5', '26.2-R15.1p2'), 'none')

    def test_unparsable(self):
        self.assertEqual(classify_upgrade('', '26.2-R15.1p2'), 'none')
        self.assertEqual(classify_upgrade('26.1-R15.0p13', ''), 'none')
        self.assertEqual(classify_upgrade('garbage', 'garbage'), 'none')


if __name__ == '__main__':
    unittest.main()
