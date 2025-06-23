"""
HTTP/SSE Server for MCP requests
Enables exposing MCP functionality via HTTP instead of stdio
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, AsyncGenerator

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uvicorn

from .handler import McpHandler
from .models import RedBeeConfig

logger = logging.getLogger(__name__)

# Pydantic models for JSON-RPC requests
class JsonRpcRequest(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    method: str = Field(description="Method to call")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")
    id: Optional[str] = Field(default=None, description="Request ID")

class JsonRpcResponse(BaseModel):
    jsonrpc: str = Field(default="2.0", description="JSON-RPC version")
    id: Optional[str] = Field(description="Request ID")
    result: Optional[Any] = Field(default=None, description="Method result")
    error: Optional[Dict[str, Any]] = Field(default=None, description="Error if any")

class McpHttpServer:
    """
    HTTP/SSE server for MCP requests
    Compatible with JSON-RPC 2.0 protocol
    """
    
    def __init__(self, config: Optional[RedBeeConfig] = None, host: str = "0.0.0.0", port: int = 8000):
        self.config = config
        self.host = host
        self.port = port
        self.handler = McpHandler(config)
        self.app = FastAPI(
            title="Red Bee MCP Server",
            description="MCP Server for Red Bee Media OTT Platform via HTTP/SSE",
            version="1.0.0"
        )
        
        # Configure CORS to allow requests from browser
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, specify allowed domains
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information"""
            return {
                "name": "Red Bee MCP Server",
                "version": "1.0.0",
                "description": "MCP Server for Red Bee Media OTT Platform",
                "endpoints": {
                    "jsonrpc": "POST /",
                    "sse": "GET /sse",
                    "health": "GET /health"
                }
            }
        
        @self.app.get("/health")
        async def health_check():
            """Server health check"""
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "tools_count": len(await self.handler.list_tools())
            }
        
        @self.app.post("/", response_model=JsonRpcResponse)
        async def handle_jsonrpc(request: JsonRpcRequest):
            """
            Main endpoint for JSON-RPC MCP requests
            Compatible with list_tools and call_tool
            """
            try:
                logger.info(f"JSON-RPC request: {request.method}")
                
                if request.method == "tools/list":
                    # List all available tools
                    tools = await self.handler.list_tools()
                    tools_data = [tool.model_dump() for tool in tools]
                    
                    return JsonRpcResponse(
                        id=request.id,
                        result={"tools": tools_data}
                    )
                
                elif request.method == "tools/call":
                    # Call a specific tool
                    if not request.params:
                        raise HTTPException(status_code=400, detail="Parameters required for tools/call")
                    
                    tool_name = request.params.get("name")
                    tool_arguments = request.params.get("arguments", {})
                    
                    if not tool_name:
                        raise HTTPException(status_code=400, detail="Tool name required")
                    
                    result = await self.handler.call_tool(tool_name, tool_arguments)
                    result_data = [content.model_dump() for content in result]
                    
                    return JsonRpcResponse(
                        id=request.id,
                        result={"content": result_data}
                    )
                
                else:
                    return JsonRpcResponse(
                        id=request.id,
                        error={
                            "code": -32601,
                            "message": f"Unknown method: {request.method}"
                        }
                    )
                    
            except Exception as e:
                logger.error(f"Error processing JSON-RPC request: {str(e)}")
                return JsonRpcResponse(
                    id=request.id,
                    error={
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                )
        
        @self.app.get("/sse")
        async def sse_endpoint(request: Request):
            """
            Server-Sent Events endpoint for streaming
            Enables real-time communication with client
            """
            async def event_generator() -> AsyncGenerator[str, None]:
                client_id = str(uuid.uuid4())
                logger.info(f"New SSE connection: {client_id}")
                
                try:
                    # Send welcome message
                    yield f"data: {json.dumps({'type': 'welcome', 'client_id': client_id, 'timestamp': time.time()})}\n\n"
                    
                    # Send list of available tools
                    tools = await self.handler.list_tools()
                    tools_data = [tool.model_dump() for tool in tools]
                    yield f"data: {json.dumps({'type': 'tools', 'tools': tools_data})}\n\n"
                    
                    # Keep connection alive
                    while True:
                        # Check if client is still connected
                        if await request.is_disconnected():
                            logger.info(f"SSE client disconnected: {client_id}")
                            break
                        
                        # Send periodic ping
                        yield f"data: {json.dumps({'type': 'ping', 'timestamp': time.time()})}\n\n"
                        
                        # Wait before next ping
                        await asyncio.sleep(30)
                        
                except Exception as e:
                    logger.error(f"SSE error for client {client_id}: {str(e)}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                finally:
                    logger.info(f"SSE connection ended: {client_id}")
            
            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no"  # For nginx
                }
            )
        
        @self.app.post("/sse/call")
        async def sse_call_tool(request: JsonRpcRequest):
            """
            Endpoint to call a tool via SSE
            Returns result immediately (no streaming for tools)
            """
            try:
                if request.method != "tools/call":
                    raise HTTPException(status_code=400, detail="Only tools/call method is supported")
                
                if not request.params:
                    raise HTTPException(status_code=400, detail="Parameters required")
                
                tool_name = request.params.get("name")
                tool_arguments = request.params.get("arguments", {})
                
                if not tool_name:
                    raise HTTPException(status_code=400, detail="Tool name required")
                
                result = await self.handler.call_tool(tool_name, tool_arguments)
                result_data = [content.model_dump() for content in result]
                
                return {
                    "type": "tool_result",
                    "tool_name": tool_name,
                    "result": result_data,
                    "timestamp": time.time()
                }
                
            except Exception as e:
                logger.error(f"Error calling SSE tool: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self):
        """Starts the HTTP server"""
        logger.info(f"Starting MCP HTTP server on {self.host}:{self.port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            access_log=True
        )
        
        server = uvicorn.Server(config)
        await server.serve()

async def start_http_server(config: Optional[RedBeeConfig] = None, host: str = "0.0.0.0", port: int = 8000):
    """
    Helper function to start the HTTP server
    """
    server = McpHttpServer(config, host, port)
    await server.start()

if __name__ == "__main__":
    # For direct testing
    asyncio.run(start_http_server()) 