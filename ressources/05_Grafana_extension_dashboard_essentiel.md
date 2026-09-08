# Étendre un dashboard Grafana existant — Mini-cours

> Brief associé : M6-B1
> Durée de lecture : ~20 min
> Pré-requis : Grafana provisionné en M5 (mini-cours M5 `04`)

## Pourquoi cette techno ?

Vous avez déjà un dashboard de prod en M5. En M6, on ne crée **pas** un nouveau
dashboard from scratch : on **étend l'existant** avec des panels de suivi de
dérive. C'est le réflexe pro — capitaliser sur l'outillage en place plutôt que
multiplier les tableaux de bord orphelins. Le dashboard reste **provisionné**
(versionné en JSON, chargé au démarrage), pas bricolé à la main.

## Concepts clés

- **Provisioning** : le dashboard vit en JSON dans le repo (`grafana/provisioning/dashboards/`, **le seul dossier scanné par la stack M5**)
  et est chargé automatiquement — un panel ajouté à la main dans l'UI est perdu
  au prochain `compose down` s'il n'est pas exporté.
- **Étendre = ajouter des panels** au JSON (ou un nouveau JSON provisionné par le
  même provider), pas refaire l'UI.
- **Grafana n'affiche que ce que Prometheus a scrapé.** Et Prometheus ne scrape
  que ce qu'un **service expose en HTTP, en continu**. Corollaire direct pour
  M6 : un PSI calculé dans votre notebook **n'existe pas** pour Grafana. Ce
  n'est pas une limite de l'outil, c'est sa définition.
- **Métriques offline vs live — deux supports différents.** Le PSI, le KS, le
  Chi² et le F1 sur 12 semaines sont des mesures **batch** : leur place est une
  **figure matplotlib dans le notebook**. La distribution des probabilités et la
  répartition des classes prédites sont **live** : elles sont déjà exposées par
  vos services M5, donc scrapées, donc affichables. Mettre une mesure batch dans
  Grafana sans l'avoir publiée ne produit pas une erreur : ça produit un panel
  « No data », c'est-à-dire un dashboard qui ment.
- **Publier une mesure batch, si on y tient** : il faut qu'un serveur HTTP la
  serve au format Prometheus (principe du *textfile collector*). Faisable sans
  ajouter de service — cf. la mission ⭐ du brief.
- ⚠️ **Gauge vs Histogram — la requête n'est pas la même.** `pyrenex_feature_psi`
  est une **gauge** : on l'interroge directement. `pyrenex_prediction_proba` est
  un **Histogram** (M5, mini-cours 02) : il n'existe pas tel quel dans
  Prometheus, il génère les séries `_bucket` / `_sum` / `_count`. Pour un
  quantile, il faut passer par `histogram_quantile()` **sur les buckets** :

  ```promql
  # ✅ médiane des probabilités prédites sur 5 min
  histogram_quantile(0.5, sum by (le) (rate(pyrenex_prediction_proba_bucket[5m])))

  # ❌ ne fonctionne pas : la métrique brute n'est pas une série interrogeable
  histogram_quantile(0.5, pyrenex_prediction_proba)
  ```

  Le `sum by (le)` agrège les buckets sur toutes les instances ; le `rate()`
  est nécessaire parce que les buckets sont des **compteurs cumulatifs**.
- **Seuils colorés** : configurez les `thresholds` du panel PSI (vert < 0.1,
  orange < 0.25, rouge ≥ 0.25) pour une lecture immédiate.
- **uid de datasource** : référencez la datasource Prometheus par son `uid`
  (comme en M5) pour que le provisioning soit reproductible.

## Exemple minimal qui tourne

Panel branché sur une métrique **que votre service `model` expose déjà** — donc il
affiche une courbe dès la première prédiction, sans rien installer de plus.

```json
// à ajouter dans "panels" de grafana/provisioning/dashboards/pyrenex_drift.json
{
  "title": "Comportement — probabilités prédites (médiane / p90)",
  "type": "timeseries",
  "datasource": { "type": "prometheus", "uid": "prometheus" },
  "fieldConfig": { "defaults": { "min": 0, "max": 1 } },
  "targets": [
    { "refId": "A",
      "expr": "histogram_quantile(0.5, sum(rate(pyrenex_prediction_proba_bucket[1h])) by (le))",
      "legendFormat": "médiane" },
    { "refId": "B",
      "expr": "histogram_quantile(0.9, sum(rate(pyrenex_prediction_proba_bucket[1h])) by (le))",
      "legendFormat": "p90" }
  ]
}
```

