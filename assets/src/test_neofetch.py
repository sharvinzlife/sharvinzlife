#!/usr/bin/env python3
"""Tests for the neofetch card generator and the stats fetcher."""
import re
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from unittest import mock

import fetch_stats as f
import gen_neofetch as g

FIXTURE = {
    "repos": 42,
    "commits": 12345,
    "stars": 678,
    "followers": 90,
    "loc": 1234567,
    "generated": "2026-10-10",
}


def luma(hexcol):
    r = int(hexcol[1:3], 16)
    gg = int(hexcol[3:5], 16)
    b = int(hexcol[5:7], 16)
    return 0.299 * r + 0.587 * gg + 0.114 * b


def local_tag(el):
    return el.tag.split("}")[-1]


class AsciiPortraitTests(unittest.TestCase):
    def test_shape_and_background(self):
        portrait = g.ascii_portrait()
        self.assertEqual(len(portrait), 30)
        for row in portrait:
            self.assertEqual(len(row), 56)
            for cell in row:
                self.assertEqual(len(cell), 2)
                ch, col = cell
                if col is None:
                    self.assertEqual(ch, " ")
                else:
                    self.assertRegex(col, r"^#[0-9a-f]{6}$")
        self.assertEqual(portrait[0][0], (" ", None))

    def test_non_background_is_lifted_and_inked(self):
        for row in g.ascii_portrait():
            for ch, col in row:
                if col is not None:
                    self.assertNotEqual(ch, " ")
                    self.assertGreaterEqual(luma(col), 70)


class UptimeTests(unittest.TestCase):
    def test_full_span(self):
        self.assertEqual(
            g.uptime("2020-11-11", date(2026, 10, 10)),
            "5 years, 10 months, 29 days",
        )

    def test_singular_day(self):
        self.assertEqual(
            g.uptime("2020-11-11", date(2020, 11, 12)),
            "0 years, 0 months, 1 day",
        )


class BuildSvgTests(unittest.TestCase):
    def setUp(self):
        self.svg = g.build_svg(FIXTURE, today=date(2026, 10, 10))

    def test_well_formed_xml(self):
        ET.fromstring(self.svg)

    def test_no_external_references(self):
        stripped = self.svg.replace("http://www.w3.org/2000/svg", "")
        self.assertNotIn("http", stripped)

    def test_no_email(self):
        self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", self.svg))

    def test_numbers_have_thousands_separators(self):
        for n in ("42", "12,345", "678", "90", "1,234,567"):
            self.assertIn(n, self.svg)

    def test_background_rect_is_first_after_defs(self):
        root = ET.fromstring(self.svg)
        after = [el for el in root if local_tag(el) != "defs"]
        first = after[0]
        self.assertEqual(local_tag(first), "rect")
        self.assertEqual(first.get("fill"), g.BG)
        self.assertEqual(first.get("width"), "1200")
        self.assertGreater(int(first.get("height")), 0)

    def test_missing_key_raises(self):
        for key in ("repos", "commits", "stars", "followers", "loc"):
            bad = dict(FIXTURE)
            del bad[key]
            with self.assertRaises(ValueError):
                g.build_svg(bad)

    def test_non_int_raises(self):
        for key in ("repos", "commits", "stars", "followers", "loc"):
            bad = dict(FIXTURE)
            bad[key] = "42"
            with self.assertRaises(ValueError):
                g.build_svg(bad)


class LocForTests(unittest.TestCase):
    def test_sums_additions_and_deletions(self):
        calls = {"n": 0}

        def fake(args):
            calls["n"] += 1
            if calls["n"] <= 3:
                return "HTTP/2.0 202 Accepted\n\n"
            return "HTTP/2.0 200 OK\n\n[[1700000000,100,-40],[1700086400,5,-5]]"

        with mock.patch.object(f.time, "sleep", lambda s: None):
            self.assertEqual(f.loc_for("demo", run=fake), 60)

    def test_persistent_202_raises_naming_repo(self):
        def fake(args):
            return "HTTP/2.0 202 Accepted\n\n"

        with mock.patch.object(f.time, "sleep", lambda s: None):
            with self.assertRaises(RuntimeError) as cm:
                f.loc_for("demo", run=fake)
        self.assertIn("demo", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
