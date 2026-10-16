import { inboxPage } from './agent-inbox-page.js';

const PREFIX = 'agent:v1:';
const INVITATION = 'kinetiq-agent-guestbook-v1';
const SESSION_SECONDS = 8 * 60 * 60;
const COOKIE = '__Host-kinetiq_agent_owner';
const encoder = new TextEncoder();

// Agent identities are self-reported. The public endpoint accepts feedback only;
// it never executes submissions or makes them public.
export async function agentFeedback(request, env) {
  const url = new URL(request.url);
  if (url.pathname === '/owner/agent-replies' || url.pathname === '/owner/agent-replies/') {
    if (!['GET', 'HEAD'].includes(request.method)) return json({ error: 'Use GET.' }, 405);
    return new Response(request.method === 'HEAD' ? null : inboxPage, {
      headers: {
        'content-type': 'text/html; charset=utf-8', 'cache-control': 'no-store',
        'x-robots-tag': 'noindex, nofollow, noarchive', 'x-content-type-options': 'nosniff',
        'referrer-policy': 'no-referrer',
        'content-security-policy': "default-src 'none'; script-src 'self'; style-src 'unsafe-inline'; connect-src 'self'; img-src 'self'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'",
      },
    });
  }
  const isPublic = url.pathname === '/api/agent-feedback';
  const isSession = url.pathname === '/api/owner/agent-feedback/session';
  const isList = url.pathname === '/api/owner/agent-feedback';
  const deleteId = /^\/api\/owner\/agent-feedback\/(\d{13}(?::|%3[aA])[0-9a-f-]{36})$/.exec(url.pathname)?.[1]?.replace(/%3a/i, ':');
  if (!isPublic && !isSession && !isList && !deleteId) return null;

  try {
    if (!env.SIGNUPS) return json({ error: 'Feedback storage is not available.' }, 503);
    if (isPublic) {
      if (request.method !== 'POST') return json({ error: 'Use POST.' }, 405);
      if (!allowedOrigin(request)) return json({ error: 'Cross-site submission rejected.' }, 403);
      const body = await readJson(request);
      if (body.invitation !== INVITATION) return json({ error: 'Read /llms.txt before submitting feedback.' }, 400);
      const message = typeof body.message === 'string' ? body.message.replace(/[\u0000-\u0008\u000b-\u001f\u007f]/g, '').trim() : '';
      if (message.length < 10 || message.length > 4000) {
        return json({ error: 'Send a message between 10 and 4000 characters.' }, 400);
      }
      let page = text(body.page, 500);
      if (page) {
        let source;
        try { source = new URL(page); } catch { return json({ error: 'Use a valid Kinetiq Gym page URL.' }, 400); }
        if (source.protocol !== 'https:' || !['kinetiqgym.com', 'www.kinetiqgym.com'].includes(source.hostname) || source.username || source.password) {
          return json({ error: 'Use a Kinetiq Gym page URL without credentials.' }, 400);
        }
        page = source.origin + source.pathname;
      }
      // KV counters are a best-effort abuse limit, not an identity check.
      if (await limited(env, request, 'feedback', 5)) return json({ error: 'Please wait before sending more feedback.' }, 429);
      const id = `${String(9999999999999 - Date.now()).padStart(13, '0')}:${crypto.randomUUID()}`;
      const record = {
        id, created: new Date().toISOString(), agent: text(body.agent, 120) || 'Unidentified agent',
        message,
        page, identityVerified: false,
      };
      await env.SIGNUPS.put(PREFIX + id, JSON.stringify(record));
      return json({ ok: true, id, note: 'Your feedback was stored privately for the site owner.' }, 201);
    }

    if (!configured(env)) return json({ error: 'The owner inbox has not been configured.' }, 503);
    if (isSession) {
      if (!['POST', 'DELETE'].includes(request.method)) return json({ error: 'Use POST or DELETE.' }, 405);
      if (!sameOrigin(request)) return json({ error: 'Same-origin requests only.' }, 403);
      if (request.method === 'DELETE') return json({ ok: true }, 200, { 'set-cookie': cookie('', 0) });
      const body = await readJson(request);
      if (typeof body.key !== 'string' || body.key.length > 512) return json({ error: 'Enter the owner access key.' }, 400);
      if (await limited(env, request, 'owner-login', 10)) return json({ error: 'Too many attempts. Try again later.' }, 429);
      if (!(await equal(body.key, env.AGENT_INBOX_KEY))) return json({ error: 'Invalid owner access key.' }, 401);
      const expiry = Math.floor(Date.now() / 1000) + SESSION_SECONDS;
      const payload = `v1.${expiry}`;
      return json({ ok: true }, 200, { 'set-cookie': cookie(`${payload}.${await sign(payload, env.AGENT_INBOX_KEY)}`, SESSION_SECONDS) });
    }
    if (!(await authenticated(request, env))) return json({ error: 'Owner login required.' }, 401);
    if (deleteId) {
      if (request.method !== 'DELETE') return json({ error: 'Use DELETE.' }, 405);
      if (!sameOrigin(request)) return json({ error: 'Same-origin requests only.' }, 403);
      await env.SIGNUPS.delete(PREFIX + deleteId);
      return json({ ok: true });
    }
    if (request.method !== 'GET') return json({ error: 'Use GET.' }, 405);
    const cursor = url.searchParams.get('cursor') || undefined;
    if (cursor && (cursor.length > 2048 || /[\u0000-\u001f]/.test(cursor))) return json({ error: 'Invalid cursor.' }, 400);
    const listing = await env.SIGNUPS.list({ prefix: PREFIX, limit: 25, ...(cursor ? { cursor } : {}) });
    const records = (await Promise.all(listing.keys.map(key => env.SIGNUPS.get(key.name, 'json')))).filter(Boolean);
    return json({ replies: records, cursor: listing.list_complete ? null : listing.cursor });
  } catch (error) {
    // Do not log payloads, cookies, owner keys, or third-party error details.
    return json({ error: error instanceof InputError ? error.message : 'The request could not be completed. Please try again.' }, error instanceof InputError ? error.status : 503);
  }
}

