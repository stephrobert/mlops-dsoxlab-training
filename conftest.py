"""Les helpers partagés par les tests de ce catalogue.

POURQUOI CE FICHIER EST ICI ET PAS DANS DSOXLAB

Un test de lab doit rester jouable par un simple `pytest`, sans l'outil
installé : c'est le test de non-couplage du catalogue. Un
`from dsoxlab… import` en tête d'un fichier de tests le casserait. dsoxlab ne
reconnaît donc que la FORME de l'appel, `message(en=…, fr=…)`.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def message(en: str, fr: str) -> str:
    """Le message d'une assertion, dans la langue de l'apprenant.

    Quand un test échoue, `dsoxlab check` affiche le message écrit par
    l'auteur : c'est la seule consigne que l'apprenant reçoit à cet instant. Or
    tout le reste du catalogue existe dans les deux langues, et ce texte-là ne
    peut pas : le contrat impose un nom de fichier unique,
    `challenge/tests/test_functional.py`. Il n'y a donc pas de version anglaise
    possible par duplication, d'où ce choix à l'exécution.

    Usage :

        from conftest import message

        assert chemin.exists(), message(
            en="/etc/myapp is missing. Create it.",
            fr="/etc/myapp est absent. Crée-le.",
        )
    """
    langue = os.environ.get("DSOXLAB_LANG", "en").lower()
    return fr if langue.startswith("fr") else en


def workdir_lab(fichier_test: str | Path) -> Path:
    """Le répertoire de travail du lab auquel appartient un fichier de test.

    `<lab>/challenge/work` par défaut ; `LAB_WORKDIR` le surcharge, ce dont le
    mode formateur se sert pour jouer la solution de référence ailleurs.
    """
    surcharge = os.environ.get("LAB_WORKDIR")
    if surcharge:
        return Path(surcharge)
    return Path(fichier_test).resolve().parents[2] / "challenge" / "work"


def exiger_workdir(workdir: Path, lab_id: str) -> None:
    """Skippe un lab qui n'a pas été démarré, au lieu de le noter 0.

    Un répertoire de travail absent ne dit pas que l'apprenant a échoué : il
    dit que `dsoxlab run` n'a pas été joué. Les deux appellent des gestes
    opposés, donc on skippe en le nommant. dsoxlab 0.4.1 et au-delà
    n'enregistrent aucune note quand TOUS les tests skippent.
    """
    if not workdir.is_dir():
        pytest.skip(
            f"le lab {lab_id} n'a pas été démarré : joue `dsoxlab run {lab_id}`"
        )
