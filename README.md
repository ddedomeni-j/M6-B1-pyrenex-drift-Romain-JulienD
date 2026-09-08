# M6-B1 — Analyser la performance et détecter la dérive (Pyrenex, 3 mois post-prod)

> **Repo template.** Un·e du binôme clique **« Use this template »** →
> `M6-B1-pyrenex-drift-<binome>`, ajoute l'autre en collaborateur. Vous
> diagnostiquez la dérive du modèle déployé en M5 et rendez une note à Sophie Léger.

## 🚀 Démarrage

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q tests            # vert dès le clone (certains tests se débloquent avec vos TODO)
jupyter notebook notebooks/M6-B1_template.ipynb
```

> Variante `uv` : `uv venv .venv && source .venv/bin/activate` puis
> `uv pip install -r requirements.txt`.
> Dépannage : `No module named pip` → vous êtes dans un venv créé par `uv`,
> utilisez `uv pip install …` (pas `pip install`).

Les **données sont fournies** dans `data/` : `reference_set.csv` (baseline),
`prod_3months.csv` (3 mois de prod), `predictions_log.csv` (logs du modèle).

## 🧭 Ce que vous construisez

| # | À faire | Fichier | Mini-cours |
|---|---|---|---|
| 1 | Détection PSI / KS / Chi² | `src/drift_detection.py` | `01` |
| 2 | Calibration (reliability diagram ; ECE en bonus ⭐) | `src/calibration.py` | `03` |
| 3 | Analyse complète | `notebooks/M6-B1_template.ipynb` | `01`,`02`,`03` |
| 4 | Diagnostic data vs concept drift | `diagnostic.md` | `02` |
| 5 | Note de recommandation | `note_recommandation_TEMPLATE.md` | `04` |
| 6 | Extension dashboard Grafana (3 panels **live**) | `grafana/provisioning/dashboards/pyrenex_drift_TEMPLATE.json` | `05` |
| 6⭐ | *(option)* publier le PSI a Prometheus sans nouveau service | `metrics/psi.prom` + compose + `prometheus.yml` | `05` |

## ✅ Réussite (rappel)

- PSI/KS/Chi² sur **toutes** les features pertinentes.
- Diagnostic **chiffré et tranché** (data drift vs concept drift — regarder l'AUC !).
- Note **lisible Sophie Léger** (pas ML), chiffrée, décision tranchée.
- Dashboard étendu **provisionné** sur la stack M5 — dans
  `grafana/provisioning/dashboards/` (**le seul dossier monté** par votre compose M5),
  et **sans aucun panel « No data »** : PSI, KS, Chi² et F1-12-semaines sont des
  mesures batch, leur place est le **notebook**. Votre README dit pourquoi en 2 lignes.
- Notebook top→bottom, commits `Co-authored-by:`, **journal de bord**.

## 📚 Ressources

Voir [`./ressources/`](./ressources/) — 5 mini-cours + `liens_officiels.md`.
