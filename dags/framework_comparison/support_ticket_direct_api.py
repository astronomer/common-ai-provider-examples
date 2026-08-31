"""
## support_ticket_direct_api

The `support_ticket_common_ai` flow with no agent framework at all. The draft
step calls the OpenAI SDK directly and hand-rolls both the tool-calling loop
and the structured output parsing. This is the floor to measure the other five
Dags against.
"""

from __future__ import annotations

from datetime import timedelta

from airflow.providers.standard.operators.hitl import (
    HITLBranchOperator,
    HITLEntryOperator,
)
from airflow.sdk import Param, chain, dag, task

from include.custom_functions import (
    OPENAI_TOOLS,
    SYSTEM_PROMPT,
    build_user_prompt,
    get_open_tickets,
    lookup_shipment,
)
from include.models import TicketResponse


@dag(
    dag_id="support_ticket_direct_api",
    tags=["framework-comparison", "openai-sdk", "hitl-operators", "support-ticket"],
    doc_md=__doc__,
)
def support_ticket_direct_api():
    @task
    def fetch_pending_ticket() -> dict:
        return get_open_tickets(1)[0]

    _fetch_pending_ticket = fetch_pending_ticket()

    @task
    def generate_ai_response(ticket: dict) -> dict:
        import json

        from openai import OpenAI

        client = OpenAI()
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(ticket)},
        ]
        while True:
            completion = client.chat.completions.parse(
                model="gpt-5-mini",
                messages=messages,
                tools=OPENAI_TOOLS,
                response_format=TicketResponse,
            )
            message = completion.choices[0].message
            if not message.tool_calls:
                return message.parsed.model_dump()
            messages.append(
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                }
            )
            for tc in message.tool_calls:
                arguments = json.loads(tc.function.arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            lookup_shipment(arguments["shipment_id"])
                        ),
                    }
                )

    _generate_ai_response = generate_ai_response(_fetch_pending_ticket)

    @task
    def format_approval_request(
        ai_response: TicketResponse | dict, original_ticket: dict
    ) -> dict:
        if not isinstance(ai_response, dict):
            ai_response = ai_response.model_dump()
        return {
            "ticket_info": (
                f"**Ticket:** {original_ticket['ticket_id']}\n"
                f"**Customer:** {original_ticket['customer_name']} "
                f"<{original_ticket['customer_email']}>\n"
                f"**Subject:** {original_ticket['subject']}\n"
                f"**Priority:** {original_ticket['priority']}"
            ),
            "summary": ai_response["summary"],
            "ai_response": ai_response["response"],
            "confidence": ai_response["confidence_score"],
            "priority": ai_response["priority"],
            "suggested_tags": ai_response["suggested_tags"],
            "metadata": ai_response,
            "original_ticket": original_ticket,
        }

    _format_approval_request = format_approval_request(
        ai_response=_generate_ai_response, original_ticket=_fetch_pending_ticket
    )

    _review_ai_response = HITLBranchOperator(
        task_id="review_ai_response",
        subject="AI Support Response Ready for Review",
        body="""**Please review the AI-generated support ticket response below:**

{{ ti.xcom_pull(task_ids='format_approval_request')['ticket_info'] }}

**AI Summary:**
{{ ti.xcom_pull(task_ids='format_approval_request')['summary'] }}

**AI Suggested Priority:** {{ ti.xcom_pull(task_ids='format_approval_request')['priority'] }}
**AI Confidence:** {{ "%.0f" | format(ti.xcom_pull(task_ids='format_approval_request')['confidence'] * 100) }}%
**Suggested Tags:** {{ ti.xcom_pull(task_ids='format_approval_request')['suggested_tags'] | join(', ') }}

**AI Response:**
```
{{ ti.xcom_pull(task_ids='format_approval_request')['ai_response'] }}
```

**Instructions:**
- **Approve**: Send this response to the customer
- **Reject**: Route to human agent for manual response

Please review for accuracy, tone, and completeness.""",
        options=[
            "Approve AI Response",
            "Respond Manually",
            "Escalate To CRE",
            "Escalate To CSM",
        ],
        options_mapping={
            "Approve AI Response": "approve_ai_response",
            "Respond Manually": "respond_manually",
            "Escalate To CRE": "escalate_to_cre",
            "Escalate To CSM": "escalate_to_csm",
        },
        defaults=["Escalate To CSM"],
        multiple=True,
        response_timeout=timedelta(hours=4),
    )

    @task
    def approve_ai_response(original_ticket: dict, ai_response: dict):
        print("Processing ticket:", original_ticket["ticket_id"])
        print("Sending Approved AI Response to customer:", ai_response["ai_response"])

    _approve_ai_response = approve_ai_response(
        ai_response=_format_approval_request,
        original_ticket=_fetch_pending_ticket,
    )

    _respond_manually = HITLEntryOperator(
        task_id="respond_manually",
        subject="Manual Response",
        body="""**Please enter the manual response to the customer:**
        ```
        {{ ti.xcom_pull(task_ids='format_approval_request')['original_ticket']['message'] }}
        ```
        """,
        params={
            "manual_response": Param(
                "None",
                type=["string"],
            ),
        },
    )

    @task
    def process_manual_response(original_ticket: dict, manual_response: dict):
        print("Processing ticket:", original_ticket["ticket_id"])
        print(
            "Sending Manual Response to customer:",
            manual_response["params_input"]["manual_response"],
        )

    _process_manual_response = process_manual_response(
        original_ticket=_fetch_pending_ticket,
        manual_response=_respond_manually.output,
    )

    @task
    def escalate_to_cre(original_ticket: dict):
        print("Processing ticket:", original_ticket["ticket_id"])
        print("Escalating to CRE")

    _escalate_to_cre = escalate_to_cre(
        original_ticket=_fetch_pending_ticket,
    )

    @task
    def escalate_to_csm(original_ticket: dict):
        print("Processing ticket:", original_ticket["ticket_id"])
        print("Escalating to CSM")

    _escalate_to_csm = escalate_to_csm(
        original_ticket=_fetch_pending_ticket,
    )

    chain(
        _format_approval_request,
        _review_ai_response,
        [
            _approve_ai_response,
            _respond_manually,
            _escalate_to_cre,
            _escalate_to_csm,
        ],
    )
    chain(
        _respond_manually,
        _process_manual_response,
    )


support_ticket_direct_api()
