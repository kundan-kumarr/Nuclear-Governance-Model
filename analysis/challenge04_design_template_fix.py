from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / 'data'
ANALYSIS_DIR = Path(__file__).resolve().parent

OUT_CSV = ANALYSIS_DIR / 'challenge04_design_template_fix_tables.csv'
OUT_MD = ANALYSIS_DIR / 'challenge04_design_template_fix.md'

info = pd.read_csv(DATA_DIR / 'amcdata_agreement_info_V2.csv', encoding='latin1')
weapons = pd.read_csv(DATA_DIR / 'amcdata_weapons_facilities_V2.csv', encoding='latin1')
vercom = pd.read_csv(DATA_DIR / 'amcdata_vercom_V2.csv', encoding='latin1')

NUCLEAR_CATS = {
    'Nuclear Weapons', 'ICBMs', 'SLBMs',
    'ICBM Launchers', 'SLBM Launchers',
    'Heavy Bombers', 'Nuclear Submarines'
}

summary = weapons[weapons['item'].astype(str).str.contains('Summary Category', na=False)][['agreement_id', 'item']].drop_duplicates()
summary['weapon_cat'] = summary['item'].str.extract(r'\((.+)\)')
nuclear_ids = set(summary[summary['weapon_cat'].isin(NUCLEAR_CATS)]['agreement_id'])
info['is_nuclear'] = info['agreement_id'].isin(nuclear_ids).astype(int)

ver = vercom.merge(info[['agreement_id', 'is_nuclear']], on='agreement_id', how='left')
v_nuc = ver[ver['is_nuclear'] == 1].copy()
v_non = ver[ver['is_nuclear'] == 0].copy()
nuc = info[info['is_nuclear'] == 1].copy()
non = info[info['is_nuclear'] == 0].copy()


def compliance_level(row):
    if row.get('verified_compliance_mechanism', 0) == 1:
        return 3
    if row.get('demonstrated_compliance_mechanism', 0) == 1:
        return 2
    if row.get('consultation_mechanism', 0) == 1:
        return 1
    return 0


info['compliance_score'] = info.apply(compliance_level, axis=1)
nuc = info[info['is_nuclear'] == 1].copy()
non = info[info['is_nuclear'] == 0].copy()


def sig_star(p):
    if pd.isna(p):
        return 'ns'
    if p < 0.001:
        return '***'
    if p < 0.01:
        return '**'
    if p < 0.05:
        return '*'
    return 'ns'


def cohens_h(p1, p2):
    p1 = min(max(float(p1), 0.0), 1.0)
    p2 = min(max(float(p2), 0.0), 1.0)
    return 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))


def binary_test(df1, df2, col):
    a1 = pd.to_numeric(df1[col], errors="coerce").fillna(0)
    a2 = pd.to_numeric(df2[col], errors="coerce").fillna(0)
    a1 = (a1 > 0).astype(float)
    a2 = (a2 > 0).astype(float)
    p1 = a1.mean()
    p2 = a2.mean()
    ct = pd.crosstab(pd.Series(['nuclear'] * len(a1) + ['non_nuclear'] * len(a2)),
                     pd.concat([a1, a2], ignore_index=True))
    if ct.shape == (2, 2):
        _, p, _, _ = chi2_contingency(ct, correction=True)
        h = cohens_h(p1, p2)
    else:
        p = np.nan
        h = np.nan
    return p1, p2, p, h


def categorical_test(df1, df2, col, mapping):
    s1 = df1[col].dropna().map(mapping).fillna('Other')
    s2 = df2[col].dropna().map(mapping).fillna('Other')
    levels = list(dict.fromkeys(list(mapping.values()) + ['Other']))
    c1 = s1.value_counts(normalize=True).reindex(levels, fill_value=0.0)
    c2 = s2.value_counts(normalize=True).reindex(levels, fill_value=0.0)
    ct = pd.concat([s1, s2], keys=['nuclear', 'non_nuclear']).reset_index(level=0).rename(columns={'level_0': 'group', col: 'value'})
    ctab = pd.crosstab(ct['group'], ct[0] if 0 in ct.columns else ct['value'])
    if ctab.shape[0] == 2 and ctab.shape[1] >= 2:
        _, p, _, _ = chi2_contingency(ctab, correction=False)
    else:
        p = np.nan
    rows = []
    for level in levels:
        rows.append({
            'section': col,
            'feature': level,
            'nuclear_pct': c1[level] * 100,
            'non_nuclear_pct': c2[level] * 100,
            'gap_pp': (c1[level] - c2[level]) * 100,
            'p_value': p,
            'effect_size_h': cohens_h(c1[level], c2[level]),
            'sig': sig_star(p),
            'test_scope': 'overall categorical chi-squared'
        })
    return rows


