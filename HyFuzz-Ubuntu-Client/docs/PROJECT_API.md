# HyFuzz API Documentation

This document provides comprehensive API documentation for HyFuzz's server and client endpoints.

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Server API](#server-api)
- [Client API](#client-api)
- [MCP Server Protocol](#mcp-server-protocol)
- [WebSocket API](#websocket-api)
- [Dashboard API](#dashboard-api)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Overview

HyFuzz provides several API interfaces:

- **Server API** (port 8080): Main control plane API for campaign management
- **Client API** (port 8001): Payload execution and instrumentation API
- **Dashboard API** (port 8888): Web dashboard and metrics API
- **MCP Protocol**: Model Context Protocol for LLM integration

### Base URLs

```
Production:   https://hyfuzz.example.com
Development:  http://localhost:8080
Client:       http://localhost:8001
Dashboard:    http://localhost:8888
```

### API Versioning

Current API version: `v1`

All endpoints are prefixed with `/api/v1` for versioning.

## Authentication

### API Key Authentication

Most endpoints require API key authentication via the `X-API-Key` header:

```bash
curl -H "X-API-Key: your-api-key-here" \
  http://localhost:8080/api/v1/campaigns
```

### JWT Authentication

For user-based authentication, use JWT tokens:

```bash
# Login to get token
curl -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl -H "Authorization: Bearer your-jwt-token" \
  http://localhost:8080/api/v1/campaigns
```

### Configuration

Enable authentication in `.env`:

```bash
REQUIRE_AUTH=true
API_KEY=your-secure-api-key
JWT_SECRET=your-jwt-secret
JWT_EXPIRATION=3600  # 1 hour
```

## Server API

### Health Check

Check server health status.

**Endpoint**: `GET /health`

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "components": {
    "database": "healthy",
    "llm": "healthy",
    "defense": "healthy"
  }
}
```

**Example**:
```bash
curl http://localhost:8080/health
```

---

### Campaign Management

#### List Campaigns

Retrieve all campaigns.

**Endpoint**: `GET /api/v1/campaigns`

**Authentication**: Required

**Query Parameters**:
- `status` (optional): Filter by status (pending, running, completed, failed)
- `protocol` (optional): Filter by protocol (coap, modbus, mqtt, http)
- `limit` (optional): Number of results (default: 50, max: 200)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "campaigns": [
    {
      "id": 1,
      "name": "coap-fuzzing-campaign",
      "protocol": "coap",
      "target": "coap://192.168.1.100:5683",
      "status": "running",
      "created_at": "2024-01-01T10:00:00Z",
      "started_at": "2024-01-01T10:05:00Z",
      "completed_at": null,
      "total_payloads": 1000,
      "successful_payloads": 856,
      "failed_payloads": 12,
      "model": "mistral",
      "metadata": {
        "description": "Testing CoAP implementation",
        "tags": ["coap", "iot"]
      }
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8080/api/v1/campaigns?status=running&protocol=coap"
```

---

#### Create Campaign

Create a new fuzzing campaign.

**Endpoint**: `POST /api/v1/campaigns`

**Authentication**: Required

**Request Body**:
```json
{
  "name": "my-campaign",
  "protocol": "coap",
  "target": "coap://192.168.1.100:5683",
  "model": "mistral",
  "config": {
    "payload_count": 1000,
    "timeout": 30,
    "max_retries": 3,
    "strategy": "adaptive"
  },
  "metadata": {
    "description": "Testing CoAP server",
    "tags": ["coap", "production"]
  }
}
```

**Response**:
```json
{
  "id": 43,
  "name": "my-campaign",
  "protocol": "coap",
  "target": "coap://192.168.1.100:5683",
  "status": "pending",
  "created_at": "2024-01-01T12:30:00Z",
  "message": "Campaign created successfully"
}
```

**Status Codes**:
- `201 Created`: Campaign created successfully
- `400 Bad Request`: Invalid request data
- `409 Conflict`: Campaign with this name already exists

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/campaigns \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-campaign",
    "protocol": "coap",
    "target": "coap://localhost:5683",
    "model": "mistral",
    "config": {"payload_count": 100}
  }'
```

---

#### Get Campaign Details

Retrieve detailed information about a specific campaign.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}`

**Authentication**: Required

**Path Parameters**:
- `campaign_id`: Campaign ID (integer)

**Response**:
```json
{
  "id": 1,
  "name": "coap-fuzzing-campaign",
  "protocol": "coap",
  "target": "coap://192.168.1.100:5683",
  "status": "running",
  "created_at": "2024-01-01T10:00:00Z",
  "started_at": "2024-01-01T10:05:00Z",
  "completed_at": null,
  "total_payloads": 1000,
  "successful_payloads": 856,
  "failed_payloads": 12,
  "model": "mistral",
  "config": {
    "payload_count": 1000,
    "timeout": 30,
    "strategy": "adaptive"
  },
  "metadata": {
    "description": "Testing CoAP implementation"
  },
  "statistics": {
    "execution_time_avg": 125.5,
    "execution_time_max": 450,
    "crash_count": 3,
    "defense_verdicts": {
      "monitor": 850,
      "investigate": 6,
      "block": 0,
      "escalate": 0
    }
  }
}
```

**Status Codes**:
- `200 OK`: Campaign found
- `404 Not Found`: Campaign does not exist

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1
```

---

#### Start Campaign

Start a pending campaign.

**Endpoint**: `POST /api/v1/campaigns/{campaign_id}/start`

**Authentication**: Required

**Response**:
```json
{
  "id": 1,
  "status": "running",
  "started_at": "2024-01-01T12:35:00Z",
  "message": "Campaign started successfully"
}
```

**Status Codes**:
- `200 OK`: Campaign started
- `400 Bad Request`: Campaign is not in pending state
- `404 Not Found`: Campaign does not exist

**Example**:
```bash
curl -X POST -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1/start
```

---

#### Stop Campaign

Stop a running campaign.

**Endpoint**: `POST /api/v1/campaigns/{campaign_id}/stop`

**Authentication**: Required

**Response**:
```json
{
  "id": 1,
  "status": "stopped",
  "completed_at": "2024-01-01T13:00:00Z",
  "message": "Campaign stopped successfully"
}
```

**Example**:
```bash
curl -X POST -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1/stop
```

---

#### Delete Campaign

Delete a campaign and all associated data.

**Endpoint**: `DELETE /api/v1/campaigns/{campaign_id}`

**Authentication**: Required

**Response**:
```json
{
  "message": "Campaign deleted successfully"
}
```

**Status Codes**:
- `200 OK`: Campaign deleted
- `400 Bad Request`: Cannot delete running campaign
- `404 Not Found`: Campaign does not exist

**Example**:
```bash
curl -X DELETE -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1
```

---

### Payload Management

#### List Payloads

Retrieve payloads for a campaign.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/payloads`

**Authentication**: Required

**Query Parameters**:
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "payloads": [
    {
      "id": 1,
      "campaign_id": 1,
      "payload_data": "{\"method\": \"GET\", \"path\": \"/test\"}",
      "protocol": "coap",
      "generated_at": "2024-01-01T10:10:00Z",
      "generation_model": "mistral",
      "generation_parameters": {
        "temperature": 0.7,
        "max_tokens": 256
      }
    }
  ],
  "total": 1000,
  "limit": 50,
  "offset": 0
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8080/api/v1/campaigns/1/payloads?limit=10"
```

---

#### Generate Payloads

Generate new payloads using LLM.

**Endpoint**: `POST /api/v1/campaigns/{campaign_id}/payloads/generate`

**Authentication**: Required

**Request Body**:
```json
{
  "count": 100,
  "model": "mistral",
  "strategy": "adaptive",
  "parameters": {
    "temperature": 0.7,
    "max_tokens": 256
  }
}
```

**Response**:
```json
{
  "campaign_id": 1,
  "generated_count": 100,
  "message": "Payloads generated successfully"
}
```

**Example**:
```bash
curl -X POST http://localhost:8080/api/v1/campaigns/1/payloads/generate \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "model": "mistral"}'
```

---

### Execution Results

#### List Executions

Retrieve execution results for a campaign.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/executions`

**Authentication**: Required

**Query Parameters**:
- `status` (optional): Filter by status (pending, completed, failed)
- `crash_detected` (optional): Filter by crash detection (true/false)
- `limit` (optional): Number of results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
{
  "executions": [
    {
      "id": 1,
      "campaign_id": 1,
      "payload_id": 1,
      "status": "completed",
      "executed_at": "2024-01-01T10:15:00Z",
      "execution_time_ms": 125,
      "exit_code": 0,
      "stdout": "Response: 2.05 Content",
      "stderr": "",
      "crash_detected": false,
      "instrumentation_data": {
        "syscalls": ["socket", "sendto", "recvfrom"],
        "coverage": "45.2%"
      }
    }
  ],
  "total": 856,
  "limit": 50,
  "offset": 0
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  "http://localhost:8080/api/v1/campaigns/1/executions?crash_detected=true"
```

---

#### Get Execution Details

Retrieve detailed information about a specific execution.

**Endpoint**: `GET /api/v1/executions/{execution_id}`

**Authentication**: Required

**Response**:
```json
{
  "id": 1,
  "campaign_id": 1,
  "payload_id": 1,
  "status": "completed",
  "executed_at": "2024-01-01T10:15:00Z",
  "execution_time_ms": 125,
  "exit_code": 0,
  "stdout": "Response: 2.05 Content\n...",
  "stderr": "",
  "crash_detected": false,
  "instrumentation_data": {
    "syscalls": ["socket", "sendto", "recvfrom", "close"],
    "coverage": "45.2%",
    "memory_usage": "12.5 MB"
  },
  "defense_result": {
    "verdict": "monitor",
    "risk_score": 0.15,
    "signals": ["normal_behavior"],
    "events": []
  },
  "judgment": {
    "score": 0.85,
    "reasoning": "Payload executed successfully without anomalies",
    "model": "gpt-4",
    "criteria": ["effectiveness", "coverage", "stability"]
  }
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/executions/1
```

---

### Defense System

#### Get Defense Statistics

Retrieve defense system statistics for a campaign.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/defense/statistics`

**Authentication**: Required

**Response**:
```json
{
  "campaign_id": 1,
  "total_verdicts": 856,
  "verdicts": {
    "monitor": 850,
    "investigate": 6,
    "block": 0,
    "escalate": 0
  },
  "average_risk_score": 0.12,
  "high_risk_count": 6,
  "signals": {
    "normal_behavior": 850,
    "suspicious_pattern": 6,
    "anomaly_detected": 0
  }
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1/defense/statistics
```

---

### Statistics and Metrics

#### Get Campaign Statistics

Retrieve comprehensive campaign statistics.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/statistics`

**Authentication**: Required

**Response**:
```json
{
  "campaign_id": 1,
  "status": "running",
  "duration_seconds": 3000,
  "payloads": {
    "total": 1000,
    "generated": 1000,
    "executed": 856,
    "successful": 844,
    "failed": 12
  },
  "performance": {
    "execution_time_avg_ms": 125.5,
    "execution_time_min_ms": 45,
    "execution_time_max_ms": 450,
    "throughput_per_second": 4.2
  },
  "crashes": {
    "total": 3,
    "unique": 2,
    "rate": 0.35
  },
  "coverage": {
    "states_covered": 15,
    "transitions_covered": 42,
    "coverage_percentage": 45.2
  },
  "defense": {
    "monitor": 850,
    "investigate": 6,
    "block": 0,
    "escalate": 0
  },
  "judgment": {
    "average_score": 0.78,
    "high_quality_count": 720,
    "low_quality_count": 124
  }
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1/statistics
```

---

### Protocol Coverage

#### Get Protocol Coverage

Retrieve protocol coverage information.

**Endpoint**: `GET /api/v1/campaigns/{campaign_id}/coverage`

**Authentication**: Required

**Response**:
```json
{
  "campaign_id": 1,
  "protocol": "coap",
  "states": [
    {
      "name": "IDLE",
      "hit_count": 856,
      "first_hit_at": "2024-01-01T10:05:00Z",
      "last_hit_at": "2024-01-01T12:30:00Z"
    },
    {
      "name": "CONNECTED",
      "hit_count": 842,
      "first_hit_at": "2024-01-01T10:05:15Z",
      "last_hit_at": "2024-01-01T12:30:05Z"
    }
  ],
  "transitions": [
    {
      "name": "IDLE->CONNECTED",
      "hit_count": 842,
      "first_hit_at": "2024-01-01T10:05:15Z",
      "last_hit_at": "2024-01-01T12:30:05Z"
    }
  ],
  "coverage_percentage": 45.2
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8080/api/v1/campaigns/1/coverage
```

---

## Client API

The Client API is exposed by Ubuntu Client instances for payload execution.

### Client Health Check

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "client_id": "ubuntu-client-01",
  "version": "1.0.0",
  "capabilities": ["instrumentation", "sandboxing"],
  "available": true
}
```

---

### Execute Payload

Execute a payload on the client.

**Endpoint**: `POST /api/v1/execute`

**Authentication**: Required

**Request Body**:
```json
{
  "payload_id": 1,
  "campaign_id": 1,
  "payload_data": "{\"method\": \"GET\", \"path\": \"/test\"}",
  "protocol": "coap",
  "target": "coap://localhost:5683",
  "config": {
    "timeout": 30,
    "instrumentation": true,
    "sandbox": true
  }
}
```

**Response**:
```json
{
  "execution_id": 1,
  "status": "completed",
  "execution_time_ms": 125,
  "exit_code": 0,
  "stdout": "Response: 2.05 Content",
  "stderr": "",
  "crash_detected": false,
  "instrumentation_data": {
    "syscalls": ["socket", "sendto", "recvfrom"],
    "coverage": "45.2%"
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8001/api/v1/execute \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "payload_id": 1,
    "campaign_id": 1,
    "payload_data": "{\"method\": \"GET\"}",
    "protocol": "coap",
    "target": "coap://localhost:5683"
  }'
```

---

### Get Client Status

**Endpoint**: `GET /api/v1/status`

**Response**:
```json
{
  "client_id": "ubuntu-client-01",
  "status": "running",
  "active_executions": 3,
  "total_executions": 856,
  "resource_usage": {
    "cpu_percent": 45.2,
    "memory_percent": 32.8,
    "disk_percent": 15.3
  },
  "uptime_seconds": 86400
}
```

**Example**:
```bash
curl -H "X-API-Key: your-api-key" \
  http://localhost:8001/api/v1/status
```

---

## MCP Server Protocol

HyFuzz implements the Model Context Protocol (MCP) for LLM integration.

### MCP Endpoints

#### List Tools

**Endpoint**: `POST /mcp/tools/list`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "create_campaign",
        "description": "Create a new fuzzing campaign",
        "inputSchema": {
          "type": "object",
          "properties": {
            "name": {"type": "string"},
            "protocol": {"type": "string"},
            "target": {"type": "string"}
          },
          "required": ["name", "protocol", "target"]
        }
      }
    ]
  }
}
```

---

#### Call Tool

**Endpoint**: `POST /mcp/tools/call`

**Request**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 2,
  "params": {
    "name": "create_campaign",
    "arguments": {
      "name": "test-campaign",
      "protocol": "coap",
      "target": "coap://localhost:5683"
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Campaign 'test-campaign' created successfully with ID 43"
      }
    ]
  }
}
```

---

## WebSocket API

Real-time updates via WebSocket connections.

### Campaign Updates

**Endpoint**: `ws://localhost:8080/ws/campaigns/{campaign_id}`

**Authentication**: Query parameter `api_key=your-api-key`

**Messages**:

Server sends updates:
```json
{
  "type": "campaign_update",
  "campaign_id": 1,
  "status": "running",
  "progress": 85.6,
  "statistics": {
    "total_payloads": 1000,
    "executed": 856
  }
}
```

```json
{
  "type": "execution_complete",
  "execution_id": 857,
  "payload_id": 857,
  "status": "completed",
  "crash_detected": false
}
```

**Example** (JavaScript):
```javascript
const ws = new WebSocket('ws://localhost:8080/ws/campaigns/1?api_key=your-api-key');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

---

## Dashboard API

The Dashboard API provides metrics and visualization data.

### Get Dashboard Metrics

**Endpoint**: `GET /api/dashboard/metrics`

**Response**:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "overview": {
    "total_campaigns": 42,
    "active_campaigns": 5,
    "total_payloads": 42000,
    "total_executions": 38450
  },
  "performance": {
    "throughput_per_second": 21.5,
    "average_execution_time_ms": 135
  },
  "defense": {
    "monitor": 38200,
    "investigate": 245,
    "block": 5,
    "escalate": 0
  }
}
```

---

### Server-Sent Events Stream

**Endpoint**: `GET /api/dashboard/stream`

**Authentication**: Query parameter `api_key=your-api-key`

**Response** (text/event-stream):
```
data: {"timestamp": "2024-01-01T12:00:00Z", "active_campaigns": 5, ...}

data: {"timestamp": "2024-01-01T12:00:05Z", "active_campaigns": 5, ...}
```

**Example** (JavaScript):
```javascript
const source = new EventSource('/api/dashboard/stream?api_key=your-api-key');

source.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Metrics:', data);
};
```

---

## Data Models

### Campaign Model

```json
{
  "id": "integer",
  "name": "string",
  "protocol": "string (coap|modbus|mqtt|http)",
  "target": "string (URL)",
  "status": "string (pending|running|completed|stopped|failed)",
  "created_at": "string (ISO 8601)",
  "started_at": "string (ISO 8601) | null",
  "completed_at": "string (ISO 8601) | null",
  "total_payloads": "integer",
  "successful_payloads": "integer",
  "failed_payloads": "integer",
  "model": "string",
  "config": "object",
  "metadata": "object"
}
```

### Payload Model

```json
{
  "id": "integer",
  "campaign_id": "integer",
  "payload_data": "string (JSON)",
  "protocol": "string",
  "generated_at": "string (ISO 8601)",
  "generation_model": "string",
  "generation_parameters": "object"
}
```

### Execution Model

```json
{
  "id": "integer",
  "campaign_id": "integer",
  "payload_id": "integer",
  "status": "string (pending|completed|failed)",
  "executed_at": "string (ISO 8601)",
  "execution_time_ms": "integer",
  "exit_code": "integer",
  "stdout": "string",
  "stderr": "string",
  "crash_detected": "boolean",
  "instrumentation_data": "object"
}
```

### Defense Result Model

```json
{
  "id": "integer",
  "execution_id": "integer",
  "verdict": "string (monitor|investigate|block|escalate)",
  "risk_score": "float (0.0-1.0)",
  "module_name": "string",
  "signals": "array of strings",
  "events": "array of objects",
  "created_at": "string (ISO 8601)"
}
```

---

## Error Handling

### Error Response Format

All errors follow this format:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict (e.g., duplicate name)
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Codes

- `INVALID_REQUEST`: Request validation failed
- `AUTHENTICATION_REQUIRED`: API key or JWT missing
- `INVALID_CREDENTIALS`: Invalid API key or JWT
- `RESOURCE_NOT_FOUND`: Requested resource doesn't exist
- `RESOURCE_CONFLICT`: Resource already exists
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Unexpected server error

### Example Error Response

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Invalid protocol specified",
    "details": {
      "field": "protocol",
      "value": "invalid",
      "allowed": ["coap", "modbus", "mqtt", "http"]
    }
  }
}
```

---

## Rate Limiting

API requests are rate-limited to prevent abuse.

### Limits

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour
- **Campaign creation**: 10 per hour
- **Payload generation**: 100 per minute

### Headers

Rate limit information is included in response headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 956
X-RateLimit-Reset: 1704110400
```

### Rate Limit Exceeded Response

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 minutes.",
    "details": {
      "limit": 1000,
      "remaining": 0,
      "reset_at": "2024-01-01T13:00:00Z"
    }
  }
}
```

---

## Examples

### Complete Campaign Workflow

```bash
#!/bin/bash

