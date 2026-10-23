"""Durable file transactions. All live replacement operations are atomic on Linux."""

import ctypes
import fcntl
import hashlib
import json
import os
import platform
import re
import shutil
import stat
import uuid
from dataclasses import dataclass
from pathlib import Path

from .catalog import PRODUCTS, get_product
from .supervisor import SupervisorError


class InstallerError(RuntimeError):
    """Installation was refused or failed; state is retained for recovery."""


class NewerIntegrationInstalled(InstallerError):
    """A verified newer installation must be preserved; the App may remain idle."""

    def __init__(self, installed_version, bundled_version):
        self.installed_version = installed_version
        self.bundled_version = bundled_version
        super().__init__(
            f"Installed integration {installed_version} is newer than bundled "
            f"{bundled_version}; automatic downgrade refused; use rollback_to "
            "only for an intentional restore"
        )


def version(value):
    if not isinstance(value, str) or not re.fullmatch(
        r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value
    ):
        raise InstallerError("Expected stable X.Y.Z version")
    return tuple(int(part) for part in value.split("."))


def safe_directory(path, create=False):
    path = Path(os.path.abspath(path))
    for parent in (*reversed(path.parents), path):
        if not parent.exists() and not parent.is_symlink() and create:
            parent.mkdir()
            sync_dir(parent.parent)
        if not stat.S_ISDIR(parent.lstat().st_mode):
            raise InstallerError(
                f"Directory must be real, without symlink parents: {parent}"
            )
    return path


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def read_file(path):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise InstallerError(f"Not a regular file: {path}")
        with os.fdopen(fd, "rb", closefd=False) as file:
            return file.read()
    finally:
        os.close(fd)


def read_json(path):
    try:
        return json.loads(read_file(path))
    except (ValueError, OSError):
        raise InstallerError(
            f"Cannot read valid state or release JSON: {path}"
        ) from None


def atomic_json(path, data):
    if path.exists() or path.is_symlink():
        read_file(path)  # Refuse links and special files before replacement.
    temporary = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as file:
        json.dump(data, file, sort_keys=True)
        file.flush()
        os.fsync(file.fileno())
    os.replace(temporary, path)
    sync_dir(path.parent)


def file_map(path, ignore_cache=False, check_syntax=False):
    safe_directory(path)
    result = {}
    for directory, dirs, files in os.walk(path, followlinks=False):
        directory = Path(directory)
        for name in list(dirs):
            child = directory / name
            if child.is_symlink() or not child.is_dir():
                raise InstallerError(f"Unsafe directory in tree: {child}")
            if name == "__pycache__":
                if ignore_cache:
                    dirs.remove(name)
                elif check_syntax:
                    raise InstallerError(
                        "Payload must not contain __pycache__ directories"
                    )
        for name in files:
            child = directory / name
            data = read_file(child)
            if check_syntax and child.suffix == ".py":
                try:
                    compile(data, str(child), "exec", dont_inherit=True)
                except (SyntaxError, ValueError):
                    raise InstallerError(f"Invalid Python syntax: {child}") from None
            result[child.relative_to(path).as_posix()] = hashlib.sha256(
                data
            ).hexdigest()
    return result


def validate_map(files):
    if not isinstance(files, dict) or not {"__init__.py", "manifest.json"}.issubset(
        files
    ):
        raise InstallerError(
            "File manifest must include integration entrypoint and manifest"
        )
    for name, digest in files.items():
        if (
            not isinstance(name, str)
            or not name
            or name.startswith("/")
            or "\\" in name
            or any(part in ("", ".", "..", "__pycache__") for part in name.split("/"))
            or not isinstance(digest, str)
            or not re.fullmatch("[a-f0-9]{64}", digest)
        ):
            raise InstallerError("Unsafe path or digest in file manifest")


