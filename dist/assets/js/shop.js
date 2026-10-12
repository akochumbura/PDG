(function(){
var KEY='pdg_cart',cart={};try{cart=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){cart={}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(cart))}catch(e){}}
function fmt(n){return '\u20be'+n.toLocaleString('en-US')}
function tot(){var t=0,c=0;for(var k in cart){t+=cart[k].p*cart[k].q;c+=cart[k].q}return[t,c]}
var badge=document.getElementById('cartCount'),dlg=document.getElementById('cart');
function lb(id){var e=document.getElementById(id);return e?e.textContent:''}
function render(){var T=tot();if(badge){badge.textContent=T[1];badge.hidden=!T[1]}
if(!dlg)return;var list=document.getElementById('cartList');list.textContent='';var keys=Object.keys(cart);
document.getElementById('cartEmpty').hidden=keys.length>0;document.getElementById('cartFoot').hidden=!keys.length;
keys.forEach(function(k){var it=cart[k],li=document.createElement('li');
function b(txt,fn,al){var x=document.createElement('button');x.type='button';x.textContent=txt;x.onclick=fn;if(al)x.setAttribute('aria-label',al);return x}
var nm=document.createElement('span');nm.className='ci-name';nm.textContent=it.n;
var q=document.createElement('span');q.className='ci-qty';q.append(b('\u2212',function(){change(k,-1)},'-'),document.createTextNode(' '+it.q+' '),b('+',function(){change(k,1)},'+'));
var pr=document.createElement('span');pr.className='ci-price';pr.textContent=fmt(it.p*it.q);
li.append(nm,q,pr,b('\u00d7',function(){delete cart[k];save();render()},lb('lbRemove')));list.appendChild(li)});
document.getElementById('cartTotal').textContent=fmt(T[0]);
var lines=keys.map(function(k){return '- '+cart[k].n+' ('+k+') x'+cart[k].q+' = '+fmt(cart[k].p*cart[k].q)}),msg='PDG '+lb('lbOrder')+':\n'+lines.join('\n')+'\n'+document.querySelector('.cart-total span').textContent+': '+fmt(T[0]);
window.PDG_MSG=function(){var f=document.getElementById('cartForm'),c=f?'\n'+f.name.value.trim()+', '+f.phone.value.trim()+(f.address.value.trim()?', '+f.address.value.trim():''):'';return msg+c};var pay=document.getElementById('cartPay');if(pay)pay.hidden=!(window.PDG_PAY&&window.PDG_PAY.endpoint);var ml=document.getElementById('cartMail');if(ml)ml.href='mailto:info@premium-drones.ge?subject='+encodeURIComponent('PDG '+lb('lbOrder'))+'&body='+encodeURIComponent(msg)}
function change(k,d){cart[k].q+=d;if(cart[k].q<1)delete cart[k];save();render()}
function open(){if(dlg&&dlg.showModal&&!dlg.open)dlg.showModal()}
document.addEventListener('click',function(e){var a=e.target.closest('.add-btn');if(a){var k=a.dataset.sku;cart[k]=cart[k]||{n:a.dataset.name,p:+a.dataset.price,q:0};cart[k].q++;save();render();a.classList.add('is-added');setTimeout(function(){a.classList.remove('is-added')},900);return}
var c=e.target.closest('.cart-link');if(c&&dlg){e.preventDefault();open()}
if(e.target===dlg||e.target.id==='cartClose')dlg.close()});
var form=document.getElementById('cartForm');
if(form){function ok(){var e=document.getElementById('cartError'),v=form.name.value.trim()&&form.phone.value.trim().length>=7;e.hidden=!!v;return !!v}
function order(){return{items:Object.keys(cart).map(function(k){return{sku:k,name:cart[k].n,qty:cart[k].q,price:cart[k].p}}),total:tot()[0],currency:'GEL',lang:document.documentElement.lang,customer:{name:form.name.value.trim(),phone:form.phone.value.trim(),address:form.address.value.trim()}}}
form.addEventListener('submit',function(e){e.preventDefault();if(!ok()||!Object.keys(cart).length)return;window.open('https://wa.me/995550004333?text='+encodeURIComponent(window.PDG_MSG()),'_blank','noopener')});
document.getElementById('cartMail').addEventListener('click',function(e){if(!ok()){e.preventDefault();return}this.href=this.href.split('&body=')[0]+'&body='+encodeURIComponent(window.PDG_MSG())});
document.getElementById('cartPay').addEventListener('click',function(){if(!ok())return;fetch(window.PDG_PAY.endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(order())}).then(function(r){return r.json()}).then(function(d){if(d&&d.url)location.href=d.url;else throw 0}).catch(function(){var e=document.getElementById('cartError');e.hidden=false})})}
if(location.hash==='#cart')open();render();
var have=window.PDG_PHOTOS||[];document.querySelectorAll('.product-photo img[data-photo]').forEach(function(im){var sku=im.dataset.photo.split('/').pop().replace('.webp','');if(have.indexOf(sku)<0)return;var p=new Image();p.onload=function(){im.src=im.dataset.photo;im.style.objectPosition='50% 50%'};p.src=im.dataset.photo});
var q=document.getElementById('partSearch');if(!q)return;var chips=document.querySelectorAll('#partChips .chip'),cards=document.querySelectorAll('#partsGrid .product'),cat='all';
function run(){var s=(q.value||'').trim().toLowerCase();cards.forEach(function(r){r.hidden=!((cat==='all'||r.dataset.cat===cat)&&(!s||r.textContent.toLowerCase().indexOf(s)>-1))})}
q.addEventListener('input',run);chips.forEach(function(c){c.addEventListener('click',function(){cat=c.dataset.filter;chips.forEach(function(o){o.classList.toggle('is-on',o===c)});run()})})})();
