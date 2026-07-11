"""いつもの改行 for Chat の純粋ロジックのテスト。

Windows上で実行してください（本体モジュールがWin32 APIを読み込むため）:

    .\\.venv\\Scripts\\python.exe -m unittest test_itsumono_kaigyo -v

キーボードフック・IME・UIAなどOSと結合した挙動はここでは検証しません。
"""

import json
import tempfile
import unittest
from pathlib import Path

import itsumono_kaigyo as app


class ProcessNameListTests(unittest.TestCase):
    def test_lowercases_and_appends_exe(self):
        self.assertEqual(
            app.process_name_list(["Sleipnir", "CHROME.EXE"]),
            ["sleipnir.exe", "chrome.exe"],
        )

    def test_removes_duplicates_and_blanks(self):
        self.assertEqual(
            app.process_name_list(["sleipnir.exe", "Sleipnir", "", "  "]),
            ["sleipnir.exe"],
        )

    def test_uses_default_when_not_list(self):
        self.assertEqual(app.process_name_list(None, ("a.exe",)), ["a.exe"])
        self.assertEqual(app.process_name_list("x", ("a.exe",)), ["a.exe"])


class KeywordsMatchTests(unittest.TestCase):
    def test_plain_partial_match_is_case_insensitive(self):
        self.assertTrue(app.keywords_match("ChatGPT - Chrome", ("chatgpt",), False))
        self.assertFalse(app.keywords_match("Google", ("chatgpt",), False))

    def test_regex_search(self):
        self.assertTrue(
            app.keywords_match(
                "google.com/search?q=x&udm=50",
                (r"google\.[a-z.]+/search\?(.*&)?udm=50(&|$)",),
                True,
            )
        )
        self.assertFalse(
            app.keywords_match(
                "google.com/search?q=x",
                (r"google\.[a-z.]+/search\?(.*&)?udm=50(&|$)",),
                True,
            )
        )

    def test_invalid_regex_is_ignored(self):
        self.assertFalse(app.keywords_match("anything", ("[",), True))

    def test_multiple_keywords_are_or_condition(self):
        self.assertTrue(app.keywords_match("x.com/home", ("twitter.com", "x.com"), False))


class ProcessesMatchTests(unittest.TestCase):
    def _target(self, processes, regex=False):
        return app.TargetDefinition(
            "key", "label", "cat", "App", app.ACTION_SHIFT_ENTER, app.MODE_ENTER,
            processes=processes, processes_regex=regex,
        )

    def test_exact_match_is_case_insensitive(self):
        target = self._target(("Sleipnir.exe",))
        self.assertTrue(app.processes_match({"sleipnir.exe"}, target))
        self.assertFalse(app.processes_match({"chrome.exe"}, target))

    def test_regex_uses_fullmatch(self):
        target = self._target((r"sleip.*",), regex=True)
        self.assertTrue(app.processes_match({"sleipnir.exe"}, target))
        target_partial = self._target((r"sleip",), regex=True)
        self.assertFalse(app.processes_match({"sleipnir.exe"}, target_partial))

    def test_empty_processes_never_match(self):
        target = self._target(())
        self.assertFalse(app.processes_match({"sleipnir.exe"}, target))


class ModeConversionTests(unittest.TestCase):
    def test_on_off_maps_to_internal_modes(self):
        self.assertEqual(
            app.internal_mode_from_config_values(app.ACTION_SHIFT_ENTER, "on"),
            app.MODE_ENTER,
        )
        self.assertEqual(
            app.internal_mode_from_config_values(app.ACTION_SHIFT_ENTER, "off"),
            app.MODE_OFF,
        )

    def test_round_trip(self):
        for mode in (app.MODE_ENTER, app.MODE_OFF):
            config_value = app.config_mode_from_values(app.ACTION_SHIFT_ENTER, mode)
            self.assertEqual(
                app.internal_mode_from_config_values(app.ACTION_SHIFT_ENTER, config_value),
                mode,
            )


class LooksLikeBrowserUrlTests(unittest.TestCase):
    def test_accepts_urls(self):
        self.assertTrue(app.looks_like_browser_url("https://chatgpt.com/"))
        self.assertTrue(app.looks_like_browser_url("chatgpt.com"))

    def test_rejects_plain_text(self):
        self.assertFalse(app.looks_like_browser_url("hello world"))
        self.assertFalse(app.looks_like_browser_url("abc"))
        self.assertFalse(app.looks_like_browser_url(""))


