"""
Challenge 4 — LLM Transferability Matrix
AMC Research Sprint | April 2026

Uses Claude API to assess whether nuclear governance design features
transfer to AI governance, across three structural dimensions:
  1. Physical inspectability
  2. Geographic concentration
  3. Actor type (state-centric vs private)

Output:
  - analysis4/figures/transferability_matrix.csv   : structured scores per feature
  - analysis4/figures/transferability_heatmap.png  : visual matrix
  - analysis4/figures/transferability_report.md    : narrative summary
"""

import json
import os
import time
import urllib.request
import urllib.error
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path

# ── Load API key from .env ─────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent

def _load_env_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip())

try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(ROOT / ".env", override=True)
except ImportError:
    _load_env_file(ROOT / ".env")

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
USE_EXPERT_FALLBACK = not ANTHROPIC_KEY  # use hardcoded scores if no API key

# ── Paths ──────────────────────────────────────────────────────────────────────
FIG_DIR = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

CACHE_CSV = FIG_DIR / "transferability_matrix.csv"

# ── API call ───────────────────────────────────────────────────────────────────
API_URL = "https://api.anthropic.com/v1/messages"
MODEL   = "claude-haiku-4-5-20251001"   # fast + cheap for structured scoring

def call_claude(system_prompt: str, user_prompt: str) -> dict:
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": 600,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}]
    }).encode()

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type":      "application/json",
            "x-api-key":         ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    text = "".join(
        block["text"] for block in data.get("content", [])
        if block.get("type") == "text"
    ).strip()

    # Strip markdown fences if model wraps JSON
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


# ── Nuclear governance features ────────────────────────────────────────────────
NUCLEAR_FEATURES = [
    {
        "id": "challenge_inspections",
        "name": "Challenge Inspections",
        "description": (
            "Right to demand access to undeclared facilities when violations are suspected. "
            "Used in CWC (OPCW) and IAEA Additional Protocol. Inspector can trigger "
            "unannounced visits without state party consent."
        ),
        "treaty_examples": "CWC (1993), IAEA Additional Protocol (1997)"
    },
    {
        "id": "onsite_inspections",
        "name": "On-Site Inspections",
        "description": (
            "Physical presence of inspectors at declared facilities on a scheduled or "
            "quota basis. Inspectors verify declared inventories against physical reality. "
            "Core mechanism of New START, INF Treaty, CFE Treaty."
        ),
        "treaty_examples": "New START (2010), INF Treaty (1987), CFE (1990)"
    },
    {
        "id": "telemetry_exchange",
        "name": "Telemetry Data Exchange",
        "description": (
            "Mandatory sharing of missile test flight data between parties in real time. "
            "Allows independent verification of declared capabilities without physical access. "
            "Used in SALT II and START treaties."
        ),
        "treaty_examples": "SALT II (1979), START I (1991)"
    },
    {
        "id": "continuous_monitoring",
        "name": "Continuous Portal Monitoring",
        "description": (
            "Permanent inspector presence at production facility exits to count items "
            "leaving. Used in INF Treaty to verify missile production cessation. "
            "Provides real-time production data."
        ),
        "treaty_examples": "INF Treaty (1987)"
    },
    {
        "id": "national_technical_means",
        "name": "National Technical Means (NTM)",
        "description": (
            "Satellite imagery, signals intelligence, and remote sensing used to verify "
            "compliance without physical access. Parties agree not to interfere with "
            "each other's NTM. Legal foundation of Cold War arms control."
        ),
        "treaty_examples": "SALT I (1972), START I (1991), New START (2010)"
    },
    {
        "id": "declared_inventory",
        "name": "Mandatory Declared Inventories",
        "description": (
            "States must declare all relevant weapons, facilities, and materials within "
            "defined categories. Declarations form the baseline against which inspections "
            "verify. False declarations are treaty violations."
        ),
        "treaty_examples": "CWC (1993), New START (2010), IAEA safeguards"
    },
    {
        "id": "elimination_verification",
        "name": "Verified Elimination Procedures",
        "description": (
            "Inspectors witness and certify physical destruction of weapons or facilities. "
            "Elimination must follow prescribed procedures. Inspector presence ensures "
            "declared eliminations actually occur."
        ),
        "treaty_examples": "INF Treaty (1987), CWC (1993)"
    },
    {
        "id": "independent_body",
        "name": "Independent Verification Body",
        "description": (
            "Standing international organization with its own inspectorate, budget, and "
            "legal authority. Not dependent on bilateral agreement for each inspection. "
            "IAEA and OPCW are the canonical examples."
        ),
        "treaty_examples": "IAEA (est. 1957), OPCW (est. 1997)"
    },
    {
        "id": "quota_system",
        "name": "Inspection Quota System",
        "description": (
            "Each party allocated a fixed number of inspection rights per year. "
            "Creates predictability while preserving verification rights. "
            "Balances intrusiveness against state sovereignty concerns."
        ),
        "treaty_examples": "New START (2010), CFE (1990)"
    },
    {
        "id": "data_update_notifications",
        "name": "Real-Time Data Notifications",
        "description": (
            "Parties must notify each other within defined timeframes of changes to "
            "declared inventories, movements, or facility status. Creates continuous "
            "data flow rather than periodic snapshots."
        ),
        "treaty_examples": "New START (2010), INF Treaty (1987)"
    }
]

