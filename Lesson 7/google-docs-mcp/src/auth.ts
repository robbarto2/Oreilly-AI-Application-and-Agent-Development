import { google } from "googleapis";

/** Full access to create/edit docs; use documents.readonly if you only need reads. */
export const DOCS_RW_SCOPE = "https://www.googleapis.com/auth/documents";

/** OAuth2 for user tokens, or GoogleAuth for service accounts (pass-through to google.docs). */
export async function getDocsAuth() {
  const saPath = process.env.GOOGLE_APPLICATION_CREDENTIALS;
  if (saPath?.trim()) {
    return new google.auth.GoogleAuth({
      scopes: [DOCS_RW_SCOPE],
    });
  }

  const clientId = process.env.GOOGLE_CLIENT_ID;
  const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
  const refreshToken = process.env.GOOGLE_REFRESH_TOKEN;

  if (!clientId || !clientSecret || !refreshToken) {
    throw new Error(
      "Set GOOGLE_APPLICATION_CREDENTIALS (service account JSON path) or " +
        "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN for user OAuth.",
    );
  }

  const oauth2 = new google.auth.OAuth2(
    clientId,
    clientSecret,
    "http://127.0.0.1",
  );
  oauth2.setCredentials({ refresh_token: refreshToken });
  return oauth2;
}
