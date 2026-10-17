#!/usr/bin/env python3
"""Joue un lab dans les DEUX sens, par dsoxlab, et affiche le verdict.

Pour chaque lab : clean, setup.sh (s'il existe), run, check (DOIT rendre 0 :
le travail n'est pas fait), solution/<lab>/solution.sh joué dans le répertoire
de travail, check (DOIT rendre 100), cleanup.sh puis clean. Le verdict est
VALIDE si 0 puis 100, ROUGE sinon.

    python3 scripts/valider-labs.py --lab m1-projet-reproductible
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def dso(*args: str, check_json: bool = False):
    r = subprocess.run(
        ["dsoxlab", *args], cwd=RACINE, input="y\n", capture_output=True, text=True
    )
    return r


def score(lab: str) -> int | None:
    r = dso("check", lab, "--json")
    try:
        return int(json.loads(r.stdout)["check"]["score"])
    except (ValueError, KeyError, TypeError):
        print(r.stdout[-1500:], r.stderr[-500:])
        return None


def etape(msg: str) -> None:
    print(f"[valider-labs] {msg}", flush=True)


def joue(lab: str) -> bool:
    d = RACINE / "labs" / lab
    work = d / "challenge" / "work"
    t0 = time.time()
    dso("clean", lab)
    if (d / "cleanup.sh").exists():
        subprocess.run(["bash", str(d / "cleanup.sh")], cwd=RACINE)
    if (d / "setup.sh").exists():
        etape("setup.sh")
        subprocess.run(["bash", str(d / "setup.sh")], cwd=RACINE, check=True)
    dso("run", lab)
    avant = score(lab)
    etape(f"sans solution : {avant} (attendu 0)")
    t1 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        for f in (RACINE / "solution" / lab).iterdir():
            subprocess.run(
                ["ansible-vault", "decrypt", "--vault-password-file",
                 str(RACINE / ".vault-pass"), "--output", f"{tmp}/{f.name}", str(f)],
                check=True, capture_output=True,
            )
        r = subprocess.run(["bash", f"{tmp}/solution.sh"], cwd=work)
    etape(f"solution.sh rc={r.returncode} en {time.time() - t1:.0f}s")
    apres = score(lab)
    etape(f"avec solution : {apres} (attendu 100)")
    if (d / "cleanup.sh").exists():
        subprocess.run(["bash", str(d / "cleanup.sh")], cwd=RACINE)
    dso("clean", lab)
    ok = avant == 0 and apres == 100
    etape(f"{lab} : {'VALIDE' if ok else 'ROUGE'} ({time.time() - t0:.0f}s)")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lab", action="append", required=True)
    a = p.parse_args()
    return 0 if all([joue(lab) for lab in a.lab]) else 1


if __name__ == "__main__":
    sys.exit(main())
