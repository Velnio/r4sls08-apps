"""Security and distribution contracts for the public, payload-free installer."""

import hashlib
import io
import json
import stat
import tempfile
import time
import unittest
import urllib.error
import contextlib
import warnings
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

from velnio_installer.runtime import private_release as private
from velnio_installer.runtime.__main__ import load_options
from velnio_installer.runtime import __main__ as cli
from velnio_installer.runtime.installer import InstallerError

TOKEN = "github_pat_fixture_do_not_use"
ROOT = Path(__file__).resolve().parents[1]


def zip_bytes(names):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        for name, data in names:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                archive.writestr(name, data)
    return stream.getvalue()


class Response:
    status = 200

    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read(self, size):
        return self.stream.read(size)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stream.close()


class DownloadTests(unittest.TestCase):
    def test_redirect_does_not_forward_pat_to_asset_host(self):
        requests = []

        class Opener:
            def open(self, request, **kwargs):
                requests.append(request)
                if len(requests) == 1:
                    raise urllib.error.HTTPError(request.full_url, 302, "redirect", {
                        "Location": "https://release-assets.githubusercontent.com/asset?signature=fixture"
                    }, io.BytesIO())
                return Response(b"payload")

        with patch.object(private.urllib.request, "build_opener", return_value=Opener()):
            value = private.request_bytes(private.API + "/repos/Velnio/velnio-ha/releases/assets/1",
                                          TOKEN, "application/octet-stream", 20, time.monotonic() + 10)
        self.assertEqual(value, b"payload")
        self.assertEqual(requests[0].get_header("Authorization"), "Bearer " + TOKEN)
        self.assertIsNone(requests[1].get_header("Authorization"))

    def test_rejects_untrusted_redirect_before_sending_pat(self):
        for target in ("http://release-assets.githubusercontent.com/asset", "https://evil.example/file",
                       "https://api.github.com/repos/other/repo", "https://release-assets.githubusercontent.com:444/file"):
            with self.subTest(target=target):
                opener = unittest.mock.Mock()
                opener.open.side_effect = urllib.error.HTTPError(private.API, 302, "redirect", {"Location": target}, io.BytesIO())
                with patch.object(private.urllib.request, "build_opener", return_value=opener):
                    with self.assertRaises(InstallerError):
                        private.request_bytes(private.API, TOKEN, "application/json", 10, time.monotonic() + 10)
                self.assertEqual(opener.open.call_count, 1)

    def test_auth_error_does_not_echo_token_or_response(self):
        opener = unittest.mock.Mock()
        opener.open.side_effect = urllib.error.HTTPError(private.API, 401, TOKEN, {}, io.BytesIO(TOKEN.encode()))
        with patch.object(private.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(InstallerError) as error:
                private.request_bytes(private.API, TOKEN, "application/json", 10, time.monotonic() + 10)
        self.assertNotIn(TOKEN, str(error.exception))
        self.assertIn("401", str(error.exception))

    def test_bounds_response_size(self):
        opener = unittest.mock.Mock()
        opener.open.return_value = Response(b"x" * 11)
        with patch.object(private.urllib.request, "build_opener", return_value=opener):
            with self.assertRaises(InstallerError):
                private.request_bytes(private.API, TOKEN, "application/json", 10, time.monotonic() + 10)

    def test_deadline_stops_before_network(self):
        with patch.object(private.urllib.request, "build_opener") as factory:
            with self.assertRaises(InstallerError):
                private.request_bytes(private.API, TOKEN, "application/json", 10, time.monotonic() - 1)
            factory.return_value.open.assert_not_called()

    def test_no_token_stops_before_network_and_extraction(self):
        for token in ("", None, "contains\nnewline", "x" * 513):
            with self.subTest(token_type=type(token).__name__), tempfile.TemporaryDirectory() as name:
                with patch.object(private, "request_bytes") as request:
                    with self.assertRaises(InstallerError):
                        private.prepare_private_release(token, ROOT / "velnio_installer/private-release.json", Path(name))
                    request.assert_not_called()
                    self.assertEqual(list(Path(name).iterdir()), [])

    def test_rejects_checksum_mismatch_before_writing(self):
        plan = json.loads((ROOT / "velnio_installer/private-release.json").read_text())
        metadata = json.dumps({"draft": False, "tag_name": plan["tag"], "assets": [
            {"name": spec["name"], "id": index} for index, spec in enumerate(plan["assets"].values(), 1)
        ]}).encode()
        with tempfile.TemporaryDirectory() as name, patch.object(private, "request_bytes", side_effect=[metadata, b"corrupt"]):
            with self.assertRaisesRegex(InstallerError, "checksum mismatch"):
                private.prepare_private_release(TOKEN, ROOT / "velnio_installer/private-release.json", Path(name))
            self.assertEqual(list(Path(name).iterdir()), [])

    def test_valid_pinned_payload_is_verified(self):
        archive = zip_bytes([("custom_components/velnio/__init__.py", b"# fixture\n"),
                             ("custom_components/velnio/manifest.json", b'{"domain":"velnio","version":"0.7.3"}')])
        manifest = json.dumps({"integration_version": "0.7.3", "artifact": {
            "archive_sha256": hashlib.sha256(archive).hexdigest()}}).encode()
        plan = {"schema": 1, "repository": "Velnio/velnio-ha", "tag": "velnio-0.7.3", "integration_version": "0.7.3", "assets": {
            "archive": {"name": "velnio-0.7.3.zip", "sha256": hashlib.sha256(archive).hexdigest()},
            "manifest": {"name": "velnio-0.7.3.installer.json", "sha256": hashlib.sha256(manifest).hexdigest()}}}
        metadata = json.dumps({"draft": False, "tag_name": plan["tag"], "assets": [
            {"name": spec["name"], "id": index} for index, spec in enumerate(plan["assets"].values(), 1)
        ]}).encode()
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "plan.json").write_text(json.dumps(plan))
            with patch.object(private, "request_bytes", side_effect=[metadata, archive, manifest]), patch.object(private, "validate_release") as validate:
                payload, release = private.prepare_private_release(TOKEN, root / "plan.json", root)
            self.assertEqual((payload / "__init__.py").read_bytes(), b"# fixture\n")
            self.assertEqual(release.read_bytes(), manifest)
            validate.assert_called_once_with(payload, release, "velnio")
            self.assertNotIn(TOKEN, "".join(p.read_text() for p in root.rglob("*") if p.is_file()))


