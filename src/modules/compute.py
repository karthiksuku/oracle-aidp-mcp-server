"""
Module 4: Compute Cluster Management  
Uses OCI Data Flow for Spark cluster operations
"""
from typing import Any, Optional
import mcp.types as types

from src.oci_client import OCIClient
from utils.logger import get_logger
from utils.formatters import format_success_response, format_list_response
from utils.validators import validate_required_fields, validate_cluster_name
from utils.errors import ValidationError

logger = get_logger(__name__)


def get_tools() -> list[types.Tool]:
    """Get list of compute cluster tools"""
    return [
        types.Tool(
            name="list_clusters",
            description="List all Spark clusters (Data Flow applications)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of clusters to return",
                    },
                },
            },
        ),
        types.Tool(
            name="get_cluster_details",
            description="Get detailed information about a specific cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "Cluster/application OCID",
                    },
                },
                "required": ["cluster_id"],
            },
        ),
        types.Tool(
            name="create_cluster",
            description="Create a new Spark cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_name": {
                        "type": "string",
                        "description": "Name for the cluster",
                    },
                    "driver_shape": {
                        "type": "string",
                        "description": "Driver node shape (e.g., VM.Standard2.1)",
                    },
                    "executor_shape": {
                        "type": "string",
                        "description": "Executor node shape (e.g., VM.Standard2.1)",
                    },
                    "num_executors": {
                        "type": "integer",
                        "description": "Number of executor nodes",
                    },
                },
                "required": ["cluster_name"],
            },
        ),
        types.Tool(
            name="delete_cluster",
            description="Delete a Spark cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "Cluster/application OCID to delete",
                    },
                },
                "required": ["cluster_id"],
            },
        ),
        types.Tool(
            name="list_cluster_runs",
            description="List all runs/executions for clusters",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "Filter by specific cluster/application OCID",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of runs to return",
                    },
                },
            },
        ),
        types.Tool(
            name="get_run_details",
            description="Get details about a specific cluster run",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "Run OCID",
                    },
                },
                "required": ["run_id"],
            },
        ),
        types.Tool(
            name="create_run",
            description="Start a new run/execution on a cluster",
            inputSchema={
                "type": "object",
                "properties": {
                    "cluster_id": {
                        "type": "string",
                        "description": "Cluster/application OCID",
                    },
                    "display_name": {
                        "type": "string",
                        "description": "Display name for the run",
                    },
                },
                "required": ["cluster_id"],
            },
        ),
        types.Tool(
            name="delete_run",
            description="Delete a cluster run",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "Run OCID to delete",
                    },
                },
                "required": ["run_id"],
            },
        ),
        types.Tool(
            name="get_run_logs",
            description="Get logs from a cluster run",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "Run OCID",
                    },
                },
                "required": ["run_id"],
            },
        ),
        types.Tool(
            name="list_pools",
            description="List all resource pools",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of pools to return",
                    },
                },
            },
        ),
        types.Tool(
            name="get_pool_details",
            description="Get details about a resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_id": {
                        "type": "string",
                        "description": "Pool OCID",
                    },
                },
                "required": ["pool_id"],
            },
        ),
        types.Tool(
            name="create_pool",
            description="Create a new resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_name": {
                        "type": "string",
                        "description": "Name for the pool",
                    },
                    "node_count": {
                        "type": "integer",
                        "description": "Number of nodes in the pool",
                    },
                },
                "required": ["pool_name"],
            },
        ),
        types.Tool(
            name="start_pool",
            description="Start a stopped resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_id": {
                        "type": "string",
                        "description": "Pool OCID",
                    },
                },
                "required": ["pool_id"],
            },
        ),
        types.Tool(
            name="stop_pool",
            description="Stop a running resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_id": {
                        "type": "string",
                        "description": "Pool OCID",
                    },
                },
                "required": ["pool_id"],
            },
        ),
        types.Tool(
            name="delete_pool",
            description="Delete a resource pool",
            inputSchema={
                "type": "object",
                "properties": {
                    "pool_id": {
                        "type": "string",
                        "description": "Pool OCID",
                    },
                },
                "required": ["pool_id"],
            },
        ),
    ]