API_KEY="your-api-key"
BASE_URL="http://localhost:8080/api/v1"

# 1. Create campaign
CAMPAIGN_ID=$(curl -s -X POST "$BASE_URL/campaigns" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-campaign",
    "protocol": "coap",
    "target": "coap://localhost:5683",
    "model": "mistral",
    "config": {"payload_count": 100}
  }' | jq -r '.id')

echo "Created campaign: $CAMPAIGN_ID"

# 2. Generate payloads
curl -s -X POST "$BASE_URL/campaigns/$CAMPAIGN_ID/payloads/generate" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "model": "mistral"}'

echo "Payloads generated"

# 3. Start campaign
curl -s -X POST "$BASE_URL/campaigns/$CAMPAIGN_ID/start" \
  -H "X-API-Key: $API_KEY"

echo "Campaign started"

# 4. Monitor progress
while true; do
  STATUS=$(curl -s "$BASE_URL/campaigns/$CAMPAIGN_ID" \
    -H "X-API-Key: $API_KEY" | jq -r '.status')

  if [ "$STATUS" = "completed" ]; then
    break
  fi

  echo "Status: $STATUS"
  sleep 5
done

# 5. Get results
curl -s "$BASE_URL/campaigns/$CAMPAIGN_ID/statistics" \
  -H "X-API-Key: $API_KEY" | jq '.'

