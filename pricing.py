"""Capacity shadow pricing and separate operator and tariff accounts."""

from __future__ import annotations

from typing import Dict, List

from wells import Well
from social_optimum import solve_social_optimum


def solve_capacity_pricing(
    wells: List[Well],
    q_max: float,
    p_oil: float = 70.0,
    c_gas: float = 5.0,
) -> Dict:
    """Posted shadow price; operators take the price as given."""
    social = solve_social_optimum(wells, q_max, p_oil, c_gas)
    tau = social["shadow_price"]

    decentralized_allocations = [
        w.standalone_demand(p_oil, c_gas, tau=tau) for w in wells
    ]
    operating_profits = [
        wells[i].profit(decentralized_allocations[i], p_oil, c_gas, tau=0.0)
        for i in range(len(wells))
    ]
    payments = [tau * q for q in decentralized_allocations]
    net_profits = [profit - payment for profit, payment in zip(operating_profits, payments)]
    return {
        "tariff": tau,
        "allocations": decentralized_allocations,
        "operating_profits": operating_profits,
        "net_profits": net_profits,
        "tariff_payments": payments,
        "tariff_revenue": float(sum(payments)),
        "total_net_profit": float(sum(net_profits)),
        "total_welfare": float(sum(operating_profits)),
        "total_gas": float(sum(decentralized_allocations)),
    }


if __name__ == "__main__":
    from pprint import pprint
    from wells import get_default_field

    pprint(solve_capacity_pricing(get_default_field(), q_max=1000.0))
