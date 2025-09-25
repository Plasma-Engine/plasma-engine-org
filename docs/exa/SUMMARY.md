<!--
Explainer: Endpoint summaries for Exa API with pointers to schemas and source citations.
Replace placeholder fields after verification via Rube MCP.
-->

## Endpoints Overview

### Search
- Schema: `schemas/exa-search.schema.json`, `schemas/exa-search.schema.yaml`
- Purpose: Full-text and semantic search across indexed web content.
- Key fields (placeholder): `query`, `numResults`, `includeDomains`, `excludeDomains`, `useAutoprompt`.
- Source: `https://docs.exa.ai/reference/search` (TODO: verify and cite exact URL)

### Answers
- Schema: `schemas/exa-answers.schema.json`, `schemas/exa-answers.schema.yaml`
- Purpose: Direct answer generation grounded in search results.
- Key fields (placeholder): `question`, `numResults`, `citationStyle`, `returnSources`.
- Source: `https://docs.exa.ai/reference/answers` (TODO: verify and cite exact URL)

### Find Similar
- Schema: `schemas/exa-find-similar.schema.json`, `schemas/exa-find-similar.schema.yaml`
- Purpose: Find content similar to a given URL or document.
- Key fields (placeholder): `url`, `query`, `numResults`.
- Source: `https://docs.exa.ai/reference/find-similar` (TODO: verify and cite exact URL)

### Content Retrieval (if available)
- Schema: `schemas/exa-content.schema.json`, `schemas/exa-content.schema.yaml`
- Purpose: Retrieve extracted content for a given URL/doc id.
- Key fields (placeholder): `id`, `url`, `includeHtml`, `includeExtractedText`.
- Source: `https://docs.exa.ai/reference/content` (TODO: verify and cite exact URL)

