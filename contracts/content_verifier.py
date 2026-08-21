# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ContentVerifier(gl.Contract):
    """AI-assisted content moderation using per-request GenLayer consensus."""

    next_request_id: int
    requests: dict

    def __init__(self):
        self.next_request_id = 1
        self.requests = {}

    @gl.public.write
    def verify_content(self, text: str) -> int:
        """Create a moderation request and resolve it through validator consensus."""
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")

        request_id = self.next_request_id
        self.next_request_id += 1

        self.requests[request_id] = {
            "text": cleaned,
            "verdict": "PENDING",
            "reason": "",
            "moderation": "PENDING",
            "sources": "",
        }

        def review():
            prompt = f"""
You are a content quality reviewer and source verifier.
Review the text below and return exactly this format:
VERDICT: PASS, REVIEW, or REJECT
REASON: one short sentence
SOURCES: comma-separated URLs or source names that directly support the factual assessment, or NONE

Rules:
- PASS: clear, useful, non-deceptive content supported by relevant evidence.
- REVIEW: ambiguous, low quality, or claims that require additional verification.
- REJECT: clearly harmful, fraudulent, or deceptive content.
- Prefer relevant primary or authoritative sources when factual claims are present.
- Do not invent sources. Use NONE when no source can be verified.

Text:
{cleaned}
"""
            return gl.nondet.exec_prompt(prompt).strip()

        result = gl.eq_principle.prompt_comparative(
            review,
            principle=(
                "The VERDICT must be the same. The REASON and SOURCES may differ in wording, "
                "but they must support the same moderation verdict and factual assessment."
            ),
        )

        verdict = "REVIEW"
        reason = "Consensus result requires review."
        sources = "NONE"

        for line in str(result).splitlines():
            cleaned_line = line.strip()
            upper = cleaned_line.upper()
            if upper.startswith("VERDICT:"):
                candidate = cleaned_line.split(":", 1)[1].strip().upper()
                if candidate in ("PASS", "REVIEW", "REJECT"):
                    verdict = candidate
            elif upper.startswith("REASON:"):
                reason = cleaned_line.split(":", 1)[1].strip()
            elif upper.startswith("SOURCES:"):
                sources = cleaned_line.split(":", 1)[1].strip() or "NONE"

        self.requests[request_id] = {
            "text": cleaned,
            "verdict": verdict,
            "reason": reason,
            "moderation": "PENDING",
            "sources": sources,
        }
        return request_id

    @gl.public.write
    def set_moderation(self, request_id: int, action: str):
        """Apply a real moderation action to one stored request."""
        if request_id not in self.requests:
            raise ValueError("Unknown request id")

        normalized = action.strip().upper()
        if normalized not in ("APPROVE", "REJECT", "HOLD"):
            raise ValueError("Action must be APPROVE, REJECT, or HOLD")

        self.requests[request_id] = {
            "text": self.requests[request_id]["text"],
            "verdict": self.requests[request_id]["verdict"],
            "reason": self.requests[request_id]["reason"],
            "moderation": normalized,
            "sources": self.requests[request_id]["sources"],
        }

    @gl.public.view
    def get_request(self, request_id: int) -> dict:
        if request_id not in self.requests:
            raise ValueError("Unknown request id")
        return self.requests[request_id]

    @gl.public.view
    def get_request_count(self) -> int:
        return self.next_request_id - 1
