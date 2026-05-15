# Lesson 7 — Web Pong with optional RL agent

A canvas **Pong** game (Vite + TypeScript) plus an offline **PPO** training pipeline (Gymnasium + Stable-Baselines3). The trained policy is exported to `public/policy.json` and runs in the browser with a small MLP forward pass (no TensorFlow.js).

## Run the game

```bash
npm install
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`). Use **arrow keys** or **W/S** for the left paddle; **Space** pauses. Toggle **RL agent** to steer the right paddle with the learned policy (falls back to the heuristic if `policy.json` is missing).

## Train the policy

Use Python **3.10+** (recommended).

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python rl/train.py --out public/policy.json --timesteps 400000
```

- Reduce `--timesteps` for a quick smoke test (e.g. `50000`); quality improves with more steps (default `400000`).
- Restart or refresh the dev server after regenerating `policy.json`.

## Keep physics in sync

These must match between the web game and the env:

| Quantity | TypeScript | Python (`rl/pong_env.py`) |
|---------|------------|---------------------------|
| Court size | [`src/game/constants.ts`](src/game/constants.ts) `COURT_WIDTH`, `COURT_HEIGHT` | `PHYSICS["COURT_WIDTH"]`, `PHYSICS["COURT_HEIGHT"]` |
| Paddle / ball | `PADDLE_*`, `BALL_RADIUS`, `PADDLE_MARGIN` | same keys in `PHYSICS` |
| Speeds | `PADDLE_SPEED`, `BALL_BASE_SPEED`, `BALL_SPEED_MULT`, `V_MAX` | same |
| Win score | `WIN_SCORE` | `PHYSICS["WIN_SCORE"]` |
| Observation dim | `OBS_DIM` | `OBS_DIM` in `pong_env.py` |

The observation vector and normalization are mirrored in `buildObservation()` (TypeScript) and `_build_observation()` (Python).

## Layout

- `src/game/` — constants, physics, rendering
- `src/rl/policy.ts` — loads `policy.json`, ReLU MLP, argmax action
- `rl/pong_env.py` — Gymnasium environment
- `rl/train.py` — PPO training + export

## Build for production

```bash
npm run build
npm run preview
```
