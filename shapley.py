"""Cooperative profit sharing with participation and coalition stability checks."""

from __future__ import annotations

import itertools
import math
from typing import Dict, List, Tuple

from wells import Well, validate_inputs
from social_optimum import solve_social_optimum


def solve_shapley_values(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> Dict:
    """Share cooperative profit when each operator brings an equal capacity quota."""
    validate_inputs(wells, q_max, p_oil, c_gas)
    n = len(wells)
    if n > 10:
        raise ValueError("Exact Shapley calculation is limited to 10 wells for this demo.")
    quota_per_well = q_max / n
    v: Dict[Tuple[int, ...], float] = {}

    # 1. Calculate each coalition's profit using its members' combined quotas.
    for k in range(n + 1):
        for subset in itertools.combinations(range(n), k):
            if not subset:
                v[subset] = 0.0
            else:
                sub_wells = [wells[i] for i in subset]
                cap_s = len(subset) * quota_per_well
                res = solve_social_optimum(sub_wells, cap_s, p_oil, c_gas)
                v[subset] = res["total_profit"]

    # 2. Average each player's marginal contributions using Shapley weights.
    shapley = [0.0] * n
    for i in range(n):
        other_players = [j for j in range(n) if j != i]
        for k in range(n):
            for subset in itertools.combinations(other_players, k):
                weight = (
                    math.factorial(k)
                    * math.factorial(n - k - 1)
                    / math.factorial(n)
                )
                with_i = tuple(sorted(subset + (i,)))
                shapley[i] += weight * (v[with_i] - v[subset])

    # 3. Check whether any coalition could earn more by leaving together.
    defection_margins = {}
    for k in range(1, n):
        for subset in itertools.combinations(range(n), k):
            defection_margins[str(subset)] = sum(shapley[i] for i in subset) - v[subset]

    return {
        "characteristic_function": {str(k): val for k, val in v.items()},
        "shapley_values": shapley,
        "grand_coalition_profit": v[tuple(range(n))],
        "defection_margins": defection_margins,
        "singleton_values": [v[(i,)] for i in range(n)],
        "individual_gains": [shapley[i] - v[(i,)] for i in range(n)],
        "in_core": all(m >= -1e-6 for m in defection_margins.values()),
        "blocking_coalitions": [
            {"members": [wells[i].name for i in subset],
             "gain": v[subset] - sum(shapley[i] for i in subset)}
            for subset in v if 0 < len(subset) < n
            and v[subset] - sum(shapley[i] for i in subset) > 1e-6
        ],
    }


if __name__ == "__main__":
    from pprint import pprint
    from wells import get_default_field

    pprint(solve_shapley_values(get_default_field(), q_max=1000.0))
