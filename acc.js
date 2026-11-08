/* RAYL: بطاقات قابلة للفتح والقفل — دوس على العنوان يفتح، دوس تاني يقفل */
(function(){
var st=document.createElement('style');
st.textContent='.acc>h2{cursor:pointer;display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:0}'+
'.acc>h2::after{content:"▼";flex:none;font-size:.55em;color:#15803D;background:#EAF4EA;border:2px solid #15803D;border-radius:50%;width:1.9em;height:1.9em;display:inline-flex;align-items:center;justify-content:center}'+
'.acc.open>h2::after{content:"▲"}'+
'.acc>.accb{display:none;margin-top:10px}.acc.open>.accb{display:block}'+
'.acc{cursor:pointer}.acc>.accb{cursor:auto}';
document.head.appendChild(st);
function toggle(c){c.classList.toggle('open')}
function init(){
  var cards=document.querySelectorAll('main section.card.day, main section.card[id]');
  Array.prototype.forEach.call(cards,function(c){
    var h=c.querySelector('h2'); if(!h||c.getAttribute('data-acc'))return;
    var b=document.createElement('div');b.className='accb';
    var n=h.nextSibling;while(n){var nx=n.nextSibling;b.appendChild(n);n=nx}
    if(!b.childNodes.length)return;
    c.appendChild(b);c.setAttribute('data-acc','1');c.classList.add('acc');
    h.setAttribute('role','button');h.setAttribute('tabindex','0');
    c.addEventListener('click',function(e){
      if(b.contains(e.target))return;
      if(e.target.closest&&e.target.closest('a'))return;
      toggle(c)});
    h.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();toggle(c)}});
  });
  openHash(true);
}
function openHash(first){
  var id=decodeURIComponent((location.hash||'').slice(1));if(!id)return;
  var el=document.getElementById(id);
  if(el&&el.classList.contains('acc')){el.classList.add('open');setTimeout(function(){el.scrollIntoView({behavior:first?'auto':'smooth',block:'start'})},60)}
}
window.addEventListener('hashchange',function(){openHash(false)});
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
