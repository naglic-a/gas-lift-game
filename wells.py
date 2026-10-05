"""Shared well economics, example fields and allocation helpers."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class Well:
    name: str
    a: float  # Maximum oil potential
    b: float  # Inverse gas-rate units, so b*q is dimensionless
    max_gas: float = 1200.0  # Physical gas injection limit (Mscfd)

    def __post_init__(self):
        if not all(math.isfinite(x) and x > 0 for x in (self.a, self.b)):
            raise ValueError("Well a and b must be finite and positive.")
        if not math.isfinite(self.max_gas) or self.max_gas < 0:
            raise ValueError("Well gas limit must be finite and nonnegative.")

    def oil_production(self, q: float) -> float:
        """Oil production: q_o(q) = a * (1 - exp(-b * q))."""
        q_clean = max(0.0, float(q))
        return float(self.a * (1.0 - math.exp(-self.b * q_clean)))

    def marginal_oil_production(self, q: float) -> float:
        """First derivative: dq_o / dq = a * b * exp(-b * q)."""
        q_clean = max(0.0, float(q))
        return float(self.a * self.b * math.exp(-self.b * q_clean))

    def profit(
        self, q: float, p_oil: float = 70.0, c_gas: float = 5.0, tau: float = 0.0
    ) -> float:
        """Daily operating profit: Pi = P_oil * q_o(q) - (C_gas + tau) * q."""
        q_clean = max(0.0, float(q))
        return float(
            p_oil * self.oil_production(q_clean) - (c_gas + tau) * q_clean
        )

    def marginal_profit(
        self, q: float, p_oil: float = 70.0, c_gas: float = 5.0, tau: float = 0.0
    ) -> float:
        """Marginal profit: dPi / dq = P_oil * a * b * exp(-b * q) - (C_gas + tau)."""
        q_clean = max(0.0, float(q))
        return float(
            p_oil * self.marginal_oil_production(q_clean) - (c_gas + tau)
        )

    def standalone_demand(
        self, p_oil: float = 70.0, c_gas: float = 5.0, tau: float = 0.0
    ) -> float:
        """Unconstrained profit-maximizing gas nomination r_i* where dPi/dq = 0."""
        effective_cost = c_gas + tau
        if not math.isfinite(effective_cost) or effective_cost <= 0:
            raise ValueError("Effective gas cost must be finite and positive.")
        if self.a * self.b * p_oil <= effective_cost:
            return 0.0
        q_star = (1.0 / self.b) * math.log((p_oil * self.a * self.b) / effective_cost)
        return float(min(self.max_gas, max(0.0, q_star)))

# -----
def get_default_field() -> List[Well]:
    """Returns 3 canonical benchmark wells (High, Medium, and Low PI)."""
    return [
        Well(name="Well 1 (High PI)", a=500.0, b=0.005),
        Well(name="Well 2 (Medium PI)", a=300.0, b=0.004),
        Well(name="Well 3 (Low PI)", a=150.0, b=0.003),
    ]


def get_4_well_field() -> List[Well]:
    """Returns 4 benchmark wells illustrating scaling up."""
    return [
        Well(name="Well 1 (Super-Producer)", a=650.0, b=0.006),
        Well(name="Well 2 (High PI)", a=450.0, b=0.005),
        Well(name="Well 3 (Medium PI)", a=280.0, b=0.0035),
        Well(name="Well 4 (Marginal)", a=140.0, b=0.0025),
    ]


def generate_random_field(
    n_wells: int = 4,
    seed: int | None = 42,
    a_range: Tuple[float, float] = (150.0, 700.0),
    b_range: Tuple[float, float] = (0.0025, 0.0065),
) -> List[Well]:
    """
    Generates n_wells with stochastic parameters using a reproducible seed.
    Wells are sorted descending by Productivity Index (PI = a * b)
    """
    if n_wells < 1:
        raise ValueError("Number of wells must be a positive integer.")
    rng = np.random.default_rng(seed)
    a_vals = rng.uniform(a_range[0], a_range[1], n_wells)
    b_vals = rng.uniform(b_range[0], b_range[1], n_wells)
    pi_vals = a_vals * b_vals
    sorted_order = np.argsort(-pi_vals)

    wells = []
    for rank, idx in enumerate(sorted_order, start=1):
        wells.append(
            Well(
                name=f"Well {rank} (PI={pi_vals[idx]:.2f})",
                a=round(float(a_vals[idx]), 1),
                b=round(float(b_vals[idx]), 4),
            )
        )
    return sorted(wells, key=lambda w: w.a * w.b, reverse=True)


def validate_inputs(wells, q_max, p_oil=70.0, c_gas=5.0):
    if not wells:
        raise ValueError("Provide at least one well.")
    if not math.isfinite(q_max) or q_max < 0:
        raise ValueError("Capacity must be finite and nonnegative.")
    if not all(math.isfinite(x) and x > 0 for x in (p_oil, c_gas)):
        raise ValueError("Oil price and gas cost must be finite and positive.")


def ration_allocations(nominations, q_max):
    """Requests up to each well's max_gas; gas is charged only when delivered."""
    total = sum(nominations)
    scale = min(1.0, q_max / total) if total else 0.0
    return [r * scale for r in nominations]


def allocation_result(wells, allocations, p_oil, c_gas):
    profits = [w.profit(q, p_oil, c_gas) for w, q in zip(wells, allocations)]
    return {"allocations": allocations, "profits": profits,
            "total_profit": float(sum(profits)), "total_gas": float(sum(allocations))}
