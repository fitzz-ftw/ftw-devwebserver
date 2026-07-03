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

>>> conf_file = env.copy2cwd(f"{test_data_pre}/test_webserver.toml", "pyproject.toml")

>> def stub_getpass(prompt:str)->str:
...     print(prompt)
...     return "strenggeheim"


.. !SECTION - Prepare


>>> from fitzzftw.devwebserver.config import TomlSerializer

>>> TomlSerializer.deserialize(conf_file) #doctest: +SKIP





>>> from fitzzftw.devwebserver.config import DevWebServerConfig

>>> conf = DevWebServerConfig()

>>> conf.set_config()

>>> conf.convert()

>>> conf.as_default() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
{'host': '0.0.0.0', 
 'port': 8080, 
 'root_dir': ...Path('docs/_build/html'), 
 'watch_dirs': [...Path('docs/source')], 
 'ignore_patterns': ['.git/*', 
     '**/__pycache__/*', 
     '**/.DS_Store', 
     '**/*.tmp'], 
 'enabled': True, 
 'cert_file': ...Path('.certs/server.crt'), 
 'key_file': ...Path('.certs/server.key'), 
 'reload_delay': 500}

>>> from fitzzftw.devwebserver.cli_parser import devwebparser

>>> parser = devwebparser()

>>> parser.set_defaults(**conf.as_default())

>>> parser.print_help(file=sys.stderr)

>>> args = parser.parse_args(["--host","192.168.2.1"])

>>> args #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
DevWebserverArguments(cert_file='.certs/server.crt'
    enabled='True'
    host='192.168.2.1'
    ignore_patterns='['.git/*', '**/__pycache__/*', '**/.DS_Store', '**/*.tmp']'
    key_file='.certs/server.key'
    port='8080'
    reload_delay='500'
    root_dir='docs/_build/html'
    watch_dirs='[...Path('docs/source')]')

>>> from fitzzftw.devwebserver.watcher import DirectoryWatcher

>>> from fitzzftw.devwebserver.communication import ReloadBroker

>>> broker = ReloadBroker()

>>> watcher = DirectoryWatcher(args.watch_dirs, broker.signal_change, args.root_dir)


>>> watcher.handler.callback
<bound method ReloadBroker.signal_change of ReloadBroker(Id: 1/1)>

>>> watcher.watch_dirs #doctest: +ELLIPSIS
[...Path('...docs/source')]

>>> from fitzzftw.devwebserver.server import WebServer

>>> server = WebServer(broker= broker, root_dir=args.root_dir)
>>> server
WebServer(wwwdoc: docs/_build/html, broker: ReloadBroker(Id: 1/1))

>>> server.broker.signal_change == watcher.handler.callback
True

>>> watcher.handler.callback.__self__ is server.broker
True

>>> server.broker.wait_for_reload.__self__ is watcher.handler.callback.__self__
True

>>> watcher.handler.callback()

>>> watcher.handler.callback()

>>> watcher.handler.callback()


>>> watcher.handler.callback
<bound method ReloadBroker.signal_change of ReloadBroker(Id: 1/1)>

<bound method ReloadBroker.signal_change of ReloadBroker(Id: 1/1)>

>>> asyncio.run(server.broker.wait_for_reload())


.. SECTION - Teardown

>> loop.stop()

>>> env.clean_home()
>>> env.teardown()


.. !SECTION - Teardown
