# File: src/fitzzftw/devwebserver/cli_parser.py
# Author: Fitzz TeXnik Welt
# Email: FitzzTeXnikWelt@t-online.de
# License: LGPLv2 or above
"""
cli_parser
===============================

Provides classes and factory functions to manage CLI argument 
parsing based on custom configurations.
"""

from argparse import ArgumentParser
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from tomllib import load
from typing import Any, Generic, Type, TypeVar

# SECTION - ArgumentParser help
# FUNCTION - get_help_entries

HELP_FILE = Path(__file__).parent.joinpath("cli_parser.help")


def load_help_entries(constance: dict[str, Any], help_file: Path) -> None:
    """
    Loads help entries from a TOML file into a dictionary.

    :param constance: The dictionary to update with help entries.
    :param help_file: The path to the TOML help file.
    """
    with help_file.open("rb") as f:
        constance.update(load(f))


# !FUNCTION - get_help_entries

_HELP: dict[str, Any] = {}

load_help_entries(_HELP, HELP_FILE)

# print(_HELP)

#!SECTION - ArgumentParser help
LANG = "en"


# CLASS - ParserHelp
class ParserHelp:
    """
    Manages help text for parser arguments.

    :ivar dict _help: The dictionary containing help content mappings.
    :ivar str _lang: The language code for the help text.
    """

    def __init__(
        self,
        parser_id: str,
        help_entries: dict[str, str | dict[str, str]] = _HELP,
        lang: str = LANG,
    ) -> None:
        """
        Initializes the help parser for a specific parser ID.

        :param parser_id: The unique identifier for the parser.
        :param help_entries: Dictionary containing the help content mappings.
        :param lang: The language code for the requested help text.
        """
        self._help = help_entries.get(parser_id)
        self._lang = lang

    def update(self, parser_id: str, new_help: dict[str, str | dict[str, str]] = _HELP) -> None:
        """
        Updates the existing help entries with new content.

        :param parser_id: The identifier for the help entries to update.
        :param new_help: The dictionary containing new help mappings.
        """
        self._help.update(new_help.get(parser_id))  # type: ignore

    def help(self, arg_dest_name: str) -> str:
        """
        Retrieve the help text for a specific argument destination.

        :param arg_dest_name: The destination name of the argument.
        :returns: The help string for the specified language or an empty string.
        """
        ret = self._help.get(arg_dest_name, "")  # type: ignore
        return ret.get(self._lang, "en") if ret else ret  # type: ignore

    def __call__(self, arg_dest_name: str) -> str:
        """
        Return the help text for the given argument destination.

        :param arg_dest_name: The destination name of the argument.
        :returns: The help text.
        """
        return self.help(arg_dest_name)


# !CLASS - ParserHelp


# CLASS - KeyNames Mixin
class KeyNames:
    """
    Mixin class to provide property access for cryptographic key names.

    :ivar str key_name: The stem of the file name, ha to be providet from 
        the class to be mixed in.
    """
    @property
    def private_key(self) -> str:
        """
        Returns the private key filename based on the key name. **(ro)**
        """
        return f"{self.key_name}.key.pem" if hasattr(self, "key_name") else ""  # type: ignore

    @property
    def public_key(self) -> str:
        """
        Returns the public key filename based on the key name. **(ro)**
        """
        return f"{self.key_name}.pub.pem" if hasattr(self, "key_name") else ""  # type: ignore


# !CLASS - KeyNames Mixin


