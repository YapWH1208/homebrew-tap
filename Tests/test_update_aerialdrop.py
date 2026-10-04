"""Offline checks against the fixture used by AerialDrop's canonical resolver."""

import importlib.util
import json
import re
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("update_aerialdrop", ROOT / "Scripts/update-aerialdrop.py")
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)
FIXTURE = json.loads((ROOT / "Tests/Fixtures/compatibility.json").read_text(encoding="utf-8"))


class UpdateAerialDropTests(unittest.TestCase):
    def test_unpinned_selection_matches_shared_resolver_fixture(self):
        for case in FIXTURE["cases"]:
            if "version" in case:
                continue
            with self.subTest(case=case["name"]):
                catalogue = FIXTURE["catalogues"][case["catalogue"]]
                selected = updater.selected_or_none(
                    FIXTURE["policy"], catalogue, case["macos"], case["arch"]
                )
                self.assertEqual(
                    selected["version"] if selected else None, case["expected_version"]
                )

    def test_static_os_branches_choose_correct_release(self):
        policy = {
            **FIXTURE["policy"],
            "releases": [record for record in FIXTURE["policy"]["releases"]
                         if record["architectures"] == ["arm64"]],
        }
        text = updater.generate_stanzas(policy, FIXTURE["catalogues"]["base"])
        self.assertIn('on_tahoe do\n    version "1.1.9"', text)
        self.assertIn('on_golden_gate :or_newer do\n    version "1.1.10"', text)
        self.assertIn(
            'url "https://github.com/YapWH1208/AerialDrop/releases/download/'
            'v1.1.10/AerialDrop-1.1.10-macOS.zip"', text
        )
        self.assertIn("depends_on arch: :arm64", text)
        self.assertEqual(self.branch_version(text, 26), "1.1.9")
        self.assertEqual(self.branch_version(text, 27), "1.1.10")
        self.assertEqual(self.branch_version(text, 28), "1.1.10")

    def test_maximum_and_gaps_do_not_fall_through(self):
        policy = {
            "schema_version": 1,
            "releases": [record for record in FIXTURE["policy"]["releases"]
                         if record["version"] == "1.2.0"],
        }
        text = updater.generate_stanzas(policy, FIXTURE["catalogues"]["bounds"])
        self.assertEqual(self.branch_version(text, 26), "1.2.0")
        self.assertIsNone(self.branch_version(text, 27))
        self.assertIsNone(self.branch_version(text, 28))
        self.assertIn("depends_on arch: :x86_64", text)

    def test_mixed_architecture_requires_explicit_new_dsl_mapping(self):
        with self.assertRaisesRegex(updater.CompatibilityError, "multiple architectures"):
            updater.generate_stanzas(FIXTURE["policy"], FIXTURE["catalogues"]["base"])

    def test_unknown_macos_branch_requires_supported_homebrew_symbol(self):
        policy = {
            "schema_version": 1,
            "releases": [{"version": "1.1.10", "min_macos": 28,
                          "max_macos": None, "architectures": ["arm64"]}],
        }
        with self.assertRaisesRegex(updater.CompatibilityError, "macOS 28 requires"):
            updater.generate_stanzas(policy, [FIXTURE["catalogues"]["base"][2]])

    def test_unpublished_future_declaration_keeps_existing_unbounded_branch(self):
        policy = {
            "schema_version": 1,
            "releases": [
                {"version": "1.1.9", "min_macos": 26, "max_macos": None,
                 "architectures": ["arm64"]},
                {"version": "1.1.10", "min_macos": 28, "max_macos": None,
                 "architectures": ["arm64"]},
            ],
        }
        text = updater.generate_stanzas(policy, [FIXTURE["catalogues"]["base"][1]])
        self.assertIn("on_tahoe :or_newer do", text)
        self.assertNotIn("on_golden_gate", text)

    def test_render_is_deterministic_and_preserves_manual_stanzas(self):
        policy = {
            **FIXTURE["policy"],
            "releases": [record for record in FIXTURE["policy"]["releases"]
                         if record["architectures"] == ["arm64"]],
        }
        with tempfile.TemporaryDirectory() as directory:
            cask = Path(directory) / "aerialdrop.rb"
            cask.write_text((ROOT / "Casks/aerialdrop.rb").read_text(encoding="utf-8"),
                            encoding="utf-8")
            self.assertTrue(updater.update_cask(cask, policy, FIXTURE["catalogues"]["base"]))
            first = cask.read_text(encoding="utf-8")
            self.assertFalse(updater.update_cask(cask, policy, FIXTURE["catalogues"]["base"]))
            self.assertEqual(first, cask.read_text(encoding="utf-8"))
            self.assertIn("postflight do", first)
            self.assertIn("zap trash:", first)

    def test_fetch_pins_policy_and_reads_every_page(self):
        commit = 'a' * 40
        first_page = [{'tag_name': f'v9.0.{index}'} for index in range(100)]
        last_page = [FIXTURE['catalogues']['base'][1]]
        with patch.object(updater, 'get_json', side_effect=[
            {'commit': {'sha': commit}}, FIXTURE['policy'], first_page, last_page
        ]) as fetch:
            policy, catalogue = updater.fetch_official_data(None)
        self.assertEqual(policy, FIXTURE['policy'])
        self.assertEqual(catalogue, first_page + last_page)
        self.assertEqual(fetch.call_args_list[1].args[0],
                         f'{updater.RAW}/{commit}/docs/release-compatibility.json')
        self.assertTrue(fetch.call_args_list[2].args[0].endswith('per_page=100&page=1'))
        self.assertTrue(fetch.call_args_list[3].args[0].endswith('per_page=100&page=2'))

    def test_oversized_release_page_is_rejected(self):
        with patch.object(updater, 'get_json', side_effect=[
            {'commit': {'sha': 'a' * 40}}, FIXTURE['policy'], [{}] * 101
        ]):
            with self.assertRaisesRegex(updater.CompatibilityError, 'exceeds 100 entries'):
                updater.fetch_official_data(None)

    def test_failed_generation_preserves_cask(self):
        with tempfile.TemporaryDirectory() as directory:
            cask = Path(directory) / 'aerialdrop.rb'
            original = (ROOT / 'Casks/aerialdrop.rb').read_text(encoding='utf-8')
            cask.write_text(original, encoding='utf-8')
            with self.assertRaises(updater.CompatibilityError):
                updater.update_cask(cask, {'schema_version': 2, 'releases': []}, [])
            self.assertEqual(cask.read_text(encoding='utf-8'), original)

    @staticmethod
    def branch_version(stanzas: str, macos: int) -> str | None:
        symbols = {26: "tahoe", 27: "golden_gate"}
        branches = re.findall(
            r'  on_(tahoe|golden_gate)( :or_newer)? do\n    version "([^"]+)"', stanzas
        )
        for symbol, modifier, version in branches:
            branch_macos = {value: key for key, value in symbols.items()}[symbol]
            if macos == branch_macos or (modifier and macos >= branch_macos):
                return version
        return None


if __name__ == "__main__":
    unittest.main()