echo "Campaign complete!"
```

### Python SDK Example

```python
import requests
import time

class HyFuzzClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key}

    def create_campaign(self, name, protocol, target):
        response = requests.post(
            f'{self.base_url}/campaigns',
            headers=self.headers,
            json={
                'name': name,
                'protocol': protocol,
                'target': target,
                'model': 'mistral',
                'config': {'payload_count': 100}
            }
        )
        return response.json()

    def start_campaign(self, campaign_id):
        response = requests.post(
            f'{self.base_url}/campaigns/{campaign_id}/start',
            headers=self.headers
        )
        return response.json()

    def get_status(self, campaign_id):
        response = requests.get(
            f'{self.base_url}/campaigns/{campaign_id}',
            headers=self.headers
        )
        return response.json()

    def wait_for_completion(self, campaign_id):
        while True:
            status = self.get_status(campaign_id)
            if status['status'] in ['completed', 'failed', 'stopped']:
                return status
            time.sleep(5)

# Usage
client = HyFuzzClient('http://localhost:8080/api/v1', 'your-api-key')

campaign = client.create_campaign('my-campaign', 'coap', 'coap://localhost:5683')
print(f"Created campaign: {campaign['id']}")

client.start_campaign(campaign['id'])
print("Campaign started")

result = client.wait_for_completion(campaign['id'])
print(f"Campaign completed: {result['status']}")
```

---

For more information:
- **Quick Start**: See [QUICKSTART.md](QUICKSTART.md)
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Troubleshooting**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

**API Support**: For API-related questions, visit our documentation or contact api-support@hyfuzz.example.com
