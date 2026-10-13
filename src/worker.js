// KinetiqGym.com: static site (./site) plus two form endpoints that keep the build list and project enquiries in Workers KV.
//   POST /api/subscribe  { email, interest?, source? }   build-list signup; a second call with the same email adds the interest answer
//   POST /api/contact    { name, email, company?, message }  "Discuss a project"
// Records live in the SIGNUPS namespace: sub:<email> and msg:<time>:<id>. Export them with tools/export-signups.mjs.
const INTERESTS = ['build', 'kit', 'complete', 'research', 'engineering'];
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,190}\.[^\s@]{2,24}$/;

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/subscribe' || url.pathname === '/api/contact') {
      if (request.method !== 'POST') return reply({ error: 'Use POST.' }, 405);
      if (!env.SIGNUPS) return reply({ error: 'The list is not connected yet. Please try again later.' }, 503);
      let body;
      try { body = await readBody(request); } catch { return reply({ error: 'That request could not be read.' }, 400); }
      if (body.website) return reply({ ok: true });                       // honeypot: bots fill the hidden field
      if (await limited(env, request, url.pathname)) return reply({ error: 'Too many requests. Please wait a few minutes and try again.' }, 429);
      return url.pathname === '/api/subscribe' ? subscribe(body, env, request) : contact(body, env, request);
    }
    if (url.pathname.startsWith('/api/')) return reply({ error: 'Not found.' }, 404);
    return env.ASSETS.fetch(request);
  },
};

async function subscribe(body, env, request) {
  const email = clean(body.email, 254).toLowerCase();
  if (!EMAIL.test(email)) return reply({ error: 'Enter a valid email address.' }, 400);
  const interest = INTERESTS.includes(body.interest) ? body.interest : null;
  const key = `sub:${email}`;
  const now = new Date().toISOString();
  const old = await env.SIGNUPS.get(key, 'json');
  const record = old || { email, created: now, source: clean(body.source, 40) || 'home', country: request.cf?.country || null };
  record.updated = now;
  if (interest) record.interest = interest;
  await env.SIGNUPS.put(key, JSON.stringify(record));
  return reply({ ok: true, returning: Boolean(old) });
}

async function contact(body, env, request) {
  const email = clean(body.email, 254).toLowerCase();
  const name = clean(body.name, 120), company = clean(body.company, 160), message = String(body.message ?? '').replace(/[\u0000-\u0009\u000b-\u001f\u007f]/g, ' ').trim().slice(0, 5000);
  if (!name) return reply({ error: 'Add your name.' }, 400);
  if (!EMAIL.test(email)) return reply({ error: 'Enter a valid email address so I can reply.' }, 400);
  if (message.length < 20) return reply({ error: 'Tell me a little more about the project (a few sentences is plenty).' }, 400);
  const now = new Date().toISOString();
  const id = crypto.randomUUID().slice(0, 8);
  await env.SIGNUPS.put(`msg:${now}:${id}`, JSON.stringify({ name, email, company, message, created: now, country: request.cf?.country || null }));
  return reply({ ok: true });
}

async function readBody(request) {
  const type = request.headers.get('content-type') || '';
  if (Number(request.headers.get('content-length') || 0) > 20000) throw new Error('too large');
  if (type.includes('application/json')) return await request.json();
  return Object.fromEntries(await request.formData());
}

async function limited(env, request, path) {
  const ip = request.headers.get('cf-connecting-ip') || 'unknown';
  const key = `rate:${path}:${ip}`;
  const n = Number(await env.SIGNUPS.get(key)) || 0;
  if (n >= (path === '/api/contact' ? 5 : 20)) return true;
  await env.SIGNUPS.put(key, String(n + 1), { expirationTtl: 3600 });
  return false;
}

const clean = (v, max) => String(v ?? '').replace(/[\u0000-\u001f\u007f]/g, ' ').trim().slice(0, max);
const reply = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' },
});
