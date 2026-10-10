#!/usr/bin/env python3
"""Offline tests for the force pack's hardware panels: the committed layouts (ports/<id>/layout.conf,
ports/ml185/vst/layout.conf) and the hwpanel toolkit. No device, no Docker:
    python3 ports/force-pack/test_force_pack.py

Two kinds of check:
  - playable on a Force: every control inside the plugin area, knobs small enough for MPC's filmstrips, every
    Q-Link on a control its page shows, at most 16 per set, touch boxes that don't overlap;
  - the hardware's placement: controls at the positions measured from each machine's reference photo (README.md
    lists the photos), so a later edit can't quietly move a knob away from where the hardware has it."""
import glob
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, HERE)
import shadow_skin  # noqa: E402
import hwpanel  # noqa: E402

Y_OFF, W, H = 86, 1280, 628
LAYOUTS = sorted(glob.glob(os.path.join(HERE, "ports", "*", "layout.conf"))) + \
    [os.path.join(REPO, "ports", "ml185", "vst", "layout.conf")]
CONTROLS = ("knob", "slider_v", "slider_h", "toggle", "button", "enum_h", "enum_v", "popup", "readout", "menu", "stepper")


def pid(path):
    return os.path.basename(os.path.dirname(path)) if "force-pack" in path else "ml185"


def layout(name):
    path = [p for p in LAYOUTS if pid(p) == name][0]
    return shadow_skin.parse_layout(path)[0]


def where(tabs, key, tab=0, kind=None):
    """(cx, cy) of key's control on a tab, in plugin-area pixels (the photo's frame)."""
    for w in tabs[tab]["widgets"]:
        if w.get("key") == key and (kind is None or w["kind"] == kind) and "cx" in w:
            return w["cx"], w["cy"] - Y_OFF
    raise AssertionError("%s not on tab %s" % (key, tabs[tab]["name"]))


class Playable(unittest.TestCase):
    def test_layouts_present(self):
        self.assertEqual(len(LAYOUTS), 24)

    def test_controls_inside_plugin_area(self):
        for path in LAYOUTS:
            for t in shadow_skin.parse_layout(path)[0]:
                for w in t["widgets"]:
                    if w["kind"] in CONTROLS and "cx" in w:
                        with self.subTest(plugin=pid(path), tab=t["name"], key=w.get("key")):
                            self.assertTrue(0 <= w["cx"] <= W and Y_OFF <= w["cy"] <= Y_OFF + H)

    def test_knobs_fit_mpc_filmstrips(self):
        for path in LAYOUTS:
            for t in shadow_skin.parse_layout(path)[0]:
                for w in t["widgets"]:
                    if w["kind"] == "knob":
                        with self.subTest(plugin=pid(path), key=w.get("key")):
                            self.assertLessEqual(w["r"], 59)

    def test_qlinks_on_shown_controls(self):
        for path in LAYOUTS:
            for t in shadow_skin.parse_layout(path)[0]:
                keys = {w.get("key") for w in t["widgets"]}
                for title, ks in t["qlinks"]:
                    with self.subTest(plugin=pid(path), page=title):
                        self.assertLessEqual(len(ks), 16)
                        self.assertEqual([k for k in ks if k != "-" and k not in keys], [])

    def test_at_points_inside_plugin_area(self):
        for path in LAYOUTS:
            for t in shadow_skin.parse_layout(path)[0]:
                for w in t["widgets"]:
                    if w.get("at"):
                        for x, y in (map(int, xy.split(":")) for xy in w["at"].split(",")):
                            with self.subTest(plugin=pid(path), key=w["key"], at=(x, y)):
                                self.assertTrue(0 <= x <= W and Y_OFF <= y <= Y_OFF + H)


class HwPanel(unittest.TestCase):
    def test_switch_at_writes_points_and_rects(self):
        p = hwpanel.Page("T")
        p.switch("k", 0, 0, 3, vertical=False, sw=58, sh=50, at=[(343, 580), (407, 580), (655, 505)])
        line = p.lines({"k": {"nopts": 3}})[0]
        self.assertIn('at="343:666,407:666,655:591"', line)
        self.assertTrue(line.startswith("enum_h "))
        self.assertEqual(p.seg_rects(p.ctl[0])[2], (626, 480, 58, 50))

    def test_option_count_checked(self):
        p = hwpanel.Page("T")
        p.switch("k", 0, 0, 2, at=[(10, 10), (20, 20)])
        with self.assertRaises(SystemExit):
            p.lines({"k": {"nopts": 3}})

    def test_fit_widths_keeps_neighbours_apart(self):
        p = hwpanel.Page("T")
        for i in range(4):
            p.knob("k%d" % i, 370 + 70.1 * i, 116, 14, "LEVEL")
        p.fit_widths()
        for a, b in zip(p.ctl, p.ctl[1:]):
            ra, rb = p.box(a, a["bw_auto"]), p.box(b, b["bw_auto"])
            self.assertLessEqual(ra[2], rb[0] + 2)

    def test_knob_too_big_for_filmstrip(self):
        with self.assertRaises(SystemExit):
            hwpanel.Page("T").knob("k", 100, 100, 60, "BIG")


