Common AI Provider Example DAGs
===============================

Example Airflow DAGs covering every user-facing component of
[`apache-airflow-providers-common-ai`](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/).
Space-logistics themed. Each DAG follows a uniform shape so the demo is
legible:

```
prepare_input  ->  <ai operator / decorator>  ->  consume_output
```

`prepare_input` synthesizes or loads context and hands it to the AI task.
`consume_output` pulls the XCom return value (often a Pydantic model) and
does something observable with it.

---

Quick start
-----------

```bash
# 1. put your OpenAI key in .env (replace the blank)
#    OPENAI_API_KEY=sk-...
# 2. start Airflow; Astro auto-loads .env into the containers
astro dev start
```

Connections live in `.env` as `AIRFLOW_CONN_*` JSON entries (one per line).
The `pydanticai_default` connection points at OpenAI (`openai:gpt-5-mini`);
swap the `model` field to target Anthropic, Bedrock, Vertex AI, Ollama,
or any other pydantic-ai provider — operators are provider-agnostic.

Validate locally without triggering:

```bash
astro dev parse
```

---

Provider surface coverage
-------------------------

| Component | Type | Covered by |
|---|---|---|
| `LLMOperator` / `@task.llm` | Operator | `example_llm_operator.py` |
| `LLMBranchOperator` / `@task.llm_branch` | Operator | `example_llm_branch.py` |
| `LLMSQLQueryOperator` / `@task.llm_sql` | Operator | `example_llm_sql_query.py` |
| `LLMFileAnalysisOperator` / `@task.llm_file_analysis` | Operator | `example_llm_file_analysis.py` |
| `LLMSchemaCompareOperator` | Operator | `example_llm_schema_compare.py` |
| `AgentOperator` / `@task.agent` (no toolset) | Operator | `example_agent_basic.py` |
| `AgentOperator` + `SQLToolset` | Toolset | `example_agent_sql_toolset.py` |
| `AgentOperator` + `HookToolset` | Toolset | `example_agent_hook_toolset.py` |
| `AgentOperator` + `DataFusionToolset` | Toolset | `example_agent_datafusion_toolset.py` |
| `AgentOperator` + `MCPToolset` | Toolset | `example_agent_mcp_toolset.py` |
| `AgentOperator` + `LoggingToolset` | Toolset | `example_agent_logging_toolset.py` |
| Multi-toolset composition | Pattern | `example_agent_multi_toolset.py` |
| HITL review (FastAPI `/hitl-review` plugin) | Feature | `example_agent_hitl_review.py` |
| `PydanticAIHook.create_agent()` direct | Hook | `example_pydantic_ai_hook.py` |
| `mcp` connection (stdio + http transports) | Connection | `example_mcp_connection_transports.py` |
| `pydanticai` connection | Connection | every DAG (`pydanticai_default`) |

Pydantic `output_type=...` is exercised in `example_llm_operator`,
`example_llm_file_analysis`, `example_agent_basic`, `example_agent_sql_toolset`,
and `example_pydantic_ai_hook`.

---

Project layout
--------------

```
dags/
  example_llm_operator.py
  example_llm_branch.py
  example_llm_sql_query.py
  example_llm_file_analysis.py
  example_llm_schema_compare.py
  example_agent_basic.py
  example_agent_sql_toolset.py
  example_agent_hook_toolset.py
  example_agent_datafusion_toolset.py
  example_agent_mcp_toolset.py
  example_agent_logging_toolset.py
  example_agent_multi_toolset.py
  example_agent_hitl_review.py
  example_pydantic_ai_hook.py
  example_mcp_connection_transports.py
include/
  models.py              - shared Pydantic output models
  seed.py                - seeds /tmp/space_logistics.db and the drifted alt DB
  fixtures_hook.py       - FSHook subclass with list_files/read_file for HookToolset
  csvs/                  - space-logistics seed data
  fixtures/              - anomaly_report.log (+ .md source), cargo_manifests/*.json
  mcp_server/            - tiny stdio MCP server (space tools)
.env                     - OPENAI_API_KEY + AIRFLOW_CONN_* JSON entries for
                           pydanticai_default, mcp_default, mcp_stdio_space,
                           space_logistics, space_logistics_alt, fixtures_fs
docker-compose.override.yml - overrides AIRFLOW__API__BASE_URL so the HITL
                           Review React bundle loads from the project subdomain
                           instead of the Astro default http://localhost:8080
requirements.txt         - apache-airflow-providers-common-ai[sql,mcp,parquet,avro]==0.1.0,
                           apache-airflow-providers-sqlite==4.3.2,
                           pydantic-ai-slim[openai,anthropic,mcp]==1.85.1,
                           datafusion==53.0.0
```

---

Running individual DAGs
-----------------------

All DAGs are `schedule=None, catchup=False`. Trigger from the UI or:

```bash
uvx --from astro-airflow-mcp af runs trigger-wait example_llm_operator
```

For the HITL example, after triggering open the task-instance page for
`example_agent_hitl_review.review_plan` and click the **HITL Review** tab —
that's where the chat UI for approve / reject / request-changes lives.
`/hitl-review/*` on the API server is the underlying REST API, not an HTML
page. The React bundle that powers the tab is loaded from
`AIRFLOW__API__BASE_URL`; Astro defaults that to `http://localhost:8080`,
which the browser can't reach on a subdomain-based local env, so this repo
ships a `docker-compose.override.yml` that pins it to the project subdomain.
If you rename the project (or change the Astro port), update the override.

---

Adapting to your stack
----------------------

- Swap the LLM by editing `pydanticai_default.extra.model` to e.g.
  `anthropic:claude-sonnet-4-6` or `ollama:llama3`. Set the matching API
  key via `conn_password` or environment variable.
- Swap the warehouse by pointing the `space_logistics` connection at
  Postgres, Snowflake, or BigQuery — no DAG changes required for the
  SQL-toolset and schema-compare examples.
- Add your own MCP server by updating `mcp_default` (HTTP) or
  `mcp_stdio_space` (stdio command/args).
