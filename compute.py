import argparse
from aiyagari import core

def main():
    parser = argparse.ArgumentParser(description="Run computations for the Aiyagari (1994) model.")
    parser.add_argument(
        '--mode',
        type=str,
        choices=['baseline', 'full'],
        required=True,
        help="Execution mode: 'baseline' for a quick test, 'full' for the complete replication."
    )
    args = parser.parse_args()

    if args.mode == 'baseline':
        core.run_baseline_simulation()
    elif args.mode == 'full':
        core.run_full_replication()

if __name__ == "__main__":
    main() 