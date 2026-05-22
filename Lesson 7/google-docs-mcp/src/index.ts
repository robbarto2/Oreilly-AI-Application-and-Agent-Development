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
      name: "docs_list",
      description:
        "List Google Docs accessible to the authenticated account. " +
        "Returns id, name, modifiedTime, and webViewLink for each doc.",
      inputSchema: {
        type: "object",
        properties: {
          pageSize: {
            type: "number",
            description: "Max docs to return (1–100, default 20).",
          },
          query: {
            type: "string",
            description:
              "Optional Drive search query (e.g. \"name contains 'notes'\").",
          },
        },
      },
    },
    {
      name: "docs_create",
      description:
        "Create a new empty Google Doc. Returns documentId and webViewLink.",
      inputSchema: {
        type: "object",
        properties: {
          title: { type: "string", description: "Document title." },
        },
        required: ["title"],
      },
    },
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
    {
      name: "docs_replace_text",
      description:
        "Find and replace all occurrences of a string in a Google Doc.",
      inputSchema: {
        type: "object",
        properties: {
          documentId: { type: "string", description: "The Google Doc ID." },
          find: { type: "string", description: "Text to search for." },
          replace: { type: "string", description: "Replacement text." },
          matchCase: {
            type: "boolean",
            description: "Case-sensitive match (default false).",
          },
        },
        required: ["documentId", "find", "replace"],
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

function clampPageSize(value: unknown): number {
  const n = Number(value);
  if (!Number.isFinite(n)) return 20;
  return Math.min(100, Math.max(1, Math.floor(n)));
}

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const auth = await getDocsAuth();
  const docs = google.docs({ version: "v1", auth });
  const drive = google.drive({ version: "v3", auth });
  const name = request.params.name;
  const args = (request.params.arguments ?? {}) as Record<string, unknown>;

  try {
    if (name === "docs_list") {
      const pageSize = clampPageSize(args.pageSize);
      const userQuery =
        typeof args.query === "string" ? args.query.trim() : "";
      const q = [
        "mimeType='application/vnd.google-apps.document'",
        "trashed=false",
        userQuery,
      ]
        .filter(Boolean)
        .join(" and ");

      const { data } = await drive.files.list({
        q,
        pageSize,
        orderBy: "modifiedTime desc",
        fields: "files(id, name, modifiedTime, webViewLink)",
      });

      return jsonResult({
        count: data.files?.length ?? 0,
        files: data.files ?? [],
      });
    }

    if (name === "docs_create") {
      const title = String(args.title ?? "").trim();
      if (!title) return errResult("title is required");

      const { data } = await docs.documents.create({
        requestBody: { title },
      });

      return jsonResult({
        documentId: data.documentId,
        title: data.title,
        webViewLink: data.documentId
          ? `https://docs.google.com/document/d/${data.documentId}/edit`
          : undefined,
      });
    }

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

    if (name === "docs_replace_text") {
      const documentId = String(args.documentId ?? "");
      const find = String(args.find ?? "");
      const replace = String(args.replace ?? "");
      const matchCase = args.matchCase === true;
      if (!documentId || !find) {
        return errResult("documentId and find are required");
      }

      const { data } = await docs.documents.batchUpdate({
        documentId,
        requestBody: {
          requests: [
            {
              replaceAllText: {
                containsText: { text: find, matchCase },
                replaceText: replace,
              },
            },
          ],
        },
      });

      const changed =
        data.replies?.[0]?.replaceAllText?.occurrencesChanged ?? 0;
      return jsonResult({
        ok: true,
        documentId,
        occurrencesChanged: changed,
      });
    }

    return errResult(`Unknown tool: ${name}`);
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    return errResult(`Google Docs API error: ${msg}`);
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
