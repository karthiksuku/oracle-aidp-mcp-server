# Oracle AIDP MCP Server

A comprehensive Model Context Protocol (MCP) server for Oracle AI Data Platform (AIDP), enabling seamless integration with Claude Desktop and other MCP-compatible clients.

## Features

- **152 Tools** across 10 feature modules
- **Production-Ready**: Comprehensive error handling, logging, and retry logic
- **Real OCI Integration**: Uses official Oracle Cloud Infrastructure Python SDK
- **Flexible Configuration**: YAML-based configuration with multiple instance support
- **Async Architecture**: High-performance async/await implementation
- **Type-Safe**: Full Pydantic validation for all inputs

## Modules

### Fully Functional (Real OCI APIs)

1. **Instance Management** (10 tools)
   - Get instance status and metrics
   - Manage workspaces
   - Control access permissions

2. **Object Storage** (20 tools)
   - Bucket management (create, list, delete, update)
   - Object operations (upload, download, copy, move)
   - Lifecycle policies and versioning
   - Pre-signed URLs
   - Bulk operations

3. **Compute Clusters** (15 tools)
   - Spark cluster management via OCI Data Flow
   - Create, list, and manage clusters
   - Run management and monitoring
   - Resource pool operations
   - Log retrieval

### Framework Ready

4. **Data Catalog** (20 tools) - Search, browse, and manage data assets
5. **Notebooks** (15 tools) - Jupyter notebook management
6. **Jobs & Workflows** (20 tools) - Schedule and execute jobs
7. **Data Pipelines** (15 tools) - Build and manage data pipelines
8. **External Connections** (12 tools) - Connect to external data sources
9. **ML Models** (15 tools) - Machine learning model lifecycle
10. **Analytics & Reporting** (10 tools) - Generate reports and dashboards

## Prerequisites

- Python 3.8 or higher
- Oracle Cloud Infrastructure (OCI) account
- AIDP instance provisioned in OCI
- OCI CLI configured with credentials

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server.git
cd oracle-aidp-mcp-server
```

### 2. Run Installation Script

```bash
chmod +x install.sh
./install.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Set up configuration directories

### 3. Configure OCI Credentials

If you haven't already, configure your OCI credentials:

```bash
oci setup config
```

This will create `~/.oci/config` with your credentials.

### 4. Configure AIDP Instance

Copy the example configuration and update it with your AIDP instance details:

```bash
cp config/aidp_config.example.yaml config/aidp_config.yaml
```

Edit `config/aidp_config.yaml` and update:
- `ocid`: Your AIDP instance OCID
- `region`: Your OCI region (e.g., `us-ashburn-1`, `ap-melbourne-1`)
- `compartment_ocid`: Your compartment OCID
- `namespace`: Your Object Storage namespace

**How to find these values:**

1. **AIDP Instance OCID**: OCI Console → Analytics & AI → AI Data Platform → Your Instance → Copy OCID
2. **Region**: Shown in OCI Console (top right)
3. **Compartment OCID**: OCI Console → Identity & Security → Compartments → Your Compartment → Copy OCID
4. **Namespace**: OCI Console → Object Storage → Click any bucket → Note the namespace

### 5. Test the Installation

```bash
./run_server.sh
```

You should see initialization messages. Press Ctrl+C to stop.

## Claude Desktop Integration

### 1. Locate Claude Desktop Config

The config file is located at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 2. Add Server Configuration

Edit the config file and add:

```json
{
  "mcpServers": {
    "aidp": {
      "command": "/FULL/PATH/TO/oracle-aidp-mcp-server/run_server.sh",
      "env": {
        "AIDP_INSTANCE": "my-instance"
      }
    }
  }
}
```

**Important**:
- Replace `/FULL/PATH/TO/` with the actual absolute path
- Replace `my-instance` with the instance name from your `aidp_config.yaml`

### 3. Restart Claude Desktop

Completely quit and restart Claude Desktop.

### 4. Verify Connection

In Claude Desktop, you should see the "aidp" server connected. Try asking:

```
"List all my Object Storage buckets"
"Show me my AIDP instance status"
"What Spark clusters do I have?"
```

## Usage Examples

### Object Storage

```
# List buckets
"List all my Object Storage buckets"

# Create a bucket
"Create a new bucket named 'my-data-bucket'"

# Upload a file
"Upload ~/Documents/data.csv to bucket 'my-data-bucket' as data/file.csv"

# Download a file
"Download object 'report.pdf' from bucket 'reports' to ~/Downloads/"

# Generate pre-signed URL
"Create a pre-signed URL for object 'data.csv' in bucket 'my-bucket' valid for 24 hours"
```

