import math
import pytest
from wells import Well, generate_random_field, get_default_field, ration_allocations
from social_optimum import solve_social_optimum
from nash import solve_proportional_rationing_game
from pricing import solve_capacity_pricing
from shapley import solve_shapley_values
from results import compute_efficiency_ratio


def test_social_optimum_kkt():
    """1. Social Optimum satisfies KKT equi-marginal rule."""
    wells = get_default_field()
    q_max = 1000.0
    res = solve_social_optimum(wells, q_max)
    lam = res["shadow_price"]

    # At social optimum, every active well has the exact same marginal profit equal to shadow price
    for i, w in enumerate(wells):
        q_i = res["allocations"][i]
        assert math.isclose(w.marginal_profit(q_i), lam, rel_tol=1e-2)


def test_tragedy_of_the_commons():
    """2. Nash Equilibrium is strictly worse than Social Optimum (PoA > 1.0)."""
    wells = get_default_field()
    q_max = 1000.0
    social = solve_social_optimum(wells, q_max)
    nash = solve_proportional_rationing_game(wells, q_max)

    # Coordinated planner always beats selfish uncoordinated bidding
    assert social["total_profit"] > nash["total_profit"]
    assert compute_efficiency_ratio(wells, q_max) > 1.0


def test_pigouvian_pricing_recovers_optimum():
    """3. Pigouvian congestion tariff recovers 100% of Social Optimum welfare."""
    wells = get_default_field()
    q_max = 1000.0
    social = solve_social_optimum(wells, q_max)
    pricing = solve_capacity_pricing(wells, q_max)

    # When operators face tariff tau = lambda*, total welfare equals the social planner's profit
    assert math.isclose(pricing["total_welfare"], social["total_profit"], rel_tol=1e-3)


def test_shapley_axioms():
    """4. Shapley value satisfies Efficiency and Individual Rationality."""
    wells = get_default_field()
    q_max = 1000.0
    res = solve_shapley_values(wells, q_max)

    # Efficiency axiom: All profit is distributed (sum of shares equals grand coalition profit)
    assert math.isclose(sum(res["shapley_values"]), res["grand_coalition_profit"], rel_tol=1e-3)

    # Individual rationality: Every well earns strictly more than producing alone with its quota
    assert all(gain > 0 for gain in res["individual_gains"])