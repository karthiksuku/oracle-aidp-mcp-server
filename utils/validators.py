"""
Input validation utilities for AIDP MCP Server
"""
import re
from typing import Any, Optional
from .errors import ValidationError


def validate_ocid(ocid: str, resource_type: Optional[str] = None) -> None:
    """
    Validate an Oracle Cloud Identifier (OCID)

    Args:
        ocid: The OCID to validate
        resource_type: Optional specific resource type to validate (e.g., 'compartment', 'instance')

    Raises:
        ValidationError: If OCID is invalid
    """
    if not ocid:
        raise ValidationError("OCID cannot be empty")

    # OCID format: ocid1.<resource_type>.<realm>.<region>.<unique_id>
    ocid_pattern = r"^ocid1\.[a-z0-9]+(\.[a-z0-9-]+){2,}\.[a-z0-9]+$"

    if not re.match(ocid_pattern, ocid, re.IGNORECASE):
        raise ValidationError(
            f"Invalid OCID format: {ocid}",
            details={"expected_format": "ocid1.<resource_type>.<realm>.<region>.<unique_id>"},
        )

    if resource_type:
        expected_prefix = f"ocid1.{resource_type}."
        if not ocid.lower().startswith(expected_prefix.lower()):
            raise ValidationError(
                f"OCID does not match expected resource type: {resource_type}",
                details={
                    "ocid": ocid,
                    "expected_prefix": expected_prefix,
                },
            )


def validate_bucket_name(bucket_name: str) -> None:
    """
    Validate an Object Storage bucket name

    Args:
        bucket_name: The bucket name to validate

    Raises:
        ValidationError: If bucket name is invalid
    """
    if not bucket_name:
        raise ValidationError("Bucket name cannot be empty")

    # Bucket name rules:
    # - Length: 1-256 characters
    # - Characters: alphanumeric, hyphen, underscore, period
    # - Cannot start/end with period
    # - No consecutive periods

    if len(bucket_name) > 256:
        raise ValidationError(
            "Bucket name too long (max 256 characters)",
            details={"length": len(bucket_name)},
        )

    if bucket_name.startswith(".") or bucket_name.endswith("."):
        raise ValidationError("Bucket name cannot start or end with a period")

    if ".." in bucket_name:
        raise ValidationError("Bucket name cannot contain consecutive periods")

    if not re.match(r"^[a-zA-Z0-9._-]+$", bucket_name):
        raise ValidationError(
            "Bucket name contains invalid characters",
            details={
                "bucket_name": bucket_name,
                "allowed_characters": "alphanumeric, hyphen, underscore, period",
            },
        )


def validate_object_name(object_name: str) -> None:
    """
    Validate an Object Storage object name

    Args:
        object_name: The object name to validate

    Raises:
        ValidationError: If object name is invalid
    """
    if not object_name:
        raise ValidationError("Object name cannot be empty")

    # Object name rules:
    # - Length: 1-1024 characters
    # - Most UTF-8 characters are allowed

    if len(object_name) > 1024:
        raise ValidationError(
            "Object name too long (max 1024 characters)",
            details={"length": len(object_name)},
        )


def validate_workspace_name(workspace_name: str) -> None:
    """
    Validate a workspace name

    Args:
        workspace_name: The workspace name to validate

    Raises:
        ValidationError: If workspace name is invalid
    """
    if not workspace_name:
        raise ValidationError("Workspace name cannot be empty")

    if len(workspace_name) > 100:
        raise ValidationError(
            "Workspace name too long (max 100 characters)",
            details={"length": len(workspace_name)},
        )

    if not re.match(r"^[a-zA-Z0-9_-]+$", workspace_name):
        raise ValidationError(
            "Workspace name contains invalid characters",
            details={
                "workspace_name": workspace_name,
                "allowed_characters": "alphanumeric, hyphen, underscore",
            },
        )


def validate_cluster_name(cluster_name: str) -> None:
    """
    Validate a cluster name

    Args:
        cluster_name: The cluster name to validate

    Raises:
        ValidationError: If cluster name is invalid
    """
    if not cluster_name:
        raise ValidationError("Cluster name cannot be empty")

    if len(cluster_name) > 100:
        raise ValidationError(
            "Cluster name too long (max 100 characters)",
            details={"length": len(cluster_name)},
        )

    if not re.match(r"^[a-zA-Z0-9_-]+$", cluster_name):
        raise ValidationError(
            "Cluster name contains invalid characters",
            details={
                "cluster_name": cluster_name,
                "allowed_characters": "alphanumeric, hyphen, underscore",
            },
        )


def validate_positive_integer(value: Any, field_name: str) -> int:
    """
    Validate that a value is a positive integer

    Args:
        value: The value to validate
        field_name: Name of the field for error messages

    Returns:
        The validated integer value

    Raises:
        ValidationError: If value is not a positive integer
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(
            f"{field_name} must be an integer",
            details={"value": value, "type": type(value).__name__},
        )

    if int_value <= 0:
        raise ValidationError(
            f"{field_name} must be positive",
            details={"value": int_value},
        )

    return int_value


def validate_enum(value: str, valid_values: list[str], field_name: str) -> str:
    """
    Validate that a value is one of the allowed enum values

    Args:
        value: The value to validate
        valid_values: List of valid values
        field_name: Name of the field for error messages

    Returns:
        The validated value

    Raises:
        ValidationError: If value is not in valid_values
    """
    if value not in valid_values:
        raise ValidationError(
            f"Invalid {field_name}",
            details={
                "value": value,
                "valid_values": valid_values,
            },
        )

    return value


def validate_required_fields(data: dict[str, Any], required_fields: list[str]) -> None:
    """
    Validate that all required fields are present in data

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Raises:
        ValidationError: If any required field is missing
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise ValidationError(
            "Missing required fields",
            details={"missing_fields": missing_fields},
        )
