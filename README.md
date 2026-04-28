Common AI Provider Example Dags
===============================

Example Airflow Dags covering every user-facing component of
[`apache-airflow-providers-common-ai`](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/),
themed around space logistics.

> **For a full walkthrough of the provider — operators, hooks, toolsets,
> connections, and HITL — see the Astronomer guide:
> [Airflow Common AI provider](https://www.astronomer.io/docs/learn/airflow-common-ai-provider).**

---

Quick start
-----------

1. Copy .env_example to .env and add your own credentials
2. Start Airflow

```bash
astro dev start
```

Connections live in `.env` as `AIRFLOW_CONN_*` JSON entries. The
`pydanticai_default` connection points at `openai:gpt-5-mini`; swap the
`extra.model` field to target Anthropic, Bedrock, Vertex AI, Ollama, or any
other pydantic-ai provider — operators are provider-agnostic.

---

Dags
----

| Dag | Provider component |
|---|---|
| `example_llm_operator.py` | `LLMOperator` / `@task.llm` + Pydantic `output_type` |
| `example_llm_branch.py` | `LLMBranchOperator` / `@task.llm_branch` |
| `example_llm_sql_query.py` | `LLMSQLQueryOperator` / `@task.llm_sql` |
| `example_llm_file_analysis.py` | `LLMFileAnalysisOperator` / `@task.llm_file_analysis` |
| `example_llm_schema_compare.py` | `LLMSchemaCompareOperator` |
| `example_agent_basic.py` | `AgentOperator` / `@task.agent` (no toolset) |
| `example_agent_basic_durable.py` | `AgentOperator` with `durable=True` (DurableStorage) |
| `example_agent_advanced.py` | `AgentOperator` with custom `AbstractToolset` + full constructor knobs |
| `example_agent_sql_toolset.py` | `SQLToolset` |
| `example_agent_hook_toolset.py` | `HookToolset` |
| `example_agent_datafusion_toolset.py` | `DataFusionToolset` |
| `example_agent_mcp_toolset.py` | `MCPToolset` |
| `example_agent_logging_toolset.py` | `LoggingToolset` |
| `example_agent_multi_toolset.py` | Multi-toolset composition |
| `example_agent_hitl_review.py` | HITL review (FastAPI `/hitl-review` plugin) |
| `example_pydantic_ai_hook.py` | `PydanticAIHook.create_agent()` direct |
| `example_mcp_connection_transports.py` | `mcp` connection (stdio + http transports) |

Every Dag uses the `pydanticai_default` connection.

---

Project layout
--------------

```
dags/                          - example Dags (table above)
include/
  models.py                    - shared Pydantic output models
  seed.py                      - seeds /tmp/space_logistics.db and the drifted alt DB
  fixtures_hook.py             - FSHook subclass with list_files/read_file for HookToolset
  iss_open_notify_toolset.py   - custom AbstractToolset used by the advanced agent DAG
  csvs/                        - space-logistics seed data
  fixtures/                    - anomaly_report.log, cargo_manifests/*.json, parquet, etc.
  mcp_server/                  - tiny stdio MCP server (space tools)
.env_example                   - Add your own credentials and update for your model provider as .env
docker-compose.override.yml    - optional, pins AIRFLOW__API__BASE_URL to the project subdomain
                                 so the HITL Review React bundle loads correctly if the URL differs from the default
requirements.txt               - common-ai provider, sqlite provider, pydantic-ai, datafusion
```

---

Running Dags
------------

All Dags are `schedule=None, catchup=False`. Trigger from the UI or:

```bash
uvx --from astro-airflow-mcp af runs trigger-wait example_llm_operator
```

For `example_agent_hitl_review`, after triggering open the task-instance page
for `review_plan` and click the **HITL Review** tab to approve / reject /
request changes. The bundled `docker-compose.override.yml` makes that tab
load on the project subdomain — if you rename the project or change the
Astro port, update the override.

---

Adapting to your stack
----------------------

- **Swap the LLM:** edit `pydanticai_default.extra.model` (e.g.
  `anthropic:claude-sonnet-4-6`, `ollama:llama3`). Set the matching API key
  via the connection or environment.
- **Swap the warehouse:** point `space_logistics` at Postgres, Snowflake, or
  BigQuery — no Dag changes needed for the SQL-toolset and schema-compare
  examples.
- **Plug in your MCP server:** update `mcp_default` (HTTP) or
  `mcp_stdio_space` (stdio command/args).

For deeper context on any of the above, see the
[Astronomer guide](https://www.astronomer.io/docs/learn/airflow-common-ai-provider).