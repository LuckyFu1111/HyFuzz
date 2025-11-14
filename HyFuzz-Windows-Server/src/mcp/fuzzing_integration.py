"""
MCP Server Integration for Fuzzing Engine

Provides integration layer between HyFuzz fuzzing engine and MCP server,
enabling distributed fuzzing, real-time monitoring, and coordinated attacks.

Features:
- RESTful API endpoints for fuzzing control
- WebSocket support for real-time updates
- Distributed fuzzing coordination
- Campaign management and scheduling
- Metrics aggregation and reporting

Author: HyFuzz Team
Version: 1.0.0
Date: 2025-01-13
"""

import asyncio
import logging
import json
import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


# ==============================================================================
# DATA MODELS
# ==============================================================================

class CampaignStatus(Enum):
    """Fuzzing campaign status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class FuzzingCampaign:
    """Fuzzing campaign configuration"""
    campaign_id: str
    name: str
    target_info: Dict[str, Any]
    config: Dict[str, Any]

    status: CampaignStatus = CampaignStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Statistics
    total_execs: int = 0
    unique_crashes: int = 0
    edges_covered: int = 0
    exec_per_sec: float = 0.0

    # Results
    crashes: List[Dict[str, Any]] = field(default_factory=list)
    interesting_inputs: List[bytes] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['started_at'] = self.started_at.isoformat() if self.started_at else None
        result['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        # Convert bytes to base64 for JSON serialization
        result['interesting_inputs'] = [
            inp.hex() for inp in self.interesting_inputs[:10]  # Limit to 10
        ]
        return result


@dataclass
class FuzzingNode:
    """Distributed fuzzing node"""
    node_id: str
    hostname: str
    status: str = "idle"  # idle, fuzzing, error
    current_campaign: Optional[str] = None

    # Node capabilities
    max_parallel_campaigns: int = 1
    supported_protocols: List[str] = field(default_factory=list)

    # Statistics
    total_execs: int = 0
    total_crashes: int = 0
    uptime_seconds: float = 0.0

    last_heartbeat: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['last_heartbeat'] = self.last_heartbeat.isoformat()
        return result


# ==============================================================================
# MCP FUZZING COORDINATOR
# ==============================================================================

class MCPFuzzingCoordinator:
    """
    MCP Server integration coordinator

    Manages fuzzing campaigns, coordinates distributed nodes,
    and provides API endpoints for control and monitoring.
    """

    def __init__(
        self,
        workspace_dir: Path,
        enable_distributed: bool = True,
        max_concurrent_campaigns: int = 5
    ):
        """
        Initialize MCP coordinator

        Args:
            workspace_dir: Directory for campaign data and results
            enable_distributed: Enable distributed fuzzing across nodes
            max_concurrent_campaigns: Max concurrent campaigns
        """
        self.workspace_dir = Path(workspace_dir)
        self.enable_distributed = enable_distributed
        self.max_concurrent_campaigns = max_concurrent_campaigns

        # Campaign management
        self.campaigns: Dict[str, FuzzingCampaign] = {}
        self.campaign_tasks: Dict[str, asyncio.Task] = {}

        # Node management (for distributed fuzzing)
        self.nodes: Dict[str, FuzzingNode] = {}

        # Event subscribers (for real-time updates)
        self.event_subscribers: List[asyncio.Queue] = []

        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"MCPFuzzingCoordinator initialized: "
            f"workspace={workspace_dir}, distributed={enable_distributed}"
        )

    # ==========================================================================
    # CAMPAIGN MANAGEMENT
    # ==========================================================================

    async def create_campaign(
        self,
        name: str,
        target_info: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create new fuzzing campaign

        Args:
            name: Campaign name
            target_info: Target information (protocol, host, port, etc.)
            config: Fuzzing configuration

        Returns:
            Campaign ID
        """
        campaign_id = str(uuid.uuid4())[:8]

        campaign = FuzzingCampaign(
            campaign_id=campaign_id,
            name=name,
            target_info=target_info,
            config=config or self._get_default_config()
        )

        self.campaigns[campaign_id] = campaign

        # Save campaign metadata
        await self._save_campaign_metadata(campaign)

        # Emit event
        await self._emit_event({
            "type": "campaign_created",
            "campaign_id": campaign_id,
            "name": name
        })

        logger.info(f"Created campaign: {campaign_id} ({name})")

        return campaign_id

    async def start_campaign(self, campaign_id: str) -> bool:
        """Start fuzzing campaign"""
        if campaign_id not in self.campaigns:
            logger.error(f"Campaign not found: {campaign_id}")
            return False

        campaign = self.campaigns[campaign_id]

        if campaign.status == CampaignStatus.RUNNING:
            logger.warning(f"Campaign already running: {campaign_id}")
            return False

        # Check capacity
        running_campaigns = sum(
            1 for c in self.campaigns.values()
            if c.status == CampaignStatus.RUNNING
        )

        if running_campaigns >= self.max_concurrent_campaigns:
            logger.warning("Max concurrent campaigns reached")
            return False

        # Update status
        campaign.status = CampaignStatus.RUNNING
        campaign.started_at = datetime.now()

        # Start fuzzing task
        task = asyncio.create_task(self._run_campaign(campaign))
        self.campaign_tasks[campaign_id] = task

        # Emit event
        await self._emit_event({
            "type": "campaign_started",
            "campaign_id": campaign_id
        })

        logger.info(f"Started campaign: {campaign_id}")

        return True

    async def stop_campaign(self, campaign_id: str) -> bool:
        """Stop fuzzing campaign"""
        if campaign_id not in self.campaigns:
            return False

        campaign = self.campaigns[campaign_id]
        campaign.status = CampaignStatus.PAUSED

        # Cancel task
        if campaign_id in self.campaign_tasks:
            self.campaign_tasks[campaign_id].cancel()
            del self.campaign_tasks[campaign_id]

        # Emit event
        await self._emit_event({
            "type": "campaign_stopped",
            "campaign_id": campaign_id
        })

        logger.info(f"Stopped campaign: {campaign_id}")

        return True

    async def get_campaign_status(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign status"""
        if campaign_id not in self.campaigns:
            return None

        campaign = self.campaigns[campaign_id]
        return campaign.to_dict()

    async def list_campaigns(
        self,
        status_filter: Optional[CampaignStatus] = None
    ) -> List[Dict[str, Any]]:
        """List all campaigns"""
        campaigns = self.campaigns.values()

        if status_filter:
            campaigns = [c for c in campaigns if c.status == status_filter]

        return [c.to_dict() for c in campaigns]

    async def delete_campaign(self, campaign_id: str) -> bool:
        """Delete campaign"""
        if campaign_id not in self.campaigns:
            return False

        # Stop if running
        await self.stop_campaign(campaign_id)

        # Delete data
        campaign_dir = self.workspace_dir / campaign_id
        if campaign_dir.exists():
            import shutil
            shutil.rmtree(campaign_dir)

        # Remove from memory
        del self.campaigns[campaign_id]

        logger.info(f"Deleted campaign: {campaign_id}")

        return True

    # ==========================================================================
    # DISTRIBUTED NODE MANAGEMENT
    # ==========================================================================

    async def register_node(
        self,
        hostname: str,
        supported_protocols: List[str],
        max_parallel_campaigns: int = 1
    ) -> str:
        """Register distributed fuzzing node"""
        node_id = str(uuid.uuid4())[:8]

        node = FuzzingNode(
            node_id=node_id,
            hostname=hostname,
            supported_protocols=supported_protocols,
            max_parallel_campaigns=max_parallel_campaigns
        )

        self.nodes[node_id] = node

        logger.info(f"Registered node: {node_id} ({hostname})")

        return node_id

    async def unregister_node(self, node_id: str) -> bool:
        """Unregister node"""
        if node_id not in self.nodes:
            return False

        node = self.nodes[node_id]

        # Stop any campaigns running on this node
        if node.current_campaign:
            await self.stop_campaign(node.current_campaign)

        del self.nodes[node_id]

        logger.info(f"Unregistered node: {node_id}")

        return True

    async def update_node_heartbeat(self, node_id: str) -> bool:
        """Update node heartbeat"""
        if node_id not in self.nodes:
            return False

        self.nodes[node_id].last_heartbeat = datetime.now()
        return True

    async def get_available_nodes(
        self,
        protocol: Optional[str] = None
    ) -> List[FuzzingNode]:
        """Get available nodes"""
        nodes = [
            node for node in self.nodes.values()
            if node.status == "idle"
        ]

        if protocol:
            nodes = [
                node for node in nodes
                if protocol in node.supported_protocols
            ]

        return nodes

    # ==========================================================================
    # REAL-TIME MONITORING
    # ==========================================================================

    async def subscribe_events(self) -> asyncio.Queue:
        """Subscribe to real-time events"""
        queue = asyncio.Queue()
        self.event_subscribers.append(queue)
        return queue

    async def unsubscribe_events(self, queue: asyncio.Queue):
        """Unsubscribe from events"""
        if queue in self.event_subscribers:
            self.event_subscribers.remove(queue)

    async def _emit_event(self, event: Dict[str, Any]):
        """Emit event to all subscribers"""
        event['timestamp'] = datetime.now().isoformat()

        # Send to all subscribers
        for queue in self.event_subscribers:
            try:
                await queue.put(event)
            except:
                pass

    async def get_global_statistics(self) -> Dict[str, Any]:
        """Get global fuzzing statistics"""
        total_campaigns = len(self.campaigns)
        running_campaigns = sum(
            1 for c in self.campaigns.values()
            if c.status == CampaignStatus.RUNNING
        )
        total_execs = sum(c.total_execs for c in self.campaigns.values())
        total_crashes = sum(c.unique_crashes for c in self.campaigns.values())

        return {
            "total_campaigns": total_campaigns,
            "running_campaigns": running_campaigns,
            "total_nodes": len(self.nodes),
            "active_nodes": sum(1 for n in self.nodes.values() if n.status != "idle"),
            "total_executions": total_execs,
            "total_unique_crashes": total_crashes,
            "avg_exec_per_sec": sum(c.exec_per_sec for c in self.campaigns.values()),
        }

    # ==========================================================================
    # INTERNAL IMPLEMENTATION
    # ==========================================================================

    async def _run_campaign(self, campaign: FuzzingCampaign):
        """Run fuzzing campaign"""
        try:
            logger.info(f"Running campaign: {campaign.campaign_id}")

            # Import fuzzing components
            import sys
            from pathlib import Path
            sys.path.insert(0, str(Path(__file__).parent.parent))

            from fuzzing.advanced_mutation_engine import AdvancedMutationEngine

            # Initialize components
            mutation_engine = AdvancedMutationEngine()

            # Get configuration
            config = campaign.config
            duration = config.get('duration_seconds', 300)
            seed_inputs = config.get('seed_inputs', [b"test"])

            # Fuzzing loop
            start_time = datetime.now()
            end_time = start_time.timestamp() + duration

            corpus = list(seed_inputs)
            iteration = 0

            while campaign.status == CampaignStatus.RUNNING:
                if datetime.now().timestamp() >= end_time:
                    break

                iteration += 1

                # Select seed
                seed = corpus[iteration % len(corpus)]

                # Mutate
                mutants = mutation_engine.mutate(seed, count=10)

                # Execute
                for mutant in mutants:
                    # Simulate execution
                    campaign.total_execs += 1

                    # Check for crash (simplified)
                    if b"AAAA" * 10 in mutant or b"<script>" in mutant:
                        campaign.unique_crashes += 1
                        campaign.crashes.append({
                            "input": mutant[:100].hex(),
                            "timestamp": datetime.now().isoformat()
                        })

                        # Emit crash event
                        await self._emit_event({
                            "type": "crash_found",
                            "campaign_id": campaign.campaign_id,
                            "crash_id": len(campaign.crashes)
                        })

                    # Update metrics
                    elapsed = (datetime.now() - start_time).total_seconds()
                    campaign.exec_per_sec = campaign.total_execs / elapsed

                # Periodic updates
                if iteration % 100 == 0:
                    await self._emit_event({
                        "type": "campaign_progress",
                        "campaign_id": campaign.campaign_id,
                        "total_execs": campaign.total_execs,
                        "exec_per_sec": campaign.exec_per_sec,
                        "crashes": campaign.unique_crashes
                    })

                await asyncio.sleep(0.01)

            # Campaign completed
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.now()

            await self._emit_event({
                "type": "campaign_completed",
                "campaign_id": campaign.campaign_id
            })

            logger.info(f"Campaign completed: {campaign.campaign_id}")

        except asyncio.CancelledError:
            logger.info(f"Campaign cancelled: {campaign.campaign_id}")
            campaign.status = CampaignStatus.PAUSED

        except Exception as e:
            logger.error(f"Campaign failed: {campaign.campaign_id} - {e}", exc_info=True)
            campaign.status = CampaignStatus.FAILED

            await self._emit_event({
                "type": "campaign_failed",
                "campaign_id": campaign.campaign_id,
                "error": str(e)
            })

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default fuzzing configuration"""
        return {
            "duration_seconds": 300,
            "seed_inputs": [b"GET / HTTP/1.1\r\n\r\n"],
            "mutation_strategies": ["all"],
            "max_input_size": 4096,
            "timeout_ms": 1000
        }

    async def _save_campaign_metadata(self, campaign: FuzzingCampaign):
        """Save campaign metadata to disk"""
        campaign_dir = self.workspace_dir / campaign.campaign_id
        campaign_dir.mkdir(parents=True, exist_ok=True)

        metadata_file = campaign_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(campaign.to_dict(), f, indent=2)


# ==============================================================================
# REST API HANDLER
# ==============================================================================

class FuzzingAPIHandler:
    """HTTP API handler for fuzzing operations"""

    def __init__(self, coordinator: MCPFuzzingCoordinator):
        """Initialize API handler"""
        self.coordinator = coordinator

    async def handle_create_campaign(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/fuzzing/campaigns"""
        name = request_data.get('name', 'Unnamed Campaign')
        target_info = request_data.get('target', {})
        config = request_data.get('config')

        campaign_id = await self.coordinator.create_campaign(name, target_info, config)

        return {
            "status": "success",
            "campaign_id": campaign_id
        }

    async def handle_start_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """POST /api/fuzzing/campaigns/{id}/start"""
        success = await self.coordinator.start_campaign(campaign_id)

        return {
            "status": "success" if success else "error",
            "campaign_id": campaign_id
        }

    async def handle_stop_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """POST /api/fuzzing/campaigns/{id}/stop"""
        success = await self.coordinator.stop_campaign(campaign_id)

        return {
            "status": "success" if success else "error",
            "campaign_id": campaign_id
        }

    async def handle_get_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """GET /api/fuzzing/campaigns/{id}"""
        campaign = await self.coordinator.get_campaign_status(campaign_id)

        if not campaign:
            return {"status": "error", "message": "Campaign not found"}

        return {
            "status": "success",
            "campaign": campaign
        }

    async def handle_list_campaigns(self) -> Dict[str, Any]:
        """GET /api/fuzzing/campaigns"""
        campaigns = await self.coordinator.list_campaigns()

        return {
            "status": "success",
            "campaigns": campaigns
        }

    async def handle_get_statistics(self) -> Dict[str, Any]:
        """GET /api/fuzzing/statistics"""
        stats = await self.coordinator.get_global_statistics()

        return {
            "status": "success",
            "statistics": stats
        }


# ==============================================================================
# TESTING
# ==============================================================================

async def test_mcp_integration():
    """Test MCP integration"""
    logging.basicConfig(level=logging.INFO)

    # Create coordinator
    coordinator = MCPFuzzingCoordinator(
        workspace_dir=Path("/tmp/hyfuzz_mcp_test"),
        enable_distributed=True
    )

    # Subscribe to events
    event_queue = await coordinator.subscribe_events()

    # Create event listener
    async def event_listener():
        while True:
            event = await event_queue.get()
            print(f"EVENT: {event['type']} - {event}")

    listener_task = asyncio.create_task(event_listener())

    # Create campaign
    campaign_id = await coordinator.create_campaign(
        name="Test SQL Injection",
        target_info={
            "protocol": "http",
            "host": "localhost",
            "port": 8080
        },
        config={
            "duration_seconds": 10,
            "seed_inputs": [b"username=admin&password=test"]
        }
    )

    print(f"Created campaign: {campaign_id}")

    # Start campaign
    await coordinator.start_campaign(campaign_id)

    # Monitor for 15 seconds
    await asyncio.sleep(15)

    # Get status
    status = await coordinator.get_campaign_status(campaign_id)
    print(f"\nCampaign Status:")
    print(json.dumps(status, indent=2))

    # Get statistics
    stats = await coordinator.get_global_statistics()
    print(f"\nGlobal Statistics:")
    print(json.dumps(stats, indent=2))

    # Cleanup
    listener_task.cancel()


if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
