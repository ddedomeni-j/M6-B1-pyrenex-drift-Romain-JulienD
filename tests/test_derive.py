"""Script manuel : appelle le service de scoring (docker-compose M5)
avec les données de `reference_set.csv` et `prod_3months.csv`.

Nécessite le stack M5 démarré (`docker compose up -d` dans le dossier
M5-B1-Romain_Joelle) et exposant le backend sur `BACKEND_URL`
(par défaut http://localhost:8001).

Usage :
    python tests/test_derive.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")
SCORE_ENDPOINT = f"{BACKEND_URL}/score"

# Colonnes attendues par le schéma Pydantic `LoanApplication` du service.
FEATURE_COLUMNS = [
    "loan_amnt",
    "term",
    "int_rate",
    "installment",
    "grade",
    "emp_length",
    "home_ownership",
    "annual_inc",
    "verification_status",
    "purpose",
    "dti",
    "delinq_2yrs",
    "fico_range_low",
    "revol_util",
]

# Nombre de lignes envoyées au service par fichier (garde le script rapide).
N_SAMPLES = 1000


def backend_disponible() -> bool:
    """Vérifie que le service backend (docker) répond."""
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=3)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


def charger_echantillon(nom_fichier: str) -> list[dict]:
    """Charge un CSV de données et retourne des payloads prêts pour /score."""
    df = pd.read_csv(ROOT / "data" / nom_fichier)
    df = df.dropna(subset=FEATURE_COLUMNS).head(N_SAMPLES)
    return df[FEATURE_COLUMNS].to_dict(orient="records")


def appeler_service(nom_fichier: str, payloads: list[dict]) -> bool:
    """Poste chaque payload au service et affiche le résultat. Retourne le succès."""
    if not payloads:
        print(f"[{nom_fichier}] KO : aucun payload exploitable")
        return False

    erreurs = 0
    for i, payload in enumerate(payloads):
        try:
            response = requests.post(SCORE_ENDPOINT, json=payload, timeout=10)
        except requests.exceptions.RequestException as exc:
            print(f"[{nom_fichier}] ligne {i} KO : requête impossible ({exc})")
            erreurs += 1
            continue

        if response.status_code != 200:
            print(f"[{nom_fichier}] ligne {i} KO : HTTP {response.status_code} — {response.text[:200]}")
            erreurs += 1
            continue

        data = response.json()
        if data["prediction"] not in (0, 1) or not (0.0 <= data["probability"] <= 1.0):
            print(f"[{nom_fichier}] ligne {i} KO : réponse invalide {data}")
            erreurs += 1

    total = len(payloads)
    print(f"[{nom_fichier}] {total - erreurs}/{total} prédictions OK")
    return erreurs == 0


def main() -> int:
    if not backend_disponible():
        print(f"Service backend indisponible sur {BACKEND_URL} (docker compose up ?)")
        return 1

    ok_reference = appeler_service("reference_set.csv", charger_echantillon("reference_set.csv"))
    ok_prod = appeler_service("prod_3months.csv", charger_echantillon("prod_3months.csv"))

    return 0 if (ok_reference and ok_prod) else 1


if __name__ == "__main__":
    sys.exit(main())
