// One-off: copy the build list and project enquiries from the old SIGNUPS KV namespace into D1 (apply db/schema.sql first).
//   node tools/migrate-signups-kv-to-d1.mjs            into the live D1 database
//   node tools/migrate-signups-kv-to-d1.mjs --local    into the local one wrangler dev uses (a dry run with the real records)
// Run it after deploying the D1 worker, so no signup can land in KV after the copy. Safe to run again: a row already in D1 keeps
// the earlier of the two dates and its own interest answer. Records pass through a temporary folder that is deleted at the end.
import { execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const where = process.argv.includes('--local') ? '--local' : '--remote';
const win = process.platform === 'win32';
const quote = a => (win && /[\s,()*]/.test(a) ? `"${a}"` : a);
const wrangler = (...a) => {
  const out = execFileSync(win ? 'npx.cmd' : 'npx', ['-y', 'wrangler@4', ...a].map(quote),
    { encoding: 'utf8', shell: win, maxBuffer: 64e6, stdio: ['ignore', 'pipe', 'pipe'] });
  return out.slice(Math.max(0, out.search(/[[{]/)));                        // skip wrangler's banner and warnings
};
const q = v => (v == null ? 'NULL' : `'${String(v).replace(/'/g, "''")}'`);

const dir = mkdtempSync(join(tmpdir(), 'kq-signups-'));
try {
  const keys = JSON.parse(wrangler('kv', 'key', 'list', '--binding', 'SIGNUPS', '--remote')).map(k => k.name)
    .filter(k => k.startsWith('sub:') || k.startsWith('msg:'));
  const values = {};
  for (let i = 0; i < keys.length; i += 100) {                              // bulk get takes up to 100 keys
    const file = join(dir, `keys-${i}.json`);
    writeFileSync(file, JSON.stringify(keys.slice(i, i + 100)));
    Object.assign(values, JSON.parse(wrangler('kv', 'bulk', 'get', file, '--binding', 'SIGNUPS', '--remote')));
  }
  const sql = [];
  for (const [key, raw] of Object.entries(values)) {
    const r = typeof raw === 'string' ? JSON.parse(raw) : raw;
    if (!r) continue;
    if (key.startsWith('sub:')) {
      sql.push(`INSERT INTO signups (email, interest, source, country, created, updated) VALUES (${q(r.email)}, ${q(r.interest)}, ${q(r.source)}, ${q(r.country)}, ${q(r.created)}, ${q(r.updated || r.created)})`
        + ' ON CONFLICT (email) DO UPDATE SET created = MIN(signups.created, excluded.created), interest = COALESCE(signups.interest, excluded.interest);');
    } else {
      sql.push(`INSERT OR IGNORE INTO enquiries (id, created, name, email, company, message, country) VALUES (${q(key.slice(4))}, ${q(r.created)}, ${q(r.name)}, ${q(r.email)}, ${q(r.company)}, ${q(r.message)}, ${q(r.country)});`);
    }
  }
  const file = join(dir, 'copy.sql');
  writeFileSync(file, sql.join('\n') + '\n');
  wrangler('d1', 'execute', 'kinetiqgym', where, '--file', file, '--yes');
  const [{ results: [now] }] = JSON.parse(wrangler('d1', 'execute', 'kinetiqgym', where, '--json', '--command',
    'SELECT (SELECT count(*) FROM signups) AS signups, (SELECT count(*) FROM enquiries) AS enquiries'));
  const n = p => keys.filter(k => k.startsWith(p)).length;
  console.log(`read ${n('sub:')} signups and ${n('msg:')} enquiries from KV; D1 (${where.slice(2)}) now holds ${now.signups} signups and ${now.enquiries} enquiries`);
} finally {
  rmSync(dir, { recursive: true, force: true });
}
