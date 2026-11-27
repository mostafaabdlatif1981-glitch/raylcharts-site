// بوت الأسئلة @AskRaylBot («اسأل رايل | Ask RAYL»)
// المشترك يكتب سؤاله أو يبعت صورة للبوت ← يوصل في جروب «دعم رايل» في موضوع (Topic) خاص بيه.
// مصطفى يرد جوه الموضوع ← البوت يوصّل الرد للمشترك باسم رايل. الأرقام مخفية في الاتجاهين.
// أي رسالة في الموضوع بتبدأ بـ # ملاحظة داخلية ما بتتبعتش.
// الإعداد في KV (SUBS) تحت ask_cfg: {token, secret, group}. بيتحط من /api/askset (محمي بـ SEND_KEY).

async function tg(cfg, m, p) {
  const r = await fetch(`https://api.telegram.org/bot${cfg.token}/${m}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(p) });
  return r.json();
}
const esc = (s) => String(s || '').replace(/[<&>]/g, c => ({ '<': '&lt;', '&': '&amp;', '>': '&gt;' }[c]));
const fullName = (f) => [f.first_name, f.last_name].filter(Boolean).join(' ') || 'مشترك';

const WELCOME = `أهلاً بيك في <b>اسأل رايل</b> 👋

هنا تقدر تسألنا أي سؤال لوحدك:
• سؤال عن سهم أو عن الشارت
• صورة محفظتك أو شارت عايز رأينا فيه
• أي استفسار عن الاشتراك أو الكورس

اكتب سؤالك أو ابعت الصورة هنا على طول، وهنرد عليك في نفس الشات 🙏

📌 للاشتراك والدفع: @RaylChartsBot
⚠️ المحتوى تعليمي مش توصية.`;

async function logEv(env, ev) {
  const ts = Date.now(); ev.ts = ts; ev.bot = 'ask';
  await env.SUBS.put('ev_' + String(ts).padStart(14, '0') + '_' + Math.random().toString(36).slice(2, 7), JSON.stringify(ev), { expirationTtl: 60 * 60 * 24 * 120 });
}

async function subStatus(env, uid) {
  try {
    const list = JSON.parse((await env.SUBS.get('tg_subs')) || '[]');
    const x = list.filter(a => String(a.uid) === String(uid)).sort((a, b) => b.until - a.until)[0];
    if (!x) return 'مش مشترك';
    const d = new Date(x.until + 2 * 3600e3).toISOString().slice(0, 10);
    return x.removed || x.until < Date.now() ? `اشتراكه خلص (${d})` : `مشترك لحد ${d}`;
  } catch (e) { return '—'; }
}

async function makeTopic(cfg, env, from) {
  const name = fullName(from);
  const label = name.replace(/[\s.\-_]/g, '').length >= 2 ? name : (from.username ? '@' + from.username : 'مشترك ' + from.id);
  const t = await tg(cfg, 'createForumTopic', { chat_id: cfg.group, name: label.slice(0, 120) });
  if (!t.ok) return null;
  const th = t.result.message_thread_id;
  await env.SUBS.put('askt_' + from.id, String(th));
  await env.SUBS.put('askr_' + th, String(from.id));
  const st = await subStatus(env, from.id);
  await tg(cfg, 'sendMessage', {
    chat_id: cfg.group, message_thread_id: th, parse_mode: 'HTML',
    text: `👤 <b>${esc(name)}</b>${from.username ? ' (@' + esc(from.username) + ')' : ''}\nرقم تليجرام: <code>${from.id}</code>\nالاشتراك: ${esc(st)}\n\n✍️ اكتب ردك هنا وهيوصله باسم رايل.\n🔒 أي رسالة تبدأ بـ # ملاحظة ليك انت بس ومش هتتبعت.`,
  });
  return th;
}

