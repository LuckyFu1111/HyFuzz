"""
Batch LLM Request Processor

Implements intelligent batching and parallelization of LLM requests
to maximize throughput and minimize costs.

Features:
- Request queuing and automatic batching
- Parallel request processing with rate limiting
- Token usage optimization
- Request deduplication and similarity grouping
- Automatic retry with exponential backoff

Author: HyFuzz Team
Version: 1.0.0
Date: 2025-01-13
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


# ==============================================================================
# DATA MODELS
# ==============================================================================

@dataclass
class LLMRequest:
    """Individual LLM request"""
    prompt: str
    request_id: str = ""
    priority: int = 0  # Higher = more urgent
    metadata: Dict[str, Any] = field(default_factory=dict)
    submitted_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.request_id:
            self.request_id = hashlib.md5(
                f"{self.prompt}{time.time()}".encode()
            ).hexdigest()[:16]


@dataclass
class LLMResponse:
    """LLM response with timing information"""
    request_id: str
    prompt: str
    response: str
    token_count: int = 0
    response_time_ms: float = 0.0
    from_cache: bool = False
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchStats:
    """Batch processing statistics"""
    total_requests: int = 0
    batched_requests: int = 0
    parallel_requests: int = 0
    cache_hits: int = 0
    total_tokens: int = 0
    total_time_ms: float = 0.0
    errors: int = 0

    @property
    def batch_efficiency(self) -> float:
        """Percentage of requests processed in batches"""
        if self.total_requests == 0:
            return 0.0
        return (self.batched_requests / self.total_requests) * 100

    @property
    def avg_response_time_ms(self) -> float:
        """Average response time per request"""
        if self.total_requests == 0:
            return 0.0
        return self.total_time_ms / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_requests": self.total_requests,
            "batched_requests": self.batched_requests,
            "parallel_requests": self.parallel_requests,
            "cache_hits": self.cache_hits,
            "batch_efficiency": f"{self.batch_efficiency:.2f}%",
            "total_tokens": self.total_tokens,
            "avg_response_time_ms": round(self.avg_response_time_ms, 2),
            "errors": self.errors
        }


# ==============================================================================
# BATCH PROCESSOR
# ==============================================================================

class BatchLLMProcessor:
    """
    Intelligent batch processor for LLM requests

    Queues incoming requests and processes them in optimized batches
    to maximize throughput and minimize API costs.
    """

    def __init__(
        self,
        llm_function: Callable[[str], Tuple[str, int]],
        semantic_cache: Optional[Any] = None,
        batch_size: int = 10,
        batch_timeout_ms: float = 100.0,
        max_parallel: int = 5,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60
    ):
        """
        Initialize batch processor

        Args:
            llm_function: Function to call LLM (prompt) -> (response, token_count)
            semantic_cache: Optional semantic cache instance
            batch_size: Maximum requests per batch
            batch_timeout_ms: Max time to wait before processing partial batch
            max_parallel: Maximum parallel batch requests
            max_retries: Max retry attempts for failed requests
            rate_limit_per_minute: Rate limit for API calls
        """
        self.llm_function = llm_function
        self.semantic_cache = semantic_cache
        self.batch_size = batch_size
        self.batch_timeout_ms = batch_timeout_ms
        self.max_parallel = max_parallel
        self.max_retries = max_retries
        self.rate_limit_per_minute = rate_limit_per_minute

        # Request queue (priority-based)
        self.request_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

        # Response futures for async coordination
        self.response_futures: Dict[str, asyncio.Future] = {}

        # Statistics
        self.stats = BatchStats()

        # Rate limiting
        self.request_times: List[float] = []
        self.rate_limit_lock = asyncio.Lock()

        # Control flags
        self.running = False
        self.worker_task: Optional[asyncio.Task] = None

        logger.info(
            f"BatchLLMProcessor initialized: batch_size={batch_size}, "
            f"timeout={batch_timeout_ms}ms, parallel={max_parallel}"
        )

    async def start(self):
        """Start batch processing worker"""
        if self.running:
            logger.warning("Batch processor already running")
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._process_batches())
        logger.info("Batch processor started")

    async def stop(self):
        """Stop batch processing worker"""
        self.running = False
        if self.worker_task:
            await self.worker_task
        logger.info("Batch processor stopped")

    async def submit(
        self,
        prompt: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Submit request for processing

        Args:
            prompt: Input prompt
            priority: Request priority (higher = more urgent)
            metadata: Additional metadata

        Returns:
            LLM response (awaitable)
        """
        request = LLMRequest(
            prompt=prompt,
            priority=priority,
            metadata=metadata or {}
        )

        # Create future for response
        future = asyncio.Future()
        self.response_futures[request.request_id] = future

        # Check cache first
        if self.semantic_cache:
            cached = self.semantic_cache.get(prompt)
            if cached:
                self.stats.cache_hits += 1
                response = LLMResponse(
                    request_id=request.request_id,
                    prompt=prompt,
                    response=cached.response,
                    token_count=cached.token_count,
                    response_time_ms=0.0,
                    from_cache=True
                )
                future.set_result(response)
                return await future

        # Add to queue (negative priority for max-heap behavior)
        await self.request_queue.put((-priority, request))

        return await future

    async def _process_batches(self):
        """Main batch processing loop"""
        while self.running:
            try:
                # Collect batch
                batch = await self._collect_batch()

                if not batch:
                    # No requests, wait a bit
                    await asyncio.sleep(0.01)
                    continue

                # Process batch in parallel
                await self._process_batch_parallel(batch)

            except Exception as e:
                logger.error(f"Error in batch processing loop: {e}", exc_info=True)
                await asyncio.sleep(0.1)

    async def _collect_batch(self) -> List[LLMRequest]:
        """Collect batch of requests from queue"""
        batch = []
        deadline = time.time() + (self.batch_timeout_ms / 1000.0)

        while len(batch) < self.batch_size and time.time() < deadline:
            try:
                # Wait for request with timeout
                timeout = max(0.01, deadline - time.time())
                priority, request = await asyncio.wait_for(
                    self.request_queue.get(),
                    timeout=timeout
                )
                batch.append(request)

                # If queue has more ready items, grab them immediately
                while not self.request_queue.empty() and len(batch) < self.batch_size:
                    priority, request = self.request_queue.get_nowait()
                    batch.append(request)

            except asyncio.TimeoutError:
                # Timeout reached, process what we have
                break

        return batch

    async def _process_batch_parallel(self, batch: List[LLMRequest]):
        """Process batch with parallel execution"""
        # Group similar requests for deduplication
        grouped = self._group_similar_requests(batch)

        # Process groups in parallel (up to max_parallel)
        semaphore = asyncio.Semaphore(self.max_parallel)

        tasks = []
        for group_key, requests in grouped.items():
            task = asyncio.create_task(
                self._process_request_group(requests, semaphore)
            )
            tasks.append(task)

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Update stats
        self.stats.batched_requests += len(batch)

    def _group_similar_requests(
        self,
        requests: List[LLMRequest]
    ) -> Dict[str, List[LLMRequest]]:
        """Group similar requests for deduplication"""
        groups = defaultdict(list)

        for request in requests:
            # Simple grouping by prompt hash
            # In production, could use semantic similarity
            prompt_hash = hashlib.md5(request.prompt.encode()).hexdigest()[:8]
            groups[prompt_hash].append(request)

        return groups

    async def _process_request_group(
        self,
        requests: List[LLMRequest],
        semaphore: asyncio.Semaphore
    ):
        """Process group of similar requests"""
        async with semaphore:
            # Use first request as representative
            representative = requests[0]

            # Apply rate limiting
            await self._rate_limit()

            # Process with retry logic
            response_text, token_count, elapsed_ms = await self._process_with_retry(
                representative.prompt
            )

            # Cache the response
            if self.semantic_cache and response_text:
                self.semantic_cache.put(
                    prompt=representative.prompt,
                    response=response_text,
                    token_count=token_count,
                    response_time_ms=elapsed_ms
                )

            # Create responses for all requests in group
            for request in requests:
                response = LLMResponse(
                    request_id=request.request_id,
                    prompt=request.prompt,
                    response=response_text,
                    token_count=token_count,
                    response_time_ms=elapsed_ms / len(requests),  # Amortized
                    from_cache=False,
                    metadata=request.metadata
                )

                # Fulfill future
                if request.request_id in self.response_futures:
                    future = self.response_futures[request.request_id]
                    if not future.done():
                        future.set_result(response)
                    del self.response_futures[request.request_id]

                # Update stats
                self.stats.total_requests += 1
                self.stats.total_tokens += token_count
                self.stats.total_time_ms += elapsed_ms / len(requests)

    async def _process_with_retry(
        self,
        prompt: str
    ) -> Tuple[str, int, float]:
        """Process single request with retry logic"""
        last_error = None

        for attempt in range(self.max_retries):
            try:
                start_time = time.time()

                # Call LLM function
                response_text, token_count = await asyncio.to_thread(
                    self.llm_function,
                    prompt
                )

                elapsed_ms = (time.time() - start_time) * 1000

                return response_text, token_count, elapsed_ms

            except Exception as e:
                last_error = e
                logger.warning(
                    f"LLM request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                # Exponential backoff
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        # All retries failed
        self.stats.errors += 1
        logger.error(f"LLM request failed after {self.max_retries} attempts: {last_error}")
        return "", 0, 0.0

    async def _rate_limit(self):
        """Apply rate limiting"""
        async with self.rate_limit_lock:
            now = time.time()

            # Remove old timestamps (outside 1-minute window)
            self.request_times = [
                t for t in self.request_times
                if now - t < 60.0
            ]

            # Check if we need to wait
            if len(self.request_times) >= self.rate_limit_per_minute:
                oldest = self.request_times[0]
                wait_time = 60.0 - (now - oldest)
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)
                    now = time.time()

            # Record this request
            self.request_times.append(now)

    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        stats = self.stats.to_dict()
        stats.update({
            "queue_size": self.request_queue.qsize(),
            "pending_responses": len(self.response_futures),
            "running": self.running
        })
        return stats


