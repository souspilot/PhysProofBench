# The physics-intuition pilot, explained

A companion to the pilot slides. It explains the five categories of
"physical decision" and walks through all ten pilot problems and their
solutions. It assumes you can follow algebra and a little calculus
(derivatives, integrals, the idea of a Taylor series), but not that you have
met the specific laws or jargon. Every law is introduced where it is used,
and there is a glossary at the end.

Each problem is paraphrased from the US Physics Olympiad (USAPhO), whose
official solutions are written by the AAPT problem committee. The item IDs
(`PI_A_001` and so on) match the files in `items/`.

---

## Contents

1. [What we are trying to test](#1-what-we-are-trying-to-test)
2. [How an item turns into a theorem](#2-how-an-item-turns-into-a-theorem)
3. [The five categories](#3-the-five-categories)
4. [The ten problems](#4-the-ten-problems)
   - [A1. Arc vs chord](#a1-pi_a_001--how-much-longer-is-an-arc-than-its-chord)
   - [A2. Einstein solid](#a2-pi_a_002--the-first-quantum-correction-to-a-solids-heat-capacity)
   - [B1. Carnot-like cycle](#b1-pi_b_001--when-does-a-reversible-engine-reach-carnot-efficiency)
   - [B2. Multilayer electromagnet](#b2-pi_b_002--how-strong-can-a-multilayer-electromagnet-be)
   - [C1. Leaning unicyclist](#c1-pi_c_001--the-leaning-unicyclist-as-an-extended-body)
   - [C2. Joule expansion](#c2-pi_c_002--free-expansion-of-a-slightly-sticky-gas)
   - [D1. Piston on a gas](#d1-pi_d_001--a-piston-that-shares-heat-with-the-gas)
   - [D2. Ring of minima](#d2-pi_d_002--orbits-near-a-ring-of-minima)
   - [E1. Tidal disruption](#e1-pi_e_001--why-a-shredded-star-fades-as-a-power-law)
   - [E2. White dwarf](#e2-pi_e_002--heavier-white-dwarfs-are-smaller)
5. [What the models did](#5-what-the-models-did)
6. [Glossary](#6-glossary)

---

## 1. What we are trying to test

Most physics problems in textbooks and benchmarks reward one skill: pick the
right formula and substitute numbers. "A pendulum is 2 m long; find its
period" is solved by remembering $T = 2\pi\sqrt{L/g}$.

Physicists spend much of their time on a different skill that comes *before*
any formula: deciding what matters. Which quantity is small? Which effect
can be ignored? Which approximation is safe here, and which one silently
throws away the answer? We call this the **physical decision**.

A good example is $\sin x \approx x$. For a pendulum swinging through a few
degrees it is excellent. But if the question is "how much longer is a gently
curved path than a straight one?", using $\sin x \approx x$ gives the answer
*zero*, which is wrong. The true difference is small but real, and it lives
in the next term of the expansion. Knowing that is the skill.

Every item in this set is chosen so that:

1. **There is a physical decision.** At least one step is a judgment about
   the physics, not algebra.
2. **Plugging in fails.** The "obvious" formula gives a wrong answer, or no
   answer. We record that wrong answer as the item's **trap**.
3. **The decision is checkable.** If you make the wrong decision, the formal
   statement we write is false. So a computer proof checker can tell whether
   the decision was right.
4. **The source is credible.** The problem and its solution come from experts
   (here, the olympiad committee), not from us.

---

## 2. How an item turns into a theorem

Each item has three parts:

- **A statement in words**, paraphrased from the source.
- **The expert solution**, with the physical decision marked.
- **A statement in Lean.** Lean is a programming language in which you can
  write mathematical theorems and proofs, and a small, trusted program (the
  "kernel") checks every step of a proof. If Lean accepts a proof, the
  theorem is true, given its assumptions.

A model being tested is given the Lean statement and must produce a Lean
proof. We never need to grade a proof by hand: it either checks or it does
not. To test the physics on its own, we also ask for the answer from the
plain-English problem, and read those answers by hand.

The most useful kind of Lean statement leaves the answer **blank**. Instead
of "prove that the coefficient is 2/3", it says "prove that there exists a
coefficient $c$ such that ...". To prove an existence statement in Lean you
must name the value, so the model has to supply $c = 2/3$ itself. If it
supplies the trap value $1/2$, the remaining claim is false and no proof
exists. A guard such as "$c \neq 0$" stops the model from proving something
trivial with $c = 0$.

The **assumptions** (hypotheses) of each theorem are general laws: the
conservation of energy, Newton's second law, the rule that physical formulas
must work in any units. We avoid putting the problem's key equation into the
assumptions, because then the physics is already done for the prover. (Two
of the ten pilot items break this rule, as explained below.)

---

## 3. The five categories

Each category is a different kind of physical decision.

### A. Leading-order expansion

**The move:** find the small quantity in the problem and expand in it, up to
the first term that actually contributes.

Many physical quantities are smooth functions of a small number $\varepsilon$
and can be written as a series, $f(\varepsilon) = f_0 + f_1 \varepsilon +
f_2 \varepsilon^2 + \dots$ (a **Taylor expansion**). Usually the first term
or two are enough. The decision is knowing *how far to go*: sometimes the
first terms cancel exactly, and the physics lives in a later term. Stopping
too early gives zero, or gives a "correction" of the wrong size.

**In Lean**, such claims are statements about how fast an error shrinks:
"the difference between the exact answer and $C\varepsilon^n$ becomes
negligible compared with $\varepsilon^n$ as $\varepsilon \to 0$". This is
written with *little-o* notation, $f = o(g)$, meaning $f/g \to 0$.

### B. Limiting regimes

**The move:** know what survives when a parameter goes to an extreme (very
hot or very cold, very near or very far, very long times), and state
precisely *when* a simplified description is valid.

The decision is usually about which of two competing quantities wins. In
Lean, these become statements about limits, often an "if and only if" that
pins down the exact condition.

### C. Model reduction (neglecting an effect)

**The move:** decide that a physical effect is small enough to drop, and
know what the first correction is when it is not quite negligible. Typical
examples: a spring's own mass, air resistance, the recoil of a gun, or
treating an extended object as a single point.

A simplified model ("the rider is a point", "the gas is ideal") is usually
right in some limit. The decision is recognizing which effect is being
dropped and computing its leading influence correctly.

### D. Linearization and stability

**The move:** find the equilibrium (the state where nothing changes), then
look at small departures from it. For a small displacement $x$, almost any
restoring force is approximately proportional to $x$, $F \approx -\kappa x$.
That gives simple harmonic motion with angular frequency
$\omega = \sqrt{\kappa / m}$.

The decision is figuring out what $\kappa$ really is. Hidden contributions
(heat flowing into another part of the system, a force that vanishes at
equilibrium) change the answer.

### E. Scaling and dimensional analysis

**The move:** get the *form* of an answer (how one quantity scales with
another) before, or instead of, solving the full problem.

Physical laws can't depend on our choice of units. That is a surprisingly
strong constraint: if a pressure can depend only on a few quantities, there
is often just one combination of them with the units of pressure. The answer
is a power law, $y \propto x^n$, and the exponent $n$ is what we ask for.

---

## 4. The ten problems

Each problem follows the same structure: the setup, the background you need,
the solution with the physical decision marked, the trap, and how the Lean
version captures the decision.

---

### A1 (`PI_A_001`) — How much longer is an arc than its chord?

*USAPhO 2023, problem B3, part c.i. Category A.*

**Setup.** A particle with a tiny electric charge travels from a supernova to
Earth, a straight-line distance $d$. Space has a weak uniform magnetic field,
perpendicular to the line of sight. The field bends the particle's path into
an arc of a huge circle of radius $r$, much larger than $d$. How much longer
is the curved path, of length $\ell$, than the straight line?

(Physically, this is about timing. Light travels straight, while the charged
particle travels the slightly longer arc. If the extra length is measurable,
the particle arrives later, and the delay reveals its charge.)

**Background.**

- *Why the path is a circle:* a magnetic field pushes a moving charge
  sideways, at right angles to its velocity. A force always at right angles
  to the motion changes the direction but not the speed, which produces
  circular motion.
- *Arc and chord:* on a circle of radius $r$, an arc of length $\ell$ spans
  an angle $\theta = \ell / r$ (in radians). The straight line joining its
  ends, the **chord**, has length $d = 2r \sin(\theta/2) = 2r\sin(\ell/2r)$.
  You can see this by splitting the triangle from the centre into two right
  triangles.
- *Taylor series of sine:* for small $x$,
  $\sin x = x - \frac{x^3}{6} + \frac{x^5}{120} - \dots$

**Solution.** Let $x = \ell / 2r$, which is tiny. Then

$$d = 2r \sin x = 2r\left(x - \frac{x^3}{6} + \dots\right) = \ell - \frac{\ell^3}{24 r^2} + \dots$$

**[Physical decision]** The first-order term, $2r \cdot x$, is *exactly*
$\ell$. So $\ell - d$ is zero at first order, and the whole effect comes from
the cubic term:

$$\ell - d \approx \frac{\ell^3}{24 r^2} \approx \frac{d^3}{24 r^2}.$$

(Replacing $\ell$ by $d$ on the right is fine, because they differ only at a
higher order.) The error in this approximation is about
$\ell^5 / (1920\, r^4)$, which is far smaller still.

**The trap.** "The angle is small, so $\sin x \approx x$." That gives
$d = \ell$: no extra length and no delay. It isn't wrong as an
approximation of $d$. It is wrong as an approximation of $\ell - d$, because
it throws away exactly the term that contains the answer.

**In Lean.** The theorem says: there exist a nonzero coefficient $C$ and a
whole number $n$ such that $\ell - d - C\ell^n$ is negligible compared with
$\ell^n$ as $\ell \to 0$. The prover has to supply $C = 1/(24r^2)$ and
$n = 3$. With $n = 1$ or $2$ no nonzero $C$ works, because $\ell - d$ is much
smaller than $\ell$ or $\ell^2$.

---

### A2 (`PI_A_002`) — The first quantum correction to a solid's heat capacity

*USAPhO 2024, problem B2, part a. Category A.*

**Setup.** A crystal of $N$ atoms is modelled as $3N$ independent vibrating
springs (each atom can vibrate in 3 directions). Quantum mechanics says each
vibration can only hold energy in packets ("quanta") of size $\hbar\omega$,
where $\omega$ is the vibration frequency and $\hbar$ is Planck's constant
divided by $2\pi$. With $m$ quanta in total, the energy is
$E = \hbar\omega\, m$. Find how the solid's heat capacity departs from its
classical value at high temperature.

**Background.**

- *Heat capacity* $C$ is how much energy it takes to raise the temperature
  by one degree: $C = dE/dT$.
- *The classical answer (Dulong–Petit law):* each vibration direction of
  each atom holds an average energy $k_B T$, where $k_B$ is Boltzmann's
  constant. So $E = 3N k_B T$ and $C = 3Nk_B$. This is the high-temperature
  value for many solids.
- *Entropy and temperature:* entropy $S$ measures how many microscopic
  arrangements are consistent with what we see. Temperature is defined
  through it by $dE = T\, dS$: adding energy $dE$ raises the entropy by
  $dE/T$. For this model, counting the ways to share $m$ quanta among $3N$
  springs gives $S/k_B = (3N+m)\ln(3N+m) - m\ln m$ (up to a constant).

**Solution.** Apply $dE = T\,dS$ with $E = \hbar\omega m$. Differentiating
the entropy with respect to $m$:

$$\frac{dS}{dm} = k_B \ln\frac{3N+m}{m}, \qquad \hbar\omega = T\frac{dS}{dm} = k_B T \ln\frac{3N+m}{m}.$$

Writing $\alpha = \hbar\omega / k_B T$ and solving for $m$:

$$m = \frac{3N}{e^\alpha - 1}.$$

High temperature means $\alpha \ll 1$: the energy packets are small compared
with the typical thermal energy.

**[Physical decision]** We need to expand $1/(e^\alpha - 1)$ for small
$\alpha$, and the question is how far. Its expansion is

$$\frac{1}{e^\alpha - 1} = \frac{1}{\alpha} - \frac{1}{2} + \frac{\alpha}{12} - \dots$$

The leading term $1/\alpha$ is *large*. When we multiply by $\hbar\omega$ to
get the energy, each term moves up a power of $\alpha$:

$$E = \hbar\omega\, m = 3N\left(k_B T - \frac{\hbar\omega}{2} + \frac{(\hbar\omega)^2}{12\, k_B T} - \dots\right).$$

The first term is the classical result. The second is a constant, which
doesn't affect the heat capacity because it doesn't change with $T$. So the
first term that changes the heat capacity is the *third* one, which came
from the second-order term of the expansion. Differentiating with respect to
$T$:

$$C = \frac{dE}{dT} = 3Nk_B\left(1 - \frac{\alpha^2}{12}\right).$$

So the heat capacity falls slightly below the classical value, by a factor
$1 + b\,\alpha^n$ with $b = -1/12$ and $n = 2$.

**The trap.** Expanding only to $m \approx 3N(1/\alpha - 1/2)$ gives
$E = 3N(k_BT - \hbar\omega/2)$ and $C = 3Nk_B$ *exactly*: no correction at
all. Quoting Dulong–Petit directly does the same. The correction is hidden
one order further down, because the leading term carried a $1/\alpha$.

**In Lean.** The hypotheses are the entropy formula and the relation
$dE = T\,dS$ (written as a derivative condition), not the formula for $m$. The
theorem says that there exist $b \neq 0$ and $n > 0$ such that
$C/(3Nk_B) - 1 - b\,\alpha^n$ is negligible compared with $\alpha^n$ as the
temperature goes to infinity. The prover must find $b = -1/12$ and $n = 2$.

---

### B1 (`PI_B_001`) — When does a reversible engine reach Carnot efficiency?

*USAPhO 2023, problem A3, part a. Category B.*

**Setup.** One mole of a monatomic ideal gas (like helium) runs through a
four-step cycle between a cold temperature $T_0$ and a hot temperature
$(1+\beta)T_0$:

1. Heat it at constant pressure $P_0$ until it reaches $(1+\beta)T_0$.
2. Let it expand at constant temperature until its pressure has dropped to
   $P_0/\alpha$.
3. Cool it at constant pressure back to $T_0$.
4. Compress it at constant temperature back to $P_0$.

For which values of $\alpha$ and $\beta$ does this engine's efficiency
approach the best possible efficiency for engines running between these two
temperatures?

**Background.**

- *Heat engines:* an engine takes heat in, turns some of it into work, and
  dumps the rest. Its **efficiency** is $\eta = W / Q_{in}$, work out over
  heat in.
- *The Carnot limit:* no engine running between a hot temperature $T_H$ and
  a cold temperature $T_C$ can beat $\eta_C = 1 - T_C/T_H$. Here
  $\eta_C = 1 - 1/(1+\beta) = \beta/(1+\beta)$. Only an idealized engine
  that takes in *all* its heat at $T_H$ and dumps *all* of it at $T_C$
  reaches this limit.
- *Ideal gas facts:* $PV = RT$ for one mole ($R$ is the gas constant).
  Heating at constant pressure costs $\frac{5}{2}R$ per degree for a
  monatomic gas. Expanding at constant temperature from pressure $P_1$ to
  $P_2$ takes in heat $RT\ln(P_1/P_2)$, and that heat all becomes work.
- *Reversible* means the process can be run backwards with no losses: no
  friction, no sudden jumps.

**Solution.** Write $P_0V_0 = RT_0$. The heats in each step are:

| Step | Heat | Value |
|---|---|---|
| 1. Heat at constant $P$ | in | $Q_1 = \frac{5}{2}\beta P_0 V_0$ |
| 2. Expand at $(1+\beta)T_0$ | in | $Q_2 = (1+\beta)P_0V_0\ln\alpha$ |
| 3. Cool at constant $P$ | out | $\frac{5}{2}\beta P_0V_0$ |
| 4. Compress at $T_0$ | out | $P_0V_0\ln\alpha$ |

The net work is the heat in minus the heat out:
$W = \beta P_0V_0 \ln \alpha$. The efficiency is $W/(Q_1 + Q_2)$, and
comparing with Carnot gives the clean result

$$\frac{\eta}{\eta_C} = \frac{1}{1 + \frac{5}{2}\cdot\frac{\beta}{(1+\beta)\ln\alpha}} = \frac{1}{1 + Q_1/Q_2}.$$

**[Physical decision]** The engine is reversible, but that alone isn't
enough to reach Carnot. Carnot efficiency requires that essentially all the
heat enters at the hottest temperature. Here, $Q_2$ enters at the top
temperature, but $Q_1$ enters while the gas is still warming up, at lower
temperatures. So the engine approaches Carnot exactly when $Q_1$ becomes
negligible next to $Q_2$:

$$\frac{\beta}{(1+\beta)\ln\alpha} \to 0.$$

This condition is both necessary and sufficient, since the formula above
depends on nothing else.

**A note on the official answer.** The official solution also requires the
heat *dumped* at the wrong temperature to be negligible, and concludes the
stricter condition $\beta \ll \ln\alpha$. That condition is sufficient but
not necessary. For example, take $\beta = n^2$ and $\ln\alpha = n$ with $n$
growing. Then $\beta/\ln\alpha = n \to \infty$, so the official condition
fails, but $\beta/((1+\beta)\ln\alpha) = n/(1+n^2) \to 0$, so the engine
does approach Carnot efficiency. Writing the claim as a precise "if and only
if" theorem is what exposed this.

**The trap.** "It's reversible, and reversible engines are as efficient as
possible, so it's always Carnot." Reversible engines are optimal only if they
exchange heat at the two extreme temperatures. This cycle doesn't.

**In Lean.** The theorem says that the efficiency ratio tends to 1 *if and
only if* $\beta/((1+\beta)\ln\alpha)$ tends to 0, along any way of sending
$(\alpha, \beta)$ to a limit. The prover has to establish the efficiency
formula and both directions of the equivalence.

---

### B2 (`PI_B_002`) — How strong can a multilayer electromagnet be?

*USAPhO 2025, problem A3, parts b and d. Category B.*

**Setup.** A solenoid (a coil that makes a uniform magnetic field inside it)
is wound from many layers of round wire of diameter $t$, filling the space
between an inner radius $a$ and an outer radius $b$. The wire breaks if
stretched beyond its tensile strength $\sigma$ (force per unit
cross-sectional area). The current in each layer is tuned so all layers are
equally close to breaking. What is the strongest field $B$ the magnet can
reach?

**Background.**

- *Magnetic pressure:* a magnetic field pushes outward on the coil that
  creates it, like gas inflating a balloon. The pressure is $B^2/2\mu_0$,
  where $\mu_0$ is a constant of nature.
- *Hoop stress:* a ring of radius $r$ under outward pressure $p$ is
  stretched. For a strip of ring of axial width $w$, the tension is
  $p \cdot r \cdot w$ (the same reason a balloon's skin is under tension).
- Inside a solenoid the field is uniform; outside it, the field is zero.
  Each layer of current adds a step to the field.

**Solution.** Number the layers from the outside in. Let $B_k$ be the field
just inside layer $k$ and $B_{k-1}$ the field just outside it.

**[Physical decision]** Each layer only has to hold back the *difference* in
magnetic pressure across it, $(B_k^2 - B_{k-1}^2)/2\mu_0$, not the full
pressure $B^2/2\mu_0$. The layers outside it carry the rest. (Equivalently:
the current in a layer sits in the average of the fields on its two sides.)

Each wire, of cross-sectional area $\pi t^2/4$, can carry tension up to
$\sigma\pi t^2/4$. Balancing the hoop tension of a strip one wire wide
($w = t$) at radius $r_k$:

$$\frac{B_k^2 - B_{k-1}^2}{2\mu_0}\, r_k\, t \le \sigma \frac{\pi t^2}{4} \quad\Longrightarrow\quad B_k^2 - B_{k-1}^2 \le \frac{\pi}{2}\sigma\mu_0 \frac{t}{r_k}.$$

Adding this up over all layers, the left side telescopes: everything cancels
except the field in the middle (and the field outside, which is zero):

$$B^2 \le \frac{\pi}{2}\sigma\mu_0 \sum_k \frac{t}{r_k}.$$

For thin wire, the sum is a Riemann sum (layer spacing $t$, function $1/r$),
so it becomes an integral:

$$\sum_k \frac{t}{r_k} \to \int_a^b \frac{dr}{r} = \ln\frac{b}{a}, \qquad B_{\max}^2 = \frac{\pi}{2}\sigma\mu_0\ln\frac{b}{a}.$$

So the achievable field grows only logarithmically with the thickness of the
winding: doubling the outer radius adds a fixed amount to $B^2$, however big
the magnet already is.

**The trap.** Treating the whole winding as one thick coil, with the full
pressure on every wire, gives a field that grows like a power of the
thickness. That is far too optimistic.

**In Lean, and a caveat.** The theorem gives, as hypotheses, how each layer's
current steps up the field, and each layer's stress limit with its current
sitting in the *average* of the fields on its two sides. It asks for the sum
bound on $B^2$. (The logarithmic limit is in the written solution, not the
theorem.) The stress hypothesis already contains the physical decision ("each
layer bears only the jump"), so what remains is a telescoping sum: pure
mathematics. This is one of the two items the review marked **revise**:
the physics is in the hypotheses.

---

### C1 (`PI_C_001`) — The leaning unicyclist as an extended body

*USAPhO 2014, problem A1. Category C.*

**Setup.** A unicyclist rides around a circular track of radius $R$,
measured to the point where the wheel touches the ground, leaning inward at
angle $\theta$ from vertical. If the rider is treated as a point, the
required angular speed satisfies $\omega^2 = (g/R)\tan\theta$. Now treat the
rider more realistically, as a uniform rod of height $h$ that isn't tiny
compared with $R$. How does $\omega$ change?

**Background.**

- *Rotating frame and centrifugal force:* it is easiest to sit on the rider,
  where everything is stationary. In a rotating frame, every bit of mass
  feels an outward "centrifugal" force $dm\,\omega^2 s$, where $s$ is its
  distance from the rotation axis. This is a bookkeeping device that makes
  Newton's laws work in the rotating frame.
- *Torque:* a force's tendency to rotate something about a pivot. It is the
  force times its lever arm: the perpendicular distance from the pivot to the
  force's line of action. A body stays balanced when the torques cancel.

**Solution.** Take the pivot at the wheel's contact point. Gravity pulls each
bit of the rod down and tries to tip the rider further inward; the
centrifugal force pushes each bit outward and tries to tip the rider upright.
Balance means these torques cancel.

A bit of rod at distance $s$ along the rod (from the bottom) has mass
$dm = (m/h)\,ds$. It sits at height $s\cos\theta$, and at horizontal distance
$R - s\sin\theta$ from the axis (the rider leans inward, so higher parts are
closer to the centre).

**[Physical decision]** The centrifugal force is proportional to distance
from the axis, so it is *not* the same on every part of the rider. You can't
just put the total centrifugal force at the centre of mass, as you can with
gravity. You have to add it up bit by bit:

$$\tau_{\text{cf}} = \int_0^h \frac{m}{h}\,\omega^2 (R - s\sin\theta)\,(s\cos\theta)\,ds = m\omega^2 h\cos\theta\left(\frac{R}{2} - \frac{h\sin\theta}{3}\right).$$

Gravity *is* uniform, so its torque is just $mg$ at the centre of mass, with
lever arm $(h/2)\sin\theta$. Setting the two equal:

$$\omega^2 = \frac{(g/R)\tan\theta}{1 - \frac{2}{3}\frac{h}{R}\sin\theta}.$$

So the coefficient is $c = 2/3$. As $h/R \to 0$, this goes back to the point
model.

**The trap.** Putting the total centrifugal force $m\omega^2(R -
\frac{h}{2}\sin\theta)$ at the centre of mass, height $h/2$, gives the same
form with $c = 1/2$. It looks reasonable and is wrong, because the force
grows with distance from the axis while the lever arm grows with height, and
the product isn't linear.

**In Lean, and a caveat.** The Lean statement gives the torque balance
(including the integral) as a hypothesis. That integral is exactly the
physical decision. So the prover only has to do calculus. Like B2, this item
is marked **revise**.

---

### C2 (`PI_C_002`) — Free expansion of a slightly sticky gas

*USAPhO 2020, problem B3, parts d–f. Category C.*

**Setup.** A gas of $N$ atoms sits in volume $V$ at temperature $T$ inside an
insulated box. A partition is removed and the gas rushes into an equal empty
volume next to it, doubling its volume. The atoms attract each other weakly.
What is the final temperature? How much does the entropy increase?

**Background.**

- *Ideal gas:* a gas whose atoms don't interact. Its energy depends only on
  temperature: $E = \frac{3}{2}Nk_BT$ for single atoms.
- *Free (Joule) expansion:* the gas expands into vacuum, pushing against
  nothing, so it does no work. The box is insulated, so no heat flows. So
  the total energy is unchanged.
- *Mean-field energy:* if each atom feels a weak average attraction from all
  the others, proportional to how crowded they are ($N/V$), the total
  attraction energy is $-aN^2/V$, where $a$ measures the stickiness. (The
  factor counting each pair once, not twice, is already absorbed into $a$.)
  So $E = \frac{3}{2}Nk_BT - \frac{aN^2}{V}$.

**Solution.** **[Physical decision]** The ideal-gas model is a *reduced
model*: it predicts no temperature change at all in free expansion. The
leading effect of the attraction is the mean-field energy term, and that is
what we must keep. Energy is conserved:

$$\frac{3}{2}Nk_BT' - \frac{aN^2}{2V} = \frac{3}{2}Nk_BT - \frac{aN^2}{V}.$$

When the volume doubles, the atoms are farther apart, so the (negative)
attraction energy shrinks in size. That energy has to come from somewhere,
and it comes from the atoms' motion. The gas cools:

$$T' = T - \frac{aN}{3k_BV}, \qquad \text{i.e.}\quad \frac{T'-T}{T} = -\frac{1}{3}\varepsilon, \quad \varepsilon = \frac{aN}{Vk_BT}.$$

Here $\varepsilon$ is the ratio of attraction energy to thermal energy per
atom, the small parameter. The coefficient is $c = 1/3$.

For the entropy, the gas gains $Nk_B\ln 2$ from having twice the room (as an
ideal gas would), and loses a little from cooling:

$$\Delta S \approx Nk_B\ln 2 - \frac{aN^2}{2VT}.$$

**The trap.** Using the ideal gas gives $\Delta T = 0$. Forgetting the
pair-counting factor in the attraction energy doubles the cooling.

**In Lean.** The theorem defines the mean-field energy and says: there is a
coefficient $c$ such that, whenever the energy at $(T', 2V)$ equals the energy
at $(T, V)$, we have $T' = T - c\,aN/(k_BV)$. The prover must find $c = 1/3$.
(The entropy part is not in the theorem yet; the review marked it for
revision.)

---

### D1 (`PI_D_001`) — A piston that shares heat with the gas

*USAPhO 2024, problem B2, part b. Category D.*

**Setup.** A vertical cylinder in vacuum holds a monatomic gas under a heavy
piston made of a solid. The gas and the piston contain the same number of
atoms. They stay at the same temperature as each other, but exchange no heat
with anything else. At rest, the gas column has height $h$. Nudge the piston:
at what angular frequency does it bob up and down?

**Background.**

- *Small oscillations:* near equilibrium, the net force on the piston is
  approximately proportional to its displacement $z$: $F \approx -\kappa z$.
  Then it oscillates with $\omega^2 = \kappa/M$.
- *Adiabatic compression:* if a gas is squeezed without heat leaving the
  system, it heats up, and its pressure rises faster than if its temperature
  stayed fixed. For an ideal gas this is described by $PV^\gamma =
  \text{constant}$, where $\gamma$ (the "adiabatic index") is the ratio of
  heat capacities at constant pressure and at constant volume. For a
  monatomic gas, $\gamma = 5/3$.
- *Heat capacity of a solid:* by the Dulong–Petit law (see A2), a solid
  stores $3k_B$ per atom per degree, twice what a monatomic gas stores
  ($\frac{3}{2}k_B$ per atom).

**Solution.** When the piston moves down, it squeezes the gas, which heats
up.

**[Physical decision]** Here the gas immediately shares that heat with the
piston, which soaks it up without doing any work (it is a solid; its volume
doesn't change). So the "system" that is insulated is gas plus piston, and
its heat capacity is the gas's plus the piston's. With $n$ moles of each:

$$\left(\tfrac{3}{2}nR + 3nR\right)dT = -P\,dV.$$

Combined with $PV = nRT$, this is an adiabatic process with an *effective*
adiabatic index

$$\gamma = \frac{C_P}{C_V} = \frac{\tfrac{5}{2} + 3}{\tfrac{3}{2} + 3} = \frac{11}{9}.$$

Since the piston absorbs some of the heat, the gas heats up less, and so it
pushes back less hard than a lone gas would. Linearizing the force about
equilibrium (with $V = Az$ and $P \propto V^{-\gamma}$):

$$F \approx -\frac{\gamma P_0 A}{h}\,z.$$

At equilibrium the gas holds up the piston, $P_0A = Mg$. So

$$\omega^2 = \frac{\gamma g}{h} = \frac{11\,g}{9\,h}.$$

**The trap.** Using the textbook monatomic value $\gamma = 5/3$ gives
$\omega^2 = 5g/3h$, too stiff, because it forgets the heat stored in the
piston.

**In Lean, and a note.** The theorem states the energy balance (first law,
with both heat capacities) and the equilibrium condition, and asks for the
$\gamma$ with $\omega^2 = \gamma g/h$. The prover must linearize and find
$\gamma = 11/9$. A stricter version would let the prover decide which heat
capacities enter. As written, the hypothesis already says the piston's heat
capacity counts.

---

### D2 (`PI_D_002`) — Orbits near a ring of minima

*USAPhO 2023, problem A2, part b. Category D.*

**Setup.** A charged particle moves in a horizontal plane above a large
charge of the opposite sign. Close to the centre, it feels a pull back
towards the centre proportional to its distance $r$, like a spring: the
potential energy is $V = \frac{k}{2}r^2$. In such a potential, *every*
circular orbit has the same angular frequency $\omega_c = \sqrt{k/m}$. Now
fix a second charge, of the same sign as the particle, at the centre. It
pushes the particle away. Find the frequency of a circular orbit just outside
the new resting radius $r_0$.

**Background.**

- *Potential energy and force:* the force is minus the slope of the
  potential, $F = -dV/dr$. A minimum of $V$ is a resting point.
- *Circular orbits:* moving in a circle of radius $r$ at angular frequency
  $\Omega$ needs a net inward force $m\Omega^2 r$.
- *Coulomb repulsion:* the central charge adds potential energy $\kappa/r$,
  which grows as the particle gets close.

**Solution.** The total potential is $V(r) = \frac{k}{2}r^2 + \frac{\kappa}{r}$.
The spring term pulls in, the repulsion pushes out, and they balance at
$r_0 = (\kappa/k)^{1/3}$. Because the problem is symmetric under rotation,
the minimum isn't a point but a whole **ring** of radius $r_0$.

The inward force needed for a circular orbit must come from $dV/dr$:

$$m\Omega^2 r = V'(r).$$

**[Physical decision]** On the ring itself, $V'(r_0) = 0$: there is no net
force at all, so a particle there just sits still ($\Omega = 0$). Slightly
outside, at $r_0 + \delta$, the only inward force is the small restoring
force from being displaced off the ring. That force is proportional to
$\delta$, with stiffness $V''(r_0) = k + 2\kappa/r_0^3 = 3k$:

$$V'(r_0 + \delta) \approx 3k\,\delta.$$

So

$$\Omega^2 \approx \frac{3k\delta}{m r_0}, \qquad \Omega \approx \sqrt{3}\,\omega_c\sqrt{\frac{\delta}{r_0}}.$$

The orbital frequency goes to zero like $\sqrt\delta$. This is very different
from the harmonic case, where every orbit had frequency $\omega_c$. It is an
example of a "soft mode": motion along a direction in which the potential is
flat costs almost nothing.

**The trap.** Reusing $\Omega = \omega_c$ from the pure spring potential, or
using $\sqrt{3}\,\omega_c$, which is the frequency of *radial* wobbles about
the ring, not of circular motion around it.

**In Lean.** The hypotheses are only Newton's law for circular orbits and the
location of the minimum. The theorem says there exist constants $c > 0$ and
$p > 0$ such that $\Omega - c\,\omega_c(\delta/r_0)^p$ is negligible compared
with $(\delta/r_0)^p$ as $\delta \to 0$. The prover must find $c = \sqrt3$ and
$p = 1/2$.

---

### E1 (`PI_E_001`) — Why a shredded star fades as a power law

*USAPhO 2025, problem A2, part g. Category E.*

**Setup.** A star wanders too close to a supermassive black hole of mass $M$
and is torn apart. About half the debris stays bound to the black hole, on
long elliptical orbits. Each piece falls back after one orbit and is
swallowed, giving off light. The pieces' orbital energies (per unit mass) are
spread evenly between some most-bound value $\varepsilon_{\min} < 0$ and $0$.
Show that the brightness eventually fades as a power law $t^{-n}$, and find
$n$.

**Background.**

- *Orbital energy:* a bound orbit has negative total energy. The more
  negative, the more tightly bound. For an ellipse with semi-major axis $a$
  (half the longest diameter), the energy per unit mass is
  $\varepsilon = -GM/(2a)$, where $G$ is Newton's gravitational constant.
- *Kepler's third law:* the orbital period is $T = 2\pi\sqrt{a^3/GM}$.
  Bigger orbits take longer, and the period grows like $a^{3/2}$.

**Solution.** **[Physical decision]** The key is to connect the even spread in
*energy* to a spread in *return times*, using Kepler's third law. Combining
the two formulas, $a \propto 1/|\varepsilon|$ and $T \propto a^{3/2}$, so

$$T \propto |\varepsilon|^{-3/2}, \qquad \text{i.e.}\quad |\varepsilon| \propto T^{-2/3}.$$

By time $t$, every piece with period at most $t$ has come back. Those are the
pieces with energy between $\varepsilon_{\min}$ and $\varepsilon(t)$, the
energy whose period is exactly $t$. Since energies are spread evenly with
density $\mu$, the mass returned is
$M_{\text{ret}}(t) = \mu\,(\varepsilon(t) - \varepsilon_{\min})$. The
brightness follows the rate of return:

$$\frac{dM_{\text{ret}}}{dt} = \mu\frac{d\varepsilon}{dt} \propto \frac{d}{dt}\left(-t^{-2/3}\right) \propto t^{-5/3}.$$

So $n = 5/3$. This fading law is actually used by astronomers to identify
tidal disruption events.

**The trap.** Saying the brightness follows the energy-period relation
directly ($t^{-2/3}$) forgets that brightness is a *rate*, a derivative.
Assuming the semi-major axis, rather than the energy, is evenly spread gives
yet another exponent.

**In Lean.** The theorem defines the Kepler period and the mass returned by
time $t$, and asks to show that this mass has derivative $C\,t^{-n}$ for some
$n$. The prover must find $n = 5/3$ and carry out the derivative.

---

### E2 (`PI_E_002`) — Heavier white dwarfs are smaller

*USAPhO 2024, problem A2, part c. Category E.*

**Setup.** A white dwarf is the dense remnant of a star like the Sun. It no
longer burns fuel; what holds it up against its own gravity is the pressure
of its electrons, which quantum mechanics forbids from being squeezed into
the same state. For a star of mass $M$ and radius $R$ with roughly uniform
density $\rho \sim M/R^3$, this pressure is $P = K\rho^{5/3}$. How does the
radius depend on the mass, $R \propto M^n$?

**Background.**

- *Dimensional analysis:* every physical quantity has units built from mass
  (M), length (L) and time (T). An equation relating physical quantities must
  have the same units on both sides, in any unit system. If you know which
  quantities an answer can depend on, this often fixes the answer up to a
  number.
- *Units involved:* pressure is force per area, M L$^{-1}$ T$^{-2}$. Newton's
  constant $G$ has units L$^3$ M$^{-1}$ T$^{-2}$.
- *Hydrostatic balance:* inside a star, the pressure at each depth has to
  support the weight of the layers above it.

**Solution.** **[Physical decision]** We don't need to solve the star's
structure in detail. The pressure needed at the centre to hold the star up
can depend only on $G$, $M$ and $R$. Try $P \sim G^x M^y R^z$ and match
units:

- time: $-2x = -2$, so $x = 1$;
- mass: $-x + y = 1$, so $y = 2$;
- length: $3x + z = -1$, so $z = -4$.

So the only possibility is

$$P_{\text{needed}} \sim \frac{GM^2}{R^4}.$$

The electrons supply

$$P_{\text{supplied}} = K\left(\frac{M}{R^3}\right)^{5/3} \propto \frac{M^{5/3}}{R^5}.$$

Setting them equal: $M^2/R^4 \propto M^{5/3}/R^5$, so $R \propto M^{-1/3}$.
So $n = -1/3$: **a heavier white dwarf is smaller.** Adding mass increases
gravity faster than it increases the electron pressure, so the star has to
shrink to a higher density to support itself.

**The trap.** Ordinary experience says more stuff takes more room: at fixed
density, $R \propto M^{1/3}$. White dwarfs do the opposite.

**In Lean.** We don't give the formula $GM^2/R^4$. Instead, the hypothesis
says the central pressure is *dimensionally covariant*: if you change the
units of mass, length and time, it transforms the way a pressure must. The
prover has to derive the scaling from that, then balance it against the
electron pressure and find $n = -1/3$. This is the cleanest example of a
hypothesis that is a general principle, not a problem-specific formula.

---

## 5. What the models did

**A correction first.** In the first runs, 8 of the 10 prompts contained the
expected answer in a Lean comment, by mistake. So those runs can't show whether
a model found the physics itself. The physics results below come from new runs
with no answer in the prompt. Details are in `docs/PILOT_02.md`.

Two models were tested: Qwen3.8-27B (an open-weights model, run on our own GPUs)
and Claude Haiku 5.5 (a commercial model, through an API). All grading used
Lean 4.34 with current Mathlib.

**Physics on its own.** Each model got only the plain-English problem and gave a
final answer, 8 attempts per problem. B1 and B2 aren't included, because they
have no single value to check.

| Problem | Qwen, no thinking phase | Qwen, thinking | Haiku |
|---|---|---|---|
| A1 Arc vs chord | 8 | 8 | 8 |
| A2 Einstein solid | 8 | 8 | 8 |
| C1 Unicyclist | 1 (5 gave the trap value) | 8 | 8 |
| C2 Joule expansion | 8 | 8 | 8 |
| D1 Piston | 4 (4 gave the trap value) | 8 | 8 |
| D2 Ring of minima | 6 (2 gave the trap value) | 8 | 8 |
| E1 Tidal disruption | 8 | 8 | 8 |
| E2 White dwarf | 5 (2 gave the trap value) | 8 | 8 |
| **Total of 64** | **48** | **64** | **64** |

**Lean proofs.** Haiku, with no answer in the prompt, first got one attempt, 4 per
problem. Each failed attempt then went back with Lean's error messages, for up to
3 rounds.

| Problem | One attempt (of 4) | After feedback (of 4) |
|---|---|---|
| A1 Arc vs chord | 0 | 4 |
| A2 Einstein solid | 0 | 1, with 3 stopped early |
| B1 Carnot-like cycle | 4 | 4 |
| B2 Electromagnet | 4 | 4 |
| C1 Unicyclist | 3 | 4 |
| C2 Joule expansion | 3 | 4 |
| D1 Piston | 1 | 4 |
| D2 Ring of minima | 3 | 4 |
| E1 Tidal disruption | 3 | 4 |
| E2 White dwarf | 4 | 4 |
| **Total of 40** | **25** | **37** |

Qwen passed 0 of its 74 completed one-attempt samples, on prompts that showed the
comments. With feedback, it passes 4 of the 20 samples tested, which had all failed
before, and adding worked examples also gives 4 of 20. 6 of those 8 passes are on C2.

A trap value doesn't always mean falling for the trap. One E2 answer we read had the
right physics, then an algebra slip that happened to give the trap's value.

Five patterns stand out:

- **The traps are real, but they only caught Qwen without its thinking phase.** It
  often used $\gamma = 5/3$ on the piston and $c = 1/2$ on the
  unicyclist. With thinking, Qwen got everything right, and so did Haiku.
- **What separates the models is Lean.** Qwen gets the physics right when it
  can think, but its one-shot proofs don't compile.
- **Feedback fixed Lean, not physics.** Haiku named the correct value in its first
  attempt in 29 of 32 samples on these problems, even when the proof didn't compile.
  The other 3 gave no answer.
- **Difficulty follows the formal mathematics.** The arc-vs-chord problem, the
  easiest physics in the set, was never proved in one shot, because it needs
  delicate Taylor estimates in Lean. With feedback, Haiku proved it every time.
- **A proof is not the same as a physical decision.** A passing proof names a
  correct value, but that value can sometimes be worked out from the Lean
  statement by mathematics alone.

The lesson for the next 40 problems: as posed, these ten are within reach of
current models when they can think. The statements also give away part of the
decision, for example by saying "to leading nontrivial order". To measure physical
judgment, we need harder decisions and fewer hints.

---

## 6. Glossary

**Adiabatic.** A process in which no heat enters or leaves the system. A gas
compressed adiabatically heats up.

**Adiabatic index ($\gamma$).** The ratio of a gas's heat capacity at
constant pressure to that at constant volume. It controls how steeply
pressure rises when a gas is squeezed without heat loss ($PV^\gamma$ stays
constant). For a monatomic gas, $\gamma = 5/3$.

**Carnot efficiency.** The maximum possible efficiency of any engine running
between a hot temperature $T_H$ and a cold one $T_C$: $1 - T_C/T_H$.

**Centrifugal force.** The apparent outward force felt in a rotating frame,
$m\omega^2 s$ at distance $s$ from the axis. It is a bookkeeping device that
lets you use Newton's laws while rotating along with an object.

**Chord.** The straight line between two points on a circle.

**Degenerate electrons.** Electrons packed so densely that quantum mechanics
(the Pauli exclusion principle: no two electrons in the same state) forces
many of them to move fast, which creates pressure even at low temperature.

**Dimensional analysis.** Using the requirement that equations have the same
units on both sides to work out how an answer depends on its inputs.

**Dulong–Petit law.** At high temperature, a solid's heat capacity is about
$3k_B$ per atom.

**Entropy ($S$).** A measure of the number of microscopic arrangements
consistent with a system's large-scale state. It connects to temperature by
$dE = T\,dS$.

**Equilibrium.** A state in which the forces balance and nothing changes.

**Heat capacity.** The energy needed to raise a system's temperature by one
degree, $dE/dT$.

**Hoop stress.** The tension in the wall of a ring or cylinder that is
pushed outward from inside.

**Ideal gas.** A gas whose particles don't interact, obeying $PV = Nk_BT$.

**Isobaric / isothermal.** At constant pressure / at constant temperature.

**Kepler's third law.** An orbit's period squared is proportional to its
semi-major axis cubed: $T = 2\pi\sqrt{a^3/GM}$.

**Lean.** A programming language and proof assistant: you write a theorem and
a proof, and Lean's kernel checks every step.

**Linearization.** Approximating a function near a point by its tangent
line. For forces near equilibrium, this gives $F \approx -\kappa x$.

**Little-o ($f = o(g)$).** "$f$ is negligible compared with $g$": $f/g \to 0$
in the limit being considered.

**Magnetic pressure.** The outward push a magnetic field exerts on the
currents that create it, $B^2/2\mu_0$.

**Mean field.** An approximation in which each particle feels the *average*
effect of all the others, instead of tracking every pair individually.

**Monatomic gas.** A gas of single atoms (helium, argon), as opposed to
molecules. It stores $\frac{3}{2}k_B$ of energy per atom per degree.

**Plug-in trap.** The answer a solver gets by substituting into the obvious
formula without making the physical decision. Each item records one.

**Potential energy ($V$).** Stored energy that depends on position. The force
is minus its slope, $F = -dV/dr$.

**Reversible process.** One that can be run backwards with no net change to
the universe: no friction, no sudden jumps, no heat flowing across a
temperature difference.

**Riemann sum.** A sum of many thin slices, $\sum f(x_k)\,\Delta x$, which
becomes the integral $\int f\,dx$ as the slices get thinner.

**Semi-major axis.** Half the longest diameter of an ellipse; it sets an
orbit's size.

**Soft mode.** A motion along a direction in which the potential energy is
flat or nearly flat, so it has very low (or zero) frequency.

**Solenoid.** A coil of wire that produces a nearly uniform magnetic field
inside it.

**Taylor expansion.** Writing a smooth function near a point as a power
series: $f(x) = f(0) + f'(0)x + \frac{1}{2}f''(0)x^2 + \dots$

**Telescoping sum.** A sum in which consecutive terms cancel, leaving only the
first and last: $\sum_k (b_k - b_{k-1}) = b_n - b_0$.

**Tensile strength ($\sigma$).** The maximum stretching force per unit
cross-sectional area a material can take before breaking.

**Torque.** The turning effect of a force about a pivot: the force times its
lever arm.
