# Distillation Experiment Configs & Ablations

## Distillation-Specific Knobs

Unlike GEPA/DSPy which optimize *what the agent says* (prompts, few-shot), distillation has its own configuration surface that controls *how the teacher diagnoses and plans*. These are the independent variables we should systematically vary.

### Axis 1: Teacher Model (who does the diagnosis)

| Config ID | Teacher Model | Provider | Cost/session | Hypothesis |
|-----------|--------------|----------|-------------|------------|
| `T-opus` | `claude-opus-4-6` | Anthropic | ~$2-5 | Best diagnosis quality, most expensive |
| `T-gpt54` | `gpt-5.4-2026-03-05` | OpenAI | ~$1-3 | Cross-provider: does GPT-5.4 diagnose differently? |
| `T-gemini` | `gemini-3.1-pro-preview` | Google | ~$0.50-2 | Third provider: different diagnostic style? |
| `T-qwen397b` | `Qwen/Qwen3.5-397B-A17B-FP8` | Local (vLLM, 8×H100) | $0 (GPU only) | Can a strong local MoE model be its own teacher? |

**Key question:** How much does teacher quality matter? Do different providers diagnose different failure modes? Can a 397B-A17B local MoE model meaningfully diagnose a 9B dense model's failures?

### Data Access Configs (same as GEPA/DSPy for fair comparison)

Each experiment is run under all 3 data configs:

| Config | Traces available | Benchmark answers | External data | Purpose |
|--------|-----------------|-------------------|---------------|---------|
| **C1** | External only (GeneralThought-430K + ADP) | Hidden | Yes | Tests whether diagnosis transfers from external tasks |
| **C2** | Benchmark traces (queries visible, answers hidden) | Hidden | No | Tests diagnosis on actual task distribution |
| **C3** | Both benchmark + external traces | Hidden | Yes | Best of both — most data for the teacher to analyze |

### Axis 2: Diagnosis Budget (how thoroughly the teacher investigates)

| Config ID | max_tool_calls | max_cost_usd | Hypothesis |
|-----------|---------------|-------------|------------|
| `B-minimal` | 5 | $0.50 | Quick scan — catches obvious issues only |
| `B-standard` | 15 | $2.00 | Default — reasonable depth |
| `B-thorough` | 30 | $5.00 | Deep investigation — finds subtle patterns |
| `B-exhaustive` | 50 | $10.00 | Diminishing returns? Or finds rare failure modes? |

**Key question:** What's the optimal cost/improvement tradeoff? Does spending 10x more on diagnosis yield proportionally better edits?

### Axis 3: Student Model Being Improved (who gets improved)

| Config ID | Student Model | Baseline | Hypothesis |
|-----------|--------------|----------|------------|
| `S-2b` | `qwen3.5:2b` | Weak | Most room for improvement — harness matters most |
| `S-9b` | `qwen3.5:9b` | Medium | Sweet spot — strong enough to benefit from good prompts |
| `S-27b` | `qwen3.5:27b` | Strong | Diminishing returns? Already good enough? |

**Key question:** Does distillation help small models more than large ones? (Hypothesis: yes, because small models are more sensitive to prompt quality and routing.)

### Axis 4: Autonomy Mode (how aggressively edits are applied)

| Config ID | Mode | Behavior | Hypothesis |
|-----------|------|----------|------------|
| `A-auto` | `auto` | Apply everything that passes the gate | Maximum throughput, risk of compounding errors |
| `A-tiered` | `tiered` | Auto for safe ops, review for prompts | Conservative — only high-confidence edits land |
| `A-manual` | `manual` | Everything goes to review (dry-run) | Measures what the teacher *would* do, no actual changes |

**Key question:** Does auto-applying everything help or hurt? Do rejected-by-gate edits indicate teacher mistakes or overly strict gating?

### Axis 5: Gate Strictness (how picky the benchmark gate is)

| Config ID | min_improvement | max_regression | Hypothesis |
|-----------|----------------|---------------|------------|
| `G-permissive` | 0.0 | 0.10 | Accept any improvement, tolerate 10% cluster regression |
| `G-standard` | 0.0 | 0.05 | Default — any improvement, 5% max regression |
| `G-strict` | 0.02 | 0.02 | Require 2% improvement, max 2% regression |
| `G-none` | -1.0 | 1.0 | No gate — apply everything (measures raw teacher quality) |

