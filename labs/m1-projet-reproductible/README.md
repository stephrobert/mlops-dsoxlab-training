# m1-projet-reproductible

**Audience:** the learner.

Make a training run reproducible: seed, configuration, locked environment and
exact data.

## What you will be able to do

- Spot the sources of randomness in a training run.
- Move seed and hyperparameters out of the code into a versioned file.
- Lock the environment with `uv` (`pyproject.toml` and `uv.lock`).
- Prove reproducibility by the fingerprint of the metrics.

## Prerequisites

Python 3.12, `uv`, `git`, PyPI access. Guide: lesson L1 of the MLOps course.

```bash
dsoxlab run m1-projet-reproductible
cd labs/m1-projet-reproductible/challenge/work
dsoxlab check m1-projet-reproductible
```
