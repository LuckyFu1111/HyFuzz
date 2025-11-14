"""
Real-Time Fuzzing Monitoring Dashboard

Web-based dashboard for monitoring fuzzing campaigns with real-time
metrics, visualizations, and crash analysis.

Features:
- Real-time metrics updates via WebSocket
- Interactive charts and graphs
- Campaign management UI
- Crash viewer and analyzer
- Performance profiling
- Export capabilities

Author: HyFuzz Team
Version: 1.0.0
Date: 2025-01-13
"""

import asyncio
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)


# ==============================================================================
# DASHBOARD HTML TEMPLATE
# ==============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyFuzz Monitoring Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f23;
            color: #00ff00;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #00ff00;
        }

        h1 {
            color: #00ff00;
            text-shadow: 0 0 10px #00ff00;
            margin-bottom: 10px;
        }

        .subtitle {
            color: #888;
            font-size: 14px;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .card {
            background: #1a1a2e;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
        }

        .card h2 {
            color: #00ff00;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #333;
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #888;
        }

        .metric-value {
            color: #00ff00;
            font-weight: bold;
            font-size: 18px;
        }

        .metric-value.large {
            font-size: 32px;
        }

        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 5px;
            font-size: 12px;
            font-weight: bold;
        }

        .status.running {
            background: #00ff00;
            color: #000;
        }

        .status.paused {
            background: #ffa500;
            color: #000;
        }

        .status.completed {
            background: #888;
            color: #fff;
        }

        .campaign-list {
            max-height: 400px;
            overflow-y: auto;
        }

        .campaign-item {
            background: #16213e;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 3px solid #00ff00;
        }

        .campaign-item h3 {
            color: #00ff00;
            margin-bottom: 5px;
            font-size: 16px;
        }

        .campaign-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin-top: 10px;
            font-size: 12px;
        }

        .chart-container {
            height: 200px;
            margin-top: 20px;
            background: #16213e;
            border-radius: 5px;
            padding: 10px;
        }

        .crash-list {
            max-height: 300px;
            overflow-y: auto;
        }

        .crash-item {
            background: #2d1b1b;
            border-left: 3px solid #ff0000;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
        }

        .crash-item .crash-id {
            color: #ff0000;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .crash-item .crash-time {
            color: #888;
            font-size: 12px;
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s;
        }

        button:hover {
            background: #00cc00;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.5);
        }

        button:disabled {
            background: #555;
            cursor: not-allowed;
        }

        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #00ff00;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.3;
            }
        }

        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #1a1a2e;
            border: 1px solid #00ff00;
            padding: 10px 20px;
            border-radius: 5px;
            display: flex;
            align-items: center;
        }

        .ascii-art {
            font-family: monospace;
            color: #00ff00;
            font-size: 10px;
            line-height: 1.2;
            white-space: pre;
            margin-bottom: 10px;
            opacity: 0.5;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #0f0f23;
        }

        ::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #00cc00;
        }
    </style>
</head>
<body>
    <div class="connection-status">
        <span class="live-indicator"></span>
        <span id="connection-text">Connecting...</span>
    </div>

    <div class="container">
        <header>
            <div class="ascii-art">
 _   _       _____
