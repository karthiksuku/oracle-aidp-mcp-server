"""
Tests for Object Storage module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.modules import storage
from utils.errors import ValidationError


@pytest.mark.asyncio
async def test_list_buckets():
    """Test listing buckets"""
    # Mock OCI client
    oci_client = Mock()
    oci_client.get_namespace.return_value = "test-namespace"
    oci_client.get_compartment_id.return_value = "ocid1.compartment.test"

    # Mock API response
    mock_bucket = Mock()
    mock_bucket.name = "test-bucket"
    mock_bucket.namespace = "test-namespace"
    mock_bucket.compartment_id = "ocid1.compartment.test"
    mock_bucket.time_created = None
    mock_bucket.etag = "etag123"

    mock_response = Mock()
    mock_response.data = [mock_bucket]

    oci_client.call_api.return_value = mock_response

    # Execute
    result = await storage.list_buckets(oci_client, limit=100)

    # Assert
    assert result["success"] == True
    assert "data" in result
    assert len(result["data"]["items"]) == 1
    assert result["data"]["items"][0]["name"] == "test-bucket"


@pytest.mark.asyncio
async def test_create_bucket_validation():
    """Test bucket creation validation"""
    oci_client = Mock()

    # Test invalid bucket name
    with pytest.raises(ValidationError):
        await storage.create_bucket(oci_client, ".invalid-bucket")

    with pytest.raises(ValidationError):
        await storage.create_bucket(oci_client, "invalid..bucket")


@pytest.mark.asyncio
async def test_upload_object_file_not_found():
    """Test upload with missing file"""
    oci_client = Mock()

    with pytest.raises(ValidationError):
        await storage.upload_object(
            oci_client,
            "test-bucket",
            "test-object",
            "/nonexistent/file.txt"
        )


def test_storage_tools_count():
    """Test that storage module has correct number of tools"""
    tools = storage.get_tools()
    assert len(tools) == 20, f"Expected 20 tools, got {len(tools)}"


def test_storage_tool_names():
    """Test that all storage tools have correct naming"""
    tools = storage.get_tools()
    tool_names = [tool.name for tool in tools]

    # Check that key tools exist
    assert "list_buckets" in tool_names
    assert "create_bucket" in tool_names
    assert "upload_object" in tool_names
    assert "download_object" in tool_names
    assert "bulk_upload" in tool_names
