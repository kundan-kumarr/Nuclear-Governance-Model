# The Nuclear Governance Model: Is the "IAEA for AI" Analogy Empirically Grounded?
## Challenge 4 — AMC Research Sprint | April 2026
*Alva Myrdal Centre for Nuclear Disarmament, Uppsala University*

> **Submission note:** This draft integrates both the original empirical analysis and the later design-template supplement so the writeup now maps directly onto the Challenge 4 brief. Analysis code:
> `analysis4/challenge04_nuclear_governance.py` (main empirical analysis) ·
> `analysis4/challenge04_design_template_fix.py` (explicit design-template supplement) ·
> `analysis4/challenge04_llm_transferability.py` (AI transferability matrix).

---

## 1. Introduction

The phrase "we need an IAEA for AI" has become a fixture of AI governance discourse. But the
analogy is only as strong as its empirical foundation: does nuclear arms control actually operate
by a distinct design logic, and if so, which elements of that logic are transferable to AI
and which are nuclear-specific?

This analysis tests the nuclear model against the AMC dataset (128 agreements, 1817–2021),
comparing nuclear-linked agreements (36) to all others (92) across the specific governance
dimensions named in the challenge brief: **compliance mechanism types, access provisions,
inspector arrangements, and trigger mechanisms**. Section 5 then applies a structured
transferability matrix to the AI-governance extension.

---

## 2. Method

**Nuclear flag construction.** Agreements are classified as nuclear if the `weapons_facilities`
dataset lists a Summary Category row for any of: Nuclear Weapons, ICBMs, SLBMs, ICBM Launchers,
SLBM Launchers, Heavy Bombers, or Nuclear Submarines. This yields **36 nuclear agreements** and
**92 non-nuclear agreements**.

**Datasets used:**
- `agreement_info` for agreement-level compliance architecture
- `vercom` for verification design details
- `weapons_facilities` for nuclear/non-nuclear classification

**Four comparison dimensions required by the brief:**

| Dimension | Dataset | Variables used |
|---|---|---|
| Compliance mechanism types | `agreement_info` | verified, demonstrated, consultation |
| Access provisions | `vercom` | area, facility, item, item-section access |
| Inspector arrangements | `vercom` | national/NTM, international, joint |
| Trigger mechanisms | `vercom` | trigger type and agreement-trigger flags |

**Statistical tests.** Binary comparisons use chi-squared with Yates' correction and Cohen's h.
Categorical inspector and trigger distributions use overall chi-squared tests. Significance
thresholds: `*` p<0.05, `**` p<0.01, `***` p<0.001.

---

## 3. Results

### 3.1 Compliance Mechanism Types

The strongest result remains the same: nuclear agreements are much more likely to mandate
**verified compliance** than non-nuclear agreements. The design-template supplement also shows
that **consultation mechanisms** are more common in nuclear agreements, while demonstrated
compliance is not meaningfully different.

| Feature | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Verified compliance | 44.4 | 19.6 | +24.9 | 0.008 | 0.54 | ** |
| Demonstrated compliance | 47.2 | 44.6 | +2.7 | 0.941 | 0.05 | ns |
| Consultation mechanism | 66.7 | 44.6 | +22.1 | 0.040 | 0.45 | * |

This matters because it sharpens the earlier claim. The nuclear model is not distinctive across
every tier of governance. It is distinctive mainly at the points where states either require
**verified oversight** or embed stronger consultation architecture.

> **Updated core finding:** The nuclear governance model is empirically distinctive at the upper
> end of oversight design, especially verified compliance, and secondarily consultation. It is
> not uniformly distinctive across all governance dimensions.

### 3.2 Access Provisions

Once verification mechanisms exist, the underlying access toolkit looks broadly shared across
weapon categories.

| Feature | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Area access | 26.8 | 25.6 | +1.2 | 1.000 | 0.03 | ns |
| Facility access | 53.6 | 60.5 | -6.9 | 0.630 | -0.14 | ns |
| Item access | 46.4 | 39.5 | +6.9 | 0.630 | 0.14 | ns |
| Item-section access | 1.8 | 0.0 | +1.8 | 1.000 | 0.27 | ns |

