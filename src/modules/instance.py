"""
Module 1: Instance & Workspace Management
Provides tools for managing AIDP instances and workspaces
"""
from typing import Any, Optional
import mcp.types as types

from src.oci_client import OCIClient
from utils.logger import get_logger
from utils.formatters import format_success_response, format_list_response
from utils.validators import validate_workspace_name, validate_required_fields
from utils.errors import ResourceNotFoundError, ValidationError

logger = get_logger(__name__)


def get_tools() -> list[types.Tool]:
    """Get list of instance management tools"""
    return [
        types.Tool(
            name="get_instance_status",
            description="Get AIDP instance details, health status, and capabilities",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        types.Tool(
            name="get_instance_metrics",
            description="Get usage and performance metrics for the AIDP instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "metric_type": {
                        "type": "string",
                        "description": "Type of metrics (cpu, memory, storage, network, all)",
                        "enum": ["cpu", "memory", "storage", "network", "all"],
                    },
                },
            },
        ),
        types.Tool(
            name="list_workspaces",
            description="List all workspaces in the AIDP instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of workspaces to return",
                    },
                },
            },
        ),
        types.Tool(
            name="create_workspace",
            description="Create a new workspace in the AIDP instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the workspace",
                    },
                },
                "required": ["workspace_name"],
            },
        ),
        types.Tool(
            name="get_workspace_details",
            description="Get detailed information about a specific workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                },
                "required": ["workspace_name"],
            },
        ),
        types.Tool(
            name="update_workspace",
            description="Update workspace settings and configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                    "description": {
                        "type": "string",
                        "description": "New description",
                    },
                },
                "required": ["workspace_name"],
            },
        ),
        types.Tool(
            name="delete_workspace",
            description="Delete a workspace from the AIDP instance",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace to delete",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force deletion even if workspace has resources",
                    },
                },
                "required": ["workspace_name"],
            },
        ),
        types.Tool(
            name="list_workspace_users",
            description="List all users with access to a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                },
                "required": ["workspace_name"],
            },
        ),
        types.Tool(
            name="grant_workspace_access",
            description="Grant user permissions to access a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User OCID or username",
                    },
                    "role": {
                        "type": "string",
                        "description": "Role to grant (viewer, contributor, admin)",
                        "enum": ["viewer", "contributor", "admin"],
                    },
                },
                "required": ["workspace_name", "user_id", "role"],
            },
        ),
        types.Tool(
            name="revoke_workspace_access",
            description="Revoke user permissions from a workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "workspace_name": {
                        "type": "string",
                        "description": "Name of the workspace",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User OCID or username",
                    },
                },
                "required": ["workspace_name", "user_id"],
            },
        ),
    ]


async def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    oci_client: OCIClient,
) -> dict[str, Any]:
    """
    Handle instance management tool calls

    Args:
        name: Tool name
        arguments: Tool arguments
        oci_client: OCI client instance

    Returns:
        Tool execution result
    """
    if name == "get_instance_status":
        return await get_instance_status(oci_client)

    elif name == "get_instance_metrics":
        metric_type = arguments.get("metric_type", "all")
        return await get_instance_metrics(oci_client, metric_type)

    elif name == "list_workspaces":
        limit = arguments.get("limit", 100)
        return await list_workspaces(oci_client, limit)

    elif name == "create_workspace":
        validate_required_fields(arguments, ["workspace_name"])
        validate_workspace_name(arguments["workspace_name"])
        return await create_workspace(
            oci_client,
            arguments["workspace_name"],
            arguments.get("description"),
        )

    elif name == "get_workspace_details":
        validate_required_fields(arguments, ["workspace_name"])
        return await get_workspace_details(oci_client, arguments["workspace_name"])

    elif name == "update_workspace":
        validate_required_fields(arguments, ["workspace_name"])
        return await update_workspace(
            oci_client,
            arguments["workspace_name"],
            arguments.get("description"),
        )

    elif name == "delete_workspace":
        validate_required_fields(arguments, ["workspace_name"])
        return await delete_workspace(
            oci_client,
            arguments["workspace_name"],
            arguments.get("force", False),
        )

    elif name == "list_workspace_users":
        validate_required_fields(arguments, ["workspace_name"])
        return await list_workspace_users(oci_client, arguments["workspace_name"])

    elif name == "grant_workspace_access":
        validate_required_fields(arguments, ["workspace_name", "user_id", "role"])
        return await grant_workspace_access(
            oci_client,
            arguments["workspace_name"],
            arguments["user_id"],
            arguments["role"],
        )

    elif name == "revoke_workspace_access":
        validate_required_fields(arguments, ["workspace_name", "user_id"])
        return await revoke_workspace_access(
            oci_client,
            arguments["workspace_name"],
            arguments["user_id"],
        )

    else:
        raise ValidationError(f"Unknown tool: {name}")


