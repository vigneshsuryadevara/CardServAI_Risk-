from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from cardserv_ai.data import generate_contacts, evaluation_cases, challenge_cases

def main():
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    contacts = generate_contacts(n=5000, seed=17, days=180)
    evals = evaluation_cases(n_per_intent=32, seed=23)
    holdout = challenge_cases()
    contacts.to_csv(data_dir / "synthetic_contacts.csv", index=False)
    evals.to_csv(data_dir / "evaluation_cases.csv", index=False)
    holdout.to_csv(data_dir / "challenge_cases.csv", index=False)
    print(f"Wrote {len(contacts):,} synthetic contacts to data/synthetic_contacts.csv")
    print(f"Wrote {len(evals):,} core evaluation cases to data/evaluation_cases.csv")
    print(f"Wrote {len(holdout):,} holdout challenge cases to data/challenge_cases.csv")

if __name__ == "__main__":
    main()
