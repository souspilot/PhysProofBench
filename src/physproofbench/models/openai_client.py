"""Thin OpenAI-compatible chat completion client.

Talks to anything speaking the OpenAI `/v1/chat/completions` API --
OpenAI itself, or a local server (vLLM, an OpenAI-compatible proxy, etc).
Reads `OPENAI_API_KEY` and `OPENAI_BASE_URL` explicitly from the
environment rather than relying on the `openai` SDK's own implicit env
handling, so it's obvious which two variables control where requests go.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass
class Completion:
    text: str
    model: str
    finish_reason: str | None


def get_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key, base_url=base_url)


def complete(
    prompt: str,
    *,
    model: str,
    system: str | None = None,
    temperature: float = 0.0,
    max_tokens: int = 4096,
) -> Completion:
    client = get_client()
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    choice = resp.choices[0]
    return Completion(
        text=choice.message.content or "",
        model=resp.model,
        finish_reason=choice.finish_reason,
    )