class HardwarePlacement(unittest.TestCase):
    """Positions measured from the reference photos (README.md), scaled to the 1280 x 628 plugin area."""
    TOL = 3

    def near(self, got, want):
        self.assertLessEqual(abs(got[0] - want[0]), self.TOL, (got, want))
        self.assertLessEqual(abs(got[1] - want[1]), self.TOL, (got, want))

    def test_tb303_top_row(self):
        t = layout("303")
        for i, k in enumerate(("tuning", "cutoff", "resonance", "env_mod", "decay", "accent")):
            self.near(where(t, k), (381 + 94.5 * i, 80))
        self.near(where(t, "volume"), (1109, 230))

    def test_tr808_instrument_columns(self):
        # the photo's twelve columns from x 335, 70.1 px apart; LEVEL / TONE / DECAY rows (instrument section x 1.109)
        t = layout("8w8")
        y = lambda py: 85 + (py - 85) * 1.109
        levels = ["vel_depth", "bd_level", "sd_level", "lt_level", "mt_level", "ht_level", "rs_level", "cp_level",
                  "cb_level", "cy_level", "oh_level", "ch_level"]
        for i, k in enumerate(levels):
            self.near(where(t, k), (370 + 70.1 * i, y(113)))
        self.near(where(t, "bd_tone"), (440.1, y(180)))
        self.near(where(t, "sd_snappy"), (510.2, y(245)))
        self.near(where(t, "oh_decay"), (1071, y(245)))

    def test_tr909_sections(self):
        t = layout("9w9")
        for k, x in (("bd_c_tune", 220), ("bd_c_level", 275), ("sd_c_tune", 341), ("ht_c_level", 760),
                     ("rs_volume", 826), ("hc_volume", 881), ("cr_volume", 1069), ("rc_volume", 1124)):
            self.near(where(t, k), (x, 200))
        for k, x in (("bd_c_attack", 220), ("chh_decay", 948), ("ohh_decay", 1003), ("rc_pitch", 1124)):
            self.near(where(t, k), (x, 270))
        self.near(where(t, "accent"), (139.5, 270))
        self.near(where(t, "volume"), (1126, 364))

    def test_cr78_panel(self):
        t = layout("cw78")
        self.near(where(t, "volume"), (297, 138))
        for k, x in (("mb_level", 500), ("tb_level", 552), ("gu_level", 604)):   # ADD VOICE sliders
            self.near(where(t, k), (x, 138))
        self.near(where(t, "vel_depth"), (762, 262))   # ACCENT
        self.near(where(t, "rhy_mode"), (1150, 405))   # START / STOP
        w = [w for w in t[0]["widgets"] if w.get("key") == "rhy_style"][0]
        pts = [tuple(int(v) for v in xy.split(":")) for xy in w["at"].split(",")]
        low = [343, 407, 470, 532, 596, 657, 720, 782, 845, 908, 970]   # WALTZ .. BEGUINE / RHUMBA
        up = [655, 720, 785, 848, 912, 975]                             # ROCK-1 .. DISCO-2
        self.assertEqual(pts, [(x, 580 + Y_OFF) for x in low] + [(x, 505 + Y_OFF) for x in up])

    def test_microfreak_panel(self):
        # top-view photo, panel x 195..1815 / y 70..660 to the plugin area
        t = layout("mrhyde")
        X = lambda x: (x - 195) * 0.790
        Y = lambda y: (y - 70) * 1.064
        for k, x, y in (("glide_ms", 295, 385), ("harmonics", 573, 385), ("morph", 797, 385), ("filter_cutoff", 1043, 385),
                        ("filter_resonance", 1160, 385), ("cycle_attack_ms", 1392, 385), ("lfo_rate", 1160, 570),
                        ("env_attack_ms", 1393, 570), ("env_sustain", 1627, 570), ("volume", 1722, 195)):
            self.near(where(t, k, kind="knob"), (X(x), Y(y)))

    def test_tr606_step_keys_unmoved_by_extra_pages(self):
        # every 606 page shares the photo's chassis: the same nine level knobs on the top strip
        t = layout("6w6")
        for i, k in enumerate(["vel_depth", "bd_level", "sd_level", "lt_level", "ht_level", "cy_level", "oh_level",
                               "ch_level", "cp_level"]):
            self.near(where(t, k), (252 + 94.5 * i, 78))


if __name__ == "__main__":
    unittest.main()
