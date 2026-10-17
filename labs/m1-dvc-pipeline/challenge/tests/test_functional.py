"""Tests fonctionnels de m1-dvc-pipeline : pipeline, bucket, métriques, rejeu réel."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from conftest import exiger_workdir, message, workdir_lab  # noqa: E402

W = workdir_lab(__file__)
SOCLE = Path(__file__).resolve().parents[4] / "shared" / "socle"
DVC = W / ".venv" / "bin" / "dvc"


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "m1-dvc-pipeline")


def run(args, cwd=W, timeout=600):
    env = dict(os.environ)
    for ligne in (SOCLE / ".env").read_text().splitlines():
        if "=" in ligne:
            k, v = ligne.split("=", 1)
            env[k] = v
    return subprocess.run(
        [str(a) for a in args], cwd=cwd, capture_output=True, text=True,
        timeout=timeout, env=env, check=False,
    )


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def exiger_dvc() -> None:
    assert DVC.exists(), message(
        en="DVC is not installed in the project environment (.venv/bin/dvc).",
        fr="DVC n'est pas installé dans l'environnement du projet (.venv/bin/dvc).",
    )


def clone_pret(tmp: Path) -> Path:
    """Clone vierge, environnement reconstruit depuis le verrou, données tirées."""
    c = tmp / "clone"
    r = run(["git", "clone", "-q", W, c])
    assert r.returncode == 0, r.stderr
    r = run(["uv", "sync", "--frozen"], cwd=c)
    assert r.returncode == 0, message(
        en=f"uv sync --frozen fails on a clone (is uv.lock committed?):\n{r.stderr}",
        fr=f"uv sync --frozen échoue sur un clone (uv.lock est-il versionné ?) :\n{r.stderr}",
    )
    return c


def test_pipeline_decrit_et_depot_propre() -> None:
    exiger_dvc()
    suivis = set(run(["git", "ls-files"]).stdout.split())
    assert {"dvc.yaml", "dvc.lock", "params.yaml", "uv.lock"} <= suivis, message(
        en="dvc.yaml, dvc.lock, params.yaml and uv.lock must be committed.",
        fr="dvc.yaml, dvc.lock, params.yaml et uv.lock doivent être versionnés.",
    )
    assert not run(["git", "status", "--porcelain"]).stdout.strip(), message(
        en="The Git working tree is not clean.", fr="L'arbre de travail Git n'est pas propre."
    )
    stages = run([DVC, "stage", "list"]).stdout
    assert len(re.findall(r"^\S+", stages, re.M)) >= 2, message(
        en=f"dvc.yaml must describe at least two stages (data, training):\n{stages}",
        fr=f"dvc.yaml doit décrire au moins deux étapes (données, entraînement) :\n{stages}",
    )
    dag = run([DVC, "dag"]).stdout
    assert "+" in dag or "*" in dag, message(
        en="The two stages are not chained: the training must depend on the data.",
        fr="Les deux étapes ne sont pas chaînées : l'entraînement doit dépendre des données.",
    )


def test_rien_a_rejouer_et_donnees_dans_le_bucket() -> None:
    exiger_dvc()
    r = run([DVC, "repro"])
    assert r.returncode == 0 and "Running stage" not in r.stdout + r.stderr, message(
        en=f"dvc repro replays something although nothing changed:\n{r.stdout}{r.stderr}",
        fr=f"dvc repro rejoue quelque chose alors que rien n'a changé :\n{r.stdout}{r.stderr}",
    )
    c = run([DVC, "status", "-c"])
    assert "in sync" in c.stdout, message(
        en=f"The pipeline outputs are not in the remote:\n{c.stdout}{c.stderr}",
        fr=f"Les sorties du pipeline ne sont pas dans le remote :\n{c.stdout}{c.stderr}",
    )


def test_clone_vierge_memes_metriques(tmp_path: Path) -> None:
    exiger_dvc()
    ref = sha(W / "metrics.json")
    c = clone_pret(tmp_path)
    (c / "metrics.json").unlink(missing_ok=True)
    r = run([c / ".venv/bin/dvc", "pull"], cwd=c)
    assert r.returncode == 0, r.stdout + r.stderr
    r = run([c / ".venv/bin/dvc", "repro", "--force"], cwd=c)
    assert r.returncode == 0, message(
        en=f"dvc repro fails on a fresh clone:\n{r.stdout}{r.stderr}",
        fr=f"dvc repro échoue sur un clone vierge :\n{r.stdout}{r.stderr}",
    )
    assert sha(c / "metrics.json") == ref, message(
        en="The clone does not give the same metrics.",
        fr="Le clone ne donne pas les mêmes métriques.",
    )


def test_un_parametre_ne_rejoue_que_son_etape(tmp_path: Path) -> None:
    exiger_dvc()
    c = clone_pret(tmp_path)
    dvc = c / ".venv/bin/dvc"
    assert run([dvc, "pull"], cwd=c).returncode == 0
    avant = sha(c / "metrics.json")
    p = c / "params.yaml"
    p.write_text(re.sub(r"(n_arbres:\s*)(\d+)", lambda m: f"{m.group(1)}{int(m.group(2)) + 10}",
                        p.read_text()))
    r = run([dvc, "repro"], cwd=c)
    sortie = r.stdout + r.stderr
    assert "Running stage 'entrainer'" in sortie, message(
        en=f"Changing n_arbres did not replay the training stage (is the stage named `entrainer` and does it declare the params?):\n{sortie}",
        fr=f"Changer n_arbres n'a pas rejoué l'étape `entrainer` (porte-t-elle ce nom et déclare-t-elle ses params ?) :\n{sortie}",
    )
    assert "Running stage 'donnees'" not in sortie, message(
        en="The data stage was replayed although its inputs did not change.",
        fr="L'étape données a été rejouée alors que ses entrées n'ont pas changé.",
    )
    assert sha(c / "metrics.json") != avant, message(
        en="The metrics did not change with the number of trees.",
        fr="Les métriques n'ont pas changé avec le nombre d'arbres.",
    )
