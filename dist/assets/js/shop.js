/* PDG shop: cart (kept in this browser), order by WhatsApp or e-mail, and online payment through
   Bank of Georgia (card, Apple Pay, Google Pay). The Pay button appears only when /api/payments/config
   says the bank keys are set (docs/07-payments.md). Orders under the threshold are paid in full,
   larger ones pay a deposit online. The payment page (payment.html) shows only what the bank confirms. */
(function () {
  "use strict";
  var KEY = "pdg_cart", WHATSAPP = "995550004333", EMAIL = "info@premium-drones.ge";
  var cart = {};
  try { cart = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { cart = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) { /* private mode */ } }
  function fmt(n) { return "₾" + Number(n).toLocaleString("en-US"); }
  function totals() { var t = 0, c = 0; Object.keys(cart).forEach(function (k) { t += cart[k].p * cart[k].q; c += cart[k].q; }); return [t, c]; }
  function label(id) { var e = document.getElementById(id); return e ? e.textContent.trim() : ""; }

  /* Keep prices in the cart in step with the current page (prices may have changed since the item was added). */
  document.querySelectorAll(".add-btn[data-sku]").forEach(function (b) {
    var item = cart[b.dataset.sku];
    if (item) { item.p = Number(b.dataset.price); item.n = b.dataset.name; }
  });
  Object.keys(cart).forEach(function (k) { var it = cart[k]; if (!it || !(it.q > 0) || !(it.p >= 0)) delete cart[k]; });
  save();

  var PAY = window.PDG_PAY || {}, payReady = false, paying = false;
  function payAmount(t) { return t >= PAY.threshold ? Math.min(Math.ceil(t * PAY.depositPercent / 100), PAY.threshold - 1) : t; }
  var badge = document.getElementById("cartCount"), dlg = document.getElementById("cart");
  var form = document.getElementById("cartForm");

  function orderText() {
    var lines = Object.keys(cart).map(function (k) {
      var it = cart[k];
      return "- " + it.n + " (" + k + ") × " + it.q + " = " + fmt(it.p * it.q);
    });
    var text = "Premium Drones Georgia — " + label("lbOrder") + "\n" + lines.join("\n") + "\n" + label("lbTotal") + ": " + fmt(totals()[0]);
    if (form) {
      var who = [form.elements.name.value.trim(), form.elements.phone.value.trim(), form.elements.address.value.trim()].filter(Boolean).join(", ");
      if (who) text += "\n\n" + who;
    }
    return text;
  }

  function render() {
    var T = totals();
    if (badge) { badge.textContent = T[1]; badge.hidden = !T[1]; }
    if (!dlg) return;
    var list = document.getElementById("cartList"), keys = Object.keys(cart);
    list.textContent = "";
    document.getElementById("cartEmpty").hidden = keys.length > 0;
    document.getElementById("cartFoot").hidden = !keys.length;
    keys.forEach(function (k) {
      var it = cart[k], li = document.createElement("li");
      function btn(txt, fn, aria) { var x = document.createElement("button"); x.type = "button"; x.textContent = txt; x.addEventListener("click", fn); if (aria) x.setAttribute("aria-label", aria); return x; }
      var name = document.createElement("span"); name.className = "ci-name"; name.textContent = it.n;
      var qty = document.createElement("span"); qty.className = "ci-qty";
      var count = document.createElement("output"); count.textContent = it.q;
      qty.append(btn("−", function () { change(k, -1); }, label("lbLess")), count, btn("+", function () { change(k, 1); }, label("lbMore")));
      var price = document.createElement("span"); price.className = "ci-price"; price.textContent = fmt(it.p * it.q);
      li.append(name, qty, price, btn("×", function () { delete cart[k]; save(); render(); }, label("lbRemove")));
      list.appendChild(li);
    });
    document.getElementById("cartTotal").textContent = fmt(T[0]);
    var pay = document.getElementById("cartPay");
    if (pay) {
      var amount = payAmount(T[0]), dep = T[0] >= PAY.threshold;
      pay.hidden = !payReady;
      pay.querySelector("span").textContent = label(dep ? "lbPayDeposit" : "lbPayFull") + " · " + fmt(amount);
      var dn = document.getElementById("cartDeposit");
      dn.hidden = !(payReady && dep);
      if (dep) dn.textContent = label("lbDeposit").replace("{pct}", PAY.depositPercent).replace("{deposit}", fmt(amount)).replace("{rest}", fmt(T[0] - amount));
      var wa = document.getElementById("cartWa");
      wa.classList.toggle("button-red", !payReady); wa.classList.toggle("button-line", payReady);
      document.getElementById("cartNote").hidden = payReady;
      document.getElementById("cartPayNote").hidden = !payReady;
    }
  }
  function change(k, d) { if (!cart[k]) return; cart[k].q += d; if (cart[k].q < 1) delete cart[k]; save(); render(); }
  function openCart() { if (dlg && dlg.showModal && !dlg.open) { dlg.showModal(); document.body.classList.add("modal-open"); } }

  document.addEventListener("click", function (e) {
    var add = e.target.closest(".add-btn");
    if (add) {
      var k = add.dataset.sku;
      cart[k] = cart[k] || { n: add.dataset.name, p: Number(add.dataset.price), q: 0 };
      cart[k].q += 1; save(); render();
      add.classList.add("is-added");
      setTimeout(function () { add.classList.remove("is-added"); }, 900);
      return;
    }
    if (e.target.closest(".cart-link") && dlg) { e.preventDefault(); openCart(); return; }
    if (dlg && (e.target === dlg || e.target.id === "cartClose")) dlg.close();
  });
  if (dlg) dlg.addEventListener("close", function () { document.body.classList.remove("modal-open"); });

  if (form) {
    var error = document.getElementById("cartError");
    function valid() {
      var ok = form.elements.name.value.trim() && form.elements.phone.value.replace(/\D/g, "").length >= 9;
      error.hidden = !!ok;
      if (!ok) (form.elements.name.value.trim() ? form.elements.phone : form.elements.name).focus();
      return !!ok;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!Object.keys(cart).length || !valid()) return;
      var url = "https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(orderText());
      var w = window.open(url, "_blank");
      if (w) w.opener = null; else location.href = url;
    });
    document.getElementById("cartMail").addEventListener("click", function (e) {
      e.preventDefault();
      if (!Object.keys(cart).length || !valid()) return;
      location.href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Premium Drones Georgia — " + label("lbOrder")) + "&body=" + encodeURIComponent(orderText());
    });
    var payBtn = document.getElementById("cartPay"), payErr = document.getElementById("cartPayError");
    payBtn.addEventListener("click", function () {
      if (paying || !payReady || !Object.keys(cart).length || !valid()) return;
      paying = true; payBtn.disabled = true; payErr.hidden = true;
      var order = {
        items: Object.keys(cart).map(function (k) { return { sku: k, qty: cart[k].q }; }),
        lang: document.documentElement.lang,
        customer: { name: form.elements.name.value.trim(), phone: form.elements.phone.value.trim(), address: form.elements.address.value.trim() }
      };
      fetch(PAY.endpoint + "/checkout", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) })
        .then(function (r) { return r.json().then(function (d) { return [r.ok, d]; }); })
        .then(function (x) {
          var d = x[1];
          if (!x[0] || !d || !d.url) throw new Error("checkout");
          try { localStorage.setItem("pdg_pay", JSON.stringify({ id: d.id, ref: d.ref, mode: d.mode, total: d.total, amount: d.amount, t: Date.now() })); } catch (e) { /* private mode */ }
          location.href = d.url;
        })
        .catch(function () { paying = false; payBtn.disabled = false; payErr.hidden = false; });
    });
    window.addEventListener("pageshow", function () { paying = false; payBtn.disabled = false; });
  }
  if (location.hash === "#cart") openCart();
  render();

  /* Online payment switches itself on when the server has the bank keys. */
  if (PAY.endpoint && dlg) {
    fetch(PAY.endpoint + "/payments/config", { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (c) {
        if (!c || !c.enabled) return;
        if (c.threshold) PAY.threshold = c.threshold;
        if (c.depositPercent) PAY.depositPercent = c.depositPercent;
        payReady = true; render();
      })
      .catch(function () { /* static preview or payments off */ });
  }

  /* Payment status page: show only what the bank confirms. */
  var ps = document.getElementById("payStatus");
  if (ps) {
    var qs = new URLSearchParams(location.search), ref = qs.get("ref") || "", saved = {};
    try { saved = JSON.parse(localStorage.getItem("pdg_pay") || "{}") || {}; } catch (e) { saved = {}; }
    if (saved.ref !== ref) saved = {};
    var okRef = /^PDG-\d{6}-[A-Z0-9]{6}$/.test(ref);
    if (okRef) {
      document.getElementById("payRefNo").textContent = ref;
      document.getElementById("payRef").hidden = false;
      document.getElementById("payWa").href = "https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(label("lb_pay_wa_text").replace("{ref}", ref));
    }
    var show = function (state, title, text) {
      ps.setAttribute("data-state", state);
      document.getElementById("payTitle").textContent = label(title);
      document.getElementById("payText").textContent = text;
      document.getElementById("payRetry").hidden = state !== "failed";
    };
    var tries = 0;
    var check = function () {
      fetch(PAY.endpoint + "/payments/status?" + (saved.id ? "id=" + encodeURIComponent(saved.id) : "ref=" + encodeURIComponent(ref)), { headers: { Accept: "application/json" } })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(new Error("status")); })
        .then(function (d) {
          if (d.ref && d.ref !== ref) throw new Error("ref");
          var s = d.status;
          if (s === "completed") {
            if (d.deposit || saved.mode === "deposit") {
              var t = label("lb_pay_dep_text").replace("{deposit}", fmt(d.amount));
              if (saved.total > d.amount) t += " " + label("lb_pay_rest").replace("{rest}", fmt(saved.total - d.amount));
              show("paid", "lb_pay_dep_done", t);
            } else show("paid", "lb_pay_done", label("lb_pay_done_text"));
            cart = {}; save(); render();
            try { localStorage.removeItem("pdg_pay"); } catch (e) { /* ignore */ }
          } else if (s === "rejected") {
            show("failed", "lb_pay_failed", label("lb_pay_failed_text"));
          } else if (["created", "processing", "auth_requested", "blocked", "partial_completed"].indexOf(s) > -1) {
            show("pending", "lb_pay_pending", label("lb_pay_pending_text"));
            if (tries++ < 6) setTimeout(check, 4000);
          } else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
        })
        .catch(function () {
          if (qs.get("r") === "fail") show("failed", "lb_pay_failed", label("lb_pay_failed_text"));
          else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
        });
    };
    if (okRef && PAY.endpoint) check(); else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
  }

  /* Parts filter */
  var search = document.getElementById("partSearch");
  if (!search) return;
  var chips = document.querySelectorAll("#partChips .chip"), cards = document.querySelectorAll("#partsGrid .product"), cat = "all";
  var none = document.getElementById("partsNone");
  function run() {
    var s = search.value.trim().toLowerCase(), shown = 0;
    cards.forEach(function (r) {
      var ok = (cat === "all" || r.dataset.cat === cat) && (!s || r.textContent.toLowerCase().indexOf(s) > -1);
      r.hidden = !ok; if (ok) shown++;
    });
    if (none) none.hidden = shown > 0;
  }
  search.addEventListener("input", run);
  var wanted = new URLSearchParams(location.search).get("cat");
  var askedFor = new URLSearchParams(location.search).get("q");
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      cat = c.dataset.filter;
      chips.forEach(function (o) { var on = o === c; o.classList.toggle("is-on", on); o.setAttribute("aria-pressed", String(on)); });
      run();
    });
    if (wanted && c.dataset.filter === wanted) c.click();
  });
  if (askedFor) { search.value = askedFor.slice(0, 60); run(); }
})();
