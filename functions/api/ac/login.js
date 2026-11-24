// تسجيل الدخول بالكود: بيسجل الجهاز (لحد max أجهزة) ويحط كوكي جلسة
import { json, getUser, putUser, sign } from './_lib.js';
export async function onRequestPost({ request, env }) {
  let b = {}; try { b = await request.json(); } catch (e) {}
  const code = String(b.code || '').toUpperCase().replace(/\s+/g, '').trim();
  const dev = String(b.dev || '').replace(/[^a-zA-Z0-9]/g, '').slice(0, 40);
  if (!/^RAYL-[A-Z0-9]{4}-[A-Z0-9]{4}$/.test(code) || dev.length < 12) return json({ ok: false, msg: 'الكود مش صحيح' }, 400);
  const u = await getUser(env, code);
  if (!u) return json({ ok: false, msg: 'الكود مش موجود. اتأكد إنك كاتبه صح' }, 404);
  if (!u.active) return json({ ok: false, msg: 'الكود ده متوقف. كلّمنا على صفحة رايل' }, 403);
  u.devices = u.devices || [];
  let d = u.devices.find((x) => x.id === dev);
  if (!d) {
    if (u.devices.length >= (u.max || 2)) return json({ ok: false, msg: `الكود ده مستخدم على ${u.max || 2} أجهزة بالفعل. لو غيّرت جهازك كلّمنا نصفّرهولك` }, 403);
    d = { id: dev, ua: String(b.ua || '').slice(0, 120), at: new Date().toISOString() };
    u.devices.push(d);
  }
  u.last = new Date().toISOString();
  await putUser(env, code, u);
  const val = code + '.' + dev + '.' + (await sign(env, code + '.' + dev));
  return json({ ok: true, name: u.name || '' }, 200, {
    'set-cookie': `ra_s=${encodeURIComponent(val)}; Path=/; Max-Age=31536000; HttpOnly; Secure; SameSite=Lax`,
  });
}
