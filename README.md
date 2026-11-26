# AI Data Analyst

**Un agent IA simple qui analyse des données comme un data analyst rigoureux :
il lit le contexte métier, analyse, vérifie sa réponse et la partage.**

Il tourne dans [Claude Code](https://claude.com/claude-code). Le cas d'usage est volontairement
simple : un e-commerce, des commandes, des annulations et des retours.

---

## La question

Claire, directrice du service client :

> « Depuis décembre, mes équipes croulent sous les retours. Est-ce que nos clients sont de
> plus en plus mécontents ? »

| Ce que l'agent sait | Ce qu'il répond | Juste ? |
|---|---|---|
| **Rien** | « Les retours ont été multipliés par 2,2 après le Black Friday. » | ❌ Il y a plus de retours parce qu'il y a eu plus de ventes |
| **« Rapporte les retours aux ventes »** | « Le taux passe de 5 % à 22 % en un mois ! » | ❌ Les retours de décembre viennent des achats de novembre |
| **« Les clients retournent sous 4 semaines »** | « Le taux est stable, autour de 14 %. **Mais Chaussures passe de 14 % à 22 % depuis octobre** (problème de tailles). » | ✅ |

Les données et le modèle sont les mêmes dans les trois cas. La seule chose qui change, c'est
**10 lignes de contexte métier** écrites en français dans `context/business_rules.md`.

## La méthode en 5 étapes

```
 1. FRAME     → quelle décision ? quel indicateur ?
 2. PROFILE   → scripts/profile_data.py   (volumes, période, anomalies)
 3. ANALYZE   → scripts/analyze.py        (le calcul imposé par les règles métier)
 4. VERIFY    → scripts/verify.py         (intégrité, règle métier, 2 méthodes qui concordent)
 5. SHARE     → /share : rapport, email, Slack, Google Docs / Slides (validés par un humain)
```

Quatre principes :
1. **Le contexte avant les données.** Les règles métier sont écrites dans des fichiers que
   l'agent lit avant de commencer.
2. **Le modèle raisonne, le code calcule.** Tous les chiffres sortent de scripts Python :
   mêmes données, mêmes chiffres, à chaque exécution.
3. **Toujours comparer.** Un chiffre seul n'est pas une conclusion.
4. **Vérifier avant de partager.** Un contrôle bloquant empêche le partage. Les limites
   font partie de la réponse.

## Installation (5 minutes)

Prérequis : Python 3.10+ et [Claude Code](https://claude.com/claude-code).

```bash
git clone <ce-repo> ai-data-analyst
cd ai-data-analyst
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/generate_data.py   # (re)génère les données de démo
claude
```

Puis dans Claude Code :

```
/analyze Depuis décembre les retours explosent. Nos clients sont-ils de plus en plus mécontents ?
```

Pour la démo complète en 3 niveaux de contexte, suivez [demo/DEMO_SCRIPT.md](demo/DEMO_SCRIPT.md).

## Structure

```
ai-data-analyst/
├── CLAUDE.md                 ← les instructions de l'agent (la méthode)
├── context/                  ← ce que l'agent sait du métier
│   ├── company.md            ·  l'entreprise, le dictionnaire des données, le stakeholder
│   ├── business_rules.md     ·  comment calculer les indicateurs (source de vérité)
│   ├── corrections.md        ·  les erreurs corrigées, pour ne pas les répéter
│   └── sharing.md            ·  où et comment partager
├── data/                     ← orders.csv, returns.csv (données fictives)
├── scripts/
│   ├── retail.py             ·  tous les calculs
│   ├── profile_data.py       ·  étape 2
│   ├── analyze.py            ·  étape 3 (+ graphiques)
│   ├── verify.py             ·  étape 4
│   ├── generate_data.py      ·  crée les données de démo
│   └── set_context.sh        ·  change le niveau de contexte (démo)
├── demo/                     ← les 3 niveaux de règles métier + le script de démo
├── outputs/                  ← rapports, graphiques, messages (générés)
└── .claude/commands/         ← /analyze et /share
```

## Partager vers Google, Gmail et Slack

`/share docs | slides | email | slack` utilise les connecteurs de Claude
(Google Drive, Google Docs, Google Slides, Gmail, Slack), à activer dans les réglages des
connecteurs de claude.ai ou via `/mcp`. Sans connecteur, l'agent écrit quand même les
fichiers dans `outputs/` : il suffit de les copier-coller.

L'agent **n'envoie jamais rien seul** : il crée un brouillon d'email et attend votre
« ok » avant de publier sur Slack.

## Adapter à vos données

1. Remplacez les CSV dans `data/` et décrivez-les dans `context/company.md`.
2. Écrivez **vos** règles métier dans `context/business_rules.md`. C'est là que se trouve
   la valeur ajoutée de l'analyste.
3. Adaptez les calculs dans `scripts/retail.py` et les contrôles dans `scripts/verify.py`.

---

Inspiré de [ai-analyst](https://github.com/ai-analyst-lab/ai-analyst) (MIT), en version
volontairement minimaliste et pédagogique.
