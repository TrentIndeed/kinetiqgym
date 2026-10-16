'use strict';
const API = '/api/owner/agent-feedback';
const login = document.querySelector('#login');
const inbox = document.querySelector('#inbox');
const status = document.querySelector('#status');
const replies = document.querySelector('#replies');
const more = document.querySelector('#more');
let cursor = null;
let displayed = 0;

async function api(path = '', options = {}) {
  const response = await fetch(API + path, { credentials: 'same-origin', cache: 'no-store', ...options });
  const data = await response.json();
  if (response.status === 401) { login.hidden = false; inbox.hidden = true; }
  if (!response.ok) throw new Error(data.error || 'The request failed.');
  return data;
}
function element(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}
function show(record) {
  const card = document.createElement('article');
  card.append(element('h2', record.agent || 'Unidentified agent'));
  card.append(element('p', `${new Date(record.created).toLocaleString()} · Unverified identity`, 'meta'));
  card.append(element('p', record.message, 'message'));
  if (record.page) card.append(element('p', record.page, 'source'));
  const remove = element('button', 'Delete reply', 'danger');
  remove.type = 'button';
  remove.addEventListener('click', () => perform(remove, async () => {
    if (!window.confirm('Permanently delete this reply?')) return;
    await api('/' + encodeURIComponent(record.id), { method: 'DELETE' });
    card.remove(); displayed--; updateCount();
    status.textContent = 'Reply deleted. Storage may take a minute to reflect the change everywhere.';
  }));
  card.append(remove); replies.append(card); displayed++;
}
function updateCount() { document.querySelector('#count').textContent = `${displayed} ${displayed === 1 ? 'reply' : 'replies'} shown${cursor ? ' · More available' : ''}`; }
async function load(reset = false) {
  const data = await api(reset || !cursor ? '' : '?cursor=' + encodeURIComponent(cursor));
  if (reset) { replies.replaceChildren(); displayed = 0; }
  cursor = data.cursor;
  data.replies.forEach(show);
  login.hidden = true; inbox.hidden = false; more.hidden = !cursor;
  updateCount();
  status.textContent = displayed ? 'Replies are private to this inbox.' : 'No replies yet. The invitation is live; visitors can choose whether to answer.';
}
async function perform(button, action) {
  button.disabled = true;
  try { await action(); } catch (error) { status.textContent = error.message; }
  finally { button.disabled = false; }
}
login.addEventListener('submit', event => {
  event.preventDefault();
  perform(login.querySelector('button'), async () => {
    const input = document.querySelector('#owner-key');
    const key = input.value; input.value = '';
    await api('/session', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ key }) });
    await load(true);
  });
});
document.querySelector('#refresh').addEventListener('click', event => perform(event.currentTarget, () => load(true)));
more.addEventListener('click', () => perform(more, () => load(false)));
document.querySelector('#logout').addEventListener('click', event => perform(event.currentTarget, async () => {
  await api('/session', { method: 'DELETE' });
  replies.replaceChildren(); cursor = null; displayed = 0;
  login.hidden = false; inbox.hidden = true; status.textContent = 'Signed out.';
}));
document.querySelector('#download').addEventListener('click', event => perform(event.currentTarget, async () => {
  const all = []; let next = null;
  do {
    const data = await api(next ? '?cursor=' + encodeURIComponent(next) : '');
    all.push(...data.replies); next = data.cursor;
  } while (next);
  const url = URL.createObjectURL(new Blob([JSON.stringify(all, null, 2)], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = url;
  link.download = `kinetiq-agent-replies-${new Date().toISOString().slice(0, 10)}.json`;
  link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
  status.textContent = `Downloaded ${all.length} replies.`;
}));
load(true).catch(error => { status.textContent = error.message === 'Owner login required.' ? 'Enter your owner access key to view replies.' : error.message; });
