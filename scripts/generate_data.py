"""Génère un jeu de données retail fictif : commandes, annulations et retours.

Ce qui est caché dans les données (à découvrir pendant la démo) :
  1. Un pic de ventes énorme pendant la semaine du Black Friday (28 nov. 2025)
     et pendant Noël → un pic de retours mécanique 1 à 4 semaines plus tard.
  2. Les clients retournent leurs achats dans les 4 semaines (≈ 9 retours sur 10).
  3. Un vrai problème : à partir du 1er octobre 2025, la catégorie Chaussures
     (nouveau fournisseur) passe d'environ 15 % à 24 % de retours.
  4. Les commandes annulées ne peuvent pas être retournées : elles ne doivent
     pas compter dans le dénominateur.

Usage : python scripts/generate_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
START = pd.Timestamp("2025-01-06")  # un lundi
END = pd.Timestamp("2026-02-01")    # date d'extraction des données
BLACK_FRIDAY = pd.Timestamp("2025-11-28")
SUPPLIER_CHANGE = pd.Timestamp("2025-10-01")

CATEGORIES = {
    #               part des ventes, panier moyen (€), taux de retour de base
    "Vêtements":    (0.35, 45, 0.22),
    "Chaussures":   (0.15, 70, 0.15),
    "Maison":       (0.20, 55, 0.06),
    "Électronique": (0.15, 160, 0.08),
    "Beauté":       (0.15, 30, 0.04),
}
REASONS = ["Taille ne convient pas", "Ne correspond pas à la description",
           "Produit défectueux", "A changé d'avis", "Livraison trop tardive"]

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def daily_volume(day: pd.Timestamp) -> float:
    """Nombre moyen de commandes attendu un jour donné (saisonnalité retail)."""
    base = 320
    if day.day_of_week >= 5:                     # week-end un peu plus fort
        base *= 1.15
    if day.month in (6, 7):                      # soldes d'été
        base *= 1.25
    if day.year == 2026 and day.month == 1:      # soldes d'hiver
        base *= 1.20
    days_from_bf = (day - BLACK_FRIDAY).days
    if -4 <= days_from_bf <= 3:                  # semaine du Black Friday + Cyber Monday
        base *= 4.5 if days_from_bf in (0, 3) else 3.0
    if pd.Timestamp("2025-12-08") <= day <= pd.Timestamp("2025-12-22"):  # Noël
        base *= 1.9
    return base


def main() -> None:
    rng = np.random.default_rng(SEED)
    days = pd.date_range(START, END - pd.Timedelta(days=1), freq="D")
    names = list(CATEGORIES)
    shares = np.array([CATEGORIES[c][0] for c in names])

    rows = []
    for day in days:
        n = rng.poisson(daily_volume(day))
        cats = rng.choice(names, size=n, p=shares)
        for cat in cats:
            basket = CATEGORIES[cat][1]
            rows.append((day, cat, round(float(rng.gamma(4, basket / 4)), 2)))

    orders = pd.DataFrame(rows, columns=["order_date", "category", "amount_eur"])
    orders.insert(0, "order_id", [f"O{i:06d}" for i in range(1, len(orders) + 1)])
    orders.insert(2, "customer_id", [f"CU{x:05d}" for x in rng.integers(1, 40_000, len(orders))])

    # Annulations : ~3 % des commandes, annulées 0 à 2 jours après l'achat
    cancelled = rng.random(len(orders)) < 0.03
    orders["status"] = np.where(cancelled, "cancelled", "delivered")
    cancel_delay = rng.integers(0, 3, len(orders))
    orders["cancellation_date"] = pd.NaT
    orders.loc[cancelled, "cancellation_date"] = (
        orders.loc[cancelled, "order_date"] + pd.to_timedelta(cancel_delay[cancelled], unit="D")
    )

    # Retours : uniquement sur les commandes livrées
    rate = orders["category"].map(lambda c: CATEGORIES[c][2]).to_numpy().copy()
    issue = (orders["category"] == "Chaussures") & (orders["order_date"] >= SUPPLIER_CHANGE)
    rate[issue.to_numpy()] = 0.24
    returned = (rng.random(len(orders)) < rate) & (orders["status"] == "delivered").to_numpy()

    # Délai de retour : la grande majorité dans les 4 semaines, une petite traîne au-delà
    n_ret = int(returned.sum())
    within_4_weeks = rng.random(n_ret) < 0.92
    delay = np.where(within_4_weeks,
                     rng.triangular(2, 9, 28, n_ret),
                     rng.uniform(29, 45, n_ret)).round().astype(int)

    returns = orders.loc[returned, ["order_id", "order_date", "category"]].copy()
    returns["return_date"] = returns["order_date"] + pd.to_timedelta(delay, unit="D")
    reason_p = np.array([0.30, 0.20, 0.15, 0.30, 0.05])
    returns["reason"] = rng.choice(REASONS, size=n_ret, p=reason_p)
    shoes = (returns["category"] == "Chaussures") & (returns["order_date"] >= SUPPLIER_CHANGE)
    returns.loc[shoes, "reason"] = rng.choice(
        REASONS, size=int(shoes.sum()), p=[0.55, 0.15, 0.10, 0.17, 0.03])

    # On ne voit que les retours déjà arrivés à la date d'extraction
    returns = returns[returns["return_date"] < END].sort_values("return_date")
    returns.insert(0, "return_id", [f"R{i:06d}" for i in range(1, len(returns) + 1)])
    returns = returns[["return_id", "order_id", "return_date", "reason"]]

    DATA_DIR.mkdir(exist_ok=True)
    orders.to_csv(DATA_DIR / "orders.csv", index=False, date_format="%Y-%m-%d")
    returns.to_csv(DATA_DIR / "returns.csv", index=False, date_format="%Y-%m-%d")
    print(f"orders.csv  : {len(orders):,} lignes "
          f"({orders['order_date'].min():%d/%m/%Y} → {orders['order_date'].max():%d/%m/%Y})")
    print(f"returns.csv : {len(returns):,} lignes")


if __name__ == "__main__":
    main()
