#!/usr/bin/env python3
"""Générateur du jeu de données fil rouge : métriques de services.

Produit un CSV de métriques par service et par minute (CPU, mémoire, requêtes,
taux d'erreur, latence p95) et deux cibles : `latence_p95_ms` (régression) et
`incident` (classification : latence au-dessus du seuil ou erreurs excessives).

Déterministe : même graine, mêmes paramètres, même fichier, octet pour octet.
Bibliothèque standard seule. Les nombres sont écrits avec un nombre fixe de
décimales et les lignes se terminent par un saut de ligne unique, quelle que
soit la plateforme.

Dérive (M3) : `--derive` (0 = aucune) décale la distribution à partir de la
fraction `--derive-debut` du jeu. Deux effets, pour montrer ce que la dérive
dit et ne dit pas :
  - dérive des entrées : la charge (requêtes/s) augmente de `derive` * 100 % ;
  - dérive du concept : à charge égale, la latence monte de `derive` * 100 %
    (régression de code, voisin bruyant).
`--derive-mode entrees` ou `concept` n'applique qu'un des deux effets.

Exemples :
    python3 genere-metriques.py --graine 42 --lignes 5000 --sortie train.csv
    python3 genere-metriques.py --graine 43 --lignes 2000 --derive 0.5 \
        --derive-debut 0.0 --sortie production.csv
"""

import argparse
import math
import random
import sys

SERVICES = ("api-gateway", "auth", "catalogue", "paiement", "recherche")
# Charge de base (requêtes/s) et latence de base (ms) propres à chaque service.
BASE = {
    "api-gateway": (220.0, 35.0),
    "auth": (90.0, 22.0),
    "catalogue": (150.0, 48.0),
    "paiement": (40.0, 85.0),
    "recherche": (120.0, 70.0),
}
SEUIL_LATENCE_MS = 250.0
SEUIL_ERREURS = 0.05
COLONNES = (
    "horodatage_min", "service", "cpu_pct", "memoire_pct", "requetes_s",
    "taux_erreur", "latence_p95_ms", "incident",
)


def borne(x, bas, haut):
    return max(bas, min(haut, x))


def genere(graine, lignes, derive, derive_debut, mode):
    rng = random.Random(graine)
    debut_derive = int(lignes * derive_debut)
    sortie = []
    for i in range(lignes):
        service = SERVICES[i % len(SERVICES)]
        minute = i // len(SERVICES)
        base_req, base_lat = BASE[service]
        # Cycle de charge de 120 minutes (court, pour ne pas confondre saison et dérive).
        cycle = 1.0 + 0.45 * math.sin(2 * math.pi * (minute % 120) / 120.0)
        req = base_req * cycle * rng.lognormvariate(0.0, 0.12)
        derive_active = derive > 0 and i >= debut_derive
        if derive_active and mode in ("tout", "entrees"):
            req *= 1.0 + derive
        # Pics de charge rares : la cause principale des incidents.
        if rng.random() < 0.01:
            req *= rng.uniform(2.0, 3.5)
        cpu = borne(8.0 + req / base_req * 28.0 + rng.gauss(0.0, 4.0), 1.0, 100.0)
        mem = borne(35.0 + (0.04 * minute) % 25 + req / base_req * 8.0
                    + rng.gauss(0.0, 3.0), 5.0, 100.0)
        # La latence suit la saturation du CPU : convexe au-delà de 70 %.
        saturation = max(0.0, cpu - 70.0) / 30.0
        lat = base_lat * (1.0 + 0.9 * (cpu / 100.0) + 6.0 * saturation ** 2)
        lat *= rng.lognormvariate(0.0, 0.08)
        if derive_active and mode in ("tout", "concept"):
            lat *= 1.0 + derive
        err = borne(0.002 + 0.12 * saturation ** 2 + rng.gauss(0.0, 0.002), 0.0, 1.0)
        incident = 1 if (lat > SEUIL_LATENCE_MS or err > SEUIL_ERREURS) else 0
        sortie.append((minute, service, cpu, mem, req, err, lat, incident))
    return sortie


def ecrit(donnees, flux):
    flux.write(",".join(COLONNES) + "\n")
    for m, s, cpu, mem, req, err, lat, inc in donnees:
        flux.write(f"{m},{s},{cpu:.2f},{mem:.2f},{req:.2f},{err:.5f},{lat:.2f},{inc}\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--graine", type=int, default=42)
    p.add_argument("--lignes", type=int, default=5000)
    p.add_argument("--derive", type=float, default=0.0,
                   help="amplitude de la dérive (0 = aucune, 0.5 = +50 %%)")
    p.add_argument("--derive-debut", type=float, default=0.5,
                   help="fraction du jeu où la dérive commence (0 à 1)")
    p.add_argument("--derive-mode", choices=("tout", "entrees", "concept"),
                   default="tout")
    p.add_argument("--sortie", default="-", help="fichier CSV, ou - pour stdout")
    a = p.parse_args(argv)
    if a.lignes < 1 or a.derive < 0 or not 0 <= a.derive_debut <= 1:
        p.error("paramètres hors bornes")
    donnees = genere(a.graine, a.lignes, a.derive, a.derive_debut, a.derive_mode)
    if a.sortie == "-":
        ecrit(donnees, sys.stdout)
    else:
        with open(a.sortie, "w", encoding="utf-8", newline="\n") as f:
            ecrit(donnees, f)
    return 0


if __name__ == "__main__":
    sys.exit(main())