async def handle_tool_call(
    name: str,
    arguments: dict[str, Any],
    oci_client: OCIClient,
) -> dict[str, Any]:
    """Handle compute/cluster tool calls"""
    
    if name == "list_clusters":
        limit = arguments.get("limit", 100)
        return await list_clusters(oci_client, limit)
    
    elif name == "get_cluster_details":
        validate_required_fields(arguments, ["cluster_id"])
        return await get_cluster_details(oci_client, arguments["cluster_id"])
    
    elif name == "create_cluster":
        validate_required_fields(arguments, ["cluster_name"])
        return await create_cluster(
            oci_client,
            arguments["cluster_name"],
            arguments.get("driver_shape"),
            arguments.get("executor_shape"),
            arguments.get("num_executors"),
        )
    
    elif name == "delete_cluster":
        validate_required_fields(arguments, ["cluster_id"])
        return await delete_cluster(oci_client, arguments["cluster_id"])
    
    elif name == "list_cluster_runs":
        return await list_cluster_runs(
            oci_client,
            arguments.get("cluster_id"),
            arguments.get("limit", 100),
        )
    
    elif name == "get_run_details":
        validate_required_fields(arguments, ["run_id"])
        return await get_run_details(oci_client, arguments["run_id"])
    
    elif name == "create_run":
        validate_required_fields(arguments, ["cluster_id"])
        return await create_run(
            oci_client,
            arguments["cluster_id"],
            arguments.get("display_name"),
        )
    
    elif name == "delete_run":
        validate_required_fields(arguments, ["run_id"])
        return await delete_run(oci_client, arguments["run_id"])
    
    elif name == "get_run_logs":
        validate_required_fields(arguments, ["run_id"])
        return await get_run_logs(oci_client, arguments["run_id"])
    
    elif name == "list_pools":
        return await list_pools(oci_client, arguments.get("limit", 100))
    
    elif name == "get_pool_details":
        validate_required_fields(arguments, ["pool_id"])
        return await get_pool_details(oci_client, arguments["pool_id"])
    
    elif name == "create_pool":
        validate_required_fields(arguments, ["pool_name"])
        return await create_pool(
            oci_client,
            arguments["pool_name"],
            arguments.get("node_count"),
        )
    
    elif name == "start_pool":
        validate_required_fields(arguments, ["pool_id"])
        return await start_pool(oci_client, arguments["pool_id"])
    
    elif name == "stop_pool":
        validate_required_fields(arguments, ["pool_id"])
        return await stop_pool(oci_client, arguments["pool_id"])
    
    elif name == "delete_pool":
        validate_required_fields(arguments, ["pool_id"])
        return await delete_pool(oci_client, arguments["pool_id"])
    
    else:
        raise ValidationError(f"Unknown tool: {name}")


# Implementation functions using OCI Data Flow

async def list_clusters(oci_client: OCIClient, limit: int = 100) -> dict[str, Any]:
    """List all Spark clusters (Data Flow applications)"""
    logger.info(f"Listing clusters/applications (limit: {limit})")
    
    response = oci_client.call_api(
        oci_client.data_flow.list_applications,
        compartment_id=oci_client.get_compartment_id(),
        limit=limit,
    )
    
    clusters = []
    for app in response.data:
        clusters.append({
            "id": app.id,
            "name": app.display_name,
            "language": app.language,
            "spark_version": app.spark_version,
            "state": app.lifecycle_state,
            "time_created": str(app.time_created) if app.time_created else None,
        })
    
    data = format_list_response(clusters, total_count=len(clusters))
    return format_success_response(data)


async def get_cluster_details(oci_client: OCIClient, cluster_id: str) -> dict[str, Any]:
    """Get cluster details"""
    logger.info(f"Getting cluster details: {cluster_id}")
    
    response = oci_client.call_api(
        oci_client.data_flow.get_application,
        application_id=cluster_id,
    )
    
    app = response.data
    data = {
        "id": app.id,
        "name": app.display_name,
        "description": app.description,
        "language": app.language,
        "spark_version": app.spark_version,
        "driver_shape": app.driver_shape,
        "executor_shape": app.executor_shape,
        "num_executors": app.num_executors,
        "state": app.lifecycle_state,
        "time_created": str(app.time_created) if app.time_created else None,
        "time_updated": str(app.time_updated) if app.time_updated else None,
    }
    
    return format_success_response(data)


