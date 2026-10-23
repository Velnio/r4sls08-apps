"""Install the verified payload bundled in the private GHCR image.

Registry authentication belongs to Supervisor, never to this runtime.
"""
import argparse
import os
import signal
import threading
from pathlib import Path

from .catalog import get_product
from .installer import Installer, InstallerError, NewerIntegrationInstalled, Options, read_json
from .supervisor import Supervisor, SupervisorError


def load_options(path):
    data = read_json(path)
    allowed = set(Options.__dataclass_fields__) | {"github_token"}
    if not isinstance(data, dict) or set(data) - allowed:
        raise InstallerError("Invalid installer options")
    data = dict(data)
    # Supervisor can retain obsolete option keys across upgrades from 1.0.20.
    # Discard the legacy value without logging or forwarding it.
    data.pop("github_token", None)
    data.setdefault("product", "velnio")
    options = Options(**data)
    if options.product != "velnio":
        raise InstallerError("This Installer only installs the Velnio integration")
    return options


def main():
    parser = argparse.ArgumentParser(description="Private Velnio integration installer")
    parser.add_argument("--config-root", type=Path, default=Path("/config"))
    parser.add_argument("--options", type=Path, default=Path("/data/options.json"))
    parser.add_argument("--payload", type=Path)
    parser.add_argument("--release", type=Path)
    parser.add_argument("--supervisor-url", default="http://supervisor")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--acknowledge-rollback-restart", metavar="TRANSACTION_ID")
    args = parser.parse_args()
    stopping = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda signum, frame: stopping.set())
    product = get_product("velnio")
    try:
        options = load_options(args.options)
        supervisor = Supervisor(
            args.supervisor_url, os.environ.get("SUPERVISOR_TOKEN", ""),
            command_timeout=options.health_timeout,
            restart_timeout=max(600, options.health_timeout), product=product,
        )
        journal = args.config_root / product.state_dir / "journal.json"
        recover_only = (not options.rollback_to and not args.acknowledge_rollback_restart
                        and (journal.exists() or journal.is_symlink()))
        result = Installer(
            args.config_root, args.payload or Path(product.payload_path),
            args.release or Path(product.release_path), supervisor, options, product=product,
        ).run(acknowledge_rollback_restart=args.acknowledge_rollback_restart,
              recover_only=recover_only)
    except NewerIntegrationInstalled as error:
        result = "newer_installed"
        print(f"VELNIO_INSTALLER_SKIPPED: installed={error.installed_version} "
              f"release={error.bundled_version}; keeping the newer integration", flush=True)
    except (InstallerError, SupervisorError) as error:
        print(f"VELNIO_INSTALLER_FAILED: {error}", flush=True)
        return 1
    except (OSError, ValueError, TypeError):
        print("VELNIO_INSTALLER_FAILED: invalid configuration or local I/O failure", flush=True)
        return 1
    print(f"VELNIO_INSTALLER_READY: {result}", flush=True)
    if not args.once:
        stopping.wait()
    print("VELNIO_INSTALLER_STOPPED", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
