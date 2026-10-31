// RAYL — تفعيل الإشعارات (Firebase Cloud Messaging)
(function(){
  var CFG={apiKey:"AIzaSyDH36M3JbgwsIyaPbphM8asBKjYO3B8P9I",authDomain:"rayl-app.firebaseapp.com",projectId:"rayl-app",storageBucket:"rayl-app.firebasestorage.app",messagingSenderId:"777146388506",appId:"1:777146388506:web:9f41683d996c4750aa41a3"};
  var VAPID="BNwUX3ZGT67w4rWo9tXu5GPiD8gk-nJzCsuvW5H0TUrqkU5eyGOiPzZePBITjMfMFSBAU_nPgAizEXVSeQafpnE";
  var V='10.12.2';
  if(!('serviceWorker' in navigator)||!('Notification' in window)||!('PushManager' in window))return;
  function ld(src){return new Promise(function(ok,no){var s=document.createElement('script');s.src=src;s.onload=ok;s.onerror=no;document.head.appendChild(s)})}
  var btn=document.getElementById('pushbtn'); if(!btn)return;
  var done=false;try{done=localStorage.getItem('rayl_push')==='1'}catch(e){}
  if(Notification.permission==='denied'){btn.style.display='none';return}
  if(done&&Notification.permission==='granted'){btn.textContent='🔔 الإشعارات شغالة';btn.classList.add('on');}
  btn.style.display='inline-flex';
  async function enable(){
    btn.textContent='⏳ لحظة…';
    try{
      var p=await Notification.requestPermission();
      if(p!=='granted'){btn.textContent='🔕 الإشعارات مقفولة من المتصفح';return}
      var reg=await navigator.serviceWorker.register('sw.js'); await navigator.serviceWorker.ready;
      await ld('https://www.gstatic.com/firebasejs/'+V+'/firebase-app-compat.js');
      await ld('https://www.gstatic.com/firebasejs/'+V+'/firebase-messaging-compat.js');
      if(!firebase.apps.length)firebase.initializeApp(CFG);
      var tok=await firebase.messaging().getToken({vapidKey:VAPID,serviceWorkerRegistration:reg});
      if(!tok)throw new Error('no token');
      var r=await fetch('/api/subscribe',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({token:tok,ua:navigator.userAgent.slice(0,120)})});
      if(!r.ok)throw new Error('save '+r.status);
      try{localStorage.setItem('rayl_push','1')}catch(e){}
      btn.textContent='🔔 الإشعارات شغالة';btn.classList.add('on');
    }catch(e){console.log('push',e);btn.textContent='⚠️ حصلت مشكلة، جرّب تاني'}
  }
  btn.onclick=enable;
  // لو مفعّلة قبل كده: جدّد التوكن بهدوء
  if(done&&Notification.permission==='granted'){setTimeout(function(){enable().catch(function(){})},4000)}
})();