class ArchiveTests(unittest.TestCase):
    def test_extracts_only_integration(self):
        with tempfile.TemporaryDirectory() as name:
            private.unpack_archive(zip_bytes([("custom_components/velnio/manifest.json", b"{}"),
                                              ("docs/info.md", b"not installed")]), Path(name))
            self.assertEqual([p.name for p in Path(name).iterdir()], ["manifest.json"])

    def test_traversal_and_duplicate_members_are_rejected_before_extraction(self):
        for names in ([('../escape.py', b'bad')], [('/absolute.py', b'bad')],
                      [('custom_components/velnio/../escape.py', b'bad')],
                      [('custom_components/velnio/x\\y', b'bad')],
                      [('custom_components/velnio/./bad.py', b'bad')],
                      [('same', b'a'), ('same', b'b')]):
            with self.subTest(names=[n for n, _ in names]), tempfile.TemporaryDirectory() as name:
                with self.assertRaises(InstallerError):
                    private.unpack_archive(zip_bytes(names), Path(name))
                self.assertEqual(list(Path(name).iterdir()), [])

    def test_symlink_member_is_rejected(self):
        info = zipfile.ZipInfo('custom_components/velnio/link')
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with tempfile.TemporaryDirectory() as name:
            with self.assertRaises(InstallerError):
                private.unpack_archive(zip_bytes([(info, b'/etc/passwd')]), Path(name))


class PublicDistributionTests(unittest.TestCase):
    def test_catalog_uses_local_build_and_masked_pat(self):
        config = json.loads((ROOT / "velnio_installer/config.json").read_text())
        self.assertNotIn("image", config)
        self.assertEqual(config["schema"]["github_token"], "password")
        self.assertEqual(config["options"]["github_token"], "")
        self.assertEqual(config["version"], "1.0.20")
        self.assertIn("1.0.20", config["breaking_versions"])

    def test_pat_is_not_passed_to_transaction_options(self):
        with tempfile.TemporaryDirectory() as name:
            path = Path(name) / "options.json"
            path.write_text(json.dumps({"github_token": TOKEN}))
            options, token = load_options(path)
            self.assertEqual(token, TOKEN)
            self.assertEqual(options.product, "velnio")
            self.assertNotIn(TOKEN, repr(options))

    def test_public_tree_has_no_integration_payload(self):
        addon = ROOT / "velnio_installer"
        self.assertFalse((addon / "payload").exists())
        self.assertFalse((addon / "custom_components").exists())
        dockerfile = (addon / "Dockerfile").read_text()
        self.assertNotIn("COPY payload", dockerfile)
        self.assertNotIn("github_token", dockerfile)
        self.assertNotIn("COPY . ", dockerfile)


