# SM_01_E01_001 — Entropy is positively homogeneous

Source: Friedli & Velenik, *Statistical Mechanics: A Mathematical
Introduction*, Exercise 1.1, p. 7 (see
`docs/SOURCE.md#sm`). Paraphrased per `CONTRIBUTING.md`, not a
transcription.

## statement

Let `S(U, V, N)` be the thermodynamic entropy of a system as a function of
energy, volume and particle number. Suppose `S` behaves correctly when `n`
identical copies of a system are combined, i.e. `S(nU, nV, nN) = n S(U, V, N)`
for every positive integer `n`, and suppose `S` is continuous. Then `S` is
positively homogeneous of degree one: `S(tU, tV, tN) = t S(U, V, N)` for every
real `t > 0`.

## proof

Following the source's solution to Exercise 1.1 (Appendix C); paraphrased, not transcribed.

First handle unit fractions. By the integer-scaling property applied to the
macrostate `X/n`, `S(X) = S(n · (X/n)) = n S(X/n)`, so `S(X/n) = S(X)/n` for
every positive integer `n`. (In the source this step is the observation that
a system can be viewed as `n` identical subsystems, each with `1/n` of the
energy, volume and particle number, and that entropy adds over them.)

Next, positive rationals. For `t = m/n`, apply integer scaling to `X/n` with
factor `m`: `S((m/n) X) = m S(X/n) = (m/n) S(X)`. So the identity holds for
every positive rational `t`.

Finally, real `t > 0`. Choose positive rationals `t_k → t`. Every `t_k X` and
`t X` lies in the positive orthant, and `S` is continuous there, so
`S(t X) = lim S(t_k X) = lim t_k S(X) = t S(X)`.
