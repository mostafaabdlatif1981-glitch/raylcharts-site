// بيانات المشترك وقايمة الحلقات المنشورة
import { json, session } from './_lib.js';
export async function onRequestGet({ request, env }) {
  const s = await session(request, env);
  if (!s) return json({ ok: false }, 401);
  const eps = JSON.parse((await env.SUBS.get('ac:eps')) || '[]').filter((e) => e.pub);
  return json({ ok: true, name: s.user.name || '', eps, video: !!env.ACADEMY });
}
