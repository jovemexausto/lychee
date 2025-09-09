"""Configuration loading functionality."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml

from lychee.core.config.merger import ConfigMerger
from lychee.core.config.models import LycheeConfig
from lychee.core.utils import get_logger

logger = get_logger(__name__)


class ConfigLoader:
    """Loads and validates monorepo configuration."""

    def __init__(self, config_path: Path):
        self.config_path = config_path.resolve()
        self.merger = ConfigMerger()

    def load(self) -> LycheeConfig:
        """Load the complete configuration."""
        # Load main configuration
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        main_config = self._load_yaml_file(self.config_path)

        # Process includes
        if "includes" in main_config:
            for include_path in main_config["includes"]:
                include_full_path = self.config_path / include_path
                if include_full_path.exists():
                    include_config = self._load_yaml_file(include_full_path)
                    main_config = self.merger.merge(main_config, include_config)
                else:
                    logger.warning(f"Include file not found: {include_full_path}")

        # Load environment-specific overrides
        env_config = self._load_environment_config()
        if env_config:
            main_config = self.merger.merge(main_config, env_config)

        # Load local overrides
        local_config = self._load_local_config()
        if local_config:
            main_config = self.merger.merge(main_config, local_config)

        # Process environment variable substitution
        main_config = self._substitute_env_vars(main_config)

        # Validate and create model
        return LycheeConfig(**main_config)

    def _load_yaml_file(self, path: Path) -> Dict[str, Any]:
        """Load a YAML file."""
        try:
            with path.open("r") as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {path}: {e}")

    def _load_environment_config(self) -> Dict[str, Any]:
        """Load environment-specific configuration."""
        env = os.getenv("MONOREPO_ENV", "development")
        env_config_path = self.config_path / ".monorepo" / "environments" / f"{env}.yml"

        if env_config_path.exists():
            logger.debug(f"Loading environment config: {env_config_path}")
            return self._load_yaml_file(env_config_path)

        return {}

    def _load_local_config(self) -> Dict[str, Any]:
        """Load local configuration overrides."""
        local_config_path = self.config_path / ".monorepo" / "local.yml"

        if local_config_path.exists():
            logger.debug(f"Loading local config: {local_config_path}")
            return self._load_yaml_file(local_config_path)

        return {}

    def _substitute_env_vars(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute environment variables in configuration."""
        new_config = {}
        for key, value in config.items():
            new_config[key] = self._substitute_recursive_helper(value)
        return new_config

    def _substitute_recursive_helper(self, obj: Any) -> Any:
        if isinstance(obj, dict):
            return {k: self._substitute_recursive_helper(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_recursive_helper(item) for item in obj]
        elif isinstance(obj, str):
            return os.path.expandvars(obj)
        else:
            return obj
