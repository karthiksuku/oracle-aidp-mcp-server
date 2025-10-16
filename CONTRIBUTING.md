# Contributing to Oracle AIDP MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, OCI region)
   - Relevant log excerpts (sanitize sensitive data!)

### Suggesting Features

1. Check [Discussions](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/discussions) for similar ideas
2. Create a new discussion or issue describing:
   - The problem you're trying to solve
   - Your proposed solution
   - Any alternatives you've considered

### Contributing Code

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server.git
   cd oracle-aidp-mcp-server
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up development environment**
   ```bash
   ./install.sh
   source venv/bin/activate
   ```

4. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add docstrings to functions
   - Update type hints

5. **Add tests**
   ```bash
   # Create test file in tests/
   # Run tests
   pytest tests/
   ```

6. **Test your changes**
   ```bash
   # Test the server starts
   ./run_server.sh

   # Test with Claude Desktop
   # Follow integration steps in README.md
   ```

7. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

   Use conventional commit messages:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Docs:` for documentation changes
   - `Refactor:` for code refactoring
   - `Test:` for test additions/changes

8. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes
   - Link any related issues

## Development Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function parameters and returns
- Keep functions focused and single-purpose
- Maximum line length: 100 characters
- Use descriptive variable names

### Documentation

- Add docstrings to all public functions
- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update configuration examples if needed

### Testing

- Write unit tests for new functionality
- Ensure all tests pass before submitting PR
- Test with real OCI services when possible
- Include both success and error cases

### Module Structure

When adding new modules:

```python
# src/modules/your_module.py

from typing import Any, Dict
from ...utils.formatters import format_success_response
from ...utils.errors import AIDPError

async def your_operation(oci_client, param1: str) -> Dict[str, Any]:
    """
    Brief description of what this does.

    Args:
        oci_client: OCI client wrapper
        param1: Description of parameter

    Returns:
        Formatted response dictionary

    Raises:
        AIDPError: If operation fails
    """
    try:
        result = oci_client.call_api(...)
        return format_success_response(result)
    except Exception as e:
        raise AIDPError(f"Operation failed: {str(e)}")

def get_tools() -> list:
    """Return list of MCP tool definitions."""
    return [
        {
            "name": "your_operation",
            "description": "User-facing description",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param1"]
            }
        }
    ]

async def handle_tool_call(name: str, arguments: dict, oci_client) -> dict:
    """Route tool calls to appropriate functions."""
    if name == "your_operation":
        return await your_operation(oci_client, **arguments)
    # ... more handlers
```

### Error Handling

- Use custom exceptions from `utils/errors.py`
- Sanitize error messages (remove OCIDs, credentials)
- Provide helpful error messages to users
- Log detailed errors for debugging

### Performance

- Use async/await for I/O operations
- Implement caching for frequently accessed data
- Add retry logic for transient failures
- Monitor memory usage for large operations

## Adding New OCI Services

To integrate a new OCI service:

1. **Add client to `oci_client.py`**
   ```python
   @property
   def your_service(self) -> oci.your_service.YourServiceClient:
       if self._your_service_client is None:
           self._your_service_client = oci.your_service.YourServiceClient(...)
       return self._your_service_client
   ```

2. **Create module in `src/modules/`**
   - Implement tool functions
   - Define MCP tool schemas
   - Add handler routing

3. **Register in `server.py`**
   - Import module
   - Add to `list_tools()`
   - Add to `call_tool()` routing

4. **Add configuration**
   - Update `config/settings.py` if needed
   - Add feature flag to `aidp_config.yaml`
   - Document in README.md

5. **Write tests**
   - Create `tests/test_your_module.py`
   - Mock OCI API responses
   - Test error cases

## Release Process

Maintainers will:

1. Review and merge PRs
2. Update version in `setup.py`
3. Update CHANGELOG.md
4. Create GitHub release
5. Announce in Discussions

## Questions?

- Open a [Discussion](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/discussions)
- Comment on relevant [Issues](https://github.com/YOUR_USERNAME/oracle-aidp-mcp-server/issues)

Thank you for contributing! 🎉
