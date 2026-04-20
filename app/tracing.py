from __future__ import annotations

import os
from typing import Any

try:
    # Langfuse v2 exposes decorators/context from langfuse.decorators.
    from langfuse.decorators import observe, langfuse_context
except Exception:  # pragma: no cover
    try:
        # Langfuse v3 exposes observe/get_client from package root.
        from langfuse import get_client, observe

        class _ClientContext:
            def __init__(self) -> None:
                self._client = get_client()

            def update_current_trace(self, **kwargs: Any) -> None:
                self._client.update_current_trace(**kwargs)

            def update_current_observation(self, **kwargs: Any) -> None:
                # v3 removed update_current_observation; route to span/generation update.
                if hasattr(self._client, "update_current_generation"):
                    self._client.update_current_generation(**kwargs)
                    return

                if hasattr(self._client, "update_current_span"):
                    span_kwargs = dict(kwargs)
                    usage_details = span_kwargs.pop("usage_details", None)
                    cost_details = span_kwargs.pop("cost_details", None)
                    if usage_details is not None:
                        metadata = dict(span_kwargs.get("metadata") or {})
                        metadata["usage_details"] = usage_details
                        span_kwargs["metadata"] = metadata
                    if cost_details is not None:
                        metadata = dict(span_kwargs.get("metadata") or {})
                        metadata["cost_details"] = cost_details
                        span_kwargs["metadata"] = metadata
                    self._client.update_current_span(**span_kwargs)

            def flush(self) -> None:
                if hasattr(self._client, "flush"):
                    self._client.flush()

        langfuse_context = _ClientContext()
    except Exception:
        def observe(*args: Any, **kwargs: Any):
            def decorator(func):
                return func
            return decorator

        class _DummyContext:
            def update_current_trace(self, **kwargs: Any) -> None:
                return None

            def update_current_observation(self, **kwargs: Any) -> None:
                return None

            def flush(self) -> None:
                return None

        langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
