from src.judge.judge import Judge


def test_judge_evaluation_contains_feedback():
    judge = Judge()
    result = judge.evaluate({"payload_id": "1", "status": "ok", "trace": "main", "coverage": "block"})
    assert "feedback" in result
    assert result["score"] == "1.0"