### Compute Clusters

```
# List clusters
"Show me all my Spark clusters"

# Get cluster details
"Get details for cluster ocid1.dataflowapplication..."

# List cluster runs
"Show me all runs for my clusters"

# Get run logs
"Get logs for run ocid1.dataflowrun..."
```

### Instance Management

```
# Instance status
"What's the status of my AIDP instance?"

# List workspaces
"Show me all workspaces in my AIDP instance"

# Create workspace
"Create a new workspace named 'analytics-team'"
```

## Configuration

### Multiple Instances

You can configure multiple AIDP instances:

```yaml
aidp:
  instances:
    production:
      ocid: "ocid1.aidataplatform.oc1.us-ashburn-1.xxx"
      region: "us-ashburn-1"
      compartment_ocid: "ocid1.compartment.oc1..xxx"
      namespace: "prod-namespace"

    development:
      ocid: "ocid1.aidataplatform.oc1.ap-melbourne-1.xxx"
      region: "ap-melbourne-1"
      compartment_ocid: "ocid1.compartment.oc1..xxx"
      namespace: "dev-namespace"
```

Set the active instance with the `AIDP_INSTANCE` environment variable.

### Feature Flags

Disable modules you don't need:

```yaml
features:
  instance_management: true
  data_catalog: true
  object_storage: true
  compute_clusters: false  # Disable compute
  notebooks: false          # Disable notebooks
```

### Logging

Configure logging level and output:

```yaml
logging:
  level: "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "~/aidp-mcp-server.log"
  max_size_mb: 100
  backup_count: 5
```

## Troubleshooting

### Server Won't Start

1. Check logs: `tail -f ~/aidp-mcp-server.log`
2. Verify OCI credentials: `oci iam region list`
3. Check Python version: `python --version` (must be 3.8+)
4. Reinstall dependencies: `./install.sh`

### "Disconnected" in Claude Desktop

1. Check Claude Desktop logs:
   - macOS: `~/Library/Logs/Claude/mcp-server-aidp.log`
   - Windows: `%APPDATA%\Claude\logs\mcp-server-aidp.log`

2. Verify run_server.sh is executable: `chmod +x run_server.sh`

3. Test server manually: `./run_server.sh`

4. Ensure absolute paths in Claude Desktop config

### API Errors

1. Verify compartment OCID is correct
2. Check IAM permissions for your OCI user
3. Ensure AIDP instance is in ACTIVE state
4. Verify region matches your instance location

### Tools Not Appearing

1. Restart Claude Desktop completely (Cmd+Q / Alt+F4)
2. Wait 5-10 seconds for server initialization
3. Check feature flags in `aidp_config.yaml`

## Development

### Project Structure

```
oracle-aidp-mcp-server/
├── src/
│   ├── server.py           # Main MCP server
│   ├── oci_client.py       # OCI SDK wrapper
│   └── modules/            # Feature modules
│       ├── instance.py
│       ├── storage.py
│       ├── compute.py
│       └── ...
├── utils/
│   ├── logger.py           # Logging setup
│   ├── errors.py           # Error handling
│   ├── formatters.py       # Response formatting
│   └── validators.py       # Input validation
├── config/
│   ├── settings.py         # Pydantic settings
│   └── aidp_config.yaml    # Instance configuration
├── tests/
│   └── test_*.py           # Unit tests
├── requirements.txt        # Python dependencies
├── install.sh             # Installation script
└── run_server.sh          # Server startup script
```

### Running Tests

```bash
source venv/bin/activate
pytest tests/
```

### Adding New Tools

1. Create/edit module in `src/modules/`
2. Define tool schemas with Pydantic
3. Implement handler functions
4. Register tools in `src/server.py`
5. Add tests in `tests/`

## Architecture

- **MCP Protocol**: JSON-RPC over stdin/stdout
- **OCI SDK**: Official `oci` Python package
- **Async/Await**: High-performance concurrent operations
- **Retry Logic**: Exponential backoff with Tenacity
- **Type Safety**: Pydantic validation throughout
- **Logging**: Rotating file logs with configurable levels

## Security

- **No Credentials in Code**: Uses OCI config file
- **Least Privilege**: Requires only necessary IAM permissions
- **Input Validation**: All inputs validated with Pydantic
- **Error Sanitization**: Sensitive data removed from errors
- **Audit Logging**: All operations logged

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/discussions)
- **Documentation**: [Wiki](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/wiki)

## Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Powered by [Oracle Cloud Infrastructure](https://www.oracle.com/cloud/)
- Integrates with [Claude Desktop](https://claude.ai/)

---

**Made with ❤️ for the Oracle AIDP community**
