# Script de démo (≈ 15 min)

**Message à faire passer :** une IA qui analyse des données sans contexte métier donne des
réponses fausses, avec beaucoup d'assurance. Le travail de l'analyste devient : **écrire le
contexte** et **vérifier** les réponses.

La question du stakeholder (Claire, directrice du service client), début février 2026 :

> « Depuis décembre, mes équipes croulent sous les retours. Est-ce que nos clients
> sont de plus en plus mécontents ? Faut-il lancer un plan qualité ? »

---

## Acte 1 : sans contexte (niveau 0)

```bash
./scripts/set_context.sh 0
claude
```
```
/analyze Depuis décembre les retours explosent. Nos clients sont-ils de plus en plus mécontents ? Faut-il lancer un plan qualité ?
```

**Ce qu'on voit :** le volume de retours est multiplié par 2,2 après le Black Friday.
L'agent, sans règle, rapporte le volume brut et conclut que les retours augmentent.

**Le point à faire passer :** le chiffre est juste, mais la conclusion est fausse. Il y a
plus de retours parce qu'il y a eu plus de ventes. Notez que l'agent dit lui-même que
l'indicateur n'a pas été validé par le métier : c'est la règle de `CLAUDE.md`.

## Acte 2 : on normalise (niveau 1)

```bash
./scripts/set_context.sh 1
```
Relancez la même question (`/clear` d'abord pour repartir de zéro).

**Ce qu'on voit :** le taux tombe à 5 % la semaine du Black Friday, puis grimpe à 22 % fin
décembre.

**Le point à faire passer :** normaliser ne suffit pas, il faut normaliser **correctement**.
Les retours de décembre viennent des ventes de novembre. Diviser par les ventes de la même
semaine donne une baisse trompeuse, puis une fausse alerte.

## Acte 3 : la vraie règle métier (niveau 2)

```bash
./scripts/set_context.sh 2
```
Montrez le fichier `context/business_rules.md` à l'écran : ce sont 10 lignes de français,
pas du code. Relancez la question.

**Ce qu'on voit :**
1. Avec le décalage de 4 semaines, le taux reste autour de 14 %. Pas d'emballement.
2. Les achats du Black Friday ne sont pas plus retournés que les autres (13,1 % contre 13,2 %).
3. **Mais** Chaussures passe de 14 % à 22 % depuis octobre, avec « taille ne convient pas »
   comme motif principal (54 % contre 29 %). C'est le vrai sujet, et il était invisible dans
   les chiffres globaux.

**La recommandation qui sort :** pas de plan qualité global. Renforcer le SAV de façon
temporaire après les pics de ventes, et ouvrir un sujet ciblé avec les acheteurs Chaussures
(guide des tailles, nouveau fournisseur ?).

## Acte 4 : la vérification

Montrez `outputs/verification.md` : intégrité des données, règle des 4 semaines confirmée
dans les données (92 % des retours), deux méthodes indépendantes qui concordent, et la limite
signalée (commandes récentes encore en période de retour).

## Acte 5 : le partage

```
/share email
/share slack
/share slides
```
Montrez que l'agent crée un **brouillon** et attend la validation : l'humain garde la main.

## Bonus : l'agent apprend

Corrigez l'agent en direct, par exemple : « Ne parle jamais de mécontentement client sans
regarder les motifs de retour. » Montrez qu'il l'ajoute dans `context/corrections.md` et
qu'il l'applique à la question suivante.

---

> ⚠️ L'IA ne lit pas toujours exactement la même chose. Si à l'acte 1 l'agent normalise
> de lui-même, profitez-en : sans règle écrite, chaque analyste (humain ou IA) choisit sa
> propre méthode. Le contexte rend la bonne méthode **systématique**.
