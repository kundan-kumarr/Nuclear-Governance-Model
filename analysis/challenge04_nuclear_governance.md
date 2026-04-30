# The Nuclear Governance Model: Is the "IAEA for AI" Analogy Empirically Grounded?
## Challenge 4 — AMC Research Sprint | April 2026
*Alva Myrdal Centre for Nuclear Disarmament, Uppsala University*

> **Submission note:** This output covers both **Part A** (empirical analysis, Sections 2–4)
> and **Part B** (AI governance extension, Section 5). Analysis code:
> `analysis4/challenge04_nuclear_governance.py` (empirical) ·
> `analysis4/challenge04_llm_transferability.py` (transferability matrix).

---

## 1. Introduction

The phrase "we need an IAEA for AI" has become a fixture of AI governance discourse. But the
analogy is only as strong as its empirical foundation: does nuclear arms control actually operate
by a distinct design logic — and if so, which features of that logic are transferable to AI
governance, and which are nuclear-specific?

This analysis tests the nuclear model against the AMC dataset (128 agreements, 1817–2021),
comparing nuclear-linked agreements (36) to all others (92) across three layers of governance
architecture: compliance tier, verification mechanism design, and inspector and trigger type.
Section 5 then applies a structured transferability matrix to 10 nuclear governance features
across 3 structural dimensions, identifying which elements of the nuclear model can be selectively
adapted for AI governance — and which cannot.

---

## 2. Method

**Nuclear flag construction.** Agreements are classified as nuclear if the `weapons_facilities`
dataset lists a Summary Category row for any of: Nuclear Weapons, ICBMs, SLBMs, ICBM Launchers,
SLBM Launchers, Heavy Bombers, or Nuclear Submarines. This yields **36 nuclear agreements** and
**92 non-nuclear agreements**.

**Three comparison layers:**

| Layer | Dataset | Features compared |
|-------|---------|------------------|
| Compliance tier | `agreement_info` | Verified / Demonstrated / Consultation / None |
| Mechanism design | `vercom` (99 rows) | Facility access, item access, mechanism type |
| Oversight structure | `vercom` | Inspector type (national/international/joint), trigger type |

**Statistical tests.** Chi-squared with Yates' correction for binary proportions; Cohen's h for
effect size. Mann-Whitney U with rank-biserial r for ordinal comparisons. Significance thresholds:
`*` p<0.05, `**` p<0.01, `***` p<0.001.

---

## 3. Results

### 3.1 Nuclear Agreements Mandate Stronger Compliance — Significantly

The single strongest finding: nuclear agreements are more than twice as likely to require
**verified compliance** (third-party inspection) compared to non-nuclear agreements.

| Compliance Tier | Nuclear (n=36) | Non-Nuclear (n=92) | p-value | Cohen's h |
|----------------|---------------|-------------------|---------|-----------|
| Verified (3) | **44%** | 20% | **0.008** | **0.54** |
| Demonstrated (2) | 47% | 45% | 0.941 | 0.05 |
| Consultation (1) | — | — | — | — |
| None (0) | — | — | — | — |

A Cohen's h of 0.54 is a **large effect** by conventional standards (h > 0.5). The null result
for demonstrated compliance (h=0.05, p=0.941) is equally informative: the nuclear model is
distinguished by what it mandates at the top tier, not by broadly higher compliance standards
throughout.

> **Killer finding:** The nuclear governance model is empirically distinct — but only at the
> verified compliance tier. The radar chart (Figure 4) visualizes this directly: five of six
> governance dimensions overlap almost completely between nuclear and non-nuclear agreements.
> **One axis stands apart: verified compliance (44% vs 20%, p=0.008\*\*).**

### 3.2 Verification Toolkit Converges Once Mandated — A Positive Finding

When we examine agreements that *do* have verification mechanisms (`vercom` dataset: 56 nuclear,
43 non-nuclear mechanism rows), the design features are statistically indistinguishable:

| Feature | Nuclear (vercom) | Non-Nuclear (vercom) | p-value | Sig |
|---------|-----------------|---------------------|---------|-----|
| Facility access | 54% | 60% | 0.630 | ns |
| Item access | 46% | 40% | 0.630 | ns |
| International inspector | 9% | 14% | 0.641 | ns |

