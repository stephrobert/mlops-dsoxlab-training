"""Tests fonctionnels de e1-reproduire : l'état du dépôt, du stockage S3 et du serveur MLflow.

Aucun test ne lit les commandes tapées. Le correcteur clone le dépôt, rejoue le
pipeline et lance la suite de l'apprenant sur ses propres jeux.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from conftest import exiger_workdir, message, workdir_lab  # noqa: E402

W = workdir_lab(__file__)
P = W / "projet"
SOCLE = Path(__file__).resolve().parents[4] / "shared" / "socle"
COMPOSE = SOCLE / "compose.yaml"
URL = "http://127.0.0.1:5000"
NOM = "latence-service"
LISTE_BUCKET = """
import boto3, os, sys
s3 = boto3.client("s3", endpoint_url=os.environ["MLFLOW_S3_ENDPOINT_URL"])
cles = [o["Key"] for o in s3.list_objects_v2(Bucket="dvc-donnees").get("Contents", [])]
print("\\n".join(cles))
"""


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "e1-reproduire")


def env() -> dict:
    e = dict(os.environ)
    for ligne in (SOCLE / ".env").read_text().splitlines():
        if "=" in ligne:
            k, v = ligne.split("=", 1)
            e[k] = v
    return e


def run(args, cwd=P, timeout=900, extra=None):
    e = env()
    e.update(extra or {})
    return subprocess.run([str(a) for a in args], cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=e, check=False)


def exiger_depot() -> None:
    assert (P / ".git").is_dir() and (P / ".venv" / "bin" / "dvc").exists(), message(
        en="Clone depot.bundle into projet/ and rebuild the environment (uv sync).",
        fr="Clonez depot.bundle dans projet/ et reconstruisez l'environnement (uv sync).",
    )


def api(chemin: str, corps: dict | None = None) -> dict:
    try:
        req = urllib.request.Request(
            URL + chemin, data=None if corps is None else json.dumps(corps).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError:
        return {}
    except (urllib.error.URLError, OSError) as e:
        pytest.fail(message(
            en=f"The MLflow server does not answer on {URL} ({e}). Start the stack: bash scripts/socle-demarrer.sh mlflow",
            fr=f"Le serveur MLflow ne répond pas sur {URL} ({e}). Démarrez le socle : bash scripts/socle-demarrer.sh mlflow",
        ))


def tags(run_: dict) -> dict:
    return {t["key"]: t["value"] for t in run_["data"].get("tags", [])}


def runs_termines() -> list[dict]:
    exps = api("/api/2.0/mlflow/experiments/search", {"max_results": 100}).get("experiments", [])
    ids = [e["experiment_id"] for e in exps]
    if not ids:
        return []
    res = api("/api/2.0/mlflow/runs/search", {"experiment_ids": ids, "max_results": 200}).get("runs", [])
    return [r for r in res if r["info"]["status"] == "FINISHED"]


def run_trace(r: dict) -> bool:
    """Le run porte le commit d'un commit du dépôt et l'empreinte exacte du jeu."""
    csv = P / "data" / "metriques.csv"
    if not csv.exists():
        return False
    commits = set(run(["git", "rev-list", "--all"]).stdout.split())
    t = tags(r)
    params = {p["key"] for p in r["data"].get("params", [])}
    metriques = {m["key"] for m in r["data"].get("metrics", [])}
    return (t.get("git_commit") in commits
            and t.get("data_sha256") == hashlib.sha256(csv.read_bytes()).hexdigest()
            and bool(params) and {"rmse", "r2"} <= metriques)


def test_depot_propre_et_dvc_status_synchronise() -> None:
    exiger_depot()
    suivis = set(run(["git", "ls-files"]).stdout.split())
    assert {"dvc.yaml", "dvc.lock", "params.yaml", "uv.lock"} <= suivis, message(
        en="dvc.yaml, dvc.lock, params.yaml and uv.lock must be committed.",
        fr="dvc.yaml, dvc.lock, params.yaml et uv.lock doivent être versionnés.",
    )
    assert not run(["git", "status", "--porcelain"]).stdout.strip(), message(
        en="The Git working tree is not clean.", fr="L'arbre de travail Git n'est pas propre.")
    dvc = P / ".venv" / "bin" / "dvc"
    local = run([dvc, "status"])
    assert "up to date" in local.stdout, message(
        en=f"dvc status is not clean:\n{local.stdout}{local.stderr}",
        fr=f"dvc status n'est pas propre :\n{local.stdout}{local.stderr}")
    distant = run([dvc, "status", "-c"])
    assert "in sync" in distant.stdout, message(
        en=f"The store is not in sync (dvc push?):\n{distant.stdout}{distant.stderr}",
        fr=f"Le stockage n'est pas synchronisé (dvc push ?) :\n{distant.stdout}{distant.stderr}")


def test_empreinte_des_donnees_dans_le_stockage_s3() -> None:
    exiger_depot()
    csv = P / "data" / "metriques.csv"
    assert csv.exists(), message(en="data/metriques.csv is missing.", fr="data/metriques.csv est absent.")
    md5 = hashlib.md5(csv.read_bytes()).hexdigest()
    r = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE), "exec", "-T", "mlflow", "python", "-"],
        input=LISTE_BUCKET, capture_output=True, text=True, timeout=60, check=False)
    cle = f"files/md5/{md5[:2]}/{md5[2:]}"
    assert cle in r.stdout.split(), message(
        en=f"The fingerprint of the data ({cle}) is not in the bucket dvc-donnees:\n{r.stdout}{r.stderr}",
        fr=f"L'empreinte des données ({cle}) n'est pas dans le bucket dvc-donnees :\n{r.stdout}{r.stderr}")


def test_clone_vierge_pipeline_redonne_la_metrique(tmp_path: Path) -> None:
    exiger_depot()
    ref = json.loads((P / "metrics.json").read_text())
    c = tmp_path / "clone"
    assert run(["git", "clone", "-q", P, c], cwd=tmp_path).returncode == 0
    r = run(["uv", "sync", "--frozen"], cwd=c)
    assert r.returncode == 0, message(
        en=f"uv sync --frozen fails on a clone:\n{r.stderr}", fr=f"uv sync --frozen échoue sur un clone :\n{r.stderr}")
    dvc = c / ".venv" / "bin" / "dvc"
    r = run([dvc, "pull"], cwd=c)
    assert r.returncode == 0, message(
        en=f"dvc pull fails on a clone:\n{r.stdout}{r.stderr}", fr=f"dvc pull échoue sur un clone :\n{r.stdout}{r.stderr}")
    (c / "metrics.json").unlink(missing_ok=True)
    r = run([dvc, "repro", "--force"], cwd=c)
    assert r.returncode == 0, message(
        en=f"dvc repro fails on a fresh clone:\n{r.stdout}{r.stderr}",
        fr=f"dvc repro échoue sur un clone vierge :\n{r.stdout}{r.stderr}")
    obtenu = json.loads((c / "metrics.json").read_text())
    assert round(obtenu["rmse"], 2) == 23.31 and round(obtenu["r2"], 4) == 0.7813 and obtenu == ref, message(
        en=f"The clone does not give the expected metrics (RMSE 23.31, R2 0.7813): {obtenu}",
        fr=f"Le clone ne donne pas les métriques attendues (RMSE 23,31, R2 0,7813) : {obtenu}")


def test_run_mlflow_termine_avec_commit_et_empreinte() -> None:
    exiger_depot()
    assert any(run_trace(r) for r in runs_termines()), message(
        en="No FINISHED run carries parameters, rmse and r2, a git_commit tag of a commit of the repository and a data_sha256 tag equal to the SHA-256 of data/metriques.csv.",
        fr="Aucun run FINISHED ne porte paramètres, rmse et r2, un tag git_commit d'un commit du dépôt et un tag data_sha256 égal au SHA-256 de data/metriques.csv.")


def test_modele_enregistre_avec_l_alias_challenger() -> None:
    exiger_depot()
    q = urllib.parse.urlencode({"name": NOM, "alias": "challenger"})
    v = api(f"/api/2.0/mlflow/registered-models/alias?{q}").get("model_version", {})
    assert v, message(
        en=f"The alias 'challenger' does not exist on '{NOM}'.", fr=f"L'alias 'challenger' n'existe pas sur '{NOM}'.")
    run_ = api(f"/api/2.0/mlflow/runs/get?run_id={v['run_id']}").get("run")
    assert run_ and run_["info"]["status"] == "FINISHED" and run_trace(run_), message(
        en="The version pointed by 'challenger' must come from a FINISHED run carrying the commit and the data fingerprint.",
        fr="La version pointée par 'challenger' doit venir d'un run FINISHED qui porte le commit et l'empreinte des données.")
    assert v.get("current_stage", "None") == "None", message(
        en="Do not use registry stages: use aliases.", fr="N'utilisez pas les stages du registre : utilisez les alias.")


def suite(donnees: Path, metriques: Path) -> subprocess.CompletedProcess:
    return run([P / ".venv" / "bin" / "python", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
               extra={"DONNEES": str(donnees), "METRIQUES": str(metriques)})


def test_la_suite_refuse_le_schema_casse_et_passe_sur_le_bon() -> None:
    exiger_depot()
    bon = suite(P / "data" / "metriques.csv", P / "metrics.json")
    assert bon.returncode == 0, message(
        en=f"Your suite must pass on the repository's data and metrics (exit {bon.returncode}):\n{bon.stdout[-800:]}{bon.stderr[-300:]}",
        fr=f"Votre suite doit passer sur les données et métriques du dépôt (code {bon.returncode}) :\n{bon.stdout[-800:]}{bon.stderr[-300:]}")
    casse = suite(W / "casse-schema.csv", P / "metrics.json")
    assert casse.returncode in (1, 2) and re.search(r"failed|error", casse.stdout, re.I), message(
        en=f"Your suite must fail (exit code 1) on casse-schema.csv; exit code {casse.returncode}:\n{casse.stdout[-600:]}",
        fr=f"Votre suite doit échouer (code 1) sur casse-schema.csv ; code {casse.returncode} :\n{casse.stdout[-600:]}")


def test_la_suite_refuse_un_rmse_au_dessus_du_seuil_versionne(tmp_path: Path) -> None:
    exiger_depot()
    suivis = run(["git", "ls-files"]).stdout.split()
    assert "seuils.yaml" in suivis and any(f.startswith("tests/") for f in suivis), message(
        en="seuils.yaml and the tests/ folder must be committed.",
        fr="seuils.yaml et le dossier tests/ doivent être versionnés.")
    m = re.search(r"^rmse_max:\s*([0-9.]+)", (P / "seuils.yaml").read_text(), re.M)
    mesure = json.loads((P / "metrics.json").read_text())["rmse"]
    assert m and mesure < float(m.group(1)) <= 28.0, message(
        en=f"seuils.yaml must define rmse_max, above the RMSE of your metrics.json ({mesure:.2f}) so that your model passes, and at most 28.0.",
        fr=f"seuils.yaml doit définir rmse_max, au-dessus de la RMSE de votre metrics.json ({mesure:.2f}) pour que votre modèle passe, et au plus 28,0.")
    assert "seuils.yaml" in "".join(p.read_text() for p in (P / "tests").glob("*.py")), message(
        en="The tests must read the threshold from seuils.yaml.", fr="Les tests doivent lire le seuil dans seuils.yaml.")
    mauvais = tmp_path / "metrics-degrade.json"
    mauvais.write_text(json.dumps({"rmse": 40.0, "r2": 0.1}))
    r = suite(P / "data" / "metriques.csv", mauvais)
    assert r.returncode in (1, 2) and re.search(r"failed|error", r.stdout, re.I), message(
        en=f"Your suite must fail (exit code 1) on a metrics file with rmse 40; exit code {r.returncode}:\n{r.stdout[-600:]}",
        fr=f"Votre suite doit échouer (code 1) sur un fichier de métriques avec rmse 40 ; code {r.returncode} :\n{r.stdout[-600:]}")
