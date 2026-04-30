"""
Challenge 4 — ML Extensions
AMC Research Sprint | April 2026

Three ML analyses + two targeted additions:
  A. Logistic Regression  — does nuclear status independently predict verified compliance?
  B. Clustering           — do nuclear-verified agreements form a natural cluster?
  C. Survival Analysis    — do nuclear agreements reach verified compliance faster?
  D. Nuclear Premium Over Time — is the 44% vs 20% gap a Cold War artifact or structural?
  E. Misclassification Table  — which treaties does the model get wrong, and why?

Outputs (analysis4/figures/):
  ml_nuc_regression_coefficients.png
  ml_nuc_clustering.png
  ml_nuc_survival_curves.png
  ml_nuc_decade_premium.png
  ml_nuc_misclassification.png
"""

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, roc_auc_score
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.stats import chi2_contingency
from lifelines import KaplanMeierFitter
from lifelines.statistics import logrank_test

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIG_DIR  = Path(__file__).resolve().parent / "figures"
FIG_DIR.mkdir(exist_ok=True)

COLORS = {"nuclear": "#1a5e7a", "non_nuclear": "#f4a460"}

# ── Load data ─────────────────────────────────────────────────────────────────
info    = pd.read_csv(DATA_DIR / "amcdata_agreement_info_V2.csv",     encoding="latin1")
weapons = pd.read_csv(DATA_DIR / "amcdata_weapons_facilities_V2.csv", encoding="latin1")

# ── Compliance score ──────────────────────────────────────────────────────────
def compliance_level(row):
    if row.get("verified_compliance_mechanism",    0) == 1: return 3
    if row.get("demonstrated_compliance_mechanism",0) == 1: return 2
    if row.get("consultation_mechanism",           0) == 1: return 1
    return 0

info["compliance_score"] = info.apply(compliance_level, axis=1)
info["verified_binary"]  = (info["compliance_score"] == 3).astype(int)

# ── Nuclear flag ──────────────────────────────────────────────────────────────
NUCLEAR_CATS = {
    "Nuclear Weapons", "ICBMs", "SLBMs",
    "ICBM Launchers", "SLBM Launchers",
    "Heavy Bombers", "Nuclear Submarines"
}
summary = (
    weapons[weapons["item"].str.contains("Summary Category", na=False)]
    [["agreement_id", "item"]].drop_duplicates()
)
summary["weapon_cat"] = summary["item"].str.extract(r"\((.+)\)")
nuclear_ids = set(
    summary[summary["weapon_cat"].isin(NUCLEAR_CATS)]["agreement_id"]
)
info["is_nuclear"] = info["agreement_id"].isin(nuclear_ids).astype(int)

print(f"Nuclear agreements: {info['is_nuclear'].sum()}")
print(f"Non-nuclear:        {(info['is_nuclear']==0).sum()}")
print(f"Verified compliance overall: {info['verified_binary'].sum()}")

# =============================================================================
# A. LOGISTIC REGRESSION
# Does nuclear status independently predict verified compliance after
# controlling for era, coalition size, and laterality?
# =============================================================================

feature_cols = {
    "is_nuclear":        "Nuclear Agreement",
    "year":              "Treaty Year",
    "laterality":        "Laterality\n(2=multilateral)",
    "log_signatories":   "Log(Signatories)",
    "log_parties":       "Log(State Parties)",
}

df = info.copy()
df["log_signatories"] = np.log1p(df["nr_signatory_states"].fillna(0))
df["log_parties"]     = np.log1p(df["nr_states_parties_total"].fillna(0))

X_raw = df[list(feature_cols.keys())].copy()
y     = df["verified_binary"]

imputer = SimpleImputer(strategy="median")
scaler  = StandardScaler()
X_imp   = imputer.fit_transform(X_raw)
X_sc    = scaler.fit_transform(X_imp)

model = LogisticRegression(solver="lbfgs", max_iter=1000, random_state=42)
model.fit(X_sc, y)

preds = model.predict(X_sc)
proba = model.predict_proba(X_sc)[:, 1]
acc   = (preds == y).mean()
auc   = roc_auc_score(y, proba)

coef_series = pd.Series(
    model.coef_[0],
    index=[feature_cols[c] for c in feature_cols.keys()]
).sort_values()

