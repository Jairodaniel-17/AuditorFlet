from suitescript_auditor.core.llm import router


def test_router_selects_experts():
    assert router.route("ClientScript").experts == ["expert_clientscript", "expert_security"]
    assert router.route("UserEventScript").experts == ["expert_userevent", "expert_security"]
    assert router.route("Suitelet").experts == ["expert_suitelet", "expert_security"]
    assert router.route("MapReduceScript").experts == ["expert_mapreduce", "expert_security"]
    assert router.route(None).experts == ["expert_security"]
