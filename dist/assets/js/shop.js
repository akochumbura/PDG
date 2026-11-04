/* PDG shop: cart (kept in this browser), order by WhatsApp or e-mail, and online payment through
   Bank of Georgia (hosted page: card, Apple Pay, Google Pay and the bank's other methods; installment / pay in parts
   through the BOG calculator when /api/payments/config lists them). The Pay button appears only when /api/payments/config
   says the bank keys are set (docs/07-payments.md). Orders under the threshold are paid in full,
   larger ones pay a deposit online. The payment page (payment.html) shows only what the bank confirms. */
(function () {
  "use strict";
  var KEY = "pdg_cart", WHATSAPP = "995550004333", EMAIL = "info@premium-drones.ge";
  var cart = {};
  try { cart = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { cart = {}; }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) { /* private mode */ } }
  /* 14 Oct 2026: products now use the XAG manufacturer code (e.g. 09-017-00073); drop items saved under the old invoice codes. */
  (function () { var old = Object.keys(cart).filter(function (k) { return /^P0\d{8}$/.test(k); }); old.forEach(function (k) { delete cart[k]; }); if (old.length) save(); })();
  function fmt(n) { return "₾" + Number(n).toLocaleString("en-US"); }
  function totals() { var t = 0, c = 0; Object.keys(cart).forEach(function (k) { t += cart[k].p * cart[k].q; c += cart[k].q; }); return [t, c]; }
  function label(id) { var e = document.getElementById(id); return e ? e.textContent.trim() : ""; }
  var LANG = document.documentElement.lang || "ka";
  var TXT = (window.PDG_CONTENT && window.PDG_CONTENT[LANG]) || {}, TXT_KA = (window.PDG_CONTENT && window.PDG_CONTENT.ka) || {};
  function tx(k) { return TXT[k] || TXT_KA[k] || ""; }
  /* Positive whole number within [min, max] (max only when a verified stock limit exists). */
  function clampInt(v, min, max) {
    var n = Math.floor(Number(v)); if (!isFinite(n)) n = min;
    if (n < min) n = min; if (max > 0 && n > max) n = max; return n;
  }
  function openWa(text) {
    document.dispatchEvent(new CustomEvent("pdg:track", { detail: { name: "whatsapp_click", params: { link_location: "product_quote" } } }));
    var url = "https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(text);
    var w = window.open(url, "_blank"); if (w) w.opener = null; else location.href = url;
  }

  /* Keep prices in the cart in step with the current page (prices may have changed since the item was added). */
  document.querySelectorAll(".add-btn[data-sku]").forEach(function (b) {
    var item = cart[b.dataset.sku];
    if (item) {
      item.p = Number(b.dataset.price); item.n = b.dataset.name;
      var box = b.parentNode.querySelector(".qty-input"), mx = box ? Number(box.max) || 0 : 0;
      if (mx > 0) { item.m = mx; item.q = clampInt(item.q, 1, mx); }
    }
  });
  Object.keys(cart).forEach(function (k) { var it = cart[k]; if (!it || !(it.q > 0) || !(it.p >= 0)) delete cart[k]; });
  save();

  var PAY = window.PDG_PAY || {}, payReady = false, paying = false;
  /* Payment TEST MODE, preview addresses (*.pages.dev) only: open any preview page with ?paydemo=1. A pretend bank answers in
     the browser; nothing reaches Bank of Georgia or the PDG server, no money moves. Never active on premium-drones.ge. */
  var DEMO = false;
  try {
    if (/\.pages\.dev$/.test(location.hostname)) {
      if (/[?&]paydemo=1/.test(location.search)) sessionStorage.setItem("pdg_paydemo", "1");
      if (/[?&]paydemo=0/.test(location.search)) sessionStorage.removeItem("pdg_paydemo");
      DEMO = sessionStorage.getItem("pdg_paydemo") === "1";
    }
  } catch (e) { DEMO = false; }
  var demoRef = function () { var d = new Date(); return "PDG-" + String(d.getFullYear()).slice(2) + ("0" + (d.getMonth() + 1)).slice(-2) + ("0" + d.getDate()).slice(-2) + "-DEMO01"; };
  /* Delivery (owner, 16 Oct 2026): PAY.shippingFee under PAY.freeFrom, free from it; pickup in Tbilisi is free. The server applies the same rule. */
  var FEE = PAY.shippingFee || 30, FREE = PAY.freeFrom || 100;
  function pickup() { var f = document.getElementById("cartForm"), r = f && f.elements.delivery; return !!(r && r.value === "pickup"); }
  function ship(goods) { return pickup() || goods >= FREE ? 0 : FEE; }
  function payAmount(goods, total) { return goods >= PAY.threshold ? Math.min(Math.ceil(total * PAY.depositPercent / 100), PAY.threshold - 1) : total; }
  var badge = document.getElementById("cartCount"), dlg = document.getElementById("cart");
  var form = document.getElementById("cartForm");

  function orderText() {
    var lines = Object.keys(cart).map(function (k) {
      var it = cart[k];
      return "- " + it.n + " (" + k + ") × " + it.q + " = " + fmt(it.p * it.q);
    });
    var g = totals()[0], sh = ship(g);
    var text = "Premium Drones Georgia — " + label("lbOrder") + "\n" + lines.join("\n") + "\n"
      + label("lbShip") + ": " + (pickup() ? label("lbPickup") : (sh ? fmt(sh) : label("lbFreeWord"))) + "\n"
      + label("lbTotal") + ": " + fmt(g + sh);
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
      /* Product name opens its page (owner, 4 Nov 2026); items without a page open the parts list filtered to their code. */
      var name = document.createElement("a"); name.className = "ci-name"; name.textContent = tx("pn_" + k.replace(/[^A-Za-z0-9]/g, "_")) || it.n;
      var lp = document.documentElement.lang === "ka" ? "" : "/" + document.documentElement.lang;
      name.href = lp + ((window.PDG_LINKS || {})[k] || "/shop?q=" + encodeURIComponent(k) + "#parts");
      var qty = document.createElement("span"); qty.className = "ci-qty";
      var count = document.createElement("output"); count.textContent = it.q;
      qty.append(btn("−", function () { change(k, -1); }, label("lbLess")), count, btn("+", function () { change(k, 1); }, label("lbMore")));
      var price = document.createElement("span"); price.className = "ci-price"; price.textContent = fmt(it.p * it.q);
      li.append(name, qty, price, btn("×", function () { delete cart[k]; save(); render(); }, label("lbRemove")));
      list.appendChild(li);
    });
    var sh = ship(T[0]), total = T[0] + sh;
    showCartOffer(T[0]);
    document.getElementById("cartGoods").textContent = fmt(T[0]);
    document.getElementById("cartShip").textContent = pickup() ? label("lbFreeWord") : (sh ? fmt(sh) : label("lbFreeWord"));
    var fr = document.getElementById("cartFree");
    fr.hidden = !(sh > 0); fr.textContent = label("lbFree").replace("{free}", FREE);
    document.getElementById("cartTotal").textContent = fmt(total);
    var pay = document.getElementById("cartPay");
    if (pay) {
      var amount = payAmount(T[0], total), dep = T[0] >= PAY.threshold;
      pay.hidden = !payReady;
      pay.querySelector("span").textContent = label(dep ? "lbPayDeposit" : "lbPayFull") + " · " + fmt(amount);
      var dn = document.getElementById("cartDeposit");
      dn.hidden = !(payReady && dep);
      if (dep) dn.textContent = label("lbDeposit").replace("{pct}", PAY.depositPercent).replace("{deposit}", fmt(amount)).replace("{rest}", fmt(total - amount));
      /* Simple cart when online payment is on (owner, 4 Nov 2026): one red pay button, one installment button,
         WhatsApp / e-mail as one small line of links. */
      var wa = document.getElementById("cartWa"), ml = document.getElementById("cartMail"), alt = document.getElementById("cartAlt");
      wa.hidden = payReady; ml.hidden = payReady; if (alt) alt.hidden = !payReady;
      document.getElementById("cartNote").hidden = payReady;
      document.getElementById("cartPayNote").hidden = !payReady;
      var inst = payReady && PAY.inst, ln = document.getElementById("cartLoan");
      if (ln) {
        ln.hidden = !inst;
        /* One installment button: Bank of Georgia installment, or pay in parts when only that is switched on. */
        document.getElementById("cartLoanBtn").hidden = !(inst && inst.loan);
        document.getElementById("cartBnplBtn").hidden = !(inst && inst.bnpl && !inst.loan);
      }
    }
  }
  /* Cart package offer (owner brief, 4 Nov 2026): the components in the cart - loose items and the contents of package lines, each counted
     once - are compared with every combination of approved packages (one drone each). When a valid combination is cheaper, one inline
     offer shows it with the exact saving; the cart changes only when the customer presses the button. Other items are untouched. */
  var PKG = window.PDG_PKGS || null;
  function cartBest() {
    if (!PKG) return null;
    var keys = Object.keys(PKG.items), pool = {}, drones = 0, cur = 0, involved = [], bySku = {}, pk = {};
    keys.forEach(function (k) { pool[k] = 0; bySku[PKG.items[k].sku] = k; });
    PKG.packages.forEach(function (p) { pk[p.sku] = p; });
    Object.keys(cart).forEach(function (s) {
      var it = cart[s];
      if (s === PKG.platform.sku) { drones += it.q; cur += it.p * it.q; involved.push(s); }
      else if (bySku[s]) { pool[bySku[s]] += it.q; cur += it.p * it.q; involved.push(s); }
      else if (pk[s]) { drones += it.q; keys.forEach(function (k) { pool[k] += (pk[s].q[k] || 0) * it.q; }); cur += it.p * it.q; involved.push(s); }
    });
    if (!drones || drones > 12) return null;
    var P = PKG.packages, best = null;
    function cost(counts) {
      var need = {}, n = 0, t = 0;
      keys.forEach(function (k) { need[k] = 0; });
      P.forEach(function (p, i) { if (!counts[i]) return; n += counts[i]; t += p.price * counts[i]; keys.forEach(function (k) { need[k] += (p.q[k] || 0) * counts[i]; }); });
      if (keys.some(function (k) { return need[k] > pool[k]; })) return null;
      t += (drones - n) * PKG.platform.price;
      keys.forEach(function (k) { t += (pool[k] - need[k]) * PKG.items[k].price; });
      return t;
    }
    (function rec(i, left, counts) {
      if (i === P.length) { var t = cost(counts); if (t !== null && (!best || t < best.t)) best = { t: t, counts: counts.slice() }; return; }
      for (var c = 0; c <= left; c++) { counts[i] = c; rec(i + 1, left - c, counts); }
      counts[i] = 0;
    })(0, drones, []);
    if (!best || best.t >= cur) return null;
    var same = P.every(function (p, i) { return (best.counts[i] || 0) === ((cart[p.sku] || {}).q || 0); });
    if (same) return null;
    return { t: best.t, saving: cur - best.t, counts: best.counts, pool: pool, drones: drones, involved: involved, keys: keys };
  }
  function cartApply(o) {
    o.involved.forEach(function (s) { delete cart[s]; });
    var n = 0, need = {};
    o.keys.forEach(function (k) { need[k] = 0; });
    PKG.packages.forEach(function (p, i) {
      var c = o.counts[i]; if (!c) return;
      n += c; cart[p.sku] = { n: p.name, p: p.price, q: c, m: p.max };
      o.keys.forEach(function (k) { need[k] += (p.q[k] || 0) * c; });
    });
    if (o.drones - n > 0) cart[PKG.platform.sku] = { n: PKG.platform.name, p: PKG.platform.price, q: o.drones - n, m: PKG.platform.max };
    o.keys.forEach(function (k) { var r = o.pool[k] - need[k], it = PKG.items[k]; if (r > 0) cart[it.sku] = { n: it.name, p: it.price, q: r, m: it.max }; });
    save(); render();
  }
  var cartOffer = null;
  function showCartOffer(goods) {
    var box = document.getElementById("cartOffer"); if (!box) return;
    cartOffer = cartBest(); box.hidden = !cartOffer; if (!cartOffer) return;
    var names = PKG.packages.map(function (p, i) { var c = cartOffer.counts[i]; return c ? (c > 1 ? c + " × " : "") + p.short : ""; }).filter(Boolean).join(" + ");
    document.getElementById("cartOfferText").textContent = tx("cart_offer").replace("{names}", names).replace("{total}", fmt(goods - cartOffer.saving)).replace("{saving}", fmt(cartOffer.saving));
  }
  document.addEventListener("click", function (e) { if (e.target.closest && e.target.closest("#cartOfferBtn") && cartOffer) cartApply(cartOffer); });
  function change(k, d) {
    if (!cart[k]) return;
    var q = cart[k].q + d;
    if (q < 1) delete cart[k]; else cart[k].q = clampInt(q, 1, cart[k].m || 0);
    save(); render();
  }
  function addItem(sku, name, price, q, max) {
    if (!(price >= 0) || !(q >= 1)) return;
    cart[sku] = cart[sku] || { n: name, p: price, q: 0 };
    if (max > 0) cart[sku].m = max;
    cart[sku].q = clampInt(cart[sku].q + q, 1, cart[sku].m || 0);
  }
  function openCart() { if (dlg && dlg.showModal && !dlg.open) { dlg.showModal(); document.body.classList.add("modal-open"); } }

  document.addEventListener("click", function (e) {
    var step = e.target.closest(".qty-btn");
    if (step) {
      var inp = step.parentNode.querySelector(".qty-input");
      var min = Number(inp.min) || 0, max = Number(inp.max) || 0;
      inp.value = clampInt(Number(inp.value) + Number(step.dataset.step), min, max);
      inp.dispatchEvent(new Event("input", { bubbles: true }));
      return;
    }
    var quote = e.target.closest(".quote-btn");
    if (quote) { openWa(tx("quote_msg") + "\n" + quote.dataset.name + " (" + quote.dataset.sku + ")"); return; }
    var add = e.target.closest(".add-btn");
    if (add) {
      var k = add.dataset.sku, box = add.parentNode.querySelector(".qty-input");
      var q = box ? clampInt(box.value, 1, Number(box.max) || 0) : 1;
      addItem(k, add.dataset.name, Number(add.dataset.price), q, box ? Number(box.max) || 0 : 0);
      if (box) box.value = 1;
      save(); render();
      add.classList.add("is-added");
      setTimeout(function () { add.classList.remove("is-added"); }, 900);
      return;
    }
    if (e.target.closest(".cart-link") && dlg) { e.preventDefault(); openCart(); return; }
    if (dlg && (e.target === dlg || e.target.id === "cartClose")) dlg.close();
  });
  if (dlg) dlg.addEventListener("close", function () { document.body.classList.remove("modal-open"); });
  if (dlg) dlg.addEventListener("change", function (e) { if (e.target && e.target.name === "delivery") render(); });

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
      document.dispatchEvent(new CustomEvent("pdg:track", { detail: { name: "whatsapp_order", params: { link_location: "cart" } } }));
      var w = window.open(url, "_blank");
      if (w) w.opener = null; else location.href = url;
    });
    document.getElementById("cartMail").addEventListener("click", function (e) {
      e.preventDefault();
      if (!Object.keys(cart).length || !valid()) return;
      document.dispatchEvent(new CustomEvent("pdg:track", { detail: { name: "email_order", params: { link_location: "cart" } } }));
      location.href = "mailto:" + EMAIL + "?subject=" + encodeURIComponent("Premium Drones Georgia — " + label("lbOrder")) + "&body=" + encodeURIComponent(orderText());
    });
    var payBtn = document.getElementById("cartPay"), payErr = document.getElementById("cartPayError");
    var startCheckout = function (plan) {
      var order = {
        items: Object.keys(cart).map(function (k) { return { sku: k, qty: cart[k].q }; }),
        lang: document.documentElement.lang,
        delivery: pickup() ? "pickup" : "delivery",
        customer: { name: form.elements.name.value.trim(), phone: form.elements.phone.value.trim(), address: form.elements.address.value.trim() }
      };
      if (plan) order.plan = plan;
      if (DEMO) {
        var T = totals(), tot = T[0] + ship(T[0]), dep = !plan && T[0] >= PAY.threshold, ref = demoRef();
        var d0 = { id: "demo", ref: ref, mode: plan ? plan.kind : dep ? "deposit" : "full", total: tot, amount: plan ? tot : payAmount(T[0], tot), url: (document.documentElement.lang === "ka" ? "" : "/" + document.documentElement.lang) + "/payment?ref=" + ref };
        try { localStorage.setItem("pdg_pay", JSON.stringify({ id: d0.id, ref: d0.ref, mode: d0.mode, total: d0.total, amount: d0.amount, t: Date.now() })); } catch (e) { /* private mode */ }
        return new Promise(function (ok) { setTimeout(function () { ok(d0); }, 500); });
      }
      return fetch(PAY.endpoint + "/checkout", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) })
        .then(function (r) { return r.json().then(function (d) { return [r.ok, d]; }); })
        .then(function (x) {
          var d = x[1];
          if (!x[0] || !d || !d.url) throw new Error("checkout");
          try { localStorage.setItem("pdg_pay", JSON.stringify({ id: d.id, ref: d.ref, mode: d.mode, total: d.total, amount: d.amount, t: Date.now() })); } catch (e) { /* private mode */ }
          return d;
        });
    };
    var payFail = function () { paying = false; payBtn.disabled = false; payErr.hidden = false; };
    payBtn.addEventListener("click", function () {
      if (paying || !payReady || !Object.keys(cart).length || !valid()) return;
      paying = true; payBtn.disabled = true; payErr.hidden = true;
      startCheckout(null).then(function (d) { location.href = d.url; }).catch(payFail);
    });
    /* Installment / pay in parts: the Bank of Georgia calculator (bog-sdk.js) lets the visitor pick the term; the order is then
       created on our server with that term (full amount, no deposit) and the SDK continues with the bank's application. */
    var sdk = null;
    var loadSdk = function () {
      if (DEMO && !(window.BOG && window.BOG.Calculator)) {
        /* Pretend calculator (TEST MODE): the real one comes from Bank of Georgia once the keys exist. */
        window.BOG = { Calculator: { open: function (o) {
          var box = document.createElement("div");
          box.setAttribute("style", "position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.5);display:grid;place-items:center;padding:16px");
          var months = o.bnpl ? [4] : [6, 12, 24, 36];
          box.innerHTML = '<div style="background:#fff;color:#1c1c1c;max-width:380px;width:100%;padding:20px;border-radius:8px;font:15px/1.45 system-ui,sans-serif">'
            + '<p style="margin:0 0 4px;font-size:12px;color:#c00;font-weight:600">TEST — pretend Bank of Georgia calculator</p>'
            + '<h3 style="margin:0 0 12px">' + (o.bnpl ? "ნაწილ-ნაწილ გადახდა" : "განვადება") + ' · ₾' + o.amount.toLocaleString("en-US") + '</h3>'
            + months.map(function (m, i) { return '<label style="display:block;padding:8px 0"><input type="radio" name="dm" value="' + m + '"' + (i ? "" : " checked") + '> ' + m + ' თვე</label>'; }).join("")
            + '<p style="font-size:12px;color:#666">Real terms and monthly amounts come only from the bank.</p>'
            + '<div style="display:flex;gap:8px;margin-top:12px"><button type="button" data-go style="flex:1;min-height:44px;background:#c00;color:#fff;border:0;border-radius:4px;font:inherit">გაგრძელება</button>'
            + '<button type="button" data-x style="flex:1;min-height:44px;background:#fff;border:1px solid #1c1c1c;border-radius:4px;font:inherit">დახურვა</button></div></div>';
          document.body.appendChild(box);
          box.querySelector("[data-x]").onclick = function () { box.remove(); if (o.onClose) o.onClose(); };
          box.querySelector("[data-go]").onclick = function () {
            var m = Number(box.querySelector("input[name=dm]:checked").value);
            o.onRequest({ month: m, discount_code: o.bnpl ? "zero" : "standard", amount: 0 }, function () {
              var saved = {}; try { saved = JSON.parse(localStorage.getItem("pdg_pay") || "{}"); } catch (e) { saved = {}; }
              location.href = (document.documentElement.lang === "ka" ? "" : "/" + document.documentElement.lang) + "/payment?ref=" + saved.ref;
            }, function () { box.remove(); });
          };
        } } };
        return Promise.resolve();
      }
      if (window.BOG && window.BOG.Calculator) return Promise.resolve();
      if (sdk) return sdk;
      sdk = new Promise(function (ok, no) {
        var sc = document.createElement("script");
        sc.src = "https://webstatic.bog.ge/bog-sdk/bog-sdk.js?version=2&client_id=" + encodeURIComponent(PAY.inst.clientId);
        sc.async = true; sc.onload = function () { window.BOG && window.BOG.Calculator ? ok() : no(new Error("sdk")); };
        sc.onerror = function () { sdk = null; no(new Error("sdk")); };
        document.head.appendChild(sc);
      });
      return sdk;
    };
    var openLoan = function (kind) {
      if (paying || !payReady || !PAY.inst || !Object.keys(cart).length || !valid()) return;
      payErr.hidden = true;
      var T = totals(), total = T[0] + ship(T[0]);
      loadSdk().then(function () {
        /* The cart is a modal <dialog> (browser top layer): close it, or the bank's calculator would open underneath it. */
        if (dlg && dlg.open) { dlg.close(); document.body.classList.remove("modal-open"); }
        window.BOG.Calculator.open({
          amount: total,
          bnpl: kind === "bnpl",
          onClose: function () { openCart(); },
          onRequest: function (sel, successCb, closeCb) {
            startCheckout({ kind: kind, month: Number(sel && sel.month), code: String(sel && sel.discount_code || "") })
              .then(function (d) { successCb(d.id); })
              .catch(function () { closeCb(); openCart(); payErr.hidden = false; });
          },
          onComplete: function () { /* the bank sends the visitor to our /payment page (redirect_urls) */ }
        });
      }).catch(function () { payErr.hidden = false; });
    };
    var lb = document.getElementById("cartLoanBtn"), bb = document.getElementById("cartBnplBtn");
    if (lb) lb.addEventListener("click", function () { openLoan("loan"); });
    if (bb) bb.addEventListener("click", function () { openLoan("bnpl"); });
    var aw = document.getElementById("cartAltWa");
    if (aw) aw.addEventListener("click", function (e) { e.preventDefault(); form.requestSubmit ? form.requestSubmit() : document.getElementById("cartWa").click(); });
    window.addEventListener("pageshow", function () { paying = false; payBtn.disabled = false; });
  }
  if (location.hash === "#cart") openCart();
  render();

  /* Online payment switches itself on when the server has the bank keys. */
  if (DEMO && dlg) {
    PAY.inst = { loan: true, bnpl: true, clientId: "demo" }; payReady = true; render();
    var toD = document.getElementById("termsOnline"); if (toD) toD.hidden = false;
  } else if (PAY.endpoint && dlg) {
    fetch(PAY.endpoint + "/payments/config", { headers: { Accept: "application/json" } })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (c) {
        if (!c || !c.enabled) return;
        if (c.threshold) PAY.threshold = c.threshold;
        if (c.depositPercent) PAY.depositPercent = c.depositPercent;
        PAY.inst = c.installment && c.installment.clientId ? c.installment : null;
        payReady = true; render();
        var to = document.getElementById("termsOnline"); if (to) to.hidden = false;
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
    if (DEMO && okRef && /-DEMO01$/.test(ref)) {
      var m = saved.mode;
      if (m === "loan" || m === "bnpl") show("pending", "lb_pay_pending", label("lb_pay_loan_text"));
      else if (m === "deposit") show("paid", "lb_pay_dep_done", label("lb_pay_dep_text").replace("{deposit}", fmt(saved.amount)) + " " + label("lb_pay_rest").replace("{rest}", fmt(saved.total - saved.amount)));
      else show("paid", "lb_pay_done", label("lb_pay_done_text"));
      var tn = document.createElement("p"); tn.setAttribute("style", "color:#c00;font-weight:600");
      tn.textContent = "TEST MODE — pretend bank, no money moved. (Open the page with ?paydemo=0 to leave test mode.)";
      ps.insertBefore(tn, ps.firstChild);
      okRef = false; tries = -1;
    }
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
          } else if (s === "refunded" || s === "refunded_partially") {
            show("refunded", "lb_pay_refunded", label("lb_pay_refunded_text"));
            try { localStorage.removeItem("pdg_pay"); } catch (e) { /* ignore */ }
          } else if (s === "rejected") {
            show("failed", "lb_pay_failed", label("lb_pay_failed_text"));
          } else if (["created", "processing", "auth_requested", "blocked", "partial_completed"].indexOf(s) > -1) {
            var loan = saved.mode === "loan" || saved.mode === "bnpl" || d.method === "bog_loan" || d.method === "bnpl";
            show("pending", "lb_pay_pending", label(loan ? "lb_pay_loan_text" : "lb_pay_pending_text"));
            if (tries++ < 6) setTimeout(check, 4000);
          } else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
        })
        .catch(function () {
          if (qs.get("r") === "fail") show("failed", "lb_pay_failed", label("lb_pay_failed_text"));
          else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
        });
    };
    if (tries === -1) { /* test mode answered */ } else if (okRef && PAY.endpoint) check(); else show("unknown", "lb_pay_unknown", label("lb_pay_unknown_text"));
  }

  /* Quantity fields: keep them positive whole numbers. */
  document.addEventListener("change", function (e) {
    var inp = e.target.closest(".qty-input"); if (!inp) return;
    inp.value = clampInt(inp.value, Number(inp.min) || 0, Number(inp.max) || 0);
    inp.dispatchEvent(new Event("input", { bubbles: true }));
  });

  /* XAG P150 MAX configurator (markup and data from scripts/configurator.py; on /shop, #configurator).
     Pricing (owner brief, 4 Nov 2026): items are priced one by one until the customer picks a package (preset) or accepts the offer.
     A chosen package stays applied while the selection still holds all its components (extras are priced on top); if a component
     falls below the package, pricing switches to item-by-item with a short note. When the selection holds every component of a
     package and that is cheaper than the displayed total, one inline offer shows the package total and the exact saving.
     The offer never changes quantities. Summary, phone bar, cart, WhatsApp message and the address (?c=…&m=…) use pcState(). */
  var pcBox = document.getElementById("platformConfig");
  if (pcBox) {
    var PC = JSON.parse(pcBox.dataset.config), pcRows = pcBox.querySelectorAll(".pcfg-row[data-key]");
    var pcKeys = Object.keys(PC.items);
    var pcMode = "", pcBroken = "", pcReady = false, pcOfferPkg = null;
    function pcInput(k) { return pcBox.querySelector('.pcfg-row[data-key="' + k + '"] .qty-input'); }
    function pcQ() { var q = {}; pcKeys.forEach(function (k) { var i = pcInput(k); q[k] = clampInt(i.value, 0, Number(i.max) || 0); }); return q; }
    function rowLabel(k) { var r = pcBox.querySelector('.pcfg-row[data-key="' + k + '"] .pcfg-label'); return r ? r.textContent.trim() : PC.items[k].name; }
    function fits(p, q) { return Object.keys(p.q).every(function (k) { return (q[k] || 0) >= p.q[k]; }); }
    function pkgBy(v) { return PC.packages.filter(function (x) { return x.sku === v || x.key === v; })[0] || null; }
    function withPkg(p, q) {
      var extras = [], t = p.price;
      pcKeys.forEach(function (k) { var d = q[k] - (p.q[k] || 0); if (d > 0) { extras.push([k, d]); t += d * PC.items[k].price; } });
      return { p: p, total: t, extras: extras };
    }
    function pcState() {
      var q = pcQ(), single = PC.platform.price, pkg = null, offer = null;
      pcKeys.forEach(function (k) { single += q[k] * PC.items[k].price; });
      var chosen = pcMode ? pkgBy(pcMode) : null;
      if (chosen && fits(chosen, q)) pkg = withPkg(chosen, q);
      var total = pkg ? pkg.total : single;
      PC.packages.forEach(function (p) {
        if (!fits(p, q) || (pkg && pkg.p === p)) return;
        var c = withPkg(p, q);
        if (c.total < total && (!offer || c.total < offer.total)) offer = c;
      });
      if (offer) offer.saving = total - offer.total;
      return { q: q, single: single, pkg: pkg, total: total, offer: offer };
    }
    /* Lines to show / send / add to the cart: one package SKU + extras, or the platform + items. */
    function pcLines(st) {
      var L = [];
      if (st.pkg) {
        L.push({ sku: st.pkg.p.sku, cn: st.pkg.p.name, label: tx("pc_pkg_line").replace("{name}", st.pkg.p.short), q: 1, unit: st.pkg.p.price, max: st.pkg.p.max, pkg: st.pkg.p });
        st.pkg.extras.forEach(function (x) { var it = PC.items[x[0]]; L.push({ sku: it.sku, cn: it.name, label: rowLabel(x[0]), q: x[1], unit: it.price, max: it.max, extra: true }); });
      } else {
        L.push({ sku: PC.platform.sku, cn: PC.platform.name, label: tx("pc_platform"), q: 1, unit: PC.platform.price, max: PC.platform.max });
        pcKeys.forEach(function (k) { if (st.q[k] > 0) { var it = PC.items[k]; L.push({ sku: it.sku, cn: it.name, label: rowLabel(k), q: st.q[k], unit: it.price, max: it.max }); } });
      }
      return L;
    }
    function contentsText(p) {
      var parts = [tx("pc_platform") + " × 1"];
      Object.keys(p.q).forEach(function (k) { parts.push(rowLabel(k) + " × " + p.q[k]); });
      return parts.join(", ");
    }
    function missing(st) {
      var m = [];
      if (!st.q.remotes) m.push(tx("pc_need_remote"));
      if (!st.q.batteries) m.push(tx("pc_need_batteries"));
      if (!st.q.chargers) m.push(tx("pc_need_chargers"));
      return m;
    }
    function pcParts(st) { var parts = []; pcKeys.forEach(function (k) { if (st.q[k] > 0) parts.push(k + "-" + st.q[k]); }); return parts; }
    function pcLink(st) {
      var parts = pcParts(st), lang = document.documentElement.lang, pre = lang && lang !== "ka" ? "/" + lang : "", qs = [];
      if (parts.length) qs.push("c=" + parts.join("_"));
      if (st.pkg) qs.push("m=" + st.pkg.p.key);
      var page = location.pathname.replace(/^\/(en|ru)(?=\/)/, "") || PC.page;
      return location.origin + pre + page + (qs.length ? "?" + qs.join("&") : "") + "#configurator";
    }
    /* The selection and the pricing mode live in the address (?c=…&m=…), so reloading, sharing and switching language keep them. */
    function pcRemember(st) {
      var parts = pcParts(st), u = new URL(location.href);
      u.searchParams.delete("kit"); u.searchParams.delete("p");
      if (parts.length) u.searchParams.set("c", parts.join("_")); else u.searchParams.delete("c");
      if (st.pkg) u.searchParams.set("m", st.pkg.p.key); else u.searchParams.delete("m");
      var next = u.pathname + (u.search ? decodeURIComponent(u.search) : "") + u.hash;
      if (next !== location.pathname + location.search + location.hash) { try { history.replaceState(history.state, "", next); } catch (e) { /* ignore */ } }
    }
    function pcShow() {
      var chosen = pcMode ? pkgBy(pcMode) : null;
      if (chosen && !fits(chosen, pcQ())) { pcBroken = chosen.short; pcMode = ""; }
      var st = pcState(), list = document.getElementById("pcList");
      pcRows.forEach(function (r) { r.classList.toggle("is-on", st.q[r.dataset.key] > 0); });
      list.textContent = "";
      var extrasShown = false;
      pcLines(st).forEach(function (l) {
        if (l.extra && !extrasShown) { extrasShown = true; var h = document.createElement("li"); h.className = "pcfg-li-head"; h.textContent = tx("pc_extras"); list.appendChild(h); }
        var li = document.createElement("li"), n = document.createElement("span"), v = document.createElement("span");
        n.className = "pcfg-li-name"; n.textContent = l.label + (l.pkg ? "" : " × " + l.q);
        if (l.pkg) { var sm = document.createElement("small"); sm.textContent = contentsText(l.pkg); n.appendChild(sm); li.className = "pcfg-li-pkg"; }
        v.className = "pcfg-li-price"; v.textContent = fmt(l.q * l.unit);
        li.append(n, v); list.appendChild(li);
      });
      var ap = document.getElementById("pcApplied");
      ap.classList.toggle("is-note", !st.pkg && !!pcBroken);
      ap.hidden = !st.pkg && !pcBroken;
      ap.textContent = st.pkg ? tx("pc_applied").replace("{name}", st.pkg.p.short) : (pcBroken ? tx("pc_broken").replace("{name}", pcBroken) : "");
      var ob = document.getElementById("pcOffer");
      pcOfferPkg = st.offer ? st.offer.p : null;
      if (ob) {
        ob.hidden = !st.offer;
        if (st.offer) document.getElementById("pcOfferText").textContent = tx("pc_offer").replace("{name}", st.offer.p.short).replace("{total}", fmt(st.offer.total)).replace("{saving}", fmt(st.offer.saving))
          + (st.offer.extras.length ? " " + tx("pc_offer_extras") : "");
      }
      var m = missing(st), rm = document.getElementById("pcRemind");
      rm.hidden = !m.length; if (m.length) rm.textContent = tx("pc_remind").replace("{list}", m.join(", "));
      document.getElementById("pcTotal").textContent = fmt(st.total);
      document.getElementById("pcBarTotal").textContent = fmt(st.total);
      var pressed = st.pkg ? st.pkg.p.sku : "";
      pcBox.querySelectorAll(".pcfg-preset").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.preset === pressed ? "true" : "false"); });
      if (pcReady) pcRemember(st);
      return st;
    }
    function setQ(q) { pcKeys.forEach(function (k) { var i = pcInput(k); i.value = clampInt(q[k] || 0, 0, Number(i.max) || 0); }); }
    /* Presets load exactly the package contents at the advertised price; extras can be added afterwards. */
    function preset(v) {
      var p = pkgBy(v); if (!p) return;
      var q = {}; Object.keys(p.q).forEach(function (k) { q[k] = p.q[k]; });
      pcMode = p.sku; pcBroken = ""; setQ(q); pcShow();
    }
    function pcSend() {
      var st = pcShow(), msg = [tx("pc_msg_title")];
      pcLines(st).forEach(function (l) {
        if (l.pkg) { msg.push("- " + l.pkg.name + " (" + l.sku + ") × 1 = " + fmt(l.unit)); msg.push("  " + tx("pc_contents_of") + ": " + contentsText(l.pkg)); }
        else msg.push("- " + (l.extra ? tx("pc_extras") + ": " : "") + l.label + " (" + l.sku + ") × " + l.q + " = " + fmt(l.q * l.unit));
      });
      if (st.pkg) msg.push(tx("pc_applied").replace("{name}", st.pkg.p.short));
      var m = missing(st); if (m.length) msg.push(tx("pc_msg_missing") + ": " + m.join(", "));
      msg.push(tx("pc_total") + ": " + fmt(st.total));
      msg.push(tx("pc_msg_link") + ": " + pcLink(st));
      openWa(msg.join("\n"));
    }
    pcBox.addEventListener("input", function (e) { if (e.target.classList.contains("qty-input")) pcShow(); });
    pcBox.addEventListener("change", function (e) { if (e.target.classList.contains("qty-input")) pcShow(); });
    pcBox.addEventListener("click", function (e) { var b = e.target.closest(".pcfg-preset"); if (b) preset(b.dataset.preset); });
    document.addEventListener("click", function (e) {
      var a = e.target.closest ? e.target.closest("[data-preset-link]") : null;
      if (a) preset(a.getAttribute("data-preset-link"));
    });
    var ob0 = document.getElementById("pcOfferBtn");
    if (ob0) ob0.addEventListener("click", function () { if (pcOfferPkg) { pcMode = pcOfferPkg.sku; pcBroken = ""; pcShow(); } });
    document.getElementById("pcWa").addEventListener("click", pcSend);
    document.getElementById("pcBarSend").addEventListener("click", pcSend);
    document.getElementById("pcCart").addEventListener("click", function () {
      var st = pcShow();
      pcLines(st).forEach(function (l) { addItem(l.sku, l.cn, l.unit, l.q, l.max); });
      save(); render();
      var b = this; b.classList.add("is-added"); setTimeout(function () { b.classList.remove("is-added"); }, 900);
    });
    /* Shared links (?c=batteries-4_chargers-2&m=pro) and package pages (?kit=starter); older links may still carry &p=. */
    var qs = new URLSearchParams(location.search), q0 = {}, kit = (qs.get("kit") || "").toLowerCase(), mode0 = (qs.get("m") || "").toLowerCase();
    String(qs.get("c") || "").split("_").forEach(function (x) { var m = /^([a-z0-9]+)-(\d+)$/.exec(x); if (m && PC.items[m[1]]) q0[m[1]] = Number(m[2]); });
    var kp = pkgBy(kit);
    if (kp && !qs.get("c")) { Object.keys(kp.q).forEach(function (k) { q0[k] = kp.q[k]; }); pcMode = kp.sku; }
    var mp = pkgBy(mode0); if (mp && fits(mp, q0)) pcMode = mp.sku;
    /* Owner, 4 Nov 2026: a new visit (no saved configuration in the address) starts with Starter. */
    if (!kp && !Object.keys(q0).some(function (k) { return q0[k] > 0; })) { var st0 = PC.packages[0]; Object.keys(st0.q).forEach(function (k) { q0[k] = st0.q[k]; }); pcMode = st0.sku; }
    setQ(q0);
    pcShow();
    pcReady = true;
    /* Phones: a slim total + send bar replaces the call/chat bar while the options are on screen and the summary total is not.
       It hides while the menu, chat, cart or the on-screen keyboard are open. */
    var bar = document.getElementById("pcBar"), sumEl = document.querySelector("#pcSummary .pcfg-total-row"), optEl = pcBox.querySelector(".pcfg-options");
    if (bar && "IntersectionObserver" in window) {
      var vis = { sum: false, opt: false }, typing = false;
      var upd = function () {
        var b = document.body, busy = b.classList.contains("nav-lock") || b.classList.contains("chat-open") || b.classList.contains("modal-open") || typing;
        var on = vis.opt && !vis.sum && !busy && window.matchMedia("(max-width: 768px)").matches;
        bar.classList.toggle("is-on", on); bar.setAttribute("aria-hidden", on ? "false" : "true");
        document.getElementById("pcBarSend").tabIndex = on ? 0 : -1;
        document.body.classList.toggle("pcfg-bar-on", on);
      };
      new IntersectionObserver(function (es) { es.forEach(function (e) { vis.sum = e.isIntersecting; }); upd(); }, { threshold: 0 }).observe(sumEl);
      new IntersectionObserver(function (es) { es.forEach(function (e) { vis.opt = e.isIntersecting; }); upd(); }, { threshold: 0 }).observe(optEl);
      window.addEventListener("resize", upd);
      new MutationObserver(upd).observe(document.body, { attributes: true, attributeFilter: ["class"] });
      document.addEventListener("focusin", function (e) { if (e.target.matches && e.target.matches("input:not([type=button]), textarea, select")) { typing = true; upd(); } });
      document.addEventListener("focusout", function () { typing = false; setTimeout(upd, 50); });
    }
  }

  /* Parts filter */
  var search = document.getElementById("partSearch");
  if (!search) return;
  var chips = document.querySelectorAll("#partChips .chip"), cards = document.querySelectorAll("#partsGrid .product"), cat = "all";
  var none = document.getElementById("partsNone");
  /* Sorting and min / max price (parts without a price are left out when a price range is set and go last when sorting by price). */
  var sortSel = document.getElementById("partSort"), pMin = document.getElementById("priceMin"), pMax = document.getElementById("priceMax");
  var grid = document.getElementById("partsGrid"), list = Array.prototype.slice.call(cards);
  function cardPrice(r) { var b = r.querySelector(".add-btn[data-price]"); return b ? Number(b.dataset.price) : null; }
  function cardName(r) { var h = r.querySelector("h3"); return h ? h.textContent.trim() : ""; }
  list.forEach(function (r, i) { r._i = i; r._p = cardPrice(r); r._n = cardName(r); });
  function num(el) { var v = el && el.value.trim(); return v === "" || v == null || isNaN(Number(v)) ? null : Number(v); }
  /* "Load more": only PAGE cards of the filtered, sorted list are shown at a time; search, category, sort and price range all apply to the whole catalog. */
  var PAGE = 24, limit = PAGE, moreBox = document.getElementById("partsMore"), moreBtn = document.getElementById("partsMoreBtn"), countEl = document.getElementById("partsCount");
  function run(keep) {
    if (keep !== true) limit = PAGE;
    var s = search.value.trim().toLowerCase(), lo = num(pMin), hi = num(pMax), matched = [];
    list.forEach(function (r) { r._m = false; });
    Array.prototype.slice.call(grid.children).forEach(function (r) {
      if (!r.classList || !r.classList.contains("product")) return;
      var ok = (cat === "all" || r.dataset.cat === cat) && (!s || (r.textContent + " " + (r.dataset.k || "")).toLowerCase().indexOf(s) > -1);
      if (ok && (lo !== null || hi !== null)) ok = r._p !== null && (lo === null || r._p >= lo) && (hi === null || r._p <= hi);
      if (ok) matched.push(r);
      r.hidden = true;
    });
    matched.forEach(function (r, i) { r.hidden = i >= limit; });
    if (none) none.hidden = matched.length > 0;
    if (moreBox) {
      var shown = Math.min(limit, matched.length), left = matched.length - shown;
      moreBox.hidden = matched.length === 0;
      if (countEl) countEl.textContent = tx("parts_count").replace("{n}", shown).replace("{total}", matched.length);
      if (moreBtn) { moreBtn.hidden = left <= 0; moreBtn.textContent = tx("parts_more").replace("{n}", Math.min(PAGE, left)); }
    }
  }
  if (moreBtn) moreBtn.addEventListener("click", function () {
    var before = limit; limit += PAGE; run(true);
    var first = Array.prototype.slice.call(grid.querySelectorAll(".product")).filter(function (r) { return !r.hidden; })[before];
    var link = first && first.querySelector("a, button"); if (link) link.focus({ preventScroll: false });
  });
  function order() {
    var m = sortSel ? sortSel.value : "", sorted = list.slice();
    var big = Infinity;
    if (m === "asc") sorted.sort(function (a, b) { return (a._p === null ? big : a._p) - (b._p === null ? big : b._p) || a._i - b._i; });
    else if (m === "desc") sorted.sort(function (a, b) { return (b._p === null ? -1 : b._p) - (a._p === null ? -1 : a._p) || a._i - b._i; });
    else if (m === "name") sorted.sort(function (a, b) { return a._n.localeCompare(b._n, document.documentElement.lang || "ka") || a._i - b._i; });
    else sorted.sort(function (a, b) { return a._i - b._i; });
    sorted.forEach(function (r) { grid.appendChild(r); });
    run();
  }
  if (sortSel) sortSel.addEventListener("change", order);
  [pMin, pMax].forEach(function (el) { if (el) el.addEventListener("input", run); });
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
  if (askedFor) { search.value = askedFor.slice(0, 60); }
  run();
})();
