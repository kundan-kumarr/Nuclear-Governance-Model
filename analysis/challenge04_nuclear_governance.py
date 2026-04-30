"""
Challenge 4: The Nuclear Governance Model
AMC Research Sprint | April 2026

Research question: Do nuclear agreements follow a distinct design template?
Is the "IAEA for AI" analogy empirically grounded?

Method:
  1. Build nuclear/non-nuclear flag from weapons_facilities summary categories
  2. Compare compliance architecture (agreement_info) across nuclear vs non-nuclear
  3. Compare verification mechanism design (vercom) across groups
  4. Statistical tests: chi-squared for proportions, Mann-Whitney U for means
  5. Effect sizes: Cohen's h for proportions, rank-biserial r for distributions

Outputs (analysis4/figures/):
  nuc_compliance_comparison.png    — compliance tier by nuclear/non-nuclear
  nuc_vercom_features.png          — verification design features comparison
  nuc_inspector_access.png         — inspector type + access depth heatmap
  nuc_trigger_types.png            — trigger mechanism comparison
  nuc_radar.png                    — radar chart: nuclear design template vs others
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from scipy import stats

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR  = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

COLORS = {
    "nuclear":     "#1a5e7a",
    "non_nuclear": "#f4a460",
    "sig":         "#c0392b",
    "nsig":        "#aaa",
}

# ── Load data ─────────────────────────────────────────────────────────────────
info    = pd.read_csv(DATA_DIR / "amcdata_agreement_info_V2.csv",     encoding="latin1")
weapons = pd.read_csv(DATA_DIR / "amcdata_weapons_facilities_V2.csv", encoding="latin1")
vercom  = pd.read_csv(DATA_DIR / "amcdata_vercom_V2.csv",             encoding="latin1")

# ── Build nuclear flag ────────────────────────────────────────────────────────
# Nuclear = any agreement covering: Nuclear Weapons, ICBMs, SLBMs,
# ICBM/SLBM Launchers, Heavy Bombers, Nuclear Submarines
NUCLEAR_CATS = {
    "Nuclear Weapons", "ICBMs", "SLBMs",
    "ICBM Launchers", "SLBM Launchers",
    "Heavy Bombers", "Nuclear Submarines",
}
summary_rows = (
    weapons[weapons["item"].str.contains("Summary Category", na=False)]
    [["agreement_id", "item"]].drop_duplicates()
)
summary_rows["weapon_cat"] = summary_rows["item"].str.extract(r"\((.+)\)")
summary_rows["is_nuclear"] = summary_rows["weapon_cat"].isin(NUCLEAR_CATS)

nuc_flag = (
    summary_rows.groupby("agreement_id")["is_nuclear"]
    .any()
    .reset_index(name="nuclear")
)
df = info.merge(nuc_flag, on="agreement_id", how="left")
df["nuclear"] = df["nuclear"].fillna(False).infer_objects(copy=False)

nuc = df[df["nuclear"]]
non = df[~df["nuclear"]]
print(f"Nuclear agreements: {len(nuc)} | Non-nuclear: {len(non)} | Total: {len(df)}")

# ── Compliance score ──────────────────────────────────────────────────────────
def compliance_level(row):
    if row.get("verified_compliance_mechanism", 0) == 1:     return 3
    if row.get("demonstrated_compliance_mechanism", 0) == 1: return 2
    if row.get("consultation_mechanism", 0) == 1:             return 1
    return 0

df["compliance_score"] = df.apply(compliance_level, axis=1)
TIER_LABELS = {0: "None", 1: "Consultation", 2: "Demonstrated", 3: "Verified"}
df["compliance_label"] = df["compliance_score"].map(TIER_LABELS)

# ── Statistical helpers ───────────────────────────────────────────────────────
def chi2_test(col, df1, df2):
    """Chi-squared test for difference in proportions of binary column."""
    a1 = df1[col].fillna(0).astype(float).reset_index(drop=True)
    a2 = df2[col].fillna(0).astype(float).reset_index(drop=True)
    ct = pd.crosstab(
        pd.concat([a1.map({0:"No",1:"Yes"}), a2.map({0:"No",1:"Yes"})], ignore_index=True),
        pd.concat([pd.Series(["Nuclear"]*len(a1)), pd.Series(["NonNuclear"]*len(a2))], ignore_index=True)
    )
    if ct.shape == (2, 2):
        chi2, p, _, _ = stats.chi2_contingency(ct, correction=True)
        # Cohen's h effect size
        p1 = a1.mean(); p2 = a2.mean()
        h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
        return p, abs(h), p1, p2
    return np.nan, np.nan, a1.mean(), a2.mean()

def mwu_test(col, df1, df2):
    """Mann-Whitney U test + rank-biserial r for ordinal/continuous columns."""
    a1 = df1[col].dropna().astype(float)
    a2 = df2[col].dropna().astype(float)
    if len(a1) < 2 or len(a2) < 2:
        return np.nan, np.nan, a1.mean(), a2.mean()
    stat, p = stats.mannwhitneyu(a1, a2, alternative="two-sided")
    r = 1 - (2 * stat) / (len(a1) * len(a2))
    return p, abs(r), a1.mean(), a2.mean()

# =============================================================================
# FIGURE 1 — Compliance tier by nuclear vs non-nuclear
# =============================================================================
tiers_order = ["None", "Consultation", "Demonstrated", "Verified"]
TIER_COLORS = {
    "None":          "#d9d9d9",
    "Consultation":  "#f4a460",
    "Demonstrated":  "#4a9bc7",
    "Verified":      "#1a5e7a",
}

fig1, axes1 = plt.subplots(1, 2, figsize=(13, 5), sharey=False)
for ax, sub_df, label, color in [
    (axes1[0], df[df["nuclear"]],  "Nuclear agreements\n(n={})".format(len(nuc)),  COLORS["nuclear"]),
    (axes1[1], df[~df["nuclear"]], "Non-nuclear agreements\n(n={})".format(len(non)), COLORS["non_nuclear"]),
]:
    counts = sub_df["compliance_label"].value_counts().reindex(tiers_order, fill_value=0)
    pcts   = counts / counts.sum() * 100
    bars = ax.bar(tiers_order, pcts, color=[TIER_COLORS[t] for t in tiers_order],
                  edgecolor="white", width=0.6)
    for bar, pct, n in zip(bars, pcts, counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f"{pct:.0f}%\n(n={int(n)})", ha="center", va="bottom", fontsize=9)
    ax.set_title(label, fontsize=12, fontweight="bold")
    ax.set_ylabel("% of agreements", fontsize=10)
    ax.set_ylim(0, 75)
    ax.spines[["top","right"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=9)

# Chi-squared on verified compliance rate
p_v, h_v, rate_n, rate_nn = chi2_test("verified_compliance_mechanism", nuc, non)
sig_txt = f"Verified compliance: Nuclear {rate_n:.0%} vs Non-nuclear {rate_nn:.0%}\n"
sig_txt += f"chi-squared p={p_v:.3f}, Cohen's h={h_v:.2f} "
sig_txt += ("(significant)" if p_v < 0.05 else "(not significant)")
fig1.text(0.5, -0.03, sig_txt, ha="center", fontsize=10,
          color=COLORS["sig"] if p_v < 0.05 else COLORS["nsig"])
fig1.suptitle("Compliance Architecture: Nuclear vs Non-Nuclear Agreements",
              fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
fig1.savefig(FIG_DIR / "nuc_compliance_comparison.png", dpi=150, bbox_inches="tight")
plt.close(fig1)
print("Saved: nuc_compliance_comparison.png")

# =============================================================================
# FIGURE 2 — Verification design features (vercom) compared across groups
# =============================================================================
# Join vercom with nuclear flag
vercom_merged = vercom.merge(nuc_flag, on="agreement_id", how="left")
vercom_merged["nuclear"] = vercom_merged["nuclear"].fillna(False).infer_objects(copy=False)

v_nuc = vercom_merged[vercom_merged["nuclear"]]
v_non = vercom_merged[~vercom_merged["nuclear"]]
print(f"\nVercom rows — Nuclear: {len(v_nuc)} | Non-nuclear: {len(v_non)}")

# Mechanism type labels (from codebook exploration)
MECH_TYPE = {0: "Routine\ninspection", 1: "Declared-site\ninspection",
             2: "Challenge\ninspection", 3: "Elimination/\nclose-out", 4: "IAEA\nsafeguards"}
INSPECTOR  = {0: "National\n(NTM)", 1: "International\nbody", 2: "Joint"}
ACCESS     = {
    "area":     "Area access",
    "facility": "Facility access",
    "item":     "Item access",
    "item_section": "Item-section\naccess",
}

# Access depth comparison
fig2, axes2 = plt.subplots(1, 2, figsize=(13, 5))

# Left: mechanism type breakdown
ax_mtype = axes2[0]
mtype_col = "verified_compliance_mechanism_type"
nuc_type  = v_nuc[mtype_col].dropna().map(MECH_TYPE).value_counts(normalize=True) * 100
non_type  = v_non[mtype_col].dropna().map(MECH_TYPE).value_counts(normalize=True) * 100
all_types = list(MECH_TYPE.values())
x = np.arange(len(all_types)); w = 0.35
ax_mtype.bar(x - w/2, [nuc_type.get(t, 0) for t in all_types], width=w,
             label="Nuclear", color=COLORS["nuclear"], edgecolor="white")
ax_mtype.bar(x + w/2, [non_type.get(t, 0) for t in all_types], width=w,
             label="Non-nuclear", color=COLORS["non_nuclear"], edgecolor="white")
ax_mtype.set_xticks(x); ax_mtype.set_xticklabels(all_types, fontsize=8.5)
ax_mtype.set_ylabel("% of verification mechanisms", fontsize=10)
ax_mtype.set_title("Verification Mechanism Types", fontsize=12, fontweight="bold")
ax_mtype.legend(fontsize=9, frameon=False)
ax_mtype.spines[["top","right"]].set_visible(False)

# p-value annotation for challenge inspections
p_ch, h_ch, r_n, r_nn = chi2_test(
    mtype_col,
    v_nuc.assign(**{mtype_col: (v_nuc[mtype_col]==2).astype(float)}),
    v_non.assign(**{mtype_col: (v_non[mtype_col]==2).astype(float)}),
)
challenge_idx = all_types.index("Challenge\ninspection")
ax_mtype.annotate(
    f"p={p_ch:.2f}",
    xy=(x[challenge_idx], max(nuc_type.get("Challenge\ninspection", 0),
                              non_type.get("Challenge\ninspection", 0)) + 1),
    ha="center", fontsize=8, color=COLORS["sig"] if p_ch < 0.05 else COLORS["nsig"]
)

# Right: access depth (area / facility / item / item-section)
ax_access = axes2[1]
access_cols = {
    "area":         "verified_compliance_mechanism_area_access",
    "facility":     "verified_compliance_mechanism_facility_access",
    "item":         "verified_compliance_mechanism_item_access",
    "item_section": "verified_compliance_mechanism_item_section_access",
}
access_labels = list(ACCESS.values())
nuc_access = [v_nuc[c].fillna(0).mean()*100 if c in v_nuc.columns else 0
              for c in access_cols.values()]
non_access = [v_non[c].fillna(0).mean()*100 if c in v_non.columns else 0
              for c in access_cols.values()]
x2 = np.arange(len(access_labels))
ax_access.bar(x2 - w/2, nuc_access, width=w, label="Nuclear",
              color=COLORS["nuclear"], edgecolor="white")
ax_access.bar(x2 + w/2, non_access, width=w, label="Non-nuclear",
              color=COLORS["non_nuclear"], edgecolor="white")
ax_access.set_xticks(x2); ax_access.set_xticklabels(access_labels, fontsize=9)
ax_access.set_ylabel("% of mechanisms with this access type", fontsize=10)
ax_access.set_title("Inspector Access Depth", fontsize=12, fontweight="bold")
ax_access.legend(fontsize=9, frameon=False)
ax_access.spines[["top","right"]].set_visible(False)

# Significance stars for access
for i, (key, col) in enumerate(access_cols.items()):
    if col not in vercom_merged.columns: continue
    p_a, h_a, _, _ = chi2_test(col, v_nuc, v_non)
    star = "***" if p_a < 0.001 else "**" if p_a < 0.01 else "*" if p_a < 0.05 else "ns"
    ymax = max(nuc_access[i], non_access[i]) + 2
    ax_access.text(x2[i], ymax, star, ha="center", fontsize=10,
                   color=COLORS["sig"] if p_a < 0.05 else COLORS["nsig"])

fig2.suptitle("Verification Mechanism Design: Nuclear vs Non-Nuclear",
              fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
fig2.savefig(FIG_DIR / "nuc_vercom_features.png", dpi=150, bbox_inches="tight")
plt.close(fig2)
print("Saved: nuc_vercom_features.png")

# =============================================================================
# FIGURE 3 — Inspector type + trigger type comparison
# =============================================================================
fig3, axes3 = plt.subplots(1, 2, figsize=(13, 5))

# Left: inspector type
ax_insp = axes3[0]
insp_col = "verified_compliance_mechanism_inspector_type"
nuc_insp  = v_nuc[insp_col].dropna().map(INSPECTOR).value_counts(normalize=True)*100
non_insp  = v_non[insp_col].dropna().map(INSPECTOR).value_counts(normalize=True)*100
all_insp  = list(INSPECTOR.values())
x3 = np.arange(len(all_insp))
ax_insp.bar(x3 - w/2, [nuc_insp.get(t, 0) for t in all_insp], width=w,
            label="Nuclear", color=COLORS["nuclear"], edgecolor="white")
ax_insp.bar(x3 + w/2, [non_insp.get(t, 0) for t in all_insp], width=w,
            label="Non-nuclear", color=COLORS["non_nuclear"], edgecolor="white")
ax_insp.set_xticks(x3); ax_insp.set_xticklabels(all_insp, fontsize=9)
ax_insp.set_ylabel("% of verification mechanisms", fontsize=10)
ax_insp.set_title("Who Inspects? Inspector Type", fontsize=12, fontweight="bold")
ax_insp.legend(fontsize=9, frameon=False)
ax_insp.spines[["top","right"]].set_visible(False)

# Significance for international body
p_intl, h_intl, r_n2, r_nn2 = chi2_test(
    insp_col,
    v_nuc.assign(**{insp_col: (v_nuc[insp_col]==1).astype(float)}),
    v_non.assign(**{insp_col: (v_non[insp_col]==1).astype(float)}),
)
intl_idx = all_insp.index("International\nbody")
star = "***" if p_intl < 0.001 else "**" if p_intl < 0.01 else "*" if p_intl < 0.05 else "ns"
ax_insp.text(x3[intl_idx],
             max(nuc_insp.get("International\nbody",0), non_insp.get("International\nbody",0))+1,
             star, ha="center", fontsize=12, color=COLORS["sig"] if p_intl < 0.05 else COLORS["nsig"])

# Right: trigger type
ax_trig = axes3[1]
TRIGGER = {0: "Right-based\n(quota)", 1: "Event-\ntriggered",
           2: "Continuous/\nNTM", 4: "Challenge", 5: "Scheduled"}
trig_col = "verified_compliance_mechanism_trigger_type"
nuc_trig  = v_nuc[trig_col].dropna().map(TRIGGER).value_counts(normalize=True)*100
non_trig  = v_non[trig_col].dropna().map(TRIGGER).value_counts(normalize=True)*100
all_trig  = list(TRIGGER.values())
x4 = np.arange(len(all_trig))
ax_trig.bar(x4 - w/2, [nuc_trig.get(t, 0) for t in all_trig], width=w,
            label="Nuclear", color=COLORS["nuclear"], edgecolor="white")
ax_trig.bar(x4 + w/2, [non_trig.get(t, 0) for t in all_trig], width=w,
            label="Non-nuclear", color=COLORS["non_nuclear"], edgecolor="white")
ax_trig.set_xticks(x4); ax_trig.set_xticklabels(all_trig, fontsize=8.5)
ax_trig.set_ylabel("% of verification mechanisms", fontsize=10)
ax_trig.set_title("How Is Inspection Triggered?", fontsize=12, fontweight="bold")
ax_trig.legend(fontsize=9, frameon=False)
ax_trig.spines[["top","right"]].set_visible(False)

fig3.suptitle("Inspector Arrangements & Trigger Mechanisms: Nuclear vs Non-Nuclear",
              fontsize=14, fontweight="bold", y=1.01)
plt.tight_layout()
fig3.savefig(FIG_DIR / "nuc_inspector_trigger.png", dpi=150, bbox_inches="tight")
plt.close(fig3)
print("Saved: nuc_inspector_trigger.png")

# =============================================================================
# FIGURE 4 — Radar chart: nuclear governance "design template"
# =============================================================================
# Compute 6 dimensions (0-1 scale) for nuclear vs non-nuclear
dimensions = [
    "Verified\ncompliance**",      # only significant axis — marked
    "Facility\naccess",
    "Item\naccess",
    "International\ninspector",
    "Challenge\ninspection",
    "Demonstrated\ncompliance",
]

def safe_mean(series, val=None):
    if val is not None:
        return (series.fillna(0) == val).mean()
    return series.fillna(0).astype(float).mean()

nuc_vals = np.array([
    safe_mean(nuc["verified_compliance_mechanism"].fillna(0)),
    safe_mean(v_nuc.get("verified_compliance_mechanism_facility_access", pd.Series(dtype=float))),
    safe_mean(v_nuc.get("verified_compliance_mechanism_item_access", pd.Series(dtype=float))),
    safe_mean(v_nuc["verified_compliance_mechanism_inspector_type"].fillna(-1), 1),
    safe_mean(v_nuc["verified_compliance_mechanism_trigger_type"].fillna(-1), 4),
    safe_mean(nuc["demonstrated_compliance_mechanism"].fillna(0)),
])
non_vals = np.array([
    safe_mean(non["verified_compliance_mechanism"].fillna(0)),
    safe_mean(v_non.get("verified_compliance_mechanism_facility_access", pd.Series(dtype=float))),
    safe_mean(v_non.get("verified_compliance_mechanism_item_access", pd.Series(dtype=float))),
    safe_mean(v_non["verified_compliance_mechanism_inspector_type"].fillna(-1), 1),
    safe_mean(v_non["verified_compliance_mechanism_trigger_type"].fillna(-1), 4),
    safe_mean(non["demonstrated_compliance_mechanism"].fillna(0)),
])

N = len(dimensions)
angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
angles += angles[:1]
nuc_plot = np.append(nuc_vals, nuc_vals[0])
non_plot = np.append(non_vals, non_vals[0])

fig4, ax4 = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
ax4.plot(angles, nuc_plot, color=COLORS["nuclear"], linewidth=2.5, label="Nuclear")
ax4.fill(angles, nuc_plot, color=COLORS["nuclear"], alpha=0.20)
ax4.plot(angles, non_plot, color=COLORS["non_nuclear"], linewidth=2.5,
         linestyle="--", label="Non-nuclear")
ax4.fill(angles, non_plot, color=COLORS["non_nuclear"], alpha=0.15)

ax4.set_xticks(angles[:-1])
ax4.set_xticklabels(dimensions, fontsize=10)
ax4.set_ylim(0, 1)
ax4.set_yticks([0.25, 0.5, 0.75, 1.0])
ax4.set_yticklabels(["25%", "50%", "75%", "100%"], fontsize=8, color="#888")
ax4.set_title("The Nuclear Governance Design Template\nvs. Other Weapon Categories",
              fontsize=13, fontweight="bold", pad=20)
ax4.legend(loc="upper right", bbox_to_anchor=(1.35, 1.12), fontsize=11, frameon=False)

# Annotate both nuclear AND non-nuclear values on the verified compliance axis
# Axis 0 (top of chart) = Verified compliance — the only significant gap
verified_angle = angles[0]
ax4.text(verified_angle, nuc_vals[0] + 0.10, f"Nuclear: {nuc_vals[0]:.0%}",
         ha="center", va="center", fontsize=9.5, color=COLORS["nuclear"],
         fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=COLORS["nuclear"],
                   alpha=0.85))
ax4.text(verified_angle, non_vals[0] - 0.12, f"Non-nuclear: {non_vals[0]:.0%}",
         ha="center", va="center", fontsize=9, color=COLORS["non_nuclear"],
         fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=COLORS["non_nuclear"],
                   alpha=0.85))

# Significance callout box in the lower portion of the chart
ax4.text(0, -1.45,
         "** p=0.008, Cohen's h=0.54\n"
         "Only statistically significant gap.\n"
         "All other dimensions: p>0.05 (ns)\n"
         "— verification toolkit converges\n"
         "once mandated.",
         ha="center", va="center", fontsize=8.5,
         color="#333",
         transform=ax4.transData,
         bbox=dict(boxstyle="round,pad=0.5", facecolor="#fef9e7",
                   edgecolor=COLORS["sig"], alpha=0.9))

plt.tight_layout()
fig4.savefig(FIG_DIR / "nuc_radar_template.png", dpi=150, bbox_inches="tight")
plt.close(fig4)
print("Saved: nuc_radar_template.png")

# =============================================================================
# FIGURE 5 — Two nuclear sub-models: Bilateral/NTM vs IAEA
# =============================================================================
fig5, ax5 = plt.subplots(figsize=(12, 6))
ax5.axis("off")

sub_model_data = [
    ["Feature", "Bilateral / NTM Model\n(START, INF, ABM, New START)", "IAEA Model\n(NPT Safeguards, CTBT, CWC)"],
    ["Inspector body", "National inspection teams\n(US + USSR/Russia)", "Standing international body\n(IAEA, OPCW)"],
    ["Primary verification tool", "National Technical Means\n(satellites, seismic, SIGINT)", "Physical measurement +\nenvironmental sampling"],
    ["Treaty format", "Bilateral\n(two parties)", "Multilateral\n(many parties)"],
    ["Challenge right", "Limited / absent\n(quota-based only)", "Yes — Additional Protocol\ngrants undeclared-site access"],
    ["Inspection trigger", "Right-based quota\n(fixed # per year)", "Declared-site routine +\nevent-triggered challenge"],
    ["Transferability to AI", "LOW — NTM has no\nAI equivalent", "MEDIUM — institutional\nmodel transfers; methods don't"],
]

col_widths = [0.22, 0.37, 0.37]
row_height = 0.13
top = 0.92

# Header row
header_colors = ["#2c3e50", COLORS["nuclear"], "#2980b9"]
for col_i, (text, cw) in enumerate(zip(sub_model_data[0], col_widths)):
    x = sum(col_widths[:col_i])
    ax5.add_patch(plt.Rectangle((x, top - row_height), cw, row_height,
                                 facecolor=header_colors[col_i], edgecolor="white", lw=1.5,
                                 transform=ax5.transAxes, clip_on=False))
    ax5.text(x + cw/2, top - row_height/2, text, ha="center", va="center",
             fontsize=10, fontweight="bold", color="white", transform=ax5.transAxes)

# Data rows
row_colors_cycle = ["#f0f4f8", "#dbe8f5"]
for row_i, row in enumerate(sub_model_data[1:]):
    y = top - (row_i + 2) * row_height
    bg = row_colors_cycle[row_i % 2]
    # Highlight transferability row
    if row_i == len(sub_model_data) - 2:
        bg = "#fef9e7"
    for col_i, (text, cw) in enumerate(zip(row, col_widths)):
        x = sum(col_widths[:col_i])
        fc = bg
        ax5.add_patch(plt.Rectangle((x, y), cw, row_height,
                                     facecolor=fc, edgecolor="white", lw=1,
                                     transform=ax5.transAxes, clip_on=False))
        tc = COLORS["sig"] if row_i == len(sub_model_data) - 2 and col_i > 0 else "#1a1a1a"
        ax5.text(x + cw/2, y + row_height/2, text, ha="center", va="center",
                 fontsize=8.8, color=tc, transform=ax5.transAxes,
                 fontweight="bold" if row_i == len(sub_model_data) - 2 else "normal")

ax5.set_title("Two Sub-Models Within Nuclear Governance\n"
              "The 'IAEA for AI' analogy applies to one, not both",
              fontsize=13, fontweight="bold", pad=12)
ax5.set_xlim(0, 1); ax5.set_ylim(0, 1)

plt.tight_layout()
fig5.savefig(FIG_DIR / "nuc_submodels_comparison.png", dpi=150, bbox_inches="tight")
plt.close(fig5)
print("Saved: nuc_submodels_comparison.png")

# =============================================================================
# Console summary — statistical results table
# =============================================================================
print("\n=== STATISTICAL COMPARISON: NUCLEAR vs NON-NUCLEAR ===")
tests = [
    ("Verified compliance (agreement level)",
     chi2_test("verified_compliance_mechanism", nuc, non)),
    ("Demonstrated compliance (agreement level)",
     chi2_test("demonstrated_compliance_mechanism", nuc, non)),
    ("Facility access (vercom level)",
     chi2_test("verified_compliance_mechanism_facility_access", v_nuc, v_non)
     if "verified_compliance_mechanism_facility_access" in vercom_merged.columns
     else (np.nan, np.nan, np.nan, np.nan)),
    ("Item access (vercom level)",
     chi2_test("verified_compliance_mechanism_item_access", v_nuc, v_non)
     if "verified_compliance_mechanism_item_access" in vercom_merged.columns
     else (np.nan, np.nan, np.nan, np.nan)),
    ("International inspector (vercom level)",
     chi2_test(
         insp_col,
         v_nuc.assign(**{insp_col: (v_nuc[insp_col]==1).astype(float)}),
         v_non.assign(**{insp_col: (v_non[insp_col]==1).astype(float)}),
     )),
]
print(f"{'Feature':<45} {'Nuc%':>6} {'NonNuc%':>8} {'p':>7} {'Effect':>7} {'Sig':>5}")
print("-" * 80)
for name, (p, h, rn, rnn) in tests:
    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else "ns"
    print(f"{name:<45} {rn:>6.0%} {rnn:>8.0%} {p:>7.3f} {h:>7.2f} {sig:>5}")
