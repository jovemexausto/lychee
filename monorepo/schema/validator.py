"""Schema validation utilities."""

from typing import Dict, List

from jsonschema import Draft7Validator, SchemaError, ValidationError, validate

from monorepo.utils.logging import get_logger

logger = get_logger(__name__)


class SchemaValidator:
    """Validates JSON schemas and data against schemas."""

    def validate_schema(self, schema: Dict) -> List[str]:
        """Validate a JSON schema itself."""
        errors = []

        try:
            # Validate against JSON Schema draft
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            errors.append(f"Invalid JSON Schema: {e.message}")

        # Additional custom validations
        errors.extend(self._validate_schema_structure(schema))

        return errors

    def validate_data_against_schema(self, data: Dict, schema: Dict) -> List[str]:
        """Validate data against a schema."""
        errors = []

        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            errors.append(f"Validation error: {e.message}")

        return errors

    def _validate_schema_structure(self, schema: Dict) -> List[str]:
        """Perform custom validation on schema structure."""
        errors = []

        # Check for required fields
        if "type" not in schema:
            errors.append("Schema must have a 'type' field")

        if "title" not in schema:
            errors.append("Schema should have a 'title' field")

        # Check properties structure
        if schema.get("type") == "object":
            if "properties" not in schema:
                errors.append("Object schemas should have 'properties'")
            else:
                # Validate property definitions
                for prop_name, prop_schema in schema["properties"].items():
                    if not isinstance(prop_schema, dict):
                        errors.append(f"Property '{prop_name}' should be an object")
                    elif "type" not in prop_schema:
                        errors.append(f"Property '{prop_name}' should have a type")

        return errors
