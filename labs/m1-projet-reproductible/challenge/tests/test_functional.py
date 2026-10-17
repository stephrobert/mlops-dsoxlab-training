"""Tests fonctionnels de m1-projet-reproductible.

Ils lisent l'ÉTAT du projet (fichiers, dépôt Git, verrou, empreintes,
métriques), jamais l'historique des commandes tapées.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from conftest import exiger_workdir, message, workdir_lab  # noqa: E402

W = workdir_lab(__file__)
LAB = "m1-projet-reproductible"
SHA_DONNEES = "550be1a31a70a78891b8bd57b5d02738593eff19198b858d532cf880d6b94880"


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, LAB)


def sh(args, cwd=W, timeout=300):
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False
    )


def python_projet() -> Path:
    p = W / ".venv" / "bin" / "python"
    assert p.exists(), message(
        en="No project environment: .venv/bin/python is missing.",
        fr="Pas d'environnement du projet : .venv/bin/python est absent.",
    )
    return p


def test_projet_versionne_et_propre() -> None:
    assert (W / ".git").is_dir(), message(
        en="The project is not a Git repository.",
        fr="Le projet n'est pas un dépôt Git.",
    )
    suivis = set(sh(["git", "ls-files"]).stdout.split())
    manquants = {
        "train.py", "params.yaml", "pyproject.toml", "uv.lock",
        "genere-metriques.py",
    } - suivis
    assert not manquants, message(
        en=f"Not versioned: {sorted(manquants)}.",
        fr=f"Non versionnés : {sorted(manquants)}.",
    )
    assert not any(s.startswith(".venv/") for s in suivis), message(
        en=".venv must not be versioned.", fr=".venv ne doit pas être versionné."
    )
    sale = sh(["git", "status", "--porcelain"]).stdout.strip()
    assert not sale, message(
        en=f"The working tree is not clean:\n{sale}",
        fr=f"L'arbre de travail n'est pas propre :\n{sale}",
    )


def test_graine_dans_la_configuration() -> None:
    f = W / "params.yaml"
    assert f.exists(), message(
        en="params.yaml is missing.", fr="params.yaml est absent."
    )
    assert re.search(r"^\s*seed:\s*\d+\s*$", f.read_text(), re.M), message(
        en="params.yaml has no integer `seed` key.",
        fr="params.yaml n'a pas de clé `seed` entière.",
    )


def test_environnement_verrouille() -> None:
    assert (W / "uv.lock").exists(), message(
        en="uv.lock is missing.", fr="uv.lock est absent."
    )
    verif = sh(["uv", "lock", "--check", "--offline"])
    assert verif.returncode == 0, message(
        en=f"uv.lock does not match pyproject.toml:\n{verif.stderr}",
        fr=f"uv.lock ne correspond pas à pyproject.toml :\n{verif.stderr}",
    )
    verrou = (W / "uv.lock").read_text()
    m = re.search(r'name = "scikit-learn"\nversion = "([^"]+)"', verrou)
    assert m, message(
        en="scikit-learn is not in the lock.", fr="scikit-learn n'est pas dans le verrou."
    )
    reel = sh([str(python_projet()), "-c", "import sklearn;print(sklearn.__version__)"])
    assert reel.stdout.strip() == m.group(1), message(
        en=f".venv has scikit-learn {reel.stdout.strip()!r}, the lock says {m.group(1)}.",
        fr=f".venv a scikit-learn {reel.stdout.strip()!r}, le verrou dit {m.group(1)}.",
    )


def test_donnees_exactes() -> None:
    f = W / "data" / "metriques.csv"
    assert f.exists(), message(
        en="data/metriques.csv is missing.", fr="data/metriques.csv est absent."
    )
    assert hashlib.sha256(f.read_bytes()).hexdigest() == SHA_DONNEES, message(
        en="data/metriques.csv is not the dataset of seed 42, 5000 rows.",
        fr="data/metriques.csv n'est pas le jeu de graine 42, 5000 lignes.",
    )


def _entraine(copie: Path) -> str:
    r = sh([str(python_projet()), "train.py"], cwd=copie)
    assert r.returncode == 0, message(
        en=f"train.py fails:\n{r.stderr[-800:]}",
        fr=f"train.py échoue :\n{r.stderr[-800:]}",
    )
    return hashlib.sha256((copie / "metrics.json").read_bytes()).hexdigest()


def _copie(dest: Path) -> Path:
    shutil.copytree(
        W, dest, ignore=shutil.ignore_patterns(".venv", ".git", "metrics.json")
    )
    return dest


def test_deux_entrainements_memes_metriques(tmp_path: Path) -> None:
    python_projet()
    a = _entraine(_copie(tmp_path / "a"))
    b = _entraine(_copie(tmp_path / "b"))
    assert a == b, message(
        en="Two trainings give different metrics.",
        fr="Deux entraînements donnent des métriques différentes.",
    )


def test_la_graine_pilote_vraiment_les_metriques(tmp_path: Path) -> None:
    python_projet()
    ref = _entraine(_copie(tmp_path / "ref"))
    autre = _copie(tmp_path / "autre")
    p = autre / "params.yaml"
    p.write_text(
        re.sub(r"^(\s*seed:\s*)(\d+)", lambda m: f"{m.group(1)}{int(m.group(2)) + 1}",
               p.read_text(), count=1, flags=re.M)
    )
    assert _entraine(autre) != ref, message(
        en="Changing the seed in params.yaml changes nothing: the script ignores it.",
        fr="Changer la graine de params.yaml ne change rien : le script l'ignore.",
    )