async def create_cluster(
    oci_client: OCIClient,
    cluster_name: str,
    driver_shape: Optional[str] = None,
    executor_shape: Optional[str] = None,
    num_executors: Optional[int] = None,
) -> dict[str, Any]:
    """Create a new Spark cluster"""
    logger.info(f"Creating cluster: {cluster_name}")
    
    import oci.data_flow.models as df_models
    
    create_details = df_models.CreateApplicationDetails(
        compartment_id=oci_client.get_compartment_id(),
        display_name=cluster_name,
        language="PYTHON",
        spark_version=oci_client.settings.defaults.cluster_size or "3.2.1",
        driver_shape=driver_shape or "VM.Standard2.1",
        executor_shape=executor_shape or "VM.Standard2.1",
        num_executors=num_executors or 2,
        file_uri="oci://bucket@namespace/path/app.py",  # Placeholder
    )
    
    response = oci_client.call_api(
        oci_client.data_flow.create_application,
        create_application_details=create_details,
    )
    
    data = {
        "id": response.data.id,
        "name": response.data.display_name,
        "state": response.data.lifecycle_state,
        "message": f"Cluster '{cluster_name}' created successfully",
    }
    
    return format_success_response(data)


async def delete_cluster(oci_client: OCIClient, cluster_id: str) -> dict[str, Any]:
    """Delete a cluster"""
    logger.info(f"Deleting cluster: {cluster_id}")
    
    oci_client.call_api(
        oci_client.data_flow.delete_application,
        application_id=cluster_id,
    )
    
    data = {
        "cluster_id": cluster_id,
        "status": "DELETED",
        "message": "Cluster deleted successfully",
    }
    
    return format_success_response(data)


async def list_cluster_runs(
    oci_client: OCIClient,
    cluster_id: Optional[str] = None,
    limit: int = 100,
) -> dict[str, Any]:
    """List cluster runs"""
    logger.info(f"Listing cluster runs (cluster: {cluster_id}, limit: {limit})")
    
    kwargs = {
        "compartment_id": oci_client.get_compartment_id(),
        "limit": limit,
    }
    
    if cluster_id:
        kwargs["application_id"] = cluster_id
    
    response = oci_client.call_api(
        oci_client.data_flow.list_runs,
        **kwargs,
    )
    
    runs = []
    for run in response.data:
        runs.append({
            "id": run.id,
            "display_name": run.display_name,
            "application_id": run.application_id,
            "state": run.lifecycle_state,
            "time_created": str(run.time_created) if run.time_created else None,
            "time_updated": str(run.time_updated) if run.time_updated else None,
        })
    
    data = format_list_response(runs, total_count=len(runs))
    return format_success_response(data)


async def get_run_details(oci_client: OCIClient, run_id: str) -> dict[str, Any]:
    """Get run details"""
    logger.info(f"Getting run details: {run_id}")
    
    response = oci_client.call_api(
        oci_client.data_flow.get_run,
        run_id=run_id,
    )
    
    run = response.data
    data = {
        "id": run.id,
        "display_name": run.display_name,
        "application_id": run.application_id,
        "state": run.lifecycle_state,
        "time_created": str(run.time_created) if run.time_created else None,
        "time_updated": str(run.time_updated) if run.time_updated else None,
    }
    
    return format_success_response(data)


async def create_run(
    oci_client: OCIClient,
    cluster_id: str,
    display_name: Optional[str] = None,
) -> dict[str, Any]:
    """Create a new run"""
    logger.info(f"Creating run for cluster: {cluster_id}")
    
    import oci.data_flow.models as df_models
    
    create_details = df_models.CreateRunDetails(
        compartment_id=oci_client.get_compartment_id(),
        application_id=cluster_id,
        display_name=display_name or f"Run-{cluster_id[:8]}",
    )
    
    response = oci_client.call_api(
        oci_client.data_flow.create_run,
        create_run_details=create_details,
    )
    
    data = {
        "id": response.data.id,
        "display_name": response.data.display_name,
        "state": response.data.lifecycle_state,
        "message": "Run created successfully",
    }
    
    return format_success_response(data)


async def delete_run(oci_client: OCIClient, run_id: str) -> dict[str, Any]:
    """Delete a run"""
    logger.info(f"Deleting run: {run_id}")
    
    oci_client.call_api(
        oci_client.data_flow.delete_run,
        run_id=run_id,
    )
    
    data = {
        "run_id": run_id,
        "status": "DELETED",
        "message": "Run deleted successfully",
    }
    
    return format_success_response(data)


