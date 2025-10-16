#!/usr/bin/env python3
"""
AIDP MCP Server - Comprehensive Implementation
Main server entry point with full module integration
"""
import asyncio
import sys
import time
import json
from typing import Any
import traceback

import mcp.types as types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configuration and utilities
from config.settings import get_settings
from src.oci_client import OCIClient
from utils.logger import setup_logging, get_logger, RequestLogger
from utils.formatters import format_error_response, format_json_response
from utils.errors import AIDPError

# Import all modules
from src.modules import (
    instance,
    catalog,
    storage,
    compute,
    notebooks,
    jobs,
    pipelines,
    connections,
    ml_models,
    analytics,
)

# Initialize logger
logger = get_logger(__name__)
request_logger = RequestLogger(logger)

# Initialize MCP server
server = Server("aidp-comprehensive")

# Global state
_settings = None
_oci_client = None


def initialize_server():
    """Initialize server components"""
    global _settings, _oci_client

    try:
        # Load settings
        _settings = get_settings()

        # Setup logging
        setup_logging(
            log_level=_settings.logging.level,
            log_file=_settings.logging.file,
            max_size_mb=_settings.logging.max_size_mb,
            backup_count=_settings.logging.backup_count,
        )

        logger.info("=" * 80)
        logger.info("AIDP MCP Server - Comprehensive Edition")
        logger.info("=" * 80)
        logger.info(f"Version: 1.0.0")
        logger.info(f"Active Instance: {_settings.active_instance_name}")
        logger.info(f"Region: {_settings.instance.region}")
        logger.info(f"Compartment: {_settings.instance.compartment_ocid}")
        logger.info(f"Namespace: {_settings.instance.namespace}")
        logger.info("=" * 80)

        # Initialize OCI client
        _oci_client = OCIClient(_settings)

        # Test connection
        logger.info("Testing OCI connection...")
        connection_test = _oci_client.test_connection()
        logger.info(f"Connection test results: {json.dumps(connection_test, indent=2)}")

        logger.info("Server initialization complete")

    except Exception as e:
        logger.error(f"Failed to initialize server: {str(e)}", exc_info=True)
        raise


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List all available tools from all modules
    Returns 150+ tools across 10 modules
    """
    logger.info("Listing all available tools")

    all_tools = []

    # Module 1: Instance Management (10 tools)
    if _settings.features.instance_management:
        all_tools.extend(instance.get_tools())
        logger.debug(f"Added {len(instance.get_tools())} instance management tools")

    # Module 2: Data Catalog (20 tools)
    if _settings.features.data_catalog:
        all_tools.extend(catalog.get_tools())
        logger.debug(f"Added {len(catalog.get_tools())} data catalog tools")

    # Module 3: Object Storage (20 tools)
    if _settings.features.object_storage:
        all_tools.extend(storage.get_tools())
        logger.debug(f"Added {len(storage.get_tools())} object storage tools")

    # Module 4: Compute Clusters (15 tools)
    if _settings.features.compute_clusters:
        all_tools.extend(compute.get_tools())
        logger.debug(f"Added {len(compute.get_tools())} compute cluster tools")

    # Module 5: Notebooks (15 tools)
    if _settings.features.notebooks:
        all_tools.extend(notebooks.get_tools())
        logger.debug(f"Added {len(notebooks.get_tools())} notebook tools")

    # Module 6: Jobs & Workflows (20 tools)
    if _settings.features.jobs_workflows:
        all_tools.extend(jobs.get_tools())
        logger.debug(f"Added {len(jobs.get_tools())} jobs & workflows tools")

    # Module 7: Data Pipelines (15 tools)
    if _settings.features.data_pipelines:
        all_tools.extend(pipelines.get_tools())
        logger.debug(f"Added {len(pipelines.get_tools())} data pipeline tools")

    # Module 8: External Connections (12 tools)
    if _settings.features.external_connections:
        all_tools.extend(connections.get_tools())
        logger.debug(f"Added {len(connections.get_tools())} external connection tools")

    # Module 9: ML Models (15 tools)
    if _settings.features.ml_models:
        all_tools.extend(ml_models.get_tools())
        logger.debug(f"Added {len(ml_models.get_tools())} ML model tools")

    # Module 10: Analytics & Reporting (10 tools)
    if _settings.features.analytics_reporting:
        all_tools.extend(analytics.get_tools())
        logger.debug(f"Added {len(analytics.get_tools())} analytics & reporting tools")

    logger.info(f"Total tools available: {len(all_tools)}")

    return all_tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution with routing to appropriate module
    """
    start_time = time.time()
    request_id = f"req_{int(start_time * 1000)}"

    # Log request
    request_logger.log_request(name, arguments or {}, request_id)

    try:
        if arguments is None:
            arguments = {}

        # Route to appropriate module based on tool name prefix or pattern
        result = None

        # Instance Management tools
        if name.startswith(("get_instance", "list_workspaces", "create_workspace",
                           "get_workspace", "update_workspace", "delete_workspace",
                           "grant_workspace", "revoke_workspace")):
            result = await instance.handle_tool_call(name, arguments, _oci_client)

        # Data Catalog tools
        elif name.startswith(("list_catalog", "search_catalog", "create_catalog",
                             "update_catalog", "delete_catalog", "get_data_lineage",
                             "list_databases", "get_database", "list_schemas",
                             "list_tables", "get_table", "preview_table",
                             "refresh_catalog", "set_object_tags", "get_object_tags",
                             "export_catalog", "import_catalog", "validate_catalog")):
            result = await catalog.handle_tool_call(name, arguments, _oci_client)

        # Object Storage tools
        elif name.startswith(("list_buckets", "create_bucket", "get_bucket",
                             "update_bucket", "delete_bucket", "list_objects",
                             "upload_object", "download_object", "get_object",
                             "update_object", "delete_object", "copy_object",
                             "move_object", "create_presigned", "list_object_versions",
                             "restore_object", "set_object_lifecycle", "get_bucket_lifecycle",
                             "bulk_upload", "bulk_download")):
            result = await storage.handle_tool_call(name, arguments, _oci_client)

        # Compute Cluster tools
        elif name.startswith("compute_"):
            result = await compute.handle_tool_call(name, arguments, _oci_client)

        # Notebook tools
        elif name.startswith("notebooks_"):
            result = await notebooks.handle_tool_call(name, arguments, _oci_client)

        # Jobs & Workflows tools
        elif name.startswith("jobs_"):
            result = await jobs.handle_tool_call(name, arguments, _oci_client)

        # Data Pipeline tools
        elif name.startswith("pipelines_"):
            result = await pipelines.handle_tool_call(name, arguments, _oci_client)

        # External Connection tools
        elif name.startswith("connections_"):
            result = await connections.handle_tool_call(name, arguments, _oci_client)

        # ML Model tools
        elif name.startswith("ml_models_"):
            result = await ml_models.handle_tool_call(name, arguments, _oci_client)

        # Analytics & Reporting tools
        elif name.startswith("analytics_"):
            result = await analytics.handle_tool_call(name, arguments, _oci_client)

        else:
            raise ValueError(f"Unknown tool: {name}")

        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000

        # Log success
        request_logger.log_response(name, True, execution_time_ms, request_id)

        # Format response
        response_text = format_json_response(result)

        return [types.TextContent(type="text", text=response_text)]

    except AIDPError as e:
        # Handle known AIDP errors
        execution_time_ms = (time.time() - start_time) * 1000
        request_logger.log_error(name, e, request_id)

        error_response = format_error_response(
            e,
            request_id=request_id,
            include_traceback=_settings.logging.level == "DEBUG",
        )

        response_text = format_json_response(error_response)

        return [types.TextContent(type="text", text=response_text)]

    except Exception as e:
        # Handle unexpected errors
        execution_time_ms = (time.time() - start_time) * 1000
        request_logger.log_error(name, e, request_id)

        logger.error(f"Unexpected error in tool '{name}':", exc_info=True)

        error_response = {
            "success": False,
            "error": {
                "type": "UnexpectedError",
                "message": str(e),
                "traceback": traceback.format_exc() if _settings.logging.level == "DEBUG" else None,
            },
            "metadata": {
                "request_id": request_id,
                "execution_time_ms": round(execution_time_ms, 2),
            },
        }

        response_text = format_json_response(error_response)

        return [types.TextContent(type="text", text=response_text)]


async def main():
    """Main server entry point"""
    try:
        # Initialize server components
        initialize_server()

        # Run MCP server
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            logger.info("Starting MCP server...")

            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="aidp-comprehensive",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if _oci_client:
            _oci_client.close()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
