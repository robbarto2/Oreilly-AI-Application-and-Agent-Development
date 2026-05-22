# Google Docs MCP Server

Local [Model Context Protocol](https://modelcontextprotocol.io) server for reading and editing Google Docs from Cursor (stdio transport).

## Tools

| Tool | Description |
|------|-------------|
| `docs_list` | List accessible Google Docs (Drive API) |
| `docs_create` | Create a new empty doc |
| `docs_get` | Read title and plain text by document ID |
| `docs_append_text` | Append text to the end of a doc |
| `docs_insert_text` | Insert text at a UTF-16 index |
| `docs_replace_text` | Find and replace all occurrences |

Document IDs come from the URL: `https://docs.google.com/document/d/<DOCUMENT_ID>/edit`

## Prerequisites

1. A [Google Cloud project](https://console.cloud.google.com/) with **Google Docs API** and **Google Drive API** enabled.
2. Credentials — choose one:

### Option A — User OAuth (recommended for personal docs)

1. Create an **OAuth client ID** (Desktop app) in APIs & Services → Credentials.
2. Add your Google account as a **test user** if the OAuth consent screen is in Testing mode.
3. Build and run the one-time token helper:

```bash
cd google-docs-mcp
npm install
npm run build
GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... npm run oauth-setup
```

4. Copy the printed `GOOGLE_REFRESH_TOKEN` into your MCP env (see below).

### Option B — Service account (good for shared team docs)

1. Create a service account and download its JSON key.
2. Set `GOOGLE_APPLICATION_CREDENTIALS` to the absolute path of that JSON file.
3. **Share each Google Doc** with the service account email (`...@....iam.gserviceaccount.com`) as Editor.

## Install and build

```bash
cd google-docs-mcp
npm install
npm run build
```

## Connect in Cursor

Add to **Cursor Settings → MCP** (or `~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "google-docs": {
      "command": "node",
      "args": [
        "/ABSOLUTE/PATH/TO/Lesson 7/google-docs-mcp/dist/index.js"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_REFRESH_TOKEN": "your-refresh-token"
      }
    }
  }
}
```

For a service account, replace the OAuth env vars with:

```json
"env": {
  "GOOGLE_APPLICATION_CREDENTIALS": "/absolute/path/to/service-account.json"
}
```

Restart Cursor after saving. The server runs locally over stdio; no HTTP port is exposed.

## Security notes

- Never commit `.env`, OAuth tokens, or service account JSON.
- Use the narrowest sharing you need (per-doc for service accounts).
- Revoke and rotate credentials if they are exposed.

## Development

```bash
npm run build   # compile TypeScript → dist/
npm start       # run server on stdio (for manual testing)
```

See [`env.example`](env.example) for environment variable names.