bar_colors = ["#c0392b" if v < 0 else "#1a5e7a" for v in coef_series.values]

fig_a, ax_a = plt.subplots(figsize=(9, 5))
bars = ax_a.barh(coef_series.index, coef_series.values,
                 color=bar_colors, edgecolor="white", height=0.55)
ax_a.axvline(0, color="#555", linewidth=0.8, linestyle="--")
ax_a.set_xlabel(
    "Logistic Regression Coefficient\nPositive = increases probability of verified compliance",
    fontsize=10
)
ax_a.set_title(
    "Does Nuclear Status Independently Predict Verified Compliance?\n"
    "Binary Logistic Regression (outcome: verified compliance = 1)",
    fontsize=12, fontweight="bold", pad=12
)
ax_a.spines[["top", "right"]].set_visible(False)

for bar, val in zip(bars, coef_series.values):
    ax_a.text(
        val + (0.015 if val >= 0 else -0.015),
        bar.get_y() + bar.get_height() / 2,
        f"{val:+.2f}", va="center",
        ha="left" if val >= 0 else "right",
        fontsize=9, color="#222"
    )

# Highlight nuclear bar
nuclear_label = feature_cols["is_nuclear"]
nuc_idx = list(coef_series.index).index(nuclear_label)
bars[nuc_idx].set_edgecolor("#f39c12")
bars[nuc_idx].set_linewidth(2.5)

ax_a.text(
    0.98, 0.04,
    f"Accuracy: {acc:.0%}  |  AUC: {auc:.2f}  |  n={len(y)}",
    transform=ax_a.transAxes, ha="right", fontsize=9,
    color="#555", style="italic"
)

plt.tight_layout()
fig_a.savefig(FIG_DIR / "ml_nuc_regression_coefficients.png", dpi=150, bbox_inches="tight")
plt.close(fig_a)
print(f"\nA. Logistic Regression — Accuracy: {acc:.0%}, AUC: {auc:.2f}")
print(f"   Nuclear coefficient: {coef_series[nuclear_label]:+.3f}")
print(f"   Interpretation: {'nuclear IS independently predictive' if coef_series[nuclear_label] > 0.1 else 'nuclear effect absorbed by other features'}")

# =============================================================================
# B. HIERARCHICAL CLUSTERING
# Do nuclear-verified agreements form a distinct natural cluster,
# or do they cluster with non-nuclear verified agreements?
# =============================================================================

cluster_features = pd.DataFrame({
    "compliance_score": df["compliance_score"],
    "is_nuclear":       df["is_nuclear"],
    "year":             df["year"].fillna(df["year"].median()),
    "laterality":       df["laterality"].fillna(1),
    "log_signatories":  df["log_signatories"],
    "log_parties":      df["log_parties"],
})

X_cl  = scaler.fit_transform(imputer.fit_transform(cluster_features))
Z     = linkage(X_cl, method="ward")
k     = 4
labels = fcluster(Z, k, criterion="maxclust")

# Cross-tab: cluster vs (nuclear × verified)
df["cluster"] = labels
df["group"] = "Other"
df.loc[(df["is_nuclear"] == 1) & (df["verified_binary"] == 1), "group"] = "Nuclear-Verified"
df.loc[(df["is_nuclear"] == 0) & (df["verified_binary"] == 1), "group"] = "Non-Nuclear Verified"
df.loc[(df["is_nuclear"] == 1) & (df["verified_binary"] == 0), "group"] = "Nuclear-Unverified"

cross = pd.crosstab(df["cluster"], df["group"])

fig_b, (ax_b1, ax_b2) = plt.subplots(1, 2, figsize=(14, 6),
                                       gridspec_kw={"width_ratios": [2, 1]})

dendrogram(Z, ax=ax_b1, truncate_mode="lastp", p=25,
           color_threshold=Z[-3, 2], leaf_font_size=7,
           above_threshold_color="#aaa")
ax_b1.set_title(
    "Hierarchical Clustering\n(Ward linkage, truncated to 25 leaves)",
    fontsize=11, fontweight="bold"
)
ax_b1.set_xlabel("Agreement cluster", fontsize=10)
ax_b1.set_ylabel("Distance", fontsize=10)
ax_b1.spines[["top", "right"]].set_visible(False)

