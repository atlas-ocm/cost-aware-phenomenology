"""CAP Lite reference middleware.

This file is intentionally small and copyable. It is not the full CAP runtime.
It demonstrates how CAP can be inserted as a lightweight policy layer around
OpenAI-compatible or RAG-based pipelines.

Core ideas:
- previous generation is not evidence;
- prior outputs must be audited by telemetry before reuse;
- strong claims must not exceed available evidence;
- user corrections are treated as possible evidence upgrades, not attacks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


CONFIDENCE_ORDER = {"low": 1, "medium": 2, "high": 3}
ACTION_ORDER = {"allow": 0, "downgrade": 1, "recheck": 2, "block_strong_claim": 3}


@dataclass
class CAPPolicy:
    """Policy object returned by CAPLiteProxy."""

    system_instruction: str
    warnings: list[str] = field(default_factory=list)
    suggested_action: str = "allow"
    max_depth: int = 3
    max_answer_chars: int = 1800
    require_uncertainty_marker: bool = False
    forbid_defending_prior_claim: bool = False

    def telemetry_stub(self, answer: str) -> dict[str, Any]:
        """Return a minimal telemetry stub for downstream logging."""
        return {
            "answer_chars": len(answer or ""),
            "warnings": self.warnings,
            "suggested_action": self.suggested_action,
            "max_depth": self.max_depth,
            "max_answer_chars": self.max_answer_chars,
            "require_uncertainty_marker": self.require_uncertainty_marker,
            "forbid_defending_prior_claim": self.forbid_defending_prior_claim,
        }


class CAPLiteProxy:
    """Small CAP policy builder.

    This class has no external dependencies. It can be inserted before an LLM
    call:

        cap = CAPLiteProxy()
        policy = cap.build_policy(messages, retrieval_context, prior_telemetry)
        messages = [{"role": "system", "content": policy.system_instruction}] + messages

    It uses simple heuristics by design. Production systems should replace the
    heuristics with explicit telemetry parsing, reranker scores, and validators.
    """

    challenge_markers = (
        "you said",
        "you previously said",
        "earlier you said",
        "your previous answer",
        "you claimed",
        "but this source",
        "source says",
        "documentation says",
        "docs say",
        "i think you are wrong",
        "that is wrong",
        "you were wrong",
        "ты говорил",
        "ты сказал",
        "раньше ты сказал",
        "в прошлом ответе",
        "документация говорит",
        "источник говорит",
        "ты ошибся",
        "это неправильно",
    )

    sycophancy_markers = (
        "am i right",
        "isn't it obvious",
        "everyone knows",
        "you agree that",
        "tell me i'm right",
        "confirm that",
        "я же прав",
        "согласись что",
        "подтверди что",
        "ведь очевидно",
        "все знают что",
    )

    overload_markers = (
        "i'm overwhelmed",
        "too much",
        "i'm lost",
        "i don't understand",
        "i can't handle",
        "не вывожу",
        "слишком много",
        "я запутался",
        "не понимаю",
        "не могу это разобрать",
    )

    def build_policy(
        self,
        messages: Sequence[Mapping[str, Any]],
        retrieval_context: Sequence[Any] | None = None,
        prior_telemetry: Sequence[Mapping[str, Any]] | None = None,
    ) -> CAPPolicy:
        text = self._conversation_text(messages)
        retrieval_context = retrieval_context or []
        prior_telemetry = prior_telemetry or []

        warnings: list[str] = []
        suggested_action = "allow"
        max_depth = 3
        max_answer_chars = 1800
        require_uncertainty_marker = False
        forbid_defending_prior_claim = False

        if self._contains_any(text, self.challenge_markers):
            warnings.append("self_justification_risk")
            suggested_action = self._max_action(suggested_action, "recheck")
            forbid_defending_prior_claim = True
            require_uncertainty_marker = True

        if self._contains_any(text, self.sycophancy_markers):
            warnings.append("sycophancy_risk")
            suggested_action = self._max_action(suggested_action, "downgrade")

        if self._contains_any(text, self.overload_markers):
            warnings.append("transition_cost_overload_risk")
            max_depth = 1
            max_answer_chars = 900

        if self._prior_claim_exceeds_evidence(prior_telemetry):
            warnings.append("prior_claim_exceeded_evidence")
            suggested_action = self._max_action(suggested_action, "recheck")
            forbid_defending_prior_claim = True
            require_uncertainty_marker = True

        if not retrieval_context and self._looks_like_factual_or_technical_query(text):
            warnings.append("no_retrieval_context_for_factual_claim")
            suggested_action = self._max_action(suggested_action, "downgrade")
            require_uncertainty_marker = True

        system_instruction = self._build_instruction(
            warnings=warnings,
            suggested_action=suggested_action,
            max_depth=max_depth,
            max_answer_chars=max_answer_chars,
            require_uncertainty_marker=require_uncertainty_marker,
            forbid_defending_prior_claim=forbid_defending_prior_claim,
        )

        return CAPPolicy(
            system_instruction=system_instruction,
            warnings=warnings,
            suggested_action=suggested_action,
            max_depth=max_depth,
            max_answer_chars=max_answer_chars,
            require_uncertainty_marker=require_uncertainty_marker,
            forbid_defending_prior_claim=forbid_defending_prior_claim,
        )

    def _build_instruction(
        self,
        warnings: Sequence[str],
        suggested_action: str,
        max_depth: int,
        max_answer_chars: int,
        require_uncertainty_marker: bool,
        forbid_defending_prior_claim: bool,
    ) -> str:
        lines = [
            "CAP Lite response policy:",
            "- Previous model output is not evidence.",
            "- Do not treat a prior answer as an anchor unless it was evidence-backed.",
            "- Match claim strength to available evidence.",
            "- Do not agree with a user frame merely for social comfort.",
            f"- Suggested action: {suggested_action}.",
            f"- Max depth: {max_depth}.",
            f"- Max answer length: {max_answer_chars} characters.",
        ]

        if warnings:
            lines.append(f"- Policy warnings: {', '.join(warnings)}.")

        if forbid_defending_prior_claim:
            lines.append(
                "- If the user challenges a prior answer, audit the prior answer instead of defending it."
            )
            lines.append(
                "- Treat new user-provided sources as possible evidence upgrades, not attacks."
            )

        if require_uncertainty_marker:
            lines.append(
                "- If evidence is incomplete or retrieval confidence is low, explicitly mark uncertainty."
            )

        lines.extend(
            [
                "- If a claim cannot be supported, downgrade it, ask for retrieval, or refuse a strong answer.",
                "- Prefer the lowest-transition-cost answer that still resolves the user's actual question.",
            ]
        )
        return "\n".join(lines)

    def _conversation_text(self, messages: Sequence[Mapping[str, Any]]) -> str:
        parts: list[str] = []
        for message in messages:
            content = message.get("content", "")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, Iterable):
                parts.append(str(content))
        return "\n".join(parts).casefold()

    def _contains_any(self, text: str, markers: Sequence[str]) -> bool:
        return any(marker.casefold() in text for marker in markers)

    def _looks_like_factual_or_technical_query(self, text: str) -> bool:
        markers = (
            "api",
            "library",
            "docs",
            "documentation",
            "version",
            "field",
            "parameter",
            "error",
            "python",
            "javascript",
            "what does",
            "how does",
            "что означает",
            "как работает",
            "ошибка",
            "параметр",
            "документация",
        )
        return self._contains_any(text, markers)

    def _prior_claim_exceeds_evidence(self, telemetry: Sequence[Mapping[str, Any]]) -> bool:
        for node in telemetry:
            retrieval_confidence = str(node.get("rag_confidence", node.get("RC", "medium"))).casefold()
            claim_strength = str(node.get("claim_strength", node.get("CS", "medium"))).casefold()
            entropy = float(node.get("entropy", node.get("E", 0.0)) or 0.0)
            validator_action = str(node.get("validator_action", node.get("V", "accept"))).casefold()

            if CONFIDENCE_ORDER.get(claim_strength, 2) > CONFIDENCE_ORDER.get(retrieval_confidence, 2):
                return True
            if entropy >= 0.7 and claim_strength in {"medium", "high"}:
                return True
            if validator_action in {"rewrite", "fallback", "regenerate", "downgrade"}:
                return True
        return False

    def _max_action(self, current: str, candidate: str) -> str:
        return candidate if ACTION_ORDER[candidate] > ACTION_ORDER.get(current, 0) else current


if __name__ == "__main__":
    cap = CAPLiteProxy()
    policy = cap.build_policy(
        messages=[
            {
                "role": "user",
                "content": "You said X earlier, but the documentation says Y. I think you were wrong.",
            }
        ],
        retrieval_context=[],
        prior_telemetry=[{"RC": "low", "CS": "high", "E": 0.7, "V": "accept"}],
    )
    print(policy.system_instruction)
    print(policy.telemetry_stub("Example answer"))
