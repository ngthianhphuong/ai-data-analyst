---
description: Publier la dernière analyse (Google Docs, Google Slides, Gmail, Slack)
argument-hint: [docs | slides | email | slack | all]
---

Canal demandé : $ARGUMENTS (si vide : demande lequel).

1. Vérifie que `outputs/report.md` existe et que `outputs/verification.md` ne contient aucun
   BLOQUANT. Sinon, arrête-toi et dis pourquoi.
2. Lis `context/sharing.md` pour les destinataires et formats.
3. Selon le canal, avec les connecteurs disponibles :
   - **docs** : crée un Google Doc à partir de `outputs/report.md` (titre = la conclusion),
     avec les graphiques de `outputs/charts/`.
   - **slides** : crée 4 slides (conclusion, preuve chiffrée, cause, action), un graphique par slide.
   - **email** : crée un **brouillon** Gmail à partir de `outputs/email.md`. Ne l'envoie pas.
   - **slack** : affiche le message de `outputs/slack.md` et attends un « ok » avant de publier.
4. Donne les liens créés. Si un connecteur n'est pas disponible, dis-le et indique le fichier
   local à copier-coller à la place.
