// Export the build list and project enquiries from D1 to CSV (uses your logged-in wrangler).
//   node tools/export-signups.mjs            -> signups.csv, enquiries.csv in the current folder
import { execFileSync } from 'node:child_process';
import { writeFileSync } from 'node:fs';
const win = process.platform === 'win32';
const quote = a => (win && /[\s,()*]/.test(a) ? `"${a}"` : a);              // npx.cmd runs through the shell on Windows
const rows = sql => {
  const out = execFileSync(win ? 'npx.cmd' : 'npx', ['-y', 'wrangler@4', 'd1', 'execute', 'kinetiqgym', '--remote', '--json', '--command', sql].map(quote),
    { encoding: 'utf8', shell: win, maxBuffer: 64e6 });
  return JSON.parse(out.slice(out.indexOf('[')))[0].results;
};
const csv = list => list.map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')).join('\n') + '\n';
const subs = rows('SELECT email, interest, created, updated, source, country FROM signups ORDER BY created');
const msgs = rows('SELECT created, name, email, company, message, country FROM enquiries ORDER BY created');
writeFileSync('signups.csv', csv([['email', 'interest', 'created', 'updated', 'source', 'country'], ...subs.map(s => [s.email, s.interest, s.created, s.updated, s.source, s.country])]));
writeFileSync('enquiries.csv', csv([['created', 'name', 'email', 'company', 'message', 'country'], ...msgs.map(m => [m.created, m.name, m.email, m.company, m.message, m.country])]));
console.log(`${subs.length} signups, ${msgs.length} enquiries written`);
