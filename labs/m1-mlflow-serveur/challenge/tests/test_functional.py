"""Tests fonctionnels de m1-mlflow-serveur : runs, modèle dans le bucket, PostgreSQL, lignée.

Tout passe par l'API REST du serveur, par PostgreSQL et par le bucket : ces
tests n'importent pas MLflow, la note ne dépend pas de la façon d'y arriver.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from conftest import exiger_workdir, message, workdir_lab  # noqa: E402

W = workdir_lab(__file__)
COMPOSE = Path(__file__).resolve().parents[4] / "shared" / "socle" / "compose.yaml"
URL = "http://127.0.0.1:5000"
LISTE_BUCKET = """
import boto3, os, sys
s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
cles = [o["Key"] for o in s3.list_objects_v2(Bucket="mlflow-artefacts", Prefix=sys.argv[1]).get("Contents", [])]
print("\\n".join(cles))
"""


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "m1-mlflow-serveur")


def api(chemin: str, corps: dict | None = None) -> dict:
    """Appelle l'API REST de MLflow ; échoue avec une consigne si le serveur ne répond pas."""
    try:
        req = urllib.request.Request(
            URL + chemin,
            data=None if corps is None else json.dumps(corps).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"{}")
    except (urllib.error.URLError, OSError) as e:
        pytest.fail(message(
            en=f"The MLflow server does not answer on {URL} ({e}). Start the stack: bash scripts/socle-demarrer.sh mlflow",
            fr=f"Le serveur MLflow ne répond pas sur {URL} ({e}). Démarrez le socle : bash scripts/socle-demarrer.sh mlflow",
        ))


def runs_termines() -> list[dict]:
    exps = api("/api/2.0/mlflow/experiments/search", {"max_results": 100}).get("experiments", [])
    ids = [e["experiment_id"] for e in exps if e["name"] != "Default"]
    if not ids:
        return []
    res = api("/api/2.0/mlflow/runs/search", {"experiment_ids": ids, "max_results": 100}).get("runs", [])
    return [r for r in res if r["info"]["status"] == "FINISHED"]


def tags(run: dict) -> dict:
    return {t["key"]: t["value"] for t in run["data"].get("tags", [])}


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=W, capture_output=True, text=True, check=False)
    return r.stdout.strip()


def commit_du_run(run: dict) -> str:
    t = tags(run)
    return t.get("git_commit") or t.get("mlflow.source.git.commit", "")


def test_runs_avec_parametres_metriques_commit_et_empreinte() -> None:
    runs = runs_termines()
    assert len(runs) >= 2, message(
        en=f"Expected at least 2 FINISHED runs in an experiment other than Default, found {len(runs)}.",
        fr=f"Il faut au moins 2 runs FINISHED dans une expérience autre que Default, il y en a {len(runs)}.",
    )
    csv = W / "data" / "metriques.csv"
    assert csv.exists(), message(en="data/metriques.csv is missing.", fr="data/metriques.csv est absent.")
    empreinte = hashlib.sha256(csv.read_bytes()).hexdigest()
    commits = set(git("rev-list", "--all").split())
    for run in runs:
        params = {p["key"]: p["value"] for p in run["data"].get("params", [])}
        metriques = {m["key"] for m in run["data"].get("metrics", [])}
        assert "n_arbres" in params, message(
            en="A run does not log the n_arbres parameter.", fr="Un run ne journalise pas le paramètre n_arbres."
        )
        assert {"rmse", "r2"} <= metriques, message(
            en="A run must log the rmse and r2 metrics.", fr="Un run doit journaliser les métriques rmse et r2."
        )
        assert tags(run).get("data_sha256") == empreinte, message(
            en="A run has no tag data_sha256 equal to the SHA-256 of data/metriques.csv.",
            fr="Un run n'a pas de tag data_sha256 égal au SHA-256 de data/metriques.csv.",
        )
        assert commit_du_run(run) in commits, message(
            en="A run carries no Git commit tag that exists in the repository (git_commit).",
            fr="Un run ne porte pas de tag de commit Git existant dans le dépôt (git_commit).",
        )
    assert len({commit_du_run(r) for r in runs}) >= 2 and len(
        {next(p["value"] for p in r["data"]["params"] if p["key"] == "n_arbres") for r in runs}
    ) >= 2, message(
        en="Two trainings were expected: two commits and two different values of n_arbres.",
        fr="Deux entraînements sont attendus : deux commits et deux valeurs différentes de n_arbres.",
    )


