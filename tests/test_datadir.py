from pathlib import Path
from pytest_datadir_nng import _Datadir
from unittest.mock import MagicMock


def test_datadir_paths():
    request = MagicMock()
    basedir = Path("tests")
    datadir = basedir / "data"
    request.path.parent = basedir

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


def test_resolve():
    basedir = Path("tests")
    datadir = basedir / "data"
    request = MagicMock()
    request.path.parent = basedir

    # tests.test_module.TestClass.test_method
    request.module.__name__ = "test_module"
    request.cls.__name__ = "TestClass"
    request.function.__name__ = "test_method"
    d = _Datadir(request)
    assert d["data.txt"] == d / "data.txt" == datadir / "data.txt"
    assert d["module.txt"] == d / "module.txt" == datadir / "test_module" / "module.txt"
    assert (
        d["module_class.txt"]
        == d / "module_class.txt"
        == datadir / "test_module" / "TestClass" / "module_class.txt"
    )
    assert (
        d["module_class_method.txt"]
        == d / "module_class_method.txt"
        == datadir
        / "test_module"
        / "TestClass"
        / "test_method"
        / "module_class_method.txt"
    )

    # tests.test_module.test_function
    request.module.__name__ = "test_module"
    request.cls = None
    request.function.__name__ = "test_function"
    d = _Datadir(request)
    assert d["data.txt"] == d / "data.txt" == datadir / "data.txt"
    assert d["module.txt"] == d / "module.txt" == datadir / "test_module" / "module.txt"
    assert (
        d["module_function.txt"]
        == d / "module_function.txt"
        == datadir / "test_module" / "test_function" / "module_function.txt"
    )
