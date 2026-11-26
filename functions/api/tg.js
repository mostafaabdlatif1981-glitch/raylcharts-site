// بوت رايل على تليجرام (@RaylChartsBot) — استقبال المشتركين بالأزرار + موافقة مصطفى + لينك دخول لشخص واحد.
// الإعداد في KV (SUBS) تحت المفتاح tg_cfg: {token, admin, channel, secret, instapay}. بيتحط من /api/tgsetup (محمي بـ SEND_KEY).
const PLANS = {
  m: { name: 'اشتراك شهري', price: '300 جنيه', days: 30 },
  y: { name: 'اشتراك سنوي', price: '3,000 جنيه (بدل 3,600)', days: 365 },
  c: { name: 'كورس التحليل الفني فيديو (لوحده)', price: '3,000 جنيه', days: 0, course: true },
  yc: { name: 'اشتراك سنوي + كورس التحليل الفني فيديو', price: '4,500 جنيه (بدل 6,600: 3,000 اشتراك سنوي + الكورس بـ1,500 بدل 3,000)', days: 365 },
};
const START_TS = Date.UTC(2026, 11, 1) - 2 * 3600e3; // 1/12/2026 بتوقيت القاهرة

const SERVICES = `📋 <b>خدمات مشتركين رايل</b> (كلها حصرية للمشتركين)

⚡ <b>تقارير بتفاصيل خاصة</b> للمشتركين بس، وبنشرحها ببساطة: لو حصل كذا ← يبقى كذا.

<b>🌅 قبل الجلسة</b>
1️⃣ نشرة 9:45: إفصاحات امبارح بالليل، الأسهم اللي آخر يوم حق فيها النهارده، وأجندة اليوم

<b>⏱️ أثناء الجلسة</b>
2️⃣ 💰 حركة الكبار: سهم دخل فيه شرا كبير أو خرج منه بيع كبير
3️⃣ 📢 الإفصاحات المهمة أول ما تنزل، والنتايج مع مقارنة مبسطة
4️⃣ 🐋 الصفقات الغريبة: صفقة ضخمة على سهم صغير، تسليم وتسلم، أعضاء مجلس إدارة بيشتروا أو بيبيعوا
5️⃣ 🔔 قبل مزاد الإغلاق: الأسهم اللي الكبار اشتغلوا فيها جامد آخر ساعة

<b>🎯 أسهم للمتابعة والتدريب العملي</b>
6️⃣ لما السوق يطلّع سهم شكله الفني مميز، بنشرحه كدرس عملي (ليه، الدعوم والمقاومات، المستهدفات، المخاطر)، ونتابعه لحد ما يوصل أو يكسر — <b>وكشف حساب علني بالمكسب والخسارة</b>

<b>📌 أسهمك انت</b>
7️⃣ ضيف أسهمك في البوت، ويوصلك كل يوم تنبيه خاص بيها: الشرا كان أكتر ولا البيع ومقارنة بالمتوسط، الكبار، المتوسطات، قرّب من دعم أو مقاومة، وأي إفصاح عليها
8️⃣ 🔍 اسأل عن أي سهم في أي وقت: كارت كامل (آخر شهر، الكبار شهر بشهر، الماكد وRSI والمتوسطات، الدعوم والمقاومات، القطاع، النتايج والإفصاحات، المخاطر) + <b>الخلاصة اللي تهمك</b>

<b>📊 بعد الإقفال كل يوم</b>
9️⃣ أكتر الأسهم طلوعًا ونزولًا • القطاعات اللي الفلوس دخلت فيها وخرجت منها • الأسهم اللي الكبار دخلوا فيها وخرجوا منها • أسهم عالية المخاطرة والسبب بالأرقام • رادار الاختراقات والكسر (متوسط 200، أعلى وأقل سعر في سنة) • رادار الكوبونات والأسهم المجانية • 🎬 فيديو ملخص الجلسة بتفاصيل أكتر • 🛡️ قاعدة اليوم لحماية فلوسك

<b>📅 كل أسبوع</b>
🔟 تقرير السوق الأسبوعي + كشف حساب توقعاتنا • بطاقة كاملة لسهم من اختيارك • جلسة أسئلة وأجوبة

📆 المحتوى بيبدأ ينزل في القناة من 1 ديسمبر 2026 (تنبيه مزاد الإغلاق والصفقات الغريبة من 8 ديسمبر).`;

