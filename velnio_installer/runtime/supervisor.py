"""Bounded, sanitized Supervisor and Home Assistant HTTP boundary."""

import http.client
import json
import math
import signal
import threading
import time
import urllib.error
import urllib.request
from contextlib import contextmanager

from .catalog import get_product


class SupervisorError(RuntimeError):
    """Safe to display: never contains tokens, response bodies, or config data."""


@contextmanager
def request_deadline(timeout):
    """Interrupt synchronous HTTP, including drip-fed headers/body, on this CLI thread.

    No background worker may continue a restart after the caller has timed out.
    The standalone POSIX entrypoint owns this timer only for the request; embedded
    callers with a worker thread or an existing timer are refused before I/O.
    """
    if threading.current_thread() is not threading.main_thread():
        raise SupervisorError("Supervisor requests require the CLI main thread")
    if not math.isfinite(timeout) or timeout <= 0:
        raise SupervisorError("Supervisor request deadline must be positive and finite")
    if any(signal.getitimer(signal.ITIMER_REAL)):
        raise SupervisorError(
            "Supervisor request cannot replace an existing process timer"
        )
    deadline = time.monotonic() + timeout
    previous_handler = signal.getsignal(signal.SIGALRM)

    def expired(signum=None, frame=None):
        raise SupervisorError("Supervisor HTTP request exceeded its absolute deadline")

    signal.signal(signal.SIGALRM, expired)
    try:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            expired()
        signal.setitimer(signal.ITIMER_REAL, remaining)
        yield
        # Reject a late result even if signal dispatch was delayed by processing.
        if time.monotonic() >= deadline:
            expired()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Supervisor:
    def __init__(
        self,
        url,
        token,
        request_timeout=10,
        poll_interval=2,
        command_timeout=180,
        product="r4sls08",
        restart_timeout=None,
    ):
        if not token or not isinstance(token, str):
            raise SupervisorError("SUPERVISOR_TOKEN is required")
        try:
            self.product = get_product(product)
        except ValueError as error:
            raise SupervisorError(str(error)) from None
        self.url = url.rstrip("/")
        self.token = token
        self.request_timeout = request_timeout
        self.command_timeout = command_timeout
        self.restart_timeout = (
            command_timeout if restart_timeout is None else restart_timeout
        )
        self.poll_interval = poll_interval
        self.opener = urllib.request.build_opener(
            NoRedirect(), urllib.request.ProxyHandler({})
        )

    def request(self, method, path, timeout=None):
        budget = self.request_timeout if timeout is None else timeout
        with request_deadline(budget):
            request = urllib.request.Request(
                self.url + path,
                method=method,
                headers={
                    "Authorization": "Bearer " + self.token,
                    "Content-Type": "application/json",
                },
                data=b"{}" if method == "POST" else None,
            )
            try:
                with self.opener.open(request, timeout=budget) as response:
                    raw = response.read(4 * 1024 * 1024 + 1)
                    if len(raw) > 4 * 1024 * 1024:
                        raise SupervisorError("Supervisor response exceeds size limit")
                    return json.loads(raw)
            except urllib.error.HTTPError as error:
                error.close()
                raise SupervisorError(
                    f"Supervisor {method} {path} request failed"
                ) from None
            except (
                OSError,
                ValueError,
                urllib.error.URLError,
                http.client.HTTPException,
            ):
                raise SupervisorError(
                    f"Supervisor {method} {path} request failed"
                ) from None

    def running(self, timeout=None):
        body = self.request("GET", "/core/api/config", timeout)
        if not isinstance(body, dict) or body.get("state") != "RUNNING":
            raise SupervisorError("Home Assistant Core is not RUNNING")

    def check(self):
        self._command("/core/check")

    def restart(self):
        # Never retry a mutation: a transport failure may follow a successful restart.
        self._command("/core/restart", self.restart_timeout)

    def _command(self, path, timeout=None):
        body = self.request(
            "POST", path, self.command_timeout if timeout is None else timeout
        )
        if not isinstance(body, dict) or body.get("result") != "ok":
            raise SupervisorError(f"Supervisor {path} did not return result=ok")

    def loaded_entries(self, timeout=None):
        body = self.request(
            "GET",
            f"/core/api/config/config_entries/entry?domain={self.product.domain}",
            timeout,
        )
        if not isinstance(body, list):
            raise SupervisorError("Invalid config entry response")
        seen = set()
        loaded = []
        for entry in body:
            if (
                not isinstance(entry, dict)
                or not isinstance(entry.get("entry_id"), str)
                or not entry["entry_id"]
                or not isinstance(entry.get("state"), str)
                or not entry["state"]
                or entry["entry_id"] in seen
            ):
                raise SupervisorError("Invalid config entry response")
            seen.add(entry["entry_id"])
            if entry["state"] == "loaded":
                loaded.append(entry["entry_id"])
        return sorted(loaded)

    def wait_healthy(self, expected, timeout):
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SupervisorError(
                    "Core or expected integration entries failed health deadline"
                )
            try:
                self.running(min(self.request_timeout, remaining))
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    continue
                loaded = self.loaded_entries(min(self.request_timeout, remaining))
                if set(expected).issubset(loaded) and time.monotonic() < deadline:
                    return
            except SupervisorError:
                pass
            time.sleep(max(0, min(self.poll_interval, deadline - time.monotonic())))
