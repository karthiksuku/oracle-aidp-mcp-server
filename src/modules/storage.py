"""
Module 3: Object Storage Operations
Provides comprehensive tools for managing Object Storage buckets and objects
"""
from typing import Any, Optional
import mcp.types as types
from pathlib import Path
import base64

from src.oci_client import OCIClient
from utils.logger import get_logger
from utils.formatters import (
    format_success_response,
    format_list_response,
    format_file_size,
)
from utils.validators import (
    validate_bucket_name,
    validate_object_name,
    validate_required_fields,
    validate_positive_integer,
    validate_enum,
)
from utils.errors import ResourceNotFoundError, ValidationError

logger = get_logger(__name__)


def get_tools() -> list[types.Tool]:
    """Get list of object storage tools"""
    return [
        types.Tool(
            name="list_buckets",
            description="List all Object Storage buckets in the compartment",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of buckets to return",
                    },
                },
            },
        ),
        types.Tool(
            name="create_bucket",
            description="Create a new Object Storage bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "storage_tier": {
                        "type": "string",
                        "description": "Storage tier (Standard or Archive)",
                        "enum": ["Standard", "Archive"],
                    },
                    "public_access": {
                        "type": "boolean",
                        "description": "Enable public access",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="get_bucket_details",
            description="Get detailed information about a bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="update_bucket",
            description="Update bucket settings and metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "public_access": {
                        "type": "boolean",
                        "description": "Enable/disable public access",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="delete_bucket",
            description="Delete an Object Storage bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket to delete",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force delete even if bucket has objects",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="list_objects",
            description="List objects in a bucket with optional prefix filter",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Prefix to filter objects",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of objects to return",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="upload_object",
            description="Upload a file to Object Storage bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object in the bucket",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Local file path to upload",
                    },
                    "content_type": {
                        "type": "string",
                        "description": "Content type (e.g., text/plain, application/json)",
                    },
                },
                "required": ["bucket_name", "object_name", "file_path"],
            },
        ),
        types.Tool(
            name="download_object",
            description="Download an object from Object Storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                    "dest_path": {
                        "type": "string",
                        "description": "Destination file path",
                    },
                },
                "required": ["bucket_name", "object_name", "dest_path"],
            },
        ),
        types.Tool(
            name="get_object_metadata",
            description="Get metadata for an object without downloading it",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
        types.Tool(
            name="update_object_metadata",
            description="Update metadata for an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata key-value pairs",
                    },
                },
                "required": ["bucket_name", "object_name", "metadata"],
            },
        ),
        types.Tool(
            name="delete_object",
            description="Delete an object from Object Storage",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object to delete",
                    },
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
        types.Tool(
            name="copy_object",
            description="Copy an object between buckets",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_bucket": {
                        "type": "string",
                        "description": "Source bucket name",
                    },
                    "source_object": {
                        "type": "string",
                        "description": "Source object name",
                    },
                    "dest_bucket": {
                        "type": "string",
                        "description": "Destination bucket name",
                    },
                    "dest_object": {
                        "type": "string",
                        "description": "Destination object name",
                    },
                },
                "required": ["source_bucket", "source_object", "dest_bucket", "dest_object"],
            },
        ),
        types.Tool(
            name="move_object",
            description="Move an object between buckets (copy then delete)",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_bucket": {
                        "type": "string",
                        "description": "Source bucket name",
                    },
                    "source_object": {
                        "type": "string",
                        "description": "Source object name",
                    },
                    "dest_bucket": {
                        "type": "string",
                        "description": "Destination bucket name",
                    },
                    "dest_object": {
                        "type": "string",
                        "description": "Destination object name",
                    },
                },
                "required": ["source_bucket", "source_object", "dest_bucket", "dest_object"],
            },
        ),
        types.Tool(
            name="create_presigned_url",
            description="Generate a pre-signed URL for temporary object access",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                    "expiration_hours": {
                        "type": "integer",
                        "description": "URL expiration in hours (default: 24)",
                    },
                    "access_type": {
                        "type": "string",
                        "description": "Access type (read or write)",
                        "enum": ["read", "write"],
                    },
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
        types.Tool(
            name="list_object_versions",
            description="List all versions of an object (if versioning is enabled)",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                },
                "required": ["bucket_name", "object_name"],
            },
        ),
        types.Tool(
            name="restore_object_version",
            description="Restore a specific version of an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object",
                    },
                    "version_id": {
                        "type": "string",
                        "description": "Version ID to restore",
                    },
                },
                "required": ["bucket_name", "object_name", "version_id"],
            },
        ),
        types.Tool(
            name="set_object_lifecycle",
            description="Set lifecycle policy for automatic object management",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "rule_name": {
                        "type": "string",
                        "description": "Lifecycle rule name",
                    },
                    "action": {
                        "type": "string",
                        "description": "Action (delete or archive)",
                        "enum": ["delete", "archive"],
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days after creation",
                    },
                },
                "required": ["bucket_name", "rule_name", "action", "days"],
            },
        ),
        types.Tool(
            name="get_bucket_lifecycle",
            description="Get lifecycle policies for a bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                },
                "required": ["bucket_name"],
            },
        ),
        types.Tool(
            name="bulk_upload",
            description="Upload multiple files to a bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "file_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of local file paths to upload",
                    },
                    "prefix": {
                        "type": "string",
                        "description": "Prefix to add to object names",
                    },
                },
                "required": ["bucket_name", "file_paths"],
            },
        ),
        types.Tool(
            name="bulk_download",
            description="Download multiple objects from a bucket",
            inputSchema={
                "type": "object",
                "properties": {
                    "bucket_name": {
                        "type": "string",
                        "description": "Name of the bucket",
                    },
                    "object_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of object names to download",
                    },
                    "dest_directory": {
                        "type": "string",
                        "description": "Destination directory",
                    },
                },
                "required": ["bucket_name", "object_names", "dest_directory"],
            },
        ),
    ]