const PRICES = `💰 <b>الأسعار</b>

🔥 <b>أسعار خاصة لأول 500 مشترك بس</b>
👥 كل مجموعة مشتركين <b>100 مشترك بس</b>، عشان المتابعة تفضل قريبة من كل واحد

• شهري: <b>300 جنيه</b>
• سنوي: <b>3,000 جنيه</b> دفعة واحدة (بدل 3,600 — شهرين ببلاش)
• كورس التحليل الفني فيديو لوحده: <b>3,000 جنيه</b>
• سنوي + كورس التحليل الفني فيديو: <b>4,500 جنيه</b> بدل 6,600 (الكورس بـ1,500 بدل 3,000 — الخصم مع السنوي بس)

اختار الباقة 👇`;

const COURSE = `🎓 <b>كورس التحليل الفني فيديو — أكاديمية رايل</b>

مش نسخة من الكورس الورقي. ده شرح أكبر وأعمق بكتير، بصوت رايل وبالشارتات والسلايدات، وكل مثال على أسهم حقيقية في البورصة المصرية.

🎬 <b>أكتر من 50 حلقة</b> على 3 مستويات (ومش هنختصر حاجة، كل موضوع واخد حقه بالتفصيل)
⏱️ كل حلقة هنحاول ما تزيدش عن <b>10 دقايق</b>، عشان تتفرج وتفهم من غير ما تزهق (أكتر من 8 ساعات شرح في المجمل)
✍️ <b>تدريبات بعد كل حلقة</b> تطبق فيها اللي اتعلمته بإيدك
🏋️ <b>حلقات تدريب كاملة في آخر كل مستوى</b>: شارتات حقيقية تحللها بنفسك، وبعدين نحلها مع بعض
🆓 <b>الحلقة الأولى مجانية</b> للكل

🟢 <b>المبتدئ — من الصفر خالص</b>
• يعني إيه سهم، والشركة بتطرح ليه، والبورصة شغالة إزاي
• الجلسة الاستكشافية والمزاد والإقفال الرسمي
• أول سهم تشتريه خطوة بخطوة على التطبيق
• الأمر المحدد والأمر بسعر السوق، وأوامر الشرا والبيع المتقدمة (وقف الخسارة وجني الربح وصلاحية الأمر)
• الكوبون والأسهم المجانية وزيادة رأس المال، وليه السعر بيتعدل
• السيولة، والشارت وأنواعه، والإطار الزمني، وتشريح الشمعة، والحجم
• إزاي تستخدم TradingView ببلاش من غير اشتراك
• حلقات تدريب على المستوى

🟡 <b>المتوسط — تقرا الشارت بنفسك</b>
• نماذج الشموع كلها، كل نموذج في حلقة لوحده بأكتر من مثال حقيقي
• الاتجاه، والدعم والمقاومة، والاختراق الحقيقي والكاذب
• المتوسطات 20 و50 و100 و200، والتقاطع الذهبي وتقاطع الموت
• النماذج الكلاسيكية (رأس وكتفين، القمم والقيعان المزدوجة، المثلثات والأعلام) والفجوات
• حلقات تدريب على المستوى

🔴 <b>المتقدم — تبني خطة كاملة</b>
• RSI والانحراف، والماكد، وبولينجر وATR، وستوكاستك وADX، وفيبوناتشي
• تحليل سهم من الأول للآخر
• حجم المركز: تشتري كام سهم من غير ما تتحرق
• العائد للمخاطرة والخطة المكتوبة قبل الدخول
• الأخطاء اللي بتضيّع فلوس الناس، وعقلية المتداول
• حلقات تدريب ختامية

📌 كل واحد يبدأ من مستواه: المبتدئ من أول حلقة، واللي عارف الأساسيات من أول المستوى المتوسط، واللي فاهم الشارت من أول المستوى المتقدم.

💰 الكورس لوحده 3,000 جنيه • مع الاشتراك السنوي بـ1,500 بس (الإجمالي 4,500 بدل 6,600)
🔥 أسعار خاصة لأول 500 مشترك بس`;

const kb = (rows) => ({ inline_keyboard: rows });
async function tg(cfg, m, p) {
  const r = await fetch(`https://api.telegram.org/bot${cfg.token}/${m}`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(p) });
  return r.json();
}
const getS = async (env, id) => JSON.parse((await env.SUBS.get('tgu_' + id)) || '{}');
const putS = (env, id, s) => env.SUBS.put('tgu_' + id, JSON.stringify(s));
const esc = (s) => String(s || '').replace(/[<&>]/g, c => ({ '<': '&lt;', '&': '&amp;', '>': '&gt;' }[c]));

