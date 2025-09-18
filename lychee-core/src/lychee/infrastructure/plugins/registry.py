from __future__ import annotations

from typing import Iterable, List, Optional

from lychee.application.ports.language_runtime import LanguageRuntimePort
from lychee.application.ports.plugin_registry import PluginRegistryPort
from lychee.application.ports.schema_compiler import SchemaCompilerPort
from lychee.infrastructure.languages.python_runtime_adapter import (
    PythonRuntimeAdapter,
)
from lychee.infrastructure.process.asyncio_manager import AsyncioProcessManagerAdapter
from lychee.infrastructure.schema.quicktype_python_compiler import (
    QuicktypePythonCompiler,
)


class InMemoryPluginRegistry(PluginRegistryPort):
    """Simple registry wiring built-ins; later replace with entry-point discovery."""

    def __init__(self) -> None:
        pm = AsyncioProcessManagerAdapter()
        self._language_runtimes: List[LanguageRuntimePort] = [
            PythonRuntimeAdapter(pm)
        ]
        self._schema_compilers: List[SchemaCompilerPort] = [QuicktypePythonCompiler()]

    def get_language_runtime(self, language: str) -> Optional[LanguageRuntimePort]:
        language = language.lower()
        for rt in self._language_runtimes:
            if rt.language().lower() == language:
                return rt
        return None

    def get_schema_compiler(
        self, schema_format: str, language: str
    ) -> Optional[SchemaCompilerPort]:
        schema_format = schema_format.lower()
        language = language.lower()
        for comp in self._schema_compilers:
            if comp.supports(schema_format, language):
                return comp
        return None

    def list_language_runtimes(self) -> Iterable[LanguageRuntimePort]:
        return list(self._language_runtimes)

    def list_schema_compilers(self) -> Iterable[SchemaCompilerPort]:
        return list(self._schema_compilers)
