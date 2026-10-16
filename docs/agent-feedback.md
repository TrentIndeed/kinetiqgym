# Optional agent feedback

The public invitation is `/llms.txt`. HTML comments and non-rendered alternate
links in the site pages, plus a comment in `robots.txt`, help automated visitors
find it without changing the rendered public pages. It is not secret: humans
can inspect the source or open the text URL. Some agents ignore comments and
text files, and many cannot or should not make optional external requests.
Receiving a visit does not guarantee a reply.

The invitation explicitly defers to the agent's task, user permissions and
governing instructions, and requests only feedback about public site content.
It asks for no credentials, private prompts, conversation history, payment,
accounts, or unrelated actions.

## Reply collection

`POST /api/agent-feedback` accepts JSON with the invitation identifier and a
10–4000-character message. `agent` and `page` are optional. Names are self-reported,
not verified identities. The endpoint validates page origins, drops query strings
and fragments, bounds request bodies, rejects cross-site browser submissions, and
applies a best-effort per-network/hour limit using expiring hashed identifiers.
KV counters are eventually consistent and are not a strict distributed quota.
The endpoint does not execute, publish, or email submitted text.

Replies live under the separate `agent:v1:` prefix of the existing `SIGNUPS`
Workers KV namespace, newest first. Other signups and enquiries are not returned
by this API. Replies remain until the owner deletes them. Workers KV is eventually
consistent, so a new reply or deletion may take about a minute to appear everywhere.

## Owner inbox

Open `https://kinetiqgym.com/owner/agent-replies` and use the locally saved owner
access key. This page is not linked from the public navigation. The login page
itself contains no reply data or secrets; the read/export/delete API requires an
authenticated owner session. Replies are rendered as text, never HTML, and are
untrusted external content.

The inbox can refresh, load older replies, download all replies as JSON, delete
individual replies, and sign out. It uses an eight-hour HMAC-signed, Secure,
HttpOnly, SameSite=Strict `__Host-` cookie. Keys are not stored in browser storage
or URLs. Responses are uncacheable and marked noindex, and state-changing owner
requests require an exact same-origin header. The inbox secret must have at least
32 characters; use a cryptographically generated value. Missing configuration
fails closed.

Configure `AGENT_INBOX_KEY` as a Cloudflare Worker secret, never as a public
Wrangler variable or asset. Keep the local backup in an ignored file outside
`site/`. Rotating this secret also invalidates existing sessions. To disable
collection, remove the invitation and public endpoint together.

## Validation

```sh
node --test tools/agent-feedback.test.mjs
node --check src/worker.js
node --check site/agent-inbox.js
```

`tools/add-agent-discovery.mjs` is an idempotent helper for adding the same
non-rendered discovery hint to newly added HTML pages.
