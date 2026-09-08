"""Calibration en exploitation (SQUELETTE À COMPLÉTER).

Le modèle annonce une proba : observe-t-on le bon taux réel ?
Mini-cours : `03_Calibration_modele_essentiel.md`. ⚠️ Calibration =
**exploitation** (≠ seuils de rejet de conception, vus en M7-M8).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def reliability_table(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> pd.DataFrame:
    """Table du reliability diagram : bin / n / confiance_moyenne / taux_observe / ecart."""
    # TODO 1 — découper proba en n_bins, comparer confiance moyenne et taux observé.
    raise NotImplementedError


def expected_calibration_error(proba: pd.Series, true_label: pd.Series, n_bins: int = 10) -> float:
    """ECE = Σ (n_bin/N) * |confiance - taux observé|. 0 = parfaitement calibré."""
    # TODO 2 — pondérer l'écart absolu par la taille de chaque bin.
    raise NotImplementedError
