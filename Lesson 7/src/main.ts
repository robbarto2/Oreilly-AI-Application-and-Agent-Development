import {
  COURT_HEIGHT,
  COURT_WIDTH,
  PHYSICS_HZ,
} from "./game/constants";
import {
  buildObservation,
  createInitialState,
  isMatchOver,
  resetMatch,
  stepGame,
} from "./game/engine";
import { createRenderer } from "./game/renderer";
import type { KeyInput } from "./game/types";
import { loadPolicy, PolicyNet } from "./rl/policy";
import { bindControls } from "./ui/controls";
import "./style.css";

const HELP_KEY = "pong-lesson7-help-dismissed";

const keys: KeyInput = {
  leftUp: false,
  leftDown: false,
};

async function main(): Promise<void> {
  const root = document.querySelector<HTMLElement>("#app")!;
  const canvas = document.querySelector<HTMLCanvasElement>("#game-canvas")!;
  const maybeCtx = canvas.getContext("2d");
  if (!maybeCtx) throw new Error("2D context not available");
  if (!(maybeCtx instanceof CanvasRenderingContext2D)) {
    throw new Error("Expected 2D canvas context");
  }
  const gl: CanvasRenderingContext2D = maybeCtx;

  const elScoreL = document.querySelector<HTMLElement>("#score-left")!;
  const elScoreR = document.querySelector<HTMLElement>("#score-right")!;
  const pauseOverlay = document.querySelector<HTMLElement>("#pause-overlay")!;
  const helpOverlay = document.querySelector<HTMLElement>("#help-overlay")!;
  const policyHint = document.querySelector<HTMLElement>("#policy-hint")!;
  const btnPause = document.querySelector<HTMLButtonElement>("#btn-pause")!;

  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  const artifact = await loadPolicy("/policy.json");
  let policy: PolicyNet | null = null;
  if (artifact && artifact.layers.length > 0) {
    policy = new PolicyNet(artifact);
  }

  let state = createInitialState(1);
  let paused = false;
  let agentWantsRl = false;
  let rlEffective = false;

  function syncRlEffective(): void {
    rlEffective = agentWantsRl && policy !== null;
    if (agentWantsRl && !policy) {
      policyHint.hidden = false;
      policyHint.textContent =
        "RL agent is on, but policy.json is missing or invalid — using CPU heuristic.";
    } else {
      policyHint.hidden = true;
      policyHint.textContent = "";
    }
  }

  syncRlEffective();

  const stageWrap = canvas.parentElement as HTMLElement;
  let scale = 1;

  function resize(): void {
    const rect = stageWrap.getBoundingClientRect();
    const w = rect.width;
    const targetH = (w * COURT_HEIGHT) / COURT_WIDTH;
    canvas.style.width = `${w}px`;
    canvas.style.height = `${targetH}px`;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    scale = (w * dpr) / COURT_WIDTH;
    canvas.width = Math.round(COURT_WIDTH * scale);
    canvas.height = Math.round(COURT_HEIGHT * scale);
  }

  resize();
  window.addEventListener("resize", resize);

  const controls = bindControls(root, {
    onPauseToggle: () => {
      paused = !paused;
      pauseOverlay.hidden = !paused;
      btnPause.textContent = paused ? "Resume" : "Pause";
    },
    onResetMatch: () => {
      state = resetMatch(state);
      elScoreL.textContent = String(state.scoreLeft);
      elScoreR.textContent = String(state.scoreRight);
    },
    onAgentToggle: (enabled: boolean) => {
      agentWantsRl = enabled;
      syncRlEffective();
    },
    onDismissHelp: () => {
      try {
        localStorage.setItem(HELP_KEY, "1");
      } catch {
        /* ignore */
      }
    },
  });

  try {
    if (!localStorage.getItem(HELP_KEY)) helpOverlay.hidden = false;
  } catch {
    helpOverlay.hidden = false;
  }

  controls.setAgentChecked(false);
  canvas.focus();

  let last = performance.now();
  let accum = 0;
  const dt = 1 / PHYSICS_HZ;

  function frame(now: number): void {
    requestAnimationFrame(frame);

    const rawDt = Math.min(0.05, (now - last) / 1000);
    last = now;

    if (!paused && !isMatchOver(state)) {
      accum += rawDt;
      while (accum >= dt) {
        let rlAction = 1;
        if (rlEffective && policy) {
          rlAction = policy.act(buildObservation(state));
        }
        state = stepGame(state, dt, keys, {
          rightMode: rlEffective ? "rl" : "heuristic",
          rlAction,
        });
        accum -= dt;
      }
    }

    elScoreL.textContent = String(state.scoreLeft);
    elScoreR.textContent = String(state.scoreRight);

    const r = createRenderer(gl, scale, rlEffective, reduceMotion);
    r.draw(state);
  }

  requestAnimationFrame(frame);

  window.addEventListener("keydown", (e) => {
    if (e.code === "ArrowUp" || e.code === "KeyW") keys.leftUp = true;
    if (e.code === "ArrowDown" || e.code === "KeyS") keys.leftDown = true;
    if (e.code === "Space") {
      e.preventDefault();
      controls.focusPause();
      paused = !paused;
      pauseOverlay.hidden = !paused;
      btnPause.textContent = paused ? "Resume" : "Pause";
    }
  });

  window.addEventListener("keyup", (e) => {
    if (e.code === "ArrowUp" || e.code === "KeyW") keys.leftUp = false;
    if (e.code === "ArrowDown" || e.code === "KeyS") keys.leftDown = false;
  });
}

void main();
