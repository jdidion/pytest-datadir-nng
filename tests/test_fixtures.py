"""Integration tests that exercise the live ``datadir`` and ``datadir_copy``
fixtures against the real pytest fixture machinery.

These complement ``test_datadir.py`` (which unit-tests path resolution with a
mocked ``request``) by driving the fixtures end to end: fixture wiring, the
copy-on-access behaviour of ``datadir_copy`` (both files and directories), the
``/`` operator, and the ``KeyError`` raised for a missing resource.

Resources live under ``tests/data/test_fixtures/`` so the fixture's search path
(keyed on this module's name) resolves to them.
"""

from pathlib import Path

import pytest


def test_datadir_returns_existing_path(datadir):
    path = datadir["global.txt"]
    assert isinstance(path, Path)
    assert path.exists()
    assert path.read_text() == "global resource\n"


def test_datadir_truediv_operator(datadir):
    via_getitem = datadir["global.txt"]
    via_div = datadir / "global.txt"
    assert via_getitem == via_div


def test_datadir_missing_resource_raises_keyerror(datadir):
    with pytest.raises(KeyError) as excinfo:
        datadir["does-not-exist.txt"]
    # The message should name the missing resource and list the searched dirs.
    assert "does-not-exist.txt" in str(excinfo.value)


def test_datadir_copy_copies_file_and_is_writable(datadir, datadir_copy):
    copied = datadir_copy["copyable.txt"]
    assert copied.exists()
    assert copied.read_text() == "copy me\n"

    # The copy must live in the tmp dir, not in the source tree, and editing
    # it must not touch the original resource. Resolve the original through the
    # read-only ``datadir`` fixture so the assertion does not depend on cwd.
    original = datadir["copyable.txt"]
    assert copied != original
    copied.write_text("mutated")
    assert copied.read_text() == "mutated"
    assert original.read_text() == "copy me\n"


def test_datadir_copy_fresh_copy_each_access(datadir_copy):
    first = datadir_copy["copyable.txt"]
    first.write_text("changed")
    # Re-requesting via the dict notation must overwrite with a fresh copy
    # (documented caveat); ``first`` and ``second`` are the same path but the
    # second access restores the original contents.
    second = datadir_copy["copyable.txt"]
    assert second.read_text() == "copy me\n"


def test_datadir_copy_copies_directory_tree(datadir_copy):
    copied_dir = datadir_copy["a_dir"]
    assert copied_dir.is_dir()
    nested = copied_dir / "nested.txt"
    assert nested.exists()
    assert nested.read_text() == "nested file\n"


def test_datadir_copy_missing_resource_raises_keyerror(datadir_copy):
    with pytest.raises(KeyError):
        datadir_copy["nope.txt"]


class TestClassScope:
    """Exercise the class-name branch of the search-path construction."""

    def test_class_scoped_resource(self, datadir):
        path = datadir["class_resource.txt"]
        assert path.exists()
        assert path.read_text() == "class-scoped resource\n"

    def test_class_can_still_reach_module_resource(self, datadir):
        # Falls through the class/method dirs to the module-level resource.
        path = datadir["global.txt"]
        assert path.read_text() == "global resource\n"