**Key question:** Does gating help or just reject useful edits? What's the optimal strictness?

### Axis 6: Iterative Sessions (does repeated distillation compound?)

| Config ID | Sessions | Hypothesis |
|-----------|---------|------------|
| `I-single` | 1 session | Baseline — one-shot improvement |
| `I-three` | 3 sequential sessions | Each session finds new failure modes |
| `I-five` | 5 sequential sessions | Plateau detection — when does improvement stop? |

**Key question:** Does the teacher find genuinely new failure modes in session 2+, or does it repeat itself? This uses `parent_session_id` chaining.

### Axis 7: Benchmark Type (what the gate scores against)

| Config ID | Benchmark | Hypothesis |
|-----------|----------|------------|
| `BM-personal` | Personal benchmark (from traces) | Most relevant to user's actual tasks |
| `BM-pinchbench` | PinchBench (23 tasks) | Standard agentic benchmark |
| `BM-toolcall` | ToolCall-15 (15 tasks) | Tool-use focused |
| `BM-taubench` | TauBench (20 tasks) | Customer service focused |

**Key question:** Does optimizing against a personal benchmark generalize to standard benchmarks? Or should we gate against standard benchmarks directly?

---

## Recommended Experiment Grid

### Phase 1: Core Ablations (most informative, run first)

These answer the fundamental questions about distillation's value.

**Experiment 1a: Teacher Model Ablation**
- Fix: `S-9b`, `B-standard`, `A-auto`, `G-standard`, `I-single`
- Vary: `T-opus`, `T-gpt54`, `T-gemini`, `T-qwen397b` × `C1`, `C2`, `C3`
- Eval on: PinchBench, ToolCall-15, TauBench
- **Runs: 4 teachers × 3 benchmarks × 3 data configs = 36 sessions**
- **Cost: ~$120 total teacher API**

**Experiment 1b: Budget Ablation**
- Fix: `S-9b`, `T-opus`, `A-auto`, `G-standard`, `I-single`
- Vary: `B-minimal`, `B-standard`, `B-thorough`, `B-exhaustive` × `C1`, `C2`, `C3`
- Eval on: PinchBench, ToolCall-15, TauBench
- **Runs: 4 budgets × 3 benchmarks × 3 data configs = 36 sessions**
- **Cost: ~$180 total teacher API**

**Experiment 1c: Student Model Scaling**
- Fix: `T-opus`, `B-standard`, `A-auto`, `G-standard`, `I-single`
- Vary: `S-2b`, `S-9b`, `S-27b` × `C1`, `C2`, `C3`
- Eval on: PinchBench, ToolCall-15, TauBench
- **Runs: 3 students × 3 benchmarks × 3 data configs = 27 sessions**
- **Cost: ~$60 total teacher API**

### Phase 2: Gate & Autonomy (second priority)

**Experiment 2a: Gate Strictness**
- Fix: `S-9b`, `T-sonnet`, `B-standard`, `A-auto`, `I-single`
- Vary: `G-permissive`, `G-standard`, `G-strict`, `G-none`
- Eval on: PinchBench (most data)
- **Runs: 4 gate configs × 1 benchmark = 4 sessions**

**Experiment 2b: Autonomy Mode**
- Fix: `S-9b`, `T-sonnet`, `B-standard`, `G-standard`, `I-single`
- Vary: `A-auto`, `A-tiered`, `A-manual`
- Eval on: PinchBench
- **Runs: 3 modes × 1 benchmark = 3 sessions**

### Phase 3: Iterative & Cross-Benchmark (third priority)

**Experiment 3a: Iterative Sessions**
- Fix: `S-9b`, `T-sonnet`, `B-standard`, `A-auto`, `G-standard`
- Vary: `I-single`, `I-three`, `I-five`
- Eval on: PinchBench
- **Runs: 1 + 3 + 5 = 9 sessions (chained)**

