# Invoice Agent — MCP Server

> Create German invoices (§14 UStG) via Claude or any MCP-compatible AI. Just describe the invoice in natural language.

[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## What it does

Talk to Claude naturally:

> *"Create an invoice for Müller GmbH, 2 days consulting at €800/day"*

→ Claude creates a §14 UStG compliant PDF invoice in seconds.

## Tools available

| Tool | Description |
|------|-------------|
| `create_invoice` | Create a new German invoice as PDF |
| `list_invoices` | List recent invoices with status |
| `create_offer` | Create a quote/offer (Angebot) |
| `get_invoice_status` | Check if an invoice was paid |

## Setup (Claude Desktop)

1. **Get an API key** at [invoice.alpen-huettentouren.de/landing](https://invoice.alpen-huettentouren.de/landing)

2. **Install dependencies:**
```bash
pip install mcp httpx
```

3. **Add to Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "invoice-agent": {
      "command": "python3",
      "args": ["/path/to/invoice-agent-mcp/server.py"],
      "env": {
        "INVOICE_API_KEY": "axon_your_key_here"
      }
    }
  }
}
```

4. **Restart Claude Desktop** → the invoice tools are now available.

## Example prompts

- *"Erstelle eine Rechnung für Cloudflake GmbH, 3 Stunden KI-Beratung à 200€"*
- *"Show me my last 5 invoices"*
- *"Create an offer for Stefan Kießling for a 2-day workshop at €1,600/day"*
- *"Is invoice RE-2026-003 paid?"*

## Pricing

Plans starting at **€9/month** → [Get started](https://invoice.alpen-huettentouren.de/landing)

## Powered by

- [AXON Protocol](https://github.com/samabdelkhalek-code/axon-protocol) — Agent-to-agent payments on SUI blockchain
- §14 UStG compliant invoice generation
- Hosted on Hetzner (Germany 🇩🇪)
