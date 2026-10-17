"""Tests fonctionnels de m1-dvc-donnees : état du dépôt, du bucket, des octets."""

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
RACINE = Path(__file__).resolve().parents[4]
SOCLE = RACINE / "shared" / "socle"
SHA_V1 = "550be1a31a70a78891b8bd57b5d02738593eff19198b858d532cf880d6b94880"
SHA_V2 = "65e665e51d86d5ba2fed908cfced5439a2ef31d2b5c98593712ae4a77c4e0cb4"
DVC = W / ".venv" / "bin" / "dvc"


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "m1-dvc-donnees")


def env_s3() -> dict:
    env = dict(os.environ)
    for ligne in (SOCLE / ".env").read_text().splitlines():
        if "=" in ligne:
            k, v = ligne.split("=", 1)
            env[k] = v
    return env


def run(args, cwd=W, timeout=300):
    return subprocess.run(
        [str(a) for a in args], cwd=cwd, capture_output=True, text=True,
        timeout=timeout, env=env_s3(), check=False,
    )


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def exiger_dvc() -> None:
    assert DVC.exists(), message(
        en="DVC is not installed in the project environment (.venv/bin/dvc).",
        fr="DVC n'est pas installé dans l'environnement du projet (.venv/bin/dvc).",
    )


def test_donnees_suivies_par_dvc_pas_par_git() -> None:
    suivis = set(run(["git", "ls-files"]).stdout.split())
    assert "data/metriques.csv.dvc" in suivis, message(
        en="data/metriques.csv.dvc is not committed.",
        fr="data/metriques.csv.dvc n'est pas versionné.",
    )
    assert "data/metriques.csv" not in suivis, message(
        en="The CSV itself is in Git: DVC must hold it.",
        fr="Le CSV lui-même est dans Git : c'est DVC qui doit le porter.",
    )
    assert not run(["git", "status", "--porcelain"]).stdout.strip(), message(
        en="The Git working tree is not clean.",
        fr="L'arbre de travail Git n'est pas propre.",
    )


def test_dvc_status_propre_et_pousse() -> None:
    exiger_dvc()
    local = run([DVC, "status"])
    assert "up to date" in local.stdout, message(
        en=f"dvc status is not clean:\n{local.stdout}{local.stderr}",
        fr=f"dvc status n'est pas propre :\n{local.stdout}{local.stderr}",
    )
    cloud = run([DVC, "status", "-c"])
    assert "in sync" in cloud.stdout, message(
        en=f"The data is not in the remote:\n{cloud.stdout}{cloud.stderr}",
        fr=f"Les données ne sont pas dans le remote :\n{cloud.stdout}{cloud.stderr}",
    )


def test_empreinte_dans_le_bucket() -> None:
    r = run(["docker", "compose", "exec", "-T", "garage", "/garage", "bucket", "info",
             "dvc-donnees"], cwd=SOCLE)
    m = re.search(r"Objects:\s*(\d+)", r.stdout)
    assert m and int(m.group(1)) >= 2, message(
        en=f"The bucket dvc-donnees holds fewer than 2 objects:\n{r.stdout}{r.stderr}",
        fr=f"Le bucket dvc-donnees contient moins de 2 objets :\n{r.stdout}{r.stderr}",
    )


def _clone(tmp: Path) -> Path:
    c = tmp / "clone"
    r = run(["git", "clone", "-q", W, c])
    assert r.returncode == 0, r.stderr
    return c


def test_clone_vierge_restitue_le_jeu_courant(tmp_path: Path) -> None:
    exiger_dvc()
    c = _clone(tmp_path)
    r = run([DVC, "pull"], cwd=c)
    assert r.returncode == 0 and (c / "data" / "metriques.csv").exists(), message(
        en=f"dvc pull fails on a fresh clone:\n{r.stdout}{r.stderr}",
        fr=f"dvc pull échoue sur un clone vierge :\n{r.stdout}{r.stderr}",
    )
    assert sha(c / "data" / "metriques.csv") == SHA_V2, message(
        en="The restored dataset is not the current version (seed 43).",
        fr="Le jeu restitué n'est pas la version courante (graine 43).",
    )


def test_version_anterieure_retrouvable(tmp_path: Path) -> None:
    exiger_dvc()
    c = _clone(tmp_path)
    anciens = run(["git", "log", "--format=%H", "--", "data/metriques.csv.dvc"],
                  cwd=c).stdout.split()
    assert len(anciens) >= 2, message(
        en="Fewer than 2 commits changed data/metriques.csv.dvc: keep both versions.",
        fr="Moins de 2 commits modifient data/metriques.csv.dvc : gardez les deux versions.",
    )
    run(["git", "checkout", "-q", anciens[-1]], cwd=c)
    r = run([DVC, "pull"], cwd=c)
    assert r.returncode == 0, r.stdout + r.stderr
    assert sha(c / "data" / "metriques.csv") == SHA_V1, message(
        en="Going back to the first version does not restore seed 42 data.",
        fr="Le retour à la première version ne restitue pas le jeu de graine 42.",
    )
