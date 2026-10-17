"""Entraîne un modèle de latence et le sauvegarde.

    python train.py --arbres 100 --sortie modele/champion.joblib

La graine et la part de test viennent de params.yaml : le découpage est le
même à chaque appel, donc deux modèles se comparent sur les mêmes lignes.
"""

import argparse
from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

ENTREES = ["cpu_pct", "memoire_pct", "requetes_s", "taux_erreur"]
CIBLE = "latence_p95_ms"

p = argparse.ArgumentParser()
p.add_argument("--arbres", type=int, required=True)
p.add_argument("--sortie", required=True)
p.add_argument("--donnees", default="data/metriques.csv")
a = p.parse_args()

params = yaml.safe_load(open("params.yaml", encoding="utf-8"))["entrainement"]
df = pd.read_csv(a.donnees)
X_app, _, y_app, _ = train_test_split(
    df[ENTREES], df[CIBLE], test_size=params["part_test"], random_state=params["seed"]
)
modele = RandomForestRegressor(n_estimators=a.arbres, n_jobs=1, random_state=params["seed"])
modele.fit(X_app, y_app)
Path(a.sortie).parent.mkdir(parents=True, exist_ok=True)
joblib.dump(modele, a.sortie)
print("modele ecrit :", a.sortie)