# Heatmap
col_order = ["Nuclear-Verified", "Non-Nuclear Verified", "Nuclear-Unverified", "Other"]
col_order  = [c for c in col_order if c in cross.columns]
cross      = cross[col_order]

group_colors = {
    "Nuclear-Verified":     "#1a5e7a",
    "Non-Nuclear Verified": "#4a9bc7",
    "Nuclear-Unverified":   "#f4a460",
    "Other":                "#d9d9d9"
}

im = ax_b2.imshow(cross.values, cmap="Blues", aspect="auto")
ax_b2.set_xticks(range(len(cross.columns)))
ax_b2.set_xticklabels(cross.columns, rotation=30, ha="right", fontsize=8.5)
ax_b2.set_yticks(range(len(cross.index)))
ax_b2.set_yticklabels([f"Cluster {i}" for i in cross.index], fontsize=9)
ax_b2.set_title(
    "Cluster Composition\n(Do nuclear-verified agreements separate?)",
    fontsize=10, fontweight="bold"
)
for i in range(cross.shape[0]):
    for j in range(cross.shape[1]):
        v = cross.values[i, j]
        ax_b2.text(j, i, str(v), ha="center", va="center",
                   fontsize=10, fontweight="bold",
                   color="white" if v > cross.values.max() * 0.55 else "#333")

plt.colorbar(im, ax=ax_b2, fraction=0.046, pad=0.04)
plt.suptitle(
    "Do Nuclear-Verified Agreements Form a Natural Cluster?",
    fontsize=13, fontweight="bold", y=1.01
)
plt.tight_layout()
fig_b.savefig(FIG_DIR / "ml_nuc_clustering.png", dpi=150, bbox_inches="tight")
plt.close(fig_b)
print("\nB. Clustering complete.")
print(cross.to_string())

# =============================================================================
# C. SURVIVAL ANALYSIS — Kaplan-Meier
# How long does it take agreements to move from adoption to entry into force?
# Do nuclear agreements ratify faster or slower?
# Proxy for: does nuclear urgency accelerate commitment, or does complexity slow it?
# =============================================================================

# Parse dates
for col in ["adoption_date", "entry_into_force_date"]:
    info[col] = pd.to_datetime(info[col], errors="coerce", dayfirst=True)

survival_df = info.dropna(subset=["adoption_date"]).copy()
survival_df["entry_into_force_date"] = survival_df["entry_into_force_date"].fillna(
    pd.Timestamp("2023-01-01")  # right-censor at dataset end
)
survival_df["duration_days"] = (
    survival_df["entry_into_force_date"] - survival_df["adoption_date"]
).dt.days
survival_df = survival_df[survival_df["duration_days"] >= 0]

# Event = entered into force (1); censored = not yet in force (0)
survival_df["event"] = (
    info["entry_into_force_date"].notna() &
    (info["entry_into_force_date"] < pd.Timestamp("2023-01-01"))
).astype(int).reindex(survival_df.index).fillna(0)

nuclear_surv     = survival_df[survival_df["is_nuclear"] == 1]
non_nuclear_surv = survival_df[survival_df["is_nuclear"] == 0]

kmf_nuc = KaplanMeierFitter()
kmf_non = KaplanMeierFitter()

kmf_nuc.fit(
    nuclear_surv["duration_days"],
    event_observed=nuclear_surv["event"],
    label=f"Nuclear (n={len(nuclear_surv)})"
)
kmf_non.fit(
    non_nuclear_surv["duration_days"],
    event_observed=non_nuclear_surv["event"],
    label=f"Non-Nuclear (n={len(non_nuclear_surv)})"
)

# Log-rank test
results = logrank_test(
    nuclear_surv["duration_days"],
    non_nuclear_surv["duration_days"],
    event_observed_A=nuclear_surv["event"],
    event_observed_B=non_nuclear_surv["event"]
)

fig_c, ax_c = plt.subplots(figsize=(11, 6))

kmf_nuc.plot_survival_function(
    ax=ax_c, ci_show=True,
    color=COLORS["nuclear"], linewidth=2.5
)
kmf_non.plot_survival_function(
    ax=ax_c, ci_show=True,
    color=COLORS["non_nuclear"], linewidth=2.5, linestyle="--"
)