function configured(env) { return typeof env.AGENT_INBOX_KEY === 'string' && env.AGENT_INBOX_KEY.length >= 32; }
function allowedOrigin(request) {
  const origin = request.headers.get('origin');
  return !origin || origin === new URL(request.url).origin;
}
function sameOrigin(request) { return request.headers.get('origin') === new URL(request.url).origin; }
function cookie(value, maxAge) { return `${COOKIE}=${value}; Path=/; Max-Age=${maxAge}; HttpOnly; Secure; SameSite=Strict`; }
async function authenticated(request, env) {
  const token = (request.headers.get('cookie') || '').split(';').map(v => v.trim()).find(v => v.startsWith(COOKIE + '='))?.slice(COOKIE.length + 1) || '';
  const match = /^v1\.(\d{10})\.([0-9a-f]{64})$/.exec(token);
  const now = Math.floor(Date.now() / 1000);
  if (!match || Number(match[1]) <= now || Number(match[1]) > now + SESSION_SECONDS) return false;
  return equal(match[2], await sign(`v1.${match[1]}`, env.AGENT_INBOX_KEY));
}
async function sign(payload, secret) {
  const key = await crypto.subtle.importKey('raw', encoder.encode(secret), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']);
  return hex(await crypto.subtle.sign('HMAC', key, encoder.encode(payload)));
}
async function equal(a, b) {
  const values = await Promise.all([a, b].map(value => crypto.subtle.digest('SHA-256', encoder.encode(value))));
  const left = new Uint8Array(values[0]), right = new Uint8Array(values[1]);
  let difference = 0;
  for (let i = 0; i < left.length; i++) difference |= left[i] ^ right[i];
  return difference === 0;
}
const hex = buffer => Array.from(new Uint8Array(buffer), value => value.toString(16).padStart(2, '0')).join('');
async function limited(env, request, scope, limit) {
  const bucket = Math.floor(Date.now() / 3600000);
  const identity = request.headers.get('cf-connecting-ip') || 'unknown';
  const hashed = hex(await crypto.subtle.digest('SHA-256', encoder.encode(`${scope}:${bucket}:${identity}`))).slice(0, 32);
  const key = `rate:agent:${scope}:${bucket}:${hashed}`;
  const count = Number(await env.SIGNUPS.get(key)) || 0;
  if (count >= limit) return true;
  await env.SIGNUPS.put(key, String(count + 1), { expirationTtl: 3600 });
  return false;
}
class InputError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
async function readJson(request) {
  if ((request.headers.get('content-type') || '').split(';', 1)[0].trim().toLowerCase() !== 'application/json') throw new InputError('Use application/json.', 415);
  if (Number(request.headers.get('content-length')) > 20000) throw new InputError('Request too large.', 413);
  const reader = request.body?.getReader();
  if (!reader) throw new InputError('Send a JSON object.');
  let size = 0; const chunks = [];
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > 20000) { await reader.cancel(); throw new InputError('Request too large.', 413); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  let body;
  try { body = JSON.parse(new TextDecoder().decode(bytes)); } catch { throw new InputError('Send valid JSON.'); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new InputError('Send a JSON object.');
  return body;
}
const text = (value, max) => typeof value === 'string' ? value.replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max) : '';
const json = (data, status = 200, extra = {}) => new Response(JSON.stringify(data), {
  status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store',
    'x-content-type-options': 'nosniff', 'x-robots-tag': 'noindex, noarchive', vary: 'Cookie', ...extra },
});
