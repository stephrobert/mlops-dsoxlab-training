# MLOps Training: reproduce a training run, and prove it

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/mlops-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/mlops-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/mlops-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/mlops-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/mlops-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/mlops-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Seven hands-on labs to make a machine learning project reproducible and
traceable: pin a training run so it gives the same result twice, get back the
exact version of a dataset, replay the whole thing as a pipeline, find which
run produced a model, designate it by alias, and refuse a worse one. Every lab
runs **on your own machine**, in a shell, and is graded on the state the
project ends in, never on the commands typed.

Written for engineers who inherit a model nobody can rebuild.

## What it is

At the end, a learner can take a training script that gives a different result
at every run and return a project where the run is pinned, the data is
versioned, the pipeline replays, and the registry says which run produced the
model that is serving. Each of those is proven by tests that read the state of
the project and of the MLflow registry, never the commands typed.

**The order matters, and it is not the order of the topics.** Reproducibility
comes before tracking, because tracking a run you cannot replay records a
number nobody can check. Tracking comes before the registry, and the registry
before the tests that refuse a regression.

`dsoxlab next` follows that order, derived from the position of each lab in
`meta.yml`.

### What the tests do, and what they refuse to do

**A lab is graded on the state of the project, never on the commands typed.**

The tests question the MLflow registry through its API, replay the DVC
pipeline, and compare the artefacts produced. They do not read the script the
learner wrote.

The trap this avoids is the run that looks reproducible. A script with a seed
set in one place and a library that draws from another gives two different
models and one identical log line, so the labs require the **same artefact
twice**, not the same message.

## Requirements

A missing requirement costs the learner an hour of searching, so this list is
exact and measured against `meta.yml`.

- **Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)**
- **`git`**
- **`dsoxlab`**, the engine, installed as a standalone tool (see below)

**No virtual machine, no hypervisor, no `provision`.** All seven labs are
`shell` labs: they run on your own machine, in the working directory the lab
lays down. `meta.yml` declares no `infra:` block at all, which is what makes
this catalog the lightest of the collection to start.

`dsoxlab doctor` says what this repository needs and what it does not, and
tells apart a check that failed from one it could not measure.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/). Install it
as a standalone tool, so it stays out of this repository:

```bash
# 1. The dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab

# 2. This lab catalog
git clone https://github.com/stephrobert/mlops-dsoxlab-training.git
cd mlops-dsoxlab-training

# 3. Check the contract
dsoxlab validate-structure
dsoxlab doctor
```

### Your first lab, in five minutes

```bash
export LAB_HOME=$PWD
dsoxlab list-labs                           # the seven labs, in teaching order
dsoxlab run       m1-projet-reproductible   # sets the starting state
dsoxlab challenge m1-projet-reproductible   # read the mission, no step-by-step
dsoxlab check     m1-projet-reproductible   # run the tests, record the score
dsoxlab clean     m1-projet-reproductible   # undo what the lab set up
```

`run` is what prepares the lab: it copies the declared fixtures into the
working directory. Running `check` on a lab you never started measures
nothing, and says so rather than recording a 0.

### Keeping it up to date

```bash
uv tool upgrade dsoxlab        # the engine, published on PyPI
git -C <this repo> pull        # the catalog
```

## How it works

### The declarative contract (two levels)

This repository is **not the CLI**. An engine defect is fixed in
[dsoxlab](https://github.com/stephrobert/dsoxlab), or reported as an issue
there. Here, everything driving the CLI is declarative:

- **`meta.yml`** at the root declares the repository identity and the **order**
  of the sections shown by `list-labs`. It declares **no infrastructure**;
- **`lab.yaml`** per lab declares its `skills`, `level`, `runtime` (type,
  `workdir`, `fixtures`), `distros`, `doc_url` and a `validation` block. A
  `lab.fr.yaml` overrides `title` and `description` in French, and nothing
  else;
- **`challenge/tests/test_functional.py`** carries the proof.

A fixture that is declared but missing from disk makes `run` fail and names
every offender at once. A file present in `fixtures/` but not declared is
reported by `validate-structure`. The two directions are checked, because a
half-filled working directory looks like it works and sends the learner
hunting for a mistake in their own code.

### The lab lifecycle

```bash
dsoxlab list-labs              # browse the catalog
dsoxlab show      <id>         # metadata and status of one lab
dsoxlab run       <id>         # lay down the initial state
dsoxlab challenge <id>         # read the mission, no step-by-step
dsoxlab hint      <id>         # reveal a hint (deducted from the score)
dsoxlab check     <id>         # run the tests, compute and record the score
dsoxlab submit    <id>         # for the exam: a verdict, not a bare score
dsoxlab clean     <id>         # undo what the lab set up
dsoxlab progress               # per-section progress, average score
```

### The validation model

Validation **proves the state, it does not trust the learner**, and a lab is
proven **in both directions**: the tests must fail before the work and pass
after it. A test that is green before the work is not a test, it is an
assumption about the setup. `scripts/valider-labs.py` requires **0 before and
100 after**, and records the verdict in
[`validation-labs.json`](./validation-labs.json): **7 VALIDE out of 7**.

The reference solutions live in `solution/<lab>/solution.sh`, and **all eight
are encrypted** with `ansible-vault`. A solution shipped in clear text spoils
the lab, and git keeps it forever.

## Catalog

Seven labs, **4 h 30** in all. Levels 2 and 3 are declared in `meta.yml` and
carry no lab yet: saying so is better than letting a learner discover it
halfway through.

### Level 1: reproduce

Six labs, 3 h 45.

| Lab | What it proves |
|---|---|
| `m1-projet-reproductible` | the same training run gives the same artefact twice |
| `m1-dvc-donnees` | the exact version of a dataset comes back |
| `m1-dvc-pipeline` | the training replays as a pipeline, not as a memory |
| `m1-mlflow-serveur` | the run that produced a model can be found |
| `m1-registre-alias` | a model is designated by alias, not by number |
| `m1-tests-modele` | a worse model and broken data are refused |

### Level exam

One graded lab, 45 min.

| Lab | What it proves |
|---|---|
| `e1-reproduire` | **graded**: a model made reproducible and traceable |

### Levels 2 and 3

`m2-livrer` (ship) and `m3-exploiter` (operate) are declared and empty. They
are the next work on this catalog.

## Contributing

Read [`CONTRIBUTING.md`](./CONTRIBUTING.md). In short: a lab is proven **in both
directions** before it is merged, `dsoxlab validate-structure` is green, and the
statement exists in English and in French.

A verdict is never committed together with the shared code it measures: the
staleness check compares commit dates, and a verdict written in the same commit
as the files it grades leaves nothing to compare. A hook enforces it.

## License

See [`LICENSE`](./LICENSE).
