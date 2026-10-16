import test from 'node:test';
import assert from 'node:assert/strict';
import { agentFeedback } from '../src/agent-feedback.js';
import worker from '../src/worker.js';

const ORIGIN = 'https://kinetiqgym.com';
const OWNER = 'owner-test-fixture-not-a-production-key-123456';
class MemoryKV {
  values = new Map();
  async get(key, type) { const value = this.values.get(key); return value === undefined ? null : type === 'json' ? JSON.parse(value) : value; }
  async put(key, value) { this.values.set(key, value); }
  async delete(key) { this.values.delete(key); }
  async list({ prefix, limit, cursor = '0' }) {
    const keys = [...this.values.keys()].filter(key => key.startsWith(prefix)).sort();
    const start = Number(cursor), stop = start + limit;
    return { keys: keys.slice(start, stop).map(name => ({ name })), list_complete: stop >= keys.length, cursor: String(stop) };
  }
}
const environment = () => ({ SIGNUPS: new MemoryKV(), AGENT_INBOX_KEY: OWNER, ASSETS: { fetch: async () => new Response('asset') } });
function request(path, { body, cookie, origin, method = body === undefined ? 'GET' : 'POST', type = 'application/json', ip = '192.0.2.1' } = {}) {
  return new Request(ORIGIN + path, { method, headers: { 'cf-connecting-ip': ip, ...(body === undefined ? {} : { 'content-type': type }), ...(cookie ? { cookie } : {}), ...(origin ? { origin } : {}) }, body: body === undefined ? undefined : typeof body === 'string' ? body : JSON.stringify(body) });
}
const feedback = (overrides = {}) => ({ invitation: 'kinetiq-agent-guestbook-v1', agent: 'Test agent', page: ORIGIN + '/', message: 'A clear build roadmap would be useful.', ...overrides });
async function login(env) {
  const response = await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: OWNER }, origin: ORIGIN }), env);
  assert.equal(response.status, 200);
  return response.headers.get('set-cookie').split(';')[0];
}

