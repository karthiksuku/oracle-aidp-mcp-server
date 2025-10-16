# Quick Start Guide

Get up and running with Oracle AIDP MCP Server in 5 minutes!

## Prerequisites

- Python 3.8+
- OCI account with AIDP instance
- Claude Desktop installed

## Step 1: Clone & Install (2 minutes)

```bash
git clone https://github.com/karthiksuku/oracle-aidp-mcp-server.git
cd oracle-aidp-mcp-server
./install.sh
```

## Step 2: Configure (2 minutes)

### A. Set up OCI credentials (if not done already)

```bash
oci setup config
```

### B. Configure your AIDP instance

```bash
cp config/aidp_config.example.yaml config/aidp_config.yaml
```

Edit `config/aidp_config.yaml` - you only need to update 4 values:

```yaml
aidp:
  instances:
    my-instance:  # Change this to whatever you want
      ocid: "YOUR_AIDP_INSTANCE_OCID"
      region: "YOUR_REGION"  # e.g., us-ashburn-1
      compartment_ocid: "YOUR_COMPARTMENT_OCID"
      namespace: "YOUR_NAMESPACE"
```

**Where to find these?**
- OCID: OCI Console → AI Data Platform → Your Instance → Copy OCID
- Region: Top right in OCI Console
- Compartment: Identity & Security → Compartments → Copy OCID
- Namespace: Object Storage → Any bucket → Note namespace

## Step 3: Configure Claude Desktop (1 minute)

Edit: `~/Library/Application Support/Claude/claude_desktop_config.json`

Add (replace with your actual path):

```json
{
  "mcpServers": {
    "aidp": {
      "command": "/Users/YOUR_USERNAME/oracle-aidp-mcp-server/run_server.sh",
      "env": {
        "AIDP_INSTANCE": "my-instance"
      }
    }
  }
}
```

**Important**: Use the absolute path and match the instance name from step 2!

## Step 4: Test It!

1. Restart Claude Desktop (Cmd+Q, then reopen)
2. Wait 5 seconds for initialization
3. Ask Claude:

```
"List all my Object Storage buckets"
```

## What You Can Do

### Object Storage
- `"List my buckets"`
- `"Upload ~/data.csv to bucket 'my-bucket'"`
- `"Download 'file.txt' from bucket 'my-bucket' to ~/Downloads/"`

### Compute (Spark)
- `"Show me my Spark clusters"`
- `"List all cluster runs"`

### Instance
- `"What's my AIDP instance status?"`
- `"List all workspaces"`

## Troubleshooting

### Server shows "Disconnected"

```bash
# Check logs
tail -f ~/aidp-mcp-server.log

# Test manually
cd oracle-aidp-mcp-server
./run_server.sh
# Press Ctrl+C after you see initialization messages
```

### Can't find values for config

1. Log in to [OCI Console](https://cloud.oracle.com/)
2. Click hamburger menu → Analytics & AI → AI Data Platform
3. Click your AIDP instance
4. Copy the OCID shown

### Need Help?

- [Full Documentation](README.md)
- [GitHub Issues](https://github.com/karthiksuku/oracle-aidp-mcp-server/issues)
- [GitHub Discussions](https://github.com/karthiksuku/oracle-aidp-mcp-server/discussions)

---

**That's it! You're ready to use AIDP with Claude Desktop!** 🚀
