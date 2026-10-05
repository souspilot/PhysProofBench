"""Thin OpenAI-compatible chat completion client.

Talks to anything speaking the OpenAI `/v1/chat/completions` API --
OpenAI itself, or a local server (vLLM, an OpenAI-compatible proxy, etc).
Reads `OPENAI_API_KEY` and `OPENAI_BASE_URL` explicitly from the
environment rather than relying on the `openai` SDK's own implicit env
handling, so it's obvious which two variables control where requests go.
"""

from __future__ import annotations

import os
import time
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
    prompt_tokens: int | None = None
    # Includes reasoning tokens on vLLM (thinking is generated text too).
    completion_tokens: int | None = None
    elapsed_s: float | None = None
    # complete_continuation only: the max_tokens actually sent, after
    # capping to the context window.
    max_tokens_sent: int | None = None


def get_client(timeout: float | None = 3600.0) -> OpenAI:
    """`timeout=None` disables the client-side timeout. The SDK default is
    10 minutes with 2 retries, which is wrong for long generations: a slow
    reasoning trace that outlives it is abandoned and then *regenerated*.
    Retries are therefore off; a failed generation should fail loudly."""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        if not base_url:
            raise RuntimeError("OPENAI_API_KEY is not set")
        # A local server (vLLM without --api-key) accepts any key, but the
        # SDK refuses to start without one.
        api_key = "EMPTY"
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
    top_p: float | None = None,
    top_k: int | None = None,
    seed: int | None = None,
    client: OpenAI | None = None,
) -> Completion:
    """`max_tokens=None` or any value <= 0 (0, -1) means *no cap*: the
    parameter is omitted from the request, so the server generates until the
    model stops or its context window is full.

    `enable_thinking=False` asks a Qwen3-style chat template to skip the
    reasoning phase (sent as `chat_template_kwargs`, a vLLM extension);
    `None` leaves the server/model default alone. `top_k` is likewise a vLLM
    extension (sent in `extra_body`); `top_p` and `seed` are standard.

    Pass a shared `client` when calling from many threads (the SDK client is
    thread-safe); otherwise one is built per call with `timeout`."""
    client = client or get_client(timeout)
    messages: list[dict[str, str]] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    extra_body: dict = {}
    if enable_thinking is not None:
        extra_body["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    if top_k is not None:
        extra_body["top_k"] = top_k
    request: dict = {}
    if max_tokens is not None and max_tokens > 0:
        request["max_tokens"] = max_tokens
    if top_p is not None:
        request["top_p"] = top_p
    if seed is not None:
        request["seed"] = seed
    start = time.monotonic()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        extra_body=extra_body or None,
        **request,
    )
    elapsed = time.monotonic() - start
    choice = resp.choices[0]
    message = choice.message
    reasoning = getattr(message, "reasoning_content", None) or getattr(
        message, "reasoning", None
    )
    usage = getattr(resp, "usage", None)
    return Completion(
        text=message.content or "",
        model=resp.model,
        finish_reason=choice.finish_reason,
        reasoning=reasoning,
        prompt_tokens=getattr(usage, "prompt_tokens", None),
        completion_tokens=getattr(usage, "completion_tokens", None),
        elapsed_s=elapsed,
    )


# --- raw continuation (vLLM) -------------------------------------------------
#
# Continuing a partially written assistant turn through the *chat* API depends
# on the model's chat template, and Qwen3's template re-renders the final
# assistant message: a message whose text has no closing `</think>` gets an
# empty `<think></think>` block inserted in front of it, which corrupts a
# continuation of unfinished reasoning. So continuations are built at the
# token level instead: vLLM's `/tokenize` renders the chat prompt exactly as
# generation saw it, the prefix text is tokenized and appended, and the
# result goes to the plain completions endpoint (no template, no reasoning
# parser). This also gives exact token counts for sizing `max_tokens`.


