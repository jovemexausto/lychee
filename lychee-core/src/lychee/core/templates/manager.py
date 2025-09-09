"""Manages project and service templates for the monorepo."""

import os
import shutil
from pathlib import Path
from typing import Any, Dict, List

from lychee.core.utils import get_logger

# Use a simple templating placeholder for now.
# For more advanced use cases, a library like Jinja2 would be more suitable.
TEMPLATE_PREFIX = "{{"
TEMPLATE_SUFFIX = "}}"

logger = get_logger(__name__)


class TemplateManager:
    """
    Manages the creation of projects and services from templates.

    The templates are located in the `monorepo/templates/templates` directory.
    """

    def __init__(self):
        """Initializes the TemplateManager."""
        self.templates_dir = Path(__file__).parent / "templates"

    def list_templates(self) -> List[str]:
        """
        Lists all available templates.

        Returns:
            List[str]: A list of template names.
        """
        if not self.templates_dir.exists():
            logger.warning("Templates directory not found. No templates available.")
            return []

        return [d.name for d in self.templates_dir.iterdir() if d.is_dir()]

    def get_template_path(self, template_name: str) -> Path:
        """
        Gets the full path to a template directory.

        Args:
            template_name (str): The name of the template.

        Returns:
            Path: The full path to the template directory.

        Raises:
            ValueError: If the template does not exist.
        """
        template_path = self.templates_dir / template_name
        if not template_path.is_dir():
            raise ValueError(f"Template '{template_name}' not found.")
        return template_path

    def create_project(self, name: str, path: Path, template: str) -> None:
        """
        Creates a new monorepo project from a template.

        Args:
            name (str): The name of the project.
            path (Path): The destination directory for the new project.
            template (str): The name of the project template to use.
        """
        logger.info(
            f"Creating new project '{name}' at '{path}' using template '{template}'"
        )
        context = {
            "project_name": name,
            "project_path": str(path),
        }
        self.create_from_template(template, path, context)
        logger.info(f"Project '{name}' successfully created.")

    def create_service(self, name: str, path: Path, template: str) -> None:
        """
        Creates a new service from a template.

        Args:
            name (str): The name of the service.
            path (Path): The destination directory for the new service.
            template (str): The name of the service template to use.
        """
        logger.info(
            f"Creating new service '{name}' at '{path}' using template '{template}'"
        )
        context = {
            "service_name": name,
            "service_path": str(path),
        }
        self.create_from_template(template, path, context)
        logger.info(f"Service '{name}' successfully created.")

    def create_from_template(
        self, template_name: str, dest_path: Path, context: Dict[str, Any]
    ) -> None:
        """
        Creates a new project or service from a template.

        Args:
            template_name (str): The name of the template to use.
            dest_path (Path): The destination directory for the new project.
            context (Dict[str, Any]): A dictionary of variables for templating.

        Raises:
            FileExistsError: If the destination path already exists.
        """
        logger.info(f"Creating project from template: '{template_name}'")

        # Get the path to the template
        template_path = self.get_template_path(template_name)

        # Check if the destination already exists
        if dest_path.exists():
            raise FileExistsError(f"Destination path already exists: '{dest_path}'")

        # Copy the template to the destination
        shutil.copytree(template_path, dest_path)
        logger.info(f"Copied template to: '{dest_path}'")

        # Walk through the new directory and replace placeholders in files
        for root, dirs, files in os.walk(dest_path):
            current_path = Path(root)

            # Handle directory name templating
            for i, d in enumerate(dirs):
                new_d = self._apply_templating(d, context)
                if new_d != d:
                    os.rename(current_path / d, current_path / new_d)
                    dirs[i] = new_d  # Update the list of directories

            # Handle file content and name templating
            for f in files:
                file_path = current_path / f

                # Apply templating to filename
                new_f = self._apply_templating(f, context)
                if new_f != f:
                    file_path.rename(current_path / new_f)
                    file_path = current_path / new_f  # Update the file path

                # Read, replace, and write file content
                try:
                    content = file_path.read_text(encoding="utf-8")
                    templated_content = self._apply_templating(content, context)
                    if templated_content != content:
                        file_path.write_text(templated_content, encoding="utf-8")
                        logger.debug(f"Templated file content: {file_path}")
                except UnicodeDecodeError:
                    # Skip binary files
                    logger.debug(f"Skipping binary file: {file_path}")
                    continue

        logger.info(f"Successfully created project from template at: '{dest_path}'")

    def _apply_templating(self, text: str, context: Dict[str, Any]) -> str:
        """
        Replaces placeholders in a string with values from the context.

        Args:
            text (str): The string with placeholders.
            context (Dict[str, Any]): The variables to use for replacement.

        Returns:
            str: The string with placeholders replaced.
        """
        for key, value in context.items():
            placeholder = f"{TEMPLATE_PREFIX}{key}{TEMPLATE_SUFFIX}"
            text = text.replace(placeholder, str(value))
        return text
