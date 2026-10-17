"""Tests fonctionnels de m1-registre-alias : versions, alias, lignée, chargement réel.

Tout passe par l'API REST du serveur et par l'exécution de predire.py : ces
tests n'importent pas MLflow et ne supposent aucun numéro de version fixe.
"""

from __future__ import annotations

import json
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
URL = "http://127.0.0.1:5000"
NOM = "latence-service"


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "m1-registre-alias")


def api(chemin: str, corps: dict | None = None) -> dict:
    try:
        req = urllib.request.Request(
            URL + chemin,
            data=None if corps is None else json.dumps(corps).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError:
        return {}
    except (urllib.error.URLError, OSError) as e:
        pytest.fail(message(
            en=f"The MLflow server does not answer on {URL} ({e}). Start the stack: bash scripts/socle-demarrer.sh mlflow",
            fr=f"Le serveur MLflow ne répond pas sur {URL} ({e}). Démarrez le socle : bash scripts/socle-demarrer.sh mlflow",
        ))


def versions() -> list[dict]:
    filtre = urllib.parse.quote(f"name='{NOM}'")
    return api(f"/api/2.0/mlflow/model-versions/search?filter={filtre}&max_results=100").get("model_versions", [])


def n_arbres_du_run(run_id: str) -> str:
    run = api(f"/api/2.0/mlflow/runs/get?run_id={run_id}").get("run", {})
    for p in run.get("data", {}).get("params", []):
        if p["key"] == "n_arbres":
            return p["value"]
    return ""


def version_de_alias(alias: str) -> dict:
    q = urllib.parse.urlencode({"name": NOM, "alias": alias})
    return api(f"/api/2.0/mlflow/registered-models/alias?{q}").get("model_version", {})


def test_deux_versions_enregistrees_depuis_deux_runs() -> None:
    vs = versions()
    assert len(vs) >= 2, message(
        en=f"The registry must hold at least 2 versions of '{NOM}', found {len(vs)}.",
        fr=f"Le registre doit contenir au moins 2 versions de '{NOM}', il y en a {len(vs)}.",
    )
    arbres = {n_arbres_du_run(v["run_id"]) for v in vs}
    assert {"50", "100"} <= arbres, message(
        en=f"The versions must come from a 50-tree run and a 100-tree run (found {sorted(arbres)}).",
        fr=f"Les versions doivent venir d'un run à 50 arbres et d'un run à 100 arbres (trouvé {sorted(arbres)}).",
    )


def test_alias_champion_et_challenger_sur_les_bonnes_versions() -> None:
    for alias, attendu in (("champion", "50"), ("challenger", "100")):
        v = version_de_alias(alias)
        assert v, message(
            en=f"The alias '{alias}' does not exist on '{NOM}'.",
            fr=f"L'alias '{alias}' n'existe pas sur '{NOM}'.",
        )
        assert n_arbres_du_run(v["run_id"]) == attendu, message(
            en=f"The alias '{alias}' must point at the version built by the {attendu}-tree run.",
            fr=f"L'alias '{alias}' doit pointer la version construite par le run à {attendu} arbres.",
        )


def test_aucun_stage_utilise() -> None:
    vs = versions()
    assert vs and all(v.get("current_stage", "None") == "None" for v in vs), message(
        en="Registry stages are deprecated: leave every version in stage None and use aliases.",
        fr="Les stages du registre sont dépréciés : laissez chaque version en stage None et utilisez les alias.",
    )


def test_predire_charge_par_alias_sans_chemin() -> None:
    script = W / "predire.py"
    assert script.exists(), message(en="predire.py is missing.", fr="predire.py est absent.")
    source = script.read_text()
    assert "@challenger" in source and not re.search(r"runs:/|/artifacts|\bm-[0-9a-f]{8,}", source), message(
        en="predire.py must load models:/latence-service@challenger, with no path, run id or m- id.",
        fr="predire.py doit charger models:/latence-service@challenger, sans chemin, id de run ni id m-.",
    )
    python = W / ".venv" / "bin" / "python"
    assert python.exists(), message(en="Run uv sync in the work directory.", fr="Lancez uv sync dans le répertoire de travail.")
    try:
        r = subprocess.run([str(python), "predire.py"], cwd=W, capture_output=True, text=True, timeout=120, check=False)
    except subprocess.TimeoutExpired:
        pytest.fail(message(
            en="predire.py did not finish in 120 s: the model download hangs (see MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD).",
            fr="predire.py ne termine pas en 120 s : le téléchargement du modèle est suspendu (voir MLFLOW_ENABLE_PROXY_MULTIPART_DOWNLOAD).",
        ))
    nombres = re.findall(r"\d+\.\d+|\d+", r.stdout)
    assert r.returncode == 0 and nombres, message(
        en=f"predire.py must exit 0 and print a number:\n{r.stdout}{r.stderr[-800:]}",
        fr=f"predire.py doit rendre 0 et afficher un nombre :\n{r.stdout}{r.stderr[-800:]}",
    )
