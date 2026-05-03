<p align="center">
  <h1 align="center">AI Dev Agent Suite</h1>
  <p align="center">A local-first multi-agent system for developer productivity — requirement analysis, task planning, code review, test generation, RAG knowledge retrieval, and release risk assessment in a single run.</p>
</p>

<p align="center">
  <a href="https://github.com/1580647885cyh-cyh/mi/actions"><img src="https://github.com/1580647885cyh-cyh/mi/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+"></a>
</p>

> English | [中文](#中文)

## Features

- **Requirement Agent** — extracts goals, features, acceptance criteria, and open questions from PRD/user descriptions
- **Task Planner Agent** — auto-generates Jira-style tasks across PM, backend, frontend, QA, and DevOps
- **Code Review Agent** — scans repo snapshots for hardcoded secrets, SQL injection, broad exceptions, TODOs, missing tests
- **Test Generator Agent** — produces happy-path, edge-case, and pytest skeleton test cases
- **RAG Knowledge Agent** — retrieves relevant policies from a local Markdown knowledge base with source citations
- **Release Risk Agent** — outputs risk matrix, release checklist, and rollback recommendations
- **Three interfaces** — Web UI, REST API, CLI
- **Zero LLM dependency** — all agents use explainable rule engines out of the box; swap in a real LLM by replacing each agent's `run()` method

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app:app --reload --port 8000
```

Open http://127.0.0.1:8000.

## CLI

```bash
# From a JSON payload
python cli.py --input scripts/demo_payload.json --output run_result.json

# From a one-liner
python cli.py --requirement "Build a smart ticket triage system with knowledge base Q&A and risk detection."

# Scan a real repository
python cli.py --requirement "Review this repo for security issues" --repo-dir /path/to/your/repo
```

## API

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d @scripts/demo_payload.json
```

## Architecture

```
                   ┌─────────────────────────────┐
                   │   Web UI / CLI / REST API    │
                   └─────────────┬───────────────┘
                                 │
                   ┌─────────────▼───────────────┐
                   │       AgentWorkflow          │
                   │   (orchestration layer)      │
                   └──────┬──────┬──────┬─────────┘
                          │      │      │
          ┌───────────────┤      │      ├───────────────┐
          ▼               ▼      ▼      ▼               ▼
   ┌──────────┐   ┌──────────┐  ...  ┌──────────┐  ┌──────────┐
   │Requirement│  │  Task     │       │  Release  │  │   RAG    │
   │  Agent   │   │ Planner   │       │   Risk    │  │  Agent   │
   └──────────┘   └──────────┘       └──────────┘  └──────────┘
          │               │                  │           │
          └───────────────┴──────────────────┴───────────┘
                                 │
                   ┌─────────────▼───────────────┐
                   │      Structured JSON Output    │
                   │      + Executive Summary       │
                   └─────────────────────────────┘
```

## Project Structure

```
ai-dev-agent-suite/
├── backend/
│   ├── agents/               # 6 independent agents
│   │   ├── base.py           # shared NLP utilities
│   │   ├── requirement_agent.py
│   │   ├── task_agent.py
│   │   ├── code_review_agent.py
│   │   ├── test_agent.py
│   │   ├── rag_agent.py
│   │   └── release_risk_agent.py
│   ├── app.py                # FastAPI application
│   ├── workflow.py           # agent orchestration
│   ├── schemas.py            # data models (dataclasses)
│   ├── storage.py            # JSON file persistence
│   └── sample_data/knowledge/ # local Markdown knowledge base
├── frontend/                 # vanilla HTML/CSS/JS SPA
├── tests/
├── scripts/
├── cli.py
├── Dockerfile
├── Makefile
├── pyproject.toml
└── requirements.txt
```

## Tests

```bash
python -m pytest tests -v
```

## Docker

```bash
docker build -t ai-dev-agent-suite .
docker run -p 8000:8000 ai-dev-agent-suite
```

## Plugging in a Real LLM

All agents currently use rule-based engines. To integrate an LLM (OpenAI, Azure, local model):

```python
# In each agent's run(), replace the rule logic with:
response = llm_client.chat(
    system_prompt="You are a requirement analysis agent...",
    user_message=requirement,
    response_format=AgentResult
)
return response
```

The agent interfaces and workflow orchestration remain unchanged — only `run()` changes.

## License

MIT — see [LICENSE](LICENSE).

---

<a id="中文"></a>

## 中文说明

一个可本地运行的研发提效多 Agent 系统，覆盖需求理解、任务拆解、代码审查、测试生成、知识库检索和上线风险检查。所有 Agent 默认为可解释的规则实现，不依赖任何大模型 API。

### 功能亮点

- **需求理解 Agent**：从 PRD/用户描述中提取目标、功能点、验收标准和不明确问题
- **任务拆解 Agent**：自动生成前端、后端、测试、DevOps、产品等任务清单
- **代码审查 Agent**：扫描仓库快照，识别硬编码密钥、SQL 拼接、宽泛异常、TODO 等问题
- **测试生成 Agent**：生成核心测试、边界用例和 pytest 示例
- **RAG 知识库 Agent**：基于本地 Markdown 知识库做检索并给出引用来源
- **上线风险 Agent**：输出风险矩阵、上线检查清单和回滚建议

