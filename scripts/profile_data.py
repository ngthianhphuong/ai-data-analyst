"""Étape 2 — Lire et profiler les données AVANT de leur faire confiance.

Usage : python scripts/profile_data.py
"""

import retail as r


def main() -> None:
    orders, returns = r.load()
    end = r.extraction_date(orders, returns)
    weeks = r.usable_weeks(orders, returns)

    print("=== PROFIL DES DONNÉES ===\n")
    print(f"orders.csv  : {len(orders):,} lignes, du {orders['order_date'].min():%d/%m/%Y} "
          f"au {orders['order_date'].max():%d/%m/%Y}")
    print(f"returns.csv : {len(returns):,} lignes, du {returns['return_date'].min():%d/%m/%Y} "
          f"au {returns['return_date'].max():%d/%m/%Y}")
    print(f"Date d'extraction (dernier jour observé) : {end:%d/%m/%Y}")
    print(f"Semaines exploitables : {len(weeks)} (du {weeks.min():%d/%m/%Y} au {weeks.max():%d/%m/%Y})")
    print("  ⚠ Les 4 premières semaines sont exclues : les retours d'achats antérieurs à l'historique manquent.")
    last = orders["week"].max()
    if last not in weeks:
        print(f"  ⚠ La semaine du {last:%d/%m/%Y} est incomplète → exclue des analyses hebdo.")

    print("\n--- Qualité ---")
    print(f"Doublons order_id  : {orders['order_id'].duplicated().sum()}")
    print(f"Doublons return_id : {returns['return_id'].duplicated().sum()}")
    print(f"Commandes retournées plusieurs fois : {returns['order_id'].duplicated().sum()}")
    nulls = orders.drop(columns=["cancellation_date"]).isna().sum()
    print(f"Valeurs manquantes (orders, hors cancellation_date) : {int(nulls.sum())}")
    print(f"Retours sans commande correspondante : {returns['order_date'].isna().sum()}")

    print("\n--- Statuts ---")
    for status, n in orders["status"].value_counts().items():
        print(f"  {status:<10} {n:>8,}  ({n / len(orders):.1%})")

    print("\n--- Catégories (part des commandes) ---")
    for cat, share in orders["category"].value_counts(normalize=True).items():
        print(f"  {cat:<13} {share:.1%}")

    print("\n--- Délai entre achat et retour (jours) ---")
    d = returns["delay_days"]
    print(f"  médiane {d.median():.0f} j · 90e centile {d.quantile(0.9):.0f} j · max {d.max()} j")
    print(f"  retours faits dans les 28 jours : {(d <= r.RETURN_WINDOW_DAYS).mean():.1%}")

    print("\n--- Volume de commandes par mois ---")
    by_month = orders.groupby(orders["order_date"].dt.to_period("M")).size()
    mean = by_month.mean()
    for month, n in by_month.items():
        flag = "  ← pic" if n > 1.4 * mean else ""
        print(f"  {month}  {n:>7,}{flag}")


if __name__ == "__main__":
    main()
