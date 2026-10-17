"""Tests fonctionnels de m1-tests-modele : la suite de l'apprenant est rejouée.

Le contrôle fabrique ses propres jeux et modèles (bon, trop faible, moins bon
que le champion), lance la suite de l'apprenant avec les variables DONNEES,
MODELE et CHAMPION, et exige le bon code de sortie de pytest.
"""

from __future__ import annotations

import os
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from conftest import exiger_workdir, message, workdir_lab  # noqa: E402

W = workdir_lab(__file__)
PY = W / ".venv" / "bin" / "python"

FABRIQUE = textwrap.dedent("""
    import sys
    import joblib, pandas as pd, yaml
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    sortie, arbres, profondeur = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    p = yaml.safe_load(open("params.yaml"))["entrainement"]
    df = pd.read_csv("data/metriques.csv")
    X = df[["cpu_pct", "memoire_pct", "requetes_s", "taux_erreur"]]
    Xa, _, ya, _ = train_test_split(X, df["latence_p95_ms"], test_size=p["part_test"], random_state=p["seed"])
    m = RandomForestRegressor(n_estimators=arbres, max_depth=None if profondeur == "0" else int(profondeur),
                              n_jobs=1, random_state=p["seed"]).fit(Xa, ya)
    joblib.dump(m, sortie)
""")


@pytest.fixture(autouse=True)
def _demarre() -> None:
    exiger_workdir(W, "m1-tests-modele")


@pytest.fixture(scope="module")
def modeles(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    if not PY.exists() or not (W / "data" / "metriques.csv").exists():
        pytest.fail(message(
            en="Run uv sync and generate data/metriques.csv first.",
            fr="Lancez uv sync et générez data/metriques.csv d'abord.",
        ))
    d = tmp_path_factory.mktemp("modeles")
    # champion et bon candidat : 100 arbres ; trop faible : profondeur 2 ;
    # moins bon que le champion mais sous tout seuil raisonnable : 10 arbres.
    for nom, arbres, prof in (("champion", 100, "0"), ("bon", 100, "0"), ("faible", 50, "2"), ("moins_bon", 10, "0")):
        r = subprocess.run([str(PY), "-c", FABRIQUE, str(d / f"{nom}.joblib"), str(arbres), prof],
                           cwd=W, capture_output=True, text=True, timeout=300, check=False)
        assert r.returncode == 0, r.stderr
    return {n: d / f"{n}.joblib" for n in ("champion", "bon", "faible", "moins_bon")}


def pytest_de_l_apprenant(donnees: Path, modele: Path, champion: Path) -> subprocess.CompletedProcess:
    env = {**os.environ, "DONNEES": str(donnees), "MODELE": str(modele), "CHAMPION": str(champion)}
    return subprocess.run([str(PY), "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                          cwd=W, env=env, capture_output=True, text=True, timeout=300, check=False)


def exiger_refus(r: subprocess.CompletedProcess, quoi_en: str, quoi_fr: str) -> None:
    assert r.returncode in (1, 2) and ("failed" in r.stdout or "error" in r.stdout.lower()), message(
        en=f"Your suite must fail (exit code 1) on {quoi_en}; exit code {r.returncode}:\n{r.stdout[-600:]}",
        fr=f"Votre suite doit échouer (code 1) sur {quoi_fr} ; code {r.returncode} :\n{r.stdout[-600:]}",
    )


def test_la_suite_passe_sur_donnees_et_modele_valides(modeles: dict[str, Path]) -> None:
    r = pytest_de_l_apprenant(W / "data" / "metriques.csv", modeles["bon"], modeles["champion"])
    assert r.returncode == 0, message(
        en=f"Your suite must pass on valid data and a good model (exit {r.returncode}):\n{r.stdout[-800:]}{r.stderr[-300:]}",
        fr=f"Votre suite doit passer sur des données et un modèle valides (code {r.returncode}) :\n{r.stdout[-800:]}{r.stderr[-300:]}",
    )


def test_la_suite_refuse_les_donnees_cassees(modeles: dict[str, Path]) -> None:
    for fichier in ("casse-schema.csv", "casse-bornes.csv"):
        r = pytest_de_l_apprenant(W / fichier, modeles["bon"], modeles["champion"])
        exiger_refus(r, f"the dataset {fichier}", f"le jeu {fichier}")


def test_la_suite_refuse_un_modele_sous_le_seuil(modeles: dict[str, Path]) -> None:
    r = pytest_de_l_apprenant(W / "data" / "metriques.csv", modeles["faible"], modeles["champion"])
    exiger_refus(r, "a model whose RMSE is above rmse_max", "un modèle dont le RMSE dépasse rmse_max")


def test_la_suite_refuse_un_modele_moins_bon_que_le_champion(modeles: dict[str, Path]) -> None:
    r = pytest_de_l_apprenant(W / "data" / "metriques.csv", modeles["moins_bon"], modeles["champion"])
    exiger_refus(
        r, "a model more than 1 ms above the champion RMSE (even under rmse_max)",
        "un modèle à plus de 1 ms au-dessus du RMSE du champion (même sous rmse_max)",
    )


def test_seuil_lu_dans_un_fichier_versionne() -> None:
    import re

    suivis = subprocess.run(["git", "ls-files"], cwd=W, capture_output=True, text=True, check=False).stdout.split()
    assert "seuils.yaml" in suivis and any(f.startswith("tests/") for f in suivis), message(
        en="seuils.yaml and the tests/ folder must be committed.",
        fr="seuils.yaml et le dossier tests/ doivent être versionnés.",
    )
    m = re.search(r"^rmse_max:\s*([0-9.]+)", (W / "seuils.yaml").read_text(), re.M)
    assert m and 20.0 < float(m.group(1)) <= 28.0, message(
        en="seuils.yaml must define rmse_max, a number above 20 and at most 28.0.",
        fr="seuils.yaml doit définir rmse_max, un nombre au-dessus de 20 et au plus 28,0.",
    )
    sources = "".join(p.read_text() for p in (W / "tests").glob("*.py"))
    assert "seuils.yaml" in sources, message(
        en="The tests must read the threshold from seuils.yaml, not hard-code it.",
        fr="Les tests doivent lire le seuil dans seuils.yaml, pas l'écrire en dur.",
    )
