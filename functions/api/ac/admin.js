// إدارة المشتركين والحلقات — محمي بالهيدر x-key
import { json, getUser, putUser, isAdmin, newCode } from './_lib.js';
export async function onRequestPost({ request, env }) {
  if (!isAdmin(request, env)) return json({ ok: false }, 401);
  let b = {}; try { b = await request.json(); } catch (e) {}
  const op = b.op;
  if (op === 'add') {
    let code; for (let i = 0; i < 5; i++) { code = newCode(); if (!(await getUser(env, code))) break; }
    const u = { name: String(b.name || '').slice(0, 80), phone: String(b.phone || '').slice(0, 30), plan: String(b.plan || 'course').slice(0, 20), note: String(b.note || '').slice(0, 200), max: Math.min(5, Math.max(1, +b.max || 2)), devices: [], active: true, created: new Date().toISOString() };
    await putUser(env, code, u);
    return json({ ok: true, code, user: u });
  }
  if (op === 'list') {
    const out = []; let cursor;
    do {
      const r = await env.SUBS.list({ prefix: 'ac:u:', cursor });
      for (const k of r.keys) { const u = JSON.parse((await env.SUBS.get(k.name)) || '{}'); out.push({ code: k.name.slice(5), ...u }); }
      cursor = r.list_complete ? null : r.cursor;
    } while (cursor);
    out.sort((a, b) => (b.created || '').localeCompare(a.created || ''));
    return json({ ok: true, users: out });
  }
  if (['disable', 'enable', 'reset', 'delete', 'setmax'].includes(op)) {
    const code = String(b.code || '').toUpperCase();
    const u = await getUser(env, code);
    if (!u) return json({ ok: false, msg: 'not found' }, 404);
    if (op === 'delete') { await env.SUBS.delete('ac:u:' + code); return json({ ok: true }); }
    if (op === 'disable') u.active = false;
    if (op === 'enable') u.active = true;
    if (op === 'reset') u.devices = [];
    if (op === 'setmax') u.max = Math.min(5, Math.max(1, +b.max || 2));
    await putUser(env, code, u);
    return json({ ok: true, user: u });
  }
  if (op === 'eps') {
    if (Array.isArray(b.eps)) await env.SUBS.put('ac:eps', JSON.stringify(b.eps));
    return json({ ok: true, eps: JSON.parse((await env.SUBS.get('ac:eps')) || '[]') });
  }
  if (op === 'files') {
    if (!env.ACADEMY) return json({ ok: false, msg: 'R2 مش متوصل' }, 503);
    const r = await env.ACADEMY.list({ limit: 1000 });
    return json({ ok: true, files: r.objects.map((o) => ({ key: o.key, size: o.size })) });
  }
  return json({ ok: false, msg: 'op?' }, 400);
}
