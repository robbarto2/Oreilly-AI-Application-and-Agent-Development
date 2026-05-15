export interface ControlCallbacks {
  onPauseToggle: () => void;
  onResetMatch: () => void;
  onAgentToggle: (enabled: boolean) => void;
  onDismissHelp: () => void;
}

export function bindControls(
  root: HTMLElement,
  callbacks: ControlCallbacks,
): {
  setAgentChecked: (v: boolean) => void;
  focusPause: () => void;
} {
  const btnPause = root.querySelector<HTMLButtonElement>("#btn-pause")!;
  const btnReset = root.querySelector<HTMLButtonElement>("#btn-reset")!;
  const agentToggle = root.querySelector<HTMLInputElement>("#agent-toggle")!;
  const btnHelpClose = root.querySelector<HTMLButtonElement>("#btn-help-close")!;
  const helpOverlay = root.querySelector<HTMLElement>("#help-overlay")!;

  btnPause.addEventListener("click", () => callbacks.onPauseToggle());
  btnReset.addEventListener("click", () => callbacks.onResetMatch());
  agentToggle.addEventListener("change", () =>
    callbacks.onAgentToggle(agentToggle.checked),
  );
  btnHelpClose.addEventListener("click", () => {
    helpOverlay.hidden = true;
    callbacks.onDismissHelp();
  });

  helpOverlay.addEventListener("click", (e) => {
    if (e.target === helpOverlay) {
      helpOverlay.hidden = true;
      callbacks.onDismissHelp();
    }
  });

  return {
    setAgentChecked: (v: boolean) => {
      agentToggle.checked = v;
    },
    focusPause: () => btnPause.focus(),
  };
}
