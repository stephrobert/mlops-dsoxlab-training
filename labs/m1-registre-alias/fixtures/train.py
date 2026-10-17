"""Entraîne un modèle de latence sur les métriques de services.

La graine et les hyperparamètres viennent de params.yaml. Ce script ne garde
aucune trace de ses essais : à vous d'y brancher le serveur de suivi.
"""

import csv
import hashlib
import subprocess

import mlflow
import mlflow.sklearn

import numpy as np
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

CIBLE = "latence_p95_ms"
ENTREES = ["cpu_pct", "memoire_pct", "requetes_s", "taux_erreur"]

with open("params.yaml", encoding="utf-8") as f:
    params = yaml.safe_load(f)["entrainement"]

with open("data/metriques.csv", newline="", encoding="utf-8") as f:
    lignes = list(csv.DictReader(f))

X = np.array([[float(l[c]) for c in ENTREES] for l in lignes])
y = np.array([float(l[CIBLE]) for l in lignes])

X_app, X_test, y_app, y_test = train_test_split(
    X, y, test_size=params["part_test"], random_state=params["seed"]
)
modele = RandomForestRegressor(
    n_estimators=params["n_arbres"], n_jobs=1, random_state=params["seed"]
)
modele.fit(X_app, y_app)
pred = modele.predict(X_test)

metriques = {"rmse": float(mean_squared_error(y_test, pred) ** 0.5), "r2": float(r2_score(y_test, pred))}
print(metriques)

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("latence")
commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
empreinte = hashlib.sha256(open("data/metriques.csv", "rb").read()).hexdigest()
with mlflow.start_run() as run:
    mlflow.set_tags({"git_commit": commit, "data_sha256": empreinte})
    mlflow.log_params(params)
    mlflow.log_metrics(metriques)
    mlflow.sklearn.log_model(modele, name="modele", skops_trusted_types=["sklearn.tree._tree.Tree"])
    print("run", run.info.run_id)