This is one of the most policy-relevant null findings in the project. It means the nuclear model
is not defined by a unique technical access repertoire. Facility and item access are part of a
broader arms-control toolkit that appears whenever states choose to verify seriously.

### 3.3 Inspector Arrangements

Inspector arrangements also do not separate nuclear agreements cleanly from the rest once we move
from the agreement level to the mechanism level.

| Inspector type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| National/NTM | 83.9 | 72.1 | +11.8 | 0.350 | 0.29 | ns |
| International body | 8.9 | 14.0 | -5.0 | 0.350 | -0.16 | ns |
| Joint | 7.1 | 14.0 | -6.8 | 0.350 | -0.22 | ns |
| Other | 0.0 | 0.0 | +0.0 | 0.350 | 0.00 | ns |

This supports an important correction to the common "IAEA for AI" intuition. The iconic
international-inspector model is not the dominant empirical form even inside nuclear governance.
National technical means and bilateral inspection structures remain central.

### 3.4 Trigger Mechanisms

Trigger mechanisms are also more similar than different across nuclear and non-nuclear verified
agreements.

| Trigger type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Right-based quota | 39.3 | 44.2 | -4.9 | 0.668 | -0.10 | ns |
| Event-triggered | 33.9 | 23.3 | +10.7 | 0.668 | 0.24 | ns |
| Continuous/NTM | 10.7 | 11.6 | -0.9 | 0.668 | -0.03 | ns |
| Challenge | 7.1 | 4.7 | +2.5 | 0.668 | 0.11 | ns |
| Scheduled | 8.9 | 14.0 | -5.0 | 0.668 | -0.16 | ns |
| Other | 0.0 | 2.3 | -2.3 | 0.668 | -0.31 | ns |

The agreement-trigger flag fields do not add strong differentiation either. In other words,
**how inspections are triggered is not what makes the nuclear model empirically special**.

### 3.5 What Is Actually Nuclear-Specific?

Taken together, the results imply that the nuclear model is distinctive in **mandate intensity**
more than in **toolkit composition**.

**More nuclear-specific features:**
- Verified compliance
- Consultation mechanism presence

**Shared features across weapon categories:**
- Facility access
- Item access
- Area access
- Inspector type mix
- Trigger type mix
- Demonstrated compliance

This clarifies the challenge question directly. Nuclear agreements do follow a partially distinct
design template, but the distinctiveness lies mainly in the decision to require stronger oversight,
not in the invention of wholly different access, inspector, or trigger architectures.

### 3.6 Two Sub-Models Within Nuclear Governance

The data and the qualitative record still suggest that "nuclear governance" is not a single model
but two related sub-models:

**Bilateral / NTM Model** (START, INF, ABM, New START): verification via national technical
means, quota-based rights, and bilateral teams. No standing international body.

**IAEA Model** (NPT Safeguards, CTBT, Additional Protocol): standing international body,
declared-site inspections, environmental sampling, and challenge-style authority.

These sub-models share the verified-compliance tier but differ in implementation logic. The
"IAEA for AI" analogy invokes only one branch of the broader nuclear governance family.

---

## 4. Interpretation

### 4.1 The nuclear advantage is political, not technical

The clearest empirical distinction is not that nuclear governance has a unique inspection toolkit.
It is that nuclear agreements are substantially more willing to **mandate** the highest form of
overight. Once verification exists, the same kinds of access provisions, inspector arrangements,
and trigger mechanisms recur in non-nuclear arms control as well.

That means the nuclear model's distinctiveness is fundamentally political: catastrophic downside
risk, bargaining structure, and strategic salience made states accept more intrusive compliance
architecture.

### 4.2 The design principle: tier oversight to risk

The consistent logic across the dataset is that where the cost of undetected cheating is judged
catastrophic, states move upward on the oversight ladder. This principle appears transferable
across domains even when the specific inspection methods are not.

### 4.3 The challenge brief answered directly

