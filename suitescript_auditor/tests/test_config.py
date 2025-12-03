import json

from suitescript_auditor.core.config import loader, secure_store
from suitescript_auditor.core.config.defaults import defaults


def test_loader_returns_defaults_when_missing(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"llm_model": "custom-model"}), encoding="utf-8")
    config = loader.load_config(config_path)
    assert config["llm_model"] == "custom-model"
    assert config["region"] == defaults.region


def test_secure_store_uses_keyring(monkeypatch):
    store = {}

    class DummyKeyring:
        def set_password(self, service, name, value):
            store[name] = value

        def get_password(self, service, name):
            return store.get(name)

    monkeypatch.setattr(secure_store, "keyring", DummyKeyring())
    secure_store.save_secret("token", "abc123")
    assert secure_store.load_secret("token") == "abc123"
