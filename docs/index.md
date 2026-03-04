---
title: OpenJarvis
description: Programming abstractions for on-device AI
hide:
  - navigation
---

# _Programming abstractions_ for on-device AI

OpenJarvis is a modular framework for building, running, and learning from local AI systems. It provides composable abstractions across **five pillars** with a cross-cutting trace-driven learning system:

1. **Intelligence** -- The LM itself: Llama, Qwen, Claude, GPT, etc. Model catalog, generation defaults, quantization, and preferred engine configuration.
2. **Agents** -- The agentic harness for running it: system prompt (including objective, available tools, available models), context from past turns, retry logic, looping logic, exit logic. Seven agent types from simple single-turn to recursive decomposition.
3. **Tools** -- In an MCP interface, the available tools and LMs that can be called: web search, calculator, file read, code interpreter, retrieval systems, SQLite, sub-model calls, and any external MCP server.
4. **Engine** -- The inference runtime: Ollama, SGLang, vLLM, llama.cpp, cloud APIs (OpenAI, Anthropic, Google). All implement the same `InferenceEngine` ABC.
5. **Learning** -- Methodologies for improving Intelligence (weight updates via SFT) or Agents (changes to system prompt, tools available, models available, retry/looping/exit logic via agent advisor and ICL updater). Trace-driven feedback loop.

Everything runs on your hardware. Cloud APIs are optional.

---

## Key Features

<div class="grid cards" markdown>

-   **Five Composable Pillars**

    ---

    Intelligence, Agents, Tools, Engine, and Learning — each with a clear ABC interface and decorator-based registry.

-   **5 Engine Backends**

    ---

    Ollama, vLLM, SGLang, llama.cpp, and cloud (OpenAI/Anthropic/Google). Same `InferenceEngine` ABC.

-   **5 Memory Backends**

    ---

    SQLite/FTS5, FAISS, ColBERTv2, BM25, and Hybrid (reciprocal rank fusion). Zero-dependency default.

-   **Hardware-Aware**

    ---

    Auto-detects GPU vendor, model, and VRAM. Recommends the optimal engine for your hardware.

-   **Offline-First**

    ---

    All core functionality works without a network connection. Cloud APIs are optional extras.

-   **OpenAI-Compatible API**

    ---

    `jarvis serve` starts a FastAPI server with SSE streaming. Drop-in replacement for OpenAI clients.

-   **Trace-Driven Learning**

    ---

    Every interaction is traced. The learning system improves models (SFT) and agents (prompt, tools, logic).

-   **Python SDK**

    ---

    The `Jarvis` class: three lines of code to ask a question. Full access to agents, tools, memory, and routing.

-   **CLI-First**

    ---

    `jarvis ask`, `jarvis serve`, `jarvis memory`, `jarvis bench` — every capability from the command line.

</div>

---

## Quick Start

=== "Browser App"

    Run the full chat UI locally with one script:

    ```bash
    git clone https://github.com/HazyResearch/OpenJarvis.git
    cd OpenJarvis
    ./scripts/quickstart.sh
    ```

    This installs dependencies, starts Ollama + a local model, launches the backend
    and frontend, and opens `http://localhost:5173` in your browser.

=== "Desktop App"

    Download the native desktop app — it bundles Ollama and the Python backend
    so everything works out of the box.

    [Download for macOS (Apple Silicon)](https://github.com/HazyResearch/OpenJarvis/releases/latest/download/OpenJarvis_aarch64.dmg){ .md-button .md-button--primary }

    Also available for [macOS (Intel)](https://github.com/HazyResearch/OpenJarvis/releases/latest/download/OpenJarvis_x64.dmg), [Windows](https://github.com/HazyResearch/OpenJarvis/releases/latest/download/OpenJarvis_x64-setup.exe), [Linux (DEB)](https://github.com/HazyResearch/OpenJarvis/releases/latest/download/OpenJarvis_amd64.deb), and [Linux (RPM)](https://github.com/HazyResearch/OpenJarvis/releases/latest/download/OpenJarvis_amd64.rpm). See the [Downloads](downloads.md) page for details.

=== "Python SDK"

    ```python
    from openjarvis import Jarvis

    j = Jarvis()
    response = j.ask("Explain quicksort in two sentences.")
    print(response)
    j.close()
    ```

    For more control, use `ask_full()` to get usage stats, model info, and tool results:

    ```python
    result = j.ask_full(
        "What is 2 + 2?",
        agent="orchestrator",
        tools=["calculator"],
    )
    print(result["content"])       # "4"
    print(result["tool_results"])  # [{tool_name: "calculator", ...}]
    ```

=== "CLI"

    ```bash
    # Ask a question
    jarvis ask "What is the capital of France?"

    # Use an agent with tools
    jarvis ask --agent orchestrator --tools calculator,think "What is 137 * 42?"

    # Start the API server
    jarvis serve --port 8000

    # Index documents and search memory
    jarvis memory index ./docs/
    jarvis memory search "configuration options"

    # Run inference benchmarks
    jarvis bench run --json
    ```

---

## Project Status

OpenJarvis v1.5 (Phase 10) is complete. The framework includes the full five-pillar architecture, seven agent types, Python SDK, CLI, OpenAI-compatible API server, benchmarking framework, and Docker deployment. The test suite contains over 1,800 tests.

| Component | Status |
|-----------|--------|
| Intelligence (model catalog + config) | Stable |
| Agents (7 types: Simple, Orchestrator, NativeReAct, NativeOpenHands, RLM, OpenHands SDK, OpenClaw) | Stable |
| Tools (MCP interface + 5 storage backends) | Stable |
| Engine (5 backends) | Stable |
| Learning (routing, SFT, agent advisor, ICL updater) | Stable |
| Python SDK | Stable |
| CLI | Stable |
| API Server | Stable |
| Trace System | Stable |
| Docker Deployment | Stable |

---

## Documentation

<div class="grid cards" markdown>

-   **[Getting Started](getting-started/installation.md)**

    ---

    Install OpenJarvis, configure your first engine, and run your first query in minutes.

-   **[User Guide](user-guide/cli.md)**

    ---

    Comprehensive guides for the CLI, Python SDK, agents, memory, tools, telemetry, and benchmarks.

-   **[Architecture](architecture/overview.md)**

    ---

    Deep dive into the five-pillar design, registry pattern, query flow, and cross-cutting learning system.

-   **[API Reference](api/index.md)**

    ---

    Auto-generated reference for every module: SDK, core, engine, agents, memory, tools, intelligence, learning, traces, telemetry, and server.

-   **[Deployment](deployment/docker.md)**

    ---

    Deploy OpenJarvis with Docker, systemd, or launchd. Includes GPU-accelerated container images.

-   **[Development](development/contributing.md)**

    ---

    Contributing guide, extension patterns, roadmap, and changelog.

</div>
