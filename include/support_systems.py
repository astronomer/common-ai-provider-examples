CSAT_DIMENSIONS = ("resolution", "speed", "friendliness")

HELPDESK_REPLIES = [
    {
        "ticket_id": "TKT-4001",
        "customer_ask": (
            "Subject: Charged twice for October\n\n"
            "I was billed twice for my October invoice. Please refund the "
            "duplicate charge."
        ),
        "order_record": (
            "account_id: ACC-118\n"
            "account_tier: Starter\n"
            "invoice: INV-2026-10-118\n"
            "charges: 2026-10-01 $49.00 captured, 2026-10-01 $49.00 captured "
            "(duplicate, flagged by billing)\n"
            "refunds: 2026-10-14 $49.00 issued to card ending 4412\n"
            "refund_settlement: 5-7 business days"
        ),
        "support_response": (
            "Hi Priya,\n\nYou're right, October was charged twice on "
            "INV-2026-10-118. We refunded the duplicate $49.00 to the card "
            "ending 4412 on October 14, and it should settle back to your "
            "account within 5-7 business days.\n\n"
            "Sorry for the extra step on your end.\n\nBest,\nSupport"
        ),
        "agent": "rosa.mendez",
        "responded_at": "2026-08-14T09:12:00Z",
    },
    {
        "ticket_id": "TKT-4002",
        "customer_ask": (
            "Subject: API returning 500s in production\n\n"
            "Our integration has been failing with 500 errors for 20 minutes, "
            "blocking checkout for all of our customers."
        ),
        "order_record": (
            "account_id: ACC-204\n"
            "account_tier: Enterprise\n"
            "plan: Platform, 99.9% uptime SLA\n"
            "incident: INC-772 open, elevated 5xx on /v2/charges in eu-west-1\n"
            "incident_started: 14:02 UTC\n"
            "mitigation: rollback of release 2026.8.3 in progress\n"
            "status_page: updated 14:19 UTC"
        ),
        "support_response": (
            "Yeah, we're aware. There's an incident open (INC-772), 5xx on "
            "/v2/charges in eu-west-1, and a rollback is going out. Watch the "
            "status page for updates, no need to keep writing in.\n\nSupport"
        ),
        "agent": "dev.kapoor",
        "responded_at": "2026-08-14T14:26:00Z",
    },
    {
        "ticket_id": "TKT-4003",
        "customer_ask": (
            "Subject: How do I export my data?\n\n"
            "Could you point me to docs on exporting my account data to CSV?"
        ),
        "order_record": (
            "account_id: ACC-091\n"
            "account_tier: Growth\n"
            "features_enabled: csv_export, scheduled_reports\n"
            "export_limits: 100k rows per export, 10 exports per day\n"
            "docs: /docs/exports/csv"
        ),
        "support_response": (
            "Hi Marco,\n\nHappy to help. You can export from Settings > Data > "
            "Export, and the step-by-step is at /docs/exports/csv. On your "
            "plan you can pull up to 100k rows per export, 10 exports a day. If "
            "you'd rather not click through each time, our Snowflake and "
            "BigQuery connectors will sync the same tables continuously, just "
            "flip them on under Integrations.\n\nBest,\nSupport"
        ),
        "agent": "rosa.mendez",
        "responded_at": "2026-08-14T11:03:00Z",
    },
    {
        "ticket_id": "TKT-4004",
        "customer_ask": (
            "Subject: Cancel before renewal\n\n"
            "Our renewal is on the 1st and we've decided not to continue. Can "
            "you confirm the cancellation is processed and that we won't be "
            "charged?"
        ),
        "order_record": (
            "account_id: ACC-457\n"
            "account_tier: Enterprise\n"
            "contract: annual, auto-renew on 2026-09-01\n"
            "cancellation_request: received 2026-08-14\n"
            "notice_period: 30 days before renewal\n"
            "status: cancellation acknowledged, effective 2026-09-01, no "
            "renewal charge scheduled"
        ),
        "support_response": (
            "Hi Dana,\n\nThanks for the heads up. Your workspace stays on the "
            "Platform plan through August 31 and everything keeps working until "
            "then. Exports are available for 30 days after that if you want a "
            "copy of your data.\n\nBest,\nSupport"
        ),
        "agent": "tom.whitfield",
        "responded_at": "2026-08-14T16:41:00Z",
    },
    {
        "ticket_id": "TKT-4005",
        "customer_ask": (
            "Subject: Feature request - dark mode\n\n"
            "Would love to see a dark mode option in the dashboard."
        ),
        "order_record": (
            "account_id: ACC-330\n"
            "account_tier: Starter\n"
            "feature_request: FR-1188 dark mode, status: under consideration\n"
            "roadmap_commitment: none\n"
            "vote_count: 412"
        ),
        "support_response": (
            "Hi Yusuf,\n\nGreat news, dark mode ships in the next release at the "
            "end of the quarter and will be on by default for every account. "
            "Thanks for being patient with us.\n\nBest,\nSupport"
        ),
        "agent": "dev.kapoor",
        "responded_at": "2026-08-14T13:55:00Z",
    },
]

