import {
  BALL_BASE_SPEED,
  BALL_RADIUS,
  BALL_SPEED_MULT,
  BALL_SPEED_SCALE_MAX,
  BALL_SPEED_SCALE_MIN,
  COURT_HEIGHT,
  COURT_WIDTH,
  OBS_DIM,
  PADDLE_HEIGHT,
  PADDLE_HEIGHT_SCALE_MAX,
  PADDLE_HEIGHT_SCALE_MIN,
  PADDLE_MARGIN,
  PADDLE_SPEED,
  PADDLE_WIDTH,
  RIGHT_PADDLE_X_CENTER,
  V_MAX,
  WIN_SCORE,
} from "./constants";
import type { BallState, GameState, KeyInput } from "./types";

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n));
}

function mulberry32(seed: number): () => number {
  return function () {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function clampPaddleHeightScale(scale: number): number {
  return clamp(scale, PADDLE_HEIGHT_SCALE_MIN, PADDLE_HEIGHT_SCALE_MAX);
}

/** Pixel height of the player (left) paddle. */
export function effectiveLeftPaddleHeight(state: GameState): number {
  return PADDLE_HEIGHT * clampPaddleHeightScale(state.paddleHeightScale);
}

/** Pixel height of the opponent (right) paddle — fixed at training default. */
export function effectiveRightPaddleHeight(): number {
  return PADDLE_HEIGHT;
}

function paddleYBounds(ph: number): { min: number; max: number } {
  return { min: ph / 2, max: COURT_HEIGHT - ph / 2 };
}

function paddleTop(py: number, ph: number): number {
  return py - ph / 2;
}

function paddleBottom(py: number, ph: number): number {
  return py + ph / 2;
}

function clampSpeedScale(scale: number): number {
  return clamp(scale, BALL_SPEED_SCALE_MIN, BALL_SPEED_SCALE_MAX);
}

function serveBall(
  rng: number,
  towardRight: boolean,
  speedScale: number,
): BallState {
  const rand = mulberry32(rng);
  const base = BALL_BASE_SPEED * clampSpeedScale(speedScale);
  const theta = (rand() * 0.8 - 0.4) * Math.PI;
  let vx = Math.cos(theta) * base;
  let vy = Math.sin(theta) * base;
  if (towardRight) vx = Math.abs(vx);
  else vx = -Math.abs(vx);
  if (rand() > 0.5) vy = -vy;
  return { x: COURT_WIDTH / 2, y: COURT_HEIGHT / 2, vx, vy };
}

export function createInitialState(
  seed = 1,
  ballSpeedScale = 1,
  paddleHeightScale = 1,
): GameState {
  const bs = clampSpeedScale(ballSpeedScale);
  const ps = clampPaddleHeightScale(paddleHeightScale);
  const r = mulberry32(seed * 7919);
  const ball = serveBall(seed * 7919, r() > 0.5, bs);
  return {
    ball,
    left: { y: COURT_HEIGHT / 2 },
    right: { y: COURT_HEIGHT / 2 },
    scoreLeft: 0,
    scoreRight: 0,
    rally: 0,
    rng: seed,
    ballSpeedScale: bs,
    paddleHeightScale: ps,
  };
}

export function resetMatch(state: GameState): GameState {
  const n = createInitialState(
    state.rng + 17,
    state.ballSpeedScale,
    state.paddleHeightScale,
  );
  n.scoreLeft = 0;
  n.scoreRight = 0;
  return n;
}

function normBallX(x: number): number {
  return (x / COURT_WIDTH) * 2 - 1;
}

function normBallY(y: number): number {
  return (y / COURT_HEIGHT) * 2 - 1;
}

function normPaddleY(py: number, ph: number): number {
  const lo = ph / 2;
  const hi = COURT_HEIGHT - ph / 2;
  return ((py - lo) / (hi - lo)) * 2 - 1;
}

/** Observation from the right paddle's perspective (policy input). */
export function buildObservation(state: GameState): Float32Array {
  const { ball, left, right } = state;
  const leftPh = effectiveLeftPaddleHeight(state);
  const rightPh = effectiveRightPaddleHeight();
  const vCap = V_MAX * clampSpeedScale(state.ballSpeedScale);
  const obs = new Float32Array(OBS_DIM);
  obs[0] = normBallX(ball.x);
  obs[1] = normBallY(ball.y);
  obs[2] = clamp(ball.vx / vCap, -1, 1);
  obs[3] = clamp(ball.vy / vCap, -1, 1);
  obs[4] = normPaddleY(left.y, leftPh);
  obs[5] = normPaddleY(right.y, rightPh);
  obs[6] = clamp((ball.y - right.y) / (COURT_HEIGHT / 2), -1, 1);
  obs[7] = clamp((ball.x - RIGHT_PADDLE_X_CENTER) / (COURT_WIDTH / 2), -1, 1);
  return obs;
}

function movePaddle(
  py: number,
  up: boolean,
  down: boolean,
  dt: number,
  ph: number,
): number {
  let v = 0;
  if (up) v -= PADDLE_SPEED;
  if (down) v += PADDLE_SPEED;
  const { min, max } = paddleYBounds(ph);
  return clamp(py + v * dt, min, max);
}

/** Simple CPU opponent when RL is off. */
export function heuristicRightTarget(state: GameState, dt: number): number {
  const ph = effectiveRightPaddleHeight();
  const py = state.right.y;
  const { y: by } = state.ball;
  const dy = by - py;
  const maxStep = PADDLE_SPEED * dt;
  const { min, max } = paddleYBounds(ph);
  if (Math.abs(dy) <= maxStep) return clamp(by, min, max);
  return py + Math.sign(dy) * maxStep;
}

function rectBallOverlap(
  rx: number,
  ry: number,
  pxCenter: number,
  pyCenter: number,
  ph: number,
): boolean {
  const px0 = pxCenter - PADDLE_WIDTH / 2;
  const px1 = pxCenter + PADDLE_WIDTH / 2;
  const py0 = paddleTop(pyCenter, ph);
  const py1 = paddleBottom(pyCenter, ph);
  const bx0 = rx - BALL_RADIUS;
  const bx1 = rx + BALL_RADIUS;
  const by0 = ry - BALL_RADIUS;
  const by1 = ry + BALL_RADIUS;
  return bx0 < px1 && bx1 > px0 && by0 < py1 && by1 > py0;
}

function bounceOffPaddle(
  ball: BallState,
  pyCenter: number,
  speedScale: number,
  ph: number,
): void {
  ball.vx = -ball.vx * BALL_SPEED_MULT;
  const half = ph / 2;
  const offset = (ball.y - pyCenter) / half;
  const kick = offset * 0.35 * Math.abs(ball.vx);
  ball.vy += kick;
  const cap = V_MAX * clampSpeedScale(speedScale);
  const sp = Math.hypot(ball.vx, ball.vy);
  if (sp > cap) {
    ball.vx *= cap / sp;
    ball.vy *= cap / sp;
  }
}

export interface StepContext {
  rightMode: "heuristic" | "rl";
  /** Discrete 0 up, 1 noop, 2 down — only when rightMode === 'rl'. */
  rlAction?: number;
  /** Ball speed multiplier (browser UI; affects serve, cap, live velocity). */
  ballSpeedScale: number;
  /** Player paddle height multiplier vs `PADDLE_HEIGHT` (browser UI). */
  paddleHeightScale: number;
}

export function stepGame(
  state: GameState,
  dt: number,
  keys: KeyInput,
  ctx: StepContext,
): GameState {
  const next: GameState = {
    ...state,
    ball: { ...state.ball },
    left: { ...state.left },
    right: { ...state.right },
  };
  const newScale = clampSpeedScale(ctx.ballSpeedScale);
  const prevScale = state.ballSpeedScale;
  if (newScale !== prevScale && prevScale > 0) {
    next.ball.vx *= newScale / prevScale;
    next.ball.vy *= newScale / prevScale;
  }
  next.ballSpeedScale = newScale;

  next.paddleHeightScale = clampPaddleHeightScale(ctx.paddleHeightScale);
  const leftPh = effectiveLeftPaddleHeight(next);
  const rightPh = effectiveRightPaddleHeight();
  const leftBounds = paddleYBounds(leftPh);
  const rightBounds = paddleYBounds(rightPh);
  next.left.y = clamp(next.left.y, leftBounds.min, leftBounds.max);
  next.right.y = clamp(next.right.y, rightBounds.min, rightBounds.max);

  next.left.y = movePaddle(
    next.left.y,
    keys.leftUp,
    keys.leftDown,
    dt,
    leftPh,
  );

  if (ctx.rightMode === "heuristic") {
    next.right.y = heuristicRightTarget(next, dt);
  } else {
    const a = ctx.rlAction ?? 1;
    const up = a === 0;
    const down = a === 2;
    next.right.y = movePaddle(next.right.y, up, down, dt, rightPh);
  }

  next.ball.x += next.ball.vx * dt;
  next.ball.y += next.ball.vy * dt;

  const { ball } = next;
  if (ball.y - BALL_RADIUS <= 0) {
    ball.y = BALL_RADIUS;
    ball.vy = Math.abs(ball.vy);
  } else if (ball.y + BALL_RADIUS >= COURT_HEIGHT) {
    ball.y = COURT_HEIGHT - BALL_RADIUS;
    ball.vy = -Math.abs(ball.vy);
  }

  const leftCx = PADDLE_MARGIN + PADDLE_WIDTH / 2;
  const rightCx = RIGHT_PADDLE_X_CENTER;

  if (
    ball.vx < 0 &&
    rectBallOverlap(ball.x, ball.y, leftCx, next.left.y, leftPh)
  ) {
    bounceOffPaddle(ball, next.left.y, next.ballSpeedScale, leftPh);
    ball.x = leftCx + PADDLE_WIDTH / 2 + BALL_RADIUS + 0.01;
    next.rally += 1;
  } else if (
    ball.vx > 0 &&
    rectBallOverlap(ball.x, ball.y, rightCx, next.right.y, rightPh)
  ) {
    bounceOffPaddle(ball, next.right.y, next.ballSpeedScale, rightPh);
    ball.x = rightCx - PADDLE_WIDTH / 2 - BALL_RADIUS - 0.01;
    next.rally += 1;
  }

  if (ball.x + BALL_RADIUS < 0) {
    next.scoreRight += 1;
    next.rng += 1;
    next.ball = serveBall(next.rng * 9973, true, next.ballSpeedScale);
    next.rally = 0;
  } else if (ball.x - BALL_RADIUS > COURT_WIDTH) {
    next.scoreLeft += 1;
    next.rng += 1;
    next.ball = serveBall(next.rng * 9973, false, next.ballSpeedScale);
    next.rally = 0;
  }

  return next;
}

export function isMatchOver(state: GameState): boolean {
  return state.scoreLeft >= WIN_SCORE || state.scoreRight >= WIN_SCORE;
}
