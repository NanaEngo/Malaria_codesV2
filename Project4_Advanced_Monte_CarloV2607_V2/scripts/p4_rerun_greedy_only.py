#!/usr/bin/env python3
"""Re-run Greedy baseline with best-intermediate tracking for 20 seeds."""
import sys
import csv
import time
import copy
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from p4_mcts_rl_env import MolecularEnv
from p4_mcts_baselines import compute_mpo_reward

def run_greedy_one_seed(seed, max_steps=10, fragment_set="medium"):
    """Run Greedy for one seed, returning best intermediate."""
    env = MolecularEnv(
        initial_smiles="c1ccccc1",  # benzene start
        max_steps=max_steps,
        seed=seed
    )
    
    if fragment_set == "medium":
        env.fragment_vocab = [f for f in env.fragment_vocab if f not in ["[C]", "[N]", "[O]"]][:37]
    
    oracle = compute_mpo_reward
    vocab = list(env.fragment_vocab)
    state = env.state
    best_reward, best_smiles = oracle(state), state
    t0 = time.perf_counter()
    
    for step in range(max_steps):
        best_r, best_a = -1.0, None
        for a in vocab:
            env_copy = copy.deepcopy(env)
            env_copy.state = state
            env_copy.step_count = step
            next_s, _, _, _ = env_copy.step(a)
            r = oracle(next_s)
            if r > best_r:
                best_r, best_a = r, a
        
        if best_a:
            state, _, done, _ = env.step(best_a)
            r = oracle(state)
            if r > best_reward:
                best_reward, best_smiles = r, state
            if done:
                break
    
    elapsed = time.perf_counter() - t0
    return best_smiles, best_reward, elapsed

def main():
    output_dir = Path("../results/benchmark_greedy_fixed_v12")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    print("Re-running Greedy with best-intermediate tracking for 20 seeds...")
    
    for seed in range(20):
        smiles, reward, elapsed = run_greedy_one_seed(seed)
        results.append({
            "method": "greedy",
            "seed": seed,
            "reward": reward,
            "elapsed_s": f"{elapsed:.2f}"
        })
        print(f"  Seed {seed:2d}: reward={reward:.6f} time={elapsed:.2f}s")
    
    # Write CSV
    csv_path = output_dir / "p4_benchmark_greedy_fixed.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["method", "seed", "reward", "elapsed_s"])
        writer.writeheader()
        writer.writerows(results)
    
    # Compute statistics
    rewards = [float(r["reward"]) for r in results]
    mean_reward = sum(rewards) / len(rewards)
    std_reward = (sum((r - mean_reward)**2 for r in rewards) / len(rewards))**0.5
    min_reward = min(rewards)
    max_reward = max(rewards)
    mean_time = sum(float(r["elapsed_s"]) for r in results) / len(results)
    
    print(f"\n=== Greedy Statistics (fixed, best-intermediate) ===")
    print(f"  Mean reward: {mean_reward:.4f} ± {std_reward:.4f}")
    print(f"  Min: {min_reward:.4f}, Max: {max_reward:.4f}")
    print(f"  Mean time: {mean_time:.1f}s")
    print(f"  Output: {csv_path}")

if __name__ == "__main__":
    main()
