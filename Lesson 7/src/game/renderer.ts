import {
  BALL_RADIUS,
  COURT_HEIGHT,
  COURT_WIDTH,
  PADDLE_HEIGHT,
  PADDLE_MARGIN,
  PADDLE_WIDTH,
} from "./constants";
import type { GameState } from "./types";

export interface RendererColors {
  court: string;
  paddleLeft: string;
  paddleRight: string;
  paddleRightAgent: string;
  ball: string;
  line: string;
}

const defaultColors: RendererColors = {
  court: "#0d1117",
  paddleLeft: "#58a6ff",
  paddleRight: "#8b949e",
  paddleRightAgent: "#3fb950",
  ball: "#f0883e",
  line: "#30363d",
};

export function createRenderer(
  ctx: CanvasRenderingContext2D,
  scale: number,
  agentActive: boolean,
  reduceMotion: boolean,
): {
  draw: (state: GameState) => void;
} {
  const colors = defaultColors;

  function draw(state: GameState): void {
    ctx.save();
    ctx.scale(scale, scale);
    ctx.fillStyle = colors.court;
    ctx.fillRect(0, 0, COURT_WIDTH, COURT_HEIGHT);

    ctx.strokeStyle = colors.line;
    ctx.lineWidth = 2;
    ctx.setLineDash([14, 14]);
    ctx.beginPath();
    ctx.moveTo(COURT_WIDTH / 2, 0);
    ctx.lineTo(COURT_WIDTH / 2, COURT_HEIGHT);
    ctx.stroke();
    ctx.setLineDash([]);

    const lx = PADDLE_MARGIN;
    const rx = COURT_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH;

    ctx.fillStyle = colors.paddleLeft;
    ctx.fillRect(lx, state.left.y - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);

    const rightColor = agentActive ? colors.paddleRightAgent : colors.paddleRight;
    ctx.fillStyle = rightColor;
    if (agentActive && !reduceMotion) {
      ctx.shadowColor = colors.paddleRightAgent;
      ctx.shadowBlur = 18;
    }
    ctx.fillRect(rx, state.right.y - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
    ctx.shadowBlur = 0;

    ctx.fillStyle = colors.ball;
    ctx.beginPath();
    ctx.arc(state.ball.x, state.ball.y, BALL_RADIUS, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  return { draw };
}
