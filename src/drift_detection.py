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
    # TODO 1 — calculer les bords de bins (quantiles de `reference`),
    #   les comptages par bin pour ref et cur, les proportions (+ epsilon),
    #   puis la somme PSI.
    raise NotImplementedError


def psi_verdict(psi: float) -> str:
    """Traduit un PSI en verdict (stable / suspect / dérive)."""
    # TODO 2 — utiliser PSI_STABLE et PSI_DRIFT.
    raise NotImplementedError


def ks_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du test de Kolmogorov-Smirnov (2 échantillons)."""
    # TODO 3 — ks_2samp(...).pvalue
    raise NotImplementedError


def chi2_pvalue(reference: pd.Series, current: pd.Series) -> float:
    """p-value du Chi² sur les fréquences de modalités (aligner les modalités)."""
    # TODO 4 — construire la table de contingence (réindexer sur l'union des
    #   modalités, lissage +1) puis chi2_contingency(table)[1].
    raise NotImplementedError


def drift_report(
    reference: pd.DataFrame, current: pd.DataFrame,
    numeric_cols: list[str], categorical_cols: list[str],
) -> pd.DataFrame:
    """Tableau de synthèse : feature / type / psi / ks_pvalue / chi2_pvalue / verdict."""
    # TODO 5 — boucler sur numeric_cols (PSI + KS) et categorical_cols (Chi²),
    #   construire un DataFrame trié par sévérité.
    raise NotImplementedError
