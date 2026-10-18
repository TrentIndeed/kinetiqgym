// The two site forms against D1, with db/schema.sql loaded into an in-memory SQLite (node:sqlite).
//   node --test tools/*.test.mjs
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { DatabaseSync } from 'node:sqlite';
import worker from '../src/worker.js';

const SCHEMA = readFileSync(new URL('../db/schema.sql', import.meta.url), 'utf8');

class MemoryD1 {                                                             // the slice of the D1 API the worker uses
  db = new DatabaseSync(':memory:');
  constructor() { this.db.exec(SCHEMA); }
  prepare(sql) {
    const order = [];                                                        // D1 numbers its parameters (?1, ?2); node:sqlite binds in order
    const stmt = this.db.prepare(sql.replace(/\?(\d+)/g, (_, n) => { order.push(Number(n) - 1); return '?'; }));
    let args = [];
    const api = {
      bind: (...a) => { args = order.map(i => a[i] ?? null); return api; },
      first: async () => stmt.get(...args) ?? null,
      run: async () => { stmt.run(...args); return { success: true }; },
      all: async () => ({ results: stmt.all(...args) }),
    };
    return api;
  }
  rows(sql) { return this.db.prepare(sql).all(); }
}

const env = () => ({ DB: new MemoryD1(), ASSETS: { fetch: async () => new Response('asset') } });
const post = (path, body, ip = '203.0.113.7') => new Request('https://kinetiqgym.com' + path, {
  method: 'POST', headers: { 'content-type': 'application/json', 'cf-connecting-ip': ip }, body: JSON.stringify(body),
});
const call = async (e, path, body, ip) => { const r = await worker.fetch(post(path, body, ip), e); return [r.status, await r.json()]; };

test('a signup is stored once; the second call adds the interest answer and keeps the first date', async () => {
  const e = env();
  assert.deepEqual(await call(e, '/api/subscribe', { email: 'Someone@Example.test', source: 'build' }), [200, { ok: true, returning: false }]);
  const [first] = e.DB.rows('SELECT * FROM signups');
  assert.equal(first.email, 'someone@example.test'); assert.equal(first.source, 'build'); assert.equal(first.interest, null);
  await new Promise(r => setTimeout(r, 5));
  assert.deepEqual(await call(e, '/api/subscribe', { email: 'someone@example.test', interest: 'kit', source: 'home' }), [200, { ok: true, returning: true }]);
  const rows = e.DB.rows('SELECT * FROM signups');
  assert.equal(rows.length, 1); assert.equal(rows[0].interest, 'kit'); assert.equal(rows[0].source, 'build');
  assert.equal(rows[0].created, first.created); assert.notEqual(rows[0].updated, first.updated);
  await call(e, '/api/subscribe', { email: 'someone@example.test', interest: 'nonsense' });
  assert.equal(e.DB.rows('SELECT interest FROM signups')[0].interest, 'kit');           // an unknown answer does not erase the old one
});

test('bad input and the honeypot store nothing', async () => {
  const e = env();
  assert.equal((await call(e, '/api/subscribe', { email: 'not-an-email' }))[0], 400);
  assert.deepEqual(await call(e, '/api/subscribe', { email: 'bot@example.test', website: 'spam' }), [200, { ok: true }]);
  assert.equal((await call(e, '/api/contact', { name: 'A', email: 'a@example.test', message: 'too short' }))[0], 400);
  assert.equal(e.DB.rows('SELECT * FROM signups').length + e.DB.rows('SELECT * FROM enquiries').length, 0);
});

test('an enquiry is stored with its date and id', async () => {
  const e = env();
  assert.deepEqual(await call(e, '/api/contact', { name: 'Coach', email: 'coach@example.test', company: 'Studio', message: 'We would like ten units for our studios.' }), [200, { ok: true }]);
  const [m] = e.DB.rows('SELECT * FROM enquiries');
  assert.equal(m.name, 'Coach'); assert.equal(m.company, 'Studio'); assert.match(m.id, /^\d{4}-\d\d-\d\dT[\d:.]+Z:[0-9a-f]{8}$/);
});

test('20 signups and 5 enquiries per address per hour; addresses are stored only as hashes', async () => {
  const e = env();
  for (let i = 0; i < 20; i++) assert.equal((await call(e, '/api/subscribe', { email: `p${i}@example.test` }))[0], 200);
  assert.equal((await call(e, '/api/subscribe', { email: 'p20@example.test' }))[0], 429);
  assert.equal((await call(e, '/api/subscribe', { email: 'other@example.test' }, '198.51.100.9'))[0], 200);
  for (let i = 0; i < 5; i++) await call(e, '/api/contact', { name: 'N', email: 'n@example.test', message: 'A message long enough to pass.' });
  assert.equal((await call(e, '/api/contact', { name: 'N', email: 'n@example.test', message: 'A message long enough to pass.' }))[0], 429);
  assert.ok(e.DB.rows('SELECT key FROM rate').every(r => /^[0-9a-f]{32}$/.test(r.key)));
});

test('without the database the forms say so', async () => {
  const e = env(); delete e.DB;
  assert.equal((await call(e, '/api/subscribe', { email: 'a@example.test' }))[0], 503);
});
