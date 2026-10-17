# Scénario

La semaine dernière, quelqu'un a relancé le générateur de métriques sur le
même fichier `data/metriques.csv`. Le jeu précédent (graine 42) est perdu, et
le modèle qui avait été entraîné dessus ne peut plus être reconstruit. Le dépôt
Git ne doit pas porter les données elles-mêmes : elles sont lourdes. Le socle
S3 du catalogue (Garage, bucket `dvc-donnees`, point d'accès
`http://127.0.0.1:3900`, région `garage`, clés dans `shared/socle/.env`) est
disponible.

## Mission

Dans le répertoire de travail (dépôt à initialiser, environnement avec DVC et
son support S3) : versionnez le jeu de graine 42 puis le jeu de graine 43, dans
deux commits distincts, avec les données dans le bucket. Un clone vierge doit
restituer par `dvc pull` le jeu courant (graine 43), et le retour au premier
commit doit restituer le jeu de graine 42, octet pour octet. Le dépôt reste
propre et la configuration du remote voyage avec le dépôt, pas les clés.