**Experiment 3b: Cross-Benchmark Transfer**
- Run distillation using traces from one benchmark, eval on a different benchmark
- Fix: `S-9b`, `T-sonnet`, `B-standard`, `A-auto`, `G-standard`
- Pairs: optimize-on-PB→eval-on-TC15, optimize-on-TC15→eval-on-PB, etc.
- **Runs: 6 cross-pairs**

---

## Total Experiment Budget

| Phase | Sessions | Est. Teacher Cost | Est. GPU Hours | Wall Time |
|-------|---------|-------------------|---------------|-----------|
| 1a: Teacher ablation | 36 | $120 | 18h eval | 2 days |
| 1b: Budget ablation | 36 | $180 | 18h eval | 2 days |
| 1c: Student scaling | 27 | $60 | 14h eval | 1.5 days |
| 2a: Gate strictness | 12 | $24 | 6h eval | 0.5 day |
| 2b: Autonomy mode | 9 | $18 | 5h eval | 0.5 day |
| 3a: Iterative sessions | 9 | $20 | 5h eval | 1 day |
| 3b: Cross-benchmark | 6 | $12 | 3h eval | 0.5 day |
| **Total** | **135** | **~$434** | **~69h** | **~8 days** |

With parallelism (2-4 GPUs serving students, concurrent teacher API calls), wall time compresses to ~3-4 days.

---

## Metrics to Capture Per Session

For each distillation session, record:

### Diagnosis Quality
- Number of failure clusters identified
- Number of clusters with evidence (student_failure_rate > 0 AND teacher_success_rate > 0)
- Number of clusters dropped by planner (insufficient evidence)
- Number of tool calls made during diagnosis
- Diagnosis length (chars) — proxy for analysis depth
- Wall-clock time for diagnosis phase

### Plan Quality
- Number of edits proposed
- Edit type distribution (routing, prompt, tool desc, few-shot, params)
- Number of edits targeting each cluster

### Execution Quality
- Number of edits applied vs rejected vs pending vs skipped
- Per-edit benchmark delta (which edits actually helped?)
- Rejection reasons distribution (regression, no improvement, validation failure)

### Overall
- Total teacher API cost ($)
- Total wall-clock time
- Benchmark score before vs after
- Per-cluster score before vs after
- Net accuracy improvement (Δ)

### For Iterative Sessions (Experiment 3a)
- Per-session Δ accuracy (does each session add value?)
- Cumulative Δ accuracy
- Unique vs repeated failure clusters across sessions
- Edit overlap across sessions (does the teacher repeat itself?)

---

## Eval Config Files to Create

Each experiment needs a TOML config that pins all the distillation params.

### Template: `src/openjarvis/evals/configs/distillation/`

```toml
# distillation-{experiment}-{teacher}-{budget}-{student}.toml

[learning.distillation]
enabled = true
autonomy_mode = "auto"           # Vary per experiment
teacher_model = "claude-sonnet-4-6"  # Vary per experiment
max_cost_per_session_usd = 2.0   # Vary per experiment
max_tool_calls_per_diagnosis = 15 # Vary per experiment

[learning.distillation.gate]
min_improvement = 0.0            # Vary per experiment
max_regression = 0.05            # Vary per experiment
benchmark_subsample_size = 50

[learning.distillation.benchmark]
synthesis_feedback_threshold = 0.7
max_benchmark_size = 200

# Student model (not in the distillation section — this is the global config)
[intelligence]
default_model = "qwen3.5:9b"    # Vary per experiment

[engine]
default = "ollama"
```

### Configs to Generate

```
src/openjarvis/evals/configs/distillation/
├── exp1a-teacher/
│   ├── opus-9b-pb.toml
│   ├── sonnet-9b-pb.toml
│   ├── gpt4o-9b-pb.toml
│   ├── local27b-9b-pb.toml
│   ├── opus-9b-tc15.toml
│   ├── sonnet-9b-tc15.toml
│   └── ... (12 total)
├── exp1b-budget/
│   ├── minimal-9b-pb.toml
│   ├── standard-9b-pb.toml
│   ├── thorough-9b-pb.toml
│   ├── exhaustive-9b-pb.toml
│   └── ... (12 total)
├── exp1c-student/
│   ├── sonnet-2b-pb.toml
│   ├── sonnet-9b-pb.toml
│   ├── sonnet-27b-pb.toml
│   └── ... (9 total)
├── exp2a-gate/
│   ├── permissive-9b-pb.toml
│   ├── standard-9b-pb.toml
│   ├── strict-9b-pb.toml
│   └── none-9b-pb.toml
├── exp2b-autonomy/
│   ├── auto-9b-pb.toml
│   ├── tiered-9b-pb.toml
│   └── manual-9b-pb.toml
└── exp3a-iterative/
    └── sonnet-9b-pb-iterative.toml
```

