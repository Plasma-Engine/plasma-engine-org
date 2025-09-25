<!--
Explainer: Authentication flows for Exa API. Replace placeholders after
verifying with official docs via Rube MCP.
-->

# Authentication

## API Key (Bearer)
- Set environment variable `EXA_API_KEY` with a key provisioned in Exa.
- Send header `Authorization: Bearer $EXA_API_KEY`.

## Environment Setup
```bash
export EXA_API_KEY="<redacted>" # TODO: Store in secrets manager for CI
```

## References
- # TODO: Insert authoritative Exa docs link and version

