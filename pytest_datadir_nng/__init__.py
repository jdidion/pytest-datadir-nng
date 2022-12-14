# "datadir" fixtures for pytest.
#
# Copyright (c) 2015, Tilman Blumenbach
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
from pathlib import Path
import pytest
import shutil
from typing import Union


PathArg = Union[str, Path]


class _Datadir:
    def __init__(self, request: pytest.FixtureRequest):
        basedir = request.path.parent
        datadir = basedir / "data"

        self._datadirs = []

        for d in (basedir, datadir):
            testdir = d / request.module.__name__
            if request.cls is not None:
                clsdir = testdir / request.cls.__name__
                self._datadirs.extend([clsdir / request.function.__name__, clsdir])
            else:
                self._datadirs.append(testdir / request.function.__name__)
            self._datadirs.append(testdir)
        self._datadirs.append(datadir)

    def __getitem__(self, path: PathArg) -> Path:
        for datadir in self._datadirs:
            datadir_path = datadir / path
            if datadir_path.exists():
                return datadir_path
        else:
            raise KeyError(
                f"File `{path}' not found in any of the following datadirs: {self._datadirs}"
            )

    def __truediv__(self, path) -> Path:
        return self.__getitem__(path)


class _DatadirCopy(_Datadir):
    def __init__(self, request: pytest.FixtureRequest, tmpdir: Path):
        super().__init__(request)
        self._tmpdir = tmpdir

    def __getitem__(self, path: PathArg) -> Path:
        datadir_path = super().__getitem__(path)
        copied_path = self._tmpdir / path
        copied_path.parent.mkdir(parents=True, exist_ok=True)
        if datadir_path.is_dir():
            shutil.copytree(datadir_path, copied_path)
        else:
            shutil.copy2(datadir_path, copied_path)

        return copied_path


@pytest.fixture(scope="function")
def datadir(request):
    """
    Provides a "datadir" fixture which allows test functions to
    easily access resources in data directories. It was inspired
    by the `pytest-datadir plugin
    <https://github.com/gabrielcnr/pytest-datadir>`_.

    The "datadir" fixture behaves like a dictionary. Currently,
    only retrieving items using the ``d[key]`` syntax is supported.
    Things like iterators, ``len(d)`` etc. are not.

    How the fixture looks for resources is best described by an example.
    Let us assume the following directory structure for your tests:

    .. code-block:: none

        tests/
        +-- test_one.py
        +-- test_two.py
        +-- data/
        |   +-- global.dat
        +-- test_one/
        |   +-- test_func/
        |       +-- data.txt
        +-- test_two/
            +-- TestClass/
                +-- test_method/
                    +-- strings.prop

    The file ``test_one.py`` contains the following function::

        def test_func(datadir):
            data_path = datadir["data.txt"]

            # ...

    The file ``test_two.py`` contains the following class::

        class TestClass(object):
            def test_method(self, datadir):
                strings_path = datadir["strings.prop"]

                # ...

    When the ``test_func()`` function asks for the ``data.txt`` resource, the
    following directories are searched for a file or directory named ``data.txt``,
    in this order:

    - ``tests/test_one/test_func/``
    - ``tests/test_one/``
    - ``tests/data/test_one/test_func/``
    - ``tests/data/test_one/``
    - ``tests/data/``

    The path to the first existing file (or directory) is returned as a
    :class:`pathlib.Path` object. In this case, the returned path would be
    ``tests/test_one/test_func/data.txt``.

    When the ``test_method()`` method asks for the ``strings.prop`` resource,
    the following directories are searched for a file or directory with the name
    ``strings.prop``, in this order:

    - ``tests/test_two/TestClass/test_method/``
    - ``tests/test_two/TestClass/``
    - ``tests/test_two/``
    - ``tests/data/test_two/TestClass/test_method/``
    - ``tests/data/test_two/TestClass/``
    - ``tests/data/test_two/``
    - ``tests/data/``

    Here, this would return the path
    ``tests/test_two/TestClass/test_method/strings.prop``.

    As you can see, the searched directory hierarchy is slighly different if a
    *method* instead of a *function* asks for a resource. This allows you to
    load different resources based on the name of the test class, if you wish.

    Finally, if a test function or test method would ask for a resource named
    ``global.dat``, then the resulting path would be ``tests/data/global.dat``
    since no other directory in the searched directory hierarchy contains
    a file named ``global.dat``. In other words, the ``tests/data/`` directory
    is the place for global (or fallback) resources.

    If a resource cannot be found in *any* of the searched directories, a
    :class:`KeyError` is raised.
    """
    return _Datadir(request)


@pytest.fixture(scope="function")
def datadir_copy(request, tmpdir):
    """
    Similar to the :func:`.datadir` fixture, but copies the requested resources to a temporary
    directory first so that test functions or methods can modify their resources on-disk without
    affecting other test functions and methods.

    Each test function or method gets its own temporary directory and thus its own fresh copies of
    the resources it requests.

    **Caveat:** Each time a resource is requested using the dictionary notation, a fresh copy of
    the resource is made. This also applies if a test function or method requests the same resource
    multiple times. Thus, if you modify a resource and need to access the *modified* version of the
    resource later, save its path in a variable and use that variable to access the resource later
    instead of using the dictionary notation multiple times::

        def test_foo(datadir_copy):
            # This creates the initial fresh copy of data.txt and saves
            # its path in the variable "resource1".
            resource1 = datadir_copy["data.txt"]

            # ...modify resource1 on-disk...

            # You now want to access the modified version of data.txt.

            # WRONG way: This will overwrite your modified version of the
            #            resource with a fresh copy!
            fh = datadir_copy["data.txt"].open("rb")

            # CORRECT way: This will let you access the modified version
            #              of the resource.
            fh = resource1.open("rb")
    """
    return _DatadirCopy(request, tmpdir)