`docker compose up -d`, envoyez 3-4 requêtes sur `/score`, attendez un scrape
(15 s) : la courbe apparaît.

> Le même panel écrit sur `pyrenex_feature_psi` afficherait **« No data » pour
> toujours** — aucun service n'expose cette métrique. C'est tout l'objet de la
> section suivante.

## Exercice guidé

À partir du dashboard M5 :
1. Ajoutez **3 panels**, chacun répondant à une question opérationnelle :

| Panel | Question à laquelle il répond | Source (exposée par la stack M5 ✅) |
|---|---|---|
| Probabilités prédites (médiane, p90) | *Le modèle hésite-t-il plus qu'avant ?* | `histogram_quantile()` sur `pyrenex_prediction_proba_bucket` ✅ |
| Répartition des classes prédites | *La proportion de défauts annoncés a-t-elle bougé ?* | `pyrenex_predictions_total` par `predicted_class` ✅ |
| Volume et taux d'erreur | *Le contexte : y a-t-il assez de trafic pour conclure ?* | `http_requests_total` ✅ |

   ⚠️ **PSI, KS, Chi² et F1-12-semaines ne sont pas dans ce tableau**, et c'est
   volontaire : aucun service ne les expose. Leur place est le **notebook**.
   Écrivez-le dans votre README — c'est le point compris qu'on évalue.

   Un panel qui n'est relié à **aucune question** et à **aucune action du
   runbook** n'a pas sa place sur le dashboard.
2. Versionnez le JSON dans `grafana/provisioning/dashboards/pyrenex_drift.json`.
3. `docker compose up` doit le charger **sans import manuel**.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Créer un nouveau dashboard from scratch | Hors-sujet : on **étend** l'existant |
| Bricoler dans l'UI sans exporter le JSON | Perdu au redémarrage |
| Mettre un panel PSI / F1-12-semaines sans avoir publié la métrique | Panel « No data » en permanence : le dashboard **ment** |
| Poser le JSON dans `grafana/dashboards/` | **Jamais chargé, aucun message d'erreur** — le compose M5 ne monte que `./grafana/provisioning` |
| `histogram_quantile()` sur la métrique sans `_bucket` | Panel vide / erreur PromQL |
| Oublier `rate()` sur les buckets | Quantile faux (buckets = compteurs cumulatifs) |
| `uid` de datasource non référencé | « Datasource not found » au provisioning |
| Panel sans question ni action associée | Dashboard décoratif, jamais consulté en astreinte |

| Symptôme | Cause probable |
|---|---|
| Panels disparaissent au restart | JSON non versionné/provisionné |
| PSI « No data » | métrique batch jamais publiée à Prometheus (normal — cf. mission ⭐) |
| Le dashboard n'apparaît pas du tout dans Grafana | JSON hors de `grafana/provisioning/dashboards/` |
| Quantile de proba vide ou aberrant | `_bucket` oublié, ou `rate()` manquant |
| « Datasource not found » | mauvais `uid` dans le panel |

## Pour aller plus loin

- Grafana — Provisioning : https://grafana.com/docs/grafana/latest/administration/provisioning/
- Prometheus — histogram_quantile : https://prometheus.io/docs/practices/histograms/

## Vérification (checklist apprenant)

- [ ] J'ai **étendu** le dashboard M5 (pas créé un nouveau).
- [ ] Mes 3 panels sont versionnés en JSON et provisionnés.
- [ ] Mon JSON est dans `grafana/provisioning/dashboards/` (le seul dossier monté).
- [ ] `docker compose up` charge le dashboard sans clic.
- [ ] **Aucun de mes panels n'affiche « No data »** après quelques requêtes.
- [ ] Mes figures PSI / KS / Chi² / F1-12-semaines sont dans le **notebook**.
- [ ] Mon README explique en 2 lignes **pourquoi** le PSI n'est pas dans Grafana.
- [ ] Je distingue **gauge** (interrogée directement) et **Histogram**
      (`_bucket` + `rate()` + `histogram_quantile()`).
- [ ] Chacun de mes panels répond à une **question** et renvoie à une **action**
      du runbook.

> 💡 **Récap** : on **étend** le dashboard M5 (pas un nouveau), on **provisionne**
> le JSON dans `grafana/provisioning/dashboards/` (pas l'UI, pas ailleurs), et on
> range chaque mesure là où elle peut vivre — **batch → notebook**, **live →
> Grafana**. Un panel « No data » n'est pas un panel en attente : c'est un
> dashboard qui ment. Le réflexe pro : capitaliser
> sur l'outillage en place plutôt que multiplier les tableaux de bord orphelins.
