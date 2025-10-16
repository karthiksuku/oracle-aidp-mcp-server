"""
Response formatting utilities for AIDP MCP Server
"""
from datetime import datetime, timezone
from typing import Any, Optional
import json
from .errors import AIDPError


def format_timestamp() -> str:
    """
    Generate an ISO 8601 formatted timestamp in UTC

    Returns:
        ISO 8601 formatted timestamp string
    """
    return datetime.now(timezone.utc).isoformat()


def format_success_response(
    data: Any,
    request_id: Optional[str] = None,
    execution_time_ms: Optional[float] = None,
) -> dict[str, Any]:
    """
    Format a successful response

    Args:
        data: The response data
        request_id: Optional request identifier
        execution_time_ms: Optional execution time in milliseconds

    Returns:
        Formatted response dictionary
    """
    response = {
        "success": True,
        "data": data,
        "metadata": {
            "timestamp": format_timestamp(),
        },
    }

    if request_id:
        response["metadata"]["request_id"] = request_id

    if execution_time_ms is not None:
        response["metadata"]["execution_time_ms"] = round(execution_time_ms, 2)

    return response


def format_error_response(
    error: Exception,
    request_id: Optional[str] = None,
    include_traceback: bool = False,
) -> dict[str, Any]:
    """
    Format an error response

    Args:
        error: The exception that occurred
        request_id: Optional request identifier
        include_traceback: Whether to include traceback information

    Returns:
        Formatted error response dictionary
    """
    error_data: dict[str, Any] = {
        "type": error.__class__.__name__,
        "message": str(error),
    }

    # If it's our custom error, include details
    if isinstance(error, AIDPError):
        if error.details:
            error_data["details"] = error.details
        if error.original_error and include_traceback:
            error_data["original_error"] = str(error.original_error)

    response = {
        "success": False,
        "error": error_data,
        "metadata": {
            "timestamp": format_timestamp(),
        },
    }

    if request_id:
        response["metadata"]["request_id"] = request_id

    return response


def format_list_response(
    items: list[Any],
    total_count: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
) -> dict[str, Any]:
    """
    Format a list/collection response with pagination metadata

    Args:
        items: List of items
        total_count: Total number of items available
        page: Current page number (1-indexed)
        page_size: Number of items per page

    Returns:
        Formatted response with pagination metadata
    """
    data: dict[str, Any] = {
        "items": items,
        "count": len(items),
    }

    if total_count is not None:
        data["total_count"] = total_count

    if page is not None and page_size is not None:
        data["pagination"] = {
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < (total_count or len(items)),
        }

    return data


def format_table_data(
    columns: list[str],
    rows: list[list[Any]],
    max_preview_rows: int = 10,
) -> dict[str, Any]:
    """
    Format table data (for catalog preview, query results, etc.)

    Args:
        columns: List of column names
        rows: List of row data
        max_preview_rows: Maximum number of rows to include

    Returns:
        Formatted table data
    """
    preview_rows = rows[:max_preview_rows] if len(rows) > max_preview_rows else rows

    return {
        "columns": columns,
        "rows": preview_rows,
        "total_rows": len(rows),
        "preview_rows": len(preview_rows),
        "truncated": len(rows) > max_preview_rows,
    }


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string (e.g., "2h 30m 15s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours < 24:
        return f"{hours}h {remaining_minutes}m"

    days = hours // 24
    remaining_hours = hours % 24

    return f"{days}d {remaining_hours}h"


def format_json_response(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty-printed JSON string

    Args:
        data: Data to format
        indent: Number of spaces for indentation

    Returns:
        JSON formatted string
    """
    return json.dumps(data, indent=indent, default=str, ensure_ascii=False)


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate a string to maximum length

    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated

    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
