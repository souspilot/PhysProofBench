"""Request shape for the OpenAI-compatible endpoints we call."""
from types import SimpleNamespace

from physproofbench.models.openai_client import complete
from physproofbench.preflight import check_endpoint


class _FakeClient:
    def __init__(self, base_url):
        self.base_url = base_url
        self.request = None
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **request):
        self.request = request
        message = SimpleNamespace(content="ok")
        return SimpleNamespace(model=request["model"], usage=None,
                               choices=[SimpleNamespace(message=message, finish_reason="stop")])


def test_google_endpoint_gets_top_level_reasoning_effort():
    client = _FakeClient("https://generativelanguage.googleapis.com/v1beta/openai/")
    complete("p", model="m", reasoning_effort="high", client=client)
    assert client.request["reasoning_effort"] == "high"
    assert client.request["extra_body"] is None


def test_openrouter_gets_unified_reasoning_field():
    client = _FakeClient("https://openrouter.ai/api/v1")
    complete("p", model="m", reasoning_effort="high", client=client)
    assert "reasoning_effort" not in client.request
    assert client.request["extra_body"] == {"reasoning": {"effort": "high"}}


def test_seed_sent_except_to_google_endpoint():
    google = _FakeClient("https://generativelanguage.googleapis.com/v1beta/openai/")
    complete("p", model="m", seed=7, client=google)
    assert "seed" not in google.request
    openrouter = _FakeClient("https://openrouter.ai/api/v1")
    complete("p", model="m", seed=7, client=openrouter)
    assert openrouter.request["seed"] == 7


def test_preflight_accepts_google_model_id_prefix(monkeypatch):
    client = _FakeClient("https://generativelanguage.googleapis.com/v1beta/openai/")
    client.models = SimpleNamespace(
        list=lambda: SimpleNamespace(data=[SimpleNamespace(id="models/gemini-4-argon")]))
    monkeypatch.setenv("OPENAI_BASE_URL", str(client.base_url))
    monkeypatch.setattr("physproofbench.preflight.get_client", lambda *a, **k: client)
    checks, _ = check_endpoint("gemini-4-argon")
    assert all(c.ok for c in checks)
