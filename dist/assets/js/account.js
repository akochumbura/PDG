/* PDG customer accounts: sign in / register / profile / order history on /account,
   and saved details in the cart. Works only when the server has storage (see docs/11-accounts.md). */
(function () {
  "use strict";
  var page = document.getElementById("account");
  var cartForm = document.getElementById("cartForm");
  if (!page && !cartForm) return;
  function lb(k) { var e = document.getElementById("lb_" + k); return e ? e.textContent.trim() : ""; }
  function api(path, body) {
    return fetch("/api/account/" + path, body === undefined ? { credentials: "same-origin" } :
      { method: "POST", credentials: "same-origin", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (d) { d._status = r.status; return d; }); });
  }
  function fmt(n) { return "₾" + Number(n || 0).toLocaleString("en-US"); }

  /* Cart: fill in saved details and keep WhatsApp/e-mail orders in the account history. */
  if (cartForm) {
    api("me").then(function (d) {
      if (!d.user) return;
      ["name", "phone", "address"].forEach(function (k) { var f = cartForm.elements[k]; if (f && !f.value) f.value = d.user[k] || ""; });
      var cart = function () { try { return JSON.parse(localStorage.getItem("pdg_cart") || "{}") || {}; } catch (e) { return {}; } };
      var log = function (channel) {
        var c = cart(), items = Object.keys(c).map(function (k) { return { sku: k, qty: c[k].q }; });
        if (!items.length) return;
        fetch("/api/account/order-request", { method: "POST", keepalive: true, credentials: "same-origin", headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ items: items, channel: channel, lang: document.documentElement.lang, delivery: (cartForm.elements.delivery && cartForm.elements.delivery.value) || "delivery" }) }).catch(function () {});
      };
      cartForm.addEventListener("submit", function () { if (cartForm.elements.name.value.trim() && cartForm.elements.phone.value.replace(/\D/g, "").length >= 9) log("whatsapp"); });
      var mail = document.getElementById("cartMail");
      if (mail) mail.addEventListener("click", function () { if (cartForm.elements.name.value.trim() && cartForm.elements.phone.value.replace(/\D/g, "").length >= 9) log("email"); });
    }).catch(function () {});
  }
  if (!page) return;

  var social = document.getElementById("accSocial");
  var guest = document.getElementById("accGuest"), user = document.getElementById("accUser"), off = document.getElementById("accOff");
  function msg(form, text, ok) {
    var m = form.querySelector(".acc-msg"); m.textContent = text; m.hidden = !text; m.classList.toggle("is-ok", !!ok);
  }
  function busy(form, on) { var b = form.querySelector("button[type=submit]"); if (b) b.disabled = on; }
  var ERR = { exists: "acc_err_exists", login: "acc_err_login", fields: "acc_err_fields", password: "acc_err_password", locked: "acc_err_locked", busy: "acc_err_busy" };
  function errText(d) { return lb(ERR[d && d.error] || "acc_err_server"); }

  function showUser(d) {
    page.setAttribute("data-state", "user"); guest.hidden = true; user.hidden = false; off.hidden = true; if (social) social.hidden = true;
    document.getElementById("accHello").textContent = lb("acc_hello").replace("{name}", d.user.name);
    var pf = document.getElementById("profileForm");
    ["name", "phone", "company", "address"].forEach(function (k) { pf.elements[k].value = d.user[k] || ""; });
    if (!d.user.phone) msg(pf, lb("acc_need_phone"));
    var list = document.getElementById("accOrders"); list.textContent = "";
    var orders = d.orders || [];
    if (!orders.length) { var li = document.createElement("li"); li.className = "acc-empty"; li.textContent = lb("acc_no_orders"); list.appendChild(li); }
    orders.forEach(function (o) {
      var li = document.createElement("li");
      var st = o.status === "completed" ? "acc_st_completed" : o.status === "requested" ? "acc_st_requested" : o.status === "rejected" ? "acc_st_rejected" : "acc_st_pending";
      var top = document.createElement("p"); top.className = "acc-order-top";
      var ref = document.createElement("strong"); ref.textContent = o.ref;
      var badge = document.createElement("span"); badge.className = "acc-status acc-" + o.status; badge.textContent = lb(st);
      top.append(ref, badge);
      var meta = document.createElement("p"); meta.className = "acc-order-meta";
      meta.textContent = String(o.created || "").slice(0, 10) + " · " + fmt(o.total) + (o.mode === "deposit" ? " · " + lb("acc_deposit") + " " + fmt(o.amount) : "");
      var items = document.createElement("p"); items.className = "acc-order-items";
      items.textContent = (o.items || []).map(function (i) { return i.qty + " × " + i.name; }).join(", ");
      li.append(top, meta, items); list.appendChild(li);
    });
  }
  function showGuest() { page.setAttribute("data-state", "guest"); guest.hidden = false; user.hidden = true; view(resetToken ? "reset" : "login"); }

  var login = document.getElementById("loginForm"), reg = document.getElementById("registerForm"), pf = document.getElementById("profileForm");
  var forgot = document.getElementById("forgotForm"), reset = document.getElementById("resetForm");
  var tabs = { login: document.getElementById("tabLogin"), register: document.getElementById("tabRegister") };
  var tabList = tabs.login && tabs.login.parentNode;
  var resetToken = (location.search.match(/[?&]reset=([a-f0-9]{64})/) || [])[1] || "";
  if (resetToken && history.replaceState) history.replaceState(null, "", location.pathname + location.hash);  // the token never stays in the address bar
  /* One form at a time: sign in | register (tabs), forgot password, new password (from the e-mailed link). */
  function view(name) {
    var forms = { login: login, register: reg, forgot: forgot, reset: reset };
    Object.keys(forms).forEach(function (k) { if (forms[k]) forms[k].hidden = k !== name; });
    var tabbed = name === "login" || name === "register";
    if (tabList) tabList.hidden = !tabbed;
    Object.keys(tabs).forEach(function (k) { if (!tabs[k]) return; tabs[k].setAttribute("aria-selected", String(k === name)); tabs[k].tabIndex = k === name ? 0 : -1; });
    if (social) social.hidden = !(tabbed && socialAny);
  }
  Object.keys(tabs).forEach(function (k) {
    if (!tabs[k]) return;
    tabs[k].addEventListener("click", function () { view(k); });
    tabs[k].addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      var other = k === "login" ? "register" : "login"; view(other); tabs[other].focus();
    });
  });
  Array.prototype.forEach.call(document.querySelectorAll("#account [data-back]"), function (b) { b.addEventListener("click", function () { view("login"); login.elements.email.focus(); }); });
  var forgotLink = document.getElementById("accForgotLink");
  if (forgotLink) forgotLink.addEventListener("click", function () {
    view("forgot"); if (login.elements.email.value) forgot.elements.email.value = login.elements.email.value; forgot.elements.email.focus();
  });
  /* Show / hide password. */
  Array.prototype.forEach.call(document.querySelectorAll("#account .acc-eye"), function (b) {
    b.addEventListener("click", function () {
      var f = document.getElementById(b.getAttribute("data-eye")); var show = f.type === "password";
      f.type = show ? "text" : "password"; b.setAttribute("aria-pressed", String(show));
      b.setAttribute("aria-label", lb(show ? "acc_hide_pw" : "acc_show_pw")); f.focus();
    });
  });
  /* Errors appear only after a submit; a field loses its error mark as soon as it is edited. */
  function mark(form, names) {
    Array.prototype.forEach.call(form.elements, function (x) { if (x.name) x.removeAttribute("aria-invalid"); });
    names.forEach(function (n) { if (form.elements[n]) form.elements[n].setAttribute("aria-invalid", "true"); });
    if (names.length && form.elements[names[0]]) form.elements[names[0]].focus();
  }
  [login, reg, forgot, reset].forEach(function (f) { if (f) f.addEventListener("input", function (e) { if (e.target.removeAttribute) e.target.removeAttribute("aria-invalid"); }); });
  var mailOk = function (v) { return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v); };

  login.addEventListener("submit", function (e) {
    e.preventDefault(); msg(login, "");
    var bad = []; if (!mailOk(login.elements.email.value.trim())) bad.push("email"); if (!login.elements.password.value) bad.push("password");
    if (bad.length) { mark(login, bad); msg(login, lb(bad[0] === "email" ? "acc_err_email" : "acc_err_login")); return; }
    busy(login, true);
    api("login", { email: login.elements.email.value.trim(), password: login.elements.password.value })
      .then(function (d) { if (d.user) return api("me").then(showUser); mark(login, ["password"]); msg(login, errText(d)); })
      .catch(function () { msg(login, lb("acc_err_server")); })
      .then(function () { busy(login, false); });
  });
  reg.addEventListener("submit", function (e) {
    e.preventDefault(); msg(reg, "");
    var bad = [];
    if (reg.elements.name.value.trim().length < 2) bad.push("name");
    if (!mailOk(reg.elements.email.value.trim())) bad.push("email");
    if (reg.elements.phone.value.replace(/\D/g, "").length < 9) bad.push("phone");
    if (reg.elements.password.value.length < 8) bad.push("password");
    if (bad.length) { mark(reg, bad); msg(reg, lb(bad.length === 1 && bad[0] === "password" ? "acc_err_password" : "acc_err_fields")); return; }
    if (!document.getElementById("reg_terms").checked) { msg(reg, lb("acc_err_terms")); document.getElementById("reg_terms").focus(); return; }
    busy(reg, true);
    api("register", { name: reg.elements.name.value.trim(), email: reg.elements.email.value.trim(), phone: reg.elements.phone.value.trim(),
      company: reg.elements.company.value.trim(), password: reg.elements.password.value })
      .then(function (d) { if (d.user) return api("me").then(showUser); msg(reg, errText(d)); })
      .catch(function () { msg(reg, lb("acc_err_server")); })
      .then(function () { busy(reg, false); });
  });
  if (forgot) forgot.addEventListener("submit", function (e) {
    e.preventDefault(); msg(forgot, "");
    var email = forgot.elements.email.value.trim();
    if (!mailOk(email)) { mark(forgot, ["email"]); msg(forgot, lb("acc_err_email")); return; }
    busy(forgot, true);
    api("forgot", { email: email, lang: document.documentElement.lang })
      .then(function (d) { if (d.ok) msg(forgot, lb("acc_forgot_sent"), true); else msg(forgot, lb(d.error === "busy" ? "acc_err_busy" : d.error === "fields" ? "acc_err_email" : "acc_err_server")); })
      .catch(function () { msg(forgot, lb("acc_err_server")); })
      .then(function () { busy(forgot, false); });
  });
  if (reset) reset.addEventListener("submit", function (e) {
    e.preventDefault(); msg(reset, "");
    if (reset.elements.password.value.length < 8) { mark(reset, ["password"]); msg(reset, lb("acc_err_password")); return; }
    busy(reset, true);
    api("reset", { token: resetToken, password: reset.elements.password.value })
      .then(function (d) {
        if (d.user) { resetToken = ""; return api("me").then(function (m) { showUser(m); msg(pf, lb("acc_reset_done"), true); }); }
        if (d.error === "expired") { view("forgot"); msg(forgot, lb("acc_reset_expired")); return; }
        msg(reset, lb(d.error === "password" ? "acc_err_password" : "acc_err_server"));
      })
      .catch(function () { msg(reset, lb("acc_err_server")); })
      .then(function () { busy(reset, false); });
  });
  /* Phones: the call/chat bar never covers a field or the keyboard on this page. */
  page.addEventListener("focusin", function (e) { if (/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)) document.body.classList.add("acc-typing"); });
  page.addEventListener("focusout", function () { setTimeout(function () { if (!page.contains(document.activeElement) || !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)) document.body.classList.remove("acc-typing"); }, 100); });
  pf.addEventListener("submit", function (e) {
    e.preventDefault(); msg(pf, ""); busy(pf, true);
    api("update", { name: pf.elements.name.value.trim(), phone: pf.elements.phone.value.trim(), company: pf.elements.company.value.trim(), address: pf.elements.address.value.trim() })
      .then(function (d) { if (d.user) { msg(pf, lb("acc_saved"), true); document.getElementById("accHello").textContent = lb("acc_hello").replace("{name}", d.user.name); } else msg(pf, errText(d)); })
      .catch(function () { msg(pf, lb("acc_err_server")); })
      .then(function () { busy(pf, false); });
  });
  document.getElementById("accLogout").addEventListener("click", function () { api("logout", {}).then(showGuest, showGuest); });

  /* Google / Apple: buttons only when the server has their keys; ?auth=error comes back from a failed sign-in. */
  var socialAny = false, auth = (location.search.match(/[?&]auth=(\w+)/) || [])[1];
  function setupSocial(c) {
    var any = false, lang = document.documentElement.lang || "ka";
    [["accGoogle", c.google, "google"], ["accApple", c.apple, "apple"]].forEach(function (b) {
      var a = document.getElementById(b[0]); if (!a) return;
      a.hidden = !b[1]; if (b[1]) { any = true; a.href = "/api/auth/" + b[2] + "/start?lang=" + encodeURIComponent(lang); }
    });
    socialAny = any; social.hidden = !any || (login && login.hidden && reg && reg.hidden);
    if (auth === "error" || auth === "off") {
      var m = document.getElementById("accSocialMsg"); m.textContent = lb("acc_err_social"); m.hidden = false; socialAny = true; social.hidden = false;
    }
    if (auth && history.replaceState) history.replaceState(null, "", location.pathname + location.hash);
  }
  fetch("/api/account/config").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (c) {
    if (c && c.enabled && social) setupSocial(c);
    if (c && c.enabled && forgotLink) forgotLink.hidden = !c.reset;
    if (c && c.enabled && resetToken && !c.reset) resetToken = "";
    if (!c || !c.enabled) {
      page.setAttribute("data-state", "off"); off.hidden = false;
      [login, reg].forEach(function (f) { Array.prototype.forEach.call(f.elements, function (x) { x.disabled = true; }); });
      return;
    }
    api("me").then(function (d) { if (d.user) showUser(d); else showGuest(); }, showGuest);
  });
})();
