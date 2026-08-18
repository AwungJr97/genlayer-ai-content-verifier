# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *


class ContentVerifier(gl.Contract):
    """AI-assisted content review using GenLayer consensus."""

    last_text: str
    last_review: str

    def __init__(self):
        self.last_text = ""
        self.last_review = ""

    @gl.public.write
    def verify_content(self, text: str):
        """Ask independent validators to agree on a structured content review."""
        cleaned = text.strip()
        if not cleaned:
            raise ValueError("Text cannot be empty")

        def review():
            prompt = f"""
You are a content quality reviewer.
Review the text below and return exactly this format:
VERDICT: PASS, REVIEW, or REJECT
REASON: one short sentence

Text:
{cleaned}

Rules:
- PASS: clear, useful, and non-deceptive content.
- REVIEW: ambiguous, low quality, or needs context.
- REJECT: clearly harmful, fraudulent, or deceptive content.
"""
            return gl.nondet.exec_prompt(prompt).strip()

        result = gl.eq_principle.prompt_comparative(
            review,
            principle=(
                "The VERDICT must be the same. The REASON may use different wording "
                "but must support the same verdict."
            ),
        )

        self.last_text = cleaned
        self.last_review = result

    @gl.public.view
    def get_last_text(self) -> str:
        return self.last_text

    @gl.public.view
    def get_last_review(self) -> str:
        return self.last_review
