"""Boîte à outils de l'AI Data Analyst : tous les calculs passent par ici.

Principe : le modèle raisonne, le code calcule. Mêmes données → mêmes chiffres,
à chaque exécution. L'agent n'invente jamais un chiffre « de tête ».
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUTS = ROOT / "outputs"
RETURN_WINDOW_DAYS = 28  # règle métier : les clients retournent dans les 4 semaines


# ---------------------------------------------------------------- chargement

def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Charge commandes et retours, avec les dates parsées et la semaine (lundi)."""
    orders = pd.read_csv(DATA_DIR / "orders.csv", parse_dates=["order_date", "cancellation_date"])
    returns = pd.read_csv(DATA_DIR / "returns.csv", parse_dates=["return_date"])
    orders["week"] = orders["order_date"].dt.to_period("W-SUN").dt.start_time
    returns["week"] = returns["return_date"].dt.to_period("W-SUN").dt.start_time
    returns = returns.merge(
        orders[["order_id", "order_date", "category", "status"]],
        on="order_id", how="left", validate="many_to_one")
    returns["delay_days"] = (returns["return_date"] - returns["order_date"]).dt.days
    return orders, returns


def extraction_date(orders: pd.DataFrame, returns: pd.DataFrame) -> pd.Timestamp:
    """Dernier jour observé dans les données."""
    return max(orders["order_date"].max(), returns["return_date"].max())


def usable_weeks(orders: pd.DataFrame, returns: pd.DataFrame) -> pd.DatetimeIndex:
    """Semaines (lundi) exploitables pour compter les retours.

    - on écarte la dernière semaine si elle est partielle ;
    - on écarte les 4 premières semaines : les retours de commandes passées AVANT
      le début de l'historique n'existent pas dans les données, le volume y est sous-estimé.
    """
    end = extraction_date(orders, returns)
    weeks = pd.date_range(orders["week"].min(), end, freq="W-MON")
    weeks = weeks[weeks + pd.Timedelta(days=6) <= end]
    return weeks[RETURN_WINDOW_DAYS // 7:]


# ---------------------------------------------------------- les 3 niveaux

def raw_returns(orders, returns) -> pd.DataFrame:
    """Niveau 0 — sans contexte : nombre de retours par semaine."""
    weeks = usable_weeks(orders, returns)
    r = returns.groupby("week").size().reindex(weeks, fill_value=0)
    return pd.DataFrame({"week": weeks, "returns": r.to_numpy()})


def same_week_rate(orders, returns) -> pd.DataFrame:
    """Niveau 1 — on normalise, mais naïvement : retours(S) / commandes livrées(S)."""
    weeks = usable_weeks(orders, returns)
    delivered = orders[orders["status"] == "delivered"].groupby("week").size().reindex(weeks, fill_value=0)
    r = returns.groupby("week").size().reindex(weeks, fill_value=0)
    return pd.DataFrame({"week": weeks, "returns": r.to_numpy(),
                         "delivered_orders": delivered.to_numpy(),
                         "return_rate": (r / delivered).to_numpy()})


def lagged_rate(orders, returns, lag_weeks: int = 4) -> pd.DataFrame:
    """Niveau 2 — règle métier : retours(S) / moyenne des commandes livrées des 4 semaines précédentes.

    Un retour de la semaine S vient d'un achat fait entre S-4 et S-1 : c'est
    ce volume-là qu'il faut mettre au dénominateur.
    """
    weeks = usable_weeks(orders, returns)
    delivered = orders[orders["status"] == "delivered"].groupby("week").size()
    delivered = delivered.reindex(pd.date_range(delivered.index.min(), weeks.max(), freq="W-MON"), fill_value=0)
    base = delivered.shift(1).rolling(lag_weeks).mean().reindex(weeks)
    r = returns.groupby("week").size().reindex(weeks, fill_value=0)
    df = pd.DataFrame({"week": weeks, "returns": r.to_numpy(),
                       "avg_delivered_prev_4_weeks": base.round(1).to_numpy(),
                       "return_rate": (r / base).to_numpy()})
    return df.dropna().reset_index(drop=True)  # les 4 premières semaines n'ont pas d'historique


def cohort_rate(orders, returns, by: str | None = None, grain: str = "W") -> pd.DataFrame:
    """Vérification indépendante : pour chaque période d'achat, part des commandes livrées
    retournées dans les 28 jours. Seules les cohortes « mûres » (28 jours écoulés) sont gardées.
    """
    end = extraction_date(orders, returns)
    dlv = orders[orders["status"] == "delivered"].copy()
    dlv["period"] = dlv["order_date"].dt.to_period("W-SUN" if grain == "W" else "M").dt.start_time
    in_window = returns[returns["delay_days"] <= RETURN_WINDOW_DAYS]
    dlv["returned_28d"] = dlv["order_id"].isin(in_window["order_id"])
    # une cohorte est mûre si la dernière commande de la période a eu 28 jours pour être retournée
    period_end = dlv.groupby("period")["order_date"].transform("max")
    dlv = dlv[period_end + pd.Timedelta(days=RETURN_WINDOW_DAYS) <= end]
    keys = ["period"] + ([by] if by else [])
    out = dlv.groupby(keys).agg(delivered_orders=("order_id", "size"),
                                returned_28d=("returned_28d", "sum")).reset_index()
    out["return_rate"] = out["returned_28d"] / out["delivered_orders"]
    return out


def cancellation_rate(orders) -> pd.DataFrame:
    """Part des commandes annulées par mois (les annulations arrivent 0 à 2 jours après l'achat)."""
    m = orders.assign(month=orders["order_date"].dt.to_period("M").dt.start_time)
    out = m.groupby("month").agg(orders=("order_id", "size"),
                                 cancelled=("status", lambda s: (s == "cancelled").sum())).reset_index()
    out["cancellation_rate"] = out["cancelled"] / out["orders"]
    return out
