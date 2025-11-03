"""HyFuzz Monitoring Dashboard Launcher.

This script starts a web-based monitoring dashboard that provides real-time
visualization of fuzzing campaigns, defense telemetry, LLM judge feedback,
and system health metrics.

The dashboard offers:
- Campaign progress and statistics
- Live execution monitoring
- Defense verdict distribution
- Judge score analytics
- System resource usage
- Protocol-specific metrics

Technology stack:
- FastAPI for the web framework
- Server-Sent Events (SSE) for real-time updates
- Static HTML/CSS/JavaScript for the frontend
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Try to import FastAPI, provide fallback if not available
try:
    from fastapi import FastAPI, Request
    from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
    from fastapi.staticfiles import StaticFiles
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    uvicorn = None


@dataclass
class DashboardConfig:
    """Configuration for the monitoring dashboard."""

    host: str = "0.0.0.0"
    port: int = 8888
    log_level: str = "INFO"
    reload: bool = False
    data_refresh_interval: int = 5  # seconds


class DashboardMetrics:
    """Container for dashboard metrics and statistics."""

    def __init__(self):
        self.campaigns: List[Dict] = []
        self.executions: List[Dict] = []
        self.defense_verdicts: Dict[str, int] = {
            "monitor": 0,
            "investigate": 0,
            "block": 0,
            "escalate": 0
        }
        self.judge_scores: List[float] = []
        self.protocol_stats: Dict[str, int] = {}
        self.system_health: Dict[str, any] = {
            "status": "healthy",
            "uptime": 0,
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
        }

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary for JSON serialization."""
        return {
            "campaigns": self.campaigns,
            "executions": self.executions[-100:],  # Last 100 executions
            "defense_verdicts": self.defense_verdicts,
            "judge_scores": self.judge_scores[-100:],  # Last 100 scores
            "protocol_stats": self.protocol_stats,
            "system_health": self.system_health,
            "timestamp": datetime.now().isoformat(),
        }


