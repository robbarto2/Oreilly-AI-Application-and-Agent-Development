"""Train PPO on Lesson 7 Pong and export an MLP policy for the web app."""

from __future__ import annotations

import argparse
import json
import os
import sys

from stable_baselines3 import PPO

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, SCRIPT_DIR)

from pong_env import OBS_DIM, PongEnv  # noqa: E402


def export_policy_mlp(model: PPO, path: str) -> None:
    sd = model.policy.state_dict()
    layers: list[dict[str, object]] = []
    for i in (0, 2):
        w = sd[f"mlp_extractor.policy_net.{i}.weight"].detach().cpu().numpy()
        b = sd[f"mlp_extractor.policy_net.{i}.bias"].detach().cpu().numpy()
        layers.append({"weight": w.tolist(), "bias": b.tolist()})
    w = sd["action_net.weight"].detach().cpu().numpy()
    b = sd["action_net.bias"].detach().cpu().numpy()
    layers.append({"weight": w.tolist(), "bias": b.tolist()})

    artifact = {
        "version": 1,
        "obs_dim": OBS_DIM,
        "n_actions": int(model.action_space.n),
        "layers": layers,
    }
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(artifact, f)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Train PPO and write policy.json for the Vite app.",
    )
    parser.add_argument(
        "--out",
        default=os.path.join(ROOT_DIR, "public", "policy.json"),
        help="Output JSON path (default: ../public/policy.json)",
    )
    parser.add_argument(
        "--timesteps",
        type=int,
        default=400_000,
        help="PPO total_timesteps (reduce for quick smoke tests).",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    env = PongEnv(seed=args.seed)
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        seed=args.seed,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        policy_kwargs={"net_arch": [64, 64]},
    )
    model.learn(total_timesteps=args.timesteps)
    export_policy_mlp(model, args.out)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
