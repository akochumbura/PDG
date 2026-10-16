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
      var name = document.createElement("span"); name.className = "ci-name"; name.textContent = tx("pn_" + k.replace(/[^A-Za-z0-9]/g, "_")) || it.n;
      var qty = document.createElement("span"); qty.className = "ci-qty";
      var count = document.createElement("output"); count.textContent = it.q;
      qty.append(btn("−", function () { change(k, -1); }, label("lbLess")), count, btn("+", function () { change(k, 1); }, label("lbMore")));
      var price = document.createElement("span"); price.className = "ci-price"; price.textContent = fmt(it.p * it.q);
      li.append(name, qty, price, btn("×", function () { delete cart[k]; save(); render(); }, label("lbRemove")));
      list.appendChild(li);
    });
    var sh = ship(T[0]), total = T[0] + sh;
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
      var wa = document.getElementById("cartWa");
      wa.classList.toggle("button-red", !payReady); wa.classList.toggle("button-line", payReady);
      document.getElementById("cartNote").hidden = payReady;
      document.getElementById("cartPayNote").hidden = !payReady;
    }
  }
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
        delivery: pickup() ? "pickup" : "delivery",
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

  /* Quantity fields: keep them positive whole numbers. */
  document.addEventListener("change", function (e) {
    var inp = e.target.closest(".qty-input"); if (!inp) return;
    inp.value = clampInt(inp.value, Number(inp.min) || 0, Number(inp.max) || 0);
    inp.dispatchEvent(new Event("input", { bubbles: true }));
  });

  /* XAG P150 MAX configurator (owner, 16 Oct 2026; platform page and P150 MAX page). Built by scripts/configurator.py.
     Starts with the platform only. Prices = shop prices item by item; when the selection contains a complete package,
     the existing package price (+ the remaining items at shop price) is offered with a switch. No other discounts. */
  var pcBox = document.getElementById("platformConfig");
  if (pcBox) {
    var pcSec = pcBox.closest("section") || document, PC = JSON.parse(pcBox.dataset.config), pcRows = pcBox.querySelectorAll(".pcfg-row[data-key]"), usePkg = null;
    function pcQ() { var q = {}; pcRows.forEach(function (r) { var i = r.querySelector(".qty-input"); q[r.dataset.key] = clampInt(i.value, 0, Number(i.max) || 0); }); return q; }
    function rowLabel(k) { var r = pcBox.querySelector('.pcfg-row[data-key="' + k + '"] .pcfg-name > span'); return r ? r.textContent.trim() : PC.items[k].name; }
    function itemName(sku, fallback) { return tx("pn_" + String(sku).replace(/[^A-Za-z0-9]/g, "_")) || fallback; }
    function single(q) { var t = PC.platform.price; Object.keys(PC.items).forEach(function (k) { t += q[k] * PC.items[k].price; }); return t; }
    function fits(p, q) { return Object.keys(p.q).every(function (k) { return (q[k] || 0) >= p.q[k]; }); }
    function withPkg(p, q) {
      var extras = [], t = p.price;
      Object.keys(PC.items).forEach(function (k) { var d = q[k] - (p.q[k] || 0); if (d > 0) { extras.push([k, d]); t += d * PC.items[k].price; } });
      return { p: p, total: t, extras: extras, exact: !extras.length };
    }
    function best(q) {
      var b = null;
      PC.packages.forEach(function (p) { if (!fits(p, q)) return; var o = withPkg(p, q); if (!b || o.total < b.total) b = o; });
      return b;
    }
    function state() {
      var q = pcQ(), s = single(q), b = best(q), cur = null;
      if (usePkg) { var p = PC.packages.filter(function (x) { return x.sku === usePkg; })[0]; if (p && fits(p, q)) cur = withPkg(p, q); else usePkg = null; }
      return { q: q, single: s, best: b, cur: cur, total: cur ? cur.total : s };
    }
    function lines(st) {
      var out = [];
      if (st.cur) {
        out.push({ sku: st.cur.p.sku, cn: st.cur.p.name, name: st.cur.p.name, q: 1, unit: st.cur.p.price, max: st.cur.p.max, pkg: st.cur.p });
        st.cur.extras.forEach(function (x) { var it = PC.items[x[0]]; out.push({ sku: it.sku, cn: it.name, name: itemName(it.sku, it.name), label: rowLabel(x[0]), q: x[1], unit: it.price, max: it.max }); });
      } else {
        out.push({ sku: PC.platform.sku, cn: PC.platform.name, name: itemName(PC.platform.sku, PC.platform.name), label: tx("pc_platform"), q: 1, unit: PC.platform.price, max: PC.platform.max });
        Object.keys(PC.items).forEach(function (k) { if (st.q[k] > 0) { var it = PC.items[k]; out.push({ sku: it.sku, cn: it.name, name: itemName(it.sku, it.name), label: rowLabel(k), q: st.q[k], unit: it.price, max: it.max }); } });
      }
      return out;
    }
    function contentsText(p) {
      var parts = [tx("pc_platform") + " × 1"];
      Object.keys(p.q).forEach(function (k) { parts.push(rowLabel(k) + " × " + p.q[k]); });
      return parts.join(", ");
    }
    function missing(st) {
      var m = [];
      if (!st.cur) {
        if (!st.q.remotes) m.push(tx("pc_need_remote"));
        if (!st.q.batteries) m.push(tx("pc_need_batteries"));
        if (!st.q.chargers) m.push(tx("pc_need_chargers"));
      }
      return m;
    }
    function link(st) {
      var parts = [];
      Object.keys(PC.items).forEach(function (k) { if (st.q[k] > 0) parts.push(k + "-" + st.q[k]); });
      var lang = document.documentElement.lang, pre = lang && lang !== "ka" ? "/" + lang : "";
      var u = location.origin + pre + PC.page + (parts.length || st.cur ? "?c=" + (parts.join("_") || "none") + (st.cur ? "&p=" + st.cur.p.key : "") : "");
      return u;
    }
    function pcShow() {
      var st = state(), list = document.getElementById("pcList"), L = lines(st);
      pcRows.forEach(function (r) {
        var q = st.q[r.dataset.key], it = PC.items[r.dataset.key];
        r.classList.toggle("is-on", q > 0);
        r.querySelector(".pcfg-line").textContent = q > 0 ? fmt(q * it.price) : "";
      });
      list.textContent = "";
      L.forEach(function (l) {
        var li = document.createElement("li"), n = document.createElement("span"), v = document.createElement("span");
        n.className = "pcfg-li-name"; n.textContent = (l.pkg ? l.pkg.name : l.label) + " × " + l.q;
        if (l.pkg) { var sm = document.createElement("small"); sm.textContent = contentsText(l.pkg); n.appendChild(document.createElement("br")); n.appendChild(sm); }
        v.className = "pcfg-li-price"; v.textContent = fmt(l.q * l.unit);
        li.append(n, v); list.appendChild(li);
      });
      var of = document.getElementById("pcOffer"), sw = document.getElementById("pcSwitch");
      var b = st.best, showB = b && !(st.cur && st.cur.p.sku === b.p.sku);
      if (st.cur && !showB) {
        of.hidden = false; of.classList.add("is-active");
        document.getElementById("pcOfferText").textContent = tx(st.cur.exact ? "pc_offer_exact" : "pc_offer_contains").replace("{name}", st.cur.p.short);
        document.getElementById("pcOfferPrice").textContent = tx("pc_offer_price").replace("{total}", fmt(st.cur.total)).replace("{single}", fmt(st.single)).replace("{save}", fmt(st.single - st.cur.total));
        sw.dataset.act = "off"; sw.querySelector("span").textContent = tx("pc_unswitch");
      } else if (showB) {
        of.hidden = false; of.classList.remove("is-active");
        document.getElementById("pcOfferText").textContent = tx(b.exact ? "pc_offer_exact" : "pc_offer_contains").replace("{name}", b.p.short);
        document.getElementById("pcOfferPrice").textContent = tx("pc_offer_price").replace("{total}", fmt(b.total)).replace("{single}", fmt(st.single)).replace("{save}", fmt(st.single - b.total));
        sw.dataset.act = b.p.sku; sw.querySelector("span").textContent = tx("pc_switch").replace("{name}", b.p.short);
      } else of.hidden = true;
      var m = missing(st), rm = document.getElementById("pcRemind");
      rm.hidden = !m.length; if (m.length) rm.textContent = tx("pc_remind").replace("{list}", m.join(", "));
      document.getElementById("pcTotal").textContent = fmt(st.total);
      document.getElementById("pcBarTotal").textContent = fmt(st.total);
      pcSec.querySelectorAll(".pcfg-pkg").forEach(function (el) {
        var p = PC.packages.filter(function (x) { return x.sku === el.querySelector(".pcfg-load").dataset.load; })[0];
        el.classList.toggle("is-match", !!(st.cur && st.cur.p.sku === p.sku));
      });
      return st;
    }
    function setQ(q) { pcRows.forEach(function (r) { r.querySelector(".qty-input").value = clampInt(q[r.dataset.key] || 0, 0, Number(r.querySelector(".qty-input").max) || 0); }); }
    function pcSend() {
      var st = pcShow(), L = lines(st), msg = [tx("pc_msg_title")];
      L.forEach(function (l) { msg.push("- " + (l.pkg ? l.pkg.name + " (" + contentsText(l.pkg) + ")" : l.label) + " (" + l.sku + ") × " + l.q + " = " + fmt(l.q * l.unit)); });
      var m = missing(st); if (m.length) msg.push(tx("pc_msg_missing") + ": " + m.join(", "));
      msg.push(tx("pc_total") + ": " + fmt(st.total));
      msg.push(tx("pc_msg_link") + ": " + link(st));
      openWa(msg.join("\n"));
    }
    pcBox.addEventListener("input", function (e) { if (e.target.classList.contains("qty-input")) pcShow(); });
    pcSec.addEventListener("click", function (e) {
      var ld = e.target.closest(".pcfg-load");
      if (ld) {
        var p = PC.packages.filter(function (x) { return x.sku === ld.dataset.load; })[0];
        var q = {}; Object.keys(PC.items).forEach(function (k) { q[k] = p.q[k] || 0; });
        setQ(q); usePkg = p.sku; pcShow();
        var sum = document.getElementById("pcSummary"); if (sum && sum.scrollIntoView) sum.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
    document.getElementById("pcSwitch").addEventListener("click", function () { var a = this.dataset.act; usePkg = a && a !== "off" ? a : null; pcShow(); });
    document.getElementById("pcWa").addEventListener("click", pcSend);
    document.getElementById("pcBarSend").addEventListener("click", pcSend);
    document.getElementById("pcCart").addEventListener("click", function () {
      var st = pcShow();
      lines(st).forEach(function (l) { addItem(l.sku, l.cn, l.unit, l.q, l.max); });
      save(); render();
      var b = this; b.classList.add("is-added"); setTimeout(function () { b.classList.remove("is-added"); }, 900);
    });
    /* Package comparison: localised contents and savings. */
    pcSec.querySelectorAll("[data-pkg-in]").forEach(function (el) { var p = PC.packages.filter(function (x) { return x.sku === el.dataset.pkgIn; })[0]; el.textContent = contentsText(p); });
    pcSec.querySelectorAll("[data-save]").forEach(function (el) { el.textContent = tx("pc_save").replace("{save}", fmt(Number(el.dataset.save))); });
    /* Shared links: ?c=batteries-4_chargers-2&p=starter, and the package pages' ?kit=starter. */
    var qs = new URLSearchParams(location.search), q0 = {}, kit = (qs.get("kit") || qs.get("p") || "").toLowerCase();
    String(qs.get("c") || "").split("_").forEach(function (x) { var m = /^([a-z0-9]+)-(\d+)$/.exec(x); if (m && PC.items[m[1]]) q0[m[1]] = Number(m[2]); });
    var kp = PC.packages.filter(function (x) { return x.key === kit; })[0];
    if (kp && !qs.get("c")) Object.keys(kp.q).forEach(function (k) { q0[k] = kp.q[k]; });
    setQ(q0); if (kp && fits(kp, pcQ())) usePkg = kp.sku;
    pcShow();
    /* Phones: a slim total + send bar while the summary is off screen (never over the summary itself). */
    var bar = document.getElementById("pcBar"), sumEl = document.getElementById("pcSummary"), optEl = pcBox.querySelector(".pcfg-options");
    if (bar && "IntersectionObserver" in window) {
      var vis = { sum: false, opt: false };
      var upd = function () { var on = vis.opt && !vis.sum; bar.classList.toggle("is-on", on); bar.setAttribute("aria-hidden", on ? "false" : "true"); document.getElementById("pcBarSend").tabIndex = on ? 0 : -1; };
      new IntersectionObserver(function (es) { es.forEach(function (e) { vis[e.target === sumEl ? "sum" : "opt"] = e.isIntersecting; }); upd(); }, { threshold: 0 }).observe(sumEl);
      new IntersectionObserver(function (es) { es.forEach(function (e) { vis.opt = e.isIntersecting; }); upd(); }, { threshold: 0 }).observe(optEl);
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
      var ok = (cat === "all" || r.dataset.cat === cat) && (!s || r.textContent.toLowerCase().indexOf(s) > -1);
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
