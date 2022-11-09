from pathlib import Path
from pytest_datadir_nng import _Datadir
from unittest.mock import MagicMock


def test_datadir():
    request = MagicMock()
    basedir = Path("tests")
    datadir = basedir / "data"
    request.path = basedir

    # tests.test_module.TestClass.test_method
    request.module.__name__ = "test_module"
    request.cls.__name__ = "TestClass"
    request.function.__name__ = "test_method"
    d = _Datadir(request)
    assert d._datadirs == [
        basedir / "test_module" / "TestClass" / "test_method",
        basedir / "test_module" / "TestClass",
        basedir / "test_module",
        datadir / "test_module" / "TestClass" / "test_method",
        datadir / "test_module" / "TestClass",
        datadir / "test_module",
        datadir,
    ]

    # tests.test_module.test_function
    request.module.__name__ = "test_module"
    request.cls = None
    request.function.__name__ = "test_function"
    d = _Datadir(request)
    assert d._datadirs == [
        basedir / "test_module" / "test_function",
        basedir / "test_module",
        datadir / "test_module" / "test_function",
        datadir / "test_module",
        datadir,
    ]
