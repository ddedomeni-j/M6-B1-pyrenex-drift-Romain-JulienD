"""Détection de dérive — PSI, KS, Chi² (SQUELETTE À COMPLÉTER).

Trois méthodes complémentaires. Mini-cours : `01_PSI_KS_Chi2_essentiel.md`.
N'inventez pas vos métriques : PSI (formule ci-dessous), KS et Chi² sont dans
scipy.stats.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, ks_2samp

PSI_STABLE = 0.10
PSI_DRIFT = 0.25


def population_stability_index(reference: pd.Series, current: pd.Series, n_bins: int = 10) -> float:
    """PSI entre référence et courant.

    PSI = Σ (p_cur - p_ref) * ln(p_cur / p_ref), bornes des bins = quantiles de
    la référence. ⚠️ pensez au lissage anti-zéro (sinon ln(0) / division par 0).
    """
    ref = pd.to_numeric(reference, errors="coerce").dropna().to_numpy()
    cur = pd.to_numeric(current, errors="coerce").dropna().to_numpy()

    if len(ref) == 0 or len(cur) == 0:
        return np.nan

    edges = np.unique(np.quantile(ref, np.linspace(0, 1, n_bins + 1)))
    if len(edges) < 2:
        return 0.0

    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts = np.histogram(ref, bins=edges)[0]
    cur_counts = np.histogram(cur, bins=edges)[0]

    eps = 1e-6
    ref_proportions = ref_counts / ref_counts.sum() + eps
    cur_proportions = cur_counts / cur_counts.sum() + eps
    ref_proportions = ref_proportions / ref_proportions.sum()
    cur_proportions = cur_proportions / cur_proportions.sum()

    return float(np.sum((cur_proportions - ref_proportions) * np.log(cur_proportions / ref_proportions)))


def psi_verdict(psi: float) -> str:
    """Traduit un PSI en verdict (stable / suspect / dérive)."""
    if pd.isna(psi):
        return "non calculable"
    if psi < PSI_STABLE:
        return "stable"
    if psi < PSI_DRIFT:
        return "suspect"
    return "dérive"


def ks_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du test de Kolmogorov-Smirnov (2 échantillons)."""
    ref = pd.to_numeric(reference, errors="coerce").dropna()
    cur = pd.to_numeric(current, errors="coerce").dropna()

    if len(ref) == 0 or len(cur) == 0:
        return np.nan
    return float(ks_2samp(ref, cur).pvalue)


def chi2_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du Chi² sur les fréquences de modalités (aligner les modalités)."""
    ref_counts = reference.fillna("Valeur manquante").astype(str).value_counts()
    cur_counts = current.fillna("Valeur manquante").astype(str).value_counts()
    categories = sorted(set(ref_counts.index).union(cur_counts.index))

    if not categories:
        return np.nan

    table = np.vstack([
        ref_counts.reindex(categories, fill_value=0).to_numpy(),
        cur_counts.reindex(categories, fill_value=0).to_numpy(),
    ]) + 1
    return float(chi2_contingency(table)[1])


def drift_report(
    reference: pd.DataFrame, current: pd.DataFrame,
    numeric_cols: list[str], categorical_cols: list[str],
) -> pd.DataFrame:
    """Tableau de synthèse : feature / type / psi / ks_pvalue / chi2_pvalue / verdict."""
    rows = []

    for col in numeric_cols:
        psi = population_stability_index(reference[col], current[col])
        p_value = ks_pvalue(reference[col], current[col])
        verdict = psi_verdict(psi)

        if verdict == "dérive" and p_value < 0.05:
            verdict = "dérive forte"
            comment = "signaux concordants"
        elif verdict == "dérive":
            comment = "PSI fort, KS non significatif"
        elif verdict == "suspect" and p_value < 0.05:
            comment = "PSI intermédiaire et KS significatif"
        elif verdict == "suspect":
            comment = "PSI intermédiaire seul"
        elif verdict == "stable" and p_value >= 0.05:
            comment = "pas de signal"
        elif verdict == "stable":
            comment = "écart détectable mais ampleur faible"
        else:
            comment = "à investiguer"

        rows.append({
            "Feature": col,
            "Type": "numérique",
            "PSI": psi,
            "p-value": p_value,
            "Verdict": verdict,
            "Commentaire": comment,
        })

    for col in categorical_cols:
        p_value = chi2_pvalue(reference[col], current[col])
        verdict = "dérive" if p_value < 0.05 else "stable"
        comment = "modalités redistribuées" if p_value < 0.05 else "pas de signal"

        rows.append({
            "Feature": col,
            "Type": "catégorielle",
            "PSI": np.nan,
            "p-value": p_value,
            "Verdict": verdict,
            "Commentaire": comment,
        })

    return pd.DataFrame(rows)
