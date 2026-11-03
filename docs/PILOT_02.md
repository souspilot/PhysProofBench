# Physics-Intuition Set: Pilot 2 (physics and proofs measured separately, 2026-11-03)

Follows `docs/PILOT_01.md`, on the same 10 items. Lean and Mathlib v4.34. Models:
Qwen3.8-27B on vLLM (temperature 0.6, top-p 0.95, top-k 20) and Claude Haiku 5.5
through OpenRouter (temperature 1.0, top-p 1.0, reasoning effort high).

## Where this fits in the A1/A2/B1/B2 framework

For this set, the "textbook proof" is the official olympiad solution. Proof runs are
all in row A, where the Lean statement is given. Autoformalization (B1, B2) is not
built. The physics-only test is outside the grid, because it involves no Lean.

| Cell | Runs |
|---|---|
| A1, solution withheld | Haiku one-shot and repair with comments removed; Qwen one-shot and repair |
| A2, solution given | Qwen one-shot and repair |

## Correction: answers leaked into the first pilot's prompts

8 of the 10 items (all but `PI_B_001` and `PI_B_002`) state the expected answer in
a comment in the Lean item file, and proof prompts include those comments. Both
models saw them in every earlier PI run.

- The first pilot's conclusion that both models get the physics right was
  unsupported. It is replaced by the physics-only test below.
- Proof pass rates remain valid as a measure of Lean ability.
- Item files are unchanged so far, so existing runs still grade.
  `generate --strip-statement-comments` removes comments from the prompt.

One-shot results from those runs: Qwen 0/74 (6 of the planned 80 samples did not
complete) and Haiku 46/80.

## Physics-only test

`physproofbench physics-only`: the plain-English statement from `nl.md`, with no
Lean and no comments, ending in a `FINAL ANSWER` line. Items with
`shape: answer_blank` only, 8 attempts each. Answers were read and scored by hand
against `expected_answer` and `plug_in_trap`. `PI_C_002` is counted on its final
temperature.

| Item | Qwen, no thinking | Trap | Other wrong | Qwen, thinking | Haiku |
|---|---|---|---|---|---|
| PI_A_001 | 8/8 | 0 | 0 | 8/8 | 8/8 |
| PI_A_002 | 8/8 | 0 | 0 | 8/8 | 8/8 |
| PI_C_001 | 1/8 | 5 | 2 | 8/8 | 8/8 |
| PI_C_002 | 8/8 | 0 | 0 | 8/8 | 8/8 |
| PI_D_001 | 4/8 | 4 | 0 | 8/8 | 8/8 |
| PI_D_002 | 6/8 | 2 | 0 | 8/8 | 8/8 |
| PI_E_001 | 8/8 | 0 | 0 | 8/8 | 8/8 |
| PI_E_002 | 5/8 | 2 | 1 | 8/8 | 8/8 |
| **Total** | **48/64** | **13** | **3** | **64/64** | **64/64** |

Tokens per answer: Qwen without thinking 711–8,497, Qwen with thinking
778–42,213, Haiku 802–5,676. No thinking-run answer was forced. "No thinking" means
the chat-template switch was off; the model still writes out visible reasoning.

Run directories: `runs/phys-qwen-nothink`, `runs/phys-qwen-think`, `runs/phys-haiku`.

## Proofs with comments removed (Haiku)

`runs/pi-haiku-clean`: all comments removed from the statement, no expert proof,
4 attempts per item. `runs/assist-haiku-clean` then gives each failed sample up to
3 rounds of compiler feedback.

| Item | One-shot | After feedback |
|---|---|---|
| PI_A_001 | 0/4 | 4/4 |
| PI_A_002 | 0/4 | 1/4, 3 unfinished |
| PI_B_001 | 4/4 | 4/4 |
| PI_B_002 | 4/4 | 4/4 |
| PI_C_001 | 3/4 | 4/4 |
| PI_C_002 | 3/4 | 4/4 |
| PI_D_001 | 1/4 | 4/4 |
| PI_D_002 | 3/4 | 4/4 |
| PI_E_001 | 3/4 | 4/4 |
| PI_E_002 | 4/4 | 4/4 |
| **Total** | **25/40** | **37/40** |

The matching run with comments shown scored 24/40, so comments did not visibly
change the one-shot rate. Removing them also removes helpful explanations of the
statement. Every item now has a Lean-accepted proof with no answer in the prompt.
The 3 unfinished `PI_A_002` samples stopped before using all 3 rounds, so they are
not failed repairs.

## Compiler-feedback repair

Each failed proof is returned with Lean's errors and goal states, for up to 3
rounds. Items for Qwen: `PI_B_001`, `PI_B_002`, `PI_C_002`, `PI_D_001`, `PI_E_002`;
both conditions; 2 samples each, so 20 samples per setup. All 20 had failed in the
original runs. These repairs start from the original runs, so `PI_C_002`, `PI_D_001`
and `PI_E_002` had the leak; `PI_B_001` and `PI_B_002` did not.

| Setup | Runs | Passing after up to 3 rounds | Samples |
|---|---|---|---|
| Qwen, feedback only | `assist-fb-{a,b}` | 4/20 | `PI_C_002` no NL proof #0 and #1; `PI_C_002` with NL proof #1; `PI_E_002` with NL proof #0 |
| Qwen, feedback + examples | `assist-ex-{a,b}` | 4/20 | `PI_C_002` no NL proof #1; `PI_C_002` with NL proof #0 and #1; `PI_B_001` with NL proof #1 |

Worked examples are verified Haiku proofs of other items (`--examples-from
runs/pi-haiku55 --example-items PI_C_002,PI_D_001,PI_B_002,PI_E_002
--num-examples 3`); a sample never sees a proof of its own item. The two setups
can't be separated at this sample size.

## What this shows

- With reasoning, both models get these physical decisions right. Qwen's main
  obstacle on these items is Lean.
- The traps are real but only catch short reasoning. Only `PI_C_001`, `PI_D_001`,
  `PI_D_002` and `PI_E_002` caught anything, so the pilot can't yet separate capable
  models on physics.
- Compiler feedback rescues most of Haiku's failures (12 of 15). It can also produce
  valid Qwen proofs, but 6 of Qwen's 8 passes are on one algebra-heavy item. The two
  are not directly comparable: they ran on different samples, and Qwen's prompts
  showed comments.

## Limits

- Public olympiad problems: memorization can't be ruled out.
- Some statements give the form of the answer.
- Physics answers were read by one reader against recorded answers, not blind.
- A proof shows a statement holds, not that it faithfully captures the problem.
- A passing proof of an answer-blank item names a correct value, but the value can
  sometimes be derived from the statement by mathematics alone, and Lean's errors
  could steer a model away from a wrong value during repair.
- One source, and a limited range of physics.

## Pipeline

- `generate --strip-statement-comments` removes comments from the prompt.
- `physics-only` runs the physics test.
- `repair --examples-from` adds worked examples to the feedback.
- `grade-run --follow` grades each repair round's new candidate as it arrives.
- Forced answers in `repair` need a vLLM server, so a hosted-API repair that runs out
  of tokens while thinking ends in an error.

## Implications for the next 40 items

1. Screen candidates with the physics-only test before formalizing them.
2. Remove answers from item comments, and check this in review.
3. Report physics score, one-shot proof rate and assisted proof rate separately.
