from src.protocols.fuzz_engine import mutate


def test_mutation_engine_fast():
    seeds = mutate(b"seed")
    assert len(seeds) == 3