INBOX_REPLIES = [
    {
        "ticket_id": "TKT-4001",
        "customer_response": (
            "Perfect, I can see the refund pending on the card already. Thanks "
            "for turning that around so fast."
        ),
        "received_at": "2026-08-14T10:47:00Z",
    },
    {
        "ticket_id": "TKT-4002",
        "customer_response": (
            "Our checkout has been down for half an hour and \"no need to keep "
            "writing in\" is not an acceptable answer for an account on a 99.9% "
            "SLA. I want someone from your side on a call with our CTO today, "
            "and I want to know what the credit looks like."
        ),
        "received_at": "2026-08-14T14:33:00Z",
    },
    {
        "ticket_id": "TKT-4003",
        "customer_response": (
            "The CSV export worked, thank you. I went looking for the Snowflake "
            "connector though and there is nothing under Integrations. Is it "
            "something you have to enable for us, or does my plan not include "
            "it? I had already told my team we could set up the sync this week."
        ),
        "received_at": "2026-08-14T15:20:00Z",
    },
    {
        "ticket_id": "TKT-4004",
        "customer_response": (
            "That doesn't answer what I asked. I need written confirmation that "
            "the cancellation is processed and that no renewal charge will hit "
            "our card on September 1. Finance needs that before month end."
        ),
        "received_at": "2026-08-14T17:08:00Z",
    },
    {
        "ticket_id": "TKT-4005",
        "customer_response": (
            "Amazing, that made my day. I'll let the rest of the team know it's "
            "coming at the end of the quarter."
        ),
        "received_at": "2026-08-14T14:12:00Z",
    },
]

SURVEY_RESPONSES = [
    {
        "ticket_id": "TKT-4001",
        "ratings": {"resolution": 5, "speed": 5, "friendliness": 5},
        "submitted_at": "2026-08-15T08:02:00Z",
    },
    {
        "ticket_id": "TKT-4002",
        "ratings": {"resolution": 3, "speed": 2, "friendliness": 1},
        "submitted_at": "2026-08-15T07:44:00Z",
    },
    {
        "ticket_id": "TKT-4003",
        "ratings": {"resolution": 3, "speed": 4, "friendliness": 5},
        "submitted_at": "2026-08-15T09:31:00Z",
    },
    {
        "ticket_id": "TKT-4004",
        "ratings": {"resolution": 2, "speed": 4, "friendliness": 4},
        "submitted_at": "2026-08-15T08:57:00Z",
    },
    {
        "ticket_id": "TKT-4005",
        "ratings": {"resolution": 5, "speed": 5, "friendliness": 5},
        "submitted_at": "2026-08-15T10:15:00Z",
    },
]


def fetch_support_replies() -> list[dict]:
    return HELPDESK_REPLIES


def fetch_customer_replies() -> list[dict]:
    return INBOX_REPLIES


def fetch_satisfaction_scores() -> list[dict]:
    return SURVEY_RESPONSES