function mainMenu() {
  return kb([[{ text: '📋 الخدمات', callback_data: 'svc' }], [{ text: '🎓 تفاصيل كورس التحليل الفني فيديو', callback_data: 'crs' }], [{ text: '💰 الأسعار والاشتراك', callback_data: 'prc' }]]);
}

export async function onRequestPost({ request, env }) {
  const cfg = JSON.parse((await env.SUBS.get('tg_cfg')) || '{}');
  if (!cfg.token || request.headers.get('x-telegram-bot-api-secret-token') !== cfg.secret) return new Response('no', { status: 403 });
  const u = await request.json();
  try { await logEv(env, u); } catch (e) {}
  try { await handle(u, cfg, env); } catch (e) { /* نرجّع 200 عشان تليجرام ما يعيدش */ }
  return new Response('ok');
}


// سجل كل طلب للبوت (قاعدة البيانات على الماك بتسحبه من /api/tglog)
async function logEv(env, u) {
  let ev = null;
  if (u.callback_query) { const q = u.callback_query; ev = { kind: 'button', uid: q.from.id, name: [q.from.first_name, q.from.last_name].filter(Boolean).join(' '), user: q.from.username || '', data: q.data || '' }; }
  else if (u.message && u.message.chat && u.message.chat.type === 'private') {
    const m = u.message, t = (m.text || '').trim();
    let kind = 'text', data = '';
    if (t.startsWith('/')) { kind = 'command'; data = t.slice(0, 40); }
    else if (/^[A-Za-z]{3,6}$/.test(t)) { kind = 'ask_stock'; data = t.toUpperCase(); }
    else if (m.photo || m.document) { kind = 'receipt'; }
    else if (m.contact) { kind = 'contact'; }
    else { data = t.slice(0, 200); }
    ev = { kind, uid: m.from.id, name: [m.from.first_name, m.from.last_name].filter(Boolean).join(' '), user: m.from.username || '', data };
  }
  if (!ev) return;
  const ts = Date.now(); ev.ts = ts;
  await env.SUBS.put('ev_' + String(ts).padStart(14, '0') + '_' + Math.random().toString(36).slice(2, 7), JSON.stringify(ev), { expirationTtl: 60 * 60 * 24 * 120 });
}


async function sendReq(cfg, env, id, s) {
  const plan = PLANS[s.plan] || PLANS.m;
  const cap = `🆕 <b>وصل تحويل</b>\n\nالباقة: <b>${plan.name}</b>\nالمبلغ: ${plan.price}\nالاسم: ${esc(s.name)}${s.username ? ' (@' + esc(s.username) + ')' : ''}\nرقم تليجرام: ${id}\nالرقم: ${s.phone ? esc(s.phone) : '⏳ لسه بيبعته'}\n\nراجع وصول الفلوس الأول 👇`;
  const rm = kb([[{ text: '✅ الفلوس وصلت', callback_data: 'ok_' + id }, { text: '❌ مش واصلة', callback_data: 'no_' + id }]]);
  const r = s.receipt.t === 'photo' ? await tg(cfg, 'sendPhoto', { chat_id: cfg.admin, photo: s.receipt.f, caption: cap, parse_mode: 'HTML', reply_markup: rm }) : await tg(cfg, 'sendDocument', { chat_id: cfg.admin, document: s.receipt.f, caption: cap, parse_mode: 'HTML', reply_markup: rm });
  if (r && r.ok) { s.adminMsg = r.result.message_id; await putS(env, id, s); }
  return r;
}

