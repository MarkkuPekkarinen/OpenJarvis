# Distillation Experiment Execution Plan — Parallelized

## Dependency Graph

```
                    ┌─ Track A: Fix Blockers ──────────────────────────────┐
                    │  A1: Seed feedback on traces              (1 hour)   │
                    │  A2: Fix cluster JSON prompt engineering   (2 hours)  │
                    │  A3: Wire BenchmarkGate into orchestrator  (3 hours)  │
                    └──────────────────────┬───────────────────────────────┘
                                           │
                    ┌─ Track B: GEPA/DSPy ─┤─── runs in parallel with A ───┐
                    │  B1: GEPA × 3 models │                    (2-4 days)  │
                    │  B2: DSPy × 3 models │                    (1-2 days)  │
                    └──────────┬───────────┘                                │
                               │                                            │
                    ┌─ Track C: Distillation Experiments ───── after A ─────┐
                    │  C1: Experiment 1 (standalone)             (1 day)    │
                    │  C2: Experiment 5 (edit attribution)       (analysis) │
                    └──────────┬───────────────────────────────────────────┘
                               │
                    ┌─ Track D: LoRA/SFT ──── runs in parallel with A,B,C ─┐
                    │  D1: LoRA training (Qwen 2B, 9B, 27B)    (3-5 days)  │
                    │  D2: SFT training (Qwen 2B, 9B)          (3-5 days)  │
                    └──────────┬───────────────────────────────────────────┘
                               │
                    ┌─ Track E: Combinations + Analysis ─── after B,C,D ───┐
                    │  E1: Experiment 2 (head-to-head)          (1 day)    │
                    │  E2: Experiment 3 (stacking)              (2 days)   │
                    │  E3: Experiment 4 (cost frontier)          (analysis) │
                    │  E4: Paper figures + tables                (1 day)   │
                    └──────────────────────────────────────────────────────┘
```

**Critical path:** A → C → E (fix blockers → run distillation → compare)
**Parallelizable:** B and D run entirely in parallel with A and C.

---

## Track A: Fix Distillation Blockers

These must complete before any distillation experiment can run. All three are independent of each other.

### A1: Seed Feedback on Traces (1 hour, no GPU needed)

**Problem:** 373 traces exist but 0 have feedback scores. The personal benchmark needs 10+ high-feedback traces.

**Solution:** Use baseline eval scores as feedback proxies. For each trace that was part of a benchmark eval, set feedback = eval score.

```bash
uv run python << 'PYEOF'
from openjarvis.traces.store import TraceStore
from pathlib import Path

store = TraceStore(Path.home() / ".openjarvis" / "traces.db")
traces = store.list_traces(limit=500)

seeded = 0
for t in traces:
    if t.feedback is not None:
        continue
    # Heuristic: if the trace has a result and completed, give it decent feedback
    # Traces with outcome=success get 0.8, others get 0.3
    if t.outcome == "success":
        score = 0.8
    elif t.outcome == "failure":
        score = 0.2
    else:
        # No explicit outcome — use a moderate score based on whether there's a result
        score = 0.6 if t.result and len(t.result) > 50 else 0.3
    store.update_feedback(t.trace_id, score)
    seeded += 1

print(f"Seeded feedback on {seeded} traces")

# Verify
high = [t for t in store.list_traces(limit=500) if t.feedback and t.feedback >= 0.7]
print(f"High-feedback traces (>=0.7): {len(high)}")
PYEOF
```

**Verification:** `check_benchmark_ready()` returns `ready=True`.

**Can run on:** Any machine (laptop). No GPU, no API keys.

---

### A2: Fix Cluster JSON Prompt Engineering (2 hours, needs API key)

