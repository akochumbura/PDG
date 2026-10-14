/* PDG live chat. With the AI key set (/api/chat/config, docs/10-ai-chat.md) the AI replies here; without it, messages go to WhatsApp.
   WhatsApp, Messenger and phone buttons are always there to reach a person.
   The conversation is kept for this browser tab only (sessionStorage) and sent to /api/chat, which asks Claude. */
(function () {
  "use strict";
  var lang = document.documentElement.lang || "ka";
  var C = (window.PDG_CONTENT && window.PDG_CONTENT[lang]) || {};
  var KA = (window.PDG_CONTENT && window.PDG_CONTENT.ka) || {};
  function t(k) { return C[k] || KA[k] || ""; }
  var WA = "995550004333", MS = "https://m.me/PremiumDronesGeorgia", KEY = "pdg_chat", demo = !!window.PDG_CHAT_DEMO, ai = true;
  var history = [];
  try { history = JSON.parse(sessionStorage.getItem(KEY) || "[]") || []; } catch (e) { history = []; }
  function keep() { try { sessionStorage.setItem(KEY, JSON.stringify(history.slice(-30))); } catch (e) { /* private mode */ } }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var ICON = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg>';

  function build(aiOn) {
    ai = !!aiOn;
    var fab = el("button", "chat-fab");
    fab.type = "button"; fab.id = "chatFab"; fab.setAttribute("aria-controls", "chatPanel"); fab.setAttribute("aria-expanded", "false");
    fab.innerHTML = ICON; fab.appendChild(el("span", "chat-fab-label", t("chat_open")));
    var panel = el("section", "chat-panel"); panel.id = "chatPanel"; panel.hidden = true;
    panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", t("chat_title"));
    var head = el("div", "chat-head");
    var titles = el("div", "chat-titles"); titles.appendChild(el("p", "chat-title", t("chat_title"))); titles.appendChild(el("p", "chat-sub", t(ai ? "chat_sub" : "chat_sub_off")));
    var reset = el("button", "chat-icon-btn", "↺"); reset.type = "button"; reset.setAttribute("aria-label", t("chat_new")); reset.title = t("chat_new");
    var close = el("button", "chat-icon-btn", "×"); close.type = "button"; close.setAttribute("aria-label", t("chat_close"));
    head.append(titles, reset, close);
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
    var foot = el("div", "chat-foot");
    var ICONS = {
      wa: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M4 20l1.3-4A8 8 0 1 1 8.2 19z"/><path d="M9 9.5c.5 2.3 2.2 4 4.5 4.5l1.2-1.2 2 .9c-.3 1.4-1.5 2-2.7 1.7A7 7 0 0 1 8.6 10c-.3-1.2.3-2.4 1.7-2.7l.9 2z"/></svg>',
      ms: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 3C7 3 3 6.7 3 11.3c0 2.6 1.3 4.9 3.3 6.4V21l3-1.7c.9.3 1.8.4 2.7.4 5 0 9-3.7 9-8.4S17 3 12 3Z"/><path d="m7.5 13.5 3-3.2 2 2 3-3.2-3 3.2-2-2z"/></svg>',
      call: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a1 1 0 0 1-1 1A16 16 0 0 1 4 5a1 1 0 0 1 1-1Z"/></svg>'
    };
    function contact(cls, icon, label, href, blank) {
      var a = el("a", "chat-contact " + cls); a.href = href; a.innerHTML = ICONS[icon]; a.appendChild(el("span", null, label));
      if (blank) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
      return a;
    }
    var human = contact("chat-wa", "wa", "WhatsApp", "https://wa.me/" + WA, true);
    var row = el("div", "chat-contacts");
    row.append(human, contact("chat-ms", "ms", "Messenger", MS, true), contact("chat-call", "call", t("chat_call"), "tel:+995550004333"));
    var humanBox = el("div", "chat-human-box"); humanBox.append(el("p", "chat-human", t("chat_human")), row);
    if (ai) foot.append(humanBox, el("p", "chat-note", t("chat_note"))); else foot.append(humanBox);
    panel.append(head, log, chips, form, foot);
    document.body.append(fab, panel);

    function linkify(node, text) {
      var re = /(https:\/\/(?:premium-drones\.ge|wa\.me|m\.me)\/[^\s)]*|\+995 ?550 ?00 ?43 ?33)/g, last = 0, m;
      while ((m = re.exec(text))) {
        node.appendChild(document.createTextNode(text.slice(last, m.index)));
        var a = el("a", null, m[0]);
        a.href = m[0].charAt(0) === "+" ? "tel:+995550004333" : m[0].replace(/[.,]$/, "");
        if (a.href.indexOf("wa.me") > -1 || a.href.indexOf("m.me") > -1) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
        node.appendChild(a); last = m.index + m[0].length;
      }
      node.appendChild(document.createTextNode(text.slice(last)));
    }
    function bubble(role, text, extra) {
      var b = el("div", "chat-msg chat-" + role + (extra ? " " + extra : ""));
      linkify(b, text); log.appendChild(b); log.scrollTop = log.scrollHeight; return b;
    }
    function draw() {
      log.textContent = "";
      bubble("assistant", t(ai ? "chat_hello" : "chat_hello_off"));
      history.forEach(function (m) { bubble(m.role, m.content); });
      chips.hidden = history.length > 0;
      var lastQ = history.filter(function (m) { return m.role === "user"; }).pop();
      human.href = "https://wa.me/" + WA + (lastQ ? "?text=" + encodeURIComponent(lastQ.content.slice(0, 500)) : "");
    }
    var busy = false;
    function send(text) {
      text = String(text || "").trim();
      if (!text || busy) return;
      if (!ai) {  // no AI key yet: hand the question straight to WhatsApp
        window.open("https://wa.me/" + WA + "?text=" + encodeURIComponent(text.slice(0, 1000)), "_blank", "noopener");
        box.value = ""; size(); bubble("user", text); bubble("assistant", t("chat_sent_off"));
        return;
      }
      busy = true; go.disabled = true; box.value = ""; size();
      history.push({ role: "user", content: text.slice(0, 1200) }); keep(); draw();
      var typing = bubble("assistant", t("chat_typing"), "chat-typing");
      var done = function (reply, isError) {
        typing.remove();
        if (isError) bubble("assistant", reply, "chat-error");
        else { history.push({ role: "assistant", content: reply }); keep(); draw(); }
        busy = false; go.disabled = false; box.focus();
      };
      if (demo) { setTimeout(function () { done(t("chat_demo"), true); }, 700); return; }
      fetch("/api/chat", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ messages: history.slice(-16), lang: lang }) })
        .then(function (r) { return r.json().then(function (d) { return [r.status, d]; }); })
        .then(function (x) {
          if (x[1] && x[1].reply) done(x[1].reply);
          else done(t(x[0] === 429 || (x[1] && x[1].error === "busy") ? "chat_busy" : "chat_error"), true);
        })
        .catch(function () { done(t("chat_error"), true); });
    }
    function size() { box.style.height = ""; if (box.value) box.style.height = Math.min(Math.max(box.scrollHeight, 46), 140) + "px"; }
    box.addEventListener("input", size);
    box.addEventListener("keydown", function (e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(box.value); } });
    form.addEventListener("submit", function (e) { e.preventDefault(); send(box.value); });
    function open(on) {
      panel.hidden = !on; fab.setAttribute("aria-expanded", String(on)); document.body.classList.toggle("chat-open", on);
      if (on) { draw(); box.focus(); } else fab.focus();
    }
    fab.addEventListener("click", function () { open(panel.hidden); });
    close.addEventListener("click", function () { open(false); });
    reset.addEventListener("click", function () { history = []; keep(); draw(); box.focus(); });
    panel.addEventListener("keydown", function (e) { if (e.key === "Escape") open(false); });
  }

  if (demo) { build(true); return; }
  fetch("/api/chat/config", { headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (c) { build(!!(c && c.enabled)); }, function () { build(false); });
})();
