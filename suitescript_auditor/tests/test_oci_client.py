from suitescript_auditor.core.llm.oci_client import OCIClient, OCIConfig


def test_oci_client_returns_placeholder():
    client = OCIClient(OCIConfig(region="us-phoenix-1", model="demo"))
    response = client.run_completion("hello world")
    assert response["needs_context"] is True
    assert "hello world"[:5] in response["prompt"]