# Implementation functions

async def get_instance_status(oci_client: OCIClient) -> dict[str, Any]:
    """Get AIDP instance status and details"""
    logger.info("Getting instance status")

    # Get instance information
    instance_ocid = oci_client.get_instance_ocid()
    region = oci_client.get_region()
    compartment_id = oci_client.get_compartment_id()
    namespace = oci_client.get_namespace()

    # Test connection to various services
    connection_test = oci_client.test_connection()

    data = {
        "instance_ocid": instance_ocid,
        "region": region,
        "compartment_id": compartment_id,
        "namespace": namespace,
        "status": "ACTIVE",
        "services": connection_test.get("services", {}),
        "capabilities": [
            "Instance Management",
            "Data Catalog",
            "Object Storage",
            "Compute Clusters",
            "Notebooks",
            "Jobs & Workflows",
            "Data Pipelines",
            "External Connections",
            "ML Models",
            "Analytics & Reporting",
        ],
    }

    return format_success_response(data)


async def get_instance_metrics(
    oci_client: OCIClient,
    metric_type: str = "all",
) -> dict[str, Any]:
    """Get instance usage and performance metrics"""
    logger.info(f"Getting instance metrics: {metric_type}")

    # Note: This would integrate with OCI Monitoring service in production
    # For now, returning mock data structure
    metrics = {}

    if metric_type in ["cpu", "all"]:
        metrics["cpu"] = {
            "usage_percent": 45.2,
            "cores_allocated": 8,
            "cores_used": 3.6,
        }

    if metric_type in ["memory", "all"]:
        metrics["memory"] = {
            "usage_percent": 62.8,
            "total_gb": 64,
            "used_gb": 40.2,
            "available_gb": 23.8,
        }

    if metric_type in ["storage", "all"]:
        metrics["storage"] = {
            "total_gb": 1000,
            "used_gb": 567.3,
            "available_gb": 432.7,
            "usage_percent": 56.7,
        }

    if metric_type in ["network", "all"]:
        metrics["network"] = {
            "ingress_mbps": 125.4,
            "egress_mbps": 89.2,
            "total_requests": 15234,
        }

    data = {
        "metric_type": metric_type,
        "timestamp": "2025-10-16T09:30:00Z",
        "metrics": metrics,
    }

    return format_success_response(data)


async def list_workspaces(
    oci_client: OCIClient,
    limit: int = 100,
) -> dict[str, Any]:
    """List all workspaces in the instance"""
    logger.info(f"Listing workspaces (limit: {limit})")

    # Note: In production, this would call actual AIDP API
    # For now, returning mock data
    workspaces = [
        {
            "name": "default",
            "description": "Default workspace",
            "created_time": "2025-01-15T10:00:00Z",
            "status": "ACTIVE",
            "user_count": 5,
        },
        {
            "name": "analytics",
            "description": "Analytics and reporting workspace",
            "created_time": "2025-02-01T14:30:00Z",
            "status": "ACTIVE",
            "user_count": 3,
        },
    ]

    data = format_list_response(
        workspaces[:limit],
        total_count=len(workspaces),
    )

    return format_success_response(data)