tables = []

# Compliance dimensions asked for in the brief.
compliance_cols = [
    ('Verified compliance', 'verified_compliance_mechanism'),
    ('Demonstrated compliance', 'demonstrated_compliance_mechanism'),
    ('Consultation mechanism', 'consultation_mechanism'),
]
for label, col in compliance_cols:
    p1, p2, p, h = binary_test(nuc, non, col)
    tables.append({
        'section': 'compliance',
        'feature': label,
        'nuclear_pct': p1 * 100,
        'non_nuclear_pct': p2 * 100,
        'gap_pp': (p1 - p2) * 100,
        'p_value': p,
        'effect_size_h': h,
        'sig': sig_star(p),
        'test_scope': 'binary chi-squared with Yates'
    })

# Access provisions.
access_cols = [
    ('Area access', 'verified_compliance_mechanism_area_access'),
    ('Facility access', 'verified_compliance_mechanism_facility_access'),
    ('Item access', 'verified_compliance_mechanism_item_access'),
    ('Item-section access', 'verified_compliance_mechanism_item_section_access'),
]
for label, col in access_cols:
    p1, p2, p, h = binary_test(v_nuc, v_non, col)
    tables.append({
        'section': 'access',
        'feature': label,
        'nuclear_pct': p1 * 100,
        'non_nuclear_pct': p2 * 100,
        'gap_pp': (p1 - p2) * 100,
        'p_value': p,
        'effect_size_h': h,
        'sig': sig_star(p),
        'test_scope': 'binary chi-squared with Yates'
    })

INSPECTOR = {0: 'National/NTM', 1: 'International body', 2: 'Joint'}
TRIGGER = {0: 'Right-based quota', 1: 'Event-triggered', 2: 'Continuous/NTM', 4: 'Challenge', 5: 'Scheduled', 7: 'Other'}
AG_TRIGGER = {0.0: 'Unspecified', 1.0: 'Quota', 2.0: 'Cyclical', 3.0: 'Upon notification', 4.0: 'Other'}

tables.extend(categorical_test(v_nuc, v_non, 'verified_compliance_mechanism_inspector_type', INSPECTOR))
tables.extend(categorical_test(v_nuc, v_non, 'verified_compliance_mechanism_trigger_type', TRIGGER))
tables.extend(categorical_test(v_nuc, v_non, 'verified_compliance_mechanism_agreement_trigger_type', AG_TRIGGER))

# Binary trigger subfeatures for direct prompt alignment.
for label, col in [
    ('Quota trigger flag', 'verified_compliance_mechanism_agreement_trigger_qouta'),
    ('Cyclical trigger flag', 'verified_compliance_mechanism_agreement_trigger_cyclical'),
    ('Upon-notification trigger flag', 'verified_compliance_mechanism_agreement_trigger_upon_notification'),
]:
    p1, p2, p, h = binary_test(v_nuc, v_non, col)
    tables.append({
        'section': 'trigger_flags',
        'feature': label,
        'nuclear_pct': p1 * 100,
        'non_nuclear_pct': p2 * 100,
        'gap_pp': (p1 - p2) * 100,
        'p_value': p,
        'effect_size_h': h,
        'sig': sig_star(p),
        'test_scope': 'binary chi-squared with Yates'
    })

out = pd.DataFrame(tables)
out.to_csv(OUT_CSV, index=False)

# Narrative summary for the markdown supplement.
comp = out[(out['section'] == 'compliance')].copy()
access = out[(out['section'] == 'access')].copy()
insp = out[out['section'] == 'verified_compliance_mechanism_inspector_type'].copy()
trig = out[out['section'] == 'verified_compliance_mechanism_trigger_type'].copy()
trig_flags = out[out['section'] == 'trigger_flags'].copy()

sig_rows = out[out['sig'] != 'ns'].copy().sort_values('p_value')
shared_rows = out[(out['sig'] == 'ns') & (out['gap_pp'].abs() <= 10)].copy()

summary_lines = []
if sig_rows.empty:
    summary_lines.append('- No additional statistically significant nuclear/non-nuclear differences were detected beyond the main verified-compliance result.')
else:
    for _, row in sig_rows.head(8).iterrows():
        summary_lines.append(
            f"- {row['feature']}: nuclear {row['nuclear_pct']:.1f}% vs non-nuclear {row['non_nuclear_pct']:.1f}% (gap {row['gap_pp']:+.1f} pp, p={row['p_value']:.3f}, h={row['effect_size_h']:.2f}, {row['sig']})"
        )

