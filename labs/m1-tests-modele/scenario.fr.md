# Scénario

Le modèle de latence est promu quand son RMSE « a l'air correct », sur un CSV
que personne n'inspecte. Deux incidents ont déjà eu lieu : une colonne
renommée en amont, et des valeurs impossibles (CPU à 140 %). Ce lab n'a besoin
d'aucun serveur : tout se passe dans le répertoire de travail.

## Mission

Dans le répertoire de travail (`uv sync`, puis créez `data/` et générez
`data/metriques.csv` avec la graine 42 et 5000 lignes ; faites un dépôt Git) :

1. entraînez un champion et un candidat avec `train.py` (par exemple 100
   arbres dans `modele/champion.joblib` et `modele/candidat.joblib`) ;
2. écrivez `seuils.yaml`, versionné, avec la clé `rmse_max` (au plus `28.0`) ;
3. écrivez une suite pytest dans `tests/` qui lit trois variables
   d'environnement, avec ces valeurs par défaut : `DONNEES`
   (`data/metriques.csv`), `MODELE` (`modele/candidat.joblib`) et `CHAMPION`
   (`modele/champion.joblib`). Elle doit contrôler :
   - le schéma : les colonnes `cpu_pct`, `memoire_pct`, `requetes_s`,
     `taux_erreur`, `latence_p95_ms` existent ;
   - les bornes : `cpu_pct` et `memoire_pct` dans [0, 100], `taux_erreur`
     dans [0, 1], `requetes_s` au moins 0, `latence_p95_ms` supérieure à 0 ;
   - le modèle : son RMSE sur la part de test (même découpage que `train.py`,
     `params.yaml` : `part_test` et `seed`) est au plus `rmse_max`, et au plus
     1,0 ms au-dessus de celui du champion ;
4. commitez tout. Le contrôle rejoue votre suite avec ses propres jeux
   (`casse-schema.csv`, `casse-bornes.csv` et un jeu valide) et ses propres
   modèles (bon, trop faible, moins bon que le champion) : elle doit passer
   sur les valides et échouer (tests en échec, code de sortie 1) sur les
   autres.
