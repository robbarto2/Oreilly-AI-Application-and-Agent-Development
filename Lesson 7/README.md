# Lesson 7 — Web Pong with optional RL agent

A canvas **Pong** game (Vite + TypeScript) plus an offline **PPO** training pipeline (Gymnasium + Stable-Baselines3). The trained policy is exported to `public/policy.json` and runs in the browser with a small MLP forward pass (no TensorFlow.js).

## Run the game from here

```bash
npm install
npm run dev
```


Open the URL Vite prints (usually `http://localhost:5173`). Use **arrow keys** or **W/S** for the left paddle; **Space** pauses. Toggle **RL agent** to steer the right paddle with the learned policy (falls back to the heuristic if `policy.json` is missing).

## Train the policy

Use Python **3.10+** (recommended). Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once (curl snippet or package manager).

```bash
uv sync
uv run python rl/train.py --out public/policy.json --timesteps 400000
```

`uv sync` creates or refreshes `.venv/` from [`uv.lock`](uv.lock). Activating the venv is optional; `uv run` uses it automatically.

**Without uv:** `python3 -m venv .venv`, activate it, then `pip install -r requirements.txt` and `python rl/train.py …` ([`requirements.txt`](requirements.txt) is exported from the lockfile).

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

### Ball speed slider (browser only)

The **Ball speed** control scales serve speed, the post-hit velocity cap, and the live ball (when you move the slider). It is **not** part of the Python environment; the pretrained policy assumes **100%**. At other speeds, RL play may look weaker.

### Paddle size (browser only)

**Paddle size** scales **your** (left) paddle height (default **80px** at 100%); the opponent paddle stays at the training default. Same caveats as ball speed: **not** in `pong_env.py`; RL was trained at **100%**.

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

## Python environment

Deps live in [`pyproject.toml`](pyproject.toml); the resolved set is pinned in **`uv.lock`** (commit both). [`requirements.txt`](requirements.txt) is generated for pip-only workflows; refresh it after dependency changes:

```bash
uv export --format requirements.txt -o requirements.txt --no-hashes --no-annotate
```

Historical migration checklist: [docs/UV_MIGRATION_PLAN.md](docs/UV_MIGRATION_PLAN.md).
