# Red Bee MCP Server

**Model Context Protocol (MCP) Server for Red Bee Media OTT Platform**

Connect to Red Bee Media streaming services from MCP-compatible clients like Claude Desktop, or integrate via HTTP/SSE for web applications. This server provides 33 tools for authentication, content search, user management, purchases, and system operations.

[![PyPI version](https://badge.fury.io/py/redbee-mcp.svg)](https://badge.fury.io/py/redbee-mcp)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 🆕 New: HTTP/SSE Mode

**Version 1.3.1** now supports multiple operating modes:

- **Stdio Mode** (original): For local AI agents like Claude Desktop
- **HTTP Mode**: REST API with JSON-RPC for web integration  
- **SSE Mode**: Server-Sent Events for real-time communication
- **Both Modes**: Run stdio and HTTP simultaneously

## 🚀 Quick Start

### Option 1: Using uvx (Recommended)

```bash
# Test the server
uvx redbee-mcp --help

# Stdio mode (original)
uvx redbee-mcp --stdio --customer YOUR_CUSTOMER --business-unit YOUR_BU

# HTTP mode (new)
uvx redbee-mcp --http --customer YOUR_CUSTOMER --business-unit YOUR_BU

# Both modes simultaneously
uvx redbee-mcp --both --customer YOUR_CUSTOMER --business-unit YOUR_BU
```

### Option 2: Using pip

```bash
pip install redbee-mcp

# Same usage as uvx, but with redbee-mcp command
redbee-mcp --http --customer YOUR_CUSTOMER --business-unit YOUR_BU
```

## 📋 Configuration

### For Claude Desktop (Stdio Mode)

Add to your Claude Desktop MCP configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "uvx",
      "args": ["redbee-mcp", "--stdio"],
      "env": {
        "REDBEE_CUSTOMER": "CUSTOMER_NAME",
        "REDBEE_BUSINESS_UNIT": "BUSINESS_UNIT_NAME"
      }
    }
  }
}
```

### For Web Applications (HTTP Mode)

Start the HTTP server:
```bash
redbee-mcp --http --customer YOUR_CUSTOMER --business-unit YOUR_BU
```

The server will be available at `http://localhost:8000` with these endpoints:

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | API information |
| GET | `/health` | Server health check |
| POST | `/` | JSON-RPC MCP requests |
| GET | `/sse` | Server-Sent Events stream |

## 🌐 HTTP/SSE API Usage

### Example HTTP Requests

#### Health Check
```bash
curl http://localhost:8000/health
```

#### List Available Tools
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": "1"
  }'
```

#### Search Content
```bash
curl -X POST http://localhost:8000/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_content_v2",
      "arguments": {
        "query": "french films",
        "types": "MOVIE",
        "pageSize": 5
      }
    },
    "id": "search-1"
  }'
```

### Web Integration Example

```javascript
class RedBeeMCPClient {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async callTool(toolName, arguments) {
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        params: { name: toolName, arguments },
        id: Date.now().toString()
      })
    });
    return response.json();
  }

  async searchContent(query, options = {}) {
    return this.callTool('search_content_v2', {
      query,
      types: options.types || 'MOVIE,TV_SHOW',
      pageSize: options.pageSize || 10,
      ...options
    });
  }
}

// Usage
const mcp = new RedBeeMCPClient();
const results = await mcp.searchContent('comedy movies');
```

### Server-Sent Events

Connect to real-time event stream:

```javascript
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Event received:', data.type);
  
  if (data.type === 'welcome') {
    console.log('Connected with client ID:', data.client_id);
  } else if (data.type === 'tools') {
    console.log('Available tools:', data.tools.length);
  }
};
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

## Available Tools

### 🔐 Authentication
- `login_user` - Authenticate with username/password
- `create_anonymous_session` - Create anonymous session
- `validate_session_token` - Validate existing session
- `logout_user` - Logout and invalidate session

### 📺 Content Management
- `get_public_asset_details` - Get asset details via public endpoint (no auth)
- `search_content_v2` - Search V2: free text query in asset fields (including descriptions)
- `get_asset_details` - Get detailed asset information
- `get_playback_info` - Get streaming URLs and playback info
- `search_assets_autocomplete` - Autocomplete search suggestions
- `get_epg_for_channel` - Get Electronic Program Guide for a channel
- `get_episodes_for_season` - Get all episodes in a season
- `get_assets_by_tag` - Get assets by tag type (e.g., origin)
- `list_assets` - List assets with advanced filters
- `search_multi_v3` - Multi-search for assets, tags, and participants
- `get_asset_collection_entries` - Get collection entries for an asset collection
- `get_asset_thumbnail` - Get thumbnail URL for an asset at a specific time
- `get_seasons_for_series` - Get all seasons for a TV series

### 👤 User Management
- `signup_user` - Create new user account
- `change_user_password` - Change user password
- `get_user_profiles` - Get user profiles
- `add_user_profile` - Add new user profile
- `select_user_profile` - Select active profile
- `get_user_preferences` - Get user preferences
- `set_user_preferences` - Set user preferences