def _server_root(base_url: str) -> str:
    root = base_url.rstrip("/")
    return root[: -len("/v1")] if root.endswith("/v1") else root


def _post_json(url: str, body: dict, timeout: float | None) -> dict:
    import json
    import urllib.request

    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


@dataclass
class TokenizedPrefix:
    ids: list[int]
    max_model_len: int | None


def tokenize_continuation(
    prompt: str,
    prefix: str,
    *,
    model: str,
    enable_thinking: bool | None = None,
    timeout: float | None = 120.0,
) -> TokenizedPrefix:
    """Token ids for: the chat prompt (user turn + generation prompt, exactly
    as `complete` sends it), then `prefix`. If the rendered generation prompt
    already ends inside an opened `<think>` block (templates that inject it),
    a leading `<think>\\n` in `prefix` is dropped so it isn't doubled."""
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not base_url:
        raise RuntimeError("OPENAI_BASE_URL is not set")
    root = _server_root(base_url)
    chat_body: dict = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "add_generation_prompt": True,
    }
    if enable_thinking is not None:
        chat_body["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    chat = _post_json(f"{root}/tokenize", chat_body, timeout)
    ids = list(chat["tokens"])
    tail = _post_json(f"{root}/detokenize", {"model": model, "tokens": ids[-8:]}, timeout)
    if tail.get("prompt", "").rstrip().endswith("<think>") and prefix.startswith("<think>"):
        prefix = prefix[len("<think>"):].lstrip("\n")
    text = _post_json(
        f"{root}/tokenize",
        {"model": model, "prompt": prefix, "add_special_tokens": False},
        timeout,
    )
    return TokenizedPrefix(ids=ids + list(text["tokens"]),
                           max_model_len=chat.get("max_model_len"))


def complete_continuation(
    prompt: str,
    prefix: str,
    *,
    model: str,
    max_tokens: int,
    reserve_tokens: int = 0,
    enable_thinking: bool | None = None,
    temperature: float = 0.0,
    top_p: float | None = None,
    top_k: int | None = None,
    seed: int | None = None,
    timeout: float | None = 3600.0,
    client: OpenAI | None = None,
) -> Completion:
    """Generate a continuation of `prefix` (assistant-side text) after the
    chat prompt for `prompt`. `max_tokens` is capped so that prompt + prefix
    + generation + `reserve_tokens` fits the server's context window.
    Returns raw generated text in `text` (`reasoning` is always None: no
    reasoning parser runs on this path); `prompt_tokens` is the exact
    prompt + prefix length."""
    tokenized = tokenize_continuation(prompt, prefix, model=model,
                                      enable_thinking=enable_thinking)
    if tokenized.max_model_len:
        room = tokenized.max_model_len - len(tokenized.ids) - reserve_tokens
        max_tokens = min(max_tokens, room)
    if max_tokens <= 0:
        raise ValueError(
            f"no room left in the context window: prompt+prefix is {len(tokenized.ids)} "
            f"tokens, reserve {reserve_tokens}, window {tokenized.max_model_len}"
        )
    client = client or get_client(timeout)
    request: dict = {"max_tokens": max_tokens}
    if top_p is not None:
        request["top_p"] = top_p
    if seed is not None:
        request["seed"] = seed
    start = time.monotonic()
    resp = client.completions.create(
        model=model,
        prompt=tokenized.ids,
        temperature=temperature,
        extra_body={"top_k": top_k} if top_k is not None else None,
        **request,
    )
    elapsed = time.monotonic() - start
    choice = resp.choices[0]
    usage = getattr(resp, "usage", None)
    return Completion(
        text=choice.text or "",
        model=resp.model,
        finish_reason=choice.finish_reason,
        reasoning=None,
        prompt_tokens=len(tokenized.ids),
        completion_tokens=getattr(usage, "completion_tokens", None),
        elapsed_s=elapsed,
        max_tokens_sent=max_tokens,
    )
