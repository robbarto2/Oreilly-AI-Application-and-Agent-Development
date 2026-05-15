"""
Gymnasium Pong environment — physics must match `src/game/constants.ts` and
`src/game/engine.ts` (same numeric constants and step order).
"""

from __future__ import annotations

import math
from typing import Any, SupportsFloat

import gymnasium as gym
import numpy as np
from gymnasium import spaces


PHYSICS: dict[str, float] = {
    "COURT_WIDTH": 960,
    "COURT_HEIGHT": 540,
    "PADDLE_WIDTH": 12,
    "PADDLE_HEIGHT": 80,
    "BALL_RADIUS": 6,
    "PADDLE_MARGIN": 24,
    "PADDLE_SPEED": 420,
    "BALL_BASE_SPEED": 320,
    "BALL_SPEED_MULT": 1.06,
    "WIN_SCORE": 5,
    "V_MAX": 550,
}

OBS_DIM = 8
RIGHT_PADDLE_X_CENTER = (
    PHYSICS["COURT_WIDTH"] - PHYSICS["PADDLE_MARGIN"] - PHYSICS["PADDLE_WIDTH"] / 2
)


def _clamp(n: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, n))


def _paddle_y_bounds() -> tuple[float, float]:
    ph = PHYSICS["PADDLE_HEIGHT"]
    h = PHYSICS["COURT_HEIGHT"]
    return ph / 2, h - ph / 2


def _serve_ball(seed: int, toward_right: bool) -> tuple[float, float, float, float]:
    rng = np.random.default_rng(int(seed) & 0xFFFFFFFF)
    theta = (rng.random() * 0.8 - 0.4) * math.pi
    vx = math.cos(theta) * PHYSICS["BALL_BASE_SPEED"]
    vy = math.sin(theta) * PHYSICS["BALL_BASE_SPEED"]
    if toward_right:
        vx = abs(vx)
    else:
        vx = -abs(vx)
    if rng.random() > 0.5:
        vy = -vy
    cx, cy = PHYSICS["COURT_WIDTH"] / 2, PHYSICS["COURT_HEIGHT"] / 2
    return cx, cy, float(vx), float(vy)


def _heuristic_paddle(py: float, ball_y: float, dt: float) -> float:
    lo, hi = _paddle_y_bounds()
    dy = ball_y - py
    max_step = PHYSICS["PADDLE_SPEED"] * dt
    if abs(dy) <= max_step:
        return float(_clamp(ball_y, lo, hi))
    return float(_clamp(py + math.copysign(max_step, dy), lo, hi))


def _rect_ball_overlap(
    bx: float, by: float, px_center: float, py_center: float
) -> bool:
    pw, ph = PHYSICS["PADDLE_WIDTH"], PHYSICS["PADDLE_HEIGHT"]
    br = PHYSICS["BALL_RADIUS"]
    px0 = px_center - pw / 2
    px1 = px_center + pw / 2
    py0 = py_center - ph / 2
    py1 = py_center + ph / 2
    return (
        bx - br < px1 and bx + br > px0 and by - br < py1 and by + br > py0
    )


def _bounce_paddle(
    ball_vx: float, ball_vy: float, py_center: float, ball_y: float
) -> tuple[float, float]:
    vx = -ball_vx * PHYSICS["BALL_SPEED_MULT"]
    offset = (ball_y - py_center) / (PHYSICS["PADDLE_HEIGHT"] / 2)
    kick = offset * 0.35 * abs(vx)
    vy = ball_vy + kick
    cap = PHYSICS["V_MAX"]
    sp = math.hypot(vx, vy)
    if sp > cap:
        vx *= cap / sp
        vy *= cap / sp
    return vx, vy


def _norm_ball_x(x: float) -> float:
    return (x / PHYSICS["COURT_WIDTH"]) * 2 - 1


def _norm_ball_y(y: float) -> float:
    return (y / PHYSICS["COURT_HEIGHT"]) * 2 - 1


def _norm_paddle_y(py: float) -> float:
    lo, hi = _paddle_y_bounds()
    return ((py - lo) / (hi - lo)) * 2 - 1


def _build_observation(
    bx: float,
    by: float,
    bvx: float,
    bvy: float,
    left_y: float,
    right_y: float,
) -> np.ndarray:
    obs = np.zeros((OBS_DIM,), dtype=np.float32)
    obs[0] = _norm_ball_x(bx)
    obs[1] = _norm_ball_y(by)
    obs[2] = _clamp(bvx / PHYSICS["V_MAX"], -1, 1)
    obs[3] = _clamp(bvy / PHYSICS["V_MAX"], -1, 1)
    obs[4] = _norm_paddle_y(left_y)
    obs[5] = _norm_paddle_y(right_y)
    obs[6] = _clamp((by - right_y) / (PHYSICS["COURT_HEIGHT"] / 2), -1, 1)
    obs[7] = _clamp(
        (bx - RIGHT_PADDLE_X_CENTER) / (PHYSICS["COURT_WIDTH"] / 2), -1, 1
    )
    return obs