def test_modele_de_chaque_run_dans_le_bucket() -> None:
    runs = runs_termines()
    assert runs, message(en="No FINISHED run on the server.", fr="Aucun run FINISHED sur le serveur.")
    for run in runs:
        sorties = (run.get("outputs") or {}).get("model_outputs", [])
        assert sorties, message(
            en="A run has no logged model (mlflow.sklearn.log_model).",
            fr="Un run n'a pas de modèle journalisé (mlflow.sklearn.log_model).",
        )
        exp = run["info"]["experiment_id"]
        for s in sorties:
            prefixe = f"{exp}/models/{s['model_id']}/artifacts/"
            r = subprocess.run(
                ["docker", "compose", "-f", str(COMPOSE), "exec", "-T", "mlflow", "python", "-", prefixe],
                input=LISTE_BUCKET, capture_output=True, text=True, timeout=60, check=False,
            )
            cles = r.stdout.split()
            assert prefixe + "MLmodel" in cles and len(cles) >= 2, message(
                en=f"The model files are not in the bucket mlflow-artefacts under {prefixe}:\n{r.stdout}{r.stderr}",
                fr=f"Les fichiers du modèle ne sont pas dans le bucket mlflow-artefacts sous {prefixe} :\n{r.stdout}{r.stderr}",
            )


def test_metadonnees_dans_postgresql() -> None:
    attendus = {r["info"]["run_id"] for r in runs_termines()}
    assert attendus, message(en="No FINISHED run on the server.", fr="Aucun run FINISHED sur le serveur.")
    r = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "exec", "-T", "postgres", "psql", "-U", "mlflow",
         "-d", "mlflow", "-Atc", "select run_uuid from runs where status = 'FINISHED'"],
        capture_output=True, text=True, timeout=60, check=False,
    )
    en_base = set(r.stdout.split())
    assert attendus <= en_base, message(
        en=f"The runs are not stored in PostgreSQL (backend store):\n{r.stdout}{r.stderr}",
        fr=f"Les runs ne sont pas dans PostgreSQL (backend store) :\n{r.stdout}{r.stderr}",
    )


def test_run_du_modele_v1_retrouve() -> None:
    reponse = W / "run-v1.txt"
    assert reponse.exists(), message(
        en="run-v1.txt is missing: write the id of the run that produced the model of tag v1.",
        fr="run-v1.txt est absent : écrivez l'identifiant du run qui a produit le modèle du tag v1.",
    )
    commit_v1 = git("rev-parse", "v1^{commit}")
    assert commit_v1, message(en="The Git tag v1 does not exist.", fr="Le tag Git v1 n'existe pas.")
    candidats = [r["info"]["run_id"] for r in runs_termines() if commit_du_run(r) == commit_v1]
    assert candidats, message(
        en=f"No FINISHED run comes from the commit of v1 ({commit_v1[:7]}): train from a commit before tagging it.",
        fr=f"Aucun run FINISHED ne vient du commit de v1 ({commit_v1[:7]}) : entraînez depuis un commit avant de le taguer.",
    )
    assert reponse.read_text().strip() in candidats, message(
        en="run-v1.txt does not contain the id of a run built from the commit of v1.",
        fr="run-v1.txt ne contient pas l'identifiant d'un run construit depuis le commit de v1.",
    )
    assert "run-v1.txt" in git("ls-files") and not git("status", "--porcelain"), message(
        en="Commit your work: run-v1.txt must be versioned and the working tree clean.",
        fr="Commitez votre travail : run-v1.txt doit être versionné et l'arbre de travail propre.",
    )
