# Journal des modifications

Les changements notables de ce catalogue sont consignés ici. Le format suit
[Keep a Changelog](https://keepachangelog.com/fr/1.1.0/), et ce catalogue suit
le [versionnage sémantique](https://semver.org/lang/fr/).

**Ce qu'une version veut dire ici.** Un catalogue n'est pas une bibliothèque :
un incrément MINEUR ajoute des labs, un CORRECTIF corrige un énoncé ou un test
sans changer ce qu'un lab prouve, et un incrément MAJEUR renomme ou retire des
labs, ce qui casse la progression déjà enregistrée des apprenants.

## [0.1.0] - 2026-10-23

### Ajouté

- **Première publication.** Sept labs pour rendre un projet d'apprentissage
  automatique reproductible et traçable, 4 h 30 en tout. Aucune machine
  virtuelle, aucun hyperviseur : les sept sont des labs `shell` et tournent sur
  le poste de l'apprenant.

- Les sept verdicts sont **VALIDE 0 -> 100**, et les huit corrigés de
  référence sont chiffrés par `ansible-vault`.

- **La chaîne de contribution des catalogues frères** : Zizmor, Actionlint,
  Poutine, parité pre-commit et CodeQL sur `python` et `actions`, plus
  Plumber, Scorecard, Dependabot et les gabarits d'issue. La CI passe d'un job
  à **six**, pour sept contrôles requis, et `main` porte le même ruleset que
  les autres : historique linéaire, pull request avec une revue, et les sept
  contrôles.

- Le hook qui refuse un verdict commité avec ce qu'il mesure, et le jeu de
  règles `ruff` commun à la collection.

### Manques connus

- Les niveaux 2 (`m2-livrer`) et 3 (`m3-exploiter`) sont déclarés dans
  `meta.yml` et ne portent encore aucun lab. Le dire vaut mieux que de laisser
  un apprenant le découvrir à mi-parcours.
