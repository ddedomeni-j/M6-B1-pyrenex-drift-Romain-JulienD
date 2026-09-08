# Diagnostic data drift vs concept drift

## Synthèse

Le diagnostic retenu est un **data drift plausible avec impact sur la calibration**.

Les distributions de certaines variables d'entrée ont changé entre le jeu de référence et les trois mois de production, en particulier `int_rate`, `revol_util` et `grade`. En revanche, l'AUC reste stable entre le début et la fin de période, ce qui indique que le modèle conserve globalement son pouvoir de classement. Le signal principal n'est donc pas une perte complète de relation entre les features et la cible, mais plutôt un changement de population qui dégrade les probabilités produites par le modèle.

## Fiche de diagnostic

Features qui dérivent :

- `int_rate` : PSI = 0.444, KS p-value < 0.001, dérive forte.
- `revol_util` : PSI = 0.187, KS p-value < 0.001, signal suspect à investiguer.
- `grade` : Chi² p-value < 0.001, modalités redistribuées.
- `annual_inc` : PSI = 0.067, KS p-value < 0.001, écart détectable mais d'ampleur faible.

Features stables ou sans signal majeur :

- `loan_amnt`, `installment`, `dti`, `delinq_2yrs`, `fico_range_low`.
- `term`, `emp_length`, `home_ownership`, `verification_status`, `purpose`, `loan_status`.

Performance début vs fin de période :

| Indicateur | Semaines 1-4 | Semaines 9-12 | Évolution |
| --- | --: | --: | --: |
| AUC | 0.7419 | 0.7459 | +0.0040 |
| F1 macro | 0.6085 | 0.5506 | -0.0579 |
| ECE | 0.2403 | 0.3152 | +0.0749 |

Calibration début → fin :

- L'ECE augmente de 0.2403 à 0.3152.
- Le reliability diagram montre des courbes majoritairement sous la diagonale de calibration parfaite.
- Le modèle surestime donc le risque de défaut : les probabilités annoncées sont supérieures au taux de défaut réellement observé.

Temporalité :

- [x] tendance progressive
- [ ] rupture brutale

Le score moyen augmente au fil des semaines alors que le taux de défaut observé reste globalement stable. Cela ressemble davantage à une dérive progressive de calibration qu'à un bug ETL brutal.

## Diagnostic retenu

- [ ] pas de signal significatif
- [x] data drift plausible
- [x] impact sur la calibration
- [ ] concept drift à investiguer en priorité
- [ ] problème de qualité / ETL à investiguer en priorité

Le cas correspond à la matrice du mini-cours : **features qui dérivent + AUC stable = data drift plausible**. La baisse du F1 macro ne suffit pas à conclure à un concept drift, car le F1 dépend du seuil de décision. Ici, le pouvoir de tri reste stable selon l'AUC, mais les probabilités deviennent moins bien calibrées.

## Preuves qui soutiennent ce diagnostic

1. Plusieurs variables d'entrée changent de distribution : `int_rate` dérive fortement, `revol_util` est suspect et `grade` est redistribué.
2. L'AUC reste stable entre les semaines 1-4 et 9-12 : 0.7419 → 0.7459, soit un delta de +0.0040.
3. La calibration se dégrade : ECE 0.2403 → 0.3152.
4. Le F1 macro baisse : 0.6085 → 0.5506. Cela suggère que le seuil de décision devient moins adapté aux données récentes.
5. Le score moyen augmente progressivement alors que le taux de défaut observé reste relativement stable, ce qui confirme une surestimation croissante du risque.

## Ce qui manquerait pour être certain

- Une analyse plus fine par segment métier : grade, tranche de taux, revenu, ancienneté, usage du crédit.
- Une vérification de la qualité des données et de la chaîne d'ingestion pour exclure un changement de définition ou un bug ETL.
- Une comparaison avec un modèle recalibré ou réentraîné sur données récentes.
- Des métriques de performance sur une période plus longue pour vérifier si la stabilité de l'AUC tient dans le temps.

## Recommandation associée

La priorité n'est pas de conclure à un concept drift massif. Il faut d'abord traiter le **data drift avec dégradation de calibration** : surveiller les variables dérivées, recalibrer le modèle sur des données récentes, puis envisager un réentraînement si la dérive persiste ou si les métriques métier continuent de se dégrader.
