### Exa API quick reference (auth, rate limits, query syntax)

Status: Initial. Some details require confirmation against upstream docs; see `docs/exa/gaps.md`.

Authentication
- Header: `Authorization: Bearer <EXA_API_KEY>`
- Obtain API key from Exa dashboard: `https://dashboard.exa.ai`

Base URL (REST)
- Likely: `https://api.exa.ai` (verify)

Common endpoints (to verify)
- `POST /search`: semantic/web search; parameters include query, type, result count, time filters
- `POST /answers` or `POST /qa`: generate answers grounded in search results
- `GET /contents/{id}`: fetch cached content/snippet by identifier

Rate limits
- Not documented in mirrored pages. Capture from official docs when available.

CLI/SDKs
- Python SDK (`exa-py`): `pip install exa-py` (verify name); typical usage:

```python
# Requires EXA_API_KEY in environment or pass explicitly
from exa import Exa

client = Exa(api_key="<EXA_API_KEY>")
resp = client.search(query="vector databases production readiness", num_results=5)
for item in resp.results:
    print(item.url, item.title)
```

- JavaScript SDK (`exa-js`): `npm i exa-js` (verify name); example:

```javascript
import { Exa } from "exa"; // verify package name

const client = new Exa(process.env.EXA_API_KEY);
const resp = await client.search({ query: "retrieval augmented generation" , numResults: 5 });
console.log(resp.results.map(r => r.url));
```

HTTP example (curl)

```bash
curl -sS -X POST "https://api.exa.ai/search" \
  -H "Authorization: Bearer $EXA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "query": "site reliability engineering slos",
        "numResults": 5
      }'
```

Notes
- Preserve and attribute any vendored examples in `third_party/exa/`.
- Treat all TBDs as blocking for production usage; see gaps log for follow-up.

