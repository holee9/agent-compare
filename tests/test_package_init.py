"""Tests for top-level package exports."""

import src


def test_lazy_submodule_export():
    assert src.core is not None
    assert src.pipeline is not None
