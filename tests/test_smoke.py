"""Smoke test: the package imports cleanly."""


def test_import():
    import deepseek_deharness

    assert deepseek_deharness.__version__ == "0.1.0"
