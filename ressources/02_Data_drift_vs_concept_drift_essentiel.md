# Data drift vs concept drift — Mini-cours

> Brief associé : M6-B1
> Durée de lecture : ~25 min
> Pré-requis : détection de dérive (mini-cours 01), notion d'AUC

## Pourquoi cette techno ?

Détecter qu'« il y a dérive » ne suffit pas : la **remédiation dépend du type**.
Réentraîner coûte cher ; on ne le propose que si le diagnostic le justifie. La
distinction clé : les **entrées** ont-elles changé (*data drift*), ou la
**relation entrée → cible** a-t-elle changé (*concept drift*) ? Les deux se
soignent différemment.

C'est le cœur du raisonnement attendu par Sophie Léger : un diagnostic
**tranché et prouvé**, pas « on pense que… ».

## Concepts clés

- **Data drift** : la distribution des features change, mais la **logique de
  risque tient**. Ex. les taux montent, la clientèle glisse vers des grades plus
  risqués — mais « taux élevé ⇒ plus de risque » reste vrai.
- **Concept drift** : les features peuvent être stables, mais la **relation
  features → cible** a changé (nouveau comportement, choc réglementaire).
- **L'indice principal : l'AUC.** L'AUC mesure le **pouvoir de tri**
  indépendamment du seuil. Une AUC stable dit que le modèle **ordonne encore
  bien sur la période observée** — c'est un signal **compatible** avec un data
  drift. Elle ne **prouve** pas que la relation X → Y est intacte.
- ⚠️ **Signal ≠ preuve.** Une AUC qui baisse n'établit pas non plus un concept
  drift : changement de population, de prévalence, qualité des données, bug
  ETL, calibration — plusieurs causes produisent le même symptôme. Le concept
  drift est une **hypothèse à tester**, pas une conclusion automatique.
- **Triangulation** : croiser (1) dérive des features (PSI/KS/Chi²), (2)
  stabilité de l'AUC, (3) calibration, (4) temporalité (tendance vs saut).
  Le diagnostic naît du **faisceau**, jamais d'un indicateur isolé.
- **Conséquence** : le type de drift **oriente** la remédiation, il ne la
  détermine pas. Data drift ⇒ typiquement réentraîner sur données récentes
  (recale la calibration). Concept drift ⇒ réentraîner **en urgence** +
  investiguer la cause. D'autres actions restent possibles selon le contexte :
  surveiller, corriger une donnée, recalibrer, rollback, revoir les features.

### Matrice de diagnostic

| Features | AUC | Interprétation |
|---|---|---|
| stables | stable | Pas de signal majeur |
| **dérivent** | **stable** | **Data drift plausible** (cas Pyrenex) |
| dérivent | en baisse | Data drift avec impact sur la performance — concept drift à investiguer |
| stables | en baisse | Signal fort d'un changement de la relation X → Y |
| dérivent | calibration dégradée | Data drift avec impact probabiliste probable |

> **Aucune ligne ne constitue à elle seule une preuve définitive.** Elle oriente
> l'investigation ; la preuve se construit en croisant les 4 axes ci-dessus.

## Exemple minimal qui tourne

```python
from sklearn.metrics import roc_auc_score
# proba & y sur deux périodes
auc_debut = roc_auc_score(y_debut, proba_debut)
auc_fin   = roc_auc_score(y_fin,   proba_fin)
delta = auc_fin - auc_debut
if abs(delta) < 0.03:
    print(f"AUC stable (Δ={delta:+.3f}) → compatible data drift ; à croiser PSI + calibration")
else:
    print(f"AUC dégradée (Δ={delta:+.3f}) → investiguer : concept drift ? qualité ? population ?")
```

## Exercice guidé

Avec `predictions_log.csv` (colonnes `proba_default`, `true_label`, `timestamp`) :
1. Calculez l'AUC sur les semaines 1-4 puis 9-12.
2. Comparez à la dérive des features (mini-cours 01).
3. Remplissez la fiche de diagnostic ci-dessous, puis **tranchez** :

```text
Features qui dérivent : ......... (PSI / p-value à l'appui)
AUC début : .....   AUC fin : .....   ΔAUC : .....
Calibration début → fin : .........   (cf. mini-cours 03)
Temporalité : [ ] tendance progressive   [ ] rupture brutale

Diagnostic retenu (cocher) :
[ ] pas de signal significatif
[ ] data drift plausible
[ ] impact sur la calibration
[ ] concept drift à investiguer
[ ] problème de qualité / ETL à investiguer

Preuves qui soutiennent ce diagnostic :
.........
Ce qui manquerait pour être certain :
.........
```

> Attendu sur ce jeu : features qui dérivent + AUC stable → **data drift
> plausible**. Le verdict compte, mais **le faisceau de preuves compte
> autant** : c'est lui qui est évalué.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Conclure concept drift parce que le F1 baisse | Faux : le F1 dépend du seuil, regarder l'AUC |
| Traiter l'AUC comme une preuve à elle seule | Diagnostic non défendable devant le client |
| Oublier la temporalité | On confond une tendance avec un saut (bug ETL) |
| Diagnostic non chiffré | Note rejetée par le client |
| Recommander un réentraînement sans type de drift | Remédiation non proportionnée |

| Symptôme | Cause probable |
|---|---|
| F1 ↓ mais AUC stable | data drift + calibration dégradée (concept drift peu probable) |
| AUC ↓ franchement | changement de relation à investiguer — concept drift **parmi** les hypothèses (avec population, prévalence, qualité) |
| Saut brutal d'une feature | suspecter un **bug ETL**, pas une dérive « naturelle » |

## Pour aller plus loin

- Evidently — types de drift : https://www.evidentlyai.com/ml-in-production/data-drift
- scikit-learn — ROC-AUC : https://scikit-learn.org/stable/modules/model_evaluation.html#roc-metrics

## Vérification (checklist apprenant)

- [ ] Je sais définir data drift vs concept drift.
- [ ] J'utilise l'**AUC** comme indice, pas comme preuve.
- [ ] Je triangule (features + AUC + calibration + temporalité) avant de trancher.
- [ ] Mon diagnostic est **tranché et chiffré**, et j'énonce ce qui manquerait
      pour être certain.
- [ ] Je relie le type de drift à la remédiation proposée, en la proportionnant.

> 💡 **À retenir pour tout M6** : un **signal** statistique n'est pas encore un
> **diagnostic**, et un diagnostic n'est pas encore une **décision**.
