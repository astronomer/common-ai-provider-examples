import json
import random
from pathlib import Path

SHIPMENTS_FIXTURE = Path(__file__).parent / "fixtures" / "shipments.json"

SYSTEM_PROMPT = (
    "You are a friendly and helpful support agent for Cosmic Freight, an "
    "interplanetary shipping company. Draft a response to the customer's "
    "support ticket. Address the customer by name. Before answering, use the "
    "lookup_shipment tool to check the current status of the shipment "
    "referenced in the ticket and base your response on what it returns."
)

OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_shipment",
            "description": (
                "Look up current status, route, carrier and ETA for a "
                "shipment by its shipment_id."
            ),
            "strict": True,
            "parameters": {
                "type": "object",
                "properties": {"shipment_id": {"type": "string"}},
                "required": ["shipment_id"],
                "additionalProperties": False,
            },
        },
    }
]


def build_user_prompt(ticket: dict) -> str:
    return (
        "Draft a response to this customer support ticket:\n\n"
        f"{json.dumps(ticket, indent=2)}"
    )


def get_open_tickets(num: int) -> list[dict]:
    sample_tickets = [
        {
            "ticket_id": "TKT-30001",
            "customer_name": "Ada Reyes",
            "customer_email": "ada.reyes@example.com",
            "subject": "Cargo to Ceres is delayed",
            "message": (
                "Hi, my container on shipment SHP-1001 to Ceres Depot was due "
                "this week but tracking has not moved in days. My customers "
                "are waiting on these parts. When will it arrive?"
            ),
            "priority": "high",
            "shipment_id": "SHP-1001",
        },
        {
            "ticket_id": "TKT-30002",
            "customer_name": "Bram Okafor",
            "customer_email": "bram.okafor@example.com",
            "subject": "Container arrived damaged",
            "message": (
                "Our lab equipment on shipment SHP-1002 arrived at Europa "
                "Research Station with a cracked casing and two broken "
                "sensor arrays. How do I file a damage claim?"
            ),
            "priority": "high",
            "shipment_id": "SHP-1002",
        },
        {
            "ticket_id": "TKT-30003",
            "customer_name": "Chiara Lindgren",
            "customer_email": "chiara.lindgren@example.com",
            "subject": "Shipment stuck in customs at Mars",
            "message": (
                "Shipment SHP-1003 has shown 'customs hold' at Mars Orbital "
                "for three days. Nobody told us why. What paperwork is "
                "missing and how do we get it released?"
            ),
            "priority": "medium",
            "shipment_id": "SHP-1003",
        },
        {
            "ticket_id": "TKT-30004",
            "customer_name": "Devi Anand",
            "customer_email": "devi.anand@example.com",
            "subject": "Unexpected fuel surcharge on invoice",
            "message": (
                "Our latest invoice for shipment SHP-1004 includes a fuel "
                "surcharge of 240 credits that was not in the quote. Can you "
                "explain this charge or remove it?"
            ),
            "priority": "medium",
            "shipment_id": "SHP-1004",
        },
        {
            "ticket_id": "TKT-30005",
            "customer_name": "Emeka Sato",
            "customer_email": "emeka.sato@example.com",
            "subject": "Tracking says my container is lost",
            "message": (
                "Tracking for shipment SHP-1005 to Phobos Transfer Station "
                "now shows a facility on Deimos?! Is my container lost? I "
                "need an update urgently, the contents are time-sensitive."
            ),
            "priority": "high",
            "shipment_id": "SHP-1005",
        },
    ]
    return random.sample(sample_tickets, num)


def lookup_shipment(shipment_id: str) -> dict:
    """Look up current status, route, carrier and ETA for a shipment by its shipment_id."""
    shipments = json.loads(SHIPMENTS_FIXTURE.read_text())
    return shipments.get(
        shipment_id.strip(),
        {
            "shipment_id": shipment_id,
            "status": "unknown",
            "notes": "No shipment found with this id.",
        },
    )
