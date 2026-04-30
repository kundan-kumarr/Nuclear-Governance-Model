# Nuclear Governance → AI Governance: Transferability Analysis
## Challenge 4 — AMC Research Sprint | April 2026

---

## Summary

Assessed 10 nuclear governance design features across 3 structural dimensions (physical inspectability, geographic concentration, actor type). Scores: 1=Very Low to 5=Very High transferability.

**Hardest structural barrier:** Physical Inspectability (mean score: 2.20)

**Most tractable dimension:** Actor Type (State vs Private) (mean score: 3.00)

---

## High Transferability (mean >= 4.0)

**Real-Time Data Notifications** (μ=4.3) — AI analogue: *Mandatory pre-training notifications above compute threshold*
**Mandatory Declared Inventories** (μ=4.0) — AI analogue: *Mandatory model cards, capability declarations, compute reports*

## Medium Transferability (mean 2.5–3.9)

**Independent Verification Body** (μ=3.7) — key barrier: *Body can exist but lacks verification tools for AI internals*
**Telemetry Data Exchange** (μ=3.3) — key barrier: *Data transfer feasible; AI telemetry harder to define*
**Inspection Quota System** (μ=2.7) — key barrier: *Quotas imply physical visits; AI audits are not physical*

## Low Transferability (mean < 2.5)

**Continuous Portal Monitoring** (μ=2.0) — key barrier: *Physical portal monitoring requires fixed exit points*
**Verified Elimination Procedures** (μ=2.0) — key barrier: *Model deletion is unverifiable — weights can be copied silently*
**On-Site Inspections** (μ=2.0) — key barrier: *Model weights are digital; no physical inspection target*
**Challenge Inspections** (μ=1.7) — key barrier: *AI weights leave no physical signature to measure*
**National Technical Means (NTM)** (μ=1.0) — key barrier: *Satellites/seismic have zero AI equivalent*

---

## Policy Implication

Features scoring highest across all three dimensions share one property: they do not require physical access. Mandatory declarations, data notifications, and independent verification bodies work on information flows — a domain AI governance can access. Features requiring physical presence (on-site inspections, portal monitoring, elimination verification) score lowest, driven primarily by the physical inspectability barrier: AI model weights leave no physical signature.

The practical AI governance architecture implied by this analysis is built on: mandatory compute and capability declarations, real-time training run notifications, and an independent audit body with access rights — not physical inspection.

---

*Scores derived via structured expert assessment using the same rubric and prompts*
*designed for LLM scoring (1=Very Low to 5=Very High transferability).*
*Code: `analysis4/challenge04_llm_transferability.py`*