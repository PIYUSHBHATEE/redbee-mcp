# Red Bee MCP Server

**Model Context Protocol (MCP) Server for Red Bee Media OTT Platform**

Connect to Red Bee Media streaming services directly from any MCP-compatible client like Claude Desktop, Cursor, or other AI tools. This server provides 33 tools for authentication, content search, user management, purchases, and system operations.

[![PyPI version](https://badge.fury.io/py/redbee-mcp.svg)](https://badge.fury.io/py/redbee-mcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🚀 Quick Start

### Option 1: Using uvx (Recommended)

The easiest way to use Red Bee MCP is with `uvx` (requires no installation):

```bash
# Test the server
uvx redbee-mcp --help
```

### Option 2: Using pip

```bash
pip install redbee-mcp
```

## 📋 Configuration

### For Claude Desktop

Add to your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "uvx",
      "args": ["redbee-mcp"],
      "env": {
        "REDBEE_CUSTOMER": "CUSTOMER_NAME",
        "REDBEE_BUSINESS_UNIT": "BUSINESS_UNIT_NAME"
      }
    }
  }
}
```

### For Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "uvx",
      "args": ["redbee-mcp"],
      "env": {
        "REDBEE_CUSTOMER": "CUSTOMER_NAME",
        "REDBEE_BUSINESS_UNIT": "BUSINESS_UNIT_NAME"
      }
    }
  }
}
```

### Alternative: If you installed with pip

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "redbee-mcp",
      "env": {
        "REDBEE_CUSTOMER": "CUSTOMER_NAME",
        "REDBEE_BUSINESS_UNIT": "BUSINESS_UNIT_NAME"
      }
    }
  }
}
```

## 🔧 Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `REDBEE_CUSTOMER` | ✅ Yes | Red Bee customer identifier | `CUSTOMER_NAME` |
| `REDBEE_BUSINESS_UNIT` | ✅ Yes | Red Bee business unit | `BUSINESS_UNIT_NAME` |
| `REDBEE_EXPOSURE_BASE_URL` | ❌ No | API base URL | `https://exposure.api.redbee.live` |
| `REDBEE_USERNAME` | ❌ No | Username for authentication | `user@example.com` |
| `REDBEE_PASSWORD` | ❌ No | Password for authentication | `password123` |
| `REDBEE_SESSION_TOKEN` | ❌ No | Existing session token | `eyJhbGciOiJIUzI1...` |
| `REDBEE_DEVICE_ID` | ❌ No | Device identifier | `web-browser-123` |
| `REDBEE_CONFIG_ID` | ❌ No | Configuration ID | `sandwich` |
| `REDBEE_TIMEOUT` | ❌ No | Request timeout in seconds | `30` |

### Example with authentication

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "uvx",
      "args": ["redbee-mcp"],
      "env": {
        "REDBEE_CUSTOMER": "YOUR_CUSTOMER_NAME",
        "REDBEE_BUSINESS_UNIT": "YOUR_BUSINESS_UNIT_NAME",
        "REDBEE_USERNAME": "your_username",
        "REDBEE_PASSWORD": "your_password"
      }
    }
  }
}
```

## 🛠️ Available Tools (33 total)

### 🔐 Authentication (4 tools)
- `login_user` - Authenticate with username/password
- `create_anonymous_session` - Create anonymous session
- `validate_session_token` - Validate existing session
- `logout_user` - Logout and invalidate session

### 📺 Content Management (9 tools)
- `search_content` - Search for movies, TV shows, documentaries
- `get_asset_details` - Get detailed asset information
- `get_public_asset_details` - Get public asset details (no auth)
- `get_playback_info` - Get streaming URLs and playback info
- `search_assets_autocomplete` - Autocomplete search suggestions
- `get_epg_for_channel` - Get Electronic Program Guide
- `get_episodes_for_season` - Get all episodes in a season
- `get_assets_by_tag` - Get assets by tag type
- `list_assets` - List assets with filters

### 👤 User Management (6 tools)
- `signup_user` - Create new user account
- `change_user_password` - Change user password
- `get_user_profiles` - Get user profiles
- `add_user_profile` - Add new user profile
- `select_user_profile` - Select active profile
- `get_user_preferences` - Get user preferences
- `set_user_preferences` - Set user preferences

### 💳 Purchases & Transactions (7 tools)
- `get_account_purchases` - Get user purchases
- `get_account_transactions` - Get transaction history
- `get_offerings` - Get available product offerings
- `purchase_product_offering` - Purchase a product
- `cancel_purchase_subscription` - Cancel subscription
- `get_stored_payment_methods` - Get saved payment methods
- `add_payment_method` - Add new payment method

### ⚙️ System Operations (7 tools)
- `get_system_config` - Get platform configuration
- `get_system_time` - Get server time
- `get_user_location` - Get user location by IP
- `get_active_channels` - Get active TV channels
- `get_user_devices` - Get registered devices
- `delete_user_device` - Delete a device

## 🧪 Testing

### Test the server locally

```bash
# Using uvx
uvx redbee-mcp

# Using pip installation
redbee-mcp

# With environment variables
REDBEE_CUSTOMER=CUSTOMER_NAME REDBEE_BUSINESS_UNIT=BUSINESS_UNIT_NAME uvx redbee-mcp
```

### Test MCP protocol manually

```bash
# Initialize and list tools
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"roots": {"listChanged": true}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | uvx redbee-mcp
```

## 📖 Usage Examples

### Search for content

Ask your AI assistant:
> "Search for French documentaries about nature"

The assistant will use the `search_content` tool with appropriate parameters.

### Get streaming information

> "Get the playback URL for asset ID 12345"

The assistant will use `get_playback_info` to retrieve streaming details.

### Manage user profiles

> "Show me all user profiles and create a new one called 'Kids'"

The assistant will use `get_user_profiles` and `add_user_profile`.

## 🔄 Development

### Local development

```bash
git clone https://github.com/tamsibesson/redbee-mcp.git
cd redbee-mcp
pip install -e .
redbee-mcp
```

### Run tests

```bash
# Test MCP protocol
python -c "
import asyncio
from src.redbee_mcp.server import get_available_tools
print(f'Available tools: {len(asyncio.run(get_available_tools()))}')
"
```

### Project structure

```
redbee-mcp/
├── src/redbee_mcp/
│   ├── __init__.py
│   ├── __main__.py          # Entry point
│   ├── server.py            # MCP server implementation
│   ├── client.py            # Red Bee API client
│   ├── models.py            # Data models
│   └── tools/               # MCP tools
│       ├── auth.py          # Authentication tools
│       ├── content.py       # Content management tools
│       ├── user_management.py # User tools
│       ├── purchases.py     # Purchase tools
│       └── system.py        # System tools
├── pyproject.toml           # Package configuration
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/redbee-mcp/
- **Red Bee Media**: https://www.redbeemedia.com/
- **Model Context Protocol**: https://modelcontextprotocol.io/
- **Exposure API Documentation**: https://exposure.api.redbee.live/docs

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the Red Bee Media documentation
- Review the MCP specification

---

**Made with ❤️ for the Red Bee Media community** 