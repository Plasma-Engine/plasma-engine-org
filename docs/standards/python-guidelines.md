# Python Implementation Standards

These standards apply to all Python services (e.g., `plasma-engine-gateway`, `plasma-engine-research`, `plasma-engine-brand`). They extend CONTRIBUTING and DevOps docs and are enforced via CI quality gates.

## Language & Runtime
- Python 3.11+ only
- Use `uv` or virtualenv for local dev; pin dev tooling in `requirements-dev.txt`

## Style, Formatting, and Linting
- Formatter: Black (line length 88)
- Linter: Ruff (PEP8, import order, complexity)
- Type checking: MyPy (strict where feasible)
- Docstrings: Google or NumPy style, required for all public functions/classes/modules

Recommended tool commands:
```bash
black --check .
ruff check .
mypy .
```

## Project Structure
- `app/` holds service entrypoints (`main.py`), routers, domain logic
- `app/config.py` centralizes settings (pydantic BaseSettings)
- `tests/` mirrors `app/` layout (unit under `tests/unit`, integration under `tests/integration`)

## Module and File Conventions
- One major responsibility per module; keep files under ~400 lines when possible
- Name modules by domain behavior (`user_repository.py`, `auth_service.py`)

## Imports and Dependencies
- Standard library → third-party → first-party imports, separated by blank lines
- Avoid wildcard imports; import names explicitly
- Keep runtime deps in `requirements.txt`, dev tools in `requirements-dev.txt`

## Type Hints and Contracts
- Annotate all function parameters and return types
- Prefer `typing` Protocols over concrete classes for boundaries
- Use `TypedDict`/`pydantic` models for data contracts

### Example: Service with rigorous comments and types
```python
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ValidationError


class ScoreRequest(BaseModel):
    """
    Input schema for score calculation requests.

    This model validates inputs at the boundary (e.g., FastAPI request body),
    ensuring downstream code can assume shape and types.
    """

    values: List[float] = Field(..., description="Data points to score")
    # Optional weights allow customized scoring; when omitted, equal weights apply
    weights: Optional[List[float]] = Field(
        None, description="Optional per-value weights; must match values length if provided"
    )


def calculate_weighted_score(values: List[float], weights: Optional[List[float]]) -> float:
    """
    Calculate a weighted score from a list of values.

    Args:
        values: Numeric values representing observations.
        weights: Optional per-value weights; if None, uses uniform weights.

    Returns:
        Weighted average in the inclusive range [min(values), max(values)].

    Raises:
        ValueError: When `weights` length does not match `values`.

    Notes:
        - This function deliberately avoids side effects and I/O to keep it unit-testable.
        - Validation of input shape is performed here as a guard clause to fail fast.
    """

    if not values:
        # Guard clause: empty input produces a clear failure early
        raise ValueError("values must not be empty")

    if weights is None:
        # Default to uniform weights for simplicity and predictability
        weights = [1.0] * len(values)

    if len(values) != len(weights):
        # Input contract violation: lengths must match
        raise ValueError("values and weights must have the same length")

    total_weight = sum(weights)
    if total_weight == 0:
        # Prevent division by zero and undefined semantics
        raise ValueError("sum of weights must be non-zero")

    weighted_sum = sum(v * w for v, w in zip(values, weights))
    return weighted_sum / total_weight


def score_endpoint(payload: Dict) -> Dict:
    """
    Example endpoint handler demonstrating boundary validation, pure core logic,
    and structured error reporting. In real services, this would be a FastAPI
    route handler with `ScoreRequest` as the request model.
    """
    try:
        request = ScoreRequest(**payload)
        score = calculate_weighted_score(request.values, request.weights)
        return {"score": score}
    except ValidationError as ve:
        # Surface schema errors with actionable messages for clients
        return {"error": "validation_error", "details": ve.errors()}
    except ValueError as ve:
        # Input contract issue; message is safe to expose
        return {"error": "invalid_input", "message": str(ve)}
    except Exception:
        # Never leak internals in production paths; log the full exception instead
        return {"error": "internal_error"}
```

## Error Handling
- Fail fast with guard clauses
- Never expose stack traces to clients; log with correlation IDs
- Use domain-specific error types when helpful

## Logging
- Use structured logging (JSON) and include `trace_id`/`span_id` if available
- Avoid logging secrets or PII

## Configuration & Secrets
- Use `pydantic-settings` for env-driven configuration
- Never commit secrets; leverage platform secret stores and `.env` only for local

## Testing
- Unit tests cover pure functions and small units; no network/filesystem by default
- Integration tests use Testcontainers or docker-compose for external deps
- E2E tests run via API-level workflows (possibly in TS) against ephemeral stacks
- Coverage target: ≥ 80% for new/changed code; block PRs if lower

### Example: Parametrized unit test with tight scope
```python
import pytest

from app.scoring import calculate_weighted_score


@pytest.mark.parametrize(
    "values,weights,expected",
    [
        ([1.0, 2.0, 3.0], None, 2.0),  # uniform weights fallback
        ([1.0, 2.0, 3.0], [0.2, 0.3, 0.5], 2.3),
    ],
)
def test_calculate_weighted_score(values, weights, expected):
    # Unit-level: no external I/O, deterministic inputs
    assert calculate_weighted_score(values, weights) == pytest.approx(expected)


def test_calculate_weighted_score_invalid_lengths():
    # Guard clause must raise clear errors for contract violations
    with pytest.raises(ValueError):
        calculate_weighted_score([1.0, 2.0], [1.0])
```

## Documentation & Comments
- Add module-level overview at top of each file explaining purpose and key abstractions
- Provide concise comments for non-obvious logic; explain “why”, not “what”
- Include examples in docstrings when behavior is subtle

## Security
- Input validation at boundaries (FastAPI models)
- Use parameterized queries; never build SQL strings directly
- Follow OWASP Top 10 and ASVS controls (auth, session, data protection)

## Performance
- Prefer async I/O for network-bound tasks (FastAPI, httpx)
- Avoid premature optimization; add benchmarks where performance is critical

## Review Checklist (Python)
- Types annotated; MyPy clean
- Black, Ruff clean
- Public APIs documented with docstrings and examples where useful
- Unit/integration tests updated; coverage ≥ 80%
- No secrets or sensitive data in code or logs