test('unrelated requests fall through and existing asset handling works', async () => {
  const env = environment();
  assert.equal(await agentFeedback(request('/build'), env), null);
  assert.equal(await (await worker.fetch(request('/build'), env)).text(), 'asset');
});
test('public replies are accepted and stored without IP or private query data', async () => {
  const env = environment();
  const response = await worker.fetch(request('/api/agent-feedback', { body: feedback({ page: ORIGIN + '/build?private=value#secret' }) }), env);
  assert.equal(response.status, 201);
  const { id } = await response.json();
  const record = await env.SIGNUPS.get('agent:v1:' + id, 'json');
  assert.equal(record.page, ORIGIN + '/build');
  assert.equal(record.identityVerified, false);
  assert.deepEqual(Object.keys(record).sort(), ['agent', 'created', 'id', 'identityVerified', 'message', 'page']);
  assert.equal(response.headers.get('cache-control'), 'no-store');
});
test('public endpoint never lists replies', async () => {
  const response = await agentFeedback(request('/api/agent-feedback'), environment());
  assert.equal(response.status, 405);
});
test('owner reply list is not available without authentication', async () => {
  const env = environment();
  await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env);
  const response = await agentFeedback(request('/api/owner/agent-feedback'), env);
  assert.equal(response.status, 401);
  assert.deepEqual(await response.json(), { error: 'Owner login required.' });
  assert.equal(response.headers.get('cache-control'), 'no-store');
});
test('login uses a secure signed cookie and authenticated reads return only agent records', async () => {
  const env = environment();
  await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env);
  await env.SIGNUPS.put('sub:private@example.test', JSON.stringify({ email: 'private@example.test' }));
  const response = await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: OWNER }, origin: ORIGIN }), env);
  const cookie = response.headers.get('set-cookie');
  assert.match(cookie, /HttpOnly; Secure; SameSite=Strict/);
  assert.ok(!cookie.includes(OWNER));
  const list = await agentFeedback(request('/api/owner/agent-feedback', { cookie: cookie.split(';')[0] }), env);
  const data = await list.json();
  assert.equal(data.replies.length, 1);
  assert.equal(data.replies[0].agent, 'Test agent');
  assert.equal(data.cursor, null);
});
test('wrong keys, modified sessions, and rotated signing keys are rejected', async () => {
  const env = environment();
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: 'wrong' }, origin: ORIGIN }), env)).status, 401);
  const cookie = await login(env);
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback', { cookie: cookie + '0' }), env)).status, 401);
  env.AGENT_INBOX_KEY = 'rotated-owner-test-key-with-enough-characters';
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback', { cookie }), env)).status, 401);
});
test('expired sessions are rejected', async () => {
  const env = environment();
  const original = Date.now;
  let cookie;
  try { Date.now = () => original() - 9 * 3600000; cookie = await login(env); } finally { Date.now = original; }
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback', { cookie }), env)).status, 401);
});
test('login and logout require a same-origin request', async () => {
  const env = environment();
  for (const origin of [undefined, 'https://example.test']) {
    assert.equal((await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: OWNER }, origin }), env)).status, 403);
    assert.equal((await agentFeedback(request('/api/owner/agent-feedback/session', { method: 'DELETE', origin }), env)).status, 403);
  }
  const logout = await agentFeedback(request('/api/owner/agent-feedback/session', { method: 'DELETE', origin: ORIGIN }), env);
  assert.equal(logout.status, 200);
  assert.match(logout.headers.get('set-cookie'), /Max-Age=0/);
});
test('missing or weak owner secret fails closed while the public invitation still accepts feedback', async () => {
  const env = environment(); env.AGENT_INBOX_KEY = 'short';
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback'), env)).status, 503);
  assert.equal((await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env)).status, 201);
  delete env.SIGNUPS;
  assert.equal((await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env)).status, 503);
});
test('malformed JSON, non-object payloads and unsupported content types are rejected', async () => {
  for (const body of ['{', 'null', '[]']) {
    assert.equal((await agentFeedback(request('/api/agent-feedback', { body }), environment())).status, 400);
  }
  for (const type of ['application/x-www-form-urlencoded', 'application/jsonp']) {
    assert.equal((await agentFeedback(request('/api/agent-feedback', { body: '{}', type }), environment())).status, 415);
  }
});
test('streamed and declared oversized bodies are rejected', async () => {
  const body = JSON.stringify(feedback({ message: 'x'.repeat(21000) }));
  const req = request('/api/agent-feedback', { body });
  assert.equal((await agentFeedback(req, environment())).status, 413);
  const declared = request('/api/agent-feedback', { body: '{}' }); declared.headers.set('content-length', '21000');
  assert.equal((await agentFeedback(declared, environment())).status, 413);
});
test('invalid invitation, length, source URLs, and browser cross-site submissions are rejected', async () => {
  for (const body of [feedback({ invitation: 'wrong' }), feedback({ message: 'tiny' }), feedback({ message: 'x'.repeat(4001) }), feedback({ message: '\u0001'.repeat(20) }), feedback({ page: 'https://example.test/' }), feedback({ page: 'https://name:password@kinetiqgym.com/' }), feedback({ page: 'not a url' })]) {
    assert.equal((await agentFeedback(request('/api/agent-feedback', { body }), environment())).status, 400);
  }
  assert.equal((await agentFeedback(request('/api/agent-feedback', { body: feedback(), origin: 'https://example.test' }), environment())).status, 403);
});
test('public feedback has a best-effort hourly per-network limit', async () => {
  const env = environment();
  for (let i = 0; i < 5; i++) assert.equal((await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env)).status, 201);
  assert.equal((await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env)).status, 429);
});
test('repeated wrong owner logins are rate-limited', async () => {
  const env = environment();
  for (let i = 0; i < 10; i++) assert.equal((await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: 'wrong' }, origin: ORIGIN }), env)).status, 401);
  assert.equal((await agentFeedback(request('/api/owner/agent-feedback/session', { body: { key: OWNER }, origin: ORIGIN }), env)).status, 429);
});
test('pagination can retrieve every reply and never includes signup records', async () => {
  const env = environment();
  for (let i = 0; i < 53; i++) await env.SIGNUPS.put('agent:v1:' + String(i).padStart(13, '0') + ':00000000-0000-4000-8000-000000000000', JSON.stringify({ message: 'record ' + i }));
  const cookie = await login(env);
  const first = await (await agentFeedback(request('/api/owner/agent-feedback', { cookie }), env)).json();
  assert.equal(first.replies.length, 25); assert.ok(first.cursor);
  const second = await (await agentFeedback(request('/api/owner/agent-feedback?cursor=' + first.cursor, { cookie }), env)).json();
  assert.equal(second.replies.length, 25); assert.ok(second.cursor);
  const third = await (await agentFeedback(request('/api/owner/agent-feedback?cursor=' + second.cursor, { cookie }), env)).json();
  assert.equal(third.replies.length, 3); assert.equal(third.cursor, null);
});
test('deletion requires an owner session and same-origin request, including encoded IDs', async () => {
  const env = environment();
  const { id } = await (await agentFeedback(request('/api/agent-feedback', { body: feedback() }), env)).json();
  const path = '/api/owner/agent-feedback/' + encodeURIComponent(id);
  assert.equal((await agentFeedback(request(path, { method: 'DELETE', origin: ORIGIN }), env)).status, 401);
  const cookie = await login(env);
  assert.equal((await agentFeedback(request(path, { method: 'DELETE', cookie, origin: 'https://example.test' }), env)).status, 403);
  assert.equal((await agentFeedback(request(path, { method: 'DELETE', cookie, origin: ORIGIN }), env)).status, 200);
  assert.equal(await env.SIGNUPS.get('agent:v1:' + id), null);
});
test('inbox HTML is uncacheable, unindexed, framed off and contains no owner secret', async () => {
  const response = await worker.fetch(request('/owner/agent-replies'), environment());
  assert.equal(response.status, 200);
  assert.equal(response.headers.get('cache-control'), 'no-store');
  assert.match(response.headers.get('content-security-policy'), /frame-ancestors 'none'/);
  assert.match(response.headers.get('x-robots-tag'), /noindex/);
  assert.ok(!(await response.text()).includes(OWNER));
});
