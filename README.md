# Gas Allocation
This applied game theory project studies how gas is allocated between oil wells that share a compressor. Gas injection increases oil production, but compressor capacity is limited. Wells have different production characteristics, so the same amount of gas does not generate the same profit at every well.

The project examines how individual operators' decisions affect the overall outcome and what changes when allocation is coordinated. The simulation connects two questions: how to allocate gas to maximize total profit, and how to share that profit among the participants.

## What the Simulation Compares

**Proportional Allocation (Baseline)** provides the starting point. Each well requests the amount of gas that would maximize its profit without the shared capacity constraint. If total requests exceed compressor capacity, every well receives the same proportion of its requested amount.

**Nash Equilibrium** describes operators choosing their requests based on their own profits and the requests of others. A larger request can secure a greater share of capacity, but more gas is not always profitable. The simulation finds requests at which no operator can increase its profit by changing only its own request.

**Social Optimum** finds the allocation that maximizes the combined profit of all wells. Gas is directed where it provides greater marginal benefit, so some wells may receive more and others less than when operators act independently. This outcome serves as a benchmark for comparing the efficiency of other allocations.

**Shadow Pricing** introduces an additional charge for gas to align individual decisions with the social optimum. The charge is set so that each operator, choosing its most profitable consumption at that price, selects the quantity in the optimal allocation. This achieves the same allocation through the price of using capacity.

**Shapley Allocation** considers how profit is shared when operators cooperate. Each participant contributes its well and an equal share of compressor capacity, which coalition members can use jointly. A player's share of profit is determined by its average marginal contribution across all possible joining orders. The simulation also checks whether any group of participants could earn more by leaving the coalition.

Comparing these outcomes illustrates the difference between maximizing individual profit, maximizing total profit, and sharing joint earnings. The model uses known production characteristics and fixed prices to examine these differences in a simple setting.

## Running the Project

```sh
uv run simulation.py
```

If uv is unavailable, the required dependencies are listed in `requirements.txt`.
