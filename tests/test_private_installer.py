"""Registry-only distribution and upgrade contracts for the generic runtime."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from velnio_installer.runtime import __main__ as cli
from velnio_installer.runtime.installer import Installer, InstallerError, Options

ROOT = Path(__file__).resolve().parents[1]
LEGACY = "github_pat_fixture_must_not_be_used"


class RegistryInstallerTests(unittest.TestCase):
    def test_registry_auth_stays_outside_app(self):
        config = json.loads((ROOT / "velnio_installer/config.json").read_text())
        release = json.loads((ROOT / "velnio_installer/image-digests.json").read_text())
        self.assertEqual(config["image"], "ghcr.io/velnio/velnio-installer")
        self.assertEqual(config["version"], release["installer_version"])
        self.assertRegex(config["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(release["image"], config["image"])
        self.assertEqual(release["visibility"], "private")
        self.assertEqual(set(release["platforms"]), {"amd64", "arm64"})
        for digest in [release["index_digest"], *release["platforms"].values()]:
            self.assertRegex(digest, r"^sha256:[a-f0-9]{64}$")
        self.assertNotIn("github_token", config["options"])
        self.assertNotIn("github_token", config["schema"])
        self.assertFalse(config["docker_api"])
        self.assertFalse(config["full_access"])
        self.assertEqual(config["hassio_role"], "homeassistant")

    def test_upgrade_ignores_legacy_token_without_forwarding_it(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "options.json"
            path.write_text(json.dumps({"github_token": LEGACY, "backup_count": 7}))
            options = cli.load_options(path)
            self.assertEqual(options.product, "velnio")
            self.assertEqual(options.backup_count, 7)
            self.assertNotIn(LEGACY, repr(options))
            output = io.StringIO()
            with patch.dict("os.environ", {"SUPERVISOR_TOKEN": "local-fixture"}), patch("sys.argv", ["installer", "--options", str(path), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(output):
                installer.return_value.run.return_value = "unchanged"
                self.assertEqual(cli.main(), 0)
            self.assertNotIn(LEGACY, repr(installer.call_args))
            self.assertNotIn(LEGACY, output.getvalue())
            self.assertIn("READY: unchanged", output.getvalue())
            self.assertEqual(installer.call_args.args[1], Path(cli.get_product("velnio").payload_path))

    def test_unknown_options_fail_before_installer(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "options.json"
            for data in ({"registry_password": LEGACY}, [], {"product": "r4sls08"}, {"health_timeout": 0}):
                path.write_text(json.dumps(data))
                with self.subTest(data_type=type(data).__name__), self.assertRaises(InstallerError) as error:
                    cli.load_options(path)
                self.assertNotIn(LEGACY, str(error.exception))

    def test_pending_transaction_recovers_before_deployment(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            path = root / "options.json"
            path.write_text('{}')
            (root / ".velnio-installer").mkdir()
            (root / ".velnio-installer/journal.json").write_text('{}')
            with patch.dict("os.environ", {"SUPERVISOR_TOKEN": "local-fixture"}), patch("sys.argv", ["installer", "--config-root", str(root), "--options", str(path), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(io.StringIO()):
                installer.return_value.run.return_value = "recovered"
                self.assertEqual(cli.main(), 0)
            self.assertTrue(installer.return_value.run.call_args.kwargs["recover_only"])

    def test_recovery_never_requires_a_payload(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            installer = Installer(root, root / "absent", root / "absent.json", Mock(product=cli.get_product("velnio")), Options(product="velnio"), product="velnio")
            with patch.object(installer, "recover") as recover, patch.object(installer, "deploy") as deploy:
                self.assertEqual(installer.run(recover_only=True), "recovered")
                recover.assert_called_once_with(None)
                deploy.assert_not_called()

    def test_public_tree_has_no_native_integration_or_archives(self):
        root = ROOT / "velnio_installer"
        self.assertFalse((root / "payload").exists())
        self.assertFalse((root / "release-velnio.json").exists())
        self.assertFalse((root / "runtime/private_release.py").exists())
        for p in root.rglob('*'):
            self.assertNotIn(p.suffix, {'.zip', '.tar', '.gz', '.bin', '.hex'})
            if p.is_file() and '__pycache__' not in p.parts:
                self.assertNotIn(b'github_pat_', p.read_bytes())


if __name__ == "__main__":
    unittest.main()
