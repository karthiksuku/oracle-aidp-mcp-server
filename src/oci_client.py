"""
OCI SDK Client Wrapper for AIDP MCP Server
Provides unified interface to OCI services with error handling, retries, and connection pooling
"""
from typing import Any, Optional, Dict
from pathlib import Path
import oci
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from config.settings import Settings
from utils.logger import get_logger
from utils.errors import (
    AuthenticationError,
    APIError,
    NetworkError,
    TimeoutError,
    RateLimitError,
)

logger = get_logger(__name__)


class OCIClient:
    """Wrapper for OCI SDK clients with unified configuration and error handling"""

    def __init__(self, settings: Settings):
        """
        Initialize OCI client

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.config = self._load_oci_config()

        # Initialize service clients
        self._object_storage_client: Optional[oci.object_storage.ObjectStorageClient] = None
        self._identity_client: Optional[oci.identity.IdentityClient] = None
        self._resource_search_client: Optional[oci.resource_search.ResourceSearchClient] = None
        self._data_flow_client: Optional[oci.data_flow.DataFlowClient] = None  # For Spark/Compute
        self._data_catalog_client: Optional[oci.data_catalog.DataCatalogClient] = None  # For Data Catalog

        logger.info(f"OCI Client initialized for region: {settings.instance.region}")

    def _load_oci_config(self) -> dict[str, Any]:
        """
        Load OCI configuration based on auth method

        Returns:
            OCI configuration dictionary

        Raises:
            AuthenticationError: If configuration cannot be loaded
        """
        try:
            if self.settings.auth.method == "instance_principal":
                # Use instance principal authentication
                signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                config = {
                    "region": self.settings.instance.region,
                }
                config["signer"] = signer
                logger.info("Using instance principal authentication")
                return config

            else:
                # Use config file authentication
                config_path = Path(self.settings.auth.config_path).expanduser()

                if not config_path.exists():
                    raise AuthenticationError(
                        f"OCI config file not found: {config_path}",
                        details={"config_path": str(config_path)},
                    )

                config = oci.config.from_file(
                    file_location=str(config_path),
                    profile_name=self.settings.auth.profile,
                )

                # Override region if specified in instance config
                if self.settings.instance.region:
                    config["region"] = self.settings.instance.region

                # Validate config
                oci.config.validate_config(config)

                logger.info(
                    f"Loaded OCI config from {config_path} "
                    f"(profile: {self.settings.auth.profile})"
                )
                return config

        except oci.exceptions.ConfigFileNotFound as e:
            raise AuthenticationError(
                "OCI configuration file not found",
                details={"config_path": self.settings.auth.config_path},
                original_error=e,
            )
        except oci.exceptions.InvalidConfig as e:
            raise AuthenticationError(
                "Invalid OCI configuration",
                original_error=e,
            )
        except Exception as e:
            raise AuthenticationError(
                f"Failed to load OCI configuration: {str(e)}",
                original_error=e,
            )

    @property
    def object_storage(self) -> oci.object_storage.ObjectStorageClient:
        """Get Object Storage client (lazy initialization)"""
        if self._object_storage_client is None:
            self._object_storage_client = oci.object_storage.ObjectStorageClient(
                self.config,
                timeout=(
                    self.settings.performance.request_timeout_seconds,
                    self.settings.performance.request_timeout_seconds,
                ),
            )
            logger.debug("Initialized Object Storage client")
        return self._object_storage_client

    @property
    def identity(self) -> oci.identity.IdentityClient:
        """Get Identity client (lazy initialization)"""
        if self._identity_client is None:
            self._identity_client = oci.identity.IdentityClient(
                self.config,
                timeout=(
                    self.settings.performance.request_timeout_seconds,
                    self.settings.performance.request_timeout_seconds,
                ),
            )
            logger.debug("Initialized Identity client")
        return self._identity_client

    @property
    def resource_search(self) -> oci.resource_search.ResourceSearchClient:
        """Get Resource Search client (lazy initialization)"""
        if self._resource_search_client is None:
            self._resource_search_client = oci.resource_search.ResourceSearchClient(
                self.config,
                timeout=(
                    self.settings.performance.request_timeout_seconds,
                    self.settings.performance.request_timeout_seconds,
                ),
            )
            logger.debug("Initialized Resource Search client")
        return self._resource_search_client

    @property
    def data_flow(self) -> oci.data_flow.DataFlowClient:
        """Get Data Flow client for Spark/Compute operations (lazy initialization)"""
        if self._data_flow_client is None:
            self._data_flow_client = oci.data_flow.DataFlowClient(
                self.config,
                timeout=(
                    self.settings.performance.request_timeout_seconds,
                    self.settings.performance.request_timeout_seconds,
                ),
            )
            logger.debug("Initialized Data Flow client")
        return self._data_flow_client

    @property
    def data_catalog(self) -> oci.data_catalog.DataCatalogClient:
        """Get Data Catalog client (lazy initialization)"""
        if self._data_catalog_client is None:
            self._data_catalog_client = oci.data_catalog.DataCatalogClient(
                self.config,
                timeout=(
                    self.settings.performance.request_timeout_seconds,
                    self.settings.performance.request_timeout_seconds,
                ),
            )
            logger.debug("Initialized Data Catalog client")
        return self._data_catalog_client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((NetworkError, TimeoutError)),
        reraise=True,
    )
    def call_api(
        self,
        api_func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Call an OCI API function with automatic retry and error handling

        Args:
            api_func: The OCI API function to call
            *args: Positional arguments for the API function
            **kwargs: Keyword arguments for the API function

        Returns:
            API response

        Raises:
            Various AIDP exceptions based on error type
        """
        try:
            logger.debug(f"Calling API: {api_func.__name__}")
            response = api_func(*args, **kwargs)
            logger.debug(f"API call successful: {api_func.__name__}")
            return response

        except oci.exceptions.ServiceError as e:
            # OCI service errors
            status = e.status
            code = e.code
            message = e.message

            logger.error(
                f"OCI Service Error: {code} - {message} (status: {status})"
            )

            if status == 401:
                raise AuthenticationError(
                    "Authentication failed",
                    details={"code": code, "message": message},
                    original_error=e,
                )
            elif status == 404:
                from utils.errors import ResourceNotFoundError
                raise ResourceNotFoundError(
                    message,
                    details={"code": code},
                    original_error=e,
                )
            elif status == 429:
                raise RateLimitError(
                    "API rate limit exceeded",
                    details={"code": code, "message": message},
                    original_error=e,
                )
            elif status >= 500:
                raise APIError(
                    f"OCI service error: {message}",
                    details={"code": code, "status": status},
                    original_error=e,
                )
            else:
                raise APIError(
                    message,
                    details={"code": code, "status": status},
                    original_error=e,
                )

        except oci.exceptions.ConnectTimeout as e:
            logger.error(f"Connection timeout: {str(e)}")
            raise TimeoutError(
                "Connection to OCI timed out",
                original_error=e,
            )

        except oci.exceptions.RequestException as e:
            logger.error(f"Request exception: {str(e)}")
            raise NetworkError(
                "Network error while communicating with OCI",
                original_error=e,
            )

        except Exception as e:
            logger.error(f"Unexpected error in API call: {str(e)}", exc_info=True)
            raise APIError(
                f"Unexpected error: {str(e)}",
                original_error=e,
            )

    def get_namespace(self) -> str:
        """
        Get the Object Storage namespace

        Returns:
            Object Storage namespace string
        """
        return self.settings.instance.namespace

    def get_compartment_id(self) -> str:
        """
        Get the compartment OCID

        Returns:
            Compartment OCID
        """
        return self.settings.instance.compartment_ocid

    def get_instance_ocid(self) -> str:
        """
        Get the AIDP instance OCID

        Returns:
            Instance OCID
        """
        return self.settings.instance.ocid

    def get_region(self) -> str:
        """
        Get the region

        Returns:
            Region identifier
        """
        return self.settings.instance.region

    def test_connection(self) -> dict[str, Any]:
        """
        Test connection to OCI services

        Returns:
            Dictionary with connection test results
        """
        results = {
            "region": self.get_region(),
            "compartment_id": self.get_compartment_id(),
            "namespace": self.get_namespace(),
            "services": {},
        }

        # Test Identity service
        try:
            tenancy = self.call_api(
                self.identity.get_tenancy,
                tenancy_id=self.config["tenancy"],
            )
            results["services"]["identity"] = {
                "status": "connected",
                "tenancy_name": tenancy.data.name,
            }
        except Exception as e:
            results["services"]["identity"] = {
                "status": "failed",
                "error": str(e),
            }

        # Test Object Storage service
        try:
            self.call_api(
                self.object_storage.list_buckets,
                namespace_name=self.get_namespace(),
                compartment_id=self.get_compartment_id(),
            )
            results["services"]["object_storage"] = {"status": "connected"}
        except Exception as e:
            results["services"]["object_storage"] = {
                "status": "failed",
                "error": str(e),
            }

        return results

    def close(self) -> None:
        """Close all client connections"""
        # OCI clients don't have explicit close methods, but we can clean up references
        self._object_storage_client = None
        self._identity_client = None
        self._resource_search_client = None
        self._data_flow_client = None
        self._data_catalog_client = None
        logger.info("OCI clients closed")