async function fromUser(m, cfg, env) {
  const id = m.from.id;
  if (m.text && m.text.startsWith('/start')) {
    await logEv(env, { kind: 'ask_start', uid: id, name: fullName(m.from), user: m.from.username || '' });
    return tg(cfg, 'sendMessage', { chat_id: id, parse_mode: 'HTML', text: WELCOME });
  }
  let th = await env.SUBS.get('askt_' + id);
  if (!th) th = await makeTopic(cfg, env, m.from);
  if (!th) return tg(cfg, 'sendMessage', { chat_id: id, text: 'حصلت مشكلة صغيرة، ابعت سؤالك تاني بعد شوية 🙏' });
  let r = await tg(cfg, 'copyMessage', { chat_id: cfg.group, from_chat_id: id, message_id: m.message_id, message_thread_id: Number(th) });
  if (!r.ok && /thread|topic/i.test(r.description || '')) {
    await env.SUBS.delete('askt_' + id);
    th = await makeTopic(cfg, env, m.from);
    if (th) r = await tg(cfg, 'copyMessage', { chat_id: cfg.group, from_chat_id: id, message_id: m.message_id, message_thread_id: Number(th) });
  }
  await logEv(env, { kind: 'ask_q', uid: id, name: fullName(m.from), user: m.from.username || '', data: (m.text || m.caption || (m.photo ? '[صورة]' : m.document ? '[ملف]' : m.voice ? '[فويس]' : '[رسالة]')).slice(0, 300) });
  // تأكيد واحد بس، مش على كل رسالة (مرة كل 3 ساعات)
  if (!(await env.SUBS.get('aska_' + id))) {
    await env.SUBS.put('aska_' + id, '1', { expirationTtl: 3 * 3600 });
    return tg(cfg, 'sendMessage', { chat_id: id, text: 'وصل سؤالك ✅ وهنرد عليك هنا قريب.' });
  }
}

async function fromAdmin(m, cfg, env) {
  const th = m.message_thread_id;
  if (!th || m.from.is_bot) return;
  if (m.forum_topic_created || m.forum_topic_edited || m.forum_topic_closed || m.forum_topic_reopened || m.new_chat_members || m.left_chat_member || m.pinned_message) return;
  const t = (m.text || m.caption || '').trim();
  if (t.startsWith('#')) return; // ملاحظة داخلية
  const uid = await env.SUBS.get('askr_' + th);
  if (!uid) return;
  const r = await tg(cfg, 'copyMessage', { chat_id: Number(uid), from_chat_id: cfg.group, message_id: m.message_id });
  if (r.ok) {
    await tg(cfg, 'setMessageReaction', { chat_id: cfg.group, message_id: m.message_id, reaction: [{ type: 'emoji', emoji: '👍' }] });
    await env.SUBS.delete('aska_' + uid); // لو سأل تاني بعد الرد ياخد تأكيد جديد
    await logEv(env, { kind: 'ask_a', uid: Number(uid), data: (t || (m.photo ? '[صورة]' : m.voice ? '[فويس]' : '[رسالة]')).slice(0, 300) });
  } else {
    await tg(cfg, 'sendMessage', { chat_id: cfg.group, message_thread_id: th, reply_to_message_id: m.message_id, text: '⚠️ الرد ما وصلش للمشترك: ' + (r.description || '') + (/blocked/i.test(r.description || '') ? '\n(غالبًا قفل البوت)' : '') });
  }
}

export async function onRequestPost({ request, env }) {
  const cfg = JSON.parse((await env.SUBS.get('ask_cfg')) || '{}');
  if (!cfg.token || request.headers.get('x-telegram-bot-api-secret-token') !== cfg.secret) return new Response('no', { status: 403 });
  const u = await request.json();
  try {
    const m = u.message;
    if (m && m.chat) {
      if (m.chat.type === 'private') await fromUser(m, cfg, env);
      else if (String(m.chat.id) === String(cfg.group)) await fromAdmin(m, cfg, env);
    }
  } catch (e) { /* نرجّع 200 عشان تليجرام ما يعيدش */ }
  return new Response('ok');
}