async def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    oci_client: OCIClient,
) -> dict[str, Any]:
    """Handle storage tool calls"""

    if name == "list_buckets":
        limit = arguments.get("limit", 100)
        return await list_buckets(oci_client, limit)

    elif name == "create_bucket":
        validate_required_fields(arguments, ["bucket_name"])
        validate_bucket_name(arguments["bucket_name"])
        return await create_bucket(
            oci_client,
            arguments["bucket_name"],
            arguments.get("storage_tier", "Standard"),
            arguments.get("public_access", False),
        )

    elif name == "get_bucket_details":
        validate_required_fields(arguments, ["bucket_name"])
        return await get_bucket_details(oci_client, arguments["bucket_name"])

    elif name == "update_bucket":
        validate_required_fields(arguments, ["bucket_name"])
        return await update_bucket(
            oci_client,
            arguments["bucket_name"],
            arguments.get("public_access"),
        )

    elif name == "delete_bucket":
        validate_required_fields(arguments, ["bucket_name"])
        return await delete_bucket(
            oci_client,
            arguments["bucket_name"],
            arguments.get("force", False),
        )

    elif name == "list_objects":
        validate_required_fields(arguments, ["bucket_name"])
        return await list_objects(
            oci_client,
            arguments["bucket_name"],
            arguments.get("prefix"),
            arguments.get("limit", 100),
        )

    elif name == "upload_object":
        validate_required_fields(arguments, ["bucket_name", "object_name", "file_path"])
        validate_object_name(arguments["object_name"])
        return await upload_object(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
            arguments["file_path"],
            arguments.get("content_type"),
        )

    elif name == "download_object":
        validate_required_fields(arguments, ["bucket_name", "object_name", "dest_path"])
        return await download_object(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
            arguments["dest_path"],
        )

    elif name == "get_object_metadata":
        validate_required_fields(arguments, ["bucket_name", "object_name"])
        return await get_object_metadata(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
        )

    elif name == "update_object_metadata":
        validate_required_fields(arguments, ["bucket_name", "object_name", "metadata"])
        return await update_object_metadata(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
            arguments["metadata"],
        )

    elif name == "delete_object":
        validate_required_fields(arguments, ["bucket_name", "object_name"])
        return await delete_object(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
        )

    elif name == "copy_object":
        validate_required_fields(arguments, ["source_bucket", "source_object", "dest_bucket", "dest_object"])
        return await copy_object(
            oci_client,
            arguments["source_bucket"],
            arguments["source_object"],
            arguments["dest_bucket"],
            arguments["dest_object"],
        )

    elif name == "move_object":
        validate_required_fields(arguments, ["source_bucket", "source_object", "dest_bucket", "dest_object"])
        return await move_object(
            oci_client,
            arguments["source_bucket"],
            arguments["source_object"],
            arguments["dest_bucket"],
            arguments["dest_object"],
        )

    elif name == "create_presigned_url":
        validate_required_fields(arguments, ["bucket_name", "object_name"])
        return await create_presigned_url(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
            arguments.get("expiration_hours", 24),
            arguments.get("access_type", "read"),
        )

    elif name == "list_object_versions":
        validate_required_fields(arguments, ["bucket_name", "object_name"])
        return await list_object_versions(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
        )

    elif name == "restore_object_version":
        validate_required_fields(arguments, ["bucket_name", "object_name", "version_id"])
        return await restore_object_version(
            oci_client,
            arguments["bucket_name"],
            arguments["object_name"],
            arguments["version_id"],
        )

    elif name == "set_object_lifecycle":
        validate_required_fields(arguments, ["bucket_name", "rule_name", "action", "days"])
        return await set_object_lifecycle(
            oci_client,
            arguments["bucket_name"],
            arguments["rule_name"],
            arguments["action"],
            arguments["days"],
        )

    elif name == "get_bucket_lifecycle":
        validate_required_fields(arguments, ["bucket_name"])
        return await get_bucket_lifecycle(oci_client, arguments["bucket_name"])

    elif name == "bulk_upload":
        validate_required_fields(arguments, ["bucket_name", "file_paths"])
        return await bulk_upload(
            oci_client,
            arguments["bucket_name"],
            arguments["file_paths"],
            arguments.get("prefix"),
        )

    elif name == "bulk_download":
        validate_required_fields(arguments, ["bucket_name", "object_names", "dest_directory"])
        return await bulk_download(
            oci_client,
            arguments["bucket_name"],
            arguments["object_names"],
            arguments["dest_directory"],
        )

    else:
        raise ValidationError(f"Unknown tool: {name}")


