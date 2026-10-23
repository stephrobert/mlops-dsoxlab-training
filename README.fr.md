# Formation MLOps : rendre un entraînement reproductible, et le prouver

**Langue :** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/mlops-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/mlops-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/mlops-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/mlops-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/mlops-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/mlops-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![Licence : CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Sept labs pour rendre un projet d'apprentissage automatique reproductible et
traçable : figer un entraînement pour qu'il rende deux fois le même résultat,
retrouver la version exacte d'un jeu de données, rejouer l'ensemble en
pipeline, retrouver quelle exécution a produit un modèle, le désigner par
alias, et en refuser un moins bon. Chaque lab se joue **sur votre propre
machine**, dans un shell, et il est noté sur l'état où le projet finit, jamais
sur les commandes tapées.

Écrit pour les ingénieurs qui héritent d'un modèle que personne ne sait
reconstruire.

## Ce que c'est

À la fin, un apprenant sait prendre un script d'entraînement qui rend un
résultat différent à chaque passage et rendre un projet où l'exécution est
figée, les données versionnées, le pipeline rejouable, et où le registre dit
quelle exécution a produit le modèle en service. Chacun de ces points est
prouvé par des tests qui lisent l'état du projet et du registre MLflow, jamais
les commandes tapées.

**L'ordre compte, et ce n'est pas celui des sujets.** La reproductibilité vient
avant le suivi, parce que suivre une exécution qu'on ne sait pas rejouer
enregistre un chiffre invérifiable. Le suivi vient avant le registre, et le
registre avant les tests qui refusent une régression.

`dsoxlab next` suit cet ordre, dérivé de la position de chaque lab dans
`meta.yml`.

### Ce que les tests font, et ce qu'ils refusent de faire

**Un lab est noté sur l'état du projet, jamais sur les commandes tapées.**

Les tests interrogent le registre MLflow par son API, rejouent le pipeline
DVC, et comparent les artefacts produits. Ils ne lisent pas le script écrit
par l'apprenant.

Le piège ainsi évité est celui de l'exécution qui a l'air reproductible. Un
script dont la graine est fixée à un endroit, pendant qu'une bibliothèque tire
d'un autre, rend deux modèles différents et une seule ligne de journal
identique : les labs exigent donc **le même artefact deux fois**, pas le même
message.

## Prérequis

Un prérequis manquant coûte une heure de recherche à l'apprenant, donc cette
liste est exacte et mesurée sur `meta.yml`.

- **Python 3.11+ et [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **`dsoxlab`**, le moteur, installé en outil autonome (voir plus bas)

**Aucune machine virtuelle, aucun hyperviseur, aucun `provision`.** Les sept
labs sont des labs `shell` : ils tournent sur votre poste, dans le répertoire
de travail que le lab pose. `meta.yml` ne déclare aucun bloc `infra:`, ce qui
fait de ce catalogue le plus léger de la collection à démarrer.

`dsoxlab doctor` dit ce dont ce dépôt a besoin et ce dont il n'a pas besoin, et
distingue un contrôle qui a échoué d'un contrôle qu'il n'a pas pu mesurer.

## Installation

`dsoxlab` est publié sur [PyPI](https://pypi.org/project/dsoxlab/).
Installe-le en outil autonome, pour qu'il reste hors de ce dépôt :

```bash
# 1. La CLI dsoxlab (outil externe, hors de ce dépôt)
uv tool install dsoxlab

# 2. Ce catalogue de labs
git clone https://github.com/stephrobert/mlops-dsoxlab-training.git
cd mlops-dsoxlab-training

# 3. Vérifier le contrat
dsoxlab validate-structure
dsoxlab doctor
```

### Votre premier lab, en cinq minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                           # les sept labs, dans l'ordre
dsoxlab run       m1-projet-reproductible   # pose l'état de départ
dsoxlab challenge m1-projet-reproductible   # lire la mission, sans pas-à-pas
dsoxlab check     m1-projet-reproductible   # joue les tests, enregistre le score
dsoxlab clean     m1-projet-reproductible   # défait ce que le lab a posé
```

C'est `run` qui prépare le lab : il copie dans le répertoire de travail les
fixtures déclarées. Un `check` joué sur un lab jamais démarré ne mesure rien,
et le dit au lieu d'enregistrer un 0.

### Garder à jour

```bash
uv tool upgrade dsoxlab        # le moteur, publié sur PyPI
git -C <ce dépôt> pull         # le catalogue
```

## Comment ça marche

### Le contrat déclaratif, à deux niveaux

Ce dépôt n'est **pas** la CLI. Un défaut du moteur se corrige dans
[dsoxlab](https://github.com/stephrobert/dsoxlab), ou s'y signale par une
issue. Ici, tout ce qui pilote la CLI est déclaratif :

- **`meta.yml`** à la racine déclare l'identité du dépôt et l'**ordre** des
  sections affichées par `list-labs`. Il ne déclare **aucune infrastructure** ;
- **`lab.yaml`** par lab déclare ses `skills`, son `level`, son `runtime`
  (type, `workdir`, `fixtures`), ses `distros`, son `doc_url` et un bloc
  `validation`. Un `lab.fr.yaml` surcharge `title` et `description` en
  français, et rien d'autre ;
- **`challenge/tests/test_functional.py`** porte la preuve.

Une fixture déclarée mais absente du disque fait échouer `run` et nomme toutes
les fautives d'un coup. Un fichier présent dans `fixtures/` mais non déclaré
est signalé par `validate-structure`. Les deux sens sont contrôlés, parce
qu'un répertoire de travail à moitié rempli a l'air de marcher et envoie
l'apprenant chercher l'erreur dans son propre code.

### Le cycle de vie d'un lab

```bash
dsoxlab list-labs              # parcourir le catalogue
dsoxlab show      <id>         # métadonnées et état d'un lab
dsoxlab run       <id>         # poser l'état initial
dsoxlab challenge <id>         # lire la mission, sans pas-à-pas
dsoxlab hint      <id>         # révéler un indice (déduit du score)
dsoxlab check     <id>         # jouer les tests, calculer et enregistrer le score
dsoxlab submit    <id>         # pour l'épreuve : un verdict, pas un score
dsoxlab clean     <id>         # défaire ce que le lab a posé
dsoxlab progress               # progression par section, score moyen
```

### Le modèle de validation

La validation **prouve l'état, elle ne fait pas confiance**, et un lab est
prouvé **dans les deux sens** : les tests doivent échouer avant le travail et
passer après. Un test vert avant le travail n'est pas un test, c'est une
hypothèse sur le setup. `scripts/valider-labs.py` exige **0 avant et 100
après**, et inscrit le verdict dans
[`validation-labs.json`](./validation-labs.json) : **7 VALIDE sur 7**.

Les corrigés de référence vivent dans `solution/<lab>/solution.sh`, et les
**huit sont chiffrés** par `ansible-vault`. Un corrigé livré en clair gâche le
lab, et git le garde pour toujours.

## Catalogue

Sept labs, **4 h 30** en tout. Les niveaux 2 et 3 sont déclarés dans
`meta.yml` et ne portent encore aucun lab : le dire vaut mieux que de laisser
un apprenant le découvrir à mi-parcours.

### Niveau 1 : reproduire

Six labs, 3 h 45.

| Lab | Ce qu'il prouve |
|---|---|
| `m1-projet-reproductible` | le même entraînement rend deux fois le même artefact |
| `m1-dvc-donnees` | la version exacte d'un jeu de données revient |
| `m1-dvc-pipeline` | l'entraînement se rejoue en pipeline, pas de mémoire |
| `m1-mlflow-serveur` | on retrouve l'exécution qui a produit un modèle |
| `m1-registre-alias` | un modèle se désigne par alias, pas par numéro |
| `m1-tests-modele` | un modèle moins bon et des données cassées sont refusés |

### Épreuve de niveau

Un lab évalué, 45 min.

| Lab | Ce qu'il prouve |
|---|---|
| `e1-reproduire` | **évalué** : un modèle rendu reproductible et traçable |

### Niveaux 2 et 3

`m2-livrer` et `m3-exploiter` sont déclarés et vides. C'est le prochain
travail sur ce catalogue.

## Contribuer

Lire [`CONTRIBUTING.md`](./CONTRIBUTING.md). En résumé : un lab est prouvé
**dans les deux sens** avant d'être fusionné, `dsoxlab validate-structure` est
vert, et l'énoncé existe en anglais et en français.

Un verdict ne se commite jamais avec le code partagé qu'il mesure : le contrôle
de péremption compare des dates de commit, et un verdict écrit dans le même
commit que les fichiers qu'il note ne laisse rien à comparer. Un hook l'impose.

## Licence

Voir [`LICENSE`](./LICENSE).
