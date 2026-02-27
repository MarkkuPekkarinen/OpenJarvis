"""LM Studio inference engine backend (OpenAI-compatible API)."""

from __future__ import annotations

from openjarvis.core.registry import EngineRegistry
from openjarvis.engine._openai_compat import _OpenAICompatibleEngine


@EngineRegistry.register("lmstudio")
class LMStudioEngine(_OpenAICompatibleEngine):
    """LM Studio backend — thin wrapper over the shared OpenAI-compatible base."""

    engine_id = "lmstudio"
    _default_host = "http://localhost:1234"


__all__ = ["LMStudioEngine"]