This convergence is not a null result to apologize for — **it is the most policy-relevant
finding in the analysis.** It means that the verification toolkit used in nuclear arms control
is the *standard* toolkit deployed whenever states choose to mandate verification, regardless
of weapon type. The nuclear model is not technically exotic; it is politically exceptional.

> **Policy implication:** AI governance does not need to invent new verification mechanisms.
> The tools are already available in the standard arms control repertoire. What is missing
> is the political decision to require them.

**The international inspector finding is counterintuitive.** Nuclear agreements rely *less*
on international inspectors (9%) than non-nuclear agreements (14%). The dominant oversight model
in nuclear arms control is **national technical means (NTM)** — satellite imagery, seismic
monitoring, signals intelligence — supplemented by bilateral on-site inspection teams. The IAEA
is the exception, not the rule, even within nuclear governance.

### 3.3 Two Sub-Models Within Nuclear Governance

The data and the qualitative record reveal that "nuclear governance" is not a single model but
two distinct architectures (see Figure 5):

**Bilateral / NTM Model** (START, INF, ABM, New START): Verification via national technical
means — satellite surveillance, seismic monitoring, signals intelligence — supplemented by
quota-based bilateral inspection teams. No standing international body. Inspector type is
national, not international. Trigger is right-based (fixed number of inspections per year).

**IAEA Model** (NPT Safeguards, CTBT, Additional Protocol): Standing international body with
its own inspectorate, budget, and legal authority. Physical measurement and environmental
sampling. Declared-site routine inspections plus challenge inspection rights under the
Additional Protocol. Multilateral, not bilateral.

These two sub-models share the verified compliance tier but differ fundamentally in *how*
verification is implemented. The "IAEA for AI" analogy cites only one of them.

---

## 4. Interpretation

### 4.1 The nuclear advantage is political, not technical

Nuclear agreements mandate verified compliance at twice the rate of non-nuclear agreements
because the geopolitical stakes — not the technical sophistication — forced that outcome.
The Cold War dyad (US–USSR) had both the motivation (catastrophic asymmetric risk from cheating)
and the bilateral negotiating structure to build elaborate verification systems. The IAEA model
emerged from a different logic: multilateral proliferation risk requiring a neutral inspector.

The lesson for other domains: **the technical mechanisms of verification are not inherently
nuclear**. What is nuclear-specific is the political calculus that made states accept intrusive
oversight.

### 4.2 The design principle: tier oversight to risk

The consistent logic across 128 agreements: where the cost of undetected cheating is catastrophic
and irreversible, states accept intrusive verification. This principle is domain-agnostic. It
applies to chemical weapons (CWC), biological weapons (BWC, despite verification failures),
strategic delivery systems, and — the argument goes — frontier AI.

---

## 5. Part B: LLM Transferability Matrix

To move beyond qualitative comparison, we applied a structured transferability assessment to
10 nuclear governance design features across 3 structural dimensions. Each cell scores
transferability from 1 (Very Low) to 5 (Very High), using an expert-scored rubric with
explicit barrier and partial-analogue annotation. The resulting heatmap is Figure 6.

**Three structural dimensions assessed:**
1. **Physical Inspectability** — Can violations be detected without physical access?
2. **Geographic Concentration** — Do you know where to look?
3. **Actor Type** — Are you dealing with states or private labs?

### 5.1 Transferability Summary

| Transferability Tier | Features | Mean Score |
|---------------------|----------|------------|
| **High (μ ≥ 4.0)** | Real-Time Data Notifications, Mandatory Declared Inventories | 4.33, 4.00 |
| **Medium (μ 2.5–3.9)** | Independent Verification Body, Telemetry Data Exchange, Inspection Quota System | 3.67, 3.33, 2.67 |
| **Low (μ < 2.5)** | On-Site Inspections, Continuous Portal Monitoring, Verified Elimination, Challenge Inspections, NTM | 2.0–1.0 |

**Hardest structural barrier:** Physical Inspectability (dimension mean: 2.2/5). AI model
weights leave no physical signature — there is no radiation to measure, no mass to count.
This single barrier blocks direct transfer of the entire on-site inspection toolkit.

**Most tractable dimension:** Actor Type (dimension mean: 3.0/5). Companies can be legally
bound by regulatory obligation, unlike states negotiating peer treaties.

### 5.2 What Transfers and What Doesn't

**High-transferability features** share one property: they operate on information flows, not
physical access.