### 💳 Purchases & Transactions
- `get_account_purchases` - Get user purchases
- `get_account_transactions` - Get transaction history
- `get_offerings` - Get available product offerings
- `purchase_product_offering` - Purchase a product
- `cancel_purchase_subscription` - Cancel subscription
- `get_stored_payment_methods` - Get saved payment methods
- `add_payment_method` - Add new payment method

### ⚙️ System Operations
- `get_system_config` - Get platform configuration
- `get_system_time` - Get server time
- `get_user_location` - Get user location by IP
- `get_active_channels` - Get active TV channels
- `get_user_devices` - Get registered devices
- `delete_user_device` - Delete a device

## 🧪 Testing

### Test HTTP Server

```bash
# Start the server
redbee-mcp --http --customer DEMO --business-unit DEMO

# In another terminal, run the test script
python example_usage.py
```

### Test Stdio Mode

```bash
# Using uvx
REDBEE_CUSTOMER=CUSTOMER_NAME REDBEE_BUSINESS_UNIT=BUSINESS_UNIT_NAME uvx redbee-mcp --stdio

# Using pip installation
REDBEE_CUSTOMER=CUSTOMER_NAME REDBEE_BUSINESS_UNIT=BUSINESS_UNIT_NAME redbee-mcp --stdio
```

### Test MCP Protocol Manually

```bash
# Initialize and list tools
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {"roots": {"listChanged": true}}, "clientInfo": {"name": "test", "version": "1.0.0"}}}
{"jsonrpc": "2.0", "method": "notifications/initialized"}
{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}' | uvx redbee-mcp --stdio
```

## 🏗️ Architecture

### Multi-Mode Design

The server is architected with clean separation of concerns:

- **McpHandler**: Core business logic shared between all modes
- **Stdio Server**: Traditional MCP stdio interface for AI agents
- **HTTP Server**: FastAPI-based REST/SSE interface for web apps
- **CLI**: Multi-mode command line interface

### File Structure

```
src/redbee_mcp/
├── handler.py          # Core business logic
├── server.py           # Stdio MCP server
├── http_server.py      # HTTP/SSE server
├── cli.py              # Multi-mode CLI
├── models.py           # Data models
└── tools/              # Tool modules
    ├── auth.py
    ├── content.py
    ├── purchases.py
    ├── system.py
    └── user_management.py
```

## 📖 Usage Examples

### Search for French Movies (Stdio Mode)

Ask your AI assistant:
> "Search for French documentaries about nature"

### Search for Content (HTTP Mode)

```javascript
const mcp = new RedBeeMCPClient();
const results = await mcp.searchContent('french documentaries', {
  types: 'MOVIE',
  locale: ['fr'],
  pageSize: 10
});
```

### Get TV Show Information

```python
# First search for a TV show
{
  "query": "Game of Thrones",
  "types": "TV_SHOW"
}

# Then get its seasons
{
  "assetId": "tv-show-asset-id"
}
```

### User Authentication

```python
{
  "username": "user@example.com",
  "password": "password123",
  "remember_me": true
}
```

## 🚀 Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000

# HTTP mode
CMD ["redbee-mcp", "--http", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

```bash
export REDBEE_CUSTOMER="your-customer"
export REDBEE_BUSINESS_UNIT="your-business-unit"
export REDBEE_EXPOSURE_BASE_URL="https://exposure.api.redbee.live"
```

### Systemd Service

```ini
# /etc/systemd/system/redbee-mcp-http.service
[Unit]
Description=Red Bee MCP HTTP Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/redbee-mcp
Environment=REDBEE_CUSTOMER=your-customer
Environment=REDBEE_BUSINESS_UNIT=your-business-unit
ExecStart=/usr/local/bin/redbee-mcp --http --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🔒 Security Considerations

### CORS Configuration

For production HTTP deployments, configure CORS properly in `http_server.py`:

```python
self.app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specify allowed domains
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

## 📝 API Reference

The Red Bee MCP Server provides access to Red Bee Media Exposure API through:

- **MCP Tools**: For AI agents and local applications
- **HTTP/JSON-RPC**: For web applications and remote integration
- **Server-Sent Events**: For real-time updates

Each tool includes:
- Input validation with required and optional parameters
- Comprehensive error handling and messages
- Type safety for all inputs and outputs
- Detailed documentation and examples

## 🛠️ Development

### Requirements

- Python 3.8+
- MCP SDK
- aiohttp for HTTP requests
- pydantic for data validation
- FastAPI and uvicorn for HTTP mode

### Local Development

```bash
# Clone and install
git clone https://github.com/tamsibesson/redbee-mcp
cd redbee-mcp
pip install -e .

# Run in development mode
PYTHONPATH=src python -m redbee_mcp --http --customer TEST --business-unit TEST
```

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues and questions:
- GitHub Issues: https://github.com/tamsibesson/redbee-mcp/issues
- Red Bee Media Documentation: https://www.redbeemedia.com/

## 🔗 Related

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/desktop)
- [Red Bee Media](https://www.redbeemedia.com/)
- [FastAPI](https://fastapi.tiangolo.com/) 