#!/usr/bin/env python3
"""Tests for the neofetch card generator and the stats fetcher."""
import re
import textwrap
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

TODAY = date(2026, 10, 10)

HOBBIES = "Photography, Malayalam type design, Malayalam cinema"
PROJECTS = "Astroid bot, Stellar Media Organizer, Foldpix, Thenmavu font"


def local_tag(el):
    return el.tag.split("}")[-1]


def info_lines(svg):
    """Every info <text> line's rendered characters, in document order."""
    root = ET.fromstring(svg)
    return [
        "".join(el.itertext())
        for el in root.iter()
        if local_tag(el) == "text" and el.get("class")
    ]


def svg_for(layout):
    return g.build_svg(FIXTURE, layout=layout, today=TODAY)


class AsciiPortraitTests(unittest.TestCase):
    def test_shape_and_background(self):
        portrait = g.ascii_portrait()
        self.assertEqual(len(portrait), 58)
        for row in portrait:
            self.assertEqual(len(row), 81)
            for cell in row:
                self.assertEqual(len(cell), 2)
                ch, col = cell
                if col is None:
                    self.assertEqual(ch, " ")
                else:
                    self.assertEqual(col, g.WHITE)
                    self.assertIn(ch, g.RAMP_INV)
        self.assertEqual(portrait[0][0], (" ", None))

    def test_at_least_a_quarter_is_inked(self):
        cells = [cell for row in g.ascii_portrait() for cell in row]
        inked = [cell for cell in cells if cell[1] is not None]
        self.assertGreaterEqual(len(inked), len(cells) * 0.25)


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
        self.wide = svg_for(g.WIDE)
        self.narrow = svg_for(g.NARROW)

    def test_both_well_formed_xml(self):
        for svg in (self.wide, self.narrow):
            ET.fromstring(svg)

    def test_no_external_references(self):
        for svg in (self.wide, self.narrow):
            stripped = svg.replace("http://www.w3.org/2000/svg", "")
            self.assertNotIn("http", stripped)

    def test_no_email(self):
        for svg in (self.wide, self.narrow):
            self.assertIsNone(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", svg))

    def test_numbers_have_thousands_separators(self):
        for svg in (self.wide, self.narrow):
            for n in ("42", "12,345", "678", "90", "1,234,567"):
                self.assertIn(n, svg)

    def test_background_rect_is_first_after_defs(self):
        for svg, width in ((self.wide, "1200"), (self.narrow, "600")):
            root = ET.fromstring(svg)
            after = [el for el in root if local_tag(el) != "defs"]
            first = after[0]
            self.assertEqual(local_tag(first), "rect")
            self.assertEqual(first.get("fill"), g.BG)
            self.assertEqual(first.get("width"), width)
            self.assertGreater(int(first.get("height")), 0)

    def test_wide_geometry(self):
        self.assertIn('viewBox="0 0 1200 ', self.wide)
        self.assertIn('width="1200"', self.wide)
        self.assertIn('font-size="18"', self.wide)

    def test_narrow_geometry(self):
        self.assertIn('viewBox="0 0 600 ', self.narrow)
        self.assertIn('width="600"', self.narrow)
        self.assertIn('font-size="21"', self.narrow)

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


class LayoutTests(unittest.TestCase):
    def test_no_info_line_exceeds_max_chars(self):
        for layout in (g.WIDE, g.NARROW):
            for line in info_lines(svg_for(layout)):
                self.assertLessEqual(len(line), layout.max_chars, repr(line))

    def test_no_info_line_overflows_viewbox(self):
        for layout in (g.WIDE, g.NARROW):
            for line in info_lines(svg_for(layout)):
                right = layout.info_x + len(line) * 0.6 * layout.info_font
                self.assertLessEqual(right, layout.width - 20, repr(line))

    def test_long_values_wrap_on_word_boundaries(self):
        for layout in (g.WIDE, g.NARROW):
            joined = " ".join(l.strip() for l in info_lines(svg_for(layout)))
            self.assertIn(HOBBIES, joined)
            self.assertIn(PROJECTS, joined)

    def test_continuations_indented_to_value_column(self):
        col = 16
        for layout in (g.WIDE, g.NARROW):
            lines = info_lines(svg_for(layout))
            chunks = textwrap.wrap(HOBBIES, layout.max_chars - col)
            self.assertGreater(len(chunks), 1)
            for chunk in chunks[1:]:
                self.assertIn(" " * col + chunk, lines)

    def test_narrow_splits_stat_pairs(self):
        narrow = info_lines(svg_for(g.NARROW))
        wide = info_lines(svg_for(g.WIDE))
        self.assertFalse(any("Repos" in l and "Stars" in l for l in narrow))
        self.assertTrue(any("Repos" in l and "Stars" in l for l in wide))
        for key in ("Repos", "Stars", "Commits", "Followers", "Lines of code"):
            self.assertTrue(any(l.startswith(key) for l in narrow), key)


class LocForTests(unittest.TestCase):
    def test_sums_additions_and_deletions(self):
        calls = {"n": 0}

        def fake(args):
            calls["n"] += 1
            if calls["n"] <= 3:
                return "HTTP/2.0 202 Accepted\n\n"
            return "HTTP/2.0 200 OK\n\n[[1700000000,100,-40],[1700086400,5,-5]]"

        self.assertEqual(f.loc_for("demo", run=fake, sleep=lambda s: None), 60)

    def test_persistent_202_raises_naming_repo(self):
        def fake(args):
            return "HTTP/2.0 202 Accepted\n\n"

        with self.assertRaises(RuntimeError) as cm:
            f.loc_for("demo", run=fake, cache={}, warnings=[], sleep=lambda s: None)
        self.assertEqual(str(cm.exception), "demo: stats not ready")

    def test_persistent_202_uses_cached_value_with_warning(self):
        def fake(args):
            return "HTTP/2.0 202 Accepted\n\n"

        cache = {"repoA": 123}
        warnings = []
        self.assertEqual(
            f.loc_for("repoA", run=fake, cache=cache, warnings=warnings,
                      sleep=lambda s: None),
            123,
        )
        self.assertEqual(len(warnings), 1)
        self.assertIn("repoA", warnings[0])
        self.assertIn("123", warnings[0])

    def test_200_updates_cache(self):
        def fake(args):
            return "HTTP/2.0 200 OK\n\n[[1700000000,100,-40]]"

        cache = {}
        self.assertEqual(f.loc_for("repoA", run=fake, cache=cache,
                                   sleep=lambda s: None), 60)
        self.assertEqual(cache, {"repoA": 60})

    def test_backoff_schedule(self):
        sleeps = []

        def fake(args):
            return "HTTP/2.0 202 Accepted\n\n"

        with self.assertRaises(RuntimeError):
            f.loc_for("demo", run=fake, cache={}, warnings=[],
                      sleep=sleeps.append)
        self.assertEqual(sleeps, [2, 4, 8, 16, 30, 30, 30, 30])


class CommitsForTests(unittest.TestCase):
    def test_link_header_last_page(self):
        def fake(args):
            return (
                "HTTP/2.0 200 OK\n"
                "link: <https://api.github.com/repositories/1/commits?per_page=1&page=2774>; "
                'rel="last"\n\n[{"sha": "a"}]'
            )

        self.assertEqual(f.commits_for("demo", 100, run=fake), 2774)

    def test_no_link_header_counts_body(self):
        def fake(args):
            return "HTTP/2.0 200 OK\n\n[{\"sha\": \"a\"}]"

        self.assertEqual(f.commits_for("demo", 100, run=fake), 1)

    def test_empty_repo_skips_api(self):
        def fake(args):
            raise AssertionError("runner must not be called for an empty repo")

        self.assertEqual(f.commits_for("demo", 0, run=fake), 0)

    def test_error_status_raises_naming_repo(self):
        def fake(args):
            return "HTTP/2.0 404 Not Found\n\n{}"

        with self.assertRaises(RuntimeError) as cm:
            f.commits_for("demo", 100, run=fake)
        self.assertIn("demo", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
