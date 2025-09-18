from __future__ import annotations

from importlib import metadata
from typing import Iterable, List, Optional, Set

from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.application.ports.plugin_registry import PluginRegistryPort
from lychee.application.ports.schema_compiler import SchemaCompilerPort
from lychee.core.utils import get_logger
from lychee.infrastructure.languages.python_runtime_adapter import (
    PythonRuntimeAdapter,
)
from lychee.infrastructure.process.asyncio_manager import AsyncioProcessManagerAdapter
from lychee.infrastructure.schema.quicktype_python_compiler import (
    QuicktypePythonCompiler,
)

logger = get_logger(__name__)

# Entry point groups exposed for third-party plugins
EP_GROUP_LANG = "lychee.language_runtimes"
EP_GROUP_SCHEMA = "lychee.schema_compilers"


class EntryPointPluginRegistry(PluginRegistryPort):
    """
    Discovers plugins via Python entry points and provides access to them.

    Third-party packages can register entry points in their pyproject.toml, e.g.:

    [project.entry-points."lychee.language_runtimes"]
    lychee_python = "my_pkg.python_plugin:make_plugin"  # callable returning LanguageRuntimePort

    [project.entry-points."lychee.schema_compilers"]
    quicktype_py = "my_pkg.quicktype_plugin:QuicktypeCompiler"  # class implementing SchemaCompilerPort
    """

    def __init__(self, include_builtins: bool = True, allowed_entrypoint_names: Optional[Set[str]] = None) -> None:
        self._language_runtimes: List[LanguageRuntimePort] = []
        self._schema_compilers: List[SchemaCompilerPort] = []
        self._allowed_entrypoint_names: Optional[Set[str]] = (
            {name.lower() for name in allowed_entrypoint_names}
            if allowed_entrypoint_names
            else None
        )

        if include_builtins:
            # Wire built-ins so Lychee works out of the box
            pm = AsyncioProcessManagerAdapter()
            self._language_runtimes.append(PythonRuntimeAdapter(pm))
            self._schema_compilers.append(QuicktypePythonCompiler())

        self._load_entry_points()

    @classmethod
    def from_config(cls, config, include_builtins: bool = True) -> "EntryPointPluginRegistry":
        """
        Build a registry using `LycheeConfig` to optionally allowlist entry points.

        If `config.plugins` is non-empty, treat their `name` values as an allowlist of
        entry point names to load. Built-ins remain enabled by default.
        """
        allowed: Optional[Set[str]] = None
        try:
            plugins = getattr(config, "plugins", []) or []
            if plugins:
                allowed = {getattr(p, "name", "").lower() for p in plugins if getattr(p, "name", None)}
        except Exception:
            allowed = None
        return cls(include_builtins=include_builtins, allowed_entrypoint_names=allowed)

    def _load_entry_points(self) -> None:
        # Load language runtime plugins
        try:
            for ep in metadata.entry_points(group=EP_GROUP_LANG):  # type: ignore[attr-defined]
                try:
                    if self._allowed_entrypoint_names is not None and ep.name.lower() not in self._allowed_entrypoint_names:
                        logger.debug(f"Skipping language runtime plugin '{ep.name}' due to allowlist")
                        continue
                    obj = ep.load()
                    plugin = self._instantiate(obj, expected=LanguageRuntimePort)
                    if plugin is not None:
                        self._language_runtimes.append(plugin)
                        logger.info(f"Loaded language runtime plugin: {ep.name}")
                    else:
                        logger.warning(
                            f"Entry point '{ep.name}' did not provide a LanguageRuntimePort"
                        )
                except Exception as e:
                    logger.warning(f"Failed to load language runtime plugin '{ep.name}': {e}")
        except Exception as e:
            logger.debug(f"No entry points for {EP_GROUP_LANG}: {e}")

        # Load schema compiler plugins
        try:
            for ep in metadata.entry_points(group=EP_GROUP_SCHEMA):  # type: ignore[attr-defined]
                try:
                    if self._allowed_entrypoint_names is not None and ep.name.lower() not in self._allowed_entrypoint_names:
                        logger.debug(f"Skipping schema compiler plugin '{ep.name}' due to allowlist")
                        continue
                    obj = ep.load()
                    plugin = self._instantiate(obj, expected=SchemaCompilerPort)
                    if plugin is not None:
                        self._schema_compilers.append(plugin)
                        logger.info(f"Loaded schema compiler plugin: {ep.name}")
                    else:
                        logger.warning(
                            f"Entry point '{ep.name}' did not provide a SchemaCompilerPort"
                        )
                except Exception as e:
                    logger.warning(f"Failed to load schema compiler plugin '{ep.name}': {e}")
        except Exception as e:
            logger.debug(f"No entry points for {EP_GROUP_SCHEMA}: {e}")

    def _instantiate(self, obj, expected):
        # If it's already an instance of the expected type
        if isinstance(obj, expected):
            return obj
        # If it's a class, try to instantiate with no args
        try:
            if isinstance(obj, type):
                instance = obj()  # type: ignore[call-arg]
                if isinstance(instance, expected):
                    return instance
                return None
        except Exception:
            pass
        # If it's a factory/callable, call it and validate
        try:
            if callable(obj):
                produced = obj()
                if isinstance(produced, expected):
                    return produced
        except Exception:
            pass
        return None

    def get_language_runtime(self, language: str) -> Optional[LanguageRuntimePort]:
        language = language.lower()
        for rt in self._language_runtimes:
            try:
                if rt.language().lower() == language:
                    return rt
            except Exception:
                continue
        return None

    def get_schema_compiler(
        self, schema_format: str, language: str
    ) -> Optional[SchemaCompilerPort]:
        schema_format = schema_format.lower()
        language = language.lower()
        for comp in self._schema_compilers:
            try:
                if comp.supports(schema_format, language):
                    return comp
            except Exception:
                continue
        return None

    def list_language_runtimes(self) -> Iterable[LanguageRuntimePort]:
        return list(self._language_runtimes)

    def list_schema_compilers(self) -> Iterable[SchemaCompilerPort]:
        return list(self._schema_compilers)
