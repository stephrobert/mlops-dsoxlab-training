# m1-dvc-donnees

**Audience:** the learner.

Version a dataset with DVC and an S3 remote, and get it back identically.

## Prerequisites

Docker, `uv`, `git`, having played `m1-projet-reproductible`. Start the stack
before `dsoxlab run`: `bash scripts/socle-demarrer.sh`. S3 keys are in
`shared/socle/.env` (export them: `set -a; source shared/socle/.env; set +a`).
Stop: `bash scripts/socle-arreter.sh`.
