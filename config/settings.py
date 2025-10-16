"""
Settings and configuration management for AIDP MCP Server
"""
import os
from pathlib import Path
from typing import Any, Optional
import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator

from utils.errors import ConfigurationError


class InstanceConfig(BaseModel):
    """Configuration for a single AIDP instance"""

    ocid: str
    region: str
    compartment_ocid: str
    namespace: str
    default_bucket: Optional[str] = None
    default_workspace: str = "default"
    display_name: Optional[str] = None


class AuthConfig(BaseModel):
    """OCI authentication configuration"""

    method: str = "config_file"  # config_file or instance_principal
    config_path: str = "~/.oci/config"
    profile: str = "DEFAULT"


class DefaultsConfig(BaseModel):
    """Default values for various operations"""

    cluster_size: str = "small"
    cluster_shape: str = "VM.Standard2.4"
    cluster_worker_count: int = 2
    notebook_kernel: str = "python3"
    notebook_shape: str = "VM.Standard2.1"
    job_timeout_minutes: int = 60
    job_max_retries: int = 3
    pipeline_batch_size: int = 1000
    object_storage_tier: str = "Standard"
    lifecycle_policy_days: int = 90
    max_query_results: int = 1000
    query_timeout_seconds: int = 300


class PerformanceConfig(BaseModel):
    """Performance and connection settings"""

    request_timeout_seconds: int = 300
    max_concurrent_requests: int = 10
    retry_max_attempts: int = 3
    retry_backoff_seconds: int = 2
    connection_pool_size: int = 20


class CacheConfig(BaseModel):
    """Cache configuration"""

    enabled: bool = True
    ttl_seconds: int = 300
    max_size_mb: int = 100


class LoggingConfig(BaseModel):
    """Logging configuration"""

    level: str = "INFO"
    file: Optional[str] = "~/aidp-mcp-server.log"
    max_size_mb: int = 100
    backup_count: int = 5
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class FeaturesConfig(BaseModel):
    """Feature flags for enabling/disabling modules"""

    instance_management: bool = True
    data_catalog: bool = True
    object_storage: bool = True
    compute_clusters: bool = True
    notebooks: bool = True
    jobs_workflows: bool = True
    data_pipelines: bool = True
    external_connections: bool = True
    ml_models: bool = True
    analytics_reporting: bool = True


class Settings:
    """Main settings class for AIDP MCP Server"""

    def __init__(
        self,
        config_file: Optional[str] = None,
        instance_name: Optional[str] = None,
    ):
        """
        Initialize settings

        Args:
            config_file: Path to YAML configuration file
            instance_name: Name of the AIDP instance to use
        """
        # Load environment variables
        load_dotenv()

        # Determine config file path
        if config_file is None:
            config_file = os.getenv(
                "AIDP_CONFIG",
                str(Path(__file__).parent / "aidp_config.yaml"),
            )

        self.config_file = Path(config_file).expanduser()

        # Load configuration
        self._load_config()

        # Determine active instance
        self.active_instance_name = instance_name or os.getenv("AIDP_INSTANCE", "melbourne")

        if self.active_instance_name not in self.instances:
            raise ConfigurationError(
                f"Instance '{self.active_instance_name}' not found in configuration",
                details={"available_instances": list(self.instances.keys())},
            )

    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        if not self.config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_file}",
                details={"config_file": str(self.config_file)},
            )

        try:
            with open(self.config_file, "r") as f:
                config_data = yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file: {str(e)}",
                original_error=e,
            )

        if not isinstance(config_data, dict) or "aidp" not in config_data:
            raise ConfigurationError("Invalid configuration file structure")

        aidp_config = config_data["aidp"]

        # Parse instances
        self.instances: dict[str, InstanceConfig] = {}
        for name, instance_data in aidp_config.get("instances", {}).items():
            try:
                self.instances[name] = InstanceConfig(**instance_data)
            except Exception as e:
                raise ConfigurationError(
                    f"Invalid configuration for instance '{name}': {str(e)}",
                    original_error=e,
                )

        if not self.instances:
            raise ConfigurationError("No instances configured")

        # Parse other config sections
        try:
            self.auth = AuthConfig(**aidp_config.get("auth", {}))
            self.defaults = DefaultsConfig(**aidp_config.get("defaults", {}))
            self.performance = PerformanceConfig(**aidp_config.get("performance", {}))
            self.cache = CacheConfig(**aidp_config.get("cache", {}))
            self.logging = LoggingConfig(**aidp_config.get("logging", {}))
            self.features = FeaturesConfig(**aidp_config.get("features", {}))
        except Exception as e:
            raise ConfigurationError(
                f"Invalid configuration: {str(e)}",
                original_error=e,
            )

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration"""
        # Logging overrides
        if log_level := os.getenv("LOG_LEVEL"):
            self.logging.level = log_level

        if log_file := os.getenv("LOG_FILE"):
            self.logging.file = log_file

        if log_max_size := os.getenv("LOG_MAX_SIZE_MB"):
            try:
                self.logging.max_size_mb = int(log_max_size)
            except ValueError:
                pass

        # Auth overrides
        if auth_method := os.getenv("OCI_AUTH_METHOD"):
            self.auth.method = auth_method

        if config_path := os.getenv("OCI_CONFIG_PATH"):
            self.auth.config_path = config_path

        if profile := os.getenv("OCI_PROFILE"):
            self.auth.profile = profile

        # Performance overrides
        if timeout := os.getenv("REQUEST_TIMEOUT"):
            try:
                self.performance.request_timeout_seconds = int(timeout)
            except ValueError:
                pass

        if max_retries := os.getenv("MAX_RETRIES"):
            try:
                self.performance.retry_max_attempts = int(max_retries)
            except ValueError:
                pass

        # Cache overrides
        if cache_enabled := os.getenv("ENABLE_CACHE"):
            self.cache.enabled = cache_enabled.lower() in ("true", "1", "yes")

        if cache_ttl := os.getenv("CACHE_TTL_SECONDS"):
            try:
                self.cache.ttl_seconds = int(cache_ttl)
            except ValueError:
                pass

    @property
    def instance(self) -> InstanceConfig:
        """Get the active instance configuration"""
        return self.instances[self.active_instance_name]

    def get_instance(self, name: str) -> InstanceConfig:
        """
        Get configuration for a specific instance

        Args:
            name: Instance name

        Returns:
            Instance configuration

        Raises:
            ConfigurationError: If instance not found
        """
        if name not in self.instances:
            raise ConfigurationError(
                f"Instance '{name}' not found",
                details={"available_instances": list(self.instances.keys())},
            )
        return self.instances[name]

    def to_dict(self) -> dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            "active_instance": self.active_instance_name,
            "instances": {
                name: instance.model_dump() for name, instance in self.instances.items()
            },
            "auth": self.auth.model_dump(),
            "defaults": self.defaults.model_dump(),
            "performance": self.performance.model_dump(),
            "cache": self.cache.model_dump(),
            "logging": self.logging.model_dump(),
            "features": self.features.model_dump(),
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings(
    config_file: Optional[str] = None,
    instance_name: Optional[str] = None,
    force_reload: bool = False,
) -> Settings:
    """
    Get the global settings instance (singleton pattern)

    Args:
        config_file: Path to configuration file (only used on first call)
        instance_name: Name of instance to use (only used on first call)
        force_reload: Force reload of configuration

    Returns:
        Settings instance
    """
    global _settings

    if _settings is None or force_reload:
        _settings = Settings(config_file=config_file, instance_name=instance_name)

    return _settings