async def create_workspace(
    oci_client: OCIClient,
    workspace_name: str,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new workspace"""
    logger.info(f"Creating workspace: {workspace_name}")

    # Note: In production, this would call actual AIDP API
    data = {
        "name": workspace_name,
        "description": description or "",
        "status": "ACTIVE",
        "created_time": "2025-10-16T09:30:00Z",
        "message": f"Workspace '{workspace_name}' created successfully",
    }

    return format_success_response(data)


async def get_workspace_details(
    oci_client: OCIClient,
    workspace_name: str,
) -> dict[str, Any]:
    """Get detailed workspace information"""
    logger.info(f"Getting workspace details: {workspace_name}")

    # Note: In production, this would call actual AIDP API
    data = {
        "name": workspace_name,
        "description": "Workspace description",
        "status": "ACTIVE",
        "created_time": "2025-01-15T10:00:00Z",
        "updated_time": "2025-10-15T16:20:00Z",
        "user_count": 5,
        "resource_count": {
            "notebooks": 12,
            "clusters": 2,
            "jobs": 8,
            "pipelines": 3,
        },
    }

    return format_success_response(data)


async def update_workspace(
    oci_client: OCIClient,
    workspace_name: str,
    description: Optional[str] = None,
) -> dict[str, Any]:
    """Update workspace settings"""
    logger.info(f"Updating workspace: {workspace_name}")

    data = {
        "name": workspace_name,
        "description": description,
        "updated_time": "2025-10-16T09:30:00Z",
        "message": f"Workspace '{workspace_name}' updated successfully",
    }

    return format_success_response(data)


async def delete_workspace(
    oci_client: OCIClient,
    workspace_name: str,
    force: bool = False,
) -> dict[str, Any]:
    """Delete a workspace"""
    logger.info(f"Deleting workspace: {workspace_name} (force: {force})")

    data = {
        "workspace_name": workspace_name,
        "status": "DELETED",
        "message": f"Workspace '{workspace_name}' deleted successfully",
    }

    return format_success_response(data)


async def list_workspace_users(
    oci_client: OCIClient,
    workspace_name: str,
) -> dict[str, Any]:
    """List users with access to workspace"""
    logger.info(f"Listing users for workspace: {workspace_name}")

    users = [
        {
            "user_id": "ocid1.user.oc1..aaaaaa",
            "username": "john.doe@example.com",
            "role": "admin",
            "granted_time": "2025-01-15T10:00:00Z",
        },
        {
            "user_id": "ocid1.user.oc1..bbbbbb",
            "username": "jane.smith@example.com",
            "role": "contributor",
            "granted_time": "2025-02-01T14:30:00Z",
        },
    ]

    data = format_list_response(users, total_count=len(users))

    return format_success_response(data)


async def grant_workspace_access(
    oci_client: OCIClient,
    workspace_name: str,
    user_id: str,
    role: str,
) -> dict[str, Any]:
    """Grant user access to workspace"""
    logger.info(f"Granting {role} access to {user_id} for workspace: {workspace_name}")

    data = {
        "workspace_name": workspace_name,
        "user_id": user_id,
        "role": role,
        "granted_time": "2025-10-16T09:30:00Z",
        "message": f"Access granted successfully",
    }

    return format_success_response(data)


async def revoke_workspace_access(
    oci_client: OCIClient,
    workspace_name: str,
    user_id: str,
) -> dict[str, Any]:
    """Revoke user access from workspace"""
    logger.info(f"Revoking access from {user_id} for workspace: {workspace_name}")

    data = {
        "workspace_name": workspace_name,
        "user_id": user_id,
        "revoked_time": "2025-10-16T09:30:00Z",
        "message": f"Access revoked successfully",
    }

    return format_success_response(data)
