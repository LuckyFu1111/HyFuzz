# Fuzzing Strategy Guide

The HyFuzz client combines deterministic mutations, grammar-driven generation, and LLM-assisted payload
crafting received from the server. Use this guide to tune fuzzing behaviour per campaign.

## Mutation Pipelines

1. **Seed ingestion** – Seeds are pulled from `data/payloads/` and synchronised with the server.
2. **Grammar fuzzing** – `src/fuzzing/grammar_fuzzer.py` expands protocol grammars to create structured
   payloads.
3. **Mutation engine** – `src/fuzzing/mutation_engine.py` applies bit flips, arithmetic mutations, block
   insertions, and dictionary substitutions.
4. **LLM augmentation** – The server provides high-value payloads via MCP; the client treats them as
   priority seeds.

Configure mutation intensity via `config/execution_config.yaml` (`mutator_profiles`) and
`config/protocol_config.yaml` (per-protocol dictionaries and grammars).

## Corpus Management

- `src/fuzzing/corpus_manager.py` maintains unique payloads and rotates stale entries.
- Use `scripts/fuzzing/sync_corpus.py` (optional) to share corpora between clients.
- Store high-impact payloads in `data/payloads/corpus/` and reference them in configuration files.

## Dictionaries

- Protocol-specific dictionaries are located under `data/payloads/` (e.g., `mqtt_payloads.json`).
- Extend dictionaries and update `config/protocol_config.yaml` to load them automatically.
- Custom dictionaries can be generated from traffic captures using
  `notebooks/03_fuzzing_analysis.ipynb`.

## Campaign Profiles

| Profile | Location | Characteristics |
|---------|----------|-----------------|
| Development | `config/example_configs/config_dev.yaml` | Balanced coverage vs. stability |
| Aggressive | `config/example_configs/config_aggressive.yaml` | High mutation rate, short timeouts |
| Safe | `config/example_configs/config_safe.yaml` | Conservative mutations, verbose logging |
| Protocol-specific | `config/example_configs/config_{protocol}.yaml` | Tailored timeouts and mutators |
| Distributed | `config/example_configs/config_distributed.yaml` | Optimised for multi-worker pools |

## Adaptive Feedback

- The client forwards local metrics (coverage deltas, crash density) to the server.
- Server-side LLM judge returns adjustments (e.g., focus on certain message types) that the client
  applies through `src/judge/adaptive_tuner.py`.
- Review applied hints in `logs/judge.log` and `logs/execution.log`.

## Performance Considerations

- Increase worker count cautiously; instrumentation overhead can grow non-linearly.
- Disable expensive mutators when latency is critical by editing `config/execution_config.yaml` and
  toggling specific entries under `mutators`.
- For CPU-bound workloads, pin workers to cores using `taskset` or cgroup configs in the sandbox layer.

## Best Practices

- Keep corpora fresh: remove payloads that no longer trigger unique behaviour.
- Use performance tests in `tests/performance/` to validate throughput after configuration changes.
- Version payload dictionaries and corpora to reproduce historic results.
- Periodically snapshot the SQLite database to maintain a history of successful payloads and outcomes.
