# Engine Module

The engine module implements the inference runtime pillar. All backends
implement the `InferenceEngine` ABC with `generate()`, `stream()`,
`list_models()`, and `health()` methods. The discovery subsystem probes
running engines and selects the best available backend based on
configuration and health checks.

## Abstract Base Class

### InferenceEngine

::: openjarvis.engine._stubs.InferenceEngine
    options:
      show_source: true
      members_order: source

### EngineConnectionError

::: openjarvis.engine._base.EngineConnectionError
    options:
      show_source: true

### messages_to_dicts

::: openjarvis.engine._base.messages_to_dicts
    options:
      show_source: true

---

## Engine Implementations

### OllamaEngine

::: openjarvis.engine.ollama.OllamaEngine
    options:
      show_source: true
      members_order: source

### OpenAI-Compatible Engines (vLLM, SGLang, llama.cpp, MLX, LM Studio)

These engines are thin subclasses of `_OpenAICompatibleEngine`, created
via data-driven registration in `openai_compat_engines.py`. They share
the same implementation and differ only in `engine_id` and default host.

| Engine | Registry Key | Default Host |
|--------|-------------|--------------|
| `VLLMEngine` | `vllm` | `http://localhost:8000` |
| `SGLangEngine` | `sglang` | `http://localhost:30000` |
| `LlamaCppEngine` | `llamacpp` | `http://localhost:8080` |
| `MLXEngine` | `mlx` | `http://localhost:8080` |
| `LMStudioEngine` | `lmstudio` | `http://localhost:1234` |

::: openjarvis.engine._openai_compat._OpenAICompatibleEngine
    options:
      show_source: true
      members_order: source

### CloudEngine

::: openjarvis.engine.cloud.CloudEngine
    options:
      show_source: true
      members_order: source

### estimate_cost

::: openjarvis.engine.cloud.estimate_cost
    options:
      show_source: true

---

## Engine Discovery

Functions for probing running engines, aggregating available models,
and selecting the best engine for a given configuration.

### get_engine

::: openjarvis.engine._discovery.get_engine
    options:
      show_source: true

### discover_engines

::: openjarvis.engine._discovery.discover_engines
    options:
      show_source: true

### discover_models

::: openjarvis.engine._discovery.discover_models
    options:
      show_source: true