# ==============================================================================
# TESTING
# ==============================================================================

async def test_batch_processor():
    """Test batch processor functionality"""
    logging.basicConfig(level=logging.INFO)

    # Mock LLM function
    def mock_llm(prompt: str) -> Tuple[str, int]:
        """Simulate LLM API call"""
        time.sleep(0.1)  # Simulate network latency
        response = f"Response to: {prompt[:30]}"
        tokens = len(prompt.split()) + 10
        return response, tokens

    # Create processor
    processor = BatchLLMProcessor(
        llm_function=mock_llm,
        batch_size=5,
        batch_timeout_ms=200,
        max_parallel=3
    )

    # Start processor
    await processor.start()

    # Submit multiple requests
    prompts = [
        "Generate SQL injection payload",
        "Create XSS attack vector",
        "Generate buffer overflow input",
        "Create path traversal payload",
        "Generate format string attack",
        "Create SQL injection payload",  # Duplicate
        "Generate XSS vector",  # Similar
    ]

    print("Submitting requests...")
    tasks = [processor.submit(prompt, priority=i) for i, prompt in enumerate(prompts)]

    # Wait for all responses
    responses = await asyncio.gather(*tasks)

    print("\nResponses:")
    for i, response in enumerate(responses):
        print(f"{i+1}. {response.response} (tokens={response.token_count}, "
              f"time={response.response_time_ms:.2f}ms, cache={response.from_cache})")

    # Stop processor
    await processor.stop()

    # Print stats
    print("\nBatch Processing Statistics:")
    import json
    print(json.dumps(processor.get_stats(), indent=2))


if __name__ == "__main__":
    asyncio.run(test_batch_processor())
