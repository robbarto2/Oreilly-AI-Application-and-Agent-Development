/**
 * One-time OAuth helper: prints an authorize URL, you grant access, paste the code,
 * then add the printed GOOGLE_REFRESH_TOKEN to your environment.
 *
 * Usage:
 *   GOOGLE_CLIENT_ID=... GOOGLE_CLIENT_SECRET=... npm run oauth-setup
 *
 * Create OAuth Client ID (Desktop) in Google Cloud Console; add yourself as test user if in Testing.
 */
import { createInterface } from "node:readline/promises";
import { stdin as input, stdout as output } from "node:process";
import { google } from "googleapis";
import { DOCS_RW_SCOPE } from "../auth.js";

const REDIRECT = "http://127.0.0.1";

async function main() {
  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  if (!clientId || !clientSecret) {
    console.error("Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET");
    process.exit(1);
  }

  const oauth2 = new google.auth.OAuth2(clientId, clientSecret, REDIRECT);
  const url = oauth2.generateAuthUrl({
    access_type: "offline",
    prompt: "consent",
    scope: [DOCS_RW_SCOPE],
  });

  console.log("Open this URL in a browser, sign in, and approve access:\n");
  console.log(url);
  console.log("\nAfter redirect (or from the code in the URL if using copy/paste flow), paste the `code` query param here.\n");

  const rl = createInterface({ input, output });
  const code = (await rl.question("Authorization code: ")).trim();
  rl.close();

  const { tokens } = await oauth2.getToken(code);
  if (!tokens.refresh_token) {
    console.error(
      "No refresh_token returned. Revoke app access in Google Account settings and retry with prompt=consent, or use a Desktop OAuth client.",
    );
    process.exit(1);
  }

  console.log("\nAdd this to your MCP env (do not commit):\n");
  console.log(`GOOGLE_REFRESH_TOKEN=${tokens.refresh_token}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
