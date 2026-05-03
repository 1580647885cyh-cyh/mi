from backend.workflow import AgentWorkflow


def test_workflow_returns_structured_results():
    workflow = AgentWorkflow()
    result = workflow.run({
        "project_name": "unit-test-demo",
        "requirement": "做一个研发提效 Agent，支持需求拆解、代码审查和测试生成，目标是减少 40% 人工时间。",
        "repository_snapshot": {"app.py": "print('debug')\n# TODO: remove before release"},
    })
    assert result["run_id"]
    assert "requirement_agent" in result["results"]
    assert "code_review_agent" in result["results"]
    assert result["estimated_impact"]["estimated_minutes_saved_per_run"] > 0


def test_code_review_detects_secret_and_sql():
    workflow = AgentWorkflow()
    result = workflow.run({
        "project_name": "security-demo",
        "requirement": "系统需要扫描代码风险并阻断高危问题。",
        "repository_snapshot": {"repo.py": "password = 'super-secret-value'\ndef q(uid):\n    return f'SELECT * FROM users WHERE id = {uid}'\n"},
    })
    findings = result["results"]["code_review_agent"]["findings"]
    titles = {f["title"] for f in findings}
    assert "疑似硬编码密钥" in titles
    assert "可能存在 SQL 拼接风险" in titles


def test_empty_requirement_raises():
    workflow = AgentWorkflow()
    try:
        workflow.run({"requirement": ""})
    except ValueError as exc:
        assert "requirement" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