**Problem:** The live test showed the teacher writes a 3,437-char narrative diagnosis but outputs 0 structured JSON clusters. The system prompt asks for a JSON array in a ````json` code fence but the teacher doesn't always comply.

**Solution:** Two changes to `src/openjarvis/learning/distillation/diagnose/runner.py`:

1. **Strengthen the system prompt** — add explicit formatting instructions with an example.
2. **Add a follow-up extraction call** — if `_parse_clusters()` returns empty, make one more teacher call: "You wrote a diagnosis but forgot to include the structured JSON. Here is your diagnosis: [paste]. Now output ONLY the JSON array of failure clusters."

**Files to modify:**
- `src/openjarvis/learning/distillation/diagnose/runner.py` — update `_SYSTEM_PROMPT` and add fallback extraction
- `tests/learning/distillation/test_diagnosis_runner.py` — add test for fallback extraction path

**Verification:** Run the live test again and confirm clusters > 0.

**Can run on:** Any machine with `ANTHROPIC_API_KEY`.

---

### A3: Wire BenchmarkGate into Orchestrator (3 hours, no API key needed)

**Problem:** The orchestrator (`orchestrator.py`) runs `execute_edits()` from M4 which applies edits without gating. The `BenchmarkGate` from M5 exists but isn't wired in.

**Solution:** Update the orchestrator's execute phase to:
1. Before each edit: capture `benchmark_before` snapshot via the scorer
2. After each edit: capture `benchmark_after` snapshot
3. Use `BenchmarkGate.evaluate()` to accept/reject
4. If rejected: rollback via `CheckpointStore.discard_stage()`
5. If accepted: commit via `CheckpointStore.commit_stage()`

**Files to modify:**
- `src/openjarvis/learning/distillation/orchestrator.py` — replace the simple `execute_edits()` call with the gated loop
- `tests/learning/distillation/test_orchestrator.py` — update test mocks for the gated flow

**Verification:** Mock test where one edit improves and one regresses — verify the regression is rejected and rolled back.

**Can run on:** Any machine. Tests only.

---

## Track B: Run GEPA/DSPy Baselines (2-4 days, needs GPU node)

**Runs in parallel with Track A.** Completely independent — different codepath, different results dir.

**Prerequisite:** Models served via vLLM on GPU node. See `docs/experiments/agent-optimization-instructions.md`.

### B1: GEPA (3 models × 3 benchmarks = 9 runs)

```bash
# On GPU node with models served
for model in qwen-9b qwen-27b qwen-35b; do
    for bench in toolcall15 pinchbench taubench; do
        uv run jarvis optimize run \
            --benchmark "$bench" \
            --optimizer-model claude-sonnet-4-6 \
            --trials 20 \
            --max-samples 50 \
            --output-dir "results/neurips-2026/agent-optimization/gepa/${model}/${bench}/"
    done
done
```

**Time:** ~2-4 hours per run × 9 runs. Can parallelize across GPUs: serve 3 models on 3 GPUs, run 3 GEPA jobs concurrently → ~12 hours total.

**Cost:** ~$10/run (150 evals × $0.07/eval) × 9 = ~$90 total.

### B2: DSPy (3 models × 3 benchmarks = 9 runs)

```bash
for model in qwen-9b qwen-27b qwen-35b; do
    for bench in toolcall15 pinchbench taubench; do
        uv run python -c "
from openjarvis.learning.agents.dspy_optimizer import DSPyAgentOptimizer
from openjarvis.core.config import DSPyOptimizerConfig
from openjarvis.traces.store import TraceStore
store = TraceStore()
config = DSPyOptimizerConfig(
    optimizer='BootstrapFewShotWithRandomSearch',
    teacher_lm='claude-sonnet-4-6',
    config_dir='results/neurips-2026/agent-optimization/dspy/${model}/${bench}/',
)
result = DSPyAgentOptimizer(config).optimize(store)
print(f'${model}/${bench}: {result[\"status\"]}')
"
    done
done
```

**Time:** ~1-2 hours per run × 9. Parallelizable like GEPA.

**Cost:** ~$10/run × 9 = ~$90 total.

---

## Track C: Distillation Experiments (1-2 days, after Track A)

**Blocked on Track A completing.** Once blockers are fixed, this is straightforward.

### C1: Experiment 1 — Standalone Distillation (3 models × 3 benchmarks)

For each (model, benchmark):

```bash
# 1. Baseline eval (if not already done in Step 1)
uv run python -m openjarvis.evals run \
    -c src/openjarvis/evals/configs/neurips/${model}-${bench}.toml \
    --output results/neurips-2026/baselines/${model}/${bench}/

