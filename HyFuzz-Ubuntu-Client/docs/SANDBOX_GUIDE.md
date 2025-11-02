# Sandbox Guide

The sandbox subsystem isolates target execution to protect the host while providing reproducible
conditions for fuzzing.

## Architecture

- **Sandbox profiles** – Defined in `config/sandbox_config.yaml` (namespace, cgroup, seccomp settings).
- **Sandbox manager** – `src/execution/sandbox_manager.py` orchestrates lifecycle (prepare, run, teardown).
- **Resource monitor** – `src/execution/resource_monitor.py` tracks usage and enforces limits.
- **Signal handler** – `src/execution/signal_handler.py` forwards crash signals to instrumentation.

## Sandbox Profiles

Example YAML snippet:

```yaml
profiles:
  default:
    namespaces: [ipc, mount, pid, net]
    cgroups:
      cpu_shares: 1024
      memory_limit: 2g
    seccomp: profiles/seccomp-default.json
    mounts:
      - type: bind
        source: /opt/hyfuzz-client/sandbox/rootfs
        target: /
        options: [ro, nosuid]
    env:
      LD_PRELOAD: "/opt/instrumentation/libasan.so"
  high_isolation:
    namespaces: [ipc, mount, pid, net, uts]
    cgroups:
      cpu_shares: 512
      memory_limit: 1g
    qemu:
      enabled: true
      image: images/ubuntu-minimal.qcow2
```

Select a profile in `config/execution_config.yaml` under `sandbox.profile` or override per campaign via CLI
(`--sandbox-profile high_isolation`).

## Temporary Filesystem

- Sandbox runs inside `data/sandbox/` by default.
- Clean up residual data using `scripts/maintenance/cleanup_old_results.sh`.
- Use overlay filesystems for reproducible rootfs snapshots.

## Kernel Requirements

- User namespaces (`CONFIG_USER_NS`) and cgroups v2.
- `ptrace` permissions for instrumentation.
- Optional: KVM support when using QEMU-based sandboxes.

## Tips

- Preload dependencies inside the sandbox rootfs to minimise startup time.
- Use dedicated network namespaces to isolate target traffic.
- When fuzzing ICS/OT devices, throttle network interfaces using `tc` rules defined in sandbox scripts.

## Validation

Run sandbox tests before campaigns:

```bash
pytest client_tests/unit/test_sandbox.py
python scripts/configure_sandbox.sh --validate
```

For interactions with instrumentation, read [`INSTRUMENTATION.md`](INSTRUMENTATION.md). For deployment
considerations, see [`DEPLOYMENT.md`](DEPLOYMENT.md).
