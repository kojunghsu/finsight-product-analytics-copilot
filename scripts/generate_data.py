import argparse

from finsight.synthetic import save_dataset

parser = argparse.ArgumentParser()
parser.add_argument("--rows", type=int, default=30_000)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--output", default="data/onboarding.csv")
args = parser.parse_args()
print(save_dataset(args.output, args.rows, args.seed))
