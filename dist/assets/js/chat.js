/* PDG website chat. The conversation happens here first:
   - with storage on (/api/chat/config → live), messages are kept on the server and the PDG team answers in this chat
     (team inbox: /api/chat/inbox?key=ADMIN_KEY); with the AI key set, the AI answers at once until the team takes over;
   - WhatsApp, Messenger and phone are offered after the first message, as other options.
   Without storage the chat shows those options instead. See docs/10-ai-chat.md. */
(function () {
  "use strict";
  var lang = document.documentElement.lang || "ka";
  var C = (window.PDG_CONTENT && window.PDG_CONTENT[lang]) || {};
  var KA = (window.PDG_CONTENT && window.PDG_CONTENT.ka) || {};
  function t(k) { return C[k] || KA[k] || ""; }
  var WA = "https://wa.me/995550004333", MS = "https://m.me/PremiumDronesGeorgia", TEL = "tel:+995550004333";
  var ID_KEY = "pdg_chat_id", SEEN_KEY = "pdg_chat_seen", CONTACT_KEY = "pdg_chat_contact";
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } return null; }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function newId() {
    var a = new Uint8Array(16); window.crypto.getRandomValues(a);
    return Array.prototype.map.call(a, function (b) { return ("0" + b.toString(16)).slice(-2); }).join("");
  }
  var ICON = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg>';

  function build(cfg) {
    var live = !!cfg.live, ai = !!cfg.enabled && live;
    var id = store(ID_KEY) || "", msgs = [], polling = null, openNow = false;

    var fab = el("button", "chat-fab"); fab.type = "button"; fab.id = "chatFab";
    fab.setAttribute("aria-controls", "chatPanel"); fab.setAttribute("aria-expanded", "false");
    fab.innerHTML = ICON; fab.appendChild(el("span", "chat-fab-label", t("chat_open")));
    var dot = el("span", "chat-dot"); dot.hidden = true; dot.setAttribute("aria-hidden", "true"); fab.appendChild(dot);

    var panel = el("section", "chat-panel"); panel.id = "chatPanel"; panel.hidden = true;
    panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", t("chat_title"));
    var head = el("div", "chat-head");
    var titles = el("div", "chat-titles");
    titles.append(el("p", "chat-title", t("chat_title")));
    // Owner: no subtitle in the chat header; only when the website chat is off, say where we reply instead.
    if (!live) titles.append(el("p", "chat-sub", t("chat_sub_off")));
    var close = el("button", "chat-icon-btn", "×"); close.type = "button"; close.setAttribute("aria-label", t("chat_close"));
    head.append(titles, close);
    var log = el("div", "chat-log"); log.setAttribute("role", "log"); log.setAttribute("aria-live", "polite");
    var chips = el("div", "chat-suggest");
    ["chat_s1", "chat_s2", "chat_s3"].forEach(function (k) {
      var b = el("button", "chat-chip", t(k)); b.type = "button";
      b.addEventListener("click", function () { send(t(k)); }); chips.appendChild(b);
    });
    var form = el("form", "chat-form");
    var box = el("textarea"); box.rows = 1; box.maxLength = 1200; box.placeholder = t("chat_placeholder"); box.setAttribute("aria-label", t("chat_placeholder"));
    var go = el("button", "chat-send"); go.type = "submit"; go.setAttribute("aria-label", t("chat_send"));
    go.innerHTML = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>';
    form.append(box, go);

    function link(label, href, blank) {
      var a = el("a", null, label); a.href = href;
      if (blank) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
      return a;
    }
    var other = el("p", "chat-other");
    other.append(el("span", null, t("chat_other") + " "), link("WhatsApp", WA, true), document.createTextNode(" · "),
      link("Messenger", MS, true), document.createTextNode(" · "), link(t("chat_call"), TEL));
    var foot = el("div", "chat-foot"); foot.appendChild(other);
    if (ai) foot.appendChild(el("p", "chat-note", t("chat_note")));
    if (live) panel.append(head, log, chips, form, foot); else { panel.classList.add("chat-off"); Array.prototype.slice.call(other.childNodes).forEach(function (n) { if (n.nodeType === 3) n.remove(); }); panel.append(head, log, foot); }
    document.body.append(fab, panel);

    function linkify(node, text) {
      var re = /(https:\/\/(?:premium-drones\.ge|wa\.me|m\.me)\/[^\s)]*|\+995 ?550 ?00 ?43 ?33)/g, last = 0, m;
      while ((m = re.exec(text))) {
        node.appendChild(document.createTextNode(text.slice(last, m.index)));
        var a = el("a", null, m[0]);
        a.href = m[0].charAt(0) === "+" ? TEL : m[0].replace(/[.,]$/, "");
        if (/wa\.me|m\.me/.test(a.href)) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
        node.appendChild(a); last = m.index + m[0].length;
      }
      node.appendChild(document.createTextNode(text.slice(last)));
    }
    function bubble(role, text, extra) {
      var cls = role === "v" ? "user" : "assistant";
      var b = el("div", "chat-msg chat-" + cls + (role === "team" ? " chat-team" : "") + (extra ? " " + extra : ""));
      if (role === "team") b.appendChild(el("span", "chat-who", t("chat_team")));
      linkify(b, text); log.appendChild(b); return b;
    }
    function contactBox() {
      var wrap = el("div", "chat-msg chat-assistant chat-contact-ask");
      wrap.appendChild(el("p", null, t("chat_got")));
      var f = el("form", "chat-contact-form");
      var inp = el("input"); inp.type = "text"; inp.maxLength = 120; inp.autocomplete = "tel"; inp.placeholder = t("chat_contact_ph"); inp.setAttribute("aria-label", t("chat_contact_ph"));
      var b = el("button", null, t("chat_contact_save")); b.type = "submit";
      f.append(inp, b); wrap.appendChild(f);
      f.addEventListener("submit", function (e) {
        e.preventDefault();
        var v = inp.value.trim(); if (v.replace(/\W/g, "").length < 6) { inp.focus(); return; }
        b.disabled = true;
        post("/api/chat/contact", { id: id, contact: v }).then(function () { store(CONTACT_KEY, "1"); draw(); }, function () { b.disabled = false; });
      });
      return wrap;
    }
    function draw() {
      log.textContent = "";
      bubble("ai", t(live ? (ai ? "chat_hello" : "chat_hello_live") : "chat_hello_off"));
      msgs.forEach(function (m) { bubble(m.r, m.t); });
      var mine = msgs.filter(function (m) { return m.r === "v"; }).length;
      var answered = msgs.some(function (m) { return m.r === "team"; });
      if (live && mine && !ai && !answered) {
        if (store(CONTACT_KEY)) bubble("ai", t("chat_contact_thanks")); else log.appendChild(contactBox());
      }
      chips.hidden = mine > 0;
      other.hidden = live && !mine;
      log.scrollTop = log.scrollHeight;
    }
    function post(url, body) {
      return fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
        .then(function (r) { return r.json().then(function (d) { if (!r.ok) throw d; return d; }); });
    }
    function merge(list) {
      (list || []).forEach(function (m) { if (m.i >= msgs.length) msgs[m.i] = { r: m.r, t: m.t }; });
      msgs = msgs.filter(Boolean);
    }
    function unseen() {
      var seen = Number(store(SEEN_KEY)) || 0;
      return msgs.slice(seen).some(function (m) { return m.r !== "v"; });
    }
    function markSeen() { store(SEEN_KEY, String(msgs.length)); dot.hidden = true; }
    function fetchNew() {
      if (!id || document.hidden) return Promise.resolve();
      return fetch("/api/chat/thread?id=" + id + "&after=" + msgs.length, { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) {
          if (!d || !d.msgs || !d.msgs.length) return;
          merge(d.msgs);
          if (openNow) { draw(); markSeen(); } else dot.hidden = !unseen();
        }).catch(function () {});
    }
    function schedule() {
      clearInterval(polling);
      if (id && live) polling = setInterval(fetchNew, openNow ? 5000 : 30000);
    }

    var busy = false;
    function send(text) {
      text = String(text || "").trim();
      if (!text || busy || !live) return;
      if (!id) { id = newId(); store(ID_KEY, id); }
      busy = true; go.disabled = true; box.value = ""; size();
      bubble("v", text).classList.add("chat-pending");
      var typing = ai ? bubble("ai", t("chat_typing"), "chat-typing") : null;
      log.scrollTop = log.scrollHeight;
      post("/api/chat/send", { id: id, text: text, lang: lang, page: location.pathname, after: msgs.length })
        .then(function (d) { merge(d.msgs); draw(); markSeen(); schedule(); })
        .catch(function (d) {
          draw(); box.value = text; size();
          bubble("ai", t(d && d.error === "busy" ? "chat_busy" : "chat_error"), "chat-error");
          other.hidden = false; log.scrollTop = log.scrollHeight;
        })
        .then(function () { busy = false; go.disabled = false; box.focus(); });
    }
    function size() { box.style.height = ""; if (box.value) box.style.height = Math.min(Math.max(box.scrollHeight, 46), 140) + "px"; }
    box.addEventListener("input", size);
    box.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(box.value); } });
    form.addEventListener("submit", function (e) { e.preventDefault(); send(box.value); });
    function open(on) {
      openNow = on; panel.hidden = !on; fab.setAttribute("aria-expanded", String(on)); document.body.classList.toggle("chat-open", on);
      if (on) { draw(); markSeen(); fetchNew(); if (live) box.focus(); } else fab.focus();
      schedule();
    }
    fab.addEventListener("click", function () { open(panel.hidden); });
    close.addEventListener("click", function () { open(false); });
    panel.addEventListener("keydown", function (e) { if (e.key === "Escape") open(false); });
    document.addEventListener("visibilitychange", function () { if (!document.hidden) fetchNew(); });
    if (id && live) { fetchNew(); schedule(); }
  }

  fetch("/api/chat/config", { headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : {}; })
    .then(function (c) { build(c || {}); }, function () { build({}); });
})();
