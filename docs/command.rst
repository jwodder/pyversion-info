.. index:: pyversion-info (command)

Command-Line Program
====================

::

    pyversion-info [<global-options>] <command> [<args> ...]

``pyversion-info`` provides a command of the same name for querying information
about Python versions from the command line.

Currently, the :command:`pyversion-info` command has two subcommands,
:command:`list` and :command:`show`.  By default, the commands provide
information about CPython versions; to get information about PyPy versions
instead, pass the ``--pypy`` option to the subcommand.


Global Options
--------------

.. program:: pyversion-info

.. option:: -d <database>, --database <database>

    Use the given JSON file as the version information database instead of
    fetching data from the default URL.  ``<database>`` can be either an HTTP
    or HTTPS URL or a path to a local file.


:command:`pyversion-info list`
------------------------------

::

    pyversion-info [<global-options>] list [<options>] {major|minor|micro}

List all major, minor, or micro Python versions, one per line.


Options
^^^^^^^

.. program:: pyversion-info list

.. option:: -a, --all

    List all known versions of the given level

.. option:: --cpython

    Show information about CPython versions.  This is the default.

.. option:: -n, --not-eol

    Only list versions that have not yet reached end-of-life (i.e., all
    supported versions plus all unreleased versions).  This may only be used
    when querying information about CPython versions.

.. option:: --pypy

    Show information about PyPy versions

.. option:: -r, --released

    Only list released versions.  This is the default.

.. option:: -s, --supported

    Only list currently-supported versions


:command:`pyversion-info show`
------------------------------

::

    pyversion-info [<global-options>] show [<options>] <version>

Show various information about a given Python version.

Sample outputs:

.. code:: console

    $ pyversion-info show 3
    Version: 3
    Level: major
    Release-date: 2008-12-03
    Is-released: yes
    Is-supported: yes
    EOL-Date: UNKNOWN
    Is-EOL: no
    Subversions: 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9

.. code:: console

    $ pyversion-info show 3.3
    Version: 3.3
    Level: minor
    Release-date: 2012-09-29
    Is-released: yes
    Is-supported: no
    EOL-date: 2017-09-29
    Is-EOL: yes
    Subversions: 3.3.0, 3.3.1, 3.3.2, 3.3.3, 3.3.4, 3.3.5, 3.3.6, 3.3.7

.. code:: console

    $ pyversion-info show 3.9.5
    Version: 3.9.5
    Level: micro
    Release-date: 2021-05-03
    Is-released: yes
    Is-supported: yes
    EOL-Date: 2025-10-01
    Is-EOL: no

.. code:: console

    $ pyversion-info show --pypy 7.3
    Version: 7.3
    Level: minor
    Release-Date: 2019-12-23
    Is-Released: yes
    Subversions: 7.3.0, 7.3.1, 7.3.2, 7.3.3, 7.3.4, 7.3.5, 7.3.6, 7.3.7
    CPython-Series: 2.7, 3.6, 3.7, 3.8

.. code:: console

    $ pyversion-info show --pypy 7.3.7
    Version: 7.3.7
    Level: micro
    Release-Date: 2021-10-25
    Is-Released: yes
    CPython: 3.7.12, 3.8.12

Options
^^^^^^^

.. option:: --cpython

    Show information about CPython versions.  This is the default.

.. option:: -J, --json

    Output JSON

.. option:: --pypy

    Show information about PyPy versions

.. option:: -S, --subversions <all|not-eol|released|supported>

    Which subversions to list (and, for PyPy versions, which subversions to
    take into account when determining supported CPython versions); the choices
    have the same meanings as the :command:`list` options of the same name
    [default: ``released``]
