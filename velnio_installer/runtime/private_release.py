"""Fetch a pinned private release without storing or forwarding the user's PAT."""

import hashlib
import io
import json
import re
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

from .installer import InstallerError, read_json, validate_release

API = "https://api.github.com"
ASSET_HOSTS = {"release-assets.githubusercontent.com", "objects.githubusercontent.com"}
MAX_ARCHIVE = 8 * 1024 * 1024
MAX_EXPANDED = 32 * 1024 * 1024
MAX_FILE = 4 * 1024 * 1024
MAX_JSON = 512 * 1024


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_bytes(url, token, accept, limit, deadline):
    """Only the fixed GitHub API receives Authorization, never the asset CDN."""
    opener = urllib.request.build_opener(NoRedirect())
    for _ in range(3):
        try:
            parsed = urllib.parse.urlsplit(url)
            port = parsed.port
        except ValueError:
            raise InstallerError("GitHub returned an invalid download location") from None
        if (parsed.scheme != "https" or parsed.username or parsed.password
                or port not in (None, 443)
                or parsed.hostname not in ({"api.github.com"} | ASSET_HOSTS)):
            raise InstallerError("GitHub returned an untrusted download location")
        headers = {"Accept": accept, "User-Agent": "Velnio-Installer/1.0.20"}
        if parsed.hostname == "api.github.com":
            headers["Authorization"] = "Bearer " + token
            headers["X-GitHub-Api-Version"] = "2022-11-28"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise InstallerError("Private release download timed out")
        try:
            response = opener.open(urllib.request.Request(url, headers=headers),
                                   timeout=min(20, remaining))
        except urllib.error.HTTPError as error:
            if error.code in (301, 302, 303, 307, 308):
                location = error.headers.get("Location", "")
                error.close()
                target = urllib.parse.urljoin(url, location)
                if urllib.parse.urlsplit(target).hostname not in ASSET_HOSTS:
                    raise InstallerError("GitHub returned an untrusted asset redirect") from None
                url = target
                continue
            code = error.code
            error.close()
            raise InstallerError(
                f"Private GitHub release request failed (HTTP {code}); "
                "check the PAT, repository access and release availability"
            ) from None
        except (OSError, ValueError, urllib.error.URLError):
            raise InstallerError("Cannot connect securely to the private GitHub release") from None
        try:
            with response:
                if response.status != 200:
                    raise InstallerError("Unexpected private release response")
                data = bytearray()
                while True:
                    if time.monotonic() >= deadline:
                        raise InstallerError("Private release download timed out")
                    block = response.read(min(65536, limit + 1 - len(data)))
                    if not block:
                        return bytes(data)
                    data.extend(block)
                    if len(data) > limit:
                        raise InstallerError("Private release download exceeds its size limit")
        except (OSError, ValueError):
            raise InstallerError("Private release download was interrupted") from None
    raise InstallerError("Too many private release redirects")


def unpack_archive(data, destination):
    """Validate every ZIP member before extracting only the integration tree."""
    prefix = "custom_components/velnio/"
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if len(members) > 256 or sum(m.file_size for m in members) > MAX_EXPANDED:
                raise InstallerError("Private release archive is too large")
            seen = set()
            for member in members:
                name = member.filename
                path = PurePosixPath(name)
                mode = member.external_attr >> 16
                if (name in seen or path.is_absolute() or ".." in path.parts
                        or "\\" in name or "\x00" in name
                        or path.as_posix() != name.rstrip("/")
                        or member.flag_bits & 1 or member.file_size > MAX_FILE
                        or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                    raise InstallerError("Unsafe member in private release archive")
                seen.add(name)
            for member in members:
                if member.is_dir() or not member.filename.startswith(prefix):
                    continue
                relative = member.filename[len(prefix):]
                if not relative:
                    raise InstallerError("Invalid integration archive member")
                target = destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as output:
                    output.write(archive.read(member))
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError):
        raise InstallerError("Cannot unpack the verified private release archive") from None


def prepare_private_release(token, plan_path, temporary):
    if (not isinstance(token, str) or not 10 <= len(token) <= 512
            or not re.fullmatch(r"[A-Za-z0-9_]+", token)):
        raise InstallerError("Set your own GitHub PAT in the github_token option")
    plan = read_json(Path(plan_path))
    if (not isinstance(plan, dict) or plan.get("schema") != 1 or plan.get("repository") != "Velnio/velnio-ha"
            or not re.fullmatch(r"velnio-\d+\.\d+\.\d+", plan.get("tag", ""))):
        raise InstallerError("Invalid pinned private release identity")
    assets = plan.get("assets")
    if not isinstance(assets, dict) or set(assets) != {"archive", "manifest"}:
        raise InstallerError("Invalid pinned private release assets")
    for spec in assets.values():
        if (not isinstance(spec, dict) or set(spec) != {"name", "sha256"}
                or not isinstance(spec["name"], str)
                or not re.fullmatch(r"[A-Za-z0-9.-]+", spec["name"])
                or not isinstance(spec.get("sha256"), str)
                or not re.fullmatch(r"[a-f0-9]{64}", spec["sha256"])):
            raise InstallerError("Invalid pinned private release asset digest")
    deadline = time.monotonic() + 120
    endpoint = f"{API}/repos/{plan['repository']}/releases/tags/{plan['tag']}"
    raw = request_bytes(endpoint, token, "application/vnd.github+json", MAX_JSON, deadline)
    try:
        release = json.loads(raw)
    except ValueError:
        raise InstallerError("Private release metadata is not valid JSON") from None
    if (not isinstance(release, dict) or release.get("draft") is not False
            or release.get("tag_name") != plan["tag"]
            or not isinstance(release.get("assets"), list)):
        raise InstallerError("Private release metadata does not match the pinned release")
    downloaded = {}
    for kind, spec in assets.items():
        matches = [a for a in release["assets"]
                   if isinstance(a, dict) and a.get("name") == spec["name"]]
        if len(matches) != 1 or type(matches[0].get("id")) is not int or matches[0]["id"] <= 0:
            raise InstallerError("Pinned private release asset is missing or ambiguous")
        url = f"{API}/repos/{plan['repository']}/releases/assets/{matches[0]['id']}"
        data = request_bytes(url, token, "application/octet-stream",
                             MAX_ARCHIVE if kind == "archive" else MAX_JSON, deadline)
        if hashlib.sha256(data).hexdigest() != spec["sha256"]:
            raise InstallerError("Private release asset checksum mismatch; installation refused")
        downloaded[kind] = data
    payload = temporary / "payload"
    payload.mkdir(mode=0o700)
    unpack_archive(downloaded["archive"], payload)
    manifest_path = temporary / "release.json"
    manifest_path.write_bytes(downloaded["manifest"])
    manifest = read_json(manifest_path)
    if (not isinstance(manifest, dict) or manifest.get("integration_version") != plan.get("integration_version")
            or manifest.get("artifact", {}).get("archive_sha256") != assets["archive"]["sha256"]):
        raise InstallerError("Private release package provenance mismatch")
    validate_release(payload, manifest_path, "velnio")
    return payload, manifest_path
