# TICKET-001: HTTP transport integration test (mocked urllib)

**Cycle:** 2
**Status:** DONE
**File:** tests/test_http_transport.py

## What
Added an integration test that drives call_llm through the *default*
transport (_default_transport, which uses urllib.request), mocking only
urllib.request.urlopen. This proves the adapter works end-to-end without
hitting a real LLM: correct URL, method, headers (Content-Type,
Authorization Bearer), JSON body shape (model/messages/tools), and response
parsing into {content, tool_calls, usage}.

## Tests (4)
- test_default_transport_posts_correct_request_and_parses
- test_default_transport_content_only
- test_default_transport_is_the_real_urllib_path
- test_default_transport_reads_env_defaults

Stdlib only (urllib, json, unittest.mock). No new dependencies.
