import type { docs_v1 } from "googleapis";

/** Best-effort plain text: paragraphs and simple text runs; tables are skipped.  */
export function documentToPlainText(doc: docs_v1.Schema$Document): string {
  const lines: string[] = [];
  const content = doc.body?.content ?? [];
  for (const el of content) {
    if (el.paragraph) {
      let line = "";
      for (const pEl of el.paragraph.elements ?? []) {
        if (pEl.textRun?.content) line += pEl.textRun.content;
      }
      lines.push(line);
    }
  }
  return lines.join("").replace(/\x03/g, "");
}

/** Index to use with InsertText for appending (Google: last structural endIndex - 1). */
export function appendInsertIndex(doc: docs_v1.Schema$Document): number {
  const content = doc.body?.content ?? [];
  let maxEnd = 1;
  for (const el of content) {
    if (typeof el.endIndex === "number" && el.endIndex > maxEnd) {
      maxEnd = el.endIndex;
    }
  }
  return Math.max(1, maxEnd - 1);
}
