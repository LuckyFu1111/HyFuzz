from src.judge.judge import Judge
from src.judge.learning_engine import LearningEngine


def test_feedback_loop_updates_learning_engine():
    judge = Judge()
    result = judge.evaluate({"payload_id": "1", "status": "ok", "trace": "main", "coverage": "block"})
    engine = LearningEngine()
    update = engine.update(result["feedback"])
    assert "model-updated" in update