# 2. Run distillation session
ANTHROPIC_API_KEY="..." uv run jarvis learning run --autonomy auto

# 3. Post-optimization eval
uv run python -m openjarvis.evals run \
    -c src/openjarvis/evals/configs/neurips/${model}-${bench}.toml \
    --output results/neurips-2026/agent-optimization/distillation/${model}/${bench}/

# 4. Record artifacts
cp ~/.openjarvis/learning/sessions/latest/* \
   results/neurips-2026/agent-optimization/distillation/${model}/
```

**Time:** ~30 min per distillation session + 15 min per eval × 9 = ~7 hours. Partially parallelizable if serving multiple models.

**Cost:** ~$5/session × 9 = ~$45 total teacher API.

### C2: Experiment 5 — Edit Attribution (analysis only, after C1)

No additional runs needed. Extract from the 9 distillation sessions:

```bash
uv run python << 'PYEOF'
import json
from pathlib import Path
from collections import Counter

edit_types = Counter()
edit_deltas = {}

for session_dir in Path("results/neurips-2026/agent-optimization/distillation/").rglob("plan.json"):
    plan = json.loads(session_dir.read_text())
    for edit in plan.get("edits", []):
        op = edit["op"]
        edit_types[op] += 1

print("Edit type frequency:")
for op, count in edit_types.most_common():
    print(f"  {op}: {count}")
PYEOF
```

---

## Track D: LoRA/SFT Training (3-5 days, runs in parallel with everything)

**Completely independent.** Already planned in Phase 2b of the NeurIPS plan.

This track runs on training GPU nodes while Tracks A-C run on eval nodes.

| Run | Model | Method | GPUs | Est. Time |
|-----|-------|--------|------|-----------|
| D1 | Qwen-2B | LoRA | 1x H100 | 4-8 hours |
| D2 | Qwen-9B | LoRA | 1x H100 | 8-16 hours |
| D3 | Qwen-27B | LoRA | 2x H100 | 16-24 hours |
| D4 | Qwen-2B | SFT | 1x H100 | 8-16 hours |
| D5 | Qwen-9B | SFT | 2x H100 | 16-24 hours |

All can run concurrently on separate GPU allocations.

---

## Track E: Combination Experiments + Analysis (2-3 days, after B+C+D)

**Blocked on:** Tracks B, C, D all completing. This is the final phase.

### E1: Experiment 2 — Head-to-Head (1 day)

Already have results from B (GEPA/DSPy) and C (distillation). Compile:

```bash
uv run python << 'PYEOF'
import json
from pathlib import Path

methods = ["gepa", "dspy", "distillation"]
models = ["qwen-9b", "qwen-27b", "qwen-35b"]
benchmarks = ["toolcall15", "pinchbench", "taubench"]

print(f"{'Model':<12} {'Bench':<12} {'Baseline':>8} {'GEPA':>8} {'DSPy':>8} {'Distill':>8}")
for model in models:
    for bench in benchmarks:
        base_path = f"results/neurips-2026/baselines/{model}/{bench}/summary.json"
        base = json.load(open(base_path))["accuracy"] if Path(base_path).exists() else 0
        row = f"{model:<12} {bench:<12} {base:>7.1%}"
        for method in methods:
            opt_path = f"results/neurips-2026/agent-optimization/{method}/{model}/{bench}/summary.json"
            if Path(opt_path).exists():
                opt = json.load(open(opt_path))["accuracy"]
                row += f" {opt:>7.1%}"
            else:
                row += f" {'—':>8}"
        print(row)
PYEOF
```

### E2: Experiment 3 — Stacking (2 days, needs GPU + API)

Run combinations sequentially:

```bash
# Stacking order matters — apply distillation first, then layer on top

# Combo 1: Distillation + GEPA
# Start from distillation-optimized config (from C1)
# Run GEPA on top of it
uv run jarvis optimize run \
    --benchmark pinchbench \
    --optimizer-model claude-sonnet-4-6 \
    --trials 20 \
    --output-dir "results/neurips-2026/agent-optimization/combined/distill+gepa/qwen-9b/"

# Combo 2: Distillation + LoRA
# Use distillation-optimized config + LoRA adapter from D
# Just eval — the combination is config from C + weights from D
uv run python -m openjarvis.evals run \
    -c results/neurips-2026/agent-optimization/combined/distill+lora/qwen-9b/config.toml

# Combo 3: Full stack (Distillation + GEPA + LoRA)
# Layer all three optimizations
```

**6 combinations × 3 models × 3 benchmarks = 54 eval runs.** At ~5 min/eval = ~4.5 hours.

### E3: Experiment 4 — Cost Frontier (analysis only)

```bash
uv run python << 'PYEOF'
# Compile cost and accuracy data for Pareto plot
import json

data = []
# For each method, compute (total_cost, delta_accuracy)
# Distillation: cost = teacher_cost_usd from session.json
# GEPA: cost = trials × per_trial_cost
# DSPy: cost = candidates × per_candidate_cost
# LoRA: cost = GPU_hours × hourly_rate
# Stacked: sum of component costs

# Output: data points for matplotlib Pareto frontier
PYEOF
```

### E4: Paper Figures (1 day)

Generate all figures from compiled data:
1. Comparison table (all methods × models × benchmarks)
2. Cost-efficiency Pareto frontier
3. Stacking gain bar chart
4. Edit attribution heatmap
5. Sample efficiency curves

---

## Resource Allocation (Parallelized Timeline)

```
Day 0-1:  Track A (fix blockers)          | Track B starts (GEPA/DSPy)  | Track D starts (LoRA/SFT)
Day 1-2:  Track C (distillation exps)     | Track B continues           | Track D continues
Day 2-3:  Track C finishes                | Track B finishes            | Track D continues
Day 3-5:  Track E1+E2 (combinations)      |                             | Track D finishes
Day 5-6:  Track E3+E4 (analysis+figures)  |
```

**Total wall-clock time: ~6 days** (with parallelism)
**Total API cost: ~$225** (GEPA $90 + DSPy $90 + Distillation $45)
**Total GPU-hours:** Dominated by Track D (LoRA/SFT training), ~100-200 H100-hours

---

## Machine Allocation

| Machine | Tracks | What runs |
|---------|--------|-----------|
| **Laptop/workstation** | A1, A2, A3, C2, E3, E4 | Blocker fixes, analysis scripts, figure generation |
| **GPU eval node** (1-2x H100) | B1, B2, C1, E1, E2 | GEPA, DSPy, distillation evals, stacking evals |
| **GPU training node** (4-8x H100) | D1-D5 | LoRA and SFT training runs |

Tracks B and D can share a multi-GPU node (training on GPUs 0-3, eval serving on GPUs 4-7).

---

## Checklist (in execution order)

### Immediate (Day 0 — can start now)
- [ ] A1: Seed feedback on 373 traces
- [ ] A2: Fix cluster JSON prompt in `runner.py`
- [ ] A3: Wire BenchmarkGate into orchestrator
- [ ] B1: Start GEPA runs on GPU node (3 models × 3 benchmarks)
- [ ] B2: Start DSPy runs on GPU node (3 models × 3 benchmarks)
- [ ] D1-D5: Start LoRA/SFT training runs on training node

### After Track A (Day 1-2)
- [ ] C1: Run distillation standalone (3 models × 3 benchmarks)
- [ ] C2: Extract edit attribution data from C1 sessions

### After B+C complete (Day 3-4)
- [ ] E1: Compile head-to-head comparison table
- [ ] E2: Run stacking combinations (Distill+GEPA, Distill+LoRA, full stack)

### After everything (Day 5-6)
- [ ] E3: Generate cost-efficiency Pareto frontier
- [ ] E4: Generate all paper figures and tables
- [ ] Write results section