class EntrypointTests(unittest.TestCase):
    def setUp(self):
        environment = patch.dict(os.environ, {"SUPERVISOR_TOKEN": "supervisor_fixture"})
        environment.start()
        self.addCleanup(environment.stop)

    def test_missing_pat_leaves_config_untouched_and_never_calls_installer(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            options = root / "options.json"
            options.write_text('{"github_token":""}')
            output = io.StringIO()
            with patch("sys.argv", ["installer", "--options", str(options), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(output):
                self.assertEqual(cli.main(), 1)
            installer.assert_not_called()
            self.assertIn("Set your own GitHub PAT", output.getvalue())
            self.assertEqual([p.name for p in root.iterdir()], ["options.json"])

    def test_verified_download_is_used_then_temporary_files_are_removed(self):
        def prepare(token, plan, temporary):
            self.assertEqual(token, TOKEN)
            self.temporary = temporary
            payload = temporary / "payload"
            payload.mkdir()
            release = temporary / "release.json"
            release.write_text('{}')
            return payload, release

        with tempfile.TemporaryDirectory() as name:
            options = Path(name) / "options.json"
            options.write_text(json.dumps({"github_token": TOKEN}))
            output = io.StringIO()
            with patch("sys.argv", ["installer", "--options", str(options), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "prepare_private_release", side_effect=prepare), patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(output):
                installer.return_value.run.return_value = "unchanged"
                self.assertEqual(cli.main(), 0)
            args = installer.call_args.args
            self.assertEqual(args[1], self.temporary / "payload")
            self.assertNotIn(TOKEN, repr(args))
            self.assertFalse(self.temporary.exists())
            self.assertNotIn(TOKEN, output.getvalue())
            self.assertIn("READY: unchanged", output.getvalue())

    def test_manual_rollback_works_without_pat_or_network(self):
        with tempfile.TemporaryDirectory() as name:
            options = Path(name) / "options.json"
            options.write_text(json.dumps({"rollback_to": "a" * 32}))
            with patch("sys.argv", ["installer", "--options", str(options), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "prepare_private_release") as prepare, patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(io.StringIO()):
                installer.return_value.run.return_value = "rolled_back"
                self.assertEqual(cli.main(), 0)
            prepare.assert_not_called()

    def test_pending_transaction_recovers_without_pat_or_network(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            options = root / "options.json"
            options.write_text('{}')
            (root / ".velnio-installer").mkdir()
            (root / ".velnio-installer/journal.json").write_text('{}')
            with patch("sys.argv", ["installer", "--config-root", str(root), "--options", str(options), "--once"]), patch.object(cli.signal, "signal"), patch.object(cli, "prepare_private_release") as prepare, patch.object(cli, "Installer") as installer, contextlib.redirect_stdout(io.StringIO()):
                installer.return_value.run.return_value = "recovered"
                self.assertEqual(cli.main(), 0)
            prepare.assert_not_called()
            self.assertTrue(installer.return_value.run.call_args.kwargs["recover_only"])

    def test_recovery_mode_never_deploys_or_requires_a_payload(self):
        from velnio_installer.runtime.installer import Installer, Options
        with tempfile.TemporaryDirectory() as name:
            root = Path(name).resolve()
            installer = Installer(root, root / "absent", root / "absent.json",
                                  unittest.mock.Mock(product=cli.get_product("velnio")),
                                  Options(product="velnio"), product="velnio")
            with patch.object(installer, "recover") as recover, patch.object(installer, "deploy") as deploy:
                self.assertEqual(installer.run(recover_only=True), "recovered")
                recover.assert_called_once_with(None)
                deploy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
