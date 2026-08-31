Common AI Provider Example Dags
===============================

Example Airflow Dags for
[`apache-airflow-providers-common-ai`](https://airflow.apache.org/docs/apache-airflow-providers-common-ai/stable/) and
human-in-the-loop operators from the standard provider.

> See [Orchestrate AI tasks with Apache Airflow® and the Common AI provider](https://www.astronomer.io/docs/learn/airflow-common-ai-provider) and [Human-in-the-loop workflows with Airflow](https://www.astronomer.io/docs/learn/airflow-human-in-the-loop) for more information.

Astro Runtime 3.3 (Airflow 3.3). Provider versions are pinned in
`requirements.txt`.

How to use this repository
-----------

1. Copy `.env_example` to `.env` and add your own credentials for your model provider, adjust the model in `AIRFLOW_CONN_PYDANTICAI_DEFAULT` if needed.
2. Start Airflow

```bash
astro dev start
```

---

Layout
------

```
dags/
  01_llm_tasks/          one Dag per @task.llm* decorator
  02_agent/              @task.agent, from minimal to every knob turned on
  03_toolsets/           one Dag per toolset, plus one that combines three
  04_hitl/               human in the loop, standard operators and agent review
  05_connections_hooks/  the hook API and the MCP connection transports
  other/                 end-to-end pipelines built out of the above
  framework_comparison/  the same Dag six times, once per agent framework
```

### 01_llm_tasks

| Dag | Provider component |
|---|---|
| `example_llm_operator` | `LLMOperator` / `@task.llm` with a Pydantic `output_type` and `UsageLimits` |
| `example_llm_branch` | `LLMBranchOperator` / `@task.llm_branch` |
| `example_llm_sql_query` | `LLMSQLQueryOperator` / `@task.llm_sql` |
| `example_llm_file_analysis` | `LLMFileAnalysisOperator` / `@task.llm_file_analysis` |
| `example_llm_schema_compare` | `@task.llm_schema_compare` |

### 02_agent

| Dag | Provider component |
|---|---|
| `example_agent_basic` | `AgentOperator` / `@task.agent` with no toolset |
| `example_agent_complex` | `durable`, `usage_limits`, `message_history`, tool logging |
| `example_agent_advanced` | A custom `AbstractToolset` |
| `example_agent_basic_durable` | `durable=True` |
| `example_llm_retry_policy` | `LLMRetryPolicy` |

### 03_toolsets

| Dag | Toolset |
|---|---|
| `example_agent_sql_toolset` | `SQLToolset` |
| `example_agent_hook_toolset` | `HookToolset`. Any Airflow Hook's methods can become tools |
| `example_agent_datafusion_toolset` | `DataFusionToolset` |
| `example_agent_mcp_toolset` | `MCPToolset` |
| `example_agent_logging_toolset` | `LoggingToolset`|
| `example_agent_multi_toolset` | SQL, Hook and Logging toolset |

### 04_hitl

| Dag | Operator | Info |
|---|---|---|
| `example_hitl_approval` | `ApprovalOperator` | Approve or reject. Rejecting skips the downstream tasks |
| `example_hitl_operator` | `HITLOperator` | N options, `multiple=True` |
| `example_hitl_branch` | `HITLBranchOperator` | `options_mapping`  |
| `example_hitl_entry` | `HITLEntryOperator` | Input form |
| `example_agent_hitl_review` | common-ai `enable_hitl_review=True` | Note: HITL interaction in a separate plugin tab on the task instances |

That last one is the only Dag here that uses common-ai's React review plugin.
The plugin loads its JS bundle from `AIRFLOW__API__BASE_URL`, so if your Airflow
isn't on `http://localhost:8080` you need the base-URL block in
`docker-compose.override.yml`, which ships commented out. The four standard
operators work either way.

### 05_connections_hooks

| Dag | Provider component |
|---|---|
| `example_pydantic_ai_hook` | `PydanticAIHook.create_agent()` |
| `example_mcp_connection_transports` | `mcp` connection using stdio and http |

### other

| Dag | What it builds |
|---|---|
| `email_routing` | `@task.llm` sorts mail into P0-P4, `@task.branch` routes it |
| `support_reply_evals` | LLM as judge. Scores agent replies and customer reactions, CSAT|

---

Agent framework comparison
--------------------------------------------------

Six Dags run an identical support-ticket flow. Fetch a ticket, draft a
structured `TicketResponse` using a `lookup_shipment` tool, HITL review branch.

| Dag | Framework |
|---|---|
| `support_ticket_common_ai` | common-ai provider (`@task.agent`) |
| `support_ticket_pydantic_ai` | pydantic-ai used directly |
| `support_ticket_langgraph` | LangGraph ReAct agent |
| `support_ticket_crewai` | CrewAI single-agent crew |
| `support_ticket_temporal` | Temporal workflow |
| `support_ticket_direct_api` | OpenAI SDK and a hand-written tool loop |

All examples other than the common AI one use `gpt-5-mini` with `OPENAI_API_KEY`, adjust for other model providers.

The Temporal Dag uses the `temporal` service from `docker-compose.override.yml`. Its web UI is at `http://localhost:8233`.

---
