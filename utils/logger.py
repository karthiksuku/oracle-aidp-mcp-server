"""
Logging configuration for AIDP MCP Server
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional
import colorlog


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_size_mb: int = 100,
    backup_count: int = 5,
) -> None:
    """
    Setup logging configuration for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (optional)
        max_size_mb: Maximum log file size in MB before rotation
        backup_count: Number of backup files to keep
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatters
    console_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s%(reset)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [%(filename)s:%(lineno)d]",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Only add console handler if not running as MCP server (detect by checking if stdin is a pipe)
    # MCP servers communicate via stdin/stdout, so we should NOT log to console
    import os
    is_mcp_server = not os.isatty(0)  # stdin is not a terminal = likely MCP server

    if not is_mcp_server:
        # Console handler (only for interactive/debug mode)
        console_handler = logging.StreamHandler(sys.stderr)  # Use stderr, not stdout
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler (if log_file specified)
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

    # Set levels for noisy libraries
    logging.getLogger("oci").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the specified module

    Args:
        name: Module name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class RequestLogger:
    """Helper class for logging API requests and responses"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log_request(
        self, tool_name: str, arguments: dict, request_id: Optional[str] = None
    ) -> None:
        """Log an incoming tool request"""
        log_data = {
            "tool": tool_name,
            "args": arguments,
        }
        if request_id:
            log_data["request_id"] = request_id

        self.logger.info(f"Received request: {log_data}")

    def log_response(
        self,
        tool_name: str,
        success: bool,
        execution_time_ms: float,
        request_id: Optional[str] = None,
    ) -> None:
        """Log a tool response"""
        status = "SUCCESS" if success else "FAILED"
        log_data = {
            "tool": tool_name,
            "status": status,
            "execution_time_ms": execution_time_ms,
        }
        if request_id:
            log_data["request_id"] = request_id

        if success:
            self.logger.info(f"Response: {log_data}")
        else:
            self.logger.error(f"Response: {log_data}")

    def log_error(
        self, tool_name: str, error: Exception, request_id: Optional[str] = None
    ) -> None:
        """Log an error during tool execution"""
        log_data = {
            "tool": tool_name,
            "error_type": error.__class__.__name__,
            "error_message": str(error),
        }
        if request_id:
            log_data["request_id"] = request_id

        self.logger.error(f"Error: {log_data}", exc_info=True)
