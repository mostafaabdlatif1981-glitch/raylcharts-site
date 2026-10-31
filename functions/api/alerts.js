// آخر تنبيهات الإفصاحات المهمة (لليوم بتوقيت القاهرة) — بيقراها الموقع ويعرضها في مربع «تنبيه هام»
export async function onRequestGet({ env }) {
  const all = JSON.parse((await env.SUBS.get('alerts')) || '[]');
  const today = new Date(Date.now() + 2 * 3600e3).toISOString().slice(0, 10);
  const list = all.filter(a => (a.day || '') === today).slice(0, 5);
  return new Response(JSON.stringify(list), { headers: { 'content-type': 'application/json', 'cache-control': 'no-store' } });
}
