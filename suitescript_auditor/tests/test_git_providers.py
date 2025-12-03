from suitescript_auditor.core.git import providers


def test_providers_registry():
    assert "github" in providers.PROVIDERS
    assert providers.PROVIDERS["gitlab"].remote_url.startswith("https://gitlab")
