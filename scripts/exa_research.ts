#!/usr/bin/env -S node --loader ts-node/esm
/**
 * Exa Research Helper (Stub)
 *
 * Purpose:
 * - Demonstrate how to call Exa's API using an API key from env.
 * - Provide commented structure for future expansion.
 *
 * TODO:
 * - Confirm endpoint paths and request schema via Rube MCP.
 */

import fetch from 'node-fetch';

async function main(): Promise<void> {
  const apiKey = process.env.EXA_API_KEY;
  if (!apiKey) {
    console.error('Missing EXA_API_KEY in environment');
    process.exit(2);
  }

  const endpoint = process.env.EXA_ENDPOINT || 'https://api.exa.ai/v1/search'; // TODO confirm
  const body = {
    query: 'example search query',
    size: 5,
  };

  const res = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const text = await res.text();
    console.error('Request failed', res.status, text);
    process.exit(1);
  }

  const data = await res.json();
  console.log(JSON.stringify(data, null, 2));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});