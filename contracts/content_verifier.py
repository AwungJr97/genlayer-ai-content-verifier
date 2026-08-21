# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json


class ContentVerifier(gl.Contract):
    """AI-assisted content moderation with request-scoped evidence and actions."""

    next_request_id: u256
    request_text: TreeMap[u256, str]
    request_verdict: TreeMap[u256, str]
    request_reason: TreeMap[u256, str]
    request_sources: TreeMap[u256, str]
    request_moderation: TreeMap[u256, str]

    def __init__(self):
        self.next_request_id = u256(1)

    @gl.public.write
    def verify_content(self, text: str) -> u256:
        """Create one request, verify supplied source URLs, and store its consensus review."""
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")

        request_id = self.next_request_id
        self.next_request_id += 1

        self.request_text[request_id] = cleaned
        self.request_verdict[request_id] = "PENDING"
        self.request_reason[request_id] = ""
        self.request_sources[request_id] = "NONE"
        self.request_moderation[request_id] = "PENDING"

        urls = []
        for token in cleaned.replace("\n", " ").split():
            candidate = token.strip("()[]{}<>,.;\"'")
            if candidate.startswith("http://") or candidate.startswith("https://"):
                if candidate not in urls:
                    urls.append(candidate)

        def review():
            source_evidence = []
            for url in urls[:5]:
                try:
                    response = gl.nondet.web.get(url)
                    body = response.body.decode("utf-8")[:5000]
                    source_evidence.append(f"SOURCE {url}\n{body}")
                except Exception:
                    source_evidence.append(f"SOURCE {url}\nUNAVAILABLE")

            evidence_text = "\n\n".join(source_evidence) if source_evidence else "No URLs were supplied in the submitted content."
            prompt = f"""
You are a content quality reviewer and factual-source verifier.
Review the submitted content against the supplied source evidence.
Return JSON with exactly these keys:
{{"verdict":"PASS|REVIEW|REJECT","reason":"one short sentence","sources":"comma-separated verified URLs or NONE"}}

Rules:
- PASS: clear, useful, non-deceptive content whose factual claims are supported by the supplied evidence when evidence is needed.
- REVIEW: ambiguous, low quality, unsupported, or insufficiently evidenced claims.
- REJECT: clearly harmful, fraudulent, or deceptive content.
- Never invent a source or claim that a source supports something it does not support.
- Only list a URL in sources if its fetched content is relevant to the submitted claim.

Submitted content:
{cleaned}

Fetched source evidence:
{evidence_text}
"""
            return gl.nondet.exec_prompt(prompt, response_format="json")

        result = gl.eq_principle.prompt_comparative(
            review,
            principle=(
                "The verdict must be the same. The reason must support that verdict. "
                "Every listed source must be one of the supplied URLs and must be relevant "
                "to the submitted content."
            ),
        )

        verdict = "REVIEW"
        reason = "Consensus result requires review."
        sources = "NONE"
        try:
            verdict_candidate = str(result.get("verdict", "")).strip().upper()
            if verdict_candidate in ("PASS", "REVIEW", "REJECT"):
                verdict = verdict_candidate
            reason = str(result.get("reason", reason)).strip() or reason
            sources = str(result.get("sources", "NONE")).strip() or "NONE"
        except Exception:
            pass

        self.request_verdict[request_id] = verdict
        self.request_reason[request_id] = reason
        self.request_sources[request_id] = sources
        return request_id

    @gl.public.write
    def set_moderation(self, request_id: u256, action: str) -> None:
        """Apply APPROVE, HOLD, or REJECT to one specific moderation request."""
        if request_id not in self.request_text:
            raise ValueError("Unknown request id")

        normalized = action.strip().upper()
        if normalized not in ("APPROVE", "REJECT", "HOLD"):
            raise ValueError("Action must be APPROVE, REJECT, or HOLD")

        self.request_moderation[request_id] = normalized

    @gl.public.view
    def get_request(self, request_id: u256) -> dict:
        if request_id not in self.request_text:
            raise ValueError("Unknown request id")
        return {
            "request_id": request_id,
            "text": self.request_text[request_id],
            "verdict": self.request_verdict[request_id],
            "reason": self.request_reason[request_id],
            "sources": self.request_sources[request_id],
            "moderation": self.request_moderation[request_id],
        }

    @gl.public.view
    def get_request_count(self) -> u256:
        return self.next_request_id - u256(1)
