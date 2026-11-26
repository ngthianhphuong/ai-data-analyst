"""Étape 4 — Vérifier que la réponse est fiable AVANT de la partager.

Chaque contrôle renvoie OK, ATTENTION (à mentionner dans le rapport) ou BLOQUANT
(on ne partage pas tant que ce n'est pas résolu).

Usage : python scripts/verify.py
"""

import pandas as pd

import retail as r

results: list[tuple[str, str, str]] = []


def check(name: str, status: str, detail: str) -> None:
    results.append((status, name, detail))


def main() -> None:
    o, t = r.load()
    end = r.extraction_date(o, t)

    # 1. Intégrité des données
    orphans = int(t["order_date"].isna().sum())
    check("Chaque retour correspond à une commande", "OK" if orphans == 0 else "BLOQUANT",
          f"{orphans} retour(s) orphelin(s)")
    on_cancelled = int((t["status"] == "cancelled").sum())
    check("Aucun retour sur une commande annulée", "OK" if on_cancelled == 0 else "BLOQUANT",
          f"{on_cancelled} retour(s) sur commande annulée")
    before_purchase = int((t["delay_days"] < 0).sum())
    check("Aucun retour daté avant l'achat", "OK" if before_purchase == 0 else "BLOQUANT",
          f"{before_purchase} cas")
    dupes = int(t["order_id"].duplicated().sum())
    check("Une commande n'est retournée qu'une fois", "OK" if dupes == 0 else "ATTENTION",
          f"{dupes} commande(s) retournée(s) plusieurs fois")

    # 2. La règle métier est-elle confirmée par les données ?
    share_28d = (t["delay_days"] <= r.RETURN_WINDOW_DAYS).mean()
    check("Règle métier « retours sous 4 semaines » confirmée",
          "OK" if share_28d >= 0.85 else "ATTENTION",
          f"{share_28d:.1%} des retours arrivent dans les 28 jours")

    # 3. Réconciliation : la somme des semaines = le total sur la même période
    weekly = r.raw_returns(o, t)
    window = t[(t["week"] >= weekly["week"].min()) & (t["week"] <= weekly["week"].max())]
    gap = int(weekly["returns"].sum()) - len(window)
    check("Somme des retours hebdo = total sur la période", "OK" if gap == 0 else "BLOQUANT",
          f"écart de {gap}")

    # 4. Données incomplètes en fin de période
    weeks = r.usable_weeks(o, t)
    excluded = o["week"].max() not in weeks
    check("Semaine partielle exclue", "OK",
          f"dernière semaine complète : {weeks.max():%d/%m/%Y}" + (" (semaine en cours écartée)" if excluded else ""))
    immature = o[(o["status"] == "delivered") &
                 (o["order_date"] > end - pd.Timedelta(days=r.RETURN_WINDOW_DAYS))]
    check("Commandes récentes encore « en période de retour »", "ATTENTION",
          f"{len(immature):,} commandes de moins de 28 jours : leurs retours ne sont pas encore tous arrivés")

    # 5. Triangulation : deux méthodes indépendantes donnent-elles le même ordre de grandeur ?
    lagged = r.lagged_rate(o, t).set_index("week")["return_rate"]
    cohort = r.cohort_rate(o, t).set_index("period")["return_rate"]
    common = lagged.index.intersection(cohort.index)
    m_lag, m_coh = lagged.loc[common].mean(), cohort.loc[common].mean()
    gap_pts = abs(m_lag - m_coh) * 100
    check("Méthode décalée vs méthode par cohorte (exacte)",
          "OK" if gap_pts < 1.5 else "ATTENTION",
          f"moyenne {m_lag:.1%} vs {m_coh:.1%} ({gap_pts:.1f} pt d'écart sur {len(common)} semaines)")
    bf = pd.Timestamp("2025-11-24")
    if bf in cohort.index:
        normal = cohort[(cohort.index < bf) & (cohort.index >= bf - pd.Timedelta(weeks=8))].mean()
        check("Les achats du Black Friday sont-ils plus retournés ?",
              "OK", f"cohorte BF {cohort[bf]:.1%} vs {normal:.1%} les 8 semaines avant")

    # 6. Les segments se recomposent en total
    by_cat = r.cohort_rate(o, t, by="category", grain="M")
    total = r.cohort_rate(o, t, grain="M")
    recomposed = by_cat["returned_28d"].sum()
    check("Somme des catégories = total", "OK" if recomposed == total["returned_28d"].sum() else "BLOQUANT",
          f"{recomposed:,} retours recomposés vs {total['returned_28d'].sum():,}")

    # Rapport
    icons = {"OK": "✅", "ATTENTION": "⚠️ ", "BLOQUANT": "❌"}
    print("=== RAPPORT DE VÉRIFICATION ===\n")
    for status, name, detail in results:
        print(f"{icons[status]} {status:<9} {name}\n             {detail}")
    blocking = sum(s == "BLOQUANT" for s, _, _ in results)
    warnings = sum(s == "ATTENTION" for s, _, _ in results)
    print(f"\nVerdict : {'NE PAS PARTAGER' if blocking else 'FIABLE, partageable'} "
          f"({blocking} bloquant(s), {warnings} point(s) d'attention à mentionner)")

    r.OUTPUTS.mkdir(exist_ok=True)
    with open(r.OUTPUTS / "verification.md", "w") as f:
        f.write("# Rapport de vérification\n\n| Statut | Contrôle | Détail |\n|---|---|---|\n")
        for status, name, detail in results:
            f.write(f"| {icons[status].strip()} {status} | {name} | {detail} |\n")


if __name__ == "__main__":
    main()