ax_c.set_xlabel("Days from Adoption to Entry into Force", fontsize=11)
ax_c.set_ylabel("Proportion Not Yet in Force", fontsize=11)
ax_c.set_title(
    "Survival Analysis: Time from Adoption to Entry into Force\n"
    "Do Nuclear Agreements Ratify Faster Than Non-Nuclear?",
    fontsize=12, fontweight="bold", pad=12
)
ax_c.set_xlim(left=0)
ax_c.spines[["top", "right"]].set_visible(False)

# Median survival times
med_nuc = kmf_nuc.median_survival_time_
med_non = kmf_non.median_survival_time_

# Annotate medians
if not np.isinf(med_nuc):
    ax_c.axvline(med_nuc, color=COLORS["nuclear"],
                 linewidth=1.2, linestyle=":", alpha=0.7)
    ax_c.text(med_nuc + 30, 0.52,
              f"Median\n{int(med_nuc)}d\n({int(med_nuc/365.25)}yr)",
              color=COLORS["nuclear"], fontsize=8.5)

if not np.isinf(med_non):
    ax_c.axvline(med_non, color=COLORS["non_nuclear"],
                 linewidth=1.2, linestyle=":", alpha=0.7)
    ax_c.text(med_non + 30, 0.42,
              f"Median\n{int(med_non)}d\n({int(med_non/365.25)}yr)",
              color=COLORS["non_nuclear"], fontsize=8.5)

# Log-rank p-value
sig = "***" if results.p_value < 0.001 else \
      "**"  if results.p_value < 0.01  else \
      "*"   if results.p_value < 0.05  else "ns"

ax_c.text(
    0.97, 0.08,
    f"Log-rank p = {results.p_value:.3f} {sig}",
    transform=ax_c.transAxes, ha="right", fontsize=10,
    bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#aaa")
)

ax_c.legend(fontsize=10, loc="upper right")
plt.tight_layout()
fig_c.savefig(FIG_DIR / "ml_nuc_survival_curves.png", dpi=150, bbox_inches="tight")
plt.close(fig_c)

print(f"\nC. Survival Analysis")
print(f"   Nuclear median time-to-force:     {med_nuc:.0f} days ({med_nuc/365.25:.1f} yrs)")
print(f"   Non-nuclear median time-to-force: {med_non:.0f} days ({med_non/365.25:.1f} yrs)")
print(f"   Log-rank p-value: {results.p_value:.4f} {sig}")

# =============================================================================
# Summary printout
# =============================================================================
print("\n" + "="*60)
print("ML EXTENSIONS SUMMARY — Challenge 4")
print("="*60)
print(f"\nA. Logistic Regression")
print(f"   Nuclear coefficient:  {coef_series[nuclear_label]:+.3f}")
print(f"   Accuracy: {acc:.0%}  |  AUC: {auc:.2f}")
print(f"\nB. Clustering — see heatmap for nuclear-verified cluster purity")
print(f"\nC. Survival Analysis")
print(f"   Nuclear ratifies in {med_nuc/365.25:.1f} yrs vs "
      f"Non-nuclear {med_non/365.25:.1f} yrs  (log-rank p={results.p_value:.3f})")
interpretation = (
    "Nuclear agreements take LONGER — political complexity hypothesis supported"
    if med_nuc > med_non else
    "Nuclear agreements ratify FASTER — Cold War urgency hypothesis supported"
)
print(f"   -> {interpretation}")

# =============================================================================
# D. NUCLEAR PREMIUM OVER TIME
# Is the 44% vs 20% verification gap a Cold War artifact or a persistent
# structural feature? Decade-by-decade rates for nuclear vs non-nuclear.
# =============================================================================

