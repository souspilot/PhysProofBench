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
    # Reasoning-model "thinking" text, when the server splits it out of
    # `content` (vLLM's reasoning parser exposes it as `reasoning_content`,
    # newer versions as `reasoning`). Empty `text` with a non-empty
    # `reasoning` and finish_reason "length" means the token budget was
    # spent thinking.
    reasoning: str | None = None


def get_client(timeout: float | None = 3600.0) -> OpenAI:
    """`timeout=None` disables the client-side timeout. The SDK default is
    10 minutes with 2 retries, which is wrong for long generations: a slow
    reasoning trace that outlives it is abandoned and then *regenerated*.
    Retries are therefore off; a failed generation should fail loudly."""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=0)


def complete(
    prompt: str,
    *,
    model: str,
    system: str | None = None,
    temperature: float = 0.0,
    max_tokens: int | None = 16384,
    enable_thinking: bool | None = None,
    timeout: float | None = 3600.0,
) -> Completion:
    """`max_tokens=None` or any value <= 0 (0, -1) means *no cap*: the
    parameter is omitted from the request, so the server generates until the
    model stops or its context window is full.

    `enable_thinking=False` asks a Qwen3-style chat template to skip the
    reasoning phase (sent as `chat_template_kwargs`, a vLLM extension);
    `None` leaves the server/model default alone."""
    client = get_client(timeout)
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    extra_body = None
    if enable_thinking is not None:
        extra_body = {"chat_template_kwargs": {"enable_thinking": enable_thinking}}
    request: dict = {}
    if max_tokens is not None and max_tokens > 0:
        request["max_tokens"] = max_tokens
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        extra_body=extra_body,
        **request,
    )
    choice = resp.choices[0]
    message = choice.message
    reasoning = getattr(message, "reasoning_content", None) or getattr(
        message, "reasoning", None
    )
    return Completion(
        text=message.content or "",
        model=resp.model,
        finish_reason=choice.finish_reason,
        reasoning=reasoning,
    )
