# datadir-nng plugin for pytest

[![pypi-badge](https://img.shields.io/pypi/v/pytest-datadir-nng.svg?)](https://pypi.python.org/pypi/pytest-datadir-nng)

The `datadir-nng` plugin for [pytest](http://pytest.org/) provides the
`datadir` and `datadir_copy` fixtures which allow test functions to
easily access resources in data directories. It was forked from the
[pytest-datadir-ng plugin](https://github.com/Tblue/pytest-datadir-ng)
and updates the code to use `pathlib.Path` rather than `py.path.local`
and to support modern python versions (hence the \"nng\" part in its name 
\-- as in \"*next* next generation\").

This plugin provides two fixtures:

-   The [datadir](#datadir) fixture allows test functions and methods to
    access resources in so-called \"data directories\".
-   The [datadir_copy](#datadir_copy) fixture is similar to the
    [datadir](#datadir) fixture, but it copies the requested resources
    to a temporary directory first so that test functions or methods can
    modify their resources on-disk without affecting other test
    functions and methods.

# Installation

Just do:

    pip install pytest-datadir-nng

# The datadir fixture

The \"datadir\" fixture allows test functions and methods to access
resources in so-called \"data directories\".

The fixture behaves like a dictionary. Currently, only retrieving items
using the `d[key]` syntax is supported. Things like iterators, `len(d)`
etc. are not.

How the fixture looks for resources is best described by an example. Let
us assume the following directory structure for your tests:

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

The file `test_one.py` contains the following function:

``` python
def test_func(datadir):
    data_path = datadir["data.txt"]

    # ...
```

The file `test_two.py` contains the following class:

``` python
class TestClass:
    def test_method(self, datadir):
        strings_path = datadir["strings.prop"]

        # ...
```

When the `test_func()` function asks for the `data.txt` resource, the
following directories are searched for a file or directory named
`data.txt`, in this order:

-   `tests/test_one/test_func/`
-   `tests/test_one/`
-   `tests/data/test_one/test_func/`
-   `tests/data/test_one/`
-   `tests/data/`

The path to the first existing file (or directory) is returned as a
`pathlib.Path` object. In this case, the returned path would be
`tests/test_one/test_func/data.txt`.

When the `test_method()` method asks for the `strings.prop` resource,
the following directories are searched for a file or directory with the
name `strings.prop`, in this order:

-   `tests/test_two/TestClass/test_method/`
-   `tests/test_two/TestClass/`
-   `tests/test_two/`
-   `tests/data/test_two/TestClass/test_method/`
-   `tests/data/test_two/TestClass/`
-   `tests/data/test_two/`
-   `tests/data/`

Here, this would return the path
`tests/test_two/TestClass/test_method/strings.prop`.

As you can see, the searched directory hierarchy is slighly different if
a *method* instead of a *function* asks for a resource. This allows you
to load different resources based on the name of the test class, if you
wish.

Finally, if a test function or test method would ask for a resource
named `global.dat`, then the resulting path would be
`tests/data/global.dat` since no other directory in the searched
directory hierarchy contains a file named `global.dat`. In other words,
the `tests/data/` directory is the place for global (or fallback)
resources.

If a resource cannot be found in *any* of the searched directories, a
`KeyError` is raised.

# The datadir_copy fixture

The \"datadir_copy\" fixture is similar to the [datadir](#datadir)
fixture, but copies the requested resources to a temporary directory
first so that test functions or methods can modify their resources
on-disk without affecting other test functions and methods.

Each test function or method gets its own temporary directory and thus
its own fresh copies of the resources it requests.

**Caveat:** Each time a resource is requested using the dictionary
notation, a fresh copy of the resource is made. This also applies if a
test function or method requests the same resource multiple times. Thus,
if you modify a resource and need to access the *modified* version of
the resource later, save its path in a variable and use that variable to
access the resource later instead of using the dictionary notation
multiple times:

``` python
def test_foo(datadir_copy):
    # This creates the initial fresh copy of data.txt and saves
    # its path in the variable "resource1".
    resource1 = datadir_copy["data.txt"]

    # ...modify resource1 on-disk...

    # You now want to access the modified version of data.txt.

    # WRONG way: This will overwrite your modified version of the
    #            resource with a fresh copy!
    fh = open(datadir_copy["data.txt"], "rb")

    # CORRECT way: This will let you access the modified version
    #              of the resource.
    fh = open(resource1, "rb")
```
