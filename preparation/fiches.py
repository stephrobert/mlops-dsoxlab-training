"""Génère preparation/fiches/*.md depuis la table du cadrage §7 (une fiche par lab)."""
import os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fiches")
os.makedirs(D, exist_ok=True)
LABS = [
 ("m1-projet-reproductible","L1","poste (Python)","guidé","Obtenir deux fois les mêmes métriques d'un entraînement.","un dossier de projet vide, le générateur `shared/genere-metriques.py`","le script d'entraînement, la graine et les dépendances sont versionnés ; deux exécutions donnent les mêmes métriques (empreinte identique)"),
 ("m1-dvc-donnees","L2","conteneur S3 (Garage)","guidé","Retrouver une version exacte du jeu de données.","un dépôt Git sans DVC, le socle S3 démarré","`dvc status` propre ; l'empreinte du jeu est dans le bucket ; un `dvc pull` sur un clone vierge redonne le même SHA-256 ; une seconde version du jeu est retrouvable par `git checkout`"),
 ("m1-dvc-pipeline","L3","conteneur S3 (Garage)","guidé","Rejouer l'entraînement à l'identique par `dvc repro`.","le dépôt du lab précédent avec ses données suivies","`dvc.yaml` décrit les étapes ; `dvc repro` rejoue sans rien recalculer quand rien ne change ; changer un paramètre ne relance que l'étape touchée ; les métriques attendues sortent"),
 ("m1-mlflow-serveur","L4","conteneurs MLflow, PostgreSQL, S3","guidé","Savoir quel run a produit quel modèle.","le socle `shared/socle/` arrêté ; un script d'entraînement sans suivi","le serveur répond sur `/health` ; un run porte paramètres, métriques, commit Git et empreinte des données ; son artefact est dans le bucket S3 ; les métadonnées survivent à un redémarrage du serveur (PostgreSQL)"),
 ("m1-registre-alias","L5","mêmes conteneurs","guidé","Désigner un modèle par alias, sans chemin.","le socle démarré avec un run existant","un modèle est enregistré en version 1 puis 2 ; l'alias `challenger` pointe la bonne version ; la lignée remonte au run ; le chargement `models:/nom@challenger` fonctionne"),
 ("m1-tests-modele","L6","poste","guidé","Refuser un modèle moins bon, et des données au schéma cassé.","un modèle de référence, un jeu valide et un jeu au schéma cassé fourni","la suite pytest échoue sur le jeu cassé et sur le modèle dégradé, passe sur les valides ; le seuil est lu dans un fichier versionné"),
 ("e1-reproduire","épreuve m1","conteneurs (socle complet)","challenge","Prouver le niveau 1 sans indice : 45 min.","un dépôt avec jeu, code et socle ; un jeu au schéma cassé fourni","`dvc status` propre ; empreinte des données dans S3 ; `dvc repro` du correcteur redonne la métrique attendue ; un run MLflow porte commit et empreinte ; l'alias `challenger` est posé ; la suite de tests échoue sur le schéma cassé"),
 ("m2-empaqueter","L7","Docker","guidé","Un modèle qui répond hors notebook.","un modèle du registre","une image épinglée par digest sert une prédiction HTTP ; la prédiction de référence est exacte ; le conteneur tourne sans privilège"),
 ("m2-kserve-installer","L9","kind","guidé","Plan de contrôle KServe prêt (mode Standard).","un cluster kind vierge","les déploiements KServe sont `Available` ; le CRD `InferenceService` existe ; versions épinglées"),
 ("m2-kserve-servir","L10","kind et S3","guidé","Servir le modèle du registre avec un `InferenceService`.","KServe installé, un modèle dans le bucket S3","`InferenceService` `READY=True` ; la prédiction de référence passe par l'API ; l'initialiseur de stockage a lu le S3"),
 ("m2-canary","L11","kind","guidé","10 % du trafic vers la nouvelle version, puis décider.","un service en version 1","la part de trafic demandée va à la version 2 (mesurée sur un lot de requêtes) ; la promotion ou l'annulation laisse un état cohérent"),
 ("m2-cicd-modele","L12","`act` et kind","guidé","Un pipeline qui refuse un modèle moins bon.","un workflow GitHub Actions et un dépôt","le workflow passe avec le bon modèle, échoue avec le modèle dégradé fourni, sans bouger l'alias `champion`"),
 ("m2-entrainement-continu","L13","kind","guidé","Réentraîner sans intervention ni risque.","un CronJob d'entraînement désactivé","le job tourne, enregistre un candidat sans toucher `champion` ; une exécution échouée ne laisse aucun état partiel"),
 ("e2-livrer","épreuve m2","kind, S3, `act`","challenge","Prouver le niveau 2 sans indice : 60 min.","cluster, registre et dépôt fournis","`InferenceService` `READY=True` ; prédiction de référence ; canary sur la part demandée ; pipeline qui échoue avec le modèle dégradé sans bouger `champion`"),
 ("m3-observer-inference","L14","kind et Prometheus","guidé","Voir le service avant le modèle.","un service servi, sans métriques scrutées","Prometheus scrute le service ; latence, trafic et erreurs sont interrogeables ; une requête PromQL donnée rend la valeur attendue"),
 ("m3-derive-production","L16","kind, Prometheus, job Evidently","guidé","Alerte sur dérive réelle.","un service servi, un flux de production sans dérive, puis avec dérive injectée par le générateur","une alerte de dérive passe à `firing` sur le flux dérivé et reste silencieuse sans dérive"),
 ("m3-rollback","L17","kind","guidé","Revenir à un modèle sain, joué hors incident.","un `champion` dégradé en service","l'alias `champion` est repointé ; l'`InferenceService` sert de nouveau le modèle sain ; la prédiction de référence est retrouvée"),
 ("m3-carte-de-modele","L18","conteneurs MLflow","guidé","Prouver d'où vient un modèle.","un modèle du registre","la carte de modèle (données, code, métriques, limites) est rattachée à la version et complète ; la lignée remonte jusqu'au commit"),
 ("e3-exploiter","épreuve m3","kind, Prometheus, S3","challenge","Prouver le niveau 3 sans indice : 60 min.","service dégradé, dérive injectée, registre fourni","alerte de dérive `firing` ; alias `champion` repointé ; `InferenceService` sert de nouveau le champion ; runbook versionné"),
]
for (i, lecon, env, typ, obj, etat, valide) in LABS:
    with open(os.path.join(D, i + ".md"), "w", encoding="utf-8") as fiche:
        fiche.write(f"""# {i}

| Champ | Valeur |
|---|---|
| Leçon | {lecon} |
| Type | {typ} |
| Environnement | {env} |
| Durée | à mesurer en jouant le lab |

## Objectif

{obj}

## État initial

{etat}.

## Ce que la validation contrôle sur l'état réel

{valide}.

La note ne dépend jamais des commandes tapées : les tests interrogent le système (DVC, S3, MLflow, Kubernetes, Prometheus). Le lab se joue dans les deux sens : `dsoxlab check` rend 0 avant le travail et 100 après la solution.

## À faire avant d'écrire le lab

- `dsoxlab new lab {i} --runtime shell` (ou `vm`), jamais un `lab.yaml` à la main ;
- rejouer le scénario complet avant d'écrire la leçon du site (règle B : lab avant guide).
""")
print(len(LABS), "fiches")
