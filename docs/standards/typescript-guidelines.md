# TypeScript Implementation Standards

These standards apply to Node/TS codebases (e.g., `plasma-engine-content`, `plasma-engine-agent`, gateway frontends if applicable). They extend CONTRIBUTING and DevOps docs and are enforced via CI quality gates.

## Language & Runtime
- TypeScript 5.x, Node.js 20+
- `"strict": true` in `tsconfig.json`
- Target modern ES2022+; moduleResolution `node`

## Style, Formatting, and Linting
- Linter: ESLint (typescript-eslint recommended + security plugins)
- Formatter: Prettier (single source of formatting truth)
- Types: Prefer explicit function signatures for module exports

Recommended commands:
```bash
npm run lint
npm run format:check
npm run typecheck
```

## Project Structure
- `src/` for implementation, `tests/` for test code
- Public API surfaces via `src/index.ts`
- Separate app entrypoint from library code

## Imports and Modules
- Use path aliases sparingly; avoid deep relative paths by organizing modules well
- No default exports for shared libraries; prefer named exports
- Import types using `import type { Foo } from '...'` when possible

## Types and Contracts
- Model external data with Zod or io-ts for runtime validation
- Use discriminated unions for state machines and variant responses
- Avoid `any`. Use `unknown` plus safe narrowing when necessary

### Example: Service with rigorous comments and types
```ts
import { z } from 'zod';

// Input schema validating external data at runtime
export const ScoreRequestSchema = z.object({
  values: z.array(z.number()).min(1, 'values must not be empty'),
  // Optional weights must match values length if provided
  weights: z.array(z.number()).optional(),
});

export type ScoreRequest = z.infer<typeof ScoreRequestSchema>;

/**
 * Calculate a weighted score from values.
 * - Pure function: no I/O, deterministic
 * - Guards: validate lengths and non-zero weights sum
 */
export function calculateWeightedScore(values: number[], weights?: number[]): number {
  if (values.length === 0) {
    throw new Error('values must not be empty');
  }

  const effectiveWeights = weights ?? Array(values.length).fill(1);
  if (values.length !== effectiveWeights.length) {
    // Input contract violation: lengths must match
    throw new Error('values and weights must have the same length');
  }

  const totalWeight = effectiveWeights.reduce((acc, w) => acc + w, 0);
  if (totalWeight === 0) {
    throw new Error('sum of weights must be non-zero');
  }

  const weightedSum = values.reduce((acc, v, i) => acc + v * effectiveWeights[i], 0);
  return weightedSum / totalWeight;
}

/**
 * Example endpoint-like boundary showing schema validation and safe error mapping.
 */
export function scoreHandler(payload: unknown): { score?: number; error?: string } {
  const parse = ScoreRequestSchema.safeParse(payload);
  if (!parse.success) {
    return { error: 'validation_error' }; // do not leak parse details to clients
  }

  try {
    const { values, weights } = parse.data;
    const score = calculateWeightedScore(values, weights);
    return { score };
  } catch (e) {
    return { error: 'invalid_input' };
  }
}
```

## Error Handling
- Use error classes for domain errors; avoid throwing strings
- Map internal errors to safe client messages; log full details with context IDs

## Logging
- Use a structured logger (pino/winston) in JSON mode
- Redact secrets (tokens, credentials) at logger configuration level

## Configuration & Secrets
- Read configuration from env; validate with Zod at startup
- Never commit secrets; use platform secrets and `.env` only for local

## Testing
- Unit: Vitest/Jest with ts-node or ts-jest
- Integration: Testcontainers or docker-compose for external deps
- E2E: Playwright against ephemeral environments
- Coverage target: ≥ 80% for new/changed code; block PRs if lower

### Example: Focused unit tests
```ts
import { describe, it, expect } from 'vitest';
import { calculateWeightedScore } from '../src/score';

describe('calculateWeightedScore', () => {
  it('uses uniform weights when none provided', () => {
    expect(calculateWeightedScore([1, 2, 3])).toBeCloseTo(2.0);
  });

  it('respects custom weights', () => {
    expect(calculateWeightedScore([1, 2, 3], [0.2, 0.3, 0.5])).toBeCloseTo(2.3);
  });

  it('throws on length mismatch', () => {
    expect(() => calculateWeightedScore([1, 2], [1])).toThrow();
  });
});
```

## Security
- Validate all external inputs (Zod schemas)
- Use parameterized queries; never build SQL strings directly
- Adopt OWASP ASVS controls and Node.js Security WG recommendations

## Performance
- Prefer async, streaming, and backpressure-aware patterns for I/O
- Avoid blocking the event loop; isolate CPU-bound work

## Review Checklist (TypeScript)
- ESLint, Prettier clean
- No `any` in public APIs; types are explicit
- Input schemas defined and validated at boundaries
- Tests and coverage ≥ 80%
- No secrets or sensitive data in code or logs