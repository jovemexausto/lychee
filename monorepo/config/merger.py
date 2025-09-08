"""
Configuration merger utility.

This module provides a class to deeply merge configuration dictionaries,
allowing for the combination of default settings with user-specific overrides.
"""

from typing import Any, Dict, List

from monorepo.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigMerger:
    """
    A class for recursively merging configuration dictionaries.

    The merge operation is non-destructive and creates a new dictionary.
    """

    def merge(self, source: Dict[str, Any], overrides: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merges a dictionary of overrides into a source dictionary.

        The values in the 'overrides' dictionary will take precedence. For nested
        dictionaries, the merge is performed recursively.

        Args:
            source (Dict[str, Any]): The base dictionary to be merged into.
            overrides (Dict[str, Any]): The dictionary containing values to override
                                        the source.

        Returns:
            Dict[str, Any]: A new dictionary representing the merged configuration.
        """
        merged = source.copy()

        for key, value in overrides.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                merged[key] = self.merge(merged[key], value)
            else:
                # Override simple values or lists
                merged[key] = value

        return merged

    def merge_multiple(self, configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sequentially merges a list of configuration dictionaries.

        Args:
            configs (List[Dict[str, Any]]): A list of dictionaries to merge.
                                            Later dictionaries in the list will
                                            override earlier ones.

        Returns:
            Dict[str, Any]: The final, merged configuration dictionary.
        """
        if not configs:
            return {}

        base_config = configs[0]
        for override_config in configs[1:]:
            base_config = self.merge(base_config, override_config)

        return base_config
