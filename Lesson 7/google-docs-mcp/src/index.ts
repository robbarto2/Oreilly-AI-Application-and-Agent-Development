#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { google } from "googleapis";
import { appendInsertIndex, documentToPlainText } from "./docs-helpers.js";
import { getDocsAuth } from "./auth.js";

const server = new Server(
  {
    name: "google-docs-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "docs_get",
      description:
        "Read a Google Doc by ID (from the URL: docs.google.com/document/d/<ID>/…). " +
        "Returns title and plain text (paragraphs; tables not fully expanded).",
      inputSchema: {
        type: "object",
        properties: {
          documentId: {
            type: "string",
            description: "The Google Doc ID.",
          },
        },
        required: ["documentId"],
      },
    },
    {
      name: "docs_append_text",
      description:
        "Append UTF-8 text to the end of a Google Doc. Requires write access; share the doc with the service account email if using a service account.",
      inputSchema: {
        type: "object",
        properties: {
          documentId: { type: "string", description: "The Google Doc ID." },
          text: { type: "string", description: "Text to append." },
        },
        required: ["documentId", "text"],
      },
    },
    {
      name: "docs_insert_text",
      description:
        "Insert text at a UTF-16 code unit index (see docs_get metadata or Google Docs API index rules).",
      inputSchema: {
        type: "object",
        properties: {
          documentId: { type: "string" },
          index: {
            type: "number",
            description: "1-based index in the document body (UTF-16).",
          },
          text: { type: "string" },
        },
        required: ["documentId", "index", "text"],
      },
    },
  ],
}));

function jsonResult(data: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
  };
}

function errResult(message: string) {
  return {
    content: [{ type: "text" as const, text: message }],
    isError: true as const,
  };
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const auth = await getDocsAuth();
  const docs = google.docs({ version: "v1", auth });
  const name = request.params.name;
  const args = (request.params.arguments ?? {}) as Record<string, unknown>;

  try {
    if (name === "docs_get") {
      const documentId = String(args.documentId ?? "");
      if (!documentId) return errResult("documentId is required");
      const { data } = await docs.documents.get({ documentId });
      const plainText = documentToPlainText(data);
      return jsonResult({
        documentId: data.documentId,
        title: data.title,
        plainText,
        revisionId: data.revisionId,
        note: "Indices for insert are UTF-16; use docs_append_text to avoid index math.",
      });
    }

    if (name === "docs_append_text") {
      const documentId = String(args.documentId ?? "");
      const text = String(args.text ?? "");
      if (!documentId || !text) {
        return errResult("documentId and text are required");
      }
      const { data: current } = await docs.documents.get({ documentId });
      const index = appendInsertIndex(current);
      await docs.documents.batchUpdate({
        documentId,
        requestBody: {
          requests: [{ insertText: { location: { index }, text } }],
        },
      });
      return jsonResult({
        ok: true,
        documentId,
        insertedAtIndex: index,
        utf16UnitsInserted: text.length,
      });
    }

    if (name === "docs_insert_text") {
      const documentId = String(args.documentId ?? "");
      const text = String(args.text ?? "");
      const index = Number(args.index);
      if (!documentId || !text || !Number.isFinite(index)) {
        return errResult("documentId, index, and text are required");
      }
      await docs.documents.batchUpdate({
        documentId,
        requestBody: {
          requests: [{ insertText: { location: { index }, text } }],
        },
      });
      return jsonResult({
        ok: true,
        documentId,
        insertedAtIndex: index,
      });
    }

    return errResult(`Unknown tool: ${name}`);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return errResult(`Google Docs API error: ${msg}`);
  }
});

async function main() {
  if (!process.env.GOOGLE_APPLICATION_CREDENTIALS) {
    if (
      !process.env.GOOGLE_CLIENT_ID ||
      !process.env.GOOGLE_CLIENT_SECRET ||
      !process.env.GOOGLE_REFRESH_TOKEN
    ) {
      // Still start; first tool call will error with a clear message.
    }
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