async def get_run_logs(oci_client: OCIClient, run_id: str) -> dict[str, Any]:
    """Get run logs"""
    logger.info(f"Getting logs for run: {run_id}")
    
    response = oci_client.call_api(
        oci_client.data_flow.list_run_logs,
        run_id=run_id,
    )
    
    logs = []
    for log in response.data:
        logs.append({
            "name": log.name,
            "size_in_bytes": log.size_in_bytes,
            "time_created": str(log.time_created) if log.time_created else None,
            "type": log.type,
        })
    
    data = format_list_response(logs, total_count=len(logs))
    return format_success_response(data)


async def list_pools(oci_client: OCIClient, limit: int = 100) -> dict[str, Any]:
    """List resource pools"""
    logger.info(f"Listing resource pools (limit: {limit})")
    
    response = oci_client.call_api(
        oci_client.data_flow.list_pools,
        compartment_id=oci_client.get_compartment_id(),
        limit=limit,
    )
    
    pools = []
    for pool in response.data:
        pools.append({
            "id": pool.id,
            "name": pool.display_name,
            "state": pool.lifecycle_state,
            "time_created": str(pool.time_created) if pool.time_created else None,
        })
    
    data = format_list_response(pools, total_count=len(pools))
    return format_success_response(data)


async def get_pool_details(oci_client: OCIClient, pool_id: str) -> dict[str, Any]:
    """Get pool details"""
    logger.info(f"Getting pool details: {pool_id}")
    
    response = oci_client.call_api(
        oci_client.data_flow.get_pool,
        pool_id=pool_id,
    )
    
    pool = response.data
    data = {
        "id": pool.id,
        "name": pool.display_name,
        "description": pool.description,
        "state": pool.lifecycle_state,
        "time_created": str(pool.time_created) if pool.time_created else None,
        "time_updated": str(pool.time_updated) if pool.time_updated else None,
    }
    
    return format_success_response(data)


async def create_pool(
    oci_client: OCIClient,
    pool_name: str,
    node_count: Optional[int] = None,
) -> dict[str, Any]:
    """Create a resource pool"""
    logger.info(f"Creating pool: {pool_name}")
    
    import oci.data_flow.models as df_models
    
    pool_config = df_models.PoolConfig(
        shape="VM.Standard2.1",
        min=node_count or 1,
        max=node_count or 10,
    )
    
    create_details = df_models.CreatePoolDetails(
        compartment_id=oci_client.get_compartment_id(),
        display_name=pool_name,
        configurations=[pool_config],
    )
    
    response = oci_client.call_api(
        oci_client.data_flow.create_pool,
        create_pool_details=create_details,
    )
    
    data = {
        "id": response.data.id,
        "name": response.data.display_name,
        "state": response.data.lifecycle_state,
        "message": f"Pool '{pool_name}' created successfully",
    }
    
    return format_success_response(data)


async def start_pool(oci_client: OCIClient, pool_id: str) -> dict[str, Any]:
    """Start a pool"""
    logger.info(f"Starting pool: {pool_id}")
    
    oci_client.call_api(
        oci_client.data_flow.start_pool,
        pool_id=pool_id,
    )
    
    data = {
        "pool_id": pool_id,
        "status": "STARTING",
        "message": "Pool started successfully",
    }
    
    return format_success_response(data)


async def stop_pool(oci_client: OCIClient, pool_id: str) -> dict[str, Any]:
    """Stop a pool"""
    logger.info(f"Stopping pool: {pool_id}")
    
    oci_client.call_api(
        oci_client.data_flow.stop_pool,
        pool_id=pool_id,
    )
    
    data = {
        "pool_id": pool_id,
        "status": "STOPPING",
        "message": "Pool stopped successfully",
    }
    
    return format_success_response(data)


async def delete_pool(oci_client: OCIClient, pool_id: str) -> dict[str, Any]:
    """Delete a pool"""
    logger.info(f"Deleting pool: {pool_id}")
    
    oci_client.call_api(
        oci_client.data_flow.delete_pool,
        pool_id=pool_id,
    )
    
    data = {
        "pool_id": pool_id,
        "status": "DELETED",
        "message": "Pool deleted successfully",
    }
    
    return format_success_response(data)
