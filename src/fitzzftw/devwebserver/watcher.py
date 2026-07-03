# File: src/fitzzftw/devwebserver/watcher.py
# Author: Fitzz TeXnik Welt
# Email: FitzzTeXnikWelt@t-online.de
# License: LGPLv2 or above
"""
watcher
===============================

Provides functionality to monitor directories for file system 
changes and trigger callbacks.
"""

from collections.abc import Iterable
from pathlib import Path

from watchdog.events import (
    FileSystemEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer


class ChangeHandler(FileSystemEventHandler):
    """
    Handles file system events and triggers a callback when 
    specific criteria are met.

    """

    def __init__(self, callback, pathfilter:str|Path) -> None:
        """
        Initializes the handler with a callback and a filter path.

        :param callback: The function to execute.
        :param pathfilter: The base path for event filtering.
        """
        self.callback = callback
        self.pathfilter = Path(pathfilter).resolve()

    def on_modified(self, event: FileSystemEvent) -> None:
        """
        Processes modification events and triggers the callback if 
        the path matches the filter.

        :param event: The file system event to process.
        """
        if event.is_directory:
            new_path = Path(str(event.src_path))
            if new_path.is_relative_to(self.pathfilter):
                self.callback()


class DirectoryWatcher:
    """
    Watches multiple directories for changes using a watchdog observer.

    :ivar observer: The watchdog Observer instance.
    :ivar handler: The event handler instance.
    """

    def __init__(self, watch_dirs: Iterable[Path], callback,pathfilter:str|Path) -> None:
        """
        Initializes the directory watcher with directories and a callback.

        :param watch_dirs: Iterable of paths to watch.
        :param callback: The function to execute on changes.
        :param pathfilter: The filter path passed to the handler.
        """
        self.observer = Observer()
        self.handler = ChangeHandler(callback, pathfilter)
        self.watch_dirs = [f.resolve()  for f in watch_dirs]

    def start(self) -> None:
        """
        Schedules all directories and starts the observer.
        """
        for path in self.watch_dirs:
            if path.exists():
                self.observer.schedule(self.handler, str(path), recursive=True)
        self.observer.start()

    def stop(self) -> None:
        """
        Stops the observer and joins the thread.
        """
        self.observer.stop()
        self.observer.join()



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
        "watcher.rst",
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
