/**
 * Physics and layout — keep in sync with `rl/pong_env.py` (PHYSICS dict).
 */
export const COURT_WIDTH = 960;
export const COURT_HEIGHT = 540;
export const PADDLE_WIDTH = 12;
export const PADDLE_HEIGHT = 80;
export const BALL_RADIUS = 6;
export const PADDLE_MARGIN = 24;
export const PADDLE_SPEED = 420;
export const BALL_BASE_SPEED = 320;
export const BALL_SPEED_MULT = 1.06;
export const WIN_SCORE = 5;
export const PHYSICS_HZ = 60;
export const OBS_DIM = 8;
/** Used to clamp normalized ball velocity components. */
export const V_MAX = 550;

/** Browser-only difficulty; `1` matches training defaults in `rl/pong_env.py`. */
export const BALL_SPEED_SCALE_MIN = 0.5;
export const BALL_SPEED_SCALE_MAX = 2;
export const BALL_SPEED_SCALE_DEFAULT = 1;

/** Browser-only; `1` matches `PADDLE_HEIGHT` in `rl/pong_env.py`. */
export const PADDLE_HEIGHT_SCALE_MIN = 0.45;
export const PADDLE_HEIGHT_SCALE_MAX = 1.55;
export const PADDLE_HEIGHT_SCALE_DEFAULT = 1;

export const LEFT_PADDLE_X_CENTER = PADDLE_MARGIN + PADDLE_WIDTH / 2;
export const RIGHT_PADDLE_X_CENTER =
  COURT_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH / 2;
