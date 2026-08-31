SAMPLE_EMAILS = [
    "Subject: Charged twice for October\n\nI was billed twice for my October "
    "invoice. Please refund the duplicate charge.",
    "Subject: API returning 500s in production\n\nOur integration has been "
    "failing with 500 errors for 20 minutes, blocking checkout for all of "
    "our customers.",
    "Subject: How do I export my data?\n\nCould you point me to docs on "
    "exporting my account data to CSV?",
    "Subject: Feature request - dark mode\n\nWould love to see a dark mode "
    "option in the dashboard.",
]


def fetch_emails_from_server() -> list[str]:
    return SAMPLE_EMAILS


EMAIL_CLASSIFICATION_SYSTEM_PROMPT = (
    "You are a support inbox triage assistant. Classify each inbound email "
    "by priority and topic tags.\n\n"
    "Priority levels:\n"
    "- P0: Full outage or critical failure affecting many customers right "
    "now (e.g. production down, data loss, security incident). Needs "
    "immediate human attention.\n"
    "- P1: Severe issue affecting a single customer's ability to use the "
    "product (e.g. broken integration, blocked payment, major bug with no "
    "workaround).\n"
    "- P2: Real problem with a workaround or limited impact (e.g. billing "
    "discrepancy, confusing but non-blocking error, degraded but working "
    "feature).\n"
    "- P3: General question, how-to request, or minor issue that isn't "
    "urgent (e.g. documentation question, account setting help).\n"
    "- P4: No action needed beyond an automated reply (e.g. feature "
    "request, feedback, thank-you note)."
)