async function handle(u, cfg, env) {
  if (u.callback_query) {
    const q = u.callback_query, from = q.from, chat = q.message.chat.id, d = q.data || '';
    await tg(cfg, 'answerCallbackQuery', { callback_query_id: q.id });
    // أزرار مصطفى على الطلبات
    if (d.startsWith('ok_') || d.startsWith('no_')) {
      if (String(from.id) !== String(cfg.admin)) return;
      const uid = d.slice(3); const s = await getS(env, uid);
      if (d.startsWith('ok_')) {
        if (s.approved) return;
        const plan = PLANS[s.plan] || PLANS.m;
        if (plan.course && !plan.days) {
          s.approved = Date.now(); await putS(env, uid, s);
          const cl = JSON.parse((await env.SUBS.get('tg_course')) || '[]'); cl.push({ uid, at: Date.now(), name: s.name || '', phone: s.phone || '' }); await env.SUBS.put('tg_course', JSON.stringify(cl));
          await tg(cfg, 'sendMessage', { chat_id: uid, parse_mode: 'HTML', text: `✅ <b>تم تسجيلك في كورس التحليل الفني فيديو</b>\n\nهنبعتلك هنا في البوت بيانات الدخول لصفحة الكورس على raylcharts.com، وكل حلقة أول ما تنزل.\n\nلو حبيت بعدين تضيف اشتراك رايل برو، دوس /start.` });
          await tg(cfg, 'editMessageCaption', { chat_id: chat, message_id: q.message.message_id, parse_mode: 'HTML', caption: (q.message.caption || '') + '\n\n✅ اتسجل في الكورس' });
          return;
        }
        const start = Math.max(Date.now(), START_TS);
        const until = start + plan.days * 86400e3;
        const link = await tg(cfg, 'createChatInviteLink', { chat_id: cfg.channel, name: ('u' + uid).slice(0, 32), member_limit: 1, expire_date: Math.floor(Date.now() / 1000) + 3 * 86400 });
        if (!link.ok) { await tg(cfg, 'sendMessage', { chat_id: cfg.admin, text: '⚠️ ما قدرتش أعمل لينك: ' + (link.description || '') }); return; }
        s.approved = Date.now(); s.until = until; s.link = link.result.invite_link; await putS(env, uid, s);
        const list = JSON.parse((await env.SUBS.get('tg_subs')) || '[]'); list.push({ uid, plan: s.plan, until, name: s.name || '', phone: s.phone || '' }); await env.SUBS.put('tg_subs', JSON.stringify(list));
        const untilStr = new Date(until + 2 * 3600e3).toISOString().slice(0, 10);
        await tg(cfg, 'sendMessage', { chat_id: uid, parse_mode: 'HTML', text: `✅ <b>تم تفعيل اشتراكك في رايل</b>\n\nالباقة: ${plan.name}\nسارية لحد: ${untilStr}\n\nده لينك دخول القناة 👇 (ليك انت بس، بيشتغل مرة واحدة، وصالح 3 أيام)\n${s.link}${s.plan === 'yc' ? '\n\n🎓 هنبعتلك تفاصيل كورس التحليل الفني قريب.' : ''}` });
        await tg(cfg, 'editMessageCaption', { chat_id: chat, message_id: q.message.message_id, parse_mode: 'HTML', caption: (q.message.caption || '') + `\n\n✅ اتفعّل لحد ${untilStr}` });
      } else {
        s.rejected = Date.now(); await putS(env, uid, s);
        await tg(cfg, 'sendMessage', { chat_id: uid, text: '⏳ لسه التحويل ما وصلش لحسابنا. لو حوّلت فعلاً استنى شوية وابعت صورة الوصل تاني هنا، أو تواصل معانا.' });
        await tg(cfg, 'editMessageCaption', { chat_id: chat, message_id: q.message.message_id, caption: (q.message.caption || '') + '\n\n❌ اتقاله إن الفلوس ما وصلتش' });
      }
      return;
    }
    if (d === 'svc') return tg(cfg, 'sendMessage', { chat_id: chat, parse_mode: 'HTML', text: SERVICES, reply_markup: kb([[{ text: '🎓 تفاصيل الكورس', callback_data: 'crs' }], [{ text: '💰 الأسعار والاشتراك', callback_data: 'prc' }]]) });
    if (d === 'crs') return tg(cfg, 'sendMessage', { chat_id: chat, parse_mode: 'HTML', text: COURSE, reply_markup: kb([[{ text: '🎬 اشترك في الكورس لوحده — 3,000', callback_data: 'p_c' }], [{ text: '🎓 سنوي + الكورس — 4,500', callback_data: 'p_yc' }], [{ text: '💰 كل الأسعار', callback_data: 'prc' }], [{ text: '📋 الخدمات', callback_data: 'svc' }]]) });
    if (d === 'prc') return tg(cfg, 'sendMessage', { chat_id: chat, parse_mode: 'HTML', text: PRICES, reply_markup: kb([[{ text: '📅 شهري — 300', callback_data: 'p_m' }], [{ text: '🗓️ سنوي — 3,000', callback_data: 'p_y' }], [{ text: '🎬 الكورس لوحده — 3,000', callback_data: 'p_c' }], [{ text: '🎓 سنوي + الكورس — 4,500', callback_data: 'p_yc' }], [{ text: '🎓 تفاصيل الكورس', callback_data: 'crs' }]]) });
    if (d.startsWith('p_')) {
      const k = d.slice(2); if (!PLANS[k]) return; const s = await getS(env, from.id); s.plan = k; s.step = 'terms'; await putS(env, from.id, s);
      return tg(cfg, 'sendMessage', { chat_id: chat, parse_mode: 'HTML', text: `اخترت: <b>${PLANS[k].name}</b> — ${PLANS[k].price}\n\n⚠️ <b>قبل التحويل:</b> ${PLANS[k].course && !PLANS[k].days ? 'الكورس' : 'الاشتراك'} مفيهوش إلغاء ولا استرجاع بعد الدفع.`, reply_markup: kb([[{ text: '✅ موافق', callback_data: 'agree' }], [{ text: '↩️ رجوع للأسعار', callback_data: 'prc' }]]) });
    }
    if (d === 'agree') {
      const s = await getS(env, from.id); if (!s.plan) return; s.step = 'receipt'; s.agreed = Date.now(); await putS(env, from.id, s);
      return tg(cfg, cfg.qr ? 'sendPhoto' : 'sendMessage', { chat_id: chat, parse_mode: 'HTML', ...(cfg.qr ? { photo: cfg.qr } : {}), [cfg.qr ? 'caption' : 'text']: `💳 <b>طريقة الدفع</b>\n\nحوّل <b>${PLANS[s.plan].price.split(' (')[0]}</b> على إنستاباي (الأفضل لأنه بيوصل فورًا):\n${cfg.instapay || '—'}\n\n📸 بعد التحويل <b>ابعت صورة الوصل هنا</b> في الشات.\n\n🔒 لينك القناة بيتبعتلك بعد ما المبلغ يوصل ونتأكد منه، مش بمجرد الصورة.` });
    }
    return;
  }

  const m = u.message; if (!m || m.chat.type !== 'private') return;
  const id = m.from.id;
  if (m.text && m.text.startsWith('/start')) {
    return tg(cfg, 'sendMessage', { chat_id: id, parse_mode: 'HTML', text: `أهلاً بيك في <b>رايل | RAYL</b> 👋\n\nاختار من الأزرار تحت عشان تعرف الخدمات والأسعار وتشترك.`, reply_markup: mainMenu() });
  }
  if (m.text && /^\s*[A-Za-z]{3,6}\s*$/.test(m.text)) {
    const sym = m.text.trim().toUpperCase();
    return tg(cfg, 'sendMessage', { chat_id: id, parse_mode: 'HTML', text: `🃏 <b>اسأل عن سهم — ${esc(sym)}</b>\n\nالخدمة دي للمشتركين بس، وهتشتغل في نفس البوت ده من <b>1 ديسمبر</b>: تبعت رمز السهم، ويوصلك كارت كامل بالأرقام (آخر شهر، الكبار شهر بشهر، المتوسطات والماكد وRSI، الدعوم والمقاومات، النتايج والإفصاحات) و<b>الخلاصة اللي تهمك</b>.\n\nلو لسه ما اشتركتش 👇`, reply_markup: mainMenu() });
  }
  const s = await getS(env, id);
  if (m.photo || (m.document && /image|pdf/.test(m.document.mime_type || ''))) {
    if (!s.plan || !s.agreed) return tg(cfg, 'sendMessage', { chat_id: id, text: 'اختار الباقة الأول من الأزرار 👇', reply_markup: mainMenu() });
    s.receipt = m.photo ? { t: 'photo', f: m.photo[m.photo.length - 1].file_id } : { t: 'doc', f: m.document.file_id };
    s.step = 'phone'; s.name = [m.from.first_name, m.from.last_name].filter(Boolean).join(' '); s.username = m.from.username || '';
    // يوصل لمصطفى فورًا أول ما الصورة توصل
    const plan0 = PLANS[s.plan];
    const cap0 = `🆕 <b>وصل تحويل جديد</b>\n\nالباقة: <b>${plan0.name}</b>\nالمبلغ: ${plan0.price}\nالاسم: ${esc(s.name)}${s.username ? ' (@' + esc(s.username) + ')' : ''}\nرقم تليجرام: ${id}\nالرقم: ⏳ لسه بيبعته\n\nراجع وصول الفلوس الأول 👇`;
    const rm0 = kb([[{ text: '✅ الفلوس وصلت', callback_data: 'ok_' + id }, { text: '❌ مش واصلة', callback_data: 'no_' + id }]]);
    const r0 = s.receipt.t === 'photo' ? await tg(cfg, 'sendPhoto', { chat_id: cfg.admin, photo: s.receipt.f, caption: cap0, parse_mode: 'HTML', reply_markup: rm0 }) : await tg(cfg, 'sendDocument', { chat_id: cfg.admin, document: s.receipt.f, caption: cap0, parse_mode: 'HTML', reply_markup: rm0 });
    s.adminMsg = r0 && r0.ok ? r0.result.message_id : null; s.sent = Date.now();
    await putS(env, id, s);
    return tg(cfg, 'sendMessage', { chat_id: id, text: '👍 وصلت صورة الوصل. دوس الزرار تحت عشان تبعت رقمك (بكود دولتك أوتوماتيك) 👇', reply_markup: { keyboard: [[{ text: '📱 ابعت رقمي', request_contact: true }]], resize_keyboard: true, one_time_keyboard: true } });
  }
  if (!m.contact && m.text && s.receipt && !s.phone && /^\s*\+?[\d\s-]{8,16}\s*$/.test(m.text)) {
    m.contact = { phone_number: m.text.replace(/[^\d+]/g, ''), user_id: id };
  }
  if (m.contact) {
    if (m.contact.user_id && m.contact.user_id !== id) return tg(cfg, 'sendMessage', { chat_id: id, text: 'ابعت رقمك انت من الزرار 📱' });
    if (!s.receipt) return tg(cfg, 'sendMessage', { chat_id: id, text: 'ابعت صورة الوصل الأول 📸', reply_markup: { remove_keyboard: true } });
    s.phone = '+' + String(m.contact.phone_number).replace(/^\+/, ''); s.step = 'review'; await putS(env, id, s);
    await tg(cfg, 'sendMessage', { chat_id: id, text: '✅ طلبك وصل. هنراجع التحويل ونبعتلك لينك القناة هنا أول ما المبلغ يوصل. شكرًا لثقتك 🙏', reply_markup: { remove_keyboard: true } });
    if (!s.adminMsg) return sendReq(cfg, env, id, s);
    return tg(cfg, 'sendMessage', { chat_id: cfg.admin, parse_mode: 'HTML', text: `📱 رقم ${esc(s.name)}: <b>${esc(s.phone)}</b>`, ...(s.adminMsg ? { reply_to_message_id: s.adminMsg } : {}) });
  }
  if (m.text && String(id) !== String(cfg.admin)) await tg(cfg, 'sendMessage', { chat_id: cfg.admin, parse_mode: 'HTML', text: `💬 <b>رسالة للبوت</b> من ${esc([m.from.first_name, m.from.last_name].filter(Boolean).join(' '))}${m.from.username ? ' (@' + esc(m.from.username) + ')' : ''}:\n${esc(m.text.slice(0, 500))}` });
  return tg(cfg, 'sendMessage', { chat_id: id, text: 'استخدم الأزرار تحت 👇', reply_markup: mainMenu() });
}

