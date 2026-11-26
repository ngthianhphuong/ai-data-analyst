"""Étape 3 — Analyser : calcule l'indicateur demandé et produit le graphique.

Usage :
  python scripts/analyze.py --level 0     # volume brut de retours (sans contexte)
  python scripts/analyze.py --level 1     # taux de retour naïf (retours / commandes de la même semaine)
  python scripts/analyze.py --level 2     # taux de retour avec décalage de 4 semaines (règle métier)
  python scripts/analyze.py --categories  # taux de retour par catégorie (cohortes mensuelles)

Sorties : outputs/level_X.csv, outputs/charts/level_X.png, et un résumé chiffré à l'écran.
"""

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

import retail as r

GREY, LIGHT_GREY, ACCENT, RED = "#8C8C8C", "#D0D0D0", "#0072B2", "#C0392B"
MONTHS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
BLACK_FRIDAY_WEEK = pd.Timestamp("2025-11-24")  # lundi de la semaine du Black Friday


def style(ax, title: str, subtitle: str) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(LIGHT_GREY)
    ax.spines["bottom"].set_color(LIGHT_GREY)
    ax.tick_params(colors=GREY)
    ax.grid(axis="y", color="#EEEEEE")
    ax.set_axisbelow(True)
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", color="#222222", pad=26)
    ax.text(0, 1.02, subtitle, transform=ax.transAxes, fontsize=10, color=GREY)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, _: f"{MONTHS_FR[mdates.num2date(x).month - 1]} {mdates.num2date(x):%y}"))


def save(fig, name: str) -> str:
    (r.OUTPUTS / "charts").mkdir(parents=True, exist_ok=True)
    path = r.OUTPUTS / "charts" / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=160, facecolor="white")
    plt.close(fig)
    return str(path.relative_to(r.ROOT))


def before_after(df: pd.DataFrame, col: str) -> tuple[float, float, float]:
    """Moyenne des 8 semaines avant le Black Friday, pic après, et 3 dernières semaines."""
    bf = BLACK_FRIDAY_WEEK
    before = df[(df["week"] < bf) & (df["week"] >= bf - pd.Timedelta(weeks=8))][col].mean()
    after = df[df["week"] >= bf]
    return before, after[col].max(), df[col].tail(3).mean()


def level_0(o, t):
    df = r.raw_returns(o, t)
    before, peak, last = before_after(df, "returns")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["week"], df["returns"], color=RED, lw=2)
    ax.axvline(BLACK_FRIDAY_WEEK, color=GREY, ls=":", lw=1)
    ax.text(BLACK_FRIDAY_WEEK, ax.get_ylim()[1] * 0.95, " Black Friday", color=GREY, fontsize=9)
    style(ax, f"Les retours ont été multipliés par {peak / before:.1f} après le Black Friday",
          "Nombre de retours par semaine · volume brut, sans normalisation")
    return df, save(fig, "level_0"), {
        "avg_returns_8_weeks_before_bf": round(before), "peak_returns_after_bf": int(peak),
        "avg_returns_last_3_weeks": round(last), "peak_multiplier": round(peak / before, 2)}


def level_1(o, t):
    df = r.same_week_rate(o, t)
    before, peak, last = before_after(df, "return_rate")
    dip = df[df["week"] == BLACK_FRIDAY_WEEK]["return_rate"].iloc[0]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["week"], df["return_rate"] * 100, color=RED, lw=2)
    ax.axvline(BLACK_FRIDAY_WEEK, color=GREY, ls=":", lw=1)
    ax.set_ylabel("% des commandes livrées", color=GREY)
    style(ax, f"Taux naïf : {dip:.0%} la semaine du Black Friday, puis {peak:.0%} fin décembre",
          "Retours de la semaine ÷ commandes livrées de la même semaine · ⚠ mesure trompeuse")
    return df, save(fig, "level_1"), {
        "avg_rate_8_weeks_before_bf": round(before, 3), "rate_bf_week": round(dip, 3),
        "max_rate_after_bf": round(peak, 3), "avg_rate_last_3_weeks": round(last, 3)}


