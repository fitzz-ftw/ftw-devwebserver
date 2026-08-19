The Webserver for Developers Program
######################################


.. SECTION - Setup

>>> test_data_pre= "."

>>> from fitzzftw.devtools.testinfra import TestHomeEnvironment
>>> from pathlib import Path
>>> env = TestHomeEnvironment(Path("doc/source/devel/testhome"),
...     appname="ftwpki", appauthor="FitzzTeXnikWelt")

>>> env.setup(True)
>>> env.clean_home()

.. !SECTION - Setup
.. SECTION - Prepare

>>> from pathlib import Path
>>> import asyncio
>>> import sys
>>> import shlex

>>> conf_file = env.copy2cwd(f"{test_data_pre}/package.json", "package.json")

>> def stub_getpass(prompt:str)->str:
...     print(prompt)
...     return "strenggeheim"


.. !SECTION - Prepare
>>> from fitzzftw.devwebserver.programs import prog_devwebserver


>>> prog_devwebserver()


.. SECTION - Teardown

>> loop.stop()

>>> env.clean_home()
>>> env.teardown()


.. !SECTION - Teardown