---

## Runner Script

```bash
#!/bin/bash
# scripts/experiments/run_distillation_experiments.sh
#
# Runs all distillation ablation experiments.
# Prerequisites:
#   - Ollama running with qwen3.5:{2b,9b,27b}
#   - ANTHROPIC_API_KEY set
#   - OPENAI_API_KEY set (for gpt-4o teacher)
#   - Traces seeded with feedback (A1 blocker resolved)
#   - jarvis learning init already run

set -euo pipefail

RESULTS_DIR="results/neurips-2026/agent-optimization/distillation"
CONFIGS_DIR="src/openjarvis/evals/configs/distillation"

run_session() {
    local experiment=$1
    local config_file=$2
    local output_dir="${RESULTS_DIR}/${experiment}/$(basename ${config_file%.toml})"

    echo "=== ${experiment}: $(basename ${config_file}) ==="
    mkdir -p "${output_dir}"

    # 1. Capture baseline eval
    uv run python -m openjarvis.evals run \
        -c "${config_file}" \
        --output "${output_dir}/baseline/" \
        2>&1 | tee "${output_dir}/baseline.log"

    # 2. Run distillation session
    uv run jarvis learning run \
        --config "${config_file}" \
        --autonomy auto \
        2>&1 | tee "${output_dir}/distillation.log"

    # 3. Capture post-distillation eval
    uv run python -m openjarvis.evals run \
        -c "${config_file}" \
        --output "${output_dir}/after/" \
        2>&1 | tee "${output_dir}/after.log"

    # 4. Copy session artifacts
    latest_session=$(ls -t ~/.openjarvis/learning/sessions/ | head -1)
    cp -r ~/.openjarvis/learning/sessions/${latest_session} \
        "${output_dir}/session/"

    echo "=== Done: ${experiment}/$(basename ${config_file}) ==="
}

# Phase 1a: Teacher Model Ablation
for config in ${CONFIGS_DIR}/exp1a-teacher/*.toml; do
    run_session "exp1a-teacher" "${config}"
done

# Phase 1b: Budget Ablation
for config in ${CONFIGS_DIR}/exp1b-budget/*.toml; do
    run_session "exp1b-budget" "${config}"
done

# Phase 1c: Student Scaling
for config in ${CONFIGS_DIR}/exp1c-student/*.toml; do
    run_session "exp1c-student" "${config}"
done

# Phase 2a: Gate Strictness
for config in ${CONFIGS_DIR}/exp2a-gate/*.toml; do
    run_session "exp2a-gate" "${config}"
done

# Phase 2b: Autonomy Mode
for config in ${CONFIGS_DIR}/exp2b-autonomy/*.toml; do
    run_session "exp2b-autonomy" "${config}"
done

echo "=== All experiments complete ==="
```

---

## Key Paper Figures (Distillation-Only)

1. **Teacher model comparison** — bar chart: accuracy improvement per teacher model across 3 benchmarks
2. **Cost-efficiency curve** — scatter: Δ accuracy vs teacher API cost (budget ablation)
3. **Student scaling curve** — line chart: Δ accuracy vs student model size (does distillation help small models more?)
4. **Gate strictness tradeoff** — bar chart: edits applied vs accuracy gain per gate config
5. **Iterative learning curve** — line chart: cumulative accuracy over 5 sequential sessions
6. **Edit type attribution heatmap** — which edit types (routing, prompt, tool desc) drive the most improvement per benchmark
7. **Cross-benchmark transfer matrix** — heatmap: optimize-on-X, eval-on-Y
