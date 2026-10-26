#!/usr/bin/env python3
"""Oracle "model": an OpenAI-compatible server that answers every prompt
with the known-correct proof of the item it asks about.

Validates the whole pipeline -- prompt rendering, extraction, statement
gate, compile, axiom audit, report -- independently of any real model:

    python scripts/oracle_server.py --port 8100 &
    OPENAI_BASE_URL=http://127.0.0.1:8100/v1 physproofbench generate \\
        --model oracle --run-dir runs/oracle-lean --items <canary ids> -k 1
    physproofbench grade-run --run-dir runs/oracle-lean

Expected: every sample passes, on every Mathlib pin (add
`--lean-project lean-v4.9` to `generate` for the old pin). Anything less is
a pipeline bug, not a model weakness.

The item is identified by the `-- PHYSPROOFBENCH-ITEM: <id>` tag that every
gold statement (and so every prompt) contains. Proofs are read from
`--proofs` (default: tests/fixtures/reference_proofs/<id>.lean). Standard
library only, so it runs in any Python 3.
"""

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ITEM_TAG = re.compile(r"PHYSPROOFBENCH-ITEM: (\S+)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--port", type=int, default=8100)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--model-name", default="oracle")
    ap.add_argument("--proofs", type=Path,
                    default=Path(__file__).resolve().parent.parent / "tests/fixtures/reference_proofs")
    args = ap.parse_args()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            self._send({"object": "list", "data": [{"id": args.model_name, "object": "model",
                                                    "created": 0, "owned_by": "oracle",
                                                    "max_model_len": 262144}]})

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            text = "\n".join(m.get("content") or "" for m in body.get("messages", []))
            match = ITEM_TAG.search(text)
            proof = args.proofs / f"{match.group(1)}.lean" if match else None
            if proof is not None and proof.exists():
                content = "```lean\n" + proof.read_text() + "```"
            else:
                content = f"(oracle has no reference proof for {match.group(1) if match else '?'})"
            self._send({"id": "oracle", "object": "chat.completion", "created": 0,
                        "model": args.model_name,
                        "choices": [{"index": 0, "finish_reason": "stop",
                                     "message": {"role": "assistant", "content": content}}],
                        "usage": {"prompt_tokens": 0, "completion_tokens": 0,
                                  "total_tokens": 0}})

    print(f"oracle serving {args.proofs} on http://{args.host}:{args.port}/v1", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
