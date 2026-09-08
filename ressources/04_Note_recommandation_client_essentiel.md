# Note de recommandation client — Mini-cours

> Brief associé : M6-B1
> Durée de lecture : ~20 min
> Pré-requis : diagnostic de drift réalisé

## Pourquoi cette techno ?

Votre analyse technique ne vaut que si **le décideur la comprend et agit**.
Sophie Léger est Lead Data, pas ML engineer ni SRE : elle veut un **constat
chiffré**, un **diagnostic clair**, une **recommandation tranchée** et un
**coût**. Une note vague (« il faudrait peut-être réentraîner ») ne permet aucune
décision. C'est un livrable de **consultant**, pas un rapport de labo.

C'est aussi un attendu de la certification (compétence C9 : communiquer,
justifier ses choix) et un geste pro central : transformer de la statistique en
décision métier.

## Concepts clés

- **Structure en 5 blocs** : Constat (chiffré) → Diagnostic (avec preuve) →
  Recommandation (action) → Coût (temps/risque/fenêtre) → Décision suggérée
  (1 phrase tranchée).
- **Chiffrer, toujours** : « F1 0.61 → 0.55 », « PSI int_rate 0.44 » — pas « ça
  baisse un peu ».
- **Trancher** : proposer **une** action principale, pas un menu d'options.
- **Proportionner** : la remédiation suit le diagnostic. Réentraîner coûte cher
  → ne le proposer que si justifié ; sinon surveiller ou ajuster. Le type de
  drift **oriente** l'action, il ne la dicte pas : selon le contexte, la bonne
  réponse peut être surveiller, corriger une donnée, recalibrer, réentraîner,
  changer la fréquence de monitoring, rollback ou revoir les features.
- **Langage métier** : pas de jargon non défini. « calibration dégradée » se
  traduit « les probabilités annoncées ne sont plus fiables ».

## Exemple minimal qui tourne

```markdown
## Constat
F1 macro 0.61 → 0.55 en 3 mois. `int_rate` a fortement dérivé (PSI 0.44).

## Diagnostic
Data drift : les entrées ont bougé alors que le modèle classe toujours aussi
bien (AUC stable ~0.74) et que ses probabilités se dégradent (ECE 0.24 → 0.32).
Un changement de la logique de risque (concept drift) est peu probable au vu de
l'AUC ; il serait à réexaminer si celle-ci décrochait.

## Recommandation
Réentraîner sur données récentes sous 3 semaines.

## Coût
~2 j-homme ; risque prod faible (la CI/CD bloque si dégradation).

## Décision suggérée
> Lancer un réentraînement encadré sous 3 semaines via la chaîne CI/CD existante.
```

## Exercice guidé

Rédigez votre `note_recommandation.md` à partir de votre diagnostic :
1. Un constat avec **au moins 2 chiffres**.
2. Un diagnostic avec **la preuve** (PSI + AUC).
3. Une décision suggérée en **une phrase**.
Faites-la relire par votre binôme : « comprend-il l'action en 1 minute ? ».

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Note non chiffrée | Indécidable pour le client |
| Menu d'options sans recommandation | Le client doit trancher à votre place |
| Jargon ML non traduit | Sophie Léger décroche |
| Recommander de réentraîner « par défaut » | Remédiation non proportionnée |
| Pas de coût / fenêtre | Le client ne peut pas planifier |

| Symptôme | Cause probable |
|---|---|
| Le client redemande « donc on fait quoi ? » | pas de décision tranchée |
| Note de 5 pages | trop technique, manque de synthèse |
| Reco contestée | diagnostic pas assez prouvé (chiffres absents) |

## Pour aller plus loin

- Pyramide de Minto (structurer une reco) : https://en.wikipedia.org/wiki/Barbara_Minto
- Cf. note type dans le correctif (data drift).

## Vérification (checklist apprenant)

- [ ] Ma note suit les 5 blocs (constat/diagnostic/reco/coût/décision).
- [ ] Chaque affirmation est **chiffrée**.
- [ ] Je tranche sur **une** action principale.
- [ ] Un décideur non-ML la comprend en 1 minute.
- [ ] La remédiation est **proportionnée** au diagnostic.
