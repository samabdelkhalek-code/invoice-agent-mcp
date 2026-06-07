"""
Invoice Agent — MCP Server
===========================
Allows Claude and any MCP-compatible AI to create German invoices
(§14 UStG compliant) via natural language.

Setup in Claude Desktop:
  {
    "mcpServers": {
      "invoice-agent": {
        "command": "python3",
        "args": ["/path/to/server.py"],
        "env": { "INVOICE_API_KEY": "axon_your_key_here" }
      }
    }
  }

Get an API key at: https://invoice.alpen-huettentouren.de/landing
"""

import os
import json
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.getenv("INVOICE_API_URL", "https://invoice.alpen-huettentouren.de")
API_KEY  = os.getenv("INVOICE_API_KEY", "")

mcp = FastMCP(
    name="invoice-agent",
    instructions="""
Du kannst professionelle Rechnungen und Angebote auf Deutsch erstellen.
Alle Rechnungen sind §14 UStG konform mit korrekter MwSt-Berechnung.
Frage nach fehlenden Informationen (Kundenname, Leistung, Preis).
""",
)


def _call(action: str, params: dict) -> dict:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["X-API-Key"] = API_KEY

    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{BASE_URL}/v1/agent-task",
            headers=headers,
            json={"session_id": "mcp-session", "action": action, "params": params},
        )
        resp.raise_for_status()
        return resp.json()


@mcp.tool()
def create_invoice(
    customer_name: str,
    customer_address: str,
    items: str,
    service_date: str = "",
    vat_rate: float = 19.0,
) -> str:
    """
    Create a German invoice (§14 UStG compliant) as PDF.

    Args:
        customer_name: Full name or company name of the customer
        customer_address: Customer address (street, city, zip)
        items: JSON array of items: [{"description": "...", "quantity": 1, "unit": "Stunden", "unit_price": 100.0}]
        service_date: Service date in YYYY-MM-DD format (optional, defaults to today)
        vat_rate: VAT rate in percent (default: 19.0)

    Returns:
        Invoice number, PDF download URL and total amount
    """
    try:
        items_parsed = json.loads(items) if isinstance(items, str) else items
    except json.JSONDecodeError:
        return "Fehler: items muss ein gültiges JSON-Array sein."

    result = _call("create_invoice", {
        "customer": {
            "name": customer_name,
            "address": customer_address,
        },
        "items": items_parsed,
        "service_date": service_date,
        "vat_rate": vat_rate,
    })

    r = result.get("result", {})
    inv_num = r.get("invoice_number", "?")
    total   = r.get("total_gross", "?")
    pdf_url = r.get("pdf_url", "")

    return (
        f"✅ Rechnung {inv_num} erstellt\n"
        f"Betrag: {total} €\n"
        f"PDF: {BASE_URL}{pdf_url}\n"
        f"Compute Units: {result.get('compute_units', '?')}"
    )


@mcp.tool()
def list_invoices(limit: int = 10) -> str:
    """
    List recent invoices.

    Args:
        limit: Maximum number of invoices to return (default: 10)

    Returns:
        List of recent invoices with number, customer, amount and status
    """
    result = _call("list_invoices", {"limit": limit})
    invoices = result.get("result", {}).get("invoices", [])

    if not invoices:
        return "Keine Rechnungen gefunden."

    lines = [f"📋 Letzte {len(invoices)} Rechnungen:\n"]
    for inv in invoices:
        status = "✅" if inv.get("paid") else "⏳"
        lines.append(
            f"{status} {inv.get('invoice_number')} — "
            f"{inv.get('customer_name')} — "
            f"{inv.get('total_gross', '?')} €"
        )
    return "\n".join(lines)


@mcp.tool()
def create_offer(
    customer_name: str,
    customer_address: str,
    items: str,
    valid_days: int = 30,
) -> str:
    """
    Create a German offer/quote (Angebot).

    Args:
        customer_name: Full name or company name of the customer
        customer_address: Customer address
        items: JSON array of items: [{"description": "...", "quantity": 1, "unit": "Stunden", "unit_price": 100.0}]
        valid_days: Offer validity in days (default: 30)

    Returns:
        Offer number and PDF download URL
    """
    try:
        items_parsed = json.loads(items) if isinstance(items, str) else items
    except json.JSONDecodeError:
        return "Fehler: items muss ein gültiges JSON-Array sein."

    result = _call("create_offer", {
        "customer": {
            "name": customer_name,
            "address": customer_address,
        },
        "items": items_parsed,
        "valid_days": valid_days,
    })

    r = result.get("result", {})
    num     = r.get("offer_number", "?")
    total   = r.get("total_gross", "?")
    pdf_url = r.get("pdf_url", "")

    return (
        f"✅ Angebot {num} erstellt\n"
        f"Betrag: {total} €\n"
        f"Gültig: {valid_days} Tage\n"
        f"PDF: {BASE_URL}{pdf_url}"
    )


@mcp.tool()
def get_invoice_status(invoice_number: str) -> str:
    """
    Get the status of a specific invoice.

    Args:
        invoice_number: Invoice number (e.g. RE-2026-001)

    Returns:
        Invoice details including payment status
    """
    result = _call("get_invoice", {"invoice_number": invoice_number})
    r = result.get("result", {})

    if not r:
        return f"Rechnung {invoice_number} nicht gefunden."

    paid = "✅ Bezahlt" if r.get("paid") else "⏳ Offen"
    return (
        f"Rechnung: {r.get('invoice_number')}\n"
        f"Kunde: {r.get('customer_name')}\n"
        f"Betrag: {r.get('total_gross')} €\n"
        f"Status: {paid}\n"
        f"Datum: {r.get('date')}"
    )


if __name__ == "__main__":
    mcp.run()
