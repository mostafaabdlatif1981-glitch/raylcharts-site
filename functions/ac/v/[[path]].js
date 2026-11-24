// تشغيل فيديوهات الأكاديمية من R2 للمشتركين بس (مع دعم Range للتقديم والتأخير)
import { session } from '../../api/ac/_lib.js';
export async function onRequestGet({ request, env, params }) {
  const s = await session(request, env);
  if (!s) return new Response('محتاج تسجيل دخول', { status: 401 });
  if (!env.ACADEMY) return new Response('الفيديوهات لسه بتتجهز', { status: 503 });
  const key = [].concat(params.path || []).join('/');
  const range = request.headers.get('range');
  let opts = {};
  if (range) {
    const m = range.match(/bytes=(\d*)-(\d*)/);
    if (m) {
      const head = await env.ACADEMY.head(key);
      if (!head) return new Response('مش موجود', { status: 404 });
      const start = m[1] ? +m[1] : head.size - +m[2];
      const end = m[2] && m[1] ? +m[2] : head.size - 1;
      opts.range = { offset: start, length: end - start + 1 };
      const obj = await env.ACADEMY.get(key, opts);
      return new Response(obj.body, { status: 206, headers: { 'content-type': head.httpMetadata?.contentType || 'video/mp4', 'content-range': `bytes ${start}-${end}/${head.size}`, 'content-length': String(end - start + 1), 'accept-ranges': 'bytes', 'cache-control': 'private, no-store' } });
    }
  }
  const obj = await env.ACADEMY.get(key);
  if (!obj) return new Response('مش موجود', { status: 404 });
  return new Response(obj.body, { headers: { 'content-type': obj.httpMetadata?.contentType || 'video/mp4', 'content-length': String(obj.size), 'accept-ranges': 'bytes', 'cache-control': 'private, no-store' } });
}
