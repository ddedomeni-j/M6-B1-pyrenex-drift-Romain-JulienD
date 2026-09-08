# Note de recommandation — Dérive `pyrenex_risk_v2`

**Pour :** Sophie Léger (Lead Data, Pyrenex)  
**De :** FastIA — JulienD & Romain

## Constat (chiffré)

Sur les trois mois de production, plusieurs signaux montrent que les données reçues par le modèle ne ressemblent plus complètement au jeu de référence.

- `int_rate` dérive fortement : PSI = 0.444 et p-value KS < 0.001.
- `revol_util` est à surveiller : PSI = 0.187 et p-value KS < 0.001.
- `grade` est redistribué : p-value Chi² < 0.001.
- `annual_inc` présente un écart statistiquement détectable, mais d'ampleur limitée : PSI = 0.067.

La performance opérationnelle se dégrade surtout sur les décisions : le F1 macro passe de 0.6085 en semaines 1-4 à 0.5506 en semaines 9-12, soit une baisse de 0.0579. En parallèle, le score moyen prédit augmente alors que le taux de défaut observé reste globalement stable.

## Diagnostic

Le diagnostic principal est un **data drift avec impact sur la calibration**.

Les variables d'entrée changent, mais le modèle conserve son pouvoir de classement : l'AUC reste stable entre le début et la fin de période, de 0.7419 à 0.7459, soit un delta de +0.0040. Cela rend un concept drift massif peu probable à ce stade.

En revanche, les probabilités annoncées deviennent moins fiables. L'ECE augmente de 0.2403 à 0.3152, et le reliability diagram montre que le modèle est majoritairement sous la diagonale de calibration parfaite. Autrement dit, le modèle surestime le risque de défaut : il annonce des probabilités trop élevées par rapport au taux de défaut réellement observé.

## Recommandation

Nous recommandons de lancer un **réentraînement encadré sur données récentes**, avec vérification de calibration avant remise en production.

Cette action est proportionnée au diagnostic : le modèle classe encore correctement les dossiers, donc il n'y a pas d'urgence à remplacer toute la logique de risque. En revanche, la dérive sur `int_rate`, `revol_util` et `grade`, combinée à la dégradation de calibration et du F1 macro, justifie de réadapter le modèle aux données récentes.

Avant déploiement, le modèle candidat doit être validé sur trois points :

- AUC au moins stable par rapport à la version actuelle.
- F1 macro amélioré ou revenu au niveau du début de période.
- Calibration améliorée, avec ECE inférieur à la situation actuelle de fin de période.

## Coût estimé

Charge estimée : environ **2 à 3 jours-homme**. (moins d'une heure grace aux agents de Franck. D'après Tom c'est déjà en prod.)

- 0,5 jour pour préparer le dataset récent et vérifier la qualité des données.
- 1 jour pour réentraîner, comparer les métriques et recalibrer si nécessaire.
- 0,5 à 1 jour pour valider le modèle candidat et préparer le déploiement.

Risque production : **modéré mais maîtrisable**. Le modèle actuel peut rester en place pendant le réentraînement, car l'AUC reste stable. La fenêtre d'intervention recommandée est une mise en production planifiée, après validation hors ligne, plutôt qu'un remplacement en urgence.

## Décision suggérée
> Lancer sous trois semaines un réentraînement encadré de `pyrenex_risk_v2` sur données récentes, avec validation explicite de la calibration avant déploiement.
