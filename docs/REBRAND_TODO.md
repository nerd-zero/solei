# Docs Rebrand TODO

This file tracks items intentionally left unchanged during the Polar → Solei rebrand,
plus items that require external action before they can be updated.

## Intentionally Left Unchanged (SDK not yet renamed)

These items use `@polar-sh` npm packages or `polar-sdk` / `polargo` Python/Go packages.
They should be updated when the SDK packages are published under a new name.

### JavaScript/TypeScript SDK (`@polar-sh/sdk`)
- `import { Polar } from "@polar-sh/sdk"` — class name from upstream package
- `const polar = new Polar({ ... })` — variable name matches class from upstream package
- `import { Webhooks } from "@polar-sh/nextjs"`, `@polar-sh/checkout`, `@polar-sh/ingestion`, etc.
- All `@polar-sh/*` npm package names throughout code examples

### Python SDK (`polar-sdk`)
- `pip install polar-sdk` — PyPI package not yet renamed
- `from polar_sdk import Polar` — import path from upstream package
- `with Polar(` / `polar.` Python method calls

### Go SDK (`polargo`)
- `polargo.New(...)`, `polargo.WithServer(...)`, `polargo.WithSecurity(...)` — Go package not yet renamed

### PHP SDK
- `Polar\Polar::builder()` — PHP namespace from upstream package

## Requires External Action

These are third-party marketplace or integration pages that Nerd Zero needs to
update by creating new listings or contacting the respective platforms.

### Integration pages (still point to old Polar listings)
- **Affonso**: `https://affonso.io/polar-affiliate-program` — needs a new Solei affiliate program page
- **Framer Marketplace**: `https://www.framer.com/marketplace/plugins/polar/` — needs new Solei plugin listing
- **Raycast Store**: `https://www.raycast.com/emilwidlund/polar` — needs new Solei extension listing
- **Zapier**: `https://zapier.com/apps/polar/integrations` — needs new Solei app on Zapier

### MCP endpoints
- `mcp.solei.to/mcp/...` — update once MCP server is live at solei.to domain

## Historical (Changelog)

`docs/changelog/recent.mdx` contains historical changelog entries that reference
`polar_mst_`, `polar_whs_`, and old Polar branding as-they-were at time of writing.
These are left unchanged intentionally as a historical record.