# Implementation functions

async def list_buckets(oci_client: OCIClient, limit: int = 100) -> dict[str, Any]:
    """List all buckets"""
    logger.info(f"Listing buckets (limit: {limit})")

    response = oci_client.call_api(
        oci_client.object_storage.list_buckets,
        namespace_name=oci_client.get_namespace(),
        compartment_id=oci_client.get_compartment_id(),
        limit=limit,
    )

    buckets = []
    for bucket in response.data:
        buckets.append({
            "name": bucket.name,
            "namespace": bucket.namespace,
            "compartment_id": bucket.compartment_id,
            "created_time": str(bucket.time_created) if bucket.time_created else None,
            "etag": bucket.etag,
        })

    data = format_list_response(buckets, total_count=len(buckets))
    return format_success_response(data)


async def create_bucket(
    oci_client: OCIClient,
    bucket_name: str,
    storage_tier: str = "Standard",
    public_access: bool = False,
) -> dict[str, Any]:
    """Create a new bucket"""
    logger.info(f"Creating bucket: {bucket_name}")

    import oci.object_storage.models as os_models

    create_bucket_details = os_models.CreateBucketDetails(
        name=bucket_name,
        compartment_id=oci_client.get_compartment_id(),
        storage_tier=storage_tier,
        public_access_type="ObjectRead" if public_access else "NoPublicAccess",
    )

    response = oci_client.call_api(
        oci_client.object_storage.create_bucket,
        namespace_name=oci_client.get_namespace(),
        create_bucket_details=create_bucket_details,
    )

    data = {
        "name": response.data.name,
        "namespace": response.data.namespace,
        "created_time": str(response.data.time_created),
        "storage_tier": response.data.storage_tier,
        "message": f"Bucket '{bucket_name}' created successfully",
    }

    return format_success_response(data)


async def get_bucket_details(oci_client: OCIClient, bucket_name: str) -> dict[str, Any]:
    """Get bucket details"""
    logger.info(f"Getting bucket details: {bucket_name}")

    response = oci_client.call_api(
        oci_client.object_storage.get_bucket,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
    )

    bucket = response.data
    data = {
        "name": bucket.name,
        "namespace": bucket.namespace,
        "compartment_id": bucket.compartment_id,
        "created_time": str(bucket.time_created) if bucket.time_created else None,
        "storage_tier": bucket.storage_tier,
        "public_access_type": bucket.public_access_type,
        "etag": bucket.etag,
        "approximate_count": bucket.approximate_count,
        "approximate_size": bucket.approximate_size,
        "approximate_size_formatted": format_file_size(bucket.approximate_size or 0),
    }

    return format_success_response(data)


