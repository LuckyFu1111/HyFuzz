from src.utils.helpers import flatten_dict


def test_flatten_dict():
    data = {"a": {"b": 1}}
    assert flatten_dict(data) == {"a.b": 1}