- **Real-Time Data Notifications** (μ=4.33): Mandatory training-run disclosure to a national
  AI authority is directly analogous to New START's notification system. Geography-agnostic,
  regulation-enforceable, and technically straightforward.
- **Mandatory Declared Inventories** (μ=4.00): Mandatory model capability declarations and
  compute reports are the AI analogue of CWC chemical weapons declarations. Already partially
  implemented in model cards; what is missing is legal obligation and independent verification.

**Low-transferability features** all share a dependence on physical detectability:

- **National Technical Means** (μ=1.0): Satellites and seismic monitors have zero AI equivalent.
  There is no remote sensing technique capable of detecting that a model is being trained. This
  is the deepest structural incompatibility between nuclear and AI governance.

- **Challenge Inspections and On-Site Inspections** (μ=1.67, 2.0): Physical inspection of
  declared facilities works when the thing you are inspecting has a physical signature. Model
  weights do not. Challenge inspection rights could in principle be extended to AI — giving a
  regulator the right to demand access to training infrastructure — but the inspector would have
  no reliable method to verify what they found.

> **The key non-transferable:** NTM is the backbone of bilateral nuclear arms control. It has
> no AI governance analogue. This is why the bilateral/NTM sub-model of nuclear governance
> cannot transfer — not even in adapted form.

### 5.3 The Interpretability Prerequisite

This is what "interpretability is the Geiger counter" means precisely. The IAEA was established
in 1957 drawing on existing radiation measurement physics. What matured over the following four
decades was the safeguards *application* of those tools — environmental sampling and in-field
isotope analysis became standard IAEA practice only in the 1990s under the Additional Protocol,
decades after the institution was founded. The institution preceded full methodological maturity
by forty years, not ten. That is a longer lead time, and a more honest precedent for the AI case.

The transferability matrix points toward a two-tier architecture that reflects this sequencing:

**Tier 1 — Build now, independent of interpretability maturity:**

- **Mandatory compute and capability declarations** (analogue: declared inventories)
- **Real-time training notifications above a compute threshold** (analogue: data notifications)
- **Independent audit body with regulatory access rights** (analogue: OPCW/IAEA model)

These three elements work on information flows and institutional authority — neither requires
interpretability tools to function. They can be designed, negotiated, and operational within
the current geopolitical window.

**Tier 2 — Build the measurement capability in parallel:**

- **Interpretability-based challenge evaluation** — mechanistic interpretability tools
  (linear probes, steering vectors, activation patching) are the early-stage equivalents
  of the environmental sampling methods that took the IAEA four decades to fully operationalise.
  The audit body should be established before these tools mature, exactly as the IAEA preceded
  the Additional Protocol by forty years.

The policy priority is clear: build Tier 1 immediately while funding Tier 2. The institution
does not need to wait for the Geiger counter — it needs to exist so it can use the Geiger
counter when it arrives.

---

## 6. Conclusion

The nuclear governance model is empirically distinct — at the verified compliance tier. The
44% vs 20% gap (p=0.008, Cohen's h=0.54) is large and statistically robust. But the distinction
is in the political mandate, not the technical toolkit: once verification exists, nuclear and
non-nuclear mechanisms look similar. The transferability matrix sharpens this: the nuclear model
contains both transferable and non-transferable features, sorted cleanly by whether they require
physical access.

**Three takeaways for AI governance:**

1. **Mandate verification for highest-risk systems** — the nuclear analogy supports this
   precisely; the effect size justifies treating it as the central design choice.

2. **Build on the IAEA sub-model, not the NTM sub-model** — declarations, notifications, and
   independent audit bodies transfer well. Bilateral technical-means surveillance does not.

3. **Interpretability is the Geiger counter** — institutional design should follow the
   measurement capability, not precede it. Priority investment in mechanistic interpretability
   tools (linear probes, steering vectors, activation patching) is the prerequisite that
   determines what AI governance can actually verify.

---

> **The "IAEA for AI" analogy is empirically grounded where it matters most — at the level of
> design principle. It fails where it matters most technically — at the level of what inspectors
> can actually measure. That gap is the central challenge for AI governance.**

---

*Analysis based on AMC Arms Control Agreement Database V2 (128 agreements, 1817–2021).*
*Code: `analysis4/challenge04_nuclear_governance.py` (empirical) · `analysis4/challenge04_llm_transferability.py` (transferability matrix)*
*Figures: `analysis4/figures/`*
