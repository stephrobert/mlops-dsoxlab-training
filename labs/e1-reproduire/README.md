# e1-reproduire

**Audience:** the learner.

Level 1 exam: make a model reproducible and traceable, without hints.

## Prerequisites

Docker, `uv`, `git`, the lessons and labs of level 1. Start the stack before
`dsoxlab run`: `bash scripts/socle-demarrer.sh mlflow`. Stop it with
`bash scripts/socle-arreter.sh`. S3 keys: `set -a; source shared/socle/.env; set +a`.

For a new attempt, stop and restart the stack (`bash scripts/socle-arreter.sh`
then `bash scripts/socle-demarrer.sh mlflow`): `dsoxlab clean` does not empty the
bucket nor the MLflow server.
