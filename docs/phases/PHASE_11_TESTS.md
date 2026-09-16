# Phase 11 — Tests

## Goal
Review and expand all unit and API tests, verify 80%+ line coverage, ensure no live API calls in default test run.

## Files to create or modify
- `backend/tests/conftest.py` — Update shared fixtures
- `backend/tests/unit/test_config.py` — Expand config tests
- `backend/tests/unit/test_exceptions.py` — Expand exception tests
- `backend/tests/unit/test_logging.py` — Expand logging tests
- `backend/tests/unit/test_parser.py` — Expand parser tests
- `backend/tests/unit/test_chunker.py` — Expand chunker tests
- `backend/tests/unit/test_embedder.py` — Expand embedder tests
- `backend/tests/unit/test_vectorstore.py` — Expand vectorstore tests
- `backend/tests/unit/test_retriever.py` — Expand retriever tests
- `backend/tests/unit/test_generator.py` — Expand generator tests
- `backend/tests/unit/test_storage.py` — Expand storage tests
- `backend/tests/unit/test_llm_base.py` — Expand LLM base tests
- `backend/tests/unit/test_llm_groq.py` — Expand Groq adapter tests
- `backend/tests/unit/test_llm_opencode_zen.py` — Expand OpenCode Zen adapter tests
- `backend/tests/api/test_auth.py` — Expand auth endpoint tests
- `backend/tests/api/test_documents.py` — Expand document endpoint tests
- `backend/tests/api/test_query.py` — Expand query endpoint tests
- `backend/tests/api/test_chats.py` — Expand chat endpoint tests

## Interfaces to define
No new interfaces. This phase reviews and expands existing tests.

## Tests required

### Unit tests (expand existing)
- Test edge cases: empty inputs, None values, missing fields
- Test error paths: invalid file types, missing chunks, failed embeddings
- Test concurrent operations: multiple uploads, multiple queries

### API tests (expand existing)
- Test all error codes: 400, 401, 404, 409, 500, 502
- Test response shapes match API.md specification
- Test cross-endpoint workflows: upload → query → delete

### Coverage
- Run `uv run pytest --cov=app --cov-report=term-missing`
- Verify 80%+ line coverage
- Identify and fix low-coverage areas

### Live tests
- Mark live tests with `@pytest.mark.live`
- Verify live tests are skipped in default run
- Document how to run live tests

## Manual verification
```bash
cd backend

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=term-missing

# Run unit tests only
uv run pytest tests/unit/

# Run API tests only
uv run pytest tests/api/

# Run live tests (requires API keys)
uv run pytest -m live
```

Expected: All tests pass, 80%+ coverage.

## Definition of Done
- [ ] All unit tests expanded with edge cases
- [ ] All API tests expanded with error codes
- [ ] Coverage report shows 80%+ line coverage
- [ ] No live API calls in default test run
- [ ] Live tests marked with @pytest.mark.live
- [ ] All tests pass

## Evidence to record
- Paste coverage report in `docs/agent/PROGRESS.md`
- Update `docs/agent/TRACKER.md` with DONE status

## If blocked
- Report: which test fails, which module has low coverage
- Report to: human

## Do NOT
- Do not add new features
- Do not change existing behavior
- Do not modify production code (only tests)
