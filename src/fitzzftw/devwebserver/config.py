# File: src/fitzzftw/devwebserver/config.py
# Author: Fitzz TeXnik Welt
# Email: FitzzTeXnikWelt@t-online.de
# License: LGPLv2 or above
"""
config
===============================

Provides classes for deserializing and managing web server configurations 
from various file formats.
"""

import json
import tomllib
from pathlib import Path
from typing import Any, Protocol


# SECTION - Protocols
class PDeserialize(Protocol):
    """
    Protocol for classes capable of deserializing content into a dictionary.
    """
    def deserialize(self, content:bytes|str|Path)->dict[str,Any]:
        """
        Deserializes content into a dictionary.

        :param bytes|str|Path content: The input content to deserialize.
        :returns: A dictionary representing the deserialized data.
        """
        ...
# !SECTION - Protocols


class Serializer:
    """
    Base class for file format serialization and deserialization.
    """
    @classmethod
    def deserialize(cls, content:bytes|str|Path)->dict[str,Any]:
        """
        Deserializes content into a dictionary.

        :param bytes|str|Path content: The input content to deserialize.
        :raises NotImplementedError: Always raised, as this is an abstract method.
        :returns: A dictionary containing the deserialized configuration data.
        """
        raise NotImplementedError
    
    @classmethod
    def serialize(cls, content:dict[str,Any])->bytes|str:
        """
        Serializes a dictionary into the target format.

        :param dict[str, Any] content: The dictionary to serialize.
        :raises NotImplementedError: Always raised, as this is an abstract method.
        :returns: The serialized content as bytes or a string.
        """
        raise NotImplementedError

class JsonSerializer(Serializer):
    """
    Serializer for JSON file formats.
    """
    @classmethod
    def deserialize(cls, content:bytes|str|Path)->dict[str,Any]:
        """
        Deserializes JSON content.

        :param bytes|str|Path content: The JSON content to deserialize.
        :returns: A dictionary representing the deserialized JSON data.
        """
        match type(content):
            case  Path() :
                content =content.read_text()
            case bytes() :
                content = content.encode(errors="replace")
        return json.loads(str(content))

class TomlSerializer(Serializer):
    """
    Serializer for TOML file formats.
    """
    @classmethod
    def deserialize(cls, content:bytes|str|Path)->dict[str,Any]:
        """
        Deserializes TOML content.

        :param bytes|str|Path content: The TOML content to deserialize.
        :returns: A dictionary representing the deserialized TOML data.
        """
        if isinstance(content,Path):
            content = content.read_text()
        elif isinstance(content, bytes):
                content = content.decode(errors="replace")
        return tomllib.loads(str(content))

class DevWebServerConfig:
    """
    Manages the loading and filtering of development web server configurations.

    :cvar tuple[Path, Path, Path] std_configs: Default configuration files to check.
    :cvar list filter: List of keys used to filter the configuration hierarchy.
    :cvar dict file_serial: Mapping of file suffixes to their respective serializers.
    :ivar dict _conf_dict: The internal storage for loaded configuration settings.
    :ivar Path _config_file: The path to the primary configuration file.
    """
    std_configs: tuple[Path, Path, Path] = (
        Path("package.json"),
        Path("pyproject.toml"),
        Path("devweb.toml"),
    )
    filter=["tool","devserver"]

    file_serial = {".toml": TomlSerializer,
                   ".json": JsonSerializer}

    def __init__(self) -> None:
        """
        Initializes the configuration manager with empty storage.
        """
        self._conf_dict:dict[str,Any] = {}
        self._config_file:Path=Path()

    def set_config(self, additional:str="")->Path|None:
        """
        Loads configurations from standard files and an optional additional path.

        :param str additional: Path to an additional configuration file.
        :returns: The path of the additional file if successfully loaded, otherwise None.
        """
        for path in self.std_configs:
            if path.is_file():
                # print(path)
                # print(path.read_text())
                # print(self.file_serial[path.suffix].deserialize(path))
                self._conf_dict.update(
                   self._filter(self.file_serial[path.suffix].deserialize(path),
                                filestem=path.stem)
                )
        add_path = Path(additional).resolve().expanduser()
        if add_path.is_file():
            self._conf_dict.update(
                self._filter(self.file_serial[path.suffix].deserialize(path), filestem=path.stem)
            )

    def _filter(self, config:dict[str,Any], filestem:str)->dict[str,Any]:
        """
        Filters the configuration dictionary based on pre-defined keys.

        :param dict[str, Any] config: The loaded configuration dictionary.
        :param str filestem: The filename stem used for context-aware filtering.
        :returns: The filtered configuration dictionary.
        """
        if filestem == "pyproject" and self.filter[0] not in config.keys():
            print("not in pyproject")
            return {}
        
        for filter_ in self.filter:
            if filestem == "pyproject" and filter_ not in config.keys():
                return {}
            if filter_ in config.keys():
                config = config[filter_]
        return config

    def convert(self) -> None:
        """
        Converts configuration values (e.g., strings) into appropriate types like Path objects.
        """
        root_dir = self._conf_dict.get("root_dir")
        if root_dir:
            self._conf_dict["root_dir"] = Path(root_dir)
        watch_dirs = self._conf_dict.get("watch_dirs")
        if watch_dirs and isinstance(watch_dirs, list):
            self._conf_dict["watch_dirs"] = [Path(p) for p in watch_dirs]
        cert_file = self._conf_dict.get("cert_file")
        if cert_file:
            self._conf_dict["cert_file"] = Path(cert_file)
        key_file = self._conf_dict.get("key_file")
        if key_file:
            self._conf_dict["key_file"] = Path(key_file)

    def as_default(self)->dict[str,Any]:
        """
        Returns the configuration dictionary for use in parser defaults.

        :returns: The current configuration dictionary.
        """
        return self._conf_dict

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
        "config.rst",
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
