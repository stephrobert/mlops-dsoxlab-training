# Changelog

All notable changes to this catalog are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this catalog
follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**What a version means here.** A catalog is not a library: a MINOR bump adds
labs, a PATCH fixes a statement or a test without changing what a lab proves,
and a MAJOR renames or removes labs, which breaks the progress already recorded
by learners.

## [0.1.0] - 2026-10-23

### Added

- **First publication.** Seven labs to make a machine learning project
  reproducible and traceable, 4 h 30 in all. No virtual machine and no
  hypervisor: all seven are `shell` labs and run on the learner's own machine.

- The seven verdicts are **VALIDE 0 -> 100**, and the eight reference
  solutions are encrypted with `ansible-vault`.

- **The contribution chain of the sibling catalogs**: Zizmor, Actionlint,
  Poutine, pre-commit parity and CodeQL on `python` and `actions`, plus
  Plumber, Scorecard, Dependabot and the issue templates. The CI goes from one
  job to **six**, for seven required checks, and `main` carries the same
  ruleset as the others: linear history, pull request with one review, and the
  seven checks.

- The hook that refuses a verdict committed together with what it measures,
  and the `ruff` rule set shared by the collection.

### Known gaps

- Levels 2 (`m2-livrer`) and 3 (`m3-exploiter`) are declared in `meta.yml` and
  carry no lab yet. Saying so is better than letting a learner discover it
  halfway through.
