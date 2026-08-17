"""deepseek-deharness: a monolithic agent harness.

One flat program: loop + tools + session + llm-adapter as plain functions.
No plugin layer, no DI container. Organized by the four algebra:
  - inner spoke: work + trajectory
  - outer spoke: append-only log reconciliation
"""

__version__ = "0.1.0"