def level_2(o, t):
    df = r.lagged_rate(o, t)
    naive = r.same_week_rate(o, t)
    before, peak, last = before_after(df, "return_rate")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(naive["week"], naive["return_rate"] * 100, color=LIGHT_GREY, lw=1.5)
    ax.plot(df["week"], df["return_rate"] * 100, color=ACCENT, lw=2.5)
    x_end = df["week"].iloc[-1]
    ax.text(x_end, df["return_rate"].iloc[-1] * 100, "  décalé 4 sem.", color=ACCENT, fontsize=9, va="center")
    ax.text(x_end, naive["return_rate"].iloc[-1] * 100 + 1.2, "  naïf", color=GREY, fontsize=9, va="center")
    ax.axvline(BLACK_FRIDAY_WEEK, color=GREY, ls=":", lw=1)
    ax.set_ylim(0, 25)
    ax.set_ylabel("% des commandes livrées", color=GREY)
    style(ax, f"Rapporté aux ventes, le taux de retour reste autour de {before:.0%} : pas d'emballement",
          "Retours de la semaine ÷ moyenne des commandes livrées des 4 semaines précédentes")
    return df, save(fig, "level_2"), {
        "avg_rate_8_weeks_before_bf": round(before, 3), "max_rate_after_bf": round(peak, 3),
        "avg_rate_last_3_weeks": round(last, 3)}


def categories(o, t):
    df = r.cohort_rate(o, t, by="category", grain="M")
    piv = df.pivot(index="period", columns="category", values="return_rate")
    fig, ax = plt.subplots(figsize=(10, 5))
    for cat in piv.columns:
        color, lw = (RED, 2.5) if cat == "Chaussures" else (LIGHT_GREY, 1.5)
        ax.plot(piv.index, piv[cat] * 100, color=color, lw=lw, marker="o", ms=3)
        ax.text(piv.index[-1], piv[cat].iloc[-1] * 100, f"  {cat}", color=color if cat == "Chaussures" else GREY,
                fontsize=9, va="center")
    ax.set_ylabel("% retournées sous 28 jours", color=GREY)
    before = piv.loc[piv.index < "2025-10-01", "Chaussures"].mean()
    after = piv.loc[piv.index >= "2025-10-01", "Chaussures"].mean()
    style(ax, f"Chaussures : le taux de retour passe de {before:.0%} à {after:.0%} depuis octobre",
          "Part des commandes livrées retournées sous 28 jours, par mois d'achat (cohortes mûres)")
    reasons = t[(t["category"] == "Chaussures")].assign(
        period=lambda x: (x["order_date"] >= "2025-10-01").map({True: "since_oct", False: "before_oct"}))
    reasons = reasons.groupby("period")["reason"].value_counts(normalize=True).round(3).unstack(0)
    print("\nMotifs de retour Chaussures (part) :\n", reasons.to_string())
    return df, save(fig, "categories"), {
        "shoes_before_oct": round(before, 3), "shoes_since_oct": round(after, 3),
        **{f"{cat}_last_month": round(v, 3) for cat, v in piv.iloc[-1].items()}}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--level", type=int, choices=[0, 1, 2])
    p.add_argument("--categories", action="store_true")
    args = p.parse_args()
    if args.level is None and not args.categories:
        p.error("choisir --level 0|1|2 ou --categories")

    o, t = r.load()
    fn, name = (categories, "categories") if args.categories else (
        [level_0, level_1, level_2][args.level], f"level_{args.level}")
    df, chart, summary = fn(o, t)
    r.OUTPUTS.mkdir(exist_ok=True)
    df.to_csv(r.OUTPUTS / f"{name}.csv", index=False)
    print(f"\n=== {name.upper()} ===")
    for k, v in summary.items():
        print(f"  {k:<32} {v}")
    print(f"  tableau   → outputs/{name}.csv\n  graphique → {chart}")


if __name__ == "__main__":
    main()