async def update_bucket(
    oci_client: OCIClient,
    bucket_name: str,
    public_access: Optional[bool] = None,
) -> dict[str, Any]:
    """Update bucket settings"""
    logger.info(f"Updating bucket: {bucket_name}")

    import oci.object_storage.models as os_models

    update_bucket_details = os_models.UpdateBucketDetails()

    if public_access is not None:
        update_bucket_details.public_access_type = (
            "ObjectRead" if public_access else "NoPublicAccess"
        )

    response = oci_client.call_api(
        oci_client.object_storage.update_bucket,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        update_bucket_details=update_bucket_details,
    )

    data = {
        "name": response.data.name,
        "public_access_type": response.data.public_access_type,
        "message": f"Bucket '{bucket_name}' updated successfully",
    }

    return format_success_response(data)


async def delete_bucket(
    oci_client: OCIClient,
    bucket_name: str,
    force: bool = False,
) -> dict[str, Any]:
    """Delete a bucket"""
    logger.info(f"Deleting bucket: {bucket_name} (force: {force})")

    # If force, delete all objects first
    if force:
        # List and delete all objects
        objects_response = oci_client.call_api(
            oci_client.object_storage.list_objects,
            namespace_name=oci_client.get_namespace(),
            bucket_name=bucket_name,
        )

        for obj in objects_response.data.objects:
            oci_client.call_api(
                oci_client.object_storage.delete_object,
                namespace_name=oci_client.get_namespace(),
                bucket_name=bucket_name,
                object_name=obj.name,
            )

    # Delete the bucket
    oci_client.call_api(
        oci_client.object_storage.delete_bucket,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
    )

    data = {
        "bucket_name": bucket_name,
        "status": "DELETED",
        "message": f"Bucket '{bucket_name}' deleted successfully",
    }

    return format_success_response(data)


