# Physics-Intuition Set: Pilot 2 (physics and proofs measured separately, 2026-11-03)

Follows `docs/PILOT_01.md`, on the same 10 items. Lean and Mathlib v4.34. Models:
Qwen3.8-27B on vLLM (temperature 0.6, top-p 0.95, top-k 20) and Claude Haiku 5.5
through OpenRouter (temperature 1.0, top-p 1.0, reasoning effort high).

## Where this fits in the A1/A2/B1/B2 framework

A1 is the easiest cell and B2 the hardest: A1/B1 give the solution, A2/B2 withhold it.
For this set, the "textbook proof" is the official olympiad solution. Proof runs are
all in row A, where the Lean statement is given. Autoformalization (B1, B2) is not
built. The physics-only test is outside the grid, because it involves no Lean.

| Cell | Runs |
|---|---|
| A1, solution given | Qwen one-shot and repair |
| A2, solution withheld | Haiku one-shot and repair with comments removed; Qwen one-shot and repair |

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

All 16 wrong answers are Qwen without thinking. One sample of each wrong answer was
read, so others with the same answer may have gone wrong differently:

| Item | Answer | Times | What went wrong in the sample read |
|---|---|---|---|
| PI_C_001 | c = 1/2 | 5 | Physics: all centrifugal force placed at the centre of mass |
| PI_C_001 | c = 1/3 | 1 | Sign error: `R_cm + (h/6) sin θ`, should be minus |
| PI_C_001 | c = 1/6 | 1 | Wrong correction term: `R/2 - (h/12) sin θ`, should be `R/2 - (h/3) sin θ` |
| PI_D_001 | ω = √(5g/3h) | 4 | Physics: γ = 5/3 for the gas alone, piston's heat capacity ignored |
| PI_D_002 | √(3k/m) | 2 | Physics: radial oscillation frequency, not orbital |
| PI_E_002 | n = -1/6 | 1 | Physics: gravitational pressure ∝ GM²/R³, which has the wrong dimensions |
| PI_E_002 | n = 1/3 | 2 | Algebra: right pressures, then `R ∝ M^(2-5/3)`, should be `M^(5/3-2)` |

The "Trap" column counts answers matching the trap's value. That doesn't always mean
falling for the trap, as the `PI_E_002` n = 1/3 sample shows.

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
| PI_A_002 | 0/4 | 1/4, 3 stopped early |
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
On the 8 answer-blank items, Haiku named the correct value in its first attempt in 29
of 32 samples, including attempts that failed to compile; the other 3 gave no answer.
This checks the first value line in each file. So the feedback fixed Lean, not physics.
The 3 `PI_A_002` samples that stopped early did so in round 1, most likely after
running out of tokens again. They count as not fixed.

## Compiler-feedback repair

Each failed proof gets a new message with up to 12 of Lean's errors (line, column,
and what is still to prove at that point), the whole file with line numbers, and an
instruction to fix it and return the complete file. The model also sees the original
prompt and its last answer, but not its earlier thinking or older attempts. Up to 3
rounds. Qwen and Haiku get the same feedback text. Qwen had 32,768 tokens per round
and Haiku 128,000, and which errors get fixed has not been measured.
 Items for Qwen: `PI_B_001`, `PI_B_002`, `PI_C_002`, `PI_D_001`, `PI_E_002`;
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

- With thinking, both models get these problems right. Qwen's main
  obstacle on these items is Lean.
- Without thinking, Qwen makes real physics mistakes, often giving the trap value.
  The wrong answers are on only `PI_C_001`, `PI_D_001`, `PI_D_002` and `PI_E_002`, and
  the pilot can't yet separate capable models on physics.
- Compiler feedback rescues most of Haiku's failures (12 of 15), and those fixes were
  to the Lean, since its values were already right in the attempts checked. It can also produce
  valid Qwen proofs, but 6 of Qwen's 8 passes are on one algebra-heavy item. The two
  are not directly comparable: they ran on different samples, and Qwen's prompts
  showed comments.

## Why Qwen's one-attempt proofs fail

Counts come from a text search of Lean's messages, so one slip can be counted several
times: type mismatch 130, no goals to be solved 86, unsolved goals 79, unknown name
59, unexpected token 14. Real examples:

| Error | Item | Code | What went wrong |
|---|---|---|---|
| Type mismatch | PI_D_001 | `mul_ne_zero (by norm_num) hnr` for `(9 / 2) * n * R ≠ 0` | Lean groups this as `((9/2) * n) * R`, so it needs `R ≠ 0`, not `n * R ≠ 0` |
| No goals | PI_C_002 | `ring` after `field_simp [hV0, h2V0]` | `field_simp` had already finished the step |
| Unsolved goals | PI_C_002 | `have h_mul : ... := by` | The equation is claimed, but its steps do not finish showing it |
| Unknown name | PI_A_001 | `rw [IsLittleO_iff_tendsto]` | The lemma is `Asymptotics.isLittleO_iff_tendsto` |

## Limits

- **Main limit: statements can make the decision for the model.** `PI_A_001` says "to
  leading nontrivial order", `PI_C_001` gives the form of the answer, and `PI_D_001`
  says "in terms of `g` and `h` only". 64/64 shows the models can solve these problems
  as posed, not that they would choose the right approximation unprompted.
- Physics scores check final answers. Reasoning was read for only one sample of each
  wrong answer, and not for the correct answers.
- Public olympiad problems: memorization can't be ruled out.
- Physics answers were read by one reader against recorded answers, not blind.
- A proof shows a statement holds, not that it faithfully captures the problem.
- A passing proof of an answer-blank item names a correct value, but the value can
  sometimes be derived from the statement by mathematics alone.
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
4. Test judgment directly: alter known problems so a remembered answer is wrong, remove
   hints and the answer's form, and ask whether an approximation holds.
