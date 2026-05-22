export interface BallState {
  x: number;
  y: number;
  vx: number;
  vy: number;
}

export interface PaddleState {
  y: number;
}

export interface GameState {
  ball: BallState;
  left: PaddleState;
  right: PaddleState;
  scoreLeft: number;
  scoreRight: number;
  rally: number;
  /** Seed for deterministic-ish serves when resetting. */
  rng: number;
  /** Multiplier for serve speed and velocity cap (browser only). */
  ballSpeedScale: number;
  /** Player (left) paddle height = PADDLE_HEIGHT × scale (browser only). */
  paddleHeightScale: number;
}

export interface KeyInput {
  leftUp: boolean;
  leftDown: boolean;
}
