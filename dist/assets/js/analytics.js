window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','G-T6H1TFBWVS',{anonymize_ip:true});var pdgGs=document.createElement('script');pdgGs.async=true;pdgGs.src='https://www.googletagmanager.com/gtag/js?id=G-T6H1TFBWVS';document.head.appendChild(pdgGs);

function pdgWhere(a){var n=a.closest('[id],header,footer,.mobile-bar,.chat-panel');if(!n)return 'page';if(n.matches('header'))return 'header';if(n.matches('footer'))return 'footer';if(n.matches('.mobile-bar'))return 'mobile_bar';if(n.matches('.chat-panel'))return 'chat';return n.id;}
document.addEventListener('click',function(e){var c=e.target.closest&&e.target.closest('[data-chat-open]');if(c)gtag('event','chat_open',{link_location:pdgWhere(c),page_path:location.pathname});var a=e.target.closest&&e.target.closest('a[href]');if(!a)return;var h=a.getAttribute('href')||'',n=null;
if(/^tel:/i.test(h))n='call_click';else if(/wa\.me\//i.test(h))n='whatsapp_click';else if(/m\.me\//i.test(h))n='messenger_click';else if(/^mailto:/i.test(h))n='email_click';
if(n)gtag('event',n,{link_location:pdgWhere(a),page_path:location.pathname});},true);
document.addEventListener('pdg:track',function(e){var d=e.detail||{};if(d.name)gtag('event',d.name,Object.assign({page_path:location.pathname},d.params||{}));});
