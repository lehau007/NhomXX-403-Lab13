from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, summarize_text
from .tracing import langfuse_context, observe


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe()
    def run(
        self,
        user_id: str,
        feature: str,
        session_id: str,
        message: str,
        correlation_id: str | None = None,
        env: str = "dev",
    ) -> AgentResult:
        started = time.perf_counter()
        docs = retrieve(message)
        prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
        response = self.llm.generate(prompt)
        quality_score = self._heuristic_quality(message, response.text, docs)
        latency_ms = int((time.perf_counter() - started) * 1000)
        input_cost = round((response.usage.input_tokens / 1_000_000) * 3, 6)
        output_cost = round((response.usage.output_tokens / 1_000_000) * 15, 6)
        cost_usd = self._estimate_cost(response.usage.input_tokens, response.usage.output_tokens)
        message_preview = summarize_text(message)
        answer_preview = summarize_text(response.text)
        user_id_hash = hash_user_id(user_id)
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        request_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        langfuse_context.update_current_trace(
            user_id=user_id_hash,
            session_id=session_id,
            input=message_preview,
            output=answer_preview,
            tags=["lab", feature, self.model],
            metadata={
                "service": "api",
                "event": "request_received",
                "level": "info",
                "env": env,
                "feature": feature,
                "model": self.model,
                "user_id_hash": user_id_hash,
                "session_id": session_id,
                "correlation_id": correlation_id,
                "ts": request_ts,
                "payload": {"message_preview": message_preview},
            },
        )
        langfuse_context.update_current_observation(
            name="response_sent",
            model=self.model,
            input=message_preview,
            output=answer_preview,
            metadata={
                "service": "api",
                "event": "response_sent",
                "level": "info",
                "env": env,
                "feature": feature,
                "model": self.model,
                "user_id_hash": user_id_hash,
                "session_id": session_id,
                "correlation_id": correlation_id,
                "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "latency_ms": latency_ms,
                "tokens_in": response.usage.input_tokens,
                "tokens_out": response.usage.output_tokens,
                "cost_usd": cost_usd,
                "quality_score": quality_score,
                "doc_count": len(docs),
                "query_preview": message_preview,
                "payload": {"answer_preview": answer_preview},
            },
            usage_details={
                "input": response.usage.input_tokens,
                "output": response.usage.output_tokens,
                "total": total_tokens,
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": total_tokens,
            },
            cost_details={
                "input": input_cost,
                "output": output_cost,
                "total": cost_usd,
                "total_cost": cost_usd,
            },
        )

        metrics.record_request(
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            quality_score=quality_score,
        )

        return AgentResult(
            answer=response.text,
            latency_ms=latency_ms,
            tokens_in=response.usage.input_tokens,
            tokens_out=response.usage.output_tokens,
            cost_usd=cost_usd,
            quality_score=quality_score,
        )

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