| | | |_   _|  ___|   _ ________
| |_| | | | | |_ | | | |_  /_  /
|  _  | |_| |  _|| |_| |/ / / /
|_| |_|\__, |_|   \__,_/___/___|
       |___/
            </div>
            <h1>🔍 HyFuzz Monitoring Dashboard</h1>
            <p class="subtitle">Real-time Fuzzing Campaign Monitoring & Analysis</p>
        </header>

        <div class="grid">
            <!-- Global Statistics -->
            <div class="card">
                <h2>📊 Global Statistics</h2>
                <div class="metric">
                    <span class="metric-label">Total Executions</span>
                    <span class="metric-value large" id="total-execs">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Executions/sec</span>
                    <span class="metric-value" id="execs-per-sec">0.0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Unique Crashes</span>
                    <span class="metric-value" id="unique-crashes">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Coverage</span>
                    <span class="metric-value" id="coverage">0</span>
                </div>
            </div>

            <!-- Campaign Status -->
            <div class="card">
                <h2>🚀 Campaign Status</h2>
                <div class="metric">
                    <span class="metric-label">Total Campaigns</span>
                    <span class="metric-value" id="total-campaigns">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Running</span>
                    <span class="metric-value" id="running-campaigns">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Nodes</span>
                    <span class="metric-value" id="active-nodes">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">0s</span>
                </div>
            </div>

            <!-- LLM Optimization -->
            <div class="card">
                <h2>🤖 LLM Optimization</h2>
                <div class="metric">
                    <span class="metric-label">Cache Hit Rate</span>
                    <span class="metric-value" id="cache-hit-rate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Tokens Saved</span>
                    <span class="metric-value" id="tokens-saved">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Batch Efficiency</span>
                    <span class="metric-value" id="batch-efficiency">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Avg Response Time</span>
                    <span class="metric-value" id="avg-response-time">0ms</span>
                </div>
            </div>
        </div>

        <!-- Active Campaigns -->
        <div class="card">
            <h2>📋 Active Campaigns</h2>
            <div class="campaign-list" id="campaign-list">
                <p style="color: #888; text-align: center; padding: 20px;">No active campaigns</p>
            </div>
        </div>

        <!-- Recent Crashes -->
        <div class="card">
            <h2>💥 Recent Crashes</h2>
            <div class="crash-list" id="crash-list">
                <p style="color: #888; text-align: center; padding: 20px;">No crashes detected</p>
            </div>
        </div>

        <!-- Event Log -->
        <div class="card">
            <h2>📝 Event Log</h2>
            <div style="max-height: 200px; overflow-y: auto; font-family: monospace; font-size: 12px;" id="event-log">
                <div style="color: #888; padding: 10px;">Waiting for events...</div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection
        let ws = null;
        let startTime = Date.now();
        let stats = {
            total_execs: 0,
            execs_per_sec: 0,
            unique_crashes: 0,
            coverage: 0,
            campaigns: [],
            crashes: []
        };

        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;

            ws = new WebSocket(wsUrl);

            ws.onopen = () => {
                console.log('WebSocket connected');
                document.getElementById('connection-text').textContent = 'Connected';
                addEventLog('Connected to server', 'success');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                handleMessage(data);
            };

            ws.onclose = () => {
                console.log('WebSocket disconnected');
                document.getElementById('connection-text').textContent = 'Disconnected';
                addEventLog('Disconnected from server', 'error');

                // Reconnect after 3 seconds
                setTimeout(connect, 3000);
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                addEventLog('Connection error', 'error');
            };
        }

        function handleMessage(data) {
            if (data.type === 'statistics') {
                updateStatistics(data.data);
            } else if (data.type === 'campaign_update') {
                updateCampaigns(data.data);
            } else if (data.type === 'crash') {
                addCrash(data.data);
            } else if (data.type === 'event') {
                addEventLog(data.message, 'info');
            }
        }

        function updateStatistics(data) {
            stats = { ...stats, ...data };

            document.getElementById('total-execs').textContent =
                formatNumber(stats.total_executions || 0);
            document.getElementById('execs-per-sec').textContent =
                (stats.avg_exec_per_sec || 0).toFixed(1);
            document.getElementById('unique-crashes').textContent =
                stats.total_unique_crashes || 0;
            document.getElementById('coverage').textContent =
                (stats.coverage || 0).toFixed(1) + '%';
            document.getElementById('total-campaigns').textContent =
                stats.total_campaigns || 0;
            document.getElementById('running-campaigns').textContent =
                stats.running_campaigns || 0;
            document.getElementById('active-nodes').textContent =
                stats.active_nodes || 0;

            // LLM stats
            if (stats.llm_stats) {
                document.getElementById('cache-hit-rate').textContent =
                    (stats.llm_stats.cache_hit_rate || 0).toFixed(1) + '%';
                document.getElementById('tokens-saved').textContent =
                    formatNumber(stats.llm_stats.tokens_saved || 0);
                document.getElementById('batch-efficiency').textContent =
                    (stats.llm_stats.batch_efficiency || 0).toFixed(1) + '%';
                document.getElementById('avg-response-time').textContent =
                    (stats.llm_stats.avg_response_time || 0).toFixed(0) + 'ms';
            }

            // Update uptime
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('uptime').textContent = formatUptime(uptime);
        }

        function updateCampaigns(campaigns) {
            const container = document.getElementById('campaign-list');

            if (!campaigns || campaigns.length === 0) {
                container.innerHTML = '<p style="color: #888; text-align: center; padding: 20px;">No active campaigns</p>';
                return;
            }

            container.innerHTML = campaigns.map(campaign => `
                <div class="campaign-item">
                    <h3>${campaign.name}</h3>
                    <span class="status ${campaign.status}">${campaign.status.toUpperCase()}</span>
                    <div class="campaign-stats">
                        <div>
                            <div style="color: #888;">Executions</div>
                            <div style="color: #00ff00; font-weight: bold;">${formatNumber(campaign.total_execs)}</div>
                        </div>
                        <div>
                            <div style="color: #888;">Crashes</div>
                            <div style="color: #ff0000; font-weight: bold;">${campaign.unique_crashes}</div>
                        </div>
                        <div>
                            <div style="color: #888;">Exec/s</div>
                            <div style="color: #00ff00; font-weight: bold;">${campaign.exec_per_sec.toFixed(1)}</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function addCrash(crash) {
            stats.crashes.unshift(crash);
            stats.crashes = stats.crashes.slice(0, 10); // Keep last 10

            const container = document.getElementById('crash-list');
            container.innerHTML = stats.crashes.map((c, i) => `
                <div class="crash-item">
                    <div class="crash-id">Crash #${i + 1} - ${c.campaign_name || 'Unknown'}</div>
                    <div class="crash-time">${new Date(c.timestamp).toLocaleTimeString()}</div>
                    <div style="color: #888; font-size: 12px; margin-top: 5px;">
                        ${c.signature || 'No signature'}
                    </div>
                </div>
            `).join('');

            addEventLog(`New crash detected in ${crash.campaign_name}`, 'crash');
        }

        function addEventLog(message, type = 'info') {
            const container = document.getElementById('event-log');
            const time = new Date().toLocaleTimeString();
            const color = {
                info: '#00ff00',
                error: '#ff0000',
                success: '#00ff00',
                crash: '#ff0000'
            }[type] || '#00ff00';

            const entry = document.createElement('div');
            entry.style.color = color;
            entry.style.padding = '5px';
            entry.style.borderBottom = '1px solid #333';
            entry.textContent = `[${time}] ${message}`;

            container.insertBefore(entry, container.firstChild);

            // Keep last 50 entries
            while (container.children.length > 50) {
                container.removeChild(container.lastChild);
            }
        }

        function formatNumber(num) {
            if (num >= 1000000) {
                return (num / 1000000).toFixed(1) + 'M';
            } else if (num >= 1000) {
                return (num / 1000).toFixed(1) + 'K';
            }
            return num.toString();
        }

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            const secs = seconds % 60;

            if (hours > 0) {
                return `${hours}h ${minutes}m`;
            } else if (minutes > 0) {
                return `${minutes}m ${secs}s`;
            } else {
                return `${secs}s`;
            }
        }

        // Connect on load
        connect();

        // Update uptime every second
        setInterval(() => {
            const uptime = Math.floor((Date.now() - startTime) / 1000);
            document.getElementById('uptime').textContent = formatUptime(uptime);
        }, 1000);

        // Simulate data for demo (remove in production)
        setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                // Request statistics update
                ws.send(JSON.stringify({ type: 'get_statistics' }));
            }
        }, 2000);
    </script>
</body>
</html>
"""


# ==============================================================================
# DASHBOARD SERVER
# ==============================================================================

class DashboardServer:
    """
    Web server for monitoring dashboard

    Serves HTML dashboard and provides WebSocket endpoint for real-time updates.
    """

    def __init__(
        self,
        coordinator: Any,
        host: str = "0.0.0.0",
        port: int = 8888
    ):
        """
        Initialize dashboard server

        Args:
            coordinator: MCPFuzzingCoordinator instance
            host: Server host
            port: Server port
        """
        self.coordinator = coordinator
        self.host = host
        self.port = port
        self.clients: List[Any] = []

        logger.info(f"Dashboard server initialized on {host}:{port}")

    def get_html(self) -> str:
        """Get dashboard HTML"""
        return DASHBOARD_HTML

    async def start(self):
        """Start dashboard server"""
        logger.info(f"Dashboard server starting on http://{self.host}:{self.port}")
        logger.info("Note: This is a simplified implementation.")
        logger.info("For production, use aiohttp or FastAPI with WebSocket support.")

        # In production, you would use aiohttp or FastAPI here:
        # from aiohttp import web
        # app = web.Application()
        # app.router.add_get('/', self.handle_index)
        # app.router.add_get('/ws', self.handle_websocket)
        # runner = web.AppRunner(app)
        # await runner.setup()
        # site = web.TCPSite(runner, self.host, self.port)
        # await site.start()

        # For now, just save HTML to file
        dashboard_file = Path("/tmp/hyfuzz_dashboard.html")
        with open(dashboard_file, 'w') as f:
            f.write(self.get_html())

        logger.info(f"Dashboard HTML saved to: {dashboard_file}")
        logger.info(f"Open file://{dashboard_file} in your browser")

    async def broadcast_statistics(self):
        """Broadcast statistics to all connected clients"""
        while True:
            try:
                stats = await self.coordinator.get_global_statistics()

                message = {
                    "type": "statistics",
                    "data": stats
                }

                # In production, broadcast to WebSocket clients
                # for client in self.clients:
                #     await client.send_json(message)

                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"Error broadcasting statistics: {e}")
                await asyncio.sleep(5)


# ==============================================================================
# TESTING
# ==============================================================================

async def test_dashboard():
    """Test dashboard"""
    logging.basicConfig(level=logging.INFO)

    # Mock coordinator
    class MockCoordinator:
        async def get_global_statistics(self):
            return {
                "total_campaigns": 5,
                "running_campaigns": 2,
                "total_nodes": 3,
                "active_nodes": 2,
                "total_executions": 125000,
                "total_unique_crashes": 15,
                "avg_exec_per_sec": 2500.5,
                "llm_stats": {
                    "cache_hit_rate": 65.5,
                    "tokens_saved": 45000,
                    "batch_efficiency": 78.2,
                    "avg_response_time": 125.3
                }
            }

    coordinator = MockCoordinator()

    # Create dashboard server
    dashboard = DashboardServer(coordinator, port=8888)

    # Start server
    await dashboard.start()

    print("\n" + "="*70)
    print("Dashboard is ready!")
    print("="*70)
    print("\nThe dashboard HTML has been generated.")
    print("In production, this would be a full web server with WebSocket support.")
    print("\nFor a complete implementation, integrate with aiohttp or FastAPI:")
    print("  pip install aiohttp")
    print("  or")
    print("  pip install fastapi uvicorn")


if __name__ == "__main__":
    asyncio.run(test_dashboard())
