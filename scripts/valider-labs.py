#!/usr/bin/env python3
"""Joue chaque lab dans les DEUX sens, par dsoxlab, et écrit validation-labs.json.

Forme du catalogue frère dev-pour-ops-dsoxlab-training : par lab, `avant` et
`apres` (echecs, passed, score, total), `rejeu` (après clean et run, doit
retomber à 0), `commit`, `date`, `duree_s`, `ecarts`, `etapes`, `raisons`,
`verdict` (VALIDE si avant = 0, après = 100 et rejeu = 0, sinon ROUGE).

Enchaînement : socle S3 démarré (labs qui en ont besoin), clean, run, check,
solution déchiffrée jouée dans le workdir, check, clean, run, check, clean,
socle arrêté. Une sortie 0 de `docker ps` sur `mlops-socle` est exigée à la fin.

    python3 scripts/valider-labs.py                  # tous les labs
    python3 scripts/valider-labs.py --lab <id>       # un seul (ne réécrit que lui)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
RELEVE = RACINE / "validation-labs.json"


def dso(*args: str):
    return subprocess.run(["dsoxlab", *args], cwd=RACINE, input="y\n",
                          capture_output=True, text=True, timeout=900)


def check(lab: str) -> dict:
    r = dso("check", lab, "--json")
    c = json.loads(r.stdout)["check"]
    echecs = sorted(set(re.findall(r"::(\w+) (?:FAILED|ERROR)", c.get("output", ""))))
    return {"echecs": echecs, "passed": c["passed"], "score": int(c["score"]),
            "total": c["total"]}


# Labs qui ont besoin du serveur MLflow et de PostgreSQL en plus de Garage.
AVEC_MLFLOW = {"m1-mlflow-serveur", "m1-registre-alias", "e1-reproduire"}


def socle(action: str, lab: str = "") -> None:
    args = ["mlflow"] if action == "demarrer" and lab in AVEC_MLFLOW else []
    subprocess.run(["bash", str(RACINE / "scripts" / f"socle-{action}.sh"), *args],
                   cwd=RACINE, check=True, capture_output=True)


def a_besoin_du_socle(lab: str) -> bool:
    fiche = RACINE / "preparation" / "fiches" / f"{lab}.md"
    return lab in AVEC_MLFLOW or (fiche.exists() and "S3" in fiche.read_text())


def conteneurs() -> int:
    r = subprocess.run(["docker", "ps", "--format", "{{.Names}}"],
                       capture_output=True, text=True)
    return sum(1 for n in r.stdout.split() if n.startswith("mlops-socle"))


def solution(lab: str, work: Path) -> int:
    with tempfile.TemporaryDirectory() as tmp:
        for f in (RACINE / "solution" / lab).iterdir():
            subprocess.run(["ansible-vault", "decrypt", "--vault-password-file",
                            str(RACINE / ".vault-pass"), "--output",
                            f"{tmp}/{f.name}", str(f)],
                           check=True, capture_output=True)
        return subprocess.run(["bash", f"{tmp}/solution.sh"], cwd=work,
                              env={**os.environ, "MLOPS_RACINE": str(RACINE)},
                              capture_output=True).returncode


def joue(lab: str) -> dict:
    t0 = time.time()
    work = RACINE / "labs" / lab / "challenge" / "work"
    res = {"commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RACINE,
                                    capture_output=True, text=True).stdout.strip(),
           "date": date.today().isoformat(), "ecarts": [], "etapes": [], "raisons": []}
    ver = subprocess.run(["uv", "--version"], capture_output=True, text=True).stdout.split()
    res["python"] = ".".join(map(str, sys.version_info[:3]))
    res["uv"] = ver[1] if len(ver) > 1 else ""
    besoin = a_besoin_du_socle(lab)
    try:
        dso("clean", lab)
        if besoin:
            socle("arreter"); socle("demarrer", lab)
            res["etapes"].append("socle S3 (Garage) démarré, bucket vide")
        dso("run", lab)
        res["avant"] = check(lab)
        res["etapes"].append(f"avant le travail : {res['avant']['passed']}/{res['avant']['total']}")
        rc = solution(lab, work)
        if rc:
            res["raisons"].append(f"solution.sh a rendu {rc}")
        res["apres"] = check(lab)
        res["etapes"].append(f"après la solution : {res['apres']['passed']}/{res['apres']['total']}")
        dso("clean", lab)
        if besoin:
            socle("arreter"); socle("demarrer", lab)  # bucket vidé, comme un poste neuf
        dso("run", lab)
        res["rejeu"] = check(lab)
        res["etapes"].append(f"après clean et run : {res['rejeu']['passed']}/{res['rejeu']['total']}")
    finally:
        dso("clean", lab)
        if besoin:
            socle("arreter")
        if besoin and conteneurs():
            res["ecarts"].append("conteneur mlops-socle resté actif")
        res["etapes"].append("poste rendu intact" if not res["ecarts"] else "écart sur le poste")
    ok = (res.get("avant", {}).get("score") == 0 and res.get("apres", {}).get("score") == 100
          and res.get("rejeu", {}).get("score") == 0 and not res["ecarts"])
    res["verdict"] = "VALIDE" if ok else "ROUGE"
    res["duree_s"] = int(time.time() - t0)
    return res


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lab", action="append")
    a = p.parse_args()
    meta = yaml.safe_load((RACINE / "meta.yml").read_text())
    tous = [lab for s in meta["sections"] for lab in s.get("labs") or []]
    cibles = a.lab or tous
    releve = json.loads(RELEVE.read_text()) if RELEVE.exists() else {}
    for lab in cibles:
        print(f"[valider-labs] {lab}", flush=True)
        releve[lab] = joue(lab)
        print(f"[valider-labs] {lab} : {releve[lab]['verdict']} "
              f"({releve[lab]['duree_s']}s)", flush=True)
    RELEVE.write_text(json.dumps(releve, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return 0 if all(releve[l]["verdict"] == "VALIDE" for l in cibles) else 1


if __name__ == "__main__":
    sys.exit(main())
