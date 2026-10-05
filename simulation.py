"""Run all models and compare their results."""
import argparse
import math

from wells import generate_random_field, get_4_well_field, get_default_field
from results import run_simulation


def main():
    parser = argparse.ArgumentParser(description="Run Shared Gas Lift Game Theory Simulation")
    parser.add_argument("--wells", type=int, default=3, help="Number of wells (default: 3)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for stochastic wells (e.g. 42)")
    parser.add_argument("--capacity", type=float, default=1000.0, help="Compressor capacity Q_max (Mscfd)")
    args = parser.parse_args()

    if not 1 <= args.wells <= 10:
        parser.error("Choose 1 to 10 wells (exact Shapley calculation).")
    if not math.isfinite(args.capacity) or args.capacity < 0:
        parser.error("Capacity must be finite and nonnegative.")
    if args.seed is not None and args.seed < 0:
        parser.error("Seed must be nonnegative.")
    if args.seed is None and args.wells not in (3, 4):
        parser.error("Fixed presets have 3 or 4 wells. Add --seed for other counts.")

    if args.seed is not None:
        wells = generate_random_field(n_wells=args.wells, seed=args.seed)
        suffix = f", Seed={args.seed}"
    elif args.wells == 4:
        wells = get_4_well_field()
        suffix = " [Fixed 4-Well Preset]"
    else:
        wells = get_default_field()
        suffix = " [Fixed 3-Well Preset]"

    run_simulation(wells, q_max=args.capacity, title_suffix=suffix)


if __name__ == "__main__":
    main()
