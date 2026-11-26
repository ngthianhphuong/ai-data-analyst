---
description: Répondre à une question métier avec la méthode AI Data Analyst (cadrer, profiler, analyser, vérifier, partager)
argument-hint: [question du stakeholder]
---

Question du stakeholder : $ARGUMENTS

Applique la méthode de `CLAUDE.md` du début à la fin :

1. Lis `context/company.md`, `context/business_rules.md` et `context/corrections.md`.
   Dis en une ligne quelles règles métier tu vas appliquer (ou qu'il n'y en a pas).
2. Cadre la question en une phrase (décision, indicateur, période).
3. Lance `scripts/profile_data.py` et résume le profil en 3 lignes.
4. Lance `scripts/analyze.py` avec le niveau imposé par les règles métier, ouvre le graphique.
5. Lance `scripts/verify.py`. S'il y a un BLOQUANT, arrête-toi et explique.
6. Écris `outputs/report.md`, `outputs/email.md` et `outputs/slack.md`.
7. Termine par ta réponse au stakeholder en 3 phrases, puis demande si tu dois partager
   (Google Docs, Slides, Gmail, Slack).
