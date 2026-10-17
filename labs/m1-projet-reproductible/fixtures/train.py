"""Entraîne un modèle de latence sur les métriques de services.

Écrit par un collègue. Les métriques changent d'un lancement à l'autre.
"""

import csv
import json

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

CIBLE = "latence_p95_ms"
ENTREES = ["cpu_pct", "memoire_pct", "requetes_s", "taux_erreur"]

with open("data/metriques.csv", newline="", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

X = np.array([[float(l[c]) for c in ENTREES] for l in lignes])
y = np.array([float(l[CIBLE]) for l in lignes])

X_app, X_test, y_app, y_test = train_test_split(X, y, test_size=0.2)
modele = RandomForestRegressor(n_estimators=50, n_jobs=1)
modele.fit(X_app, y_app)
pred = modele.predict(X_test)

metriques = {
    "rmse": float(mean_squared_error(y_test, pred) ** 0.5),
    "r2": float(r2_score(y_test, pred)),
}
with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metriques, f, indent=2)
print(metriques)
