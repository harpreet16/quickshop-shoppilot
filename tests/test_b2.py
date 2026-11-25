"""B2 provider and subprocess regressions; no real model requests."""

import runpy
import subprocess
import sys
from types import SimpleNamespace

import pytest

from baselines.b2 import run as b2
from eval import runner


@pytest.fixture
def gemini(monkeypatch):
    calls = {}

    def generate(**kwargs):
        calls["request"] = kwargs
        return SimpleNamespace(text=calls.get("text", "Grounded answer"))

    def client(**kwargs):
        calls["client"] = kwargs
        return SimpleNamespace(models=SimpleNamespace(generate_content=generate))

    types = SimpleNamespace(
        **{
            name: lambda **kw: SimpleNamespace(**kw)
            for name in (
                "HttpOptions",
                "GenerateContentConfig",
                "Tool",
                "GoogleSearch",
            )
        }
    )
    monkeypatch.setitem(
        sys.modules, "google", SimpleNamespace(genai=SimpleNamespace(Client=client))
    )
    monkeypatch.setitem(sys.modules, "google.genai", SimpleNamespace(types=types))
    monkeypatch.setattr(b2, "PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    return calls


def test_gemini_uses_search_and_bounded_timeout(gemini):
    assert b2.web_grounded_call("cotton shirt") == "Grounded answer"
    assert gemini["client"]["http_options"].timeout == 90_000
    assert gemini["request"]["model"] == b2.MODEL
    assert "cotton shirt" in gemini["request"]["contents"]
    assert gemini["request"]["config"].tools[0].google_search is not None


@pytest.mark.parametrize("text", [None, "", "  "])
def test_empty_gemini_response_is_a_failure(gemini, text):
    gemini["text"] = text
    with pytest.raises(b2.BaselineError, match="no text"):
        b2.web_grounded_call("shirt")


def test_missing_sdk_has_install_instructions(monkeypatch):
    monkeypatch.setattr(b2, "PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    monkeypatch.setitem(sys.modules, "google", SimpleNamespace())
    with pytest.raises(b2.BaselineError, match="Missing google-genai"):
        b2.web_grounded_call("shirt")


@pytest.mark.parametrize(
    "provider,key",
    [
        ("gemini", "GEMINI_API_KEY"),
        ("openai", "WEBSEARCH_API_KEY"),
        ("openrouter", "OPENROUTER_API_KEY"),
    ],
)
def test_missing_key_is_actionable(monkeypatch, provider, key):
    monkeypatch.setattr(b2, "PROVIDER", provider)
    monkeypatch.delenv(key, raising=False)
    with pytest.raises(b2.BaselineError, match=key):
        b2.web_grounded_call("shirt")


def test_openai_search_and_empty_response(monkeypatch):
    import openai

    calls = {}
    response = SimpleNamespace(output_text="Answer")

    def create(**kwargs):
        calls["request"] = kwargs
        return response

    def client(**kwargs):
        calls["client"] = kwargs
        return SimpleNamespace(responses=SimpleNamespace(create=create))

    monkeypatch.setattr(b2, "PROVIDER", "openai")
    monkeypatch.setenv("WEBSEARCH_API_KEY", "test-only")
    monkeypatch.setattr(openai, "OpenAI", client)
    assert b2.web_grounded_call("shirt") == "Answer"
    assert calls["request"]["tools"] == [{"type": "web_search"}]
    assert calls["client"] == {
        "api_key": "test-only",
        "timeout": 90.0,
        "max_retries": 0,
    }
    response.output_text = ""
    with pytest.raises(b2.BaselineError, match="no text"):
        b2.web_grounded_call("shirt")


@pytest.mark.parametrize(
    "provider,model",
    [
        ("openrouter", "google/gemini-3.8-flash"),
        ("gemini", "gemini-3.8-flash"),
        ("openai", "gpt-4o"),
        ("", "google/gemini-3.8-flash"),
    ],
)
def test_provider_specific_default_model(monkeypatch, provider, model):
    monkeypatch.setenv("PYTHON_DOTENV_DISABLED", "1")
    monkeypatch.setenv("WEBSEARCH_PROVIDER", provider)
    monkeypatch.setenv("WEBSEARCH_MODEL", "")
    assert runpy.run_path(b2.__file__)["MODEL"] == model


def test_mock_needs_no_provider(monkeypatch):
    monkeypatch.setattr(b2, "PROVIDER", "unsupported")
    assert "[MOCK OUTPUT]" in b2.web_grounded_call("shirt", mock=True)
    with pytest.raises(b2.BaselineError, match="WEBSEARCH_PROVIDER"):
        b2.web_grounded_call("shirt")


@pytest.fixture
def cli(monkeypatch, tmp_path):
    monkeypatch.setattr(b2, "__file__", str(tmp_path / "run.py"))
    monkeypatch.setattr(sys, "argv", ["run.py"])
    (tmp_path / "input.txt").write_text("shirt")
    return tmp_path / "output.txt"


def test_cli_writes_only_successful_answers(cli, monkeypatch, capsys):
    monkeypatch.setattr(b2, "web_grounded_call", lambda *a, **kw: "Fresh answer")
    assert b2.main() == 0
    assert cli.read_text() == "Fresh answer"
    assert capsys.readouterr().out == "Fresh answer\n"


def test_cli_explains_provider_failure_without_leaking_body(cli, monkeypatch, capsys):
    class ProviderError(Exception):
        code = 429

    def fail(*args, **kwargs):
        raise ProviderError("private key and request body")

    cli.write_text("Old answer")
    monkeypatch.setattr(b2, "web_grounded_call", fail)
    assert b2.main() == 1
    captured = capsys.readouterr()
    assert "HTTP 429" in captured.err and "quota" in captured.err
    assert "private" not in captured.err and captured.out == ""
    assert cli.read_text() == "Old answer"


def test_cli_prints_safe_setup_error(cli, monkeypatch, capsys):
    def fail(*args, **kwargs):
        raise b2.BaselineError("Missing google-genai")

    monkeypatch.setattr(b2, "web_grounded_call", fail)
    assert b2.main() == 1
    assert "Missing google-genai" in capsys.readouterr().err
    assert not cli.exists()


@pytest.fixture
def baseline_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(runner, "__file__", str(tmp_path / "eval" / "runner.py"))
    path = tmp_path / "baselines" / "b2"
    path.mkdir(parents=True)
    (path / "output.txt").write_text("Stale answer")
    return path


@pytest.mark.parametrize(
    "code,stdout,stderr,expected_error",
    [
        (1, "partial output", "B2: Missing google-genai", "Missing google-genai"),
        (1, "", "", "exited with code 1"),
        (0, " ", "", "empty output"),
    ],
)
def test_eval_keeps_failure_diagnostics_not_stale_output(
    baseline_dir, monkeypatch, code, stdout, stderr, expected_error
):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess([], code, stdout, stderr),
    )
    result = runner.run_b2("new query")
    assert result["success"] is False and result["output"] == ""
    assert result["exit_code"] == code and expected_error in result["error"]
    assert (baseline_dir / "output.txt").read_text() == "Stale answer"


def test_eval_uses_fresh_stdout(baseline_dir, monkeypatch):
    def invoke(args, **kwargs):
        assert args[0] == sys.executable and kwargs["timeout"] == 120
        return subprocess.CompletedProcess(args, 0, "Fresh answer\n", "")

    monkeypatch.setattr(subprocess, "run", invoke)
    result = runner.run_b2("new query")
    assert result["success"] is True and result["output"] == "Fresh answer"
    assert "error" not in result


def test_eval_timeout_is_recorded(baseline_dir, monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("b2", 120)

    monkeypatch.setattr(subprocess, "run", timeout)
    result = runner.run_b2("query")
    assert result["success"] is False and "timed out" in result["error"]


def test_eval_bounds_diagnostics(baseline_dir, monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess([], 1, "", "x" * 5000),
    )
    assert len(runner.run_b2("query")["error"]) == 4000


@pytest.mark.parametrize("content", ["Grounded Gemini answer", "", None])
def test_openrouter_uses_gemini_native_search(monkeypatch, content):
    import openai

    calls = {}
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )

    def create(**kwargs):
        calls["request"] = kwargs
        return response

    def client(**kwargs):
        calls["client"] = kwargs
        return SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(create=create))
        )

    monkeypatch.setattr(b2, "PROVIDER", "openrouter")
    monkeypatch.setattr(b2, "MODEL", "google/gemini-3.8-flash")
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-only")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(openai, "OpenAI", client)
    if content:
        assert b2.web_grounded_call("shirt") == content
    else:
        with pytest.raises(b2.BaselineError, match="OpenRouter returned no text"):
            b2.web_grounded_call("shirt")
    assert calls["client"] == {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "test-only",
        "timeout": 90.0,
        "max_retries": 0,
    }
    assert calls["request"] == {
        "model": "google/gemini-3.8-flash",
        "messages": [{"role": "user", "content": b2.PROMPT.format(query="shirt")}],
        "extra_body": {"plugins": [{"id": "web", "engine": "native"}]},
    }
    response.choices = []
    with pytest.raises(b2.BaselineError, match="OpenRouter returned no text"):
        b2.web_grounded_call("shirt")