# CLASS - BaseArguments
class BaseArguments:
    """
    Base class for defining command-line argument structures.

    :cvar list __slots__: List of allowed attribute names for instances.
    :cvar list helpid: List of help identifiers.
    :cvar dict arg_data: Configuration data for arguments.
    """
    __slots__: list[str] = ["_arguments"]
    helpid: list[str] = []
    arg_data = {}

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Initializes subclasses by merging slots and argument configuration.
        """
        super().__init_subclass__(**kwargs)
        base = cls.__base__ if cls.__base__ is not None else BaseArguments
        base_slots: list = base.__slots__.copy()
        base_slots.extend(cls.__slots__.copy())
        base_helpid: list = base.helpid.copy()
        base_helpid.extend(cls.helpid)
        base_data: dict = deepcopy(base.arg_data)
        base_data.update(cls.arg_data)
        cls.__slots__ = base_slots
        cls.arg_data = base_data
        cls.helpid = base_helpid

    @property
    def arguments(self) -> list[tuple[list[str], dict[str, Any]]]:
        """
        Returns the list of argument definitions. **(ro)**
        """
        if hasattr(self, "_arguments"):
            return self._arguments
        else:
            return []

    def setup_args(self, pre_parser: bool = False) -> None:
        """
        Configures the arguments for the parser.

        :param pre_parser: Flag indicating if this is a pre-parser.
        """
        types = self.get_types()
        if hasattr(self, "_arguments"):
            del self._arguments
        self._arguments: list[tuple[list[str], dict[str, Any]]] = []
        pre: bool = pre_parser
        help = ParserHelp(self.helpid[0], _HELP)
        for helpname in self.helpid[1:]:
            help.update(helpname)
        for name in self.arg_data:
            args = []
            kwargs = {}
            self.arg_data[name]["kws"].update(types[name]["kws"])
            if self.arg_data[name]["kws"].get("action", None) in ["store_true", "store_false"]:
                self.arg_data[name]["kws"].pop("type", None)
            args = self.arg_data[name]["flags"].copy()
            kwargs = deepcopy(self.arg_data[name]["kws"])
            if pre:
                kwargs.update(self.arg_data[name]["pre"])
            kwargs["help"] = help(name)
            if not args:
                args.append(name)
            else:
                kwargs["dest"] = name if args[0].startswith("-") else None
            entry = (args, kwargs)
            self._arguments.append(entry)

    def get_types(self):
        """
        Determines the types for all defined arguments.

        :returns: A dictionary mapping argument names to their types and configuration.
        """
        values: dict[str, dict[str, dict[str, type | str]]] = {}
        for name in [arg for arg in self.__slots__ if not arg.startswith("_")]:
            if name == "dnsubject":
                values[name] = {"kws": {"type": str}}
            else:
                curr_type = getattr(self, name)
                if isinstance(curr_type, list):
                    if not curr_type:
                        type_hint = str
                    else:
                        type_hint = type(curr_type[0])
                else:
                    type_hint = type(curr_type)
                values[name] = {"kws": {"type": type_hint}}
            del name
        return values

    def __repr__(self) -> str:
        names: list[str] = []
        self.__slots__.sort()
        for name in [arg for arg in self.__slots__ if not arg.startswith("_")]:
            if name in ["dnsubject", "host_names", "ip_addresses"]:
                names.append(f"{name}={getattr(self, name)}")
            else:
                names.append(f"{name}='{getattr(self, name)}'")
        ret = "".join(
            [
                f"{self.__class__.__name__}(",
                "\n".join(names),
                ")",
            ]
        )
        return ret


# !CLASS - BaseArguments

AT = TypeVar("AT", bound="BaseArguments")


# CLASS - FtwBaseParser
class FtwBaseParser(ArgumentParser, Generic[AT]):
    """
    Custom CLI parser for handling application configuration arguments. **(rw)**

    :ivar bool _preparser: Indicates if help was disabled during initialization.
    :ivar AT _conf: The argument configuration instance.
    """

    def __init__(
        self,
        pre_parser: bool = False,
        *,
        arg_conf: Type[AT] = BaseArguments,
        exit_on_error: bool = False,
        **kwargs,
    ) -> None:
        """
        Initializes the parser with a default or custom description. **(rw)**

        :param bool pre_parser: Flag to determine if help functionality should be disabled.
        :param Type[AT] arg_conf: The class type used for argument configuration.
        :param bool exit_on_error: Whether to exit the process on parsing errors.
        """
        if pre_parser and "add_help" not in kwargs:
            kwargs["add_help"] = False
        self._preparser: bool = not kwargs.get("add_help", True)
        kwargs["exit_on_error"] = exit_on_error
        super().__init__(**kwargs)
        self._conf: AT = arg_conf()
        self._conf.get_types()
        # print(f"{self._preparser=}")
        self._conf.setup_args(pre_parser=self._preparser)
        self._san = self.add_argument_group("SAN Entries")
        self._dn = self.add_argument_group("Destinguish Name Entires")
        self._mandantory_san = True
        self._start_o_s_a = deepcopy(self._option_string_actions)
        self._start_actions = deepcopy(self._actions)
        self._setup_parser()

    def _setup_parser(self) -> None:
        """
        Configure the argument parser for target, source, and output directory. (ro)

        Sets up the positional and optional arguments for the CLI.
        """
        for name_flags, parser_config in self._conf.arguments:
            sub = parser_config.pop("sub_parser", None)
            match sub:
                case "dn":
                    self._dn.add_argument(*name_flags, **parser_config)
                case "san":
                    self._san.add_argument(*name_flags, **parser_config)
                case _:
                    self.add_argument(*name_flags, **parser_config)

    def parse_known_args(
        self, args: list[str] | None = None, namespace: AT | None = None
    ) -> tuple[AT, list[str]]:
        """
        Parses known arguments.

        :param args: List of argument strings.
        :param namespace: Existing namespace to populate.
        :returns: A tuple containing the populated namespace and unknown arguments.
        """
        if namespace is None:
            target_args = type(self._conf)
            namespace = target_args()

        return super().parse_known_args(args=args, namespace=namespace)

    def parse_args(
        self,
        args: list[str] | None = None,
        namespace: AT | None = None,
    ) -> AT:
        """
        Parses command-line arguments and populates the namespace.

        :param args: List of argument strings.
        :param namespace: Existing namespace to populate.
        :returns: Populated namespace instance.
        """
        if namespace is None:
            target_args = type(self._conf)
            namespace = target_args()

        # sets the defaults to namespace even it has initial
        # attributes.
        for action in self._actions:
            if action.dest in namespace.__slots__:
                setattr(namespace, action.dest, action.default)
        ret = super().parse_args(args, namespace)
        return ret

    @property
    def pre_parser(self) -> bool:
        """
        Indicates whether the parser is configured as a pre-parser. **(ro)**
        """
        return self._preparser



# !CLASS - FtwBaseParser


# FUNCTION - parser_factory_creator
def parser_factory_creator(arg_type: Type[AT]) -> Callable[..., "FtwBaseParser[AT]"]:
    """
    Creates a parser factory configured for a specific argument model.

    :param arg_type: The class type used to configure the parser's expected arguments.

    :returns: A callable factory that produces a FtwBaseParser instance
        constrained to the provided argument type.
    """
    def parser_factory(pre_parser: bool = False, **kwargs) -> FtwBaseParser[AT]:
        kwargs["arg_conf"] = arg_type
        parser = FtwBaseParser(pre_parser=pre_parser, **kwargs)
        return parser

    parser_factory.__doc__ = f"Factory function for {arg_type.__name__}Parser."
    return parser_factory


# !FUNCTION - parser_factory_creator


class DevWebserverArguments(BaseArguments):
    """
    Configuration arguments for the development web server.

    :cvar list __slots__: List of attributes for web server configuration.
    :cvar list helpid: List of help identifiers for this configuration.
    :cvar dict arg_data: Argument configuration mapping.
    :ivar str host: The server host address.
    :ivar int port: The server port number.
    :ivar Path root_dir: The root directory for the web server.
    :ivar list[Path] watch_dirs: List of directories to watch for changes.
    :ivar list ignore_patterns: List of file patterns to ignore.
    :ivar bool enabled: Flag to enable or disable the server.
    :ivar Path cert_file: Path to the SSL certificate file.
    :ivar Path key_file: Path to the SSL key file.
    :ivar int reload_delay: Delay in seconds for the auto-reload feature.
    """
    __slots__: list[str] = [
        "host",
        "port",
        "root_dir",
        "watch_dirs",
        "reload_delay",
        "ignore_patterns",
        "enabled",
        "cert_file",
        "key_file",
    ]

    helpid: list[str] = ["devweb"]
    arg_data = {
        "host": {
            "flags": ["--host"],
            "kws": {},
            "pre": {},
        },
        "port": {
            "flags": ["-p", "--port"],
            "kws": {},
            "pre": {},
        },
        "root_dir": {
            "flags": ["--root-dir"],
            "kws": {},
            "pre": {},
        },
        "watch_dirs": {
            "flags": ["--watch-dir"],
            "kws": {
                "action": "append",
            },
            "pre": {},
        },
        "reload_delay": {
            "flags": ["--reload-delay"],
            "kws": {},
            "pre": {},
        },
        "ignore_patterns": {
            "flags": ["--ignore"],
            "kws": {
                "action": "append",
            },
            "pre": {},
        },
        "enabled": {
            "flags": ["--enable"],
            "kws": {"action": "store_true"},
            "pre": {},
        },
        "cert_file": {
            "flags": ["--cert-file"],
            "kws": {},
            "pre": {},
        },
        "key_file": {
            "flags": ["--key-file"],
            "kws": {},
            "pre": {},
        },
    }

    def __init__(self) -> None:
        """
        Initializes the development web server arguments with default values.
        """
        super().__init__()
        self.host:str=""
        self.port:int=0
        self.root_dir:Path=Path()
        self.watch_dirs:list[Path]=[Path()]
        self.ignore_patterns:list=[]
        self.enabled:bool=False
        self.cert_file:Path=Path()
        self.key_file:Path=Path()
        self.reload_delay:int=0

type DevWebserveParser = FtwBaseParser[DevWebserverArguments]

devwebparser: Callable[..., DevWebserveParser] = parser_factory_creator(
    DevWebserverArguments
)
"""
Factory function for the development web server parser.

:param bool|None pre_parser: Flag to determine if help functionality should be disabled.
"""
def no_color_parser() -> FtwBaseParser[DevWebserverArguments]:
    """
    Returns a DevWebserveParser with color switched off.

    :returns: A DevWebserveParser with no color.
    """
    return devwebparser(color=False)

if __name__ == "__main__":  # pragma: no cover
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
        "cli_parser.rst",
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
                print(
                    f"\nKeep going! You already passed {passed_files} files "
                    f"with {test_sum} tests before this hit."
                )
                break  # Stop on first failure if FAIL_FAST is set
            passed_files += 1
        else:
            print(f"⚠️ Warning: Test file {test_file.name} not found.")
    if test_failed == 0:
        print(f"\nDocTests passed without errors, {test_sum} tests.")
    else:
        if not option_flags & FAIL_FAST:
            print(f"\nDocTests failed: {test_failed} tests out of {test_sum}.")