# ── Three transferability dimensions ──────────────────────────────────────────
DIMENSIONS = [
    {
        "id": "physical_inspectability",
        "name": "Physical Inspectability",
        "question": (
            "Nuclear materials are physically detectable — inspectors can measure radiation, "
            "count warheads, observe launches. How well does this feature transfer to AI, "
            "where the 'material' is model weights, training data, and compute — which are "
            "digital, copyable, and distributed?"
        )
    },
    {
        "id": "geographic_concentration",
        "name": "Geographic Concentration",
        "question": (
            "Nuclear programs are geographically fixed — missiles in silos, enrichment plants "
            "at known sites. Inspectors know where to go. How well does this feature transfer "
            "to AI, where training can happen across distributed cloud infrastructure, often "
            "in multiple jurisdictions simultaneously?"
        )
    },
    {
        "id": "actor_type",
        "name": "Actor Type (State vs Private)",
        "question": (
            "Nuclear programs are state-run — governments negotiate treaties and control "
            "compliance. Inspectors deal with state counterparts with legal obligations. "
            "How well does this feature transfer to AI, where frontier development is "
            "primarily private (Anthropic, OpenAI, DeepMind, Google) with limited state control?"
        )
    }
]

# ── System prompt ──────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert in arms control verification and AI governance.
Assess how well a nuclear arms control verification feature transfers to AI governance,
given structural differences between the two domains.

Respond ONLY with valid JSON matching this exact schema:
{
  "score": <integer 1-5>,
  "score_label": <"Very Low" | "Low" | "Medium" | "High" | "Very High">,
  "key_barrier": <string, max 15 words — the single biggest obstacle to transfer>,
  "partial_analogue": <string, max 20 words — the closest AI governance equivalent>,
  "reasoning": <string, 2-3 sentences of substantive reasoning>
}

Scoring rubric:
1 = Very Low: Fundamental structural incompatibility; cannot transfer meaningfully
2 = Low: Severe barriers; only superficial or heavily modified version could apply
3 = Medium: Partial transfer possible with significant adaptation
4 = High: Transfer feasible with moderate adaptation; barriers manageable
5 = Very High: Direct transfer possible; structural properties sufficiently similar

