"""
Learning Engine for Adaptive Fuzzing

This module implements an AI-driven learning engine that:
- Learns from fuzzing feedback to improve payload generation
- Uses reinforcement learning to select optimal mutation strategies
- Tracks payload effectiveness and coverage gains
- Adapts fuzzing behavior based on historical performance
- Supports model persistence for continuous learning

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations
import json
import logging
import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, deque
from enum import Enum
import random
import time
import math


class FeedbackType(Enum):
    """Types of feedback from fuzzing execution"""
    NEW_COVERAGE = "new_coverage"
    CRASH_FOUND = "crash_found"
    HANG_DETECTED = "hang_detected"
    NO_CHANGE = "no_change"
    TIMEOUT = "timeout"
    ERROR = "error"


class MutationStrategy(Enum):
    """Available mutation strategies"""
    BIT_FLIP = "bit_flip"
    BYTE_FLIP = "byte_flip"
    ARITHMETIC = "arithmetic"
    INTERESTING_VALUES = "interesting_values"
    BLOCK_OPERATIONS = "block_operations"
    DICTIONARY = "dictionary"
    SPLICE = "splice"
    HAVOC = "havoc"
    PROTOCOL_AWARE = "protocol_aware"
    LLM_SEMANTIC = "llm_semantic"


@dataclass
class FeedbackData:
    """Structured feedback from fuzzing execution"""
    feedback_type: FeedbackType
    strategy_used: MutationStrategy
    execution_time: float
    new_edges_covered: int = 0
    crash_severity: Optional[str] = None
    payload_size: int = 0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyStats:
    """Statistics for a mutation strategy"""
    total_tries: int = 0
    new_coverage_count: int = 0
    crash_count: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 0.0
    last_success_time: float = 0.0
    consecutive_failures: int = 0


class LearningEngine:
    """
    AI-Driven Learning Engine for Adaptive Fuzzing

    Features:
    - Multi-Armed Bandit (MAB) algorithm for strategy selection
    - Reinforcement learning with epsilon-greedy exploration
    - Bayesian optimization for parameter tuning
    - Coverage-guided feedback integration
    - Model persistence for continuous learning

    Example:
        >>> engine = LearningEngine()
        >>> feedback = FeedbackData(
        ...     feedback_type=FeedbackType.NEW_COVERAGE,
        ...     strategy_used=MutationStrategy.BIT_FLIP,
        ...     execution_time=0.5,
        ...     new_edges_covered=10
        ... )
        >>> result = engine.update(feedback)
        >>> next_strategy = engine.select_strategy()
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.2,
        epsilon_decay: float = 0.995,
        min_epsilon: float = 0.05
    ):
        """
        Initialize Learning Engine

        Args:
            learning_rate: Learning rate for Q-learning updates
            discount_factor: Discount factor for future rewards
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            min_epsilon: Minimum epsilon value
        """
        self.logger = logging.getLogger(__name__)

        # Learning parameters
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.min_epsilon = min_epsilon

        # Strategy statistics
        self.strategy_stats: Dict[MutationStrategy, StrategyStats] = {
            strategy: StrategyStats() for strategy in MutationStrategy
        }

        # Q-values for reinforcement learning
        self.q_values: Dict[MutationStrategy, float] = {
            strategy: 0.0 for strategy in MutationStrategy
        }

        # Feedback history (sliding window)
        self.feedback_history: deque = deque(maxlen=1000)

        # Performance metrics
        self.total_feedback_count = 0
        self.total_new_coverage = 0
        self.total_crashes = 0

        # Bayesian priors for strategy selection (Beta distribution parameters)
        self.strategy_alpha: Dict[MutationStrategy, float] = {
            strategy: 1.0 for strategy in MutationStrategy
        }
        self.strategy_beta: Dict[MutationStrategy, float] = {
            strategy: 1.0 for strategy in MutationStrategy
        }

        self.logger.info(
            f"Learning Engine initialized: lr={learning_rate}, "
            f"gamma={discount_factor}, epsilon={epsilon}"
        )

    def update(self, feedback: FeedbackData | str) -> str:
        """
        Update learning model based on feedback

        Args:
            feedback: Feedback data from fuzzing execution (FeedbackData object or legacy string)

        Returns:
            Status message describing the update
        """
        # Handle legacy string feedback format
        if isinstance(feedback, str):
            feedback = self._parse_legacy_feedback(feedback)

        self.total_feedback_count += 1
        self.feedback_history.append(feedback)

        # Update strategy statistics
        stats = self.strategy_stats[feedback.strategy_used]
        stats.total_tries += 1

        # Calculate reward based on feedback type
        reward = self._calculate_reward(feedback)

        # Update new coverage count
        if feedback.feedback_type == FeedbackType.NEW_COVERAGE:
            stats.new_coverage_count += 1
            stats.last_success_time = feedback.timestamp
            stats.consecutive_failures = 0
            self.total_new_coverage += feedback.new_edges_covered
        elif feedback.feedback_type == FeedbackType.CRASH_FOUND:
            stats.crash_count += 1
            stats.last_success_time = feedback.timestamp
            stats.consecutive_failures = 0
            self.total_crashes += 1
        else:
            stats.consecutive_failures += 1

        # Update execution time (running average)
        if stats.total_tries == 1:
            stats.avg_execution_time = feedback.execution_time
        else:
            stats.avg_execution_time = (
                0.9 * stats.avg_execution_time + 0.1 * feedback.execution_time
            )

        # Update success rate
        stats.success_rate = (
            (stats.new_coverage_count + stats.crash_count) / stats.total_tries
        )

        # Update Q-value using Q-learning
        self._update_q_value(feedback.strategy_used, reward)

        # Update Bayesian priors
        self._update_bayesian_priors(feedback.strategy_used, reward > 0)

        # Decay epsilon
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

        self.logger.debug(
            f"Updated model: strategy={feedback.strategy_used.value}, "
            f"reward={reward:.2f}, q_value={self.q_values[feedback.strategy_used]:.2f}"
        )

        return self._format_update_result(feedback, reward)

    def _parse_legacy_feedback(self, feedback_str: str) -> FeedbackData:
        """Parse legacy string feedback format"""
        # Simple heuristic parsing
        if "crash" in feedback_str.lower():
            feedback_type = FeedbackType.CRASH_FOUND
        elif "coverage" in feedback_str.lower() or "positive" in feedback_str.lower():
            feedback_type = FeedbackType.NEW_COVERAGE
        elif "negative" in feedback_str.lower():
            feedback_type = FeedbackType.NO_CHANGE
        else:
            feedback_type = FeedbackType.NO_CHANGE

        return FeedbackData(
            feedback_type=feedback_type,
            strategy_used=random.choice(list(MutationStrategy)),
            execution_time=0.1,
            metadata={"legacy": True, "original": feedback_str}
        )

    def _calculate_reward(self, feedback: FeedbackData) -> float:
        """Calculate reward based on feedback"""
        reward = 0.0

        if feedback.feedback_type == FeedbackType.NEW_COVERAGE:
            # Reward proportional to new edges covered
            reward = 10.0 + feedback.new_edges_covered * 2.0
        elif feedback.feedback_type == FeedbackType.CRASH_FOUND:
            # High reward for crashes
            reward = 50.0
            # Bonus for high-severity crashes
            if feedback.crash_severity in ["high", "critical"]:
                reward += 30.0
        elif feedback.feedback_type == FeedbackType.NO_CHANGE:
            # Small negative reward for no progress
            reward = -1.0
        elif feedback.feedback_type == FeedbackType.TIMEOUT:
            # Penalty for timeouts
            reward = -5.0
        elif feedback.feedback_type == FeedbackType.ERROR:
            # Penalty for errors
            reward = -2.0

        # Penalize slow execution
        if feedback.execution_time > 1.0:
            reward -= (feedback.execution_time - 1.0) * 2.0

        return reward

    def _update_q_value(self, strategy: MutationStrategy, reward: float):
        """Update Q-value using Q-learning algorithm"""
        # Q(s,a) = Q(s,a) + α * (r + γ * max(Q(s',a')) - Q(s,a))
        # Simplified: Q(s,a) = Q(s,a) + α * (r - Q(s,a))

        current_q = self.q_values[strategy]
        new_q = current_q + self.learning_rate * (reward - current_q)
        self.q_values[strategy] = new_q

    def _update_bayesian_priors(self, strategy: MutationStrategy, success: bool):
        """Update Bayesian Beta distribution parameters"""
        if success:
            self.strategy_alpha[strategy] += 1.0
        else:
            self.strategy_beta[strategy] += 1.0

    def select_strategy(
        self,
        method: str = 'epsilon_greedy',
        temperature: float = 1.0
    ) -> MutationStrategy:
        """
        Select next mutation strategy using learned policy

        Args:
            method: Selection method ('epsilon_greedy', 'ucb', 'thompson', 'softmax')
            temperature: Temperature for softmax selection

        Returns:
            Selected mutation strategy
        """
        if method == 'epsilon_greedy':
            return self._select_epsilon_greedy()
        elif method == 'ucb':
            return self._select_ucb()
        elif method == 'thompson':
            return self._select_thompson_sampling()
        elif method == 'softmax':
            return self._select_softmax(temperature)
        else:
            raise ValueError(f"Unknown selection method: {method}")

    def _select_epsilon_greedy(self) -> MutationStrategy:
        """Epsilon-greedy strategy selection"""
        if random.random() < self.epsilon:
            # Explore: random strategy
            return random.choice(list(MutationStrategy))
        else:
            # Exploit: best Q-value strategy
            return max(self.q_values.items(), key=lambda x: x[1])[0]

    def _select_ucb(self) -> MutationStrategy:
        """Upper Confidence Bound (UCB1) strategy selection"""
        total_tries = sum(stats.total_tries for stats in self.strategy_stats.values())

        if total_tries == 0:
            return random.choice(list(MutationStrategy))

        ucb_values = {}
        for strategy, stats in self.strategy_stats.items():
            if stats.total_tries == 0:
                # Unvisited strategies have infinite UCB
                return strategy

            # UCB1: mean + sqrt(2 * ln(total) / tries)
            mean_reward = stats.success_rate
            exploration_bonus = math.sqrt(2 * math.log(total_tries) / stats.total_tries)
            ucb_values[strategy] = mean_reward + exploration_bonus

        return max(ucb_values.items(), key=lambda x: x[1])[0]

    def _select_thompson_sampling(self) -> MutationStrategy:
        """Thompson Sampling (Bayesian) strategy selection"""
        samples = {}
        for strategy in MutationStrategy:
            # Sample from Beta distribution
            alpha = self.strategy_alpha[strategy]
            beta = self.strategy_beta[strategy]
            samples[strategy] = random.betavariate(alpha, beta)

        return max(samples.items(), key=lambda x: x[1])[0]

    def _select_softmax(self, temperature: float = 1.0) -> MutationStrategy:
        """Softmax (Boltzmann) strategy selection"""
        # Calculate softmax probabilities
        q_values_list = list(self.q_values.values())
        strategies = list(self.q_values.keys())

        # Apply temperature scaling
        scaled_q = [q / temperature for q in q_values_list]

        # Softmax
        max_q = max(scaled_q)
        exp_q = [math.exp(q - max_q) for q in scaled_q]
        sum_exp = sum(exp_q)
        probabilities = [e / sum_exp for e in exp_q]

        # Sample from distribution
        return random.choices(strategies, weights=probabilities)[0]

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning engine statistics"""
        stats = {
            'total_feedback': self.total_feedback_count,
            'total_new_coverage': self.total_new_coverage,
            'total_crashes': self.total_crashes,
            'current_epsilon': self.epsilon,
            'strategy_stats': {},
            'q_values': {},
        }

        for strategy, strategy_stats in self.strategy_stats.items():
            stats['strategy_stats'][strategy.value] = {
                'total_tries': strategy_stats.total_tries,
                'new_coverage_count': strategy_stats.new_coverage_count,
                'crash_count': strategy_stats.crash_count,
                'success_rate': strategy_stats.success_rate,
                'avg_execution_time': strategy_stats.avg_execution_time,
                'consecutive_failures': strategy_stats.consecutive_failures,
            }
            stats['q_values'][strategy.value] = self.q_values[strategy]

        return stats

    def save_model(self, filepath: str | Path):
        """Save learning model to file"""
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)

        model_data = {
            'learning_rate': self.learning_rate,
            'discount_factor': self.discount_factor,
            'epsilon': self.epsilon,
            'strategy_stats': {
                strategy.value: {
                    'total_tries': stats.total_tries,
                    'new_coverage_count': stats.new_coverage_count,
                    'crash_count': stats.crash_count,
                    'avg_execution_time': stats.avg_execution_time,
                    'success_rate': stats.success_rate,
                    'last_success_time': stats.last_success_time,
                    'consecutive_failures': stats.consecutive_failures,
                }
                for strategy, stats in self.strategy_stats.items()
            },
            'q_values': {strategy.value: q for strategy, q in self.q_values.items()},
            'strategy_alpha': {strategy.value: alpha for strategy, alpha in self.strategy_alpha.items()},
            'strategy_beta': {strategy.value: beta for strategy, beta in self.strategy_beta.items()},
            'total_feedback_count': self.total_feedback_count,
            'total_new_coverage': self.total_new_coverage,
            'total_crashes': self.total_crashes,
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        self.logger.info(f"Model saved to {filepath}")

    @classmethod
    def load_model(cls, filepath: str | Path) -> 'LearningEngine':
        """Load learning model from file"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        engine = cls(
            learning_rate=model_data['learning_rate'],
            discount_factor=model_data['discount_factor'],
            epsilon=model_data['epsilon']
        )

        # Restore statistics
        for strategy_name, stats_dict in model_data['strategy_stats'].items():
            strategy = MutationStrategy(strategy_name)
            stats = StrategyStats(**stats_dict)
            engine.strategy_stats[strategy] = stats

        # Restore Q-values
        engine.q_values = {
            MutationStrategy(name): q for name, q in model_data['q_values'].items()
        }

        # Restore Bayesian priors
        engine.strategy_alpha = {
            MutationStrategy(name): alpha for name, alpha in model_data['strategy_alpha'].items()
        }
        engine.strategy_beta = {
            MutationStrategy(name): beta for name, beta in model_data['strategy_beta'].items()
        }

        # Restore counters
        engine.total_feedback_count = model_data['total_feedback_count']
        engine.total_new_coverage = model_data['total_new_coverage']
        engine.total_crashes = model_data['total_crashes']

        logging.getLogger(__name__).info(f"Model loaded from {filepath}")
        return engine

    def _format_update_result(self, feedback: FeedbackData, reward: float) -> str:
        """Format update result message"""
        stats = self.strategy_stats[feedback.strategy_used]

        result = (
            f"model-updated: strategy={feedback.strategy_used.value}, "
            f"feedback={feedback.feedback_type.value}, "
            f"reward={reward:.2f}, "
            f"q_value={self.q_values[feedback.strategy_used]:.2f}, "
            f"success_rate={stats.success_rate:.2%}, "
            f"epsilon={self.epsilon:.3f}"
        )

        return result


