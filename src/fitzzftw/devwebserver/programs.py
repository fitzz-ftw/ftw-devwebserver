# File: src/fitzzftw/devwebserver/programs.py
# Author: Fitzz TeXnik Welt
# Email: FitzzTeXnikWelt@t-online.de
# License: LGPLv2 or above
"""
programs
===============================

Provides main entry points and asynchronous execution logic for 
the development web server.
"""

import asyncio
from pathlib import Path

from fitzzftw.devwebserver.cli_parser import DevWebserverArguments, devwebparser
from fitzzftw.devwebserver.communication import ReloadBroker
from fitzzftw.devwebserver.config import DevWebServerConfig
from fitzzftw.devwebserver.server import WebServer
from fitzzftw.devwebserver.watcher import DirectoryWatcher


async def asyncdevwebserver(args:DevWebserverArguments) -> None:
    """
    Coordinates the asynchronous execution of the web server and the 
    directory watcher.

    :param args: The parsed configuration arguments for the web server.
    """
    broker:ReloadBroker = ReloadBroker(args.reload_delay/1000)
    watcher = DirectoryWatcher(args.watch_dirs, broker.signal_change, args.root_dir)
    with WebServer(broker=broker, root_dir=args.root_dir) as server:
        server.register_myroutes()
        webserver = asyncio.create_task(
            server.start_server(
                host=args.host,
                port=args.port,
                debug=False))
        print(f"Running on IP: {args.host} and Port {args.port}")
        watcher.start()
        await webserver
    watcher.stop()

def prog_devwebserver(argv:list[str]|None = None)->int:
    """
    Main entry point for the development web server CLI.

    :param argv: Optional list of command-line arguments.
    :returns: The exit status code (0 for success, 1 for errors, 
        2 for keyboard interrupt).
    """
    try:
        conf:DevWebServerConfig = DevWebServerConfig()
        conf.set_config()
        conf.convert()
        parser = devwebparser()
        parser.set_defaults(**conf.as_default())
        args = parser.parse_args(argv)
        asyncio.run(asyncdevwebserver(args))
        return 0
    except KeyboardInterrupt:
        return 2
    except Exception as e:
        # traceback.print_exc()
        print(e)
        return 1

if __name__ == "__main__": # pragma: no cover
    from doctest import FAIL_FAST, testfile
    
    be_verbose = False
    be_verbose = True
    option_flags = 0
    option_flags = FAIL_FAST
    test_sum = 0
    test_failed = 0
    passed_files = 0
    # Pfad zu den dokumentierenden Tests
    testfiles_dir = Path(__file__).parents[3] / "doc/source/devel"
    test_files = [
        "get_started_programs.rst",
    ]
    for file in test_files:
        test_file = testfiles_dir / file
        if test_file.exists():
            print(f"--- Running Doctest for {test_file.name} ---")
            doctestresult = testfile(
                str(test_file),
                module_relative=False,
                verbose=be_verbose,
                optionflags=option_flags,
            )
            test_failed += doctestresult.failed
            test_sum += doctestresult.attempted
            if doctestresult.failed > 0 and option_flags & FAIL_FAST:
                print(f"Doctest result for {test_file.name}: {doctestresult}")
                print(f"\nKeep going! You already passed {passed_files} files "
                  f"with {test_sum} tests before this hit.")                
                break  # Stop on first failure if FAIL_FAST is set
            passed_files += 1
        else:
            print(f"⚠️ Warning: Test file {test_file.name} not found.")
    if test_failed == 0:
        print(f"\nDocTests passed without errors, {test_sum} tests.")
    else:
        if not option_flags & FAIL_FAST:
            print(f"\nDocTests failed: {test_failed} tests out of {test_sum}.")
