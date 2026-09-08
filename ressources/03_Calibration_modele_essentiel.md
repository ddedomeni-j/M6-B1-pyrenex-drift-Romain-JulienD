# Calibration du modèle en exploitation — Mini-cours

> Brief associé : M6-B1
> Durée de lecture : ~25 min
> Pré-requis : probabilités prédites, notion de fréquence observée

## Pourquoi cette techno ?

Un modèle peut **bien classer** (bonne AUC) tout en donnant des probabilités
**peu fiables**. Quand il annonce « 70 % de risque de défaut », observe-t-on
vraiment ~70 % de défauts ? Si oui, il est **bien calibré** ; sinon, ses
probabilités trompent les décisions métier (octroi nuancé, tarification).

En exploitation, surveiller la calibration révèle une dérive que l'AUC seule ne
montre pas : la distribution des scores peut glisser sans casser le tri. ⚠️ Ici
on parle de **calibration en exploitation** (le modèle est-il toujours fiable ?),
**à ne pas confondre** avec le choix d'un **seuil de rejet/abstention** en
conception (ça, c'est M7-M8).

## Concepts clés

- **Reliability diagram** : on découpe les probabilités prédites en bins, et pour
  chaque bin on compare la **confiance moyenne** (proba prédite) au **taux réel
  observé**. Convention d'axes — à respecter, sinon la lecture s'inverse :
  **axe X = probabilité moyenne prédite**, **axe Y = fréquence réellement
  observée**. Un modèle parfait suit la **diagonale**.
- **Sur-confiance** : la courbe est sous la diagonale (annonce 0.9 mais 60 % de
  défauts réels). **Sous-confiance** : au-dessus.
- **ECE (Expected Calibration Error)** ⭐ *bonus — le brief attend le reliability
  diagram* : moyenne pondérée des écarts |confiance − observé| sur les bins.
  Plus bas = mieux calibré (0 = parfait). ⚠️ **Indicateur de synthèse dépendant
  de la méthode** : nombre de bins, stratégie de binning (largeur fixe vs
  quantiles), taille d'échantillon. Deux ECE ne se comparent que calculés **à
  méthode identique** — et l'ECE ne dit pas **où** la calibration décroche : le
  reliability diagram reste indispensable pour ça.
- **En exploitation** : comparer la calibration **début vs fin** de période
  révèle si la confiance a **dérivé** dans le temps.
- **Lien avec le drift** : data drift ⇒ souvent calibration dégradée (les
  entrées ont bougé) alors que l'AUC tient.

### ⚠️ Contrainte MLOps : la calibration se mesure en différé

Mesurer la calibration exige les **vraies cibles**. Or le label métier arrive
**après** la prédiction :

```text
prédiction aujourd'hui → l'événement se réalise plus tard → label disponible → mesure possible
```

En crédit, un défaut peut mettre **des mois** à être constaté. Conséquences
concrètes pour votre monitoring :

- La surveillance de calibration est **structurellement retardée** — on mesure
  toujours sur une période déjà ancienne, jamais sur la production du jour.
- La dérive des **features** (PSI/KS), elle, est mesurable **immédiatement** :
  c'est pourquoi elle sert de signal d'alerte précoce.
- Un dashboard qui affiche la calibration doit donc indiquer **la fenêtre
  couverte** et son décalage, sinon on croit surveiller le présent.

C'est aussi ce qui rend le réentraînement délicat : au moment où la dégradation
est prouvée, elle dure depuis un moment.

## Exemple minimal qui tourne

```python
import numpy as np, pandas as pd
def ece(proba, y, n_bins=10):
    df = pd.DataFrame({"p": proba, "y": y})
    df["bin"] = pd.cut(df["p"], np.linspace(0, 1, n_bins + 1), include_lowest=True)
    g = df.groupby("bin", observed=True).agg(n=("y", "size"),
                                             conf=("p", "mean"), obs=("y", "mean"))
    w = g["n"] / g["n"].sum()
    return float((w * (g["conf"] - g["obs"]).abs()).sum())

print("ECE :", round(ece(proba, y), 4))   # ex. 0.05 = bien calibré
```

## Exercice guidé

Avec `predictions_log.csv` :
1. Tracez le reliability diagram pour les semaines 1-4 et 9-12 (deux courbes).
2. ⭐ Bonus : calculez l'ECE pour chaque période.
3. La confiance a-t-elle dérivé ? Dans quel sens (sur/sous-confiance) ?

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Confondre calibration et seuil de rejet | Mélange exploitation (M6) et conception (M7-M8) |
| Trop de bins sur peu de données | Courbe bruitée, ECE instable |
| Comparer deux ECE calculés avec des binnings différents | Comparaison invalide |
| Oublier le décalage des labels | On croit surveiller le présent, on mesure le passé |
| Lire la calibration sur une seule période | On rate la **dérive** de calibration |
| Croire qu'une bonne AUC ⇒ bonne calibration | Faux : ce sont deux propriétés distinctes |

| Symptôme | Cause probable |
|---|---|
| Courbe sous la diagonale | sur-confiance (proba trop hautes) |
| ECE qui monte dans le temps | calibration qui dérive (souvent data drift) |
| ECE instable | trop de bins / trop peu de points |
| Calibration « impossible à calculer » sur les dernières semaines | labels pas encore disponibles — normal, documenter la fenêtre |

## Pour aller plus loin

- scikit-learn — Calibration : https://scikit-learn.org/stable/modules/calibration.html
- Exemple courbe : https://scikit-learn.org/stable/auto_examples/calibration/plot_calibration_curve.html

## Vérification (checklist apprenant)

- [ ] Je trace un reliability diagram (X = proba prédite, Y = fréquence observée).
- [ ] Je sais lire sur/sous-confiance sur le reliability diagram.
- [ ] Je sais que la calibration exige les **vrais labels**, donc qu'elle est
      mesurée **en différé**, et j'indique la fenêtre couverte.
- [ ] ⭐ Bonus : je calcule l'ECE.
- [ ] Je compare **deux périodes** pour voir la dérive de calibration.
- [ ] Je ne confonds pas calibration (exploitation) et seuil de rejet (conception).
- [ ] Je relie la calibration au diagnostic de drift.
