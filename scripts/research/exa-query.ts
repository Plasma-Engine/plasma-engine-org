#!/usr/bin/env -S node --loader ts-node/esm
/**
 * Explainer: TypeScript research script that will query Exa once official
 * schemas are synced. Includes thorough inline commentary.
 *
 * Usage:
 *   EXA_API_KEY=... ts-node scripts/research/exa-query.ts "query string"
 *
 * Notes:
 *   - Uses fetch API available in Node 18+. Replace endpoints after MCP sync.
 */

const apiKey = process.env.EXA_API_KEY || "";
if (!apiKey) {
  console.error("EXA_API_KEY is not set. See docs/exa/auth.md");
  process.exit(2);
}

const query = process.argv[2];
if (!query) {
  console.error("Usage: exa-query.ts <query>");
  process.exit(2);
}

function buildUrl(q: string): string {
  const params = new URLSearchParams({ q });
  return `https://api.exa.example.invalid/search?${params.toString()}`;
}

async function main(): Promise<void> {
  const url = buildUrl(query);
  console.log(`[exa] GET ${url}`);
  try {
    const resp = await fetch(url, {
      headers: { Authorization: `Bearer ${apiKey}` },
    });
    if (!resp.ok) {
      throw new Error(`HTTP ${resp.status}`);
    }
    const data = await resp.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (err) {
    console.error(`Request failed: ${String(err)}\n# TODO: Update endpoint once schema is synced.`);
    process.exit(1);
  }
}

void main();