def inspect_tree(path, product="r4sls08"):
    product = get_product(product)
    files = file_map(path, ignore_cache=True, check_syntax=True)
    validate_map(files)
    manifest = read_json(path / "manifest.json")
    if not isinstance(manifest, dict) or manifest.get("domain") != product.domain:
        raise InstallerError(f"Integration manifest must have domain {product.domain}")
    version(manifest.get("version"))
    return {"files": files, "version": manifest["version"]}


def validate_release(payload, release_path, product="r4sls08"):
    product = get_product(product)
    safe_directory(Path(release_path).parent)
    release = read_json(release_path)
    if (
        not isinstance(release, dict)
        or type(release.get("schema")) is not int
        or release["schema"] != (1 if product.id == "r4sls08" else 2)
    ):
        raise InstallerError("Unsupported release schema")
    if product.id == "velnio":
        validate_velnio_release(release)
    version(release.get("app_version"))
    version(release.get("integration_version"))
    if not isinstance(release.get("source_commit"), str) or not re.fullmatch(
        "[a-f0-9]{40}", release["source_commit"]
    ):
        raise InstallerError(
            "Release source_commit must be a full immutable Git commit"
        )
    validate_map(release.get("files"))
    actual = file_map(payload, check_syntax=True)
    info = inspect_tree(payload, product)
    if actual != release["files"] or info["version"] != release["integration_version"]:
        raise InstallerError("Payload does not match the immutable release manifest")
    return info, release_fingerprint(release)


def release_fingerprint(release):
    return hashlib.sha256(json.dumps(release, sort_keys=True).encode()).hexdigest()


def validate_velnio_release(release):
    if release.get("product") != "velnio" or release.get("domain") != "velnio":
        raise InstallerError("Release product/domain mismatch")
    artifact = release.get("artifact")
    if (
        not isinstance(artifact, dict)
        or set(artifact) != {"archive_sha256", "companion_sha256"}
        or any(
            not isinstance(value, str) or not re.fullmatch("[a-f0-9]{64}", value)
            for value in artifact.values()
        )
    ):
        raise InstallerError("Invalid package provenance")
    compatibility = release.get("compatibility")
    if not isinstance(compatibility, dict) or set(compatibility) != {
        "inventory_schemas",
        "config_entry_versions",
    }:
        raise InstallerError("Missing explicit compatibility evidence")
    for values in compatibility.values():
        if (
            not isinstance(values, list)
            or not values
            or any(type(v) is not int or v < 1 for v in values)
            or len(set(values)) != len(values)
        ):
            raise InstallerError("Invalid compatibility evidence")
    validate_map(release.get("files"))


def copy_verified(source, destination, expected=None):
    before = file_map(source)
    if expected is not None and before != expected:
        raise InstallerError("Source tree no longer matches its verified manifest")
    shutil.copytree(source, destination, symlinks=True)
    after = file_map(destination)
    if before != after or before != file_map(source):
        raise InstallerError("Copied tree failed verification")
    for directory, _, files in os.walk(destination, topdown=False):
        for name in files:
            fd = os.open(Path(directory) / name, os.O_RDONLY | os.O_NOFOLLOW)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        sync_dir(directory)
    sync_dir(destination.parent)
    return after


def rename_atomic(source, destination, exchange=False):
    # Linux renameat2 RENAME_NOREPLACE also protects first-install absence.
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    args = (
        ctypes.c_int(-100),
        ctypes.c_char_p(os.fsencode(source)),
        ctypes.c_int(-100),
        ctypes.c_char_p(os.fsencode(destination)),
        ctypes.c_uint(2 if exchange else 1),
    )
    if renameat2 is not None:
        renameat2.restype = ctypes.c_int
        result = renameat2(*args)
    else:
        # Alpine musl does not export renameat2. Use the Linux syscall ABI for
        # the two supported release architectures, never a non-atomic fallback.
        number = {"x86_64": 316, "aarch64": 276}.get(platform.machine())
        if platform.system() != "Linux" or number is None:
            raise InstallerError("Linux renameat2 atomic replacement is unavailable")
        libc.syscall.restype = ctypes.c_long
        result = libc.syscall(ctypes.c_long(number), *args)
    if result != 0:
        errno = ctypes.get_errno()
        raise InstallerError(
            f"Atomic renameat2 failed (errno={errno}); live tree preserved"
        )
    sync_dir(source.parent)
    sync_dir(destination.parent)


