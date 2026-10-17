# m1-projet-reproductible

**Public :** l'apprenant.

Rendre un entraînement reproductible : graine, configuration, environnement
verrouillé et données exactes.

## Ce que vous saurez faire

- Repérer les sources d'aléa d'un entraînement.
- Sortir graine et hyperparamètres du code, dans un fichier versionné.
- Verrouiller l'environnement avec `uv` (`pyproject.toml` et `uv.lock`).
- Prouver la reproductibilité par l'empreinte des métriques.

## Prérequis

Python 3.12, `uv`, `git`, accès à PyPI. Guide : leçon L1 du parcours MLOps.

```bash
dsoxlab run m1-projet-reproductible
cd labs/m1-projet-reproductible/challenge/work
dsoxlab check m1-projet-reproductible
```