shared_lines = []
for _, row in shared_rows.head(8).iterrows():
    shared_lines.append(
        f"- {row['feature']}: nuclear {row['nuclear_pct']:.1f}% vs non-nuclear {row['non_nuclear_pct']:.1f}% (gap {row['gap_pp']:+.1f} pp, ns)"
    )

md = f"""# Challenge 4 Fix Supplement: Explicit Design-Template Tables

This supplement directly addresses the parts of the Challenge 4 brief that were under-emphasized in the main writeup: **inspector arrangements**, **access provisions**, and **trigger mechanisms** as separate empirical dimensions.

Files:
- `analysis4/challenge04_design_template_fix.py`
- `analysis4/challenge04_design_template_fix_tables.csv`

## What This Fix Adds

1. A direct nuclear vs non-nuclear table for **compliance mechanism types**.
2. A separate table for **access provisions**.
3. A separate category analysis for **inspector arrangements**.
4. A separate category analysis for **trigger mechanisms**, including agreement-trigger flags.
5. A short distinction between features that look **nuclear-specific** and features that appear **shared** across weapon categories.

## Compliance Mechanism Types

| Feature | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
"""
for _, row in comp.iterrows():
    md += f"| {row['feature']} | {row['nuclear_pct']:.1f} | {row['non_nuclear_pct']:.1f} | {row['gap_pp']:+.1f} | {row['p_value']:.3f} | {row['effect_size_h']:.2f} | {row['sig']} |\n"

md += "\n## Access Provisions\n\n| Feature | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |\n|---|---:|---:|---:|---:|---:|---|\n"
for _, row in access.iterrows():
    md += f"| {row['feature']} | {row['nuclear_pct']:.1f} | {row['non_nuclear_pct']:.1f} | {row['gap_pp']:+.1f} | {row['p_value']:.3f} | {row['effect_size_h']:.2f} | {row['sig']} |\n"

md += "\n## Inspector Arrangements\n\nOverall category test is reported in the p-value column for each row.\n\n| Inspector type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |\n|---|---:|---:|---:|---:|---:|---|\n"
for _, row in insp.iterrows():
    p_txt = 'nan' if pd.isna(row['p_value']) else f"{row['p_value']:.3f}"
    md += f"| {row['feature']} | {row['nuclear_pct']:.1f} | {row['non_nuclear_pct']:.1f} | {row['gap_pp']:+.1f} | {p_txt} | {row['effect_size_h']:.2f} | {row['sig']} |\n"

md += "\n## Trigger Mechanisms\n\n### A. Mechanism trigger type\n\n| Trigger type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |\n|---|---:|---:|---:|---:|---:|---|\n"
for _, row in trig.iterrows():
    p_txt = 'nan' if pd.isna(row['p_value']) else f"{row['p_value']:.3f}"
    md += f"| {row['feature']} | {row['nuclear_pct']:.1f} | {row['non_nuclear_pct']:.1f} | {row['gap_pp']:+.1f} | {p_txt} | {row['effect_size_h']:.2f} | {row['sig']} |\n"

md += "\n### B. Agreement-trigger flags\n\n| Trigger flag | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |\n|---|---:|---:|---:|---:|---:|---|\n"
for _, row in trig_flags.iterrows():
    p_txt = 'nan' if pd.isna(row['p_value']) else f"{row['p_value']:.3f}"
    md += f"| {row['feature']} | {row['nuclear_pct']:.1f} | {row['non_nuclear_pct']:.1f} | {row['gap_pp']:+.1f} | {p_txt} | {row['effect_size_h']:.2f} | {row['sig']} |\n"

md += "\n## Nuclear-Specific vs Shared Features\n\n### Features that look more nuclear-specific\n"
md += '\n'.join(summary_lines) + '\n'
md += "\n### Features that look shared across weapon categories\n"
md += ('\n'.join(shared_lines) if shared_lines else '- No low-gap shared features met the reporting rule.') + '\n'
md += "\n## How This Fix Aligns the Project to the Brief\n\nThe original analysis already addressed the broad question well, but this supplement makes the alignment explicit by presenting the challenge's requested governance dimensions as separate empirical sections: compliance mechanism types, inspector arrangements, access provisions, and trigger mechanisms.\n"

OUT_MD.write_text(md, encoding='utf-8')
print(f'Saved: {OUT_CSV.name}')
print(f'Saved: {OUT_MD.name}')

