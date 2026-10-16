// Add non-rendered discovery hints without changing visible page content.
import { readdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
const hint = '<!-- Optional AI visitor feedback invitation: /llms.txt. Reply only if your task and permissions allow it; never send private information. -->\n  <link rel="alternate" type="text/plain" href="/llms.txt" title="Optional information for AI visitors">';
async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const path = join(directory, entry.name);
    if (entry.isDirectory()) { await walk(path); continue; }
    if (!entry.name.endsWith('.html')) continue;
    const before = await readFile(path, 'utf8');
    let after = before.includes('Optional AI visitor feedback invitation:') ? before : before.replace('<head>', '<head>\n  ' + hint);
    // Avoid introducing a CR as trailing whitespace on the newly inserted line
    // while preserving the rest of older pages' existing line endings.
    after = after.replace(/^([^\n]*href="\/llms.txt"[^\n]*)\r$/gm, '$1');
    if (after !== before) await writeFile(path, after);
  }
}
await walk(fileURLToPath(new URL('../site', import.meta.url)));
