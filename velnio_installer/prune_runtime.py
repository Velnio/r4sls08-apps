"""Prune three exact packages from the pinned, intentionally non-APK-serviceable rootfs.

This is not an APK dependency solver. Every expected version and owned file is
validated before mutation; unrelated package records and CA files are preserved.
"""
import stat
from pathlib import Path

EXPECTED = {
    "apk-tools": (b"3.0.6-r0", "/sbin/apk"),
    "libapk": (b"3.0.6-r0", "/usr/lib/libapk.so.3.0.0"),
    "ssl_client": (b"1.37.0-r30", "/usr/bin/ssl_client"),
}


def _regular(root, name):
    path = root / name.lstrip("/")
    for parent in path.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError(f"symlink ancestor is not accepted: {name}")
    try:
        if not stat.S_ISREG(path.lstat().st_mode):
            raise ValueError(f"expected regular file: {name}")
    except FileNotFoundError as error:
        raise ValueError(f"missing expected file: {name}") from error
    return path


def prune(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("root must be a real directory")
    root = root.resolve(strict=True)
    database = _regular(root, "/lib/apk/db/installed")
    world = _regular(root, "/etc/apk/world")
    records = database.read_bytes().split(b"\n\n")
    selected = {}
    kept = []
    for record in records:
        names = [line[2:] for line in record.splitlines() if line.startswith(b"P:")]
        if not record:
            kept.append(record)
            continue
        if len(names) != 1:
            raise ValueError("malformed package record")
        name = names[0].decode("ascii")
        if name not in EXPECTED:
            kept.append(record)
            continue
        if name in selected:
            raise ValueError("duplicate excluded package")
        version, owned = EXPECTED[name]
        versions = [line[2:] for line in record.splitlines() if line.startswith(b"V:")]
        directory = None
        files = []
        for line in record.splitlines():
            if line.startswith(b"F:"):
                directory = line[2:].decode("ascii")
            elif line.startswith(b"R:"):
                if directory is None:
                    raise ValueError("package file without a directory")
                files.append("/" + directory + "/" + line[2:].decode("ascii"))
        if versions != [version] or files != [owned]:
            raise ValueError(f"unexpected version or owned files: {name}")
        path = _regular(root, owned)
        with path.open("rb") as stream:
            magic = stream.read(4)
        if magic != b"\x7fELF":
            raise ValueError(f"expected ELF file: {owned}")
        selected[name] = path
    if set(selected) != set(EXPECTED):
        raise ValueError("all three exact excluded packages must be present")
    world_lines = world.read_bytes().splitlines(keepends=True)
    if sum(line.rstrip(b"\r\n") == b"apk-tools" for line in world_lines) != 1:
        raise ValueError("expected exactly one apk-tools world entry")
    replacement_world = b"".join(line for line in world_lines if line.rstrip(b"\r\n") != b"apk-tools")
    replacement_database = b"\n\n".join(kept)
    # Build-stage mutation begins only after every condition has passed.
    for path in selected.values():
        path.unlink()
    database.write_bytes(replacement_database)
    world.write_bytes(replacement_world)


if __name__ == "__main__":
    prune(Path("/"))