# ============================================================================
# Testing and Demonstration
# ============================================================================

def _self_test() -> bool:
    """Self-test for learning engine"""
    try:
        print("="*70)
        print("LEARNING ENGINE SELF-TEST")
        print("="*70)

        # Initialize engine
        engine = LearningEngine(learning_rate=0.1, epsilon=0.3)
        print(f"\n[1] Engine initialized with epsilon={engine.epsilon}")

        # Simulate feedback updates
        print("\n[2] Simulating fuzzing feedback...")

        test_feedbacks = [
            FeedbackData(
                FeedbackType.NEW_COVERAGE,
                MutationStrategy.BIT_FLIP,
                0.5,
                new_edges_covered=15
            ),
            FeedbackData(
                FeedbackType.NO_CHANGE,
                MutationStrategy.BYTE_FLIP,
                0.3
            ),
            FeedbackData(
                FeedbackType.CRASH_FOUND,
                MutationStrategy.HAVOC,
                0.8,
                crash_severity="high"
            ),
            FeedbackData(
                FeedbackType.NEW_COVERAGE,
                MutationStrategy.PROTOCOL_AWARE,
                0.6,
                new_edges_covered=8
            ),
        ]

        for i, feedback in enumerate(test_feedbacks):
            result = engine.update(feedback)
            print(f"  Update {i+1}: {result[:80]}...")

        # Test strategy selection
        print("\n[3] Testing strategy selection methods...")
        for method in ['epsilon_greedy', 'ucb', 'thompson', 'softmax']:
            strategy = engine.select_strategy(method=method)
            print(f"  {method:20s} -> {strategy.value}")

        # Test statistics
        print("\n[4] Testing statistics retrieval...")
        stats = engine.get_statistics()
        print(f"  Total feedback: {stats['total_feedback']}")
        print(f"  Total new coverage: {stats['total_new_coverage']}")
        print(f"  Total crashes: {stats['total_crashes']}")
        print(f"  Current epsilon: {stats['current_epsilon']:.3f}")

        # Test top strategies
        print("\n[5] Top 3 strategies by Q-value:")
        top_strategies = sorted(
            engine.q_values.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]
        for strategy, q_value in top_strategies:
            stats = engine.strategy_stats[strategy]
            print(f"  {strategy.value:20s} Q={q_value:6.2f} success_rate={stats.success_rate:.2%}")

        # Test model persistence
        print("\n[6] Testing model save/load...")
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as tmp:
            engine.save_model(tmp.name)
            loaded_engine = LearningEngine.load_model(tmp.name)
            print(f"  Saved and loaded model: epsilon={loaded_engine.epsilon:.3f}")

        print("\n" + "="*70)
        print("SELF-TEST PASSED ✅")
        print("="*70)
        return True

    except Exception as e:
        print(f"\nSELF-TEST FAILED ❌: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _self_test()
