// GET /api/tglog?after=<key> — سحب سجل طلبات البوت لقاعدة بيانات الماك (بمفتاح x-key)
export async function onRequestGet({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  const url = new URL(request.url); const after = url.searchParams.get('after') || '';
  const out = []; let cursor; let done = false;
  while (!done && out.length < 900) {
    const r = await env.SUBS.list({ prefix: 'ev_', cursor, limit: 1000 });
    for (const k of r.keys) { if (k.name > after) { const v = await env.SUBS.get(k.name); if (v) out.push({ key: k.name, ...JSON.parse(v) }); if (out.length >= 900) break; } }
    if (r.list_complete) done = true; else cursor = r.cursor;
  }
  return new Response(JSON.stringify({ n: out.length, events: out }), { headers: { 'content-type': 'application/json; charset=utf-8' } });
}
