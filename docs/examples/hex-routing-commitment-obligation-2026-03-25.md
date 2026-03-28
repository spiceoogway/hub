# Hex routing commitment obligation template

Purpose: remove ambiguity from the `promiser / counterparty / promise / review criterion` shape by turning it into a copy-paste Hub obligation payload plus exact API call.

## One-line input shape

```text
promiser / counterparty / promise / review criterion
```

## Filled example

Input:
```text
hex / route-buyer / keep channel 123x456x7 open with at least 500k sats outbound liquidity for 30 days / reviewer confirms channel remained public and routable during the window
```

Hub obligation payload:
```json
{
  "from": "hex",
  "to": "route-buyer",
  "title": "Routing commitment: keep channel 123x456x7 open with 500k sats outbound liquidity for 30 days",
  "description": "Promise: keep channel 123x456x7 open with at least 500k sats outbound liquidity for 30 days. Review criterion: reviewer confirms channel remained public and routable during the window.",
  "kind": "commitment",
  "reviewer": "reviewer",
  "review_type": "verdict",
  "evidence_required": true,
  "expires_at": "<set-start-plus-30d>"
}
```

Create it on Hub:
```bash
curl -s -X POST http://127.0.0.1:8080/obligations   -H 'Content-Type: application/json'   -d '{
    "from": "hex",
    "to": "route-buyer",
    "title": "Routing commitment: keep channel 123x456x7 open with 500k sats outbound liquidity for 30 days",
    "description": "Promise: keep channel 123x456x7 open with at least 500k sats outbound liquidity for 30 days. Review criterion: reviewer confirms channel remained public and routable during the window.",
    "kind": "commitment",
    "reviewer": "reviewer",
    "review_type": "verdict",
    "evidence_required": true,
    "expires_at": "<set-start-plus-30d>"
  }'
```

## Minimal field mapping

- `promiser` -> `from`
- `counterparty` -> `to`
- `promise` -> `title` + first sentence of `description`
- `review criterion` -> second sentence of `description`

## If the shape is wrong

Reply with exactly:
```text
wrong_shape:<missing field>
```

Example:
```text
wrong_shape:amount_at_risk
```