Challenge 4 asks whether nuclear agreements follow a distinct design template and what makes it
architecturally different. The answer is:

- **Yes, but only partly.**
- The distinctiveness is clearest in **verified compliance** and, to a lesser extent,
  **consultation architecture**.
- The nuclear model is **not** uniquely defined by inspector arrangements, access provisions,
  or trigger mechanisms.
- Therefore, the nuclear template is best understood as a model of **politically mandated high-
  assurance oversight**, not as a wholly unique technical verification design.

---

## 5. Part B: Transferability to AI Governance

To move beyond qualitative comparison, we applied a structured transferability assessment to
10 nuclear governance design features across 3 structural dimensions.

**Three structural dimensions assessed:**
1. **Physical Inspectability** — Can violations be detected without physical access?
2. **Geographic Concentration** — Do you know where to look?
3. **Actor Type** — Are you dealing with states or private labs?

### 5.1 Transferability Summary

| Transferability Tier | Features | Mean Score |
|---|---|---|
| **High (mu >= 4.0)** | Real-Time Data Notifications, Mandatory Declared Inventories | 4.33, 4.00 |
| **Medium (mu 2.5-3.9)** | Independent Verification Body, Telemetry Data Exchange, Inspection Quota System | 3.67, 3.33, 2.67 |
| **Low (mu < 2.5)** | On-Site Inspections, Continuous Portal Monitoring, Verified Elimination, Challenge Inspections, NTM | 2.0-1.0 |

**Hardest structural barrier:** Physical Inspectability (dimension mean: 2.2/5). AI model
weights leave no physical signature.

**Most tractable dimension:** Actor Type (dimension mean: 3.0/5).

### 5.2 What Transfers and What Doesn't

**Higher-transferability features** operate on information flows rather than physical detection:
mandatory declarations, real-time notifications, and some form of independent audit body.

**Lower-transferability features** depend on physical inspectability: on-site inspections,
challenge inspections in their nuclear form, portal monitoring, verified elimination, and NTM.

> **Key takeaway:** The most transferable part of the nuclear model is the institutional logic of
> mandatory reporting and independent oversight. The least transferable part is the physical
> verification toolkit.

### 5.3 Interpretability as the Measurement Prerequisite

This is the precise sense in which "interpretability is the Geiger counter." Nuclear governance
became powerful not merely because institutions existed, but because inspectors eventually had
measurement tools that could detect violations. AI governance can build institutions earlier,
but it will remain verification-limited until interpretability and audit methods mature.

---

## 6. Conclusion

The nuclear governance model is empirically distinct, but not in the simple way the slogan
"IAEA for AI" implies. Its strongest distinctive feature is the greater use of **verified
compliance** (44.4% vs 19.6%, p=0.008, Cohen's h=0.54), with a secondary difference in
**consultation mechanisms** (66.7% vs 44.6%, p=0.040, Cohen's h=0.45). By contrast, access
provisions, inspector arrangements, and trigger mechanisms look broadly shared across nuclear and
non-nuclear agreements once verification is present.

**Three takeaways for AI governance:**

1. **Mandate stronger oversight for the highest-risk systems.**
   This is the clearest lesson supported by the nuclear comparison.

2. **Do not overread the IAEA analogy.**
   The empirical nuclear model is not defined by a uniquely nuclear inspector or trigger toolkit.

3. **Transfer the institutional logic, not the physical toolkit.**
   Declarations, notifications, and independent oversight bodies travel better than on-site
   inspection or NTM-style monitoring.

---

> **The "IAEA for AI" analogy is empirically strongest at the level of political commitment to
> high-assurance oversight. It is weakest at the level of physical verification technique. That
> distinction is the central lesson of the nuclear governance model.**

---

*Analysis based on AMC Arms Control Agreement Database V2 (128 agreements, 1817–2021).*  
*Code: `analysis4/challenge04_nuclear_governance.py` · `analysis4/challenge04_design_template_fix.py` · `analysis4/challenge04_llm_transferability.py`*  
*Figures and tables: `analysis4/figures/` and `analysis4/challenge04_design_template_fix_tables.csv`*
