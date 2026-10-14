/* PDG AI assistant (live chat). Shows only when /api/chat/config says the AI key is set (see docs/10-ai-chat.md).
   The conversation is kept for this browser tab only (sessionStorage) and sent to /api/chat, which asks Claude. */
(function () {
  "use strict";
  var lang = document.documentElement.lang || "ka";
  var C = (window.PDG_CONTENT && window.PDG_CONTENT[lang]) || {};
  var KA = (window.PDG_CONTENT && window.PDG_CONTENT.ka) || {};
  function t(k) { return C[k] || KA[k] || ""; }
  var WA = "995550004333", KEY = "pdg_chat", demo = !!window.PDG_CHAT_DEMO;
  var history = [];
  try { history = JSON.parse(sessionStorage.getItem(KEY) || "[]") || []; } catch (e) { history = []; }
  function keep() { try { sessionStorage.setItem(KEY, JSON.stringify(history.slice(-30))); } catch (e) { /* private mode */ } }

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  var ICON = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 5h16v11H9l-5 4z"/><path d="M8 10h8M8 13h5"/></svg>';

  function build() {
    var fab = el("button", "chat-fab");
    fab.type = "button"; fab.id = "chatFab"; fab.setAttribute("aria-controls", "chatPanel"); fab.setAttribute("aria-expanded", "false");
    fab.innerHTML = ICON; fab.appendChild(el("span", "chat-fab-label", t("chat_open")));
    var panel = el("section", "chat-panel"); panel.id = "chatPanel"; panel.hidden = true;
    panel.setAttribute("role", "dialog"); panel.setAttribute("aria-label", t("chat_title"));
    var head = el("div", "chat-head");
    var titles = el("div", "chat-titles"); titles.appendChild(el("p", "chat-title", t("chat_title"))); titles.appendChild(el("p", "chat-sub", t("chat_sub")));
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
    var human = el("a", "chat-human", t("chat_human")); human.href = "https://wa.me/" + WA; human.target = "_blank"; human.rel = "noopener noreferrer";
    foot.append(el("p", "chat-note", t("chat_note")), human);
    panel.append(head, log, chips, form, foot);
    document.body.append(fab, panel);

    function linkify(node, text) {
      var re = /(https:\/\/(?:premium-drones\.ge|wa\.me)\/[^\s)]*|\+995 ?550 ?00 ?43 ?33)/g, last = 0, m;
      while ((m = re.exec(text))) {
        node.appendChild(document.createTextNode(text.slice(last, m.index)));
        var a = el("a", null, m[0]);
        a.href = m[0].charAt(0) === "+" ? "tel:+995550004333" : m[0].replace(/[.,]$/, "");
        if (a.href.indexOf("wa.me") > -1) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
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
      bubble("assistant", t("chat_hello"));
      history.forEach(function (m) { bubble(m.role, m.content); });
      chips.hidden = history.length > 0;
      var lastQ = history.filter(function (m) { return m.role === "user"; }).pop();
      human.href = "https://wa.me/" + WA + (lastQ ? "?text=" + encodeURIComponent(lastQ.content.slice(0, 500)) : "");
    }
    var busy = false;
    function send(text) {
      text = String(text || "").trim();
      if (!text || busy) return;
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

  if (demo) { build(); return; }
  fetch("/api/chat/config", { headers: { Accept: "application/json" } })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (c) { if (c && c.enabled) build(); })
    .catch(function () { /* static preview or chat off */ });
})();
