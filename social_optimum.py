"""Centralized allocation that maximizes total operating profit."""

from __future__ import annotations

from typing import Dict, List

from wells import Well, allocation_result, validate_inputs


def solve_social_optimum(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> Dict:
    """Find the capacity shadow price by bisection on bounded gas demand."""
    validate_inputs(wells, q_max, p_oil, c_gas)
    standalone = [w.standalone_demand(p_oil, c_gas) for w in wells]
    if sum(standalone) <= q_max: # supply > demand
        q_opt = standalone
        lambda_star = 0.0
    else:
        low = 0.0
        high = max(w.a * w.b * p_oil for w in wells)
        for _ in range(100):
            price = (low + high) / 2
            demand = sum(w.standalone_demand(p_oil, c_gas, price) for w in wells)
            if demand > q_max:
                low = price
            else:
                high = price
        lambda_star = high
        q_opt = [w.standalone_demand(p_oil, c_gas, high) for w in wells]
        if abs(sum(q_opt) - q_max) > 1e-7 * max(1.0, q_max):
            raise RuntimeError("Capacity price did not clear the market.")
    result = allocation_result(wells, q_opt, p_oil, c_gas)
    result["shadow_price"] = lambda_star
    return result


if __name__ == "__main__":
    from pprint import pprint
    from wells import get_default_field

    pprint(solve_social_optimum(get_default_field(), q_max=1000.0))
