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


>>> from fitzzftw.devwebserver.config import JsonSerializer

>>> JsonSerializer.deserialize(conf_file) #doctest: +NORMALIZE_WHITESPACE
{'name': 'simplecomponents', 
 'version': '1.0.0', 
 'main': 'index.js', 
 'scripts': {'dev': 'vite', 
    'build': 'vite build', 
    'test': 'vitest --config config/vite.config.js', 
    'lint': 'eslint --config config/.eslintrc.js src/**/*.js', 
    'format': 'prettier --config config/prettier.config.js --write src/**/*.js', 
    'docs': 'jsdoc -c jsdoc.json'}, 
 'keywords': [], 
 'author': 'Fitzz TeXnik Welt <FitzzTeXnikWelt@t-online.de>', 
 'license': 'ISC', 
 'description': '', 
 'devDependencies': {'@testing-library/dom': '^10.4.1', 
    'better-docs': '^2.7.3', 
    'jsdoc': '^4.0.5', 
    'jsdom': '^29.1.1', 
    'vite': '^8.2.1', 
    'vitest': '^4.1.11'}, 
 'devserver': {'port': 3000, 
    'host': 'localhost', 
    'root_dir': 'src/', 
    'watch_dirs': ['src/components', 
        'src/css'], 
    'reload_delay': 500}}

>>> from fitzzftw.devwebserver.config import DevWebServerConfig

>>> conf = DevWebServerConfig()
>>> conf.set_config()

>>> conf.convert()

>>> conf.as_default() #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
{'port': 3000, 
 'host': 'localhost', 
 'root_dir': ...Path('src'), 
 'watch_dirs': [...Path('src/components'), 
    ...Path('src/css')], 'reload_delay': 500}

>>> from fitzzftw.devwebserver.cli_parser import devwebparser

>>> parser = devwebparser()

>>> parser.set_defaults(**conf.as_default())

>>> parser.print_help(file=sys.stderr)

>>> args = parser.parse_args(["--host","192.168.2.1"])

>>> args #doctest: +ELLIPSIS +NORMALIZE_WHITESPACE
DevWebserverArguments(cert_file='None'
enabled='False'
host='192.168.2.1'
ignore_patterns='None'
key_file='None'
port='3000'
reload_delay='500'
root_dir='src'
watch_dirs='[PosixPath('src/components'), PosixPath('src/css')]')


>>> from fitzzftw.devwebserver.watcher import DirectoryWatcher

>>> from fitzzftw.devwebserver.communication import ReloadBroker

>>> broker = ReloadBroker()

>>> watcher = DirectoryWatcher(args.watch_dirs, broker.signal_change, args.root_dir)

>>> watcher.handler.callback
<bound method ReloadBroker.signal_change of ReloadBroker(Id: 2/2)>

>>> watcher.watch_dirs #doctest: +ELLIPSIS
[...Path('...src/components'), ...Path('...src/css')]

>>> from fitzzftw.devwebserver.server import WebServer

>>> server = WebServer(broker= broker, root_dir=args.root_dir)
>>> server
WebServer(wwwdoc: src, broker: ReloadBroker(Id: 2/2))

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
<bound method ReloadBroker.signal_change of ReloadBroker(Id: 2/2)>

>>> asyncio.run(server.broker.wait_for_reload())


.. SECTION - Teardown

>> loop.stop()

>>> env.clean_home()
>>> env.teardown()


.. !SECTION - Teardown
