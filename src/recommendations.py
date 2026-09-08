"""Logique de recommandation de remédiation (SQUELETTE À COMPLÉTER).

La remédiation doit être **proportionnée** au diagnostic : réentraîner coûte
cher, on ne le propose que quand ça vaut le coup. Mini-cours :
`02_Data_drift_vs_concept_drift_essentiel.md` (matrice features × AUC).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DriftDiagnosis:
    """Synthèse du diagnostic pour décider de la remédiation."""

    n_features_drift: int  # nb de features en "dérive" (PSI > 0.25)
    auc_stable: bool  # le pouvoir discriminant tient-il ?
    calibration_degraded: bool  # la confiance a-t-elle dérivé ?
    f1_drop: float  # baisse de F1 macro (early → late)


def diagnose_drift_type(d: DriftDiagnosis) -> str:
    """Oriente vers "data drift" / "concept drift" / "mixte".

    ⚠️ Heuristique d'orientation, pas une preuve : elle formalise la matrice
    du mini-cours 02 (features × AUC) pour produire une hypothèse principale.
    Le verdict final se construit en croisant features, AUC, calibration et
    temporalité — et doit énoncer ce qui manquerait pour trancher.
    """
    # TODO 1 — traduire la matrice du mini-cours 02 :
    #   features dérivent + AUC stable → ... ; features stables + AUC
    #   dégradée → ... ; sinon → "mixte".
    raise NotImplementedError


def recommend(d: DriftDiagnosis) -> dict[str, str]:
    """Recommande une action proportionnée au diagnostic.

    Returns:
        dict avec les clés : action / justification / urgence / drift_type.
    """
    # TODO 2 — décliner au moins 3 issues distinctes (surveiller / ajuster /
    #   réentraîner), chacune avec une justification en langage métier.
    #   C'est cette fonction qui alimente votre note de recommandation.
    raise NotImplementedError