df["decade"] = (df["year"] // 10 * 10).astype(int)

# Rate of verified compliance per decade × nuclear group
decade_stats = []
for decade, ddf in df.groupby("decade"):
    for is_nuc, label in [(1, "Nuclear"), (0, "Non-nuclear")]:
        sub = ddf[ddf["is_nuclear"] == is_nuc]
        if len(sub) == 0:
            continue
        rate = sub["verified_binary"].mean()
        n    = len(sub)
        decade_stats.append({
            "decade":  decade,
            "group":   label,
            "rate":    rate,
            "n":       n,
        })

dstats = pd.DataFrame(decade_stats)
dstats = dstats[dstats["decade"] >= 1940]   # enough agreements from 1940s onward

# Only include decades where BOTH groups have at least one agreement
both_present = (
    dstats.groupby("decade")["group"].nunique() == 2
)
valid_decades = both_present[both_present].index
dstats = dstats[dstats["decade"].isin(valid_decades)]

decades      = sorted(dstats["decade"].unique())
nuc_rates    = dstats[dstats["group"] == "Nuclear"].set_index("decade")["rate"]
non_rates    = dstats[dstats["group"] == "Non-nuclear"].set_index("decade")["rate"]
nuc_ns       = dstats[dstats["group"] == "Nuclear"].set_index("decade")["n"]
non_ns       = dstats[dstats["group"] == "Non-nuclear"].set_index("decade")["n"]

x    = np.arange(len(decades))
w    = 0.35
gap  = nuc_rates.reindex(decades).values - non_rates.reindex(decades).fillna(0).values

fig_d, (ax_d1, ax_d2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True,
                                       gridspec_kw={"height_ratios": [2.5, 1]})

# Top panel: side-by-side bars by decade
bars_nuc = ax_d1.bar(x - w/2,
                      nuc_rates.reindex(decades).values * 100,
                      width=w, color=COLORS["nuclear"], edgecolor="white",
                      label="Nuclear")
bars_non = ax_d1.bar(x + w/2,
                      non_rates.reindex(decades).fillna(0).values * 100,
                      width=w, color=COLORS["non_nuclear"], edgecolor="white",
                      label="Non-nuclear")

# Label bars with n=
for i, dec in enumerate(decades):
    nn = nuc_ns.get(dec, 0)
    nx = non_ns.get(dec, 0)
    nr = nuc_rates.get(dec, 0) * 100
    xr = non_rates.get(dec, 0) * 100
    if nn > 0:
        ax_d1.text(i - w/2, nr + 1.5, f"n={int(nn)}", ha="center",
                   fontsize=7.5, color=COLORS["nuclear"])
    if nx > 0:
        ax_d1.text(i + w/2, xr + 1.5, f"n={int(nx)}", ha="center",
                   fontsize=7.5, color=COLORS["non_nuclear"])

ax_d1.set_ylabel("% with verified compliance", fontsize=11)
ax_d1.set_ylim(0, 105)
ax_d1.legend(fontsize=10, frameon=False)
ax_d1.spines[["top","right"]].set_visible(False)
ax_d1.set_title(
    "Nuclear Premium Over Time: Is the Verification Gap a Cold War Artifact?\n"
    "% of agreements with verified compliance by decade and weapon type",
    fontsize=12, fontweight="bold", pad=12
)

# Shade Cold War era
cw_start = decades.index(1940) if 1940 in decades else 0
cw_end   = decades.index(1990) if 1990 in decades else len(decades) - 1
ax_d1.axvspan(cw_start - 0.5, cw_end + 0.5,
              alpha=0.07, color="#1a5e7a", label="Cold War era")
ax_d1.text((cw_start + cw_end) / 2, 97, "Cold War era (1945-1991)",
           ha="center", fontsize=8.5, color=COLORS["nuclear"], style="italic")

# Bottom panel: gap line
gap_vals = [g * 100 for g in gap]
ax_d2.bar(x, gap_vals,
          color=[COLORS["nuclear"] if g > 0 else "#c0392b" for g in gap_vals],
          edgecolor="white", alpha=0.75)
ax_d2.axhline(0, color="#555", linewidth=0.8)
ax_d2.set_ylabel("Gap\n(Nuc - NonNuc pp)", fontsize=9)
ax_d2.set_xticks(x)
ax_d2.set_xticklabels([str(d) + "s" for d in decades], fontsize=10)
ax_d2.spines[["top","right"]].set_visible(False)
ax_d2.set_xlabel("Decade", fontsize=11)

# Annotate overall gap
ax_d2.axhline(
    (nuc_rates.mean() - non_rates.mean()) * 100,
    color=COLORS["nuclear"], linewidth=1.2, linestyle="--", alpha=0.5
)
ax_d2.text(len(decades) - 0.5,
           (nuc_rates.mean() - non_rates.mean()) * 100 + 1.5,
           f"Overall avg gap: {(nuc_rates.mean()-non_rates.mean())*100:.0f}pp",
           ha="right", fontsize=8, color=COLORS["nuclear"])

plt.tight_layout()
fig_d.savefig(FIG_DIR / "ml_nuc_decade_premium.png", dpi=150, bbox_inches="tight")
plt.close(fig_d)

print(f"\nD. Nuclear Premium Over Time")
for dec in decades:
    nr = nuc_rates.get(dec, float("nan")) * 100
    xr = non_rates.get(dec, float("nan")) * 100
    print(f"   {dec}s: Nuclear {nr:.0f}%  Non-nuclear {xr:.0f}%  gap={nr-xr:+.0f}pp")
print("   Saved: ml_nuc_decade_premium.png")

# =============================================================================
# E. MISCLASSIFICATION TABLE
# Which specific agreements does the model get wrong?
# False positives = "policy gaps"  (profile predicts verification, none exists)
# False negatives = "overachievers" (low-nuclear profile, but has verification)
# =============================================================================

df["predicted_prob"] = model.predict_proba(X_sc)[:, 1]
df["predicted"]      = model.predict(X_sc)
df["correct"]        = (df["predicted"] == df["verified_binary"])

false_pos = df[(df["predicted"] == 1) & (df["verified_binary"] == 0)].copy()
false_neg = df[(df["predicted"] == 0) & (df["verified_binary"] == 1)].copy()
# df is already a copy of info, so title_short is already present — no extra merge needed

def shorten(title, n=42):
    if not isinstance(title, str): return "—"
    return title[:n] + "..." if len(title) > n else title

# Build combined table rows
rows = []
for _, r in false_pos.nlargest(5, "predicted_prob").iterrows():
    rows.append({
        "Type":        "Policy Gap",
        "Treaty":      shorten(r.get("title_short", "—")),
        "Year":        int(r["year"]) if pd.notna(r["year"]) else "?",
        "Nuclear":     "Yes" if r["is_nuclear"] else "No",
        "Pred. prob.": f"{r['predicted_prob']:.2f}",
        "Actual":      "None/Low",
    })
for _, r in false_neg.nsmallest(5, "predicted_prob").iterrows():
    rows.append({
        "Type":        "Overachiever",
        "Treaty":      shorten(r.get("title_short", "—")),
        "Year":        int(r["year"]) if pd.notna(r["year"]) else "?",
        "Nuclear":     "Yes" if r["is_nuclear"] else "No",
        "Pred. prob.": f"{r['predicted_prob']:.2f}",
        "Actual":      "Verified",
    })

mis_df = pd.DataFrame(rows)

fig_e, ax_e = plt.subplots(figsize=(13, 5))
ax_e.axis("off")

col_labels = list(mis_df.columns)
cell_vals  = mis_df.values.tolist()

tbl = ax_e.table(
    cellText=cell_vals,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
    bbox=[0, 0, 1, 1]
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.auto_set_column_width(range(len(col_labels)))

TYPE_COLORS = {"Policy Gap": "#fde8e8", "Overachiever": "#e8f4e8"}
for (row_i, col_i), cell in tbl.get_celld().items():
    cell.set_edgecolor("#ddd")
    if row_i == 0:
        cell.set_facecolor("#2c3e50")
        cell.set_text_props(color="white", fontweight="bold")
    else:
        row_type = cell_vals[row_i - 1][0]
        cell.set_facecolor(TYPE_COLORS.get(row_type, "white"))

ax_e.set_title(
    "Model Misclassifications — What the Logistic Regression Gets Wrong\n"
    "Policy Gaps (predicted verified, no mechanism) vs Overachievers (predicted low, has mechanism)",
    fontsize=11, fontweight="bold", pad=12
)

plt.tight_layout()
fig_e.savefig(FIG_DIR / "ml_nuc_misclassification.png", dpi=150, bbox_inches="tight")
plt.close(fig_e)

print(f"\nE. Misclassification Table")
print(f"   False positives (policy gaps):  {len(false_pos)}")
print(f"   False negatives (overachievers): {len(false_neg)}")
print(mis_df.to_string(index=False))
print("   Saved: ml_nuc_misclassification.png")

# =============================================================================
# Final summary
# =============================================================================
print("\n" + "="*60)
print("ALL OUTPUTS — Challenge 4 ML Extensions")
print("="*60)
for fname in sorted(FIG_DIR.glob("ml_nuc_*.png")):
    print(f"  {fname.name}")