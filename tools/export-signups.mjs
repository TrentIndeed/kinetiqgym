// Export the build list and project enquiries from Workers KV to CSV (uses your logged-in wrangler).
//   node tools/export-signups.mjs            -> signups.csv, enquiries.csv in the current folder
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const wr = (...a) => execFileSync(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['-y', 'wrangler@4', 'kv', ...a, '--binding', 'SIGNUPS', '--remote'], { encoding: 'utf8', shell: process.platform === 'win32' });
const keys = JSON.parse(wr('key', 'list')).map(k => k.name);
const get = k => JSON.parse(wr('key', 'get', k));
const csv = rows => rows.map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n') + '\n';
const subs = keys.filter(k => k.startsWith('sub:')).map(get);
const msgs = keys.filter(k => k.startsWith('msg:')).map(get);
writeFileSync('signups.csv', csv([['email', 'interest', 'created', 'updated', 'source', 'country'], ...subs.map(s => [s.email, s.interest, s.created, s.updated, s.source, s.country])]));
writeFileSync('enquiries.csv', csv([['created', 'name', 'email', 'company', 'message', 'country'], ...msgs.map(m => [m.created, m.name, m.email, m.company, m.message, m.country])]));
console.log(`${subs.length} signups, ${msgs.length} enquiries written`);
