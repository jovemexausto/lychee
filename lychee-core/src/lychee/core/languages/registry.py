"""Language adapter registry with async support."""

import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from lychee.core.config.models import ServiceConfig
from lychee.core.languages.adapter import LanguageAdapter
from lychee.core.languages.python import PythonAdapter

logger = logging.getLogger(__name__)


class LanguageAdapterRegistry:
    """Registry for language adapters with async support and enhanced features."""

    def __init__(self):
        self._adapters: Dict[str, Type[LanguageAdapter]] = {}
        self._adapter_cache: Dict[str, LanguageAdapter] = {}
        self._auto_detection_order: List[str] = []
        self._register_builtin_adapters()

    def _register_builtin_adapters(self) -> None:
        """Register built-in language adapters."""
        self.register("python", PythonAdapter)
        # self.register("typescript", TypeScriptAdapter)
        # Set detection order (more specific first)
        # self._auto_detection_order = ["typescript", "python"]

    def register(self, language: str, adapter_class: Type[LanguageAdapter]) -> None:
        """Register a language adapter."""
        if not issubclass(adapter_class, LanguageAdapter):
            raise ValueError(f"Adapter class must inherit from LanguageAdapter")

        self._adapters[language] = adapter_class
        logger.info(f"Registered language adapter: {language}")

        # Clear cache when new adapters are registered
        self._clear_cache()

    def unregister(self, language: str) -> bool:
        """Unregister a language adapter."""
        if language in self._adapters:
            del self._adapters[language]
            self._clear_cache_for_language(language)
            logger.info(f"Unregistered language adapter: {language}")
            return True
        return False

    def get_adapter_class(self, language: str) -> Optional[Type[LanguageAdapter]]:
        """Get a language adapter class by name."""
        return self._adapters.get(language)

    def get_adapter(
        self, service_config: ServiceConfig, cache_key: Optional[str] = None
    ) -> LanguageAdapter:
        """Get an adapter instance for a language."""
        language = service_config.type
        service_path = Path(service_config.path).resolve()

        if language not in self._adapters:
            raise ValueError(f"No adapter registered for language: {language}")

        # Create cache key
        if cache_key is None:
            cache_key = f"{language}:{service_path}:{hash(str(service_config))}"

        # Check cache first
        if cache_key in self._adapter_cache:
            return self._adapter_cache[cache_key]

        # Create new adapter instance
        adapter = self._adapters[language](service_path, service_config)

        # Cache the adapter
        self._adapter_cache[cache_key] = adapter

        return adapter

    async def detect_language(self, service_path: Path) -> Optional[str]:
        """Auto-detect the language of a service."""
        if not service_path.exists() or not service_path.is_dir():
            return None

        # Try each adapter in detection order
        for language in self._auto_detection_order:
            if language not in self._adapters:
                continue

            try:
                temp_config = ServiceConfig(path="tmp", type=language)

                # Create adapter instance
                adapter = self._adapters[language](service_path, temp_config)

                # Check if this adapter can handle the service
                if await self._can_handle_service(adapter, service_path):
                    logger.info(f"Detected language: {language} for {service_path}")
                    return language

            except Exception as e:
                logger.debug(f"Language detection failed for {language}: {e}")
                continue

        return None

    async def _can_handle_service(
        self, adapter: LanguageAdapter, service_path: Path
    ) -> bool:
        """Check if an adapter can handle a service."""
        try:
            # Basic validation
            validation_errors = await adapter.validate_service()
            if validation_errors:
                return False

            # Try to detect framework (if it succeeds, likely the right language)
            framework = await adapter.detect_framework()
            return framework is not None

        except Exception:
            return False

    async def get_service_info(
        self, service_path: Path, service_config: Optional[ServiceConfig] = None
    ) -> Dict[str, Any]:
        """Get comprehensive information about a service."""
        info = {
            "path": str(service_path),
            "exists": service_path.exists(),
            "language": None,
            "framework": None,
            "supported": False,
            "validation": None,
            "health": None,
        }

        if not service_path.exists():
            return info

        # Detect language if not provided
        language = None
        if service_config and service_config.type:
            language = service_config.type
        else:
            language = await self.detect_language(service_path)

        if not language:
            return info

        info["language"] = language
        info["supported"] = self.is_supported(language)

        if not info["supported"]:
            return info

        try:
            # Create service config if not provided
            if service_config is None:
                service_config = ServiceConfig(path=str(service_path), type=language)

            # Get adapter and gather information
            adapter = self.get_adapter(service_config)

            # Get framework
            info["framework"] = await adapter.detect_framework()

            # Get validation results
            info["errors"] = await adapter.validate_service()

            # Get health information
            info["health"] = await adapter.check_health()

        except Exception as e:
            info["error"] = str(e)
            logger.error(f"Failed to get service info for {service_path}: {e}")

        return info

    async def validate_all_services(
        self, services: Dict[str, tuple[Path, ServiceConfig]]
    ) -> Dict[str, Dict[str, Any]]:
        """Validate multiple services concurrently."""
        tasks = []
        service_names = []

        for name, (path, config) in services.items():
            task = self.get_service_info(path, config)
            tasks.append(task)
            service_names.append(name)

        # Run validations concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        validation_results = {}
        for name, result in zip(service_names, results):
            if isinstance(result, Exception):
                validation_results[name] = {"error": str(result), "supported": False}
            else:
                validation_results[name] = result

        return validation_results

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return list(self._adapters.keys())

    def is_supported(self, language: str) -> bool:
        """Check if a language is supported."""
        return language in self._adapters

    def get_adapter_info(self, language: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific adapter."""
        if language not in self._adapters:
            return None

        adapter_class = self._adapters[language]

        # Create temporary instance to get info
        try:
            temp_path = Path("/tmp")
            temp_config = ServiceConfig(path="tmp", type=language)
            temp_adapter = adapter_class(temp_path, temp_config)

            return {
                "language": language,
                "class_name": adapter_class.__name__,
                "module": adapter_class.__module__,
                "supported_frameworks": temp_adapter.supported_frameworks,
                "required_tools": temp_adapter.required_tools,
            }
        except Exception as e:
            return {
                "language": language,
                "class_name": adapter_class.__name__,
                "module": adapter_class.__module__,
                "error": str(e),
            }

    def set_detection_order(self, languages: List[str]) -> None:
        """Set the order for language auto-detection."""
        # Validate that all languages are registered
        for language in languages:
            if language not in self._adapters:
                raise ValueError(f"Language not registered: {language}")

        self._auto_detection_order = languages.copy()
        logger.info(f"Updated language detection order: {languages}")

    def get_detection_order(self) -> List[str]:
        """Get current language detection order."""
        return self._auto_detection_order.copy()

    def clear_cache(self) -> None:
        """Clear all cached adapter instances."""
        self._clear_cache()

    def _clear_cache(self) -> None:
        """Clear all cached adapters."""
        self._adapter_cache.clear()
        logger.debug("Cleared adapter cache")

    def _clear_cache_for_language(self, language: str) -> None:
        """Clear cached adapters for a specific language."""
        keys_to_remove = [
            k for k in self._adapter_cache.keys() if k.startswith(f"{language}:")
        ]
        for key in keys_to_remove:
            del self._adapter_cache[key]
        logger.debug(f"Cleared cache for language: {language}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self._adapter_cache),
            "cached_languages": list(
                set(k.split(":")[0] for k in self._adapter_cache.keys())
            ),
            "total_registered": len(self._adapters),
            "registered_languages": self.get_supported_languages(),
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check of the registry."""
        health = {
            "status": "healthy",
            "registered_adapters": len(self._adapters),
            "cached_adapters": len(self._adapter_cache),
            "detection_order": self._auto_detection_order,
            "adapter_health": {},
        }

        # Check each registered adapter
        for language in self._adapters:
            try:
                info = self.get_adapter_info(language)
                health["adapter_health"][language] = {"status": "healthy", "info": info}
            except Exception as e:
                health["adapter_health"][language] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"

        return health

    def __len__(self) -> int:
        """Return number of registered adapters."""
        return len(self._adapters)

    def __contains__(self, language: str) -> bool:
        """Check if language is supported."""
        return language in self._adapters

    def __iter__(self):
        """Iterate over supported languages."""
        return iter(self._adapters.keys())

    def __repr__(self) -> str:
        return f"LanguageAdapterRegistry(languages={list(self._adapters.keys())})"


# Global registry instance
language_registry = LanguageAdapterRegistry()
