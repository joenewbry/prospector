#!/usr/bin/env python3
"""Prospector MCP Server — exposes Prospector's pipeline as MCP tools."""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    TextContent,
    Tool,
    ServerCapabilities,
    ToolsCapability,
)

PROSPECTOR_URL = os.environ.get("PROSPECTOR_URL", "http://localhost:8102")

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

server = Server("prospector")


async def http_get(path: str, **params) -> Any:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(f"{PROSPECTOR_URL}{path}", params=params or None)
        resp.raise_for_status()
        return resp.json()


async def http_post(path: str, body: dict = None) -> Any:
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{PROSPECTOR_URL}{path}", json=body or {})
        resp.raise_for_status()
        return resp.json()


@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="trigger-pipeline",
            description=(
                "Start a Prospector pipeline run. Fetches candidates from the specified "
                "adapters (github, hackernews, twitter, bootcamps), scores them, and saves "
                "results. Returns run_id immediately — poll get-run-status to check completion."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "adapters": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Adapter keys to run (e.g. ['github', 'hackernews']). Omit to run all.",
                    },
                    "adapter_configs": {
                        "type": "object",
                        "description": "Per-adapter config overrides (e.g. {'github': {'max_pages': 2}}).",
                    },
                    "weights": {
                        "type": "object",
                        "description": "Scoring weight overrides (e.g. {'trust_gap': 0.5, 'reachability': 0.3}).",
                    },
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get-run-status",
            description="Get the status and metadata for a specific pipeline run. Status is 'running' or 'done'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID returned by trigger-pipeline.",
                    },
                },
                "required": ["run_id"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="list-runs",
            description="List all pipeline runs with their status, timestamps, and prospect counts.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get-prospects",
            description=(
                "Get all prospects across runs, deduped by source+username (highest score wins). "
                "Supports filtering by source, category, minimum score, and limit."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Filter by source (e.g. 'github', 'hackernews', 'twitter', 'bootcamp').",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (e.g. 'developer', 'founder').",
                    },
                    "min_score": {
                        "type": "number",
                        "description": "Minimum final_score threshold (0.0–1.0).",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of prospects to return (default: 50).",
                        "default": 50,
                    },
                },
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get-run-prospects",
            description="Get all prospects from a specific pipeline run, sorted by score descending.",
            inputSchema={
                "type": "object",
                "properties": {
                    "run_id": {
                        "type": "string",
                        "description": "The run ID to fetch prospects for.",
                    },
                },
                "required": ["run_id"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="generate-outreach",
            description="Generate a personalized outreach message for a prospect using Claude.",
            inputSchema={
                "type": "object",
                "properties": {
                    "prospect_id": {
                        "type": "integer",
                        "description": "The prospect's database ID (from get-prospects or get-run-prospects).",
                    },
                },
                "required": ["prospect_id"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="get-stats",
            description=(
                "Get Prospector pipeline statistics: PVA metrics (position/velocity/acceleration), "
                "source and category breakdowns, score distribution, and daily counts."
            ),
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
        Tool(
            name="list-adapters",
            description="List available data source adapters (github, hackernews, twitter, bootcamps) and their config schemas.",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list:
    try:
        result = await _dispatch(name, arguments)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        logger.error(f"Tool {name} error: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e), "tool": name}, indent=2))]


async def _dispatch(name: str, args: dict) -> Any:
    if name == "trigger-pipeline":
        body = {}
        if args.get("adapters"):
            body["adapters"] = args["adapters"]
        if args.get("adapter_configs"):
            body["adapter_configs"] = args["adapter_configs"]
        if args.get("weights"):
            body["weights"] = args["weights"]
        return await http_post("/api/runs", body)

    elif name == "get-run-status":
        return await http_get(f"/api/runs/{args['run_id']}/status")

    elif name == "list-runs":
        return await http_get("/api/runs")

    elif name == "get-prospects":
        prospects = await http_get("/api/prospects")
        if args.get("source"):
            prospects = [p for p in prospects if p.get("source") == args["source"]]
        if args.get("category"):
            prospects = [p for p in prospects if p.get("category") == args["category"]]
        if args.get("min_score") is not None:
            prospects = [p for p in prospects if p.get("final_score", 0) >= args["min_score"]]
        limit = args.get("limit", 50)
        return prospects[:limit]

    elif name == "get-run-prospects":
        data = await http_get(f"/api/runs/{args['run_id']}")
        return data.get("prospects", data)

    elif name == "generate-outreach":
        return await http_post(f"/api/prospects/{args['prospect_id']}/outreach")

    elif name == "get-stats":
        return await http_get("/api/stats")

    elif name == "list-adapters":
        return await http_get("/api/adapters")

    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    logger.info(f"Starting Prospector MCP Server (target: {PROSPECTOR_URL})")
    async with stdio_server() as (read_stream, write_stream):
        init_options = InitializationOptions(
            server_name="prospector",
            server_version="1.0.0",
            capabilities=ServerCapabilities(tools=ToolsCapability()),
        )
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