class DashboardApp:
    """Web application for the HyFuzz monitoring dashboard."""

    def __init__(self, config: DashboardConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.metrics = DashboardMetrics()

        if not FASTAPI_AVAILABLE:
            self.logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
            raise RuntimeError("FastAPI is required for the dashboard")

        self.app = FastAPI(title="HyFuzz Dashboard", version="1.0.0")
        self._setup_routes()

    def _setup_logging(self) -> logging.Logger:
        """Initialize logging configuration."""
        log_path = PROJECT_ROOT / "logs" / "dashboard.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper(), logging.INFO),
            format="%(asctime)s - %(levelname)s - [Dashboard] - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_path, encoding="utf-8"),
            ],
        )
        return logging.getLogger("hyfuzz.dashboard")

    def _setup_routes(self) -> None:
        """Configure API routes for the dashboard."""

        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """Serve the main dashboard HTML page."""
            return self._generate_dashboard_html()

        @self.app.get("/api/metrics")
        async def get_metrics():
            """Return current metrics as JSON."""
            return JSONResponse(content=self.metrics.to_dict())

        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return JSONResponse(content={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })

        @self.app.get("/api/stream")
        async def stream_metrics():
            """Server-Sent Events endpoint for real-time updates."""
            async def event_generator():
                while True:
                    # Send metrics update
                    data = json.dumps(self.metrics.to_dict())
                    yield f"data: {data}\n\n"
                    await asyncio.sleep(self.config.data_refresh_interval)

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream"
            )

    def _generate_dashboard_html(self) -> str:
        """Generate the HTML content for the dashboard.

        Returns:
            HTML string with embedded CSS and JavaScript
        """
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HyFuzz Monitoring Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a2e;
            color: #eee;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #16213e;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card h2 {
            font-size: 1.3em;
            margin-bottom: 15px;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #0f3460;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #aaa; }
        .metric-value {
            font-weight: bold;
            color: #4ecca3;
        }
        .status-healthy { color: #4ecca3; }
        .status-warning { color: #ffd700; }
        .status-critical { color: #ff6b6b; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        .verdict-monitor { color: #4ecca3; }
        .verdict-investigate { color: #ffd700; }
        .verdict-block { color: #ff6b6b; }
        .verdict-escalate { color: #ff3838; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 HyFuzz Monitoring Dashboard</h1>
        <p>Real-time Fuzzing Campaign Analytics</p>
    </div>

    <div class="grid">
        <div class="card">
            <h2>System Health</h2>
            <div class="metric">
                <span class="metric-label">Status:</span>
                <span class="metric-value status-healthy" id="health-status">Healthy</span>
            </div>
            <div class="metric">
                <span class="metric-label">Uptime:</span>
                <span class="metric-value" id="uptime">0h 0m</span>
            </div>
            <div class="metric">
                <span class="metric-label">CPU Usage:</span>
                <span class="metric-value" id="cpu">0%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Memory Usage:</span>
                <span class="metric-value" id="memory">0%</span>
            </div>
        </div>

        <div class="card">
            <h2>Campaign Summary</h2>
            <div class="metric">
                <span class="metric-label">Active Campaigns:</span>
                <span class="metric-value" id="active-campaigns">0</span>
            </div>
            <div class="metric">
                <span class="metric-label">Total Executions:</span>
                <span class="metric-value" id="total-executions">0</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Judge Score:</span>
                <span class="metric-value" id="avg-score">0.00</span>
            </div>
        </div>

        <div class="card">
            <h2>Defense Verdicts</h2>
            <div class="metric">
                <span class="metric-label">Monitor:</span>
                <span class="metric-value verdict-monitor" id="verdict-monitor">0</span>
            </div>
            <div class="metric">
                <span class="metric-label">Investigate:</span>
                <span class="metric-value verdict-investigate" id="verdict-investigate">0</span>
            </div>
            <div class="metric">
                <span class="metric-label">Block:</span>
                <span class="metric-value verdict-block" id="verdict-block">0</span>
            </div>
            <div class="metric">
                <span class="metric-label">Escalate:</span>
                <span class="metric-value verdict-escalate" id="verdict-escalate">0</span>
            </div>
        </div>

        <div class="card">
            <h2>Protocol Statistics</h2>
            <div id="protocol-stats">
                <div class="metric">
                    <span class="metric-label">No data yet</span>
                    <span class="metric-value">-</span>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>HyFuzz Phase 3 Dashboard | Last updated: <span id="last-update">-</span></p>
    </div>

    <script>
        // Connect to SSE endpoint for real-time updates
        const eventSource = new EventSource('/api/stream');

        eventSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        function updateDashboard(data) {
            // System health
            document.getElementById('health-status').textContent = data.system_health.status;
            document.getElementById('uptime').textContent = formatUptime(data.system_health.uptime);
            document.getElementById('cpu').textContent = data.system_health.cpu_percent.toFixed(1) + '%';
            document.getElementById('memory').textContent = data.system_health.memory_percent.toFixed(1) + '%';

            // Campaign summary
            document.getElementById('active-campaigns').textContent = data.campaigns.length;
            document.getElementById('total-executions').textContent = data.executions.length;

            const avgScore = data.judge_scores.length > 0
                ? (data.judge_scores.reduce((a, b) => a + b, 0) / data.judge_scores.length).toFixed(2)
                : '0.00';
            document.getElementById('avg-score').textContent = avgScore;

            // Defense verdicts
            document.getElementById('verdict-monitor').textContent = data.defense_verdicts.monitor;
            document.getElementById('verdict-investigate').textContent = data.defense_verdicts.investigate;
            document.getElementById('verdict-block').textContent = data.defense_verdicts.block;
            document.getElementById('verdict-escalate').textContent = data.defense_verdicts.escalate;

            // Protocol stats
            const protocolDiv = document.getElementById('protocol-stats');
            if (Object.keys(data.protocol_stats).length > 0) {
                protocolDiv.innerHTML = '';
                for (const [protocol, count] of Object.entries(data.protocol_stats)) {
                    protocolDiv.innerHTML += `
                        <div class="metric">
                            <span class="metric-label">${protocol.toUpperCase()}:</span>
                            <span class="metric-value">${count}</span>
                        </div>
                    `;
                }
            }

            // Last update timestamp
            document.getElementById('last-update').textContent = new Date(data.timestamp).toLocaleString();
        }

        function formatUptime(seconds) {
            const hours = Math.floor(seconds / 3600);
            const minutes = Math.floor((seconds % 3600) / 60);
            return `${hours}h ${minutes}m`;
        }

        // Initial load
        fetch('/api/metrics')
            .then(response => response.json())
            .then(data => updateDashboard(data));
    </script>
</body>
</html>"""

    async def start(self) -> None:
        """Start the dashboard web server."""
        self.logger.info(f"Starting HyFuzz dashboard on {self.config.host}:{self.config.port}")

        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower(),
            reload=self.config.reload,
        )
        server = uvicorn.Server(config)
        await server.serve()


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="HyFuzz monitoring dashboard launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start dashboard on default port 8888
  python start_dashboard.py

  # Start on custom port with debug logging
  python start_dashboard.py --port 9000 --log-level DEBUG

  # Enable auto-reload for development
  python start_dashboard.py --reload
        """,
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the dashboard (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8888,
        help="Port to bind the dashboard (default: 8888)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes (development only)",
    )
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=5,
        help="Data refresh interval in seconds (default: 5)",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point for the dashboard launcher."""
    args = parse_arguments()

    # Check FastAPI availability
    if not FASTAPI_AVAILABLE:
        print("❌ Error: FastAPI is not installed")
        print("   Install with: pip install fastapi uvicorn")
        print("   Or: pip install -r requirements-dev.txt")
        return 1

    # Build configuration
    config = DashboardConfig(
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
        data_refresh_interval=args.refresh_interval,
    )

    # Create and start dashboard
    dashboard = DashboardApp(config)

    print(f"🚀 Starting HyFuzz Dashboard...")
    print(f"   URL: http://{config.host}:{config.port}")
    print(f"   Log level: {config.log_level}")
    print(f"   Refresh interval: {config.data_refresh_interval}s")
    print(f"   Press Ctrl+C to stop")
    print()

    try:
        asyncio.run(dashboard.start())
        return 0
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
        return 0
    except Exception as e:
        logging.error(f"Fatal error in dashboard: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
