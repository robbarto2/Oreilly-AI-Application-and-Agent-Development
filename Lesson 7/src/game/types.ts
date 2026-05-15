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
}

export interface KeyInput {
  leftUp: boolean;
  leftDown: boolean;
}