// GET /api/tg?expire=1 (هيدر x-key = SEND_KEY): يطلّع اللي اشتراكهم خلص
export async function onRequestGet({ request, env }) {
  if (!env.SEND_KEY || request.headers.get('x-key') !== env.SEND_KEY) return new Response('no', { status: 403 });
  const cfg = JSON.parse((await env.SUBS.get('tg_cfg')) || '{}');
  const nu = new URL(request.url).searchParams.get('notify');
  if (nu) { const s = await getS(env, nu); if (!s.receipt) return new Response(JSON.stringify({ ok: false, step: s.step || null, plan: s.plan || null })); const r = await sendReq(cfg, env, nu, s); return new Response(JSON.stringify({ ok: !!(r && r.ok), phone: !!s.phone })); }
  const list = JSON.parse((await env.SUBS.get('tg_subs')) || '[]');
  const now = Date.now(); let n = 0;
  for (const x of list) {
    if (x.until < now && !x.removed) {
      await tg(cfg, 'banChatMember', { chat_id: cfg.channel, user_id: Number(x.uid) });
      await tg(cfg, 'unbanChatMember', { chat_id: cfg.channel, user_id: Number(x.uid), only_if_banned: true });
      await tg(cfg, 'sendMessage', { chat_id: Number(x.uid), text: '⏰ اشتراكك في رايل خلص. لو حابب تجدد دوس /start واختار الباقة.' });
      x.removed = now; n++;
    }
  }
  await env.SUBS.put('tg_subs', JSON.stringify(list));
  return Response.json({ removed: n, total: list.length, active: list.filter(x => !x.removed).length });
}
