"""Compare the models, print the results and save the two plots."""

from __future__ import annotations

from pathlib import Path
from typing import List

import matplotlib
matplotlib.use("Agg")  # Save figures without opening a desktop window.
import matplotlib.pyplot as plt
import numpy as np

from wells import Well
from baseline import solve_rationing_baseline
from nash import solve_proportional_rationing_game
from social_optimum import solve_social_optimum
from pricing import solve_capacity_pricing
from shapley import solve_shapley_values


def compute_efficiency_ratio(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> float:
    """Social welfare / constructed equilibrium welfare, not worst-case PoA.

    With zero attainable welfare, use 1.0 (no welfare loss).
    """
    social = solve_social_optimum(wells, q_max, p_oil, c_gas)
    nash = solve_proportional_rationing_game(wells, q_max, p_oil, c_gas)
    return float(social["total_profit"] / nash["total_profit"]) if nash["total_profit"] else 1.0


def run_simulation(
    wells: List[Well],
    q_max: float = 1000.0,
    title_suffix: str = "",
    output_dir: Path | None = None,
) -> None:
    output_dir = output_dir or Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    well_names = [w.name for w in wells]
    n = len(wells)

    social = solve_social_optimum(wells, q_max)
    baseline = solve_rationing_baseline(wells, q_max)
    nash = solve_proportional_rationing_game(wells, q_max)
    pricing = solve_capacity_pricing(wells, q_max)
    shapley = solve_shapley_values(wells, q_max)
    ratio = compute_efficiency_ratio(wells, q_max)

    col_w = max(len(name) for name in well_names + ["TOTAL FIELD"]) + 2
    header = f"GAME-THEORETIC GAS LIFT SIMULATION ({n} Wells, Q_max = {q_max:.0f} Mscfd{title_suffix})"
    print("\n" + "=" * max(80, col_w + 65))
    print(f"   {header}")
    print("=" * max(80, col_w + 65))
    print(f"Equilibrium efficiency ratio: {ratio:.4f} (Welfare loss: {(1 - 1/ratio)*100:.2f}%)")
    print(f"Capacity tariff: ${pricing['tariff']:.2f}/Mscf")
    print(f"Standalone demand: {sum(baseline['nominations']):,.1f} Mscfd")
    print(f"Rationing baseline profit: ${baseline['total_profit']:,.2f}/day (honest nominations)")
    print(f"Strategic Nash profit:     ${nash['total_profit']:,.2f}/day (with bid inflation)")
    print("-" * max(80, col_w + 65))
    print(
        f"{'Well':<{col_w}} | {'Nash Bid':<9} | {'Nash Gas':<9} | {'Social Gas':<10} | "
        f"{'Nash Profit':<12} | {'Social Profit':<13} | {'Shapley Profit':<14}"
    )
    print("-" * max(80, col_w + 65))
    for i, name in enumerate(well_names):
        print(
            f"{name:<{col_w}} | {nash['nominations'][i]:>7.1f}   | {nash['allocations'][i]:>7.1f}   | "
            f"{social['allocations'][i]:>8.1f}   | ${nash['profits'][i]:>10,.0f} | "
            f"${social['profits'][i]:>11,.0f} | ${shapley['shapley_values'][i]:>12,.0f}"
        )
    print("-" * max(80, col_w + 65))
    print(
        f"{'TOTAL FIELD':<{col_w}} | {sum(nash['nominations']):>7.1f}   | {nash['total_gas']:>7.1f}   | "
        f"{social['total_gas']:>8.1f}   | ${nash['total_profit']:>10,.0f} | "
        f"${social['total_profit']:>11,.0f} | ${shapley['grand_coalition_profit']:>12,.0f}"
    )
    print("=" * max(80, col_w + 65) + "\n")

    print("CAPACITY PRICING ($/day; tariff recipient included in welfare)")
    for i, name in enumerate(well_names):
        print(f"{name}: operating ${pricing['operating_profits'][i]:,.2f}, "
              f"payment ${pricing['tariff_payments'][i]:,.2f}, net ${pricing['net_profits'][i]:,.2f}")
    print(f"Operator net total: ${pricing['total_net_profit']:,.2f}; "
          f"tariff revenue: ${pricing['tariff_revenue']:,.2f}; "
          f"welfare: ${pricing['total_welfare']:,.2f}\n")
    print("SHAPLEY PARTICIPATION ($/day; equal capacity entitlements)")
    for i, name in enumerate(well_names):
        share = shapley['shapley_values'][i]
        print(f"{name}: gain vs alone ${shapley['individual_gains'][i]:+,.2f}, "
              f"vs Nash ${share - nash['profits'][i]:+,.2f}, "
              f"vs baseline ${share - baseline['profits'][i]:+,.2f}")
    print(f"Shapley allocation in the core: {shapley['in_core']}")
    for coalition in shapley['blocking_coalitions']:
        print(f"Can gain by leaving together: {', '.join(coalition['members'])} "
              f"(${coalition['gain']:,.2f}/day)")

    # Plot 1: Regime Comparison
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(max(12, n * 2.8), 6))
    x = np.arange(n)
    width = 0.25

    ax1.bar(x - width, baseline["allocations"], width, label="Rationing baseline", color="#94a3b8")
    ax1.bar(x, nash["allocations"], width, label="Nash equilibrium", color="#ef4444")
    ax1.bar(x + width, social["allocations"], width, label="Social Optimum", color="#3b82f6")
    ax1.set_title(f"Gas allocation (capacity {q_max:.0f} Mscfd)", fontweight="bold")
    ax1.set_ylabel("Injected Gas (Mscfd)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(well_names, rotation=20 if n > 3 else 0, ha="right" if n > 3 else "center")
    ax1.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax1.legend()

    ax2.bar(x - width, nash["profits"], width, label="Nash Profit", color="#ef4444")
    ax2.bar(x, social["profits"], width, label="Social Profit (Raw)", color="#3b82f6")
    ax2.bar(x + width, shapley["shapley_values"], width, label="Shapley share", color="#10b981")
    ax2.set_title(
        f"Daily profits (social gain over Nash: ${(social['total_profit'] - nash['total_profit']):,.0f})",
        fontweight="bold",
    )
    ax2.set_ylabel("Operating Profit ($/day)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(well_names, rotation=20 if n > 3 else 0, ha="right" if n > 3 else "center")
    ax2.grid(True, linestyle="--", alpha=0.5, axis="y")
    ax2.legend()

    plt.tight_layout()
    plot_path1 = output_dir / "regime_comparison.png"
    plt.savefig(plot_path1, dpi=300)
    plt.close()

    # Plot 2: Compare one constructed equilibrium with the non-strategic baseline.
    total_demand = sum(baseline["nominations"])
    capacities = np.linspace(max(1.0, total_demand) * 0.2, max(1.0, total_demand) * 1.2, 50)
    ratios = [compute_efficiency_ratio(wells, q) for q in capacities]
    baseline_ratios = []
    for q in capacities:
        welfare = solve_social_optimum(wells, q)["total_profit"]
        baseline_profit = solve_rationing_baseline(wells, q)["total_profit"]
        baseline_ratios.append(welfare / baseline_profit if baseline_profit else 1.0)

    fig, ax_poa = plt.subplots(figsize=(9, 5))
    ax_poa.plot(capacities, ratios, color="#b91c1c", linewidth=2.5, label="Social / Nash equilibrium")
    ax_poa.plot(capacities, baseline_ratios, color="#64748b", linestyle="--", label="Social / rationing baseline")
    ax_poa.axhline(1.0, color="gray", linestyle=":", label="Efficient allocation (ratio = 1)")
    ax_poa.axvline(
        total_demand,
        color="#2563eb",
        linestyle="--",
        label=f"Total Demand ({total_demand:,.0f} Mscfd)",
    )
    ax_poa.set_title(f"Efficiency vs. compressor capacity ({n} wells)", fontweight="bold", fontsize=12)
    ax_poa.set_xlabel("Compressor Capacity $Q_{max}$ (Mscfd)", fontsize=11)
    ax_poa.set_ylabel("Social welfare / comparison welfare", fontsize=11)
    ax_poa.grid(True, linestyle="--", alpha=0.6)
    ax_poa.legend(loc="upper right", framealpha=0.9)

    plt.tight_layout()
    plot_path2 = output_dir / "efficiency_ratio_curve.png"
    plt.savefig(plot_path2, dpi=300)
    plt.close()

    print(f"Generated plots saved to:\n  - {plot_path1}\n  - {plot_path2}\n")