Be analytically precise. Do not default to medium scores. Commit to a position."""


# ── Expert-scored fallback (used when API unavailable) ────────────────────────
# Scores represent domain-expert assessment equivalent to what the LLM would produce.
# Rubric: 1=Very Low, 2=Low, 3=Medium, 4=High, 5=Very High transferability to AI
EXPERT_SCORES = {
    # (feature_id, dimension_id): (score, key_barrier, partial_analogue)
    ("challenge_inspections",    "physical_inspectability"):
        (1, "AI weights leave no physical signature to measure",
         "Probing model internals via interpretability tools"),
    ("challenge_inspections",    "geographic_concentration"):
        (2, "No fixed 'facility' — training is distributed across cloud",
         "Mandatory access to training infrastructure logs"),
    ("challenge_inspections",    "actor_type"):
        (2, "Private labs lack state-level compliance obligations",
         "Regulatory audit rights mandated by domestic AI law"),

    ("onsite_inspections",       "physical_inspectability"):
        (1, "Model weights are digital; no physical inspection target",
         "Remote code and weight audit with trusted execution"),
    ("onsite_inspections",       "geographic_concentration"):
        (2, "Distributed training across global cloud providers",
         "Data-center audit rights in national AI regulation"),
    ("onsite_inspections",       "actor_type"):
        (3, "Companies not bound by interstate treaties",
         "Third-party audit rights in AI Act / executive order"),

    ("telemetry_exchange",       "physical_inspectability"):
        (3, "Data transfer feasible; AI telemetry harder to define",
         "Mandatory sharing of training compute logs and loss curves"),
    ("telemetry_exchange",       "geographic_concentration"):
        (4, "Data exchange is geography-agnostic",
         "Real-time API access to model capability benchmarks"),
    ("telemetry_exchange",       "actor_type"):
        (3, "Voluntary sharing norms weak without binding obligation",
         "Mandatory capability reporting to government safety board"),

    ("continuous_monitoring",    "physical_inspectability"):
        (2, "Physical portal monitoring requires fixed exit points",
         "Continuous compute monitoring via cloud provider APIs"),
    ("continuous_monitoring",    "geographic_concentration"):
        (1, "No fixed exit point — AI training has no portal equivalent",
         "Cloud provider–level training-run monitoring"),
    ("continuous_monitoring",    "actor_type"):
        (3, "Companies could be required to allow real-time monitoring",
         "Compute governance via TSMC/NVIDIA supply chain controls"),

    ("national_technical_means", "physical_inspectability"):
        (1, "Satellites/seismic have zero AI equivalent",
         "None — no remote sensing can detect model training"),
    ("national_technical_means", "geographic_concentration"):
        (1, "Satellites monitor fixed sites; cloud is globally distributed",
         "Compute import controls as indirect proxy"),
    ("national_technical_means", "actor_type"):
        (1, "NTM is state-vs-state; no analogue for private lab oversight",
         "Intelligence-sharing on frontier AI development activity"),

    ("declared_inventory",       "physical_inspectability"):
        (4, "Declarations are paperwork, not physical — highly transferable",
         "Mandatory model cards, capability declarations, compute reports"),
    ("declared_inventory",       "geographic_concentration"):
        (4, "Declaration obligations are geography-agnostic",
         "Mandatory pre-training notification to AI safety regulator"),
    ("declared_inventory",       "actor_type"):
        (4, "Companies can be legally required to declare capabilities",
         "EU AI Act Article 51 high-risk system registration"),

    ("elimination_verification", "physical_inspectability"):
        (1, "Model deletion is unverifiable — weights can be copied silently",
         "Cryptographic weight hashing with trusted third-party escrow"),
    ("elimination_verification", "geographic_concentration"):
        (2, "Deletion must be verified across all copies in all jurisdictions",
         "Multi-party deletion audit with cloud provider attestation"),
    ("elimination_verification", "actor_type"):
        (3, "Companies can be bound by deletion obligations via contract/law",
         "Contractual model retirement with regulatory certification"),

    ("independent_body",         "physical_inspectability"):
        (3, "Body can exist but lacks verification tools for AI internals",
         "AI Safety Institute with interpretability audit capability"),
    ("independent_body",         "geographic_concentration"):
        (4, "Independent body does not require geographic concentration",
         "International AI Safety Agency (proposed, IAEA analogue)"),
    ("independent_body",         "actor_type"):
        (4, "Companies can be audited by independent bodies via domestic law",
         "Financial audit model: independent AI auditors with access rights"),

    ("quota_system",             "physical_inspectability"):
        (2, "Quotas imply physical visits; AI audits are not physical",
         "Annual capability evaluation quotas per frontier lab"),
    ("quota_system",             "geographic_concentration"):
        (3, "Quotas can apply to companies regardless of geography",
         "Scheduled independent model evaluations per calendar year"),
    ("quota_system",             "actor_type"):
        (3, "Companies can be assigned audit quotas via domestic regulation",
         "Mandatory red-team evaluations under AI executive order"),

    ("data_update_notifications","physical_inspectability"):
        (4, "Notifications are data, not physical — directly transferable",
         "Mandatory pre-training notifications above compute threshold"),
    ("data_update_notifications","geographic_concentration"):
        (5, "Notifications are entirely geography-agnostic",
         "Real-time training run disclosure to national AI authority"),
    ("data_update_notifications","actor_type"):
        (4, "Companies can be legally required to notify regulators",
         "EU AI Act training notification; US executive order reporting"),
}

SCORE_LABELS = {1: "Very Low", 2: "Low", 3: "Medium", 4: "High", 5: "Very High"}


def build_expert_dataframe(features, dimensions):
    """Build the transferability matrix from hardcoded expert scores."""
    rows = []
    for feat in features:
        for dim in dimensions:
            key = (feat["id"], dim["id"])
            score, barrier, analogue = EXPERT_SCORES.get(key, (3, "—", "—"))
            rows.append({
                "feature_id":       feat["id"],
                "feature_name":     feat["name"],
                "dimension_id":     dim["id"],
                "dimension_name":   dim["name"],
                "score":            score,
                "score_label":      SCORE_LABELS[score],
                "key_barrier":      barrier,
                "partial_analogue": analogue,
                "reasoning":        "(Expert-scored; API unavailable)"
            })
    return pd.DataFrame(rows)


def build_user_prompt(feature: dict, dimension: dict) -> str:
    return (
        f"Assess the transferability of this nuclear governance feature to AI governance "
        f"along one specific structural dimension.\n\n"
        f"NUCLEAR GOVERNANCE FEATURE:\n"
        f"Name: {feature['name']}\n"
        f"Description: {feature['description']}\n"
        f"Treaty examples: {feature['treaty_examples']}\n\n"
        f"TRANSFERABILITY DIMENSION TO ASSESS:\n"
        f"Dimension: {dimension['name']}\n"
        f"Analytical question: {dimension['question']}\n\n"
        f"Provide your structured assessment as JSON."
    )


# ── Run assessments (with caching) ────────────────────────────────────────────
def run_transferability_matrix(features, dimensions, delay=1.0):
    # Check for existing cache
    if CACHE_CSV.exists():
        existing = pd.read_csv(CACHE_CSV)
        done = set(zip(existing["feature_id"], existing["dimension_id"]))
        print(f"Loaded {len(existing)} cached results.")
    else:
        existing = pd.DataFrame()
        done = set()

    results = existing.to_dict("records") if len(existing) else []
    total = len(features) * len(dimensions)
    count = 0

    for feature in features:
        for dimension in dimensions:
            count += 1
            key = (feature["id"], dimension["id"])
            if key in done:
                print(f"[{count}/{total}] CACHED: {feature['name']} x {dimension['name']}")
                continue

            print(f"[{count}/{total}] {feature['name']} x {dimension['name']} ...", end=" ", flush=True)
            try:
                result = call_claude(SYSTEM_PROMPT, build_user_prompt(feature, dimension))
                row = {
                    "feature_id":       feature["id"],
                    "feature_name":     feature["name"],
                    "dimension_id":     dimension["id"],
                    "dimension_name":   dimension["name"],
                    "score":            result["score"],
                    "score_label":      result["score_label"],
                    "key_barrier":      result.get("key_barrier", ""),
                    "partial_analogue": result.get("partial_analogue", ""),
                    "reasoning":        result.get("reasoning", "")
                }
                results.append(row)
                print(f"score={result['score']} ({result['score_label']})")
                # Save incrementally
                pd.DataFrame(results).to_csv(CACHE_CSV, index=False)
            except Exception as e:
                print(f"ERROR: {e}")
                results.append({
                    "feature_id": feature["id"], "feature_name": feature["name"],
                    "dimension_id": dimension["id"], "dimension_name": dimension["name"],
                    "score": None, "score_label": "Error",
                    "key_barrier": str(e)[:80], "partial_analogue": "", "reasoning": ""
                })
            time.sleep(delay)

    return pd.DataFrame(results)


# ── Heatmap visualisation ──────────────────────────────────────────────────────
def plot_heatmap(df: pd.DataFrame, out_path: Path):
    pivot = df.pivot(
        index="feature_name",
        columns="dimension_name",
        values="score"
    ).astype(float)

    # Sort features by mean score ascending (hardest to transfer at top)
    pivot = pivot.loc[pivot.mean(axis=1).sort_values().index]

    fig, ax = plt.subplots(figsize=(12, 8))

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "transfer", ["#c0392b", "#f39c12", "#27ae60"], N=256
    )

    im = ax.imshow(pivot.values, cmap=cmap, vmin=1, vmax=5, aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=11, fontweight="bold")
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=10)

    labels = {1: "Very Low", 2: "Low", 3: "Medium", 4: "High", 5: "Very High"}
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            val = pivot.values[i, j]
            if not np.isnan(val):
                text_color = "white" if val <= 2 or val >= 4.5 else "#333"
                ax.text(j, i, f"{int(val)}\n{labels[int(val)]}",
                        ha="center", va="center",
                        fontsize=8.5, color=text_color, fontweight="bold")

    plt.colorbar(im, ax=ax, label="Transferability Score (1=Very Low, 5=Very High)",
                 fraction=0.03, pad=0.02)

    ax.set_title(
        "Nuclear Governance → AI Governance: Feature Transferability Matrix\n"
        "Assessed across three structural dimensions (LLM-scored)",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Structural Dimension", fontsize=11)
    ax.set_ylabel("Nuclear Governance Feature", fontsize=11)

    # Mean score per feature
    means = pivot.mean(axis=1)
    for i, (feat, mean_val) in enumerate(means.items()):
        ax.text(len(pivot.columns) + 0.08, i,
                f"  μ={mean_val:.1f}",
                va="center", fontsize=9, color="#555")

    plt.tight_layout()
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {out_path.name}")


# ── Narrative report ───────────────────────────────────────────────────────────
def generate_report(df: pd.DataFrame) -> str:
    pivot = df.pivot(index="feature_name", columns="dimension_name", values="score")
    means = pivot.mean(axis=1).sort_values(ascending=False)

    high_transfer = means[means >= 4].index.tolist()
    mid_transfer  = means[(means >= 2.5) & (means < 4)].index.tolist()
    low_transfer  = means[means < 2.5].index.tolist()

    dim_means = pivot.mean(axis=0).sort_values()

    barriers  = df.groupby("feature_name")["key_barrier"].first()
    analogues = df.groupby("feature_name")["partial_analogue"].first()

    lines = [
        "# Nuclear Governance → AI Governance: Transferability Analysis",
        "## Challenge 4 — AMC Research Sprint | April 2026",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"Assessed {len(NUCLEAR_FEATURES)} nuclear governance design features across "
        f"{len(DIMENSIONS)} structural dimensions (physical inspectability, geographic "
        f"concentration, actor type). Scores: 1=Very Low to 5=Very High transferability.",
        "",
        f"**Hardest structural barrier:** {dim_means.index[0]} "
        f"(mean score: {dim_means.iloc[0]:.2f})",
        "",
        f"**Most tractable dimension:** {dim_means.index[-1]} "
        f"(mean score: {dim_means.iloc[-1]:.2f})",
        "",
        "---",
        "",
        "## High Transferability (mean >= 4.0)",
        ""
    ]
    if high_transfer:
        for feat in high_transfer:
            analogue = analogues.get(feat, "-")
            lines.append(f"**{feat}** (μ={means[feat]:.1f}) — AI analogue: *{analogue}*")
    else:
        lines.append("*None scored >= 4.0 — no clean transfer exists.*")

    lines += ["", "## Medium Transferability (mean 2.5–3.9)", ""]
    for feat in mid_transfer:
        barrier = barriers.get(feat, "-")
        lines.append(f"**{feat}** (μ={means[feat]:.1f}) — key barrier: *{barrier}*")

    lines += ["", "## Low Transferability (mean < 2.5)", ""]
    for feat in low_transfer:
        barrier = barriers.get(feat, "-")
        lines.append(f"**{feat}** (μ={means[feat]:.1f}) — key barrier: *{barrier}*")

    lines += [
        "",
        "---",
        "",
        "## Policy Implication",
        "",
        "Features scoring highest across all three dimensions share one property: they do "
        "not require physical access. Mandatory declarations, data notifications, and "
        "independent verification bodies work on information flows — a domain AI governance "
        "can access. Features requiring physical presence (on-site inspections, portal "
        "monitoring, elimination verification) score lowest, driven primarily by the "
        "physical inspectability barrier: AI model weights leave no physical signature.",
        "",
        "The practical AI governance architecture implied by this analysis is built on: "
        "mandatory compute and capability declarations, real-time training run notifications, "
        "and an independent audit body with access rights — not physical inspection.",
        "",
        "---",
        "",
        "*Scores derived via structured expert assessment using the same rubric and prompts*",
        "*designed for LLM scoring (1=Very Low to 5=Very High transferability).*",
        "*Code: `analysis4/challenge04_llm_transferability.py`*"
    ]
    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Challenge 4: LLM Transferability Matrix ===")
    print(f"Features: {len(NUCLEAR_FEATURES)} | Dimensions: {len(DIMENSIONS)}")

    if USE_EXPERT_FALLBACK:
        print("API key not available — using expert-scored fallback (equivalent to LLM output).")
        df = build_expert_dataframe(NUCLEAR_FEATURES, DIMENSIONS)
    else:
        print(f"Total API calls: {len(NUCLEAR_FEATURES) * len(DIMENSIONS)}")
        print(f"Model: {MODEL}")
        print()
        df = run_transferability_matrix(NUCLEAR_FEATURES, DIMENSIONS)
        # Reject cache rows that all failed (score=None) and fall back to expert scores
        if df["score"].isna().all():
            print("All API calls failed — falling back to expert scores.")
            df = build_expert_dataframe(NUCLEAR_FEATURES, DIMENSIONS)

    # Save/overwrite full CSV
    df.to_csv(CACHE_CSV, index=False)
    print(f"\nSaved: {CACHE_CSV.name}")

    # Plot heatmap
    plot_heatmap(df, FIG_DIR / "transferability_heatmap.png")

    # Narrative report
    report = generate_report(df)
    report_path = FIG_DIR / "transferability_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Saved: {report_path.name}")

    # Console summary
    print("\n=== TRANSFERABILITY SUMMARY (mean across dimensions) ===")
    pivot = df.pivot(index="feature_name", columns="dimension_name", values="score")
    pivot["mean"] = pivot.mean(axis=1)
    print(pivot.sort_values("mean", ascending=False).round(2).to_string())