@dataclass(frozen=True)
class Options:
    rollback_to: str = ""
    retry_failed_release: bool = False
    backup_count: int = 5
    health_timeout: float = 180
    product: str = "r4sls08"

    def __post_init__(self):
        try:
            get_product(self.product)
        except ValueError as error:
            raise InstallerError(str(error)) from None
        if not isinstance(self.rollback_to, str) or (
            self.rollback_to and not re.fullmatch("[a-f0-9]{32}", self.rollback_to)
        ):
            raise InstallerError("rollback_to must be a known backup ID")
        if type(self.retry_failed_release) is not bool:
            raise InstallerError("retry_failed_release must be boolean")
        if type(self.backup_count) is not int or not 1 <= self.backup_count <= 100:
            raise InstallerError("backup_count must be between 1 and 100")
        if (
            type(self.health_timeout) not in (int, float)
            or not 0 < self.health_timeout <= 3600
        ):
            raise InstallerError(
                "health_timeout must be greater than zero and at most 3600"
            )

    @classmethod
    def load(cls, path):
        data = read_json(Path(path))
        if not isinstance(data, dict) or set(data) - set(cls.__dataclass_fields__):
            raise InstallerError("Invalid installer options")
        return cls(**data)


class Installer:
    def __init__(
        self, config_root, payload, release, supervisor, options=None, product=None
    ):
        self.config = Path(config_root)
        self.payload = Path(payload)
        self.release = Path(release)
        self.supervisor = supervisor
        self.options = options or Options()
        try:
            self.product = get_product(
                self.options.product if product is None else product
            )
        except ValueError as error:
            raise InstallerError(str(error)) from None
        if hasattr(supervisor, "product") and supervisor.product != self.product:
            raise InstallerError("Supervisor product does not match installer product")
        self.coordinator = self.config / PRODUCTS["r4sls08"].state_dir
        self.state = self.config / self.product.state_dir
        self.backups = self.state / "backups"
        self.transactions = self.state / "transactions"
        self.target = self.config / "custom_components" / self.product.domain
        self.journal = self.state / "journal.json"
        self.history = self.state / "history.json"

    def run(self, acknowledge_rollback_restart=None, recover_only=False):
        try:
            safe_directory(self.config)
            safe_directory(self.coordinator, create=True)
            lock = os.open(
                self.coordinator / "lock",
                os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK,
                0o600,
            )
            try:
                if not stat.S_ISREG(os.fstat(lock).st_mode):
                    raise InstallerError("Installer lock is not a regular file")
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise InstallerError(
                        "Another installer holds the process lock"
                    ) from None
                self.reject_foreign_journals()
                safe_directory(self.state, create=True)
                safe_directory(self.target.parent, create=True)
                safe_directory(self.backups, create=True)
                safe_directory(self.transactions, create=True)
                self.recover(acknowledge_rollback_restart)
                if acknowledge_rollback_restart or recover_only:
                    return "recovered"
                return self.deploy()
            finally:
                os.close(lock)
        except SupervisorError as error:
            raise InstallerError(str(error)) from None
        except (OSError, ValueError, TypeError, KeyError) as error:
            raise InstallerError(f"Installer failed: {type(error).__name__}") from None

    def reject_foreign_journals(self):
        # The historical lock also coordinates updated products with old R4 processes.
        # Old binaries do not inspect foreign durable journals; adoption must stop them.
        for state in self.config.iterdir():
            if (
                not state.name.startswith(".")
                or not state.name.endswith("-installer")
                or state == self.state
            ):
                continue
            if state.is_symlink():
                raise InstallerError("Foreign installer state must not be a symlink")
            journal = state / "journal.json"
            if journal.exists() or journal.is_symlink():
                raise InstallerError(
                    "Foreign product has an unresolved recovery journal"
                )

    def validate_release_evidence(self, evidence, info):
        if not isinstance(evidence, dict) or set(evidence) != {
            "manifest",
            "fingerprint",
        }:
            raise InstallerError("Rollback lacks compatible release evidence")
        manifest = evidence["manifest"]
        if not isinstance(manifest, dict) or manifest.get("schema") != 2:
            raise InstallerError("Invalid rollback compatibility evidence")
        validate_velnio_release(manifest)
        version(manifest.get("app_version"))
        version(manifest.get("integration_version"))
        if not isinstance(manifest.get("source_commit"), str) or not re.fullmatch(
            "[a-f0-9]{40}", manifest["source_commit"]
        ):
            raise InstallerError("Invalid rollback source evidence")
        validate_map(manifest.get("files"))
        if (
            manifest["files"] != info["files"]
            or manifest["integration_version"] != info["version"]
            or release_fingerprint(manifest) != evidence["fingerprint"]
        ):
            raise InstallerError(
                "Rollback evidence does not match verified tree fingerprint"
            )
        return evidence

    def rollback_release(self, backup_id, info):
        data = read_json(self.backups / backup_id / "backup.json")
        return self.validate_release_evidence(data.get("release"), info)

    def check_storage_compatibility(self, compatibility):
        storage = self.config / ".storage"
        if not storage.exists() and not storage.is_symlink():
            return
        safe_directory(storage)

        def bounded_json(name):
            path = storage / name
            if not path.exists() and not path.is_symlink():
                return None
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
            try:
                if not stat.S_ISREG(os.fstat(fd).st_mode):
                    raise InstallerError("HA storage must be a regular file")
                with os.fdopen(fd, "rb", closefd=False) as source:
                    content = source.read(8 * 1024 * 1024 + 1)
                if len(content) > 8 * 1024 * 1024:
                    raise InstallerError(
                        "HA storage exceeds bounded compatibility inspection"
                    )
                value = json.loads(content)
                if not isinstance(value, dict):
                    raise InstallerError("Invalid HA storage compatibility data")
                return value
            finally:
                os.close(fd)

        inventory = bounded_json("velnio_inventory.json")
        if inventory is not None and (
            type(inventory.get("version")) is not int
            or inventory["version"] not in compatibility["inventory_schemas"]
        ):
            raise InstallerError("Candidate incompatible with inventory schema")
        registry = bounded_json("core.config_entries")
        if registry is not None:
            data = registry.get("data")
            if not isinstance(data, dict) or not isinstance(data.get("entries"), list):
                raise InstallerError("Invalid config-entry compatibility data")
            for entry in data["entries"]:
                if not isinstance(entry, dict):
                    raise InstallerError("Invalid config-entry compatibility data")
                if entry.get("domain") == "velnio" and (
                    type(entry.get("version")) is not int
                    or entry["version"] not in compatibility["config_entry_versions"]
                ):
                    raise InstallerError(
                        "Candidate incompatible with config-entry version"
                    )

    def current(self):
        if not self.target.exists() and not self.target.is_symlink():
            return None
        return inspect_tree(self.target, self.product)

    def history_data(self):
        if not self.history.exists() and not self.history.is_symlink():
            return {"failed": []}
        data = read_json(self.history)
        if not isinstance(data, dict) or not isinstance(data.get("failed"), list):
            raise InstallerError(
                "Invalid installer history; preserve state for inspection"
            )
        return data

    def backup_info(self, backup_id):
        if not isinstance(backup_id, str) or not re.fullmatch(
            "[a-f0-9]{32}", backup_id
        ):
            raise InstallerError("Invalid backup ID")
        root = self.backups / backup_id
        safe_directory(root)
        data = read_json(root / "backup.json")
        if (
            not isinstance(data, dict)
            or data.get("schema") != (1 if self.product.id == "r4sls08" else 2)
            or (
                self.product.id == "velnio"
                and (data.get("product") != "velnio" or data.get("domain") != "velnio")
            )
            or not isinstance(data.get("full_files"), dict)
        ):
            raise InstallerError("Invalid backup metadata")
        actual = inspect_tree(root / "tree", self.product)
        if actual != data.get("tree") or file_map(root / "tree") != data["full_files"]:
            raise InstallerError("Backup verification failed; recovery files preserved")
        return root / "tree", actual, data["full_files"]

    def create_backup(self, old):
        backup_id = uuid.uuid4().hex
        root = self.backups / backup_id
        root.mkdir(mode=0o700)
        full = copy_verified(self.target, root / "tree")
        if inspect_tree(root / "tree", self.product) != old:
            raise InstallerError("Live tree changed while backing up")
        metadata = {"schema": 1, "tree": old, "full_files": full}
        if self.product.id == "velnio":
            success = self.history_data().get("last_success", {})
            if not isinstance(success, dict):
                raise InstallerError("Invalid release history evidence")
            evidence = success.get("release") if success.get("tree") == old else None
            metadata.update(
                schema=2, product="velnio", domain="velnio", release=evidence
            )
        atomic_json(root / "backup.json", metadata)
        sync_dir(self.backups)
        return backup_id

    def deploy(self):
        history = self.history_data()
        if self.options.rollback_to:
            source, new, _ = self.backup_info(self.options.rollback_to)
            release_id = "rollback:" + self.options.rollback_to
            selected_release = (
                self.rollback_release(self.options.rollback_to, new)
                if self.product.id == "velnio"
                else None
            )
            if selected_release is not None:
                self.check_storage_compatibility(
                    selected_release["manifest"]["compatibility"]
                )
        else:
            source = self.payload
            new, release_id = validate_release(self.payload, self.release, self.product)
            selected_release = (
                {"manifest": read_json(self.release), "fingerprint": release_id}
                if self.product.id == "velnio"
                else None
            )
            if (
                selected_release is not None
                and release_fingerprint(selected_release["manifest"]) != release_id
            ):
                raise InstallerError("Release changed during verification")
        old = self.current()
        if old == new:
            return "unchanged"
        if (
            not self.options.rollback_to
            and old
            and version(new["version"]) < version(old["version"])
        ):
            raise NewerIntegrationInstalled(old["version"], new["version"])
        if selected_release is not None and not self.options.rollback_to:
            self.check_storage_compatibility(
                selected_release["manifest"]["compatibility"]
            )
        if release_id in history["failed"] and not self.options.retry_failed_release:
            raise InstallerError(
                "Release previously failed; inspect logs then enable retry_failed_release"
            )
        self.supervisor.running()
        self.supervisor.check()
        expected = self.supervisor.loaded_entries()
        backup_id = self.create_backup(old) if old else None
        transaction_id = uuid.uuid4().hex
        transaction = self.transactions / transaction_id
        transaction.mkdir(mode=0o700)
        stage = transaction / "new"
        copy_verified(source, stage)
        if inspect_tree(stage, self.product) != new or self.current() != old:
            raise InstallerError("Source or live integration changed during staging")
        if os.stat(stage).st_dev != os.stat(self.target.parent).st_dev:
            raise InstallerError("Staging and live integration must share a filesystem")
        journal = {
            "schema": 1,
            "id": transaction_id,
            "phase": "prepared",
            "old": old,
            "new": new,
            "backup_id": backup_id,
            "expected_entries": expected,
            "release_id": release_id,
            "rollback_to": self.options.rollback_to,
            "rollback_restart": None,
        }
        if self.product.id == "velnio":
            journal.update(
                schema=2, product="velnio", domain="velnio", release=selected_release
            )
        sync_dir(self.transactions)
        atomic_json(self.journal, journal)
        try:
            rename_atomic(stage, self.target, exchange=old is not None)
            journal["phase"] = "swapped"
            atomic_json(self.journal, journal)
            if self.current() != new:
                raise InstallerError("Installed tree verification failed")
            self.supervisor.check()
            journal["phase"] = "restart_intent"
            atomic_json(self.journal, journal)
            self.supervisor.restart()
            self.supervisor.wait_healthy(expected, self.options.health_timeout)
            if self.current() != new:
                raise InstallerError(
                    "External target change during health verification; preserve all trees"
                )
            journal["phase"] = "completed"
            atomic_json(self.journal, journal)
        except (Exception, KeyboardInterrupt) as error:  # noqa: BLE001 - rollback every transaction failure
            # Once journal exists, even ambiguous mutations use fingerprint recovery.
            try:
                self.recover()
            except Exception as recovery_error:  # noqa: BLE001 - retain journal on any recovery error
                raise InstallerError(
                    f"Deployment failed; recovery needs attention: {recovery_error}"
                ) from None
            raise InstallerError(
                f"Deployment failed and original tree restored: {type(error).__name__}"
            ) from None
        self.finish_success(journal)
        return "rolled_back" if self.options.rollback_to else "installed"

    def load_journal(self):
        journal = read_json(self.journal)
        if (
            not isinstance(journal, dict)
            or journal.get("schema") != (1 if self.product.id == "r4sls08" else 2)
            or (
                self.product.id == "velnio"
                and (
                    journal.get("product") != "velnio"
                    or journal.get("domain") != "velnio"
                )
            )
            or not isinstance(journal.get("id"), str)
            or not re.fullmatch("[a-f0-9]{32}", journal["id"])
            or journal.get("phase")
            not in ("prepared", "swapped", "restart_intent", "completed")
            or not isinstance(journal.get("expected_entries"), list)
            or not all(isinstance(v, str) and v for v in journal["expected_entries"])
            or not isinstance(journal.get("release_id"), str)
            or journal.get("rollback_restart") not in (None, "intent", "done")
        ):
            raise InstallerError("Invalid recovery journal; manual inspection required")
        for key in ("old", "new"):
            info = journal.get(key)
            if key == "old" and info is None:
                continue
            if not isinstance(info, dict) or set(info) != {"files", "version"}:
                raise InstallerError("Invalid recovery tree manifest")
            validate_map(info["files"])
            version(info["version"])
        if self.product.id == "velnio":
            self.validate_release_evidence(journal.get("release"), journal["new"])
        if journal["old"] is not None:
            _, backed_up, _ = self.backup_info(journal.get("backup_id"))
            if backed_up != journal["old"]:
                raise InstallerError("Journal and verified backup disagree")
        return journal

    def recover(self, acknowledge_rollback_restart=None):
        if not self.journal.exists() and not self.journal.is_symlink():
            if acknowledge_rollback_restart:
                raise InstallerError("No pending recovery journal to acknowledge")
            return
        journal = self.load_journal()
        if acknowledge_rollback_restart and (
            acknowledge_rollback_restart != journal["id"]
            or journal["phase"] != "restart_intent"
            or journal["rollback_restart"] != "intent"
        ):
            raise InstallerError(
                "Acknowledgement must name the pending ambiguous rollback transaction"
            )
        current = self.current()
        if journal["phase"] == "completed":
            if current != journal["new"]:
                raise InstallerError(
                    "External target change after completion; all trees preserved"
                )
            self.finish_success(journal)
            return
        if current != journal["old"] and current != journal["new"]:
            raise InstallerError(
                "External target change during recovery; all trees preserved; inspect journal and backups"
            )
        if (
            self.product.id == "velnio"
            and journal["phase"] == "restart_intent"
            and journal["old"] is not None
        ):
            # Core may already have migrated durable data, even if restart failed.
            # Check before restoring code, retrying a restart, or accepting an ack.
            try:
                original = self.rollback_release(journal["backup_id"], journal["old"])
                compatibility = original["manifest"]["compatibility"]
                candidate = journal["release"]["manifest"]["compatibility"]
                # Candidate startup may still persist migrations after a timeout.
                # Qualified declarations must cover schemas read and written.
                if any(
                    not set(values).issubset(compatibility[name])
                    for name, values in candidate.items()
                ):
                    raise InstallerError(
                        "Original release incompatible with pending candidate schemas"
                    )
                self.check_storage_compatibility(compatibility)
            except InstallerError as error:
                raise InstallerError(
                    "Post-restart recovery requires manual intervention; "
                    f"all trees and journal preserved: {error}"
                ) from None
        history = self.history_data()
        if journal["release_id"] not in history["failed"]:
            history["failed"].append(journal["release_id"])
            atomic_json(self.history, history)
        if current == journal["new"]:
            transaction = self.transactions / journal["id"]
            safe_directory(transaction)
            if journal["old"] is None:
                # Preserve failed first installation outside custom_components.
                rename_atomic(
                    self.target, transaction / ("removed-" + uuid.uuid4().hex)
                )
            else:
                source, _, full = self.backup_info(journal["backup_id"])
                restoration = transaction / ("restore-" + uuid.uuid4().hex)
                copy_verified(source, restoration, full)
                if self.current() != journal["new"]:
                    raise InstallerError(
                        "External target change before restore; all trees preserved"
                    )
                rename_atomic(restoration, self.target, exchange=True)
                if file_map(self.target) != full:
                    raise InstallerError(
                        "Restored tree failed full backup verification"
                    )
        if self.current() != journal["old"]:
            raise InstallerError("Original tree restoration verification failed")
        if journal["phase"] == "restart_intent":
            if journal["rollback_restart"] == "intent":
                if not acknowledge_rollback_restart:
                    raise InstallerError(
                        "Rollback restart outcome unknown; manually restart Core, then run "
                        f"python -m runtime --once --product {self.product.id} "
                        "--acknowledge-rollback-restart "
                        + journal["id"]
                    )
                self.supervisor.wait_healthy(
                    journal["expected_entries"], self.options.health_timeout
                )
                journal["rollback_restart"] = "done"
                atomic_json(self.journal, journal)
            if journal["rollback_restart"] is None:
                journal["rollback_restart"] = "intent"
                atomic_json(self.journal, journal)
                self.supervisor.restart()
                journal["rollback_restart"] = "done"
                atomic_json(self.journal, journal)
            self.supervisor.wait_healthy(
                journal["expected_entries"], self.options.health_timeout
            )
        self.clear_journal(journal)

    def clear_journal(self, journal):
        self.journal.unlink()
        sync_dir(self.state)
        transaction = self.transactions / journal["id"]
        if transaction.exists():
            safe_directory(transaction)
            shutil.rmtree(transaction)
            sync_dir(self.transactions)

    def finish_success(self, journal):
        history = self.history_data()
        history["last_success"] = {
            "release_id": journal["release_id"],
            "rollback_to": journal["rollback_to"],
            "tree": journal["new"],
        }
        if self.product.id == "velnio":
            history["last_success"]["release"] = journal["release"]
        history["failed"] = [
            value for value in history["failed"] if value != journal["release_id"]
        ]
        atomic_json(self.history, history)
        self.clear_journal(journal)
        self.prune_backups()

    def prune_backups(self):
        verified = []
        for root in self.backups.iterdir():
            try:
                _, info, _ = self.backup_info(root.name)
                if self.product.id == "velnio":
                    self.rollback_release(root.name, info)
            except (InstallerError, OSError):
                continue  # Never delete unverified/foreign content.
            verified.append(root)
        verified.sort(key=lambda root: root.stat().st_mtime_ns, reverse=True)
        keep = {root.name for root in verified[: self.options.backup_count]}
        keep.add(self.options.rollback_to)
        for root in verified:
            if root.name not in keep:
                shutil.rmtree(root)
        sync_dir(self.backups)
