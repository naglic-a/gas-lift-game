"""Standalone demand followed by proportional rationing, without strategic bidding."""

from __future__ import annotations

from typing import Dict, List

from wells import Well, allocation_result, ration_allocations, validate_inputs


def solve_rationing_baseline(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> Dict:
    """Non-strategic baseline"""
    validate_inputs(wells, q_max, p_oil, c_gas)
    nominations = [w.standalone_demand(p_oil, c_gas) for w in wells]
    result = allocation_result(wells, ration_allocations(nominations, q_max), p_oil, c_gas)
    result["nominations"] = nominations
    return result


if __name__ == "__main__":
    from pprint import pprint
    from wells import get_default_field

    pprint(solve_rationing_baseline(get_default_field(), q_max=1000.0))
