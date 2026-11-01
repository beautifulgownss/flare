"""Tests for the HTTP session and orchestrator plumbing (no network)."""
from unittest.mock import patch

import pytest

import http_client
import run_pipeline


def test_session_applies_default_timeout_and_retries():
    session = http_client.build_session(total_retries=5)
    adapter = session.get_adapter("https://api.hunter.io")
    assert isinstance(adapter, http_client._TimeoutAdapter)
    assert adapter.max_retries.total == 5
    assert 429 in adapter.max_retries.status_forcelist
    assert adapter.max_retries.respect_retry_after_header

    with patch("requests.adapters.HTTPAdapter.send", return_value="ok") as send:
        adapter.send(object())
        assert send.call_args.kwargs["timeout"] == http_client.DEFAULT_TIMEOUT
        adapter.send(object(), timeout=3)
        assert send.call_args.kwargs["timeout"] == 3


def test_optional_step_failure_does_not_stop_pipeline():
    with patch("subprocess.run") as run:
        run.return_value.returncode = 1
        assert run_pipeline.run_step("Optional", "src/x.py", required=False) is None


def test_required_step_failure_exits():
    with patch("subprocess.run") as run:
        run.return_value.returncode = 2
        with pytest.raises(SystemExit) as exc:
            run_pipeline.run_step("Required", "src/x.py", required=True)
    assert exc.value.code == 1


def test_copy_dashboard_files_skips_missing_optional_outputs(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "runs_export.json").write_text("[]")
    (tmp_path / "pages").mkdir()
    (tmp_path / "pages" / "acme.html").write_text("<html></html>")
    public = tmp_path / "public"
    monkeypatch.setattr(run_pipeline, "ROOT", tmp_path)
    monkeypatch.setattr(run_pipeline, "DASHBOARD_PUBLIC", public)

    run_pipeline.copy_dashboard_files()

    assert (public / "runs_export.json").read_text() == "[]"
    assert (public / "pages" / "acme.html").exists()
    assert not (public / "pitch_pages_status.json").exists()
