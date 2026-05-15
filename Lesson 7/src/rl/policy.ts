import { OBS_DIM } from "../game/constants";

export interface LinearLayerJSON {
  weight: number[][];
  bias: number[];
}

export interface PolicyArtifact {
  version: number;
  obs_dim: number;
  n_actions: number;
  layers: LinearLayerJSON[];
}

function relu(x: number): number {
  return x > 0 ? x : 0;
}

/** Forward pass: ReLU after each hidden linear layer; last layer is raw logits. */
export function forward_logits(
  artifact: PolicyArtifact,
  obs: Float32Array,
  outLogits: Float32Array,
): void {
  if (obs.length !== artifact.obs_dim) {
    throw new Error(
      `obs_dim mismatch: expected ${artifact.obs_dim}, got ${obs.length}`,
    );
  }

  const nLayers = artifact.layers.length;
  let maxHidden = 0;
  for (let i = 0; i < nLayers - 1; i++) {
    maxHidden = Math.max(maxHidden, artifact.layers[i]!.bias.length);
  }
  const h0 = new Float32Array(Math.max(maxHidden, 1));
  const h1 = new Float32Array(Math.max(maxHidden, 1));

  let input = obs;
  let useH0AsOutput = true;

  for (let li = 0; li < nLayers; li++) {
    const L = artifact.layers[li]!;
    const isLast = li === nLayers - 1;
    const outDim = L.bias.length;
    const inDim = L.weight[0]!.length;
    const output = isLast ? outLogits : useH0AsOutput ? h0 : h1;

    for (let o = 0; o < outDim; o++) {
      let s = L.bias[o]!;
      const row = L.weight[o]!;
      for (let j = 0; j < inDim; j++) s += row[j]! * input[j]!;
      output[o] = isLast ? s : relu(s);
    }

    if (!isLast) {
      input = output;
      useH0AsOutput = !useH0AsOutput;
    }
  }
}

export function argmaxActions(logits: Float32Array): number {
  let best = 0;
  for (let i = 1; i < logits.length; i++) {
    if (logits[i]! > logits[best]!) best = i;
  }
  return best;
}

export async function loadPolicy(url: string): Promise<PolicyArtifact | null> {
  try {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) return null;
    const data: unknown = await res.json();
    if (
      data &&
      typeof data === "object" &&
      "version" in data &&
      "layers" in data &&
      Array.isArray((data as PolicyArtifact).layers)
    ) {
      const p = data as PolicyArtifact;
      if (p.obs_dim !== OBS_DIM) {
        console.warn(`policy.json obs_dim ${p.obs_dim} != ${OBS_DIM}`);
      }
      return p;
    }
    return null;
  } catch {
    return null;
  }
}

export class PolicyNet {
  private artifact: PolicyArtifact;
  private logits: Float32Array;

  constructor(artifact: PolicyArtifact) {
    this.artifact = artifact;
    this.logits = new Float32Array(artifact.n_actions);
  }

  act(obs: Float32Array): number {
    forward_logits(this.artifact, obs, this.logits);
    return argmaxActions(this.logits);
  }
}
