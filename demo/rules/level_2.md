# Règles métier

## Taux de retour
- Ne jamais juger les retours sur leur volume brut : quand les ventes augmentent, les retours
  augmentent mécaniquement. Toujours rapporter les retours aux ventes.
- **Les clients retournent leurs achats dans les 4 semaines.** Un retour de cette semaine
  correspond donc à un achat des 4 semaines précédentes, pas de la semaine en cours.
- Taux de retour = retours de la semaine ÷ moyenne des commandes livrées des 4 semaines précédentes.
  → `scripts/analyze.py --level 2`
- Les commandes **annulées** ne sont jamais expédiées : elles sont exclues du dénominateur.
- Les commandes de moins de 4 semaines ne sont pas « terminées » : leurs retours n'ont pas
  encore eu le temps d'arriver. Le signaler dans les limites.

## Diagnostic
- Si le taux global bouge, ou pour confirmer qu'il ne bouge pas, toujours regarder par
  catégorie (`scripts/analyze.py --categories`) : une catégorie peut se dégrader sans que
  le global ne le montre.
- Pour une catégorie qui se dégrade, regarder les motifs de retour pour proposer une cause.
