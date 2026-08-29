"""
Schema validation helper.

Given a JSON response body and a path to a JSON Schema file,
raises a clear error if the response doesn't match the expected shape.
"""

import json
from pathlib import Path
from jsonschema import validate, ValidationError


def validate_schema(instance, schema_path: str):
    schema_file = Path(schema_path)
    with open(schema_file) as f:
        schema = json.load(f)

    try:
        validate(instance=instance, schema=schema)
    except ValidationError as e:
        raise AssertionError(
            f"Schema validation failed for {schema_path}:\n{e.message}"
        ) from e