class PongEnv(gym.Env[np.ndarray, int]):
    metadata = {"render_modes": []}

    def __init__(self, max_episode_steps: int = 10000, seed: int | None = None):
        super().__init__()
        self._rng_counter = int(seed) if seed is not None else 1
        self.observation_space = spaces.Box(
            low=-1.0, high=1.0, shape=(OBS_DIM,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)
        self.max_episode_steps = max_episode_steps
        self._step_count = 0

        self.ball_x = 0.0
        self.ball_y = 0.0
        self.ball_vx = 0.0
        self.ball_vy = 0.0
        self.left_y = PHYSICS["COURT_HEIGHT"] / 2
        self.right_y = PHYSICS["COURT_HEIGHT"] / 2
        self.score_left = 0
        self.score_right = 0
        self.rally = 0

    def _serve(self, toward_right: bool) -> None:
        self._rng_counter += 1
        self.ball_x, self.ball_y, self.ball_vx, self.ball_vy = _serve_ball(
            self._rng_counter * 7919, toward_right
        )

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        super().reset(seed=seed)
        if seed is not None:
            self._rng_counter = int(seed)
        self._step_count = 0
        self.score_left = 0
        self.score_right = 0
        self.left_y = PHYSICS["COURT_HEIGHT"] / 2
        self.right_y = PHYSICS["COURT_HEIGHT"] / 2
        self.rally = 0
        rng = np.random.default_rng(int(self._rng_counter * 7919) & 0xFFFFFFFF)
        self._serve(bool(rng.random() > 0.5))
        return self._get_obs(), {}

    def _get_obs(self) -> np.ndarray:
        return _build_observation(
            self.ball_x,
            self.ball_y,
            self.ball_vx,
            self.ball_vy,
            self.left_y,
            self.right_y,
        )

    def step(
        self, action: SupportsFloat
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        a = int(action)
        dt = 1.0 / 60.0
        self._step_count += 1

        self.left_y = _heuristic_paddle(self.left_y, self.ball_y, dt)

        up, down = a == 0, a == 2
        lo, hi = _paddle_y_bounds()
        vel = 0.0
        if up:
            vel -= PHYSICS["PADDLE_SPEED"]
        if down:
            vel += PHYSICS["PADDLE_SPEED"]
        self.right_y = float(_clamp(self.right_y + vel * dt, lo, hi))

        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt

        br = PHYSICS["BALL_RADIUS"]
        h = PHYSICS["COURT_HEIGHT"]
        if self.ball_y - br <= 0:
            self.ball_y = br
            self.ball_vy = abs(self.ball_vy)
        elif self.ball_y + br >= h:
            self.ball_y = h - br
            self.ball_vy = -abs(self.ball_vy)

        pm = PHYSICS["PADDLE_MARGIN"]
        pw = PHYSICS["PADDLE_WIDTH"]
        left_cx = pm + pw / 2

        reward = 0.0
        terminated = False
        truncated = False

        if self.ball_vx < 0 and _rect_ball_overlap(
            self.ball_x, self.ball_y, left_cx, self.left_y
        ):
            self.ball_vx, self.ball_vy = _bounce_paddle(
                self.ball_vx, self.ball_vy, self.left_y, self.ball_y
            )
            self.ball_x = left_cx + pw / 2 + br + 0.01
            self.rally += 1
        elif self.ball_vx > 0 and _rect_ball_overlap(
            self.ball_x, self.ball_y, RIGHT_PADDLE_X_CENTER, self.right_y
        ):
            self.ball_vx, self.ball_vy = _bounce_paddle(
                self.ball_vx, self.ball_vy, self.right_y, self.ball_y
            )
            self.ball_x = RIGHT_PADDLE_X_CENTER - pw / 2 - br - 0.01
            self.rally += 1

        w = PHYSICS["COURT_WIDTH"]
        if self.ball_x + br < 0:
            self.score_right += 1
            reward = 1.0
            self._rng_counter += 1
            self._serve(True)
            self.rally = 0
        elif self.ball_x - br > w:
            self.score_left += 1
            reward = -1.0
            self._rng_counter += 1
            self._serve(False)
            self.rally = 0

        if self.score_left >= PHYSICS["WIN_SCORE"] or self.score_right >= PHYSICS[
            "WIN_SCORE"
        ]:
            terminated = True

        if self._step_count >= self.max_episode_steps:
            truncated = True

        return self._get_obs(), reward, terminated, truncated, {}
