# Red Bee MCP

Model Context Protocol (MCP) client for Red Bee Media OTT Platform. Connect to Red Bee streaming services from any MCP client like Cursor.

## 🚀 Quick Start

### For End Users (Cursor, etc.)

#### 1. Install the package

```bash
pip install redbee-mcp
```

#### 2. Configure in Cursor

Add to your `mcp.json`:

```json
{
  "mcpServers": {
    "redbee-mcp": {
      "command": "redbee-mcp",
      "args": ["--stdio"],
      "env": {
        "REDBEE_SERVER_URL": "http://51.20.4.56:8000"
      }
    }
  }
}
```

#### 3. Restart Cursor

You should see Red Bee MCP tools available!

That's it! Just like Figma MCP but for Red Bee Media.

## 🛠️ For Developers

### Deploy the Server (AWS EC2)

```bash
git clone https://github.com/your-username/redbee-MCP.git
cd redbee-MCP
./start-aws.sh
```

Server will be available at `http://your-ec2:8000`

### Publish the Client Package

```bash
# Build and publish to PyPI
pip install build twine
python -m build
twine upload dist/*
```

## 📖 Usage

### Available Commands

```bash
redbee-mcp --help                                    # Show help
redbee-mcp --test                                    # Test server connection  
redbee-mcp --stdio                                   # Start MCP client (for Cursor)
redbee-mcp --server-url http://server:8000 --stdio   # Custom server URL
```

### MCP Tools Available

- **Authentication**: Login, anonymous sessions, logout
- **Content Search**: Search movies, TV shows, documentaries
- **Asset Details**: Get detailed information about content
- **Playback**: Get streaming URLs and playback information
- **User Management**: Profiles, preferences, account management
- **Purchases**: View subscriptions, transactions, payment methods
- **System**: Configuration, time, location, devices

### Configuration Options

#### Custom Server URL in mcp.json

```json
{
  "redbee-mcp": {
    "command": "redbee-mcp",
    "args": ["--server-url", "http://your-server:8000", "--stdio"]
  }
}
```

#### Via environment variable

```bash
export REDBEE_SERVER_URL=http://your-server:8000
redbee-mcp --stdio
```

#### Via command line

```bash
redbee-mcp --server-url http://your-server:8000 --stdio
```

#### Via mcp.json environment

```json
{
  "redbee-mcp": {
    "command": "redbee-mcp",
    "args": ["--stdio"],
    "env": {
      "REDBEE_SERVER_URL": "http://your-server:8000"
    }
  }
}
```

#### Test Connection

```bash
redbee-mcp --test
```

## 🏗️ Architecture

```
Any Machine (Cursor)
    ↓ MCP stdio
redbee-mcp CLI (pip package)
    ↓ HTTP API
Red Bee MCP Server (AWS EC2:8000)
    ↓ HTTP API
Red Bee Media OTT Platform
```

## 🔄 Comparison with Other MCPs

| Feature | Figma MCP | Red Bee MCP |
|---------|-----------|-------------|
| **Install** | `npm install figma-developer-mcp` | `pip install redbee-mcp` |
| **Command** | `npx figma-developer-mcp` | `redbee-mcp` |
| **Config** | Pass API key as arg | Pass server URL via env |
| **Transport** | `--stdio` | `--stdio` |
| **Client** | Node.js | Python |

Same simplicity, same workflow! 🎯

## 🌐 Team Deployment

### For Admins

1. **Deploy server once** on AWS EC2 using `./start-aws.sh`
2. **Share server URL** with team (e.g., `http://51.20.4.56:8000`)

### For Team Members

Everyone in your team just needs to:

1. **Install**: `pip install redbee-mcp`
2. **Configure**: Add the same server URL in `mcp.json`
3. **Use**: Restart Cursor and enjoy!

The package automatically connects to your deployed Red Bee MCP server on AWS.

## 📁 Development

### Local Development

For development from source:

```bash
git clone https://github.com/your-username/redbee-MCP.git
cd redbee-MCP
pip install -e .                    # Install in development mode
redbee-mcp --test                  # Test connection
redbee-mcp --help                  # Show all available commands
```

### Project Structure

```
redbee-MCP/
├── src/redbee_mcp/
│   ├── cli.py              # CLI entry point (like figma-developer-mcp)
│   ├── server.py           # HTTP server (for AWS deployment)
│   ├── client.py           # Red Bee API client
│   ├── models.py           # Data models
│   └── tools/              # MCP tools implementation
├── start-aws.sh            # AWS deployment script
├── deploy-aws.md           # AWS deployment guide
└── pyproject.toml          # Package configuration
```

## 📄 License

MIT License - see LICENSE file for details.

## 🔗 Related

- [Model Context Protocol](https://github.com/modelcontextprotocol)
- [Red Bee Media](https://www.redbeemedia.com/)
- [Figma MCP](https://github.com/GLips/Figma-Context-MCP) (inspiration)

---

**Red Bee MCP: Bringing streaming content to your AI workflow** 🎬 