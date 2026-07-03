# File: src/fitzzftw/devwebserver/server.py
# Author: Fitzz TeXnik Welt
# Email: FitzzTeXnikWelt@t-online.de
# License: LGPLv2 or above
"""
server
===============================

Provides a WebServer class based on Microdot for handling static files and 
server-side events (SSE)
for live reloading functionality.
"""

from pathlib import Path
from typing import NoReturn, Self

from microdot import Microdot, Response, send_file
from microdot.sse import with_sse

"""
    <script>
        /* DevServer: SSE-Client for live reloading */
        (new EventSource('/reload')).onmessage = () => location.reload();
    </script>
"""




def inject_reload_script(html_content:str)->tuple[str, int, dict]:
    """
    Injects a live-reload SSE client script into the provided HTML content.

    :param str html_content: The original HTML content.
    :returns: A tuple containing the modified HTML content, HTTP status code, and headers.
    """
    script = """
        <script>
        /* DevServer: SSE-Client for live reloading with debug logging */
        console.log("[DevServer] Initializing EventSource...");

        const evtSource = new EventSource('/reload');

        evtSource.onopen = () => {
            console.log("[DevServer] Connection opened successfully.");
        };

        evtSource.addEventListener('reload', (e) => {
            console.log("[DevServer] Reload-Signal empfangen, lade neu...");
            setTimeout(() => {
                window.location.reload(true);
            }, 50);
        });
        evtSource.onerror = (err) => {
            console.error("[DevServer] EventSource failed:", err);
        };
        </script>
    </body>"""
    return html_content.replace("</body>", script), 200, {"Content-Type": "text/html"}

# Type alias for route return values
type RouteReturn = Response | tuple[str, int, dict[str, str]] | tuple[dict[str, str], int] | None


class WebServer(Microdot):
    """
    Custom WebServer class based on Microdot.

    :ivar Path _virt_wwwdoc: Internal reference to the root directory.
    :ivar Path|None _original_cwd: The working directory prior to server initialization.
    """
    def __init__(self, broker, root_dir: str|Path) -> None:
        """
        Initializes the web server with a communication broker and root directory.

        :param broker: The communication broker used to handle reload events.
        :param root_dir: The absolute path to the server's root directory 
            for serving files.
        """
        super().__init__()
        self.broker = broker
        self.root_dir = Path(root_dir).resolve()
        self._virt_wwwdoc = self.root_dir
        self._original_cwd = None

    def __enter__(self) -> Self:
        """
        Sets up the server environment by capturing the current working directory.

        :returns: The WebServer instance.
        """
        self._original_cwd = Path.cwd()
        # os.chdir(self.root_dir)
        print(f"Server gestartet in: {self.root_dir}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Cleans up the server environment.
        """
        if self._original_cwd:
            # os.chdir(self._original_cwd)
            print("Zurück im ursprünglichen Verzeichnis.")

    def register_myroutes(self):
        """
        Registers all required routes for the server, including SSE and static file serving.
        """
        # Um @with_sse zu nutzen, muss die Route Zugriff auf die Instanz haben
        @self.route("/reload")
        @with_sse
        async def reload(request, sse) -> NoReturn:
            while True:
                # Zugriff über self.broker
                await self.broker.wait_for_reload()
                print("Send reload")
                await sse.send("reload", event="reload")

        @self.route("/<path:path>")
        async def other(request, path: str) -> RouteReturn: 
            try:
                if path.endswith("/"):
                    # return send_file(str(self.virtuell_path(path) / "index.html"))
                    return inject_reload_script(
                        (self.virtuell_path(Path(path)/ "index.html")).read_text())
                pparts = Path(path).parts
                if "_static" in pparts:
                    idx = pparts.index("_static")
                    newpath = "/".join(pparts[idx:])
                    return send_file(str(self.virtuell_path(newpath)))
                if "node_modules" in pparts or "scss" in pparts:
                    return {"error": "File not found"}, 500
                if path.startswith("_static"):
                    return send_file(str(self.virtuell_path(path)))
                return send_file(str(self.virtuell_path(path)))
            except FileNotFoundError as e:
                print(e)

        @self.route("/")
        async def index(request) -> RouteReturn:
            try:
                return inject_reload_script(self.virtuell_path("index.html").read_text())
            except FileNotFoundError as e:
                print(e)

        @self.errorhandler(500)
        async def not_found(request)->RouteReturn:
            ret ="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Build in progress...</title>
            </head>
            <body>
                <h1>FTW DevServer: Rebuilding...</h1>
                <div id="status">Warte auf Build-Signal...</div>

                <script>
                    /* SSE-Client für Live-Reloading */
                    const evtSource = new EventSource('/reload');
                    
                    evtSource.addEventListener('reload', (e) => {
                        console.log("[DevServer] Signal empfangen, lade neu...");
                        location.reload();
                    });

                    evtSource.onerror = (err) => {
                        console.log("[DevServer] Warte auf Server...");
                    };
                </script>
            </body>
            </html>
            """
            return ret, 500, {"Content-Type": "text/html"}

    def _rel_path(self, path:Path)->str:
        """
        Returns the relative path string based on the current working directory.

        :param path: The target path.
        :returns: The relative path as a string.
        """
        return path.relative_to(Path.cwd()).as_posix()

    def virtuell_path(self, routepath:str|Path) -> Path:
        """
        Resolves a virtual route path against the configured root directory.

        :param routepath: The path provided by the route.
        :returns: The absolute resolved Path object.
        """
        return self._virt_wwwdoc / routepath

    def __repr__(self) -> str:
        """
        Returns a string representation of the WebServer instance.

        :returns: The string representation.
        """
        ret = (f"{self.__class__.__name__}(wwwdoc: {self._rel_path(self.root_dir)}, "
               f"broker: {self.broker})")
        return ret


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
        "server.rst",
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
