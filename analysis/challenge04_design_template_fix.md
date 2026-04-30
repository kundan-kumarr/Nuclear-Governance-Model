# Challenge 4 Fix Supplement: Explicit Design-Template Tables

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
| Verified compliance | 44.4 | 19.6 | +24.9 | 0.008 | 0.54 | ** |
| Demonstrated compliance | 47.2 | 44.6 | +2.7 | 0.941 | 0.05 | ns |
| Consultation mechanism | 66.7 | 44.6 | +22.1 | 0.040 | 0.45 | * |

## Access Provisions

| Feature | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Area access | 26.8 | 25.6 | +1.2 | 1.000 | 0.03 | ns |
| Facility access | 53.6 | 60.5 | -6.9 | 0.630 | -0.14 | ns |
| Item access | 46.4 | 39.5 | +6.9 | 0.630 | 0.14 | ns |
| Item-section access | 1.8 | 0.0 | +1.8 | 1.000 | 0.27 | ns |

## Inspector Arrangements

Overall category test is reported in the p-value column for each row.

| Inspector type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| National/NTM | 83.9 | 72.1 | +11.8 | 0.350 | 0.29 | ns |
| International body | 8.9 | 14.0 | -5.0 | 0.350 | -0.16 | ns |
| Joint | 7.1 | 14.0 | -6.8 | 0.350 | -0.22 | ns |
| Other | 0.0 | 0.0 | +0.0 | 0.350 | 0.00 | ns |

## Trigger Mechanisms

### A. Mechanism trigger type

| Trigger type | Nuclear % | Non-Nuclear % | Gap (pp) | overall p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Right-based quota | 39.3 | 44.2 | -4.9 | 0.668 | -0.10 | ns |
| Event-triggered | 33.9 | 23.3 | +10.7 | 0.668 | 0.24 | ns |
| Continuous/NTM | 10.7 | 11.6 | -0.9 | 0.668 | -0.03 | ns |
| Challenge | 7.1 | 4.7 | +2.5 | 0.668 | 0.11 | ns |
| Scheduled | 8.9 | 14.0 | -5.0 | 0.668 | -0.16 | ns |
| Other | 0.0 | 2.3 | -2.3 | 0.668 | -0.31 | ns |

### B. Agreement-trigger flags

| Trigger flag | Nuclear % | Non-Nuclear % | Gap (pp) | p-value | Cohen's h | Sig |
|---|---:|---:|---:|---:|---:|---|
| Quota trigger flag | 0.0 | 0.0 | +0.0 | nan | nan | ns |
| Cyclical trigger flag | 0.0 | 0.0 | +0.0 | nan | nan | ns |
| Upon-notification trigger flag | 0.0 | 0.0 | +0.0 | nan | nan | ns |

## Nuclear-Specific vs Shared Features

### Features that look more nuclear-specific
- Verified compliance: nuclear 44.4% vs non-nuclear 19.6% (gap +24.9 pp, p=0.008, h=0.54, **)
- Consultation mechanism: nuclear 66.7% vs non-nuclear 44.6% (gap +22.1 pp, p=0.040, h=0.45, *)

### Features that look shared across weapon categories
- Demonstrated compliance: nuclear 47.2% vs non-nuclear 44.6% (gap +2.7 pp, ns)
- Area access: nuclear 26.8% vs non-nuclear 25.6% (gap +1.2 pp, ns)
- Facility access: nuclear 53.6% vs non-nuclear 60.5% (gap -6.9 pp, ns)
- Item access: nuclear 46.4% vs non-nuclear 39.5% (gap +6.9 pp, ns)
- Item-section access: nuclear 1.8% vs non-nuclear 0.0% (gap +1.8 pp, ns)
- International body: nuclear 8.9% vs non-nuclear 14.0% (gap -5.0 pp, ns)
- Joint: nuclear 7.1% vs non-nuclear 14.0% (gap -6.8 pp, ns)
- Other: nuclear 0.0% vs non-nuclear 0.0% (gap +0.0 pp, ns)

## How This Fix Aligns the Project to the Brief

The original analysis already addressed the broad question well, but this supplement makes the alignment explicit by presenting the challenge's requested governance dimensions as separate empirical sections: compliance mechanism types, inspector arrangements, access provisions, and trigger mechanisms.
