// يبعت إشعار لكل المشتركين. محمي بـ SEND_KEY. يحتاج FCM_SA (ملف service account كامل كنص JSON) و SUBS (KV).
const b64u = (buf) => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const enc = (o) => b64u(new TextEncoder().encode(JSON.stringify(o)));
async function accessToken(sa) {
  const now = Math.floor(Date.now() / 1000);
  const unsigned = enc({ alg: 'RS256', typ: 'JWT' }) + '.' + enc({ iss: sa.client_email, scope: 'https://www.googleapis.com/auth/firebase.messaging', aud: 'https://oauth2.googleapis.com/token', iat: now, exp: now + 3600 });
  const pem = sa.private_key.replace(/-----[^-]+-----/g, '').replace(/\s+/g, '');
  const der = Uint8Array.from(atob(pem), c => c.charCodeAt(0));
  const key = await crypto.subtle.importKey('pkcs8', der, { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' }, false, ['sign']);
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(unsigned));
  const r = await fetch('https://oauth2.googleapis.com/token', { method: 'POST', headers: { 'content-type': 'application/x-www-form-urlencoded' }, body: 'grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Ajwt-bearer&assertion=' + unsigned + '.' + b64u(sig) });
  const j = await r.json(); if (!j.access_token) throw new Error('oauth ' + JSON.stringify(j)); return j.access_token;
}
export async function onRequestPost({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  const m = await request.json();
  if (m.remove_alert) { const all = JSON.parse((await env.SUBS.get('alerts')) || '[]').filter(x => x.id !== String(m.remove_alert)); await env.SUBS.put('alerts', JSON.stringify(all)); return Response.json({ removed: m.remove_alert }); }
  // تنبيه إفصاح مهم: يتحفظ عشان يظهر في مربع «تنبيه هام» على الموقع
  if (m.alert) {
    const a = m.alert; const day = new Date(Date.now() + 2 * 3600e3).toISOString().slice(0, 10);
    const item = { id: String(a.id || Date.now()), day, time: String(a.time || ''), sym: String(a.sym || ''), company: String(a.company || ''), kind: String(a.kind || 'إفصاح'), text: String(a.text || '') };
    const all = JSON.parse((await env.SUBS.get('alerts')) || '[]').filter(x => x.id !== item.id);
    all.unshift(item); await env.SUBS.put('alerts', JSON.stringify(all.slice(0, 30)));
    m.title = m.title || `📣 تنبيه هام: ${item.company}${item.sym ? ' (' + item.sym + ')' : ''}`;
    m.body = m.body || `${item.time ? item.time + ' • ' : ''}${item.text}`;
    m.tag = m.tag || 'alert-' + item.id; m.url = m.url || ('https://raylcharts.com/#alert=' + encodeURIComponent(JSON.stringify(item)));
    if (m.alert_only) return Response.json({ saved: item.id });
  }
  const sa = JSON.parse(env.FCM_SA); const at = await accessToken(sa);
  const data = { title: String(m.title || 'RAYL'), body: String(m.body || ''), url: String(m.url || 'https://raylcharts.com/'), tag: String(m.tag || '') };
  let cursor, sent = 0, dead = 0, fail = 0;
  do {
    const page = await env.SUBS.list({ prefix: 't:', cursor }); cursor = page.list_complete ? null : page.cursor;
    await Promise.all(page.keys.map(async k => {
      const token = k.name.slice(2);
      const r = await fetch(`https://fcm.googleapis.com/v1/projects/${sa.project_id}/messages:send`, { method: 'POST', headers: { authorization: 'Bearer ' + at, 'content-type': 'application/json' }, body: JSON.stringify({ message: { token, data, webpush: { headers: { Urgency: 'high', TTL: '86400' } } } }) });
      if (r.ok) sent++; else if (r.status === 404 || r.status === 400) { dead++; await env.SUBS.delete(k.name); } else fail++;
    }));
  } while (cursor);
  return Response.json({ sent, dead, fail });
}
export async function onRequestGet({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  let n = 0, cursor; do { const p = await env.SUBS.list({ prefix: 't:', cursor }); n += p.keys.length; cursor = p.list_complete ? null : p.cursor; } while (cursor);
  return Response.json({ subscribers: n });
}
