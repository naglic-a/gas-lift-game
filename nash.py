"""Strategic Nash Equilibrium under Proportional Capacity Rationing.

Operators pay only for delivered gas, and requests are bounded by max_gas.
At equilibrium, each operator either receives its preferred quantity or
requests its limit and cannot obtain more. Always requesting the limit is
not optimal: gas beyond the preferred quantity reduces profit.
"""

from __future__ import annotations

from typing import Dict, List
from wells import Well, allocation_result, ration_allocations, validate_inputs


def solve_proportional_rationing_game(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> Dict:
    """Computes the Strategic Nash Equilibrium under proportional rationing."""
    validate_inputs(wells, q_max, p_oil, c_gas)
    demands = [w.standalone_demand(p_oil, c_gas) for w in wells]

    if q_max == 0:
        nominations = [0.0] * len(wells)
    elif sum(demands) <= q_max:
        nominations = demands
    else:
        # sum(min(preferred gas, s * request limit)) = compressor capacity.
        # Too much delivered gas -> lower s; too little -> raise s.
        low, high = 0.0, 1.0
        for _ in range(100):
            delivery_scale = (low + high) / 2.0
            total = sum(min(d, delivery_scale * w.max_gas)
                        for w, d in zip(wells, demands))
            if total < q_max:
                low = delivery_scale
            else:
                high = delivery_scale

        delivery_scale = high
        nominations = [min(w.max_gas, d / delivery_scale)
                       for w, d in zip(wells, demands)]

    allocations = ration_allocations(nominations, q_max)
    result = allocation_result(wells, allocations, p_oil, c_gas)
    result["nominations"] = nominations

    # Hold everyone else's requests fixed. Delivery increases with own request,
    # so the best reachable delivery is preferred gas, or the reachable maximum.
    for i, w in enumerate(wells):
        others = sum(r for j, r in enumerate(nominations) if j != i)
        total_at_limit = others + w.max_gas
        reachable = (w.max_gas * min(1.0, q_max / total_at_limit)
                     if total_at_limit else 0.0)
        best_profit = w.profit(min(demands[i], reachable), p_oil, c_gas)
        tolerance = 1e-8 * max(1.0, abs(best_profit))
        if best_profit - result["profits"][i] > tolerance:
            raise RuntimeError("Nash check failed: a well can profitably deviate.")
    return result


if __name__ == "__main__":
    from pprint import pprint
    from wells import get_default_field

    pprint(solve_proportional_rationing_game(get_default_field(), q_max=1000.0))