class WrapStateTests(unittest.TestCase):
    """Shiftラップ方式の状態遷移。時刻を明示的に与えて検証する。"""

    def setUp(self):
        self.state = app.WrapState()

    def test_begin_returns_true_only_on_first_call(self):
        self.assertTrue(self.state.begin(now=0.0))
        self.assertFalse(self.state.begin(now=0.1))
        self.assertTrue(self.state.active)

    def test_single_press_releases_after_hold(self):
        self.state.begin(now=0.0)
        self.assertGreater(self.state.remaining(now=0.1), 0)
        self.assertLessEqual(
            self.state.remaining(now=app.WRAP_SHIFT_HOLD_SECONDS + 0.01), 0
        )

    def test_keydown_extends_hold(self):
        self.state.begin(now=0.0)
        self.state.extend(now=0.2)
        self.assertGreater(self.state.remaining(now=0.4), 0)

    def test_keyup_shortens_hold_to_linger(self):
        self.state.begin(now=0.0)
        self.state.shorten(now=0.05)
        linger_deadline = 0.05 + app.WRAP_SHIFT_KEYUP_LINGER_SECONDS
        self.assertGreater(self.state.remaining(now=linger_deadline - 0.01), 0)
        self.assertLessEqual(self.state.remaining(now=linger_deadline + 0.01), 0)

    def test_shorten_never_lengthens_hold(self):
        self.state.begin(now=0.0)
        self.state.shorten(now=0.0, linger_seconds=10.0)
        self.assertLessEqual(
            self.state.remaining(now=app.WRAP_SHIFT_HOLD_SECONDS + 0.01), 0
        )

    def test_max_hold_caps_continuous_extends(self):
        self.state.begin(now=0.0)
        now = 0.0
        while now < app.WRAP_SHIFT_MAX_HOLD_SECONDS + 0.5:
            self.state.extend(now=now)
            now += 0.1
        self.assertLessEqual(
            self.state.remaining(now=app.WRAP_SHIFT_MAX_HOLD_SECONDS + 0.01), 0
        )

    def test_release_returns_true_once_and_sets_residual_window(self):
        self.state.begin(now=0.0)
        self.assertTrue(self.state.release(now=1.0))
        self.assertFalse(self.state.release(now=1.0))
        self.assertFalse(self.state.active)
        self.assertTrue(
            self.state.residual_shift_active(
                now=1.0 + app.WRAP_RESIDUAL_SHIFT_SECONDS - 0.01
            )
        )
        self.assertFalse(
            self.state.residual_shift_active(
                now=1.0 + app.WRAP_RESIDUAL_SHIFT_SECONDS + 0.01
            )
        )

    def test_can_begin_again_after_release(self):
        self.state.begin(now=0.0)
        self.state.release(now=1.0)
        self.assertTrue(self.state.begin(now=1.1))
        self.assertGreater(self.state.remaining(now=1.2), 0)

    def test_inactive_state_is_inert(self):
        self.state.extend(now=0.0)
        self.state.shorten(now=0.0)
        self.assertEqual(self.state.remaining(now=0.0), 0.0)
        self.assertFalse(self.state.release(now=0.0))


class ConfigMigrationTests(unittest.TestCase):
    def _load_with(self, data):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "settings.json"
            path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8-sig")
            original = app.CONFIG_PATH
            app.CONFIG_PATH = path
            try:
                return app.load_config()
            finally:
                app.CONFIG_PATH = original

    def test_defaults_include_sleipnir(self):
        config = self._load_with({})
        self.assertIn("sleipnir.exe", config["browser_processes"])
        self.assertIn("sleipnir.exe", config["chromium_browser_processes"])
        self.assertEqual(config["shift_enter_wrap_processes"], ["sleipnir.exe"])

    def test_migrates_old_keydown_key_to_wrap(self):
        config = self._load_with(
            {"shift_enter_send_on_keydown_processes": ["Sleipnir", "foo"]}
        )
        self.assertEqual(
            config["shift_enter_wrap_processes"], ["sleipnir.exe", "foo.exe"]
        )
        self.assertNotIn("shift_enter_send_on_keydown_processes", config)

    def test_new_wrap_key_takes_precedence_over_old_key(self):
        config = self._load_with(
            {
                "shift_enter_wrap_processes": ["bar"],
                "shift_enter_send_on_keydown_processes": ["Sleipnir"],
            }
        )
        self.assertEqual(config["shift_enter_wrap_processes"], ["bar.exe"])

    def test_removed_method_key_is_dropped(self):
        config = self._load_with(
            {"shift_enter_send_method_by_process": {"sleipnir.exe": "vk"}}
        )
        self.assertNotIn("shift_enter_send_method_by_process", config)

    def test_target_modes_survive_load(self):
        config = self._load_with({"targets": {"chatgpt_web": "off"}})
        self.assertEqual(config["targets"]["chatgpt_web"], app.MODE_OFF)


if __name__ == "__main__":
    unittest.main()
