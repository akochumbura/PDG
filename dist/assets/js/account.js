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
          body: JSON.stringify({ items: items, channel: channel, lang: document.documentElement.lang }) }).catch(function () {});
      };
      cartForm.addEventListener("submit", function () { if (cartForm.elements.name.value.trim() && cartForm.elements.phone.value.replace(/\D/g, "").length >= 9) log("whatsapp"); });
      var mail = document.getElementById("cartMail");
      if (mail) mail.addEventListener("click", function () { if (cartForm.elements.name.value.trim() && cartForm.elements.phone.value.replace(/\D/g, "").length >= 9) log("email"); });
    }).catch(function () {});
  }
  if (!page) return;

  var guest = document.getElementById("accGuest"), user = document.getElementById("accUser"), off = document.getElementById("accOff");
  function msg(form, text, ok) {
    var m = form.querySelector(".acc-msg"); m.textContent = text; m.hidden = !text; m.classList.toggle("is-ok", !!ok);
  }
  function busy(form, on) { var b = form.querySelector("button[type=submit]"); if (b) b.disabled = on; }
  var ERR = { exists: "acc_err_exists", login: "acc_err_login", fields: "acc_err_fields", password: "acc_err_password", locked: "acc_err_locked" };
  function errText(d) { return lb(ERR[d && d.error] || "acc_err_server"); }

  function showUser(d) {
    page.setAttribute("data-state", "user"); guest.hidden = true; user.hidden = false; off.hidden = true;
    document.getElementById("accHello").textContent = lb("acc_hello").replace("{name}", d.user.name);
    var pf = document.getElementById("profileForm");
    ["name", "phone", "company", "address"].forEach(function (k) { pf.elements[k].value = d.user[k] || ""; });
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
  function showGuest() { page.setAttribute("data-state", "guest"); guest.hidden = false; user.hidden = true; }

  var login = document.getElementById("loginForm"), reg = document.getElementById("registerForm"), pf = document.getElementById("profileForm");
  login.addEventListener("submit", function (e) {
    e.preventDefault(); msg(login, ""); busy(login, true);
    api("login", { email: login.elements.email.value.trim(), password: login.elements.password.value })
      .then(function (d) { if (d.user) return api("me").then(showUser); msg(login, errText(d)); })
      .catch(function () { msg(login, lb("acc_err_server")); })
      .then(function () { busy(login, false); });
  });
  reg.addEventListener("submit", function (e) {
    e.preventDefault(); msg(reg, "");
    if (!document.getElementById("reg_terms").checked) { msg(reg, lb("acc_err_terms")); return; }
    if (reg.elements.password.value.length < 8) { msg(reg, lb("acc_err_password")); return; }
    busy(reg, true);
    api("register", { name: reg.elements.name.value.trim(), email: reg.elements.email.value.trim(), phone: reg.elements.phone.value.trim(),
      company: reg.elements.company.value.trim(), password: reg.elements.password.value })
      .then(function (d) { if (d.user) return api("me").then(showUser); msg(reg, errText(d)); })
      .catch(function () { msg(reg, lb("acc_err_server")); })
      .then(function () { busy(reg, false); });
  });
  pf.addEventListener("submit", function (e) {
    e.preventDefault(); msg(pf, ""); busy(pf, true);
    api("update", { name: pf.elements.name.value.trim(), phone: pf.elements.phone.value.trim(), company: pf.elements.company.value.trim(), address: pf.elements.address.value.trim() })
      .then(function (d) { if (d.user) { msg(pf, lb("acc_saved"), true); document.getElementById("accHello").textContent = lb("acc_hello").replace("{name}", d.user.name); } else msg(pf, errText(d)); })
      .catch(function () { msg(pf, lb("acc_err_server")); })
      .then(function () { busy(pf, false); });
  });
  document.getElementById("accLogout").addEventListener("click", function () { api("logout", {}).then(showGuest, showGuest); });

  fetch("/api/account/config").then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (c) {
    if (!c || !c.enabled) {
      page.setAttribute("data-state", "off"); off.hidden = false;
      [login, reg].forEach(function (f) { Array.prototype.forEach.call(f.elements, function (x) { x.disabled = true; }); });
      return;
    }
    api("me").then(function (d) { if (d.user) showUser(d); else showGuest(); }, showGuest);
  });
})();