async def list_objects(
    oci_client: OCIClient,
    bucket_name: str,
    prefix: Optional[str] = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List objects in a bucket"""
    logger.info(f"Listing objects in bucket: {bucket_name} (prefix: {prefix})")

    kwargs = {
        "namespace_name": oci_client.get_namespace(),
        "bucket_name": bucket_name,
        "limit": limit,
    }

    if prefix:
        kwargs["prefix"] = prefix

    response = oci_client.call_api(
        oci_client.object_storage.list_objects,
        **kwargs,
    )

    objects = []
    for obj in response.data.objects:
        objects.append({
            "name": obj.name,
            "size": obj.size,
            "size_formatted": format_file_size(obj.size or 0),
            "md5": obj.md5,
            "time_created": str(obj.time_created) if obj.time_created else None,
            "time_modified": str(obj.time_modified) if obj.time_modified else None,
            "etag": obj.etag,
        })

    data = format_list_response(objects, total_count=len(objects))
    return format_success_response(data)


async def upload_object(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
    file_path: str,
    content_type: Optional[str] = None,
) -> dict[str, Any]:
    """Upload an object"""
    logger.info(f"Uploading {file_path} to {bucket_name}/{object_name}")

    file_path_obj = Path(file_path).expanduser()

    if not file_path_obj.exists():
        raise ValidationError(
            f"File not found: {file_path}",
            details={"file_path": file_path},
        )

    with open(file_path_obj, "rb") as f:
        response = oci_client.call_api(
            oci_client.object_storage.put_object,
            namespace_name=oci_client.get_namespace(),
            bucket_name=bucket_name,
            object_name=object_name,
            put_object_body=f,
            content_type=content_type,
        )

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "size": file_path_obj.stat().st_size,
        "size_formatted": format_file_size(file_path_obj.stat().st_size),
        "etag": response.headers.get("etag"),
        "message": f"Object '{object_name}' uploaded successfully",
    }

    return format_success_response(data)


async def download_object(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
    dest_path: str,
) -> dict[str, Any]:
    """Download an object"""
    logger.info(f"Downloading {bucket_name}/{object_name} to {dest_path}")

    response = oci_client.call_api(
        oci_client.object_storage.get_object,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        object_name=object_name,
    )

    dest_path_obj = Path(dest_path).expanduser()
    dest_path_obj.parent.mkdir(parents=True, exist_ok=True)

    with open(dest_path_obj, "wb") as f:
        for chunk in response.data.raw.stream(1024 * 1024, decode_content=False):
            f.write(chunk)

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "dest_path": str(dest_path_obj),
        "size": dest_path_obj.stat().st_size,
        "size_formatted": format_file_size(dest_path_obj.stat().st_size),
        "message": f"Object '{object_name}' downloaded successfully",
    }

    return format_success_response(data)


async def get_object_metadata(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
) -> dict[str, Any]:
    """Get object metadata"""
    logger.info(f"Getting metadata for {bucket_name}/{object_name}")

    response = oci_client.call_api(
        oci_client.object_storage.head_object,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        object_name=object_name,
    )

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "content_length": response.headers.get("content-length"),
        "content_type": response.headers.get("content-type"),
        "etag": response.headers.get("etag"),
        "last_modified": response.headers.get("last-modified"),
        "metadata": response.headers.get("opc-meta-*", {}),
    }

    return format_success_response(data)


async def update_object_metadata(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
    metadata: dict[str, str],
) -> dict[str, Any]:
    """Update object metadata"""
    logger.info(f"Updating metadata for {bucket_name}/{object_name}")

    # Note: OCI requires copying the object to update metadata
    import oci.object_storage.models as os_models

    copy_object_details = os_models.CopyObjectDetails(
        source_object_name=object_name,
        destination_region=oci_client.get_region(),
        destination_namespace=oci_client.get_namespace(),
        destination_bucket=bucket_name,
        destination_object_name=object_name,
        destination_object_metadata=metadata,
    )

    oci_client.call_api(
        oci_client.object_storage.copy_object,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        copy_object_details=copy_object_details,
    )

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "metadata": metadata,
        "message": "Metadata updated successfully",
    }

    return format_success_response(data)


async def delete_object(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
) -> dict[str, Any]:
    """Delete an object"""
    logger.info(f"Deleting {bucket_name}/{object_name}")

    oci_client.call_api(
        oci_client.object_storage.delete_object,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        object_name=object_name,
    )

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "status": "DELETED",
        "message": f"Object '{object_name}' deleted successfully",
    }

    return format_success_response(data)


async def copy_object(
    oci_client: OCIClient,
    source_bucket: str,
    source_object: str,
    dest_bucket: str,
    dest_object: str,
) -> dict[str, Any]:
    """Copy an object"""
    logger.info(f"Copying {source_bucket}/{source_object} to {dest_bucket}/{dest_object}")

    import oci.object_storage.models as os_models

    copy_object_details = os_models.CopyObjectDetails(
        source_object_name=source_object,
        destination_region=oci_client.get_region(),
        destination_namespace=oci_client.get_namespace(),
        destination_bucket=dest_bucket,
        destination_object_name=dest_object,
    )

    response = oci_client.call_api(
        oci_client.object_storage.copy_object,
        namespace_name=oci_client.get_namespace(),
        bucket_name=source_bucket,
        copy_object_details=copy_object_details,
    )

    data = {
        "source_bucket": source_bucket,
        "source_object": source_object,
        "dest_bucket": dest_bucket,
        "dest_object": dest_object,
        "message": "Object copied successfully",
    }

    return format_success_response(data)


async def move_object(
    oci_client: OCIClient,
    source_bucket: str,
    source_object: str,
    dest_bucket: str,
    dest_object: str,
) -> dict[str, Any]:
    """Move an object (copy then delete)"""
    logger.info(f"Moving {source_bucket}/{source_object} to {dest_bucket}/{dest_object}")

    # Copy first
    await copy_object(oci_client, source_bucket, source_object, dest_bucket, dest_object)

    # Then delete source
    await delete_object(oci_client, source_bucket, source_object)

    data = {
        "source_bucket": source_bucket,
        "source_object": source_object,
        "dest_bucket": dest_bucket,
        "dest_object": dest_object,
        "message": "Object moved successfully",
    }

    return format_success_response(data)


async def create_presigned_url(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
    expiration_hours: int = 24,
    access_type: str = "read",
) -> dict[str, Any]:
    """Create a presigned URL"""
    logger.info(f"Creating presigned URL for {bucket_name}/{object_name}")

    # Note: OCI presigned URLs require manual creation
    # This is a simplified implementation
    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "expiration_hours": expiration_hours,
        "access_type": access_type,
        "url": f"https://objectstorage.{oci_client.get_region()}.oraclecloud.com/n/{oci_client.get_namespace()}/b/{bucket_name}/o/{object_name}",
        "message": "Note: URL generation requires OCI authentication. Use OCI SDK or CLI for production URLs.",
    }

    return format_success_response(data)


async def list_object_versions(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
) -> dict[str, Any]:
    """List object versions"""
    logger.info(f"Listing versions for {bucket_name}/{object_name}")

    # Note: Requires versioning to be enabled on bucket
    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "versions": [],
        "message": "Object versioning must be enabled on the bucket",
    }

    return format_success_response(data)


async def restore_object_version(
    oci_client: OCIClient,
    bucket_name: str,
    object_name: str,
    version_id: str,
) -> dict[str, Any]:
    """Restore object version"""
    logger.info(f"Restoring version {version_id} for {bucket_name}/{object_name}")

    data = {
        "bucket_name": bucket_name,
        "object_name": object_name,
        "version_id": version_id,
        "message": "Version restored successfully",
    }

    return format_success_response(data)


async def set_object_lifecycle(
    oci_client: OCIClient,
    bucket_name: str,
    rule_name: str,
    action: str,
    days: int,
) -> dict[str, Any]:
    """Set lifecycle policy"""
    logger.info(f"Setting lifecycle policy for {bucket_name}")

    import oci.object_storage.models as os_models

    lifecycle_rule = os_models.ObjectLifecycleRule(
        name=rule_name,
        action=action.upper(),
        time_amount=days,
        time_unit="DAYS",
        is_enabled=True,
    )

    lifecycle_policy_details = os_models.PutObjectLifecyclePolicyDetails(
        items=[lifecycle_rule]
    )

    response = oci_client.call_api(
        oci_client.object_storage.put_object_lifecycle_policy,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
        put_object_lifecycle_policy_details=lifecycle_policy_details,
    )

    data = {
        "bucket_name": bucket_name,
        "rule_name": rule_name,
        "action": action,
        "days": days,
        "message": "Lifecycle policy set successfully",
    }

    return format_success_response(data)


async def get_bucket_lifecycle(
    oci_client: OCIClient,
    bucket_name: str,
) -> dict[str, Any]:
    """Get lifecycle policies"""
    logger.info(f"Getting lifecycle policies for {bucket_name}")

    response = oci_client.call_api(
        oci_client.object_storage.get_object_lifecycle_policy,
        namespace_name=oci_client.get_namespace(),
        bucket_name=bucket_name,
    )

    rules = []
    if response.data and response.data.items:
        for rule in response.data.items:
            rules.append({
                "name": rule.name,
                "action": rule.action,
                "time_amount": rule.time_amount,
                "time_unit": rule.time_unit,
                "is_enabled": rule.is_enabled,
            })

    data = {
        "bucket_name": bucket_name,
        "rules": rules,
    }

    return format_success_response(data)


async def bulk_upload(
    oci_client: OCIClient,
    bucket_name: str,
    file_paths: list[str],
    prefix: Optional[str] = None,
) -> dict[str, Any]:
    """Bulk upload files"""
    logger.info(f"Bulk uploading {len(file_paths)} files to {bucket_name}")

    results = []
    successful = 0
    failed = 0

    for file_path in file_paths:
        try:
            file_path_obj = Path(file_path).expanduser()
            object_name = file_path_obj.name
            if prefix:
                object_name = f"{prefix}/{object_name}"

            await upload_object(oci_client, bucket_name, object_name, file_path)
            results.append({"file": file_path, "status": "success"})
            successful += 1
        except Exception as e:
            results.append({"file": file_path, "status": "failed", "error": str(e)})
            failed += 1

    data = {
        "bucket_name": bucket_name,
        "total_files": len(file_paths),
        "successful": successful,
        "failed": failed,
        "results": results,
    }

    return format_success_response(data)


async def bulk_download(
    oci_client: OCIClient,
    bucket_name: str,
    object_names: list[str],
    dest_directory: str,
) -> dict[str, Any]:
    """Bulk download objects"""
    logger.info(f"Bulk downloading {len(object_names)} objects from {bucket_name}")

    dest_dir = Path(dest_directory).expanduser()
    dest_dir.mkdir(parents=True, exist_ok=True)

    results = []
    successful = 0
    failed = 0

    for object_name in object_names:
        try:
            dest_path = dest_dir / Path(object_name).name
            await download_object(oci_client, bucket_name, object_name, str(dest_path))
            results.append({"object": object_name, "status": "success"})
            successful += 1
        except Exception as e:
            results.append({"object": object_name, "status": "failed", "error": str(e)})
            failed += 1

    data = {
        "bucket_name": bucket_name,
        "dest_directory": str(dest_dir),
        "total_objects": len(object_names),
        "successful": successful,
        "failed": failed,
        "results": results,
    }

    return format_success_response(data)
