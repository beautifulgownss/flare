"""Shared HTTP session with timeouts and retries for third-party APIs.

Hunter, Serper, and HubSpot all rate-limit (HTTP 429) and occasionally return
transient 5xx errors. Without a timeout, a hung connection would stall a
scheduled CI run until the job is killed. Every outbound call goes through
this session so behavior is consistent across pipeline steps.
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DEFAULT_TIMEOUT = 20  # seconds
RETRY_STATUSES = (429, 500, 502, 503, 504)


class _TimeoutAdapter(HTTPAdapter):
    def send(self, request, **kwargs):
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = DEFAULT_TIMEOUT
        return super().send(request, **kwargs)


def build_session(total_retries: int = 3, backoff_factor: float = 1.0) -> requests.Session:
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff_factor,
        status_forcelist=RETRY_STATUSES,
        allowed_methods=frozenset({"GET", "POST", "PATCH", "PUT"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = _TimeoutAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


session = build_session()
