/* PDG shop: cart (kept in this browser), order by WhatsApp or e-mail, optional payment hook.
   Payments are NOT connected until payments-config.js has an endpoint (see docs/07-payments.md). */
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
    if (pay) pay.hidden = !(window.PDG_PAY && window.PDG_PAY.endpoint);
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
    document.getElementById("cartPay").addEventListener("click", function () {
      if (!valid()) return;
      var order = {
        items: Object.keys(cart).map(function (k) { return { sku: k, name: cart[k].n, qty: cart[k].q, price: cart[k].p }; }),
        total: totals()[0], currency: "GEL", lang: document.documentElement.lang,
        customer: { name: form.elements.name.value.trim(), phone: form.elements.phone.value.trim(), address: form.elements.address.value.trim() }
      };
      fetch(window.PDG_PAY.endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) })
        .then(function (r) { return r.json(); })
        .then(function (d) { if (d && d.url) location.href = d.url; else throw new Error("no url"); })
        .catch(function () { error.hidden = false; });
    });
  }
  if (location.hash === "#cart") openCart();
  render();

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
  chips.forEach(function (c) {
    c.addEventListener("click", function () {
      cat = c.dataset.filter;
      chips.forEach(function (o) { var on = o === c; o.classList.toggle("is-on", on); o.setAttribute("aria-pressed", String(on)); });
      run();
    });
  });
})();
