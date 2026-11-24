// رفع الفيديوهات لـ R2 على أجزاء (multipart) — محمي بالهيدر x-key
// ?op=create&key=..  |  ?op=part&key=..&id=..&n=..  (البودي = الجزء)  |  ?op=done&key=..&id=..  (البودي = [{partNumber,etag}])
import { json, isAdmin } from './_lib.js';
export async function onRequestPost({ request, env }) {
  if (!isAdmin(request, env)) return json({ ok: false }, 401);
  if (!env.ACADEMY) return json({ ok: false, msg: 'R2 مش متوصل' }, 503);
  const u = new URL(request.url); const op = u.searchParams.get('op'); const key = (u.searchParams.get('key') || '').replace(/[^a-zA-Z0-9_.\-\/]/g, '');
  if (!key) return json({ ok: false, msg: 'key?' }, 400);
  const ct = key.endsWith('.mp4') ? 'video/mp4' : key.endsWith('.jpg') ? 'image/jpeg' : 'application/octet-stream';
  if (op === 'put') { await env.ACADEMY.put(key, request.body, { httpMetadata: { contentType: ct } }); return json({ ok: true }); }
  if (op === 'create') { const m = await env.ACADEMY.createMultipartUpload(key, { httpMetadata: { contentType: ct } }); return json({ ok: true, id: m.uploadId }); }
  const id = u.searchParams.get('id');
  const m = env.ACADEMY.resumeMultipartUpload(key, id);
  if (op === 'part') { const n = +u.searchParams.get('n'); const p = await m.uploadPart(n, request.body); return json({ ok: true, part: p }); }
  if (op === 'done') { const parts = await request.json(); const o = await m.complete(parts); return json({ ok: true, size: o.size }); }
  if (op === 'abort') { await m.abort(); return json({ ok: true }); }
  return json({ ok: false, msg: 'op?' }, 400);
}
