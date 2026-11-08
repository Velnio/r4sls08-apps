import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SftpCatalogTests(unittest.TestCase):
    def test_qualified_release_matches_supervisor_catalog(self):
        config = json.loads((ROOT / "velnio_sftp/config.json").read_text())
        pins = json.loads((ROOT / "velnio_sftp/image-digests.json").read_text())
        self.assertEqual(config["version"], "0.1.4")
        self.assertEqual(config["version"], pins["installer_version"])
        self.assertEqual(config["image"], pins["image"])
        self.assertEqual(pins["visibility"], "private")
        self.assertEqual(set(config["arch"]), {"amd64", "aarch64"})
        self.assertEqual(set(pins["platforms"]), {"amd64", "arm64"})
        self.assertEqual(set(pins["configs"]), set(pins["platforms"]))
        self.assertEqual(pins["index_digest"], "sha256:3cb27c3be7a79a0d239f369b2c5d16d217c544d0c8cfe0c5ba936daf4ea4c743")
        for digest in [pins["index_digest"], *pins["platforms"].values(), *pins["configs"].values()]:
            self.assertRegex(digest, r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(pins["qualification"]["original_release_workflow_conclusion"], "failure")
        self.assertFalse(pins["qualification"]["original_release_artifact_uploaded"])
        self.assertFalse(pins["qualification"]["deployment_performed"])

    def test_public_update_preserves_manual_start_and_permissions(self):
        actual = json.loads((ROOT / "velnio_sftp/config.json").read_text())
        self.assertEqual(actual["startup"], "once")
        self.assertEqual(actual["privileged"], [])
        for permission in ("host_network", "docker_api", "full_access"):
            self.assertFalse(actual[permission])
        self.assertEqual(set(actual["options"]), {"operation", "restart_core", "health_timeout"})
        self.assertEqual(actual["boot"], "manual")
        self.assertEqual(actual["options"]["operation"], "status")
        self.assertFalse(actual["options"]["restart_core"])

    def test_public_sftp_entry_contains_metadata_only(self):
        allowed = {"config.json", "image-digests.json", "DOCS.md", "CHANGELOG.md", "icon.png", "logo.png"}
        self.assertEqual({p.name for p in (ROOT / "velnio_sftp").iterdir()}, allowed)


if __name__ == "__main__":
    unittest.main()
