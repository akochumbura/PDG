(function () {
  /* Owner, 4 Nov 2026: the standalone platform page is gone; its address (and shared configurator links) forward to the shop configurator with the same parameters. */
  (function () {
    var m = /^(\/(?:en|ru))?\/p150-max-platform(?:\.html)?\/?$/.exec(location.pathname);
    if (m) location.replace((m[1] || "") + "/shop" + location.search + "#configurator");
  })();
  /* 5 Nov 2026: parts have their own page and previous models live on /drones; old /shop#parts and /shop#previous-models links forward. */
  (function () {
    var m = /^(\/(?:en|ru))?\/shop(?:\.html)?\/?$/.exec(location.pathname);
    if (!m) return;
    if (location.hash === "#parts") location.replace((m[1] || "") + "/parts" + location.search);
    else if (location.hash === "#previous-models") location.replace((m[1] || "") + "/drones#previous-models");
  })();
  "use strict";
  const root = document.documentElement;
  const lang = ["ka", "en", "ru"].includes(root.lang) ? root.lang : "ka";
  const translations = window.PDG_CONTENT || {};
  const storage = {
    get(key) { try { return localStorage.getItem(key); } catch (_) { return null; } },
    set(key, value) { try { localStorage.setItem(key, value); } catch (_) { /* Optional persistence. */ } }
  };
  function t(key) {
    if (translations[lang] && Object.prototype.hasOwnProperty.call(translations[lang], key)) return translations[lang][key];
    const text = document.querySelector('[data-i18n="' + key + '"]');
    if (text) return text.textContent.trim();
    const label = document.querySelector('[data-i18n-aria="' + key + '"]');
    if (label) return label.getAttribute("aria-label");
    return (translations.en && translations.en[key]) || key;
  }
  function setTheme(theme) {
    root.dataset.theme = theme === "dark" ? "dark" : "light";
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.content = root.dataset.theme === "dark" ? "#191918" : "#ffffff";
    const toggle = document.getElementById("themeToggle");
    if (toggle) toggle.setAttribute("aria-pressed", String(root.dataset.theme === "dark"));
  }
  setTheme(storage.get("pdge-theme") || "light");
  document.getElementById("themeToggle")?.addEventListener("click", () => {
    setTheme(root.dataset.theme === "dark" ? "light" : "dark");
    storage.set("pdge-theme", root.dataset.theme);
  });
  storage.set("pdge-lang", lang);
  /* Language links carry the current query and anchor. They are rebuilt on click, so state the page wrote to the URL
     after loading (e.g. the configurator's ?c=…) survives a language change (audit 19 Oct 2026). */
  const langHref = (link) => {
    const targetLanguage = link.dataset.lang;
    const relativePath = location.pathname.replace(/^\/(en|ru)(?=\/|$)/, "");
    const path = relativePath === "/index.html" || relativePath === "" ? "/" : relativePath;
    const prefix = targetLanguage === "ka" ? "" : "/" + targetLanguage;
    link.href = prefix + path + location.search + location.hash;
  };
  document.querySelectorAll("[data-lang]").forEach((link) => {
    langHref(link);
    ["click", "focus", "pointerenter"].forEach((ev) => link.addEventListener(ev, () => langHref(link)));
    if (link.dataset.lang === lang) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  const langBtn = document.getElementById("langBtn"), langList = document.getElementById("langList");
  if (langBtn && langList) {
    const setLang = (open) => { langList.hidden = !open; langBtn.setAttribute("aria-expanded", String(open)); };
    langBtn.addEventListener("click", (e) => { e.stopPropagation(); setLang(langList.hidden); });
    document.addEventListener("click", (e) => { if (!langList.hidden && !e.target.closest(".lang-menu")) setLang(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !langList.hidden) { setLang(false); langBtn.focus(); } });
  }
  const reveal = document.querySelectorAll("[data-reveal]");
  if (reveal.length && "IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    root.classList.add("js-reveal");
    const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-in"); io.unobserve(e.target); } }), { rootMargin: "0px 0px -8% 0px" });
    reveal.forEach((el) => io.observe(el));
    // Safety net: if the observer never fires (print, odd browsers, anchors jumped to), nothing stays hidden.
    setTimeout(() => reveal.forEach((el) => el.classList.add("is-in")), 4000);
    if (location.hash) reveal.forEach((el) => el.classList.add("is-in"));
  }
  /* Owner, 6 Nov 2026: the phone call/write bar only on the contact, service and academy pages; elsewhere the round chat button. */
  if (/^\/(en\/|ru\/)?(consultation|service|academy)(\.html)?\/?$/.test(location.pathname)) document.body.classList.add("has-mbar");
  const header = document.querySelector(".site-header");
  if (header) {
    /* Phones (owner, 5 Nov 2026): a red "prices and packages" strip appears under the header once the visitor scrolls down
       (not on /shop itself). It overlays the page, so nothing jumps. */
    const onShop = /^\/(en\/|ru\/)?shop\/?$/.test(location.pathname);
    const strip = header.querySelector(".price-strip");
    /* Shown while scrolling down, fades away when scrolling up (owner, 5 Nov 2026). */
    let lastY = window.scrollY, turn = window.scrollY, dirUp = false;
    /* Never two identical buttons on one screen (owner, 6 Nov 2026): while a button to the shop is visible in the page, the strip stays away. */
    let shopBtnsSeen = 0;
    if (strip && "IntersectionObserver" in window) {
      const seen = new Set();
      const io = new IntersectionObserver((es) => { es.forEach((e) => { if (e.isIntersecting) seen.add(e.target); else seen.delete(e.target); }); shopBtnsSeen = seen.size; onScroll(); }, { rootMargin: "-110px 0px 0px 0px" });
      document.querySelectorAll("main a.button[href]").forEach((a) => { if (/^\/(en\/|ru\/)?shop(\.html)?\/?$/.test(a.pathname)) io.observe(a); });
    }
    const onScroll = () => {
      const y = window.scrollY;
      header.classList.toggle("is-scrolled", y > 8);
      if (strip && !onShop) {
        /* Turning points (owner, 6 Nov 2026): shows after 24px of travel down, hides after 16px up; tiny jitters (<3px) are ignored. */
        const d = y - lastY;
        let on = header.classList.contains("strip-on");
        if (Math.abs(d) >= 3) {
          if (d > 0) { if (dirUp) { dirUp = false; turn = lastY; } if (y - turn > 24) on = true; }
          else { if (!dirUp) { dirUp = true; turn = lastY; } if (turn - y > 16) on = false; }
          lastY = y;
        }
        if (y < 280 || shopBtnsSeen) on = false;
        if (on !== header.classList.contains("strip-on")) { header.classList.toggle("strip-on", on); strip.setAttribute("aria-hidden", on ? "false" : "true"); strip.tabIndex = on ? 0 : -1; }
      }
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
  const nav = document.getElementById("site-nav");
  const navToggle = document.getElementById("navToggle");
  /* Phone menu: while it is open the page behind it does not scroll (the menu scrolls on its own). */
  const pageParts = Array.from(document.querySelectorAll("#main, footer, .mobile-bar, .chat-fab, .chat-panel"));
  /* The page is pinned with position:fixed at its current offset, so opening and closing the menu keeps the reading position (audit 19 Oct 2026). */
  let lockedAt = null;
  function lockPage(on) {
    const body = document.body;
    if (on && lockedAt === null) {
      lockedAt = window.scrollY;
      body.style.top = -lockedAt + "px";
      body.classList.add("nav-lock");
    } else if (!on && lockedAt !== null) {
      const y = lockedAt;
      lockedAt = null;
      body.classList.remove("nav-lock");
      body.style.top = "";
      window.scrollTo({ top: y, left: 0, behavior: "instant" });
    }
    pageParts.forEach((el) => { if (on) el.setAttribute("inert", ""); else el.removeAttribute("inert"); });
  }
  /* "Why PDG" accordion: keep the opened text clear of the phone bottom bar */
  document.querySelectorAll(".why-acc").forEach((d) => d.addEventListener("toggle", () => {
    if (!d.open) return;
    const need = d.getBoundingClientRect().bottom - (window.innerHeight - 96);
    if (need > 0) window.scrollBy({ top: need, behavior: "smooth" });
  }));

  /* Current page in the menu: brand red (and its group button) */
  (function markCurrent() {
    const clean = (p) => p.replace(/^\/(en|ru)(?=\/|$)/, "").replace(/\.html$/, "").replace(/\/+$/, "") || "/";
    const here = clean(location.pathname);
    document.querySelectorAll("#site-nav a[href]:not([data-lang])").forEach((a) => {
      const u = new URL(a.getAttribute("href"), location.origin);
      if (u.origin !== location.origin || u.hash || u.search) return;
      if (clean(u.pathname) !== here) return;
      a.setAttribute("aria-current", "page");
      const g = a.closest(".nav-group"); if (g) g.querySelector(".nav-group-btn")?.classList.add("is-current");
    });
  })();
  /* iOS: a swipe on the header must not move the page behind the open menu */
  document.querySelector(".site-header")?.addEventListener("touchmove", (e) => {
    if (document.body.classList.contains("nav-lock") && !e.target.closest("#site-nav")) e.preventDefault();
  }, { passive: false });
  function closeNav(restoreFocus) {
    const wasOpen = nav?.classList.contains("is-open");
    nav?.classList.remove("is-open");
    navToggle?.setAttribute("aria-expanded", "false");
    lockPage(false);
    closeGroups();
    if (wasOpen && restoreFocus === true) navToggle?.focus({ preventScroll: true });
  }
  navToggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(open));
    lockPage(open);
    if (open) { const first = nav.querySelector(".nav-search, a, button"); first?.focus({ preventScroll: true }); nav.scrollTop = 0; } else closeGroups();
  });
  window.addEventListener("pageshow", () => closeNav());
  nav?.addEventListener("click", (event) => { if (event.target.closest("a")) closeNav(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape" && nav?.classList.contains("is-open")) closeNav(true); });
  /* Products / Services submenus: click or keyboard opens, outside click or Escape closes. */
  const groups = Array.from(document.querySelectorAll(".nav-group-btn"));
  function closeGroups(except) { groups.forEach((b) => { if (b !== except) b.setAttribute("aria-expanded", "false"); }); }
  groups.forEach((b) => b.addEventListener("click", () => {
    const open = b.getAttribute("aria-expanded") !== "true";
    closeGroups(b); b.setAttribute("aria-expanded", String(open));
  }));
  document.addEventListener("click", (event) => { if (!event.target.closest(".nav-group")) closeGroups(); });
  /* Escape also wins over hover: the hovered menu stays closed until the pointer leaves it. */
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    const open = groups.find((b) => b.getAttribute("aria-expanded") === "true");
    closeGroups();
    document.querySelectorAll(".nav-group:hover").forEach((g) => g.classList.add("nav-hover-off"));
    if (open && open.closest(".nav-group").contains(document.activeElement)) open.focus();
  });
  document.querySelectorAll(".nav-group").forEach((g) => g.addEventListener("mouseleave", () => g.classList.remove("nav-hover-off")));
  const desktop = window.matchMedia("(min-width: 901px)");
  desktop.addEventListener?.("change", (event) => { if (event.matches) closeNav(); });

  /* Site search: header button (or Ctrl/Cmd+K, or "/") opens the panel; the index loads on first use. */
  const searchDlg = document.getElementById("searchDialog");
  if (searchDlg && searchDlg.showModal) {
    const input = document.getElementById("searchInput"), box = document.getElementById("searchResults");
    const none = document.getElementById("searchNone"), hint = document.getElementById("searchHint");
    const lang = document.documentElement.lang || "ka";
    let index = null, loading = null;
    const norm = (v) => String(v || "").toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "");
    const txt = (id) => (document.getElementById(id) || {}).textContent || "";
    const esc = (v) => String(v).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    function load() {
      if (!loading) loading = fetch(((document.querySelector('link[href*="assets/css/style.css"]') || {}).href || "/assets/css/style.css").replace(/css\/style\.css.*$/, "search/") + lang + ".json").then((r) => r.json()).then((d) => {
        d.pages.forEach((p) => { p.h = norm(p.t + " " + p.d + " " + p.x + " " + (p.k || "")); p.ht = norm(p.t); });
        d.products.forEach((p) => { p.h = norm(p.n + " " + p.s + " " + p.c + " " + p.k); p.ht = norm(p.n + " " + p.s); });
        index = d; return d;
      }).catch(() => { loading = null; });
      return loading;
    }
    function snippet(p, terms) {
      const x = p.x || p.d; const i = norm(x).indexOf(terms[0]);
      if (i < 0) return p.d;
      const s = Math.max(0, i - 50);
      return (s ? "…" : "") + x.slice(s, s + 150) + "…";
    }
    function run() {
      const q = norm(input.value).trim();
      hint.hidden = !!q; none.hidden = true; box.textContent = "";
      if (!q || !index) return;
      const terms = q.split(/\s+/).filter(Boolean);
      const score = (it) => terms.every((t) => it.h.includes(t)) ? terms.reduce((s, t) => s + (it.ht.includes(t) ? 3 : 1), 0) : 0;
      /* Ties: an item with its own product page first (the B141050 battery before parts that mention B141050), then in-stock priced items. */
      const rank = (p) => { const s = score(p); return s ? s + (p.u && p.u.indexOf("?q=") < 0 ? 2 : 0) + (p.p > 0 ? 0.5 : 0) : 0; };
      /* One result per destination (5 Nov 2026): a product page found as a product (with code, price) is not listed again under pages. */
      const dest = (u) => String(u || "").split("#")[0].replace(/\/$/, "") || "/";
      const seen = new Set();
      const prods = index.products.map((p) => [rank(p), p]).filter((a) => a[0]).sort((a, b) => b[0] - a[0]).map((a) => a[1])
        .filter((p) => { const d = p.u.indexOf("?q=") < 0 ? dest(p.u) : p.u; if (seen.has(d)) return false; seen.add(d); return true; }).slice(0, 8);
      const pages = index.pages.map((p) => [score(p), p]).filter((a) => a[0] && !seen.has(dest(a[1].u))).sort((a, b) => b[0] - a[0]).slice(0, 6).map((a) => a[1]);
      if (!prods.length && !pages.length) { none.hidden = false; return; }
      let out = "";
      if (prods.length) out += '<p class="search-group">' + esc(txt("lbSearchProducts")) + "</p><ul>" + prods.map((p) =>
        '<li><a class="search-product" href="' + esc(p.u) + '"><span class="sp-name">' + esc(p.n) + '</span><span class="sp-meta">' + esc([p.o, p.s, p.c].filter(Boolean).join(" · ")) + '</span><span class="sp-price">' + (p.p > 0 ? "₾" + Number(p.p).toLocaleString("en-US") : esc(p.q || "")) + "</span></a></li>").join("") + "</ul>";
      if (pages.length) out += '<p class="search-group">' + esc(txt("lbSearchPages")) + "</p><ul>" + pages.map((p) =>
        '<li><a class="search-page" href="' + esc(p.u) + '"><span class="sp-name">' + esc(p.t) + '</span><span class="sp-text">' + esc(snippet(p, terms)) + "</span></a></li>").join("") + "</ul>";
      box.innerHTML = out;
    }
    function openSearch() {
      if (searchDlg.open) return;
      closeNav(); searchDlg.showModal(); document.body.classList.add("modal-open");
      input.focus(); input.select(); load().then(run);
    }
    document.getElementById("searchOpen")?.addEventListener("click", openSearch);
    /* phones: the header has no room for the search icon, so the menu starts with a search row (QA 15 Oct 2026) */
    if (nav && !nav.querySelector(".nav-search")) {
      const sb = document.createElement("button"); sb.type = "button"; sb.className = "nav-search";
      sb.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></svg><span></span>';
      sb.querySelector("span").textContent = document.getElementById("searchOpen")?.getAttribute("aria-label") || "ძიება";
      sb.addEventListener("click", openSearch); nav.prepend(sb);
    }
    document.getElementById("searchClose").addEventListener("click", () => searchDlg.close());
    searchDlg.addEventListener("click", (e) => { if (e.target === searchDlg) searchDlg.close(); });
    searchDlg.addEventListener("close", () => document.body.classList.remove("modal-open"));
    input.addEventListener("input", () => (index ? run() : load().then(run)));
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { e.preventDefault(); searchDlg.close(); } });
    /* Arrow keys move between the input and the results (Enter opens the focused result). */
    searchDlg.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowDown" && e.key !== "ArrowUp") return;
      const links = [input].concat(Array.from(box.querySelectorAll("a")));
      if (links.length < 2) return;
      const i = links.indexOf(document.activeElement);
      if (i < 0) return;
      e.preventDefault();
      links[(i + (e.key === "ArrowDown" ? 1 : links.length - 1)) % links.length].focus();
    });
    document.addEventListener("keydown", (e) => {
      const typing = /input|textarea|select/i.test((e.target && e.target.tagName) || "") || (e.target && e.target.isContentEditable);
      if ((e.key === "k" && (e.ctrlKey || e.metaKey)) || (e.key === "/" && !typing)) { e.preventDefault(); openSearch(); }
    });
  }

  /* Native dialog preserves keyboard focus, Escape and assistive technology semantics. */
  const lightbox = document.getElementById("lightbox");
  const photos = Array.from(document.querySelectorAll("[data-lightbox]"));
  let activePhoto = 0;
  function showPhoto(index) {
    activePhoto = (index + photos.length) % photos.length;
    const original = photos[activePhoto].querySelector("img");
    const image = document.getElementById("lightboxImage");
    image.src = photos[activePhoto].href;
    image.alt = original.alt;
    document.getElementById("lightboxCaption").textContent = original.alt;
    document.getElementById("lightboxCounter").textContent = (activePhoto + 1) + " / " + photos.length;
  }
  if (lightbox && typeof lightbox.showModal === "function") {
    photos.forEach((photo, index) => photo.addEventListener("click", (event) => {
      event.preventDefault();
      showPhoto(index);
      lightbox.showModal();
      document.body.classList.add("modal-open");
    }));
    lightbox.querySelector(".lightbox-close").addEventListener("click", () => lightbox.close());
    lightbox.addEventListener("close", () => document.body.classList.remove("modal-open"));
    lightbox.addEventListener("click", (event) => {
      if (event.target !== lightbox) return;
      const bounds = lightbox.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) lightbox.close();
    });
    lightbox.querySelectorAll("[data-gallery-step]").forEach((button) => button.addEventListener("click", () => showPhoto(activePhoto + Number(button.dataset.galleryStep))));
    lightbox.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showPhoto(activePhoto + (event.key === "ArrowLeft" ? -1 : 1));
      }
    });
  }

  const form = document.getElementById("contactForm");
  if (form) {
    const topic = document.getElementById("contactTopic");
    const requestedTopic = new URLSearchParams(location.search).get("topic");
    if (Array.from(topic.options).some((option) => option.value === requestedTopic)) topic.value = requestedTopic;
    function validate(field) {
      let error = "";
      const value = field.value.trim();
      if (!value) error = t("error_required");
      else if (field.type === "tel") {
        const count = value.replace(/\D/g, "").length;
        if (!/^[+()\d\s.\-]+$/.test(value) || count < 9 || count > 15) error = t("error_phone");
      }
      field.setAttribute("aria-invalid", String(Boolean(error)));
      document.getElementById("err-" + field.id).textContent = error;
      return error;
    }
    const fields = [document.getElementById("contactName"), document.getElementById("contactPhone")];
    const emailField = document.getElementById("contactEmail");
    fields.forEach((field) => field.addEventListener("blur", () => validate(field)));
    const loadedAt = Date.now(), status = document.getElementById("formStatus"), sendBtn = form.querySelector('button[type="submit"]');
    const lang = (document.documentElement.lang || "ka").slice(0, 2);
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (sendBtn.disabled) return;
      status.classList.remove("is-error", "is-ok");
      if (emailField) { const ev = emailField.value.trim(); const bad = ev && !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(ev); emailField.setAttribute("aria-invalid", String(Boolean(bad))); document.getElementById("err-contactEmail").textContent = bad ? t("error_email") : ""; if (bad) { status.textContent = t("form_check"); status.classList.add("is-error"); emailField.focus(); return; } }
      const invalid = fields.map((field) => ({ field, error: validate(field) })).find((result) => result.error);
      if (invalid) { status.textContent = t("form_check"); status.classList.add("is-error"); invalid.field.focus(); return; }
      sendBtn.disabled = true; status.textContent = t("form_sending");
      const payload = {
        name: fields[0].value.trim(), phone: fields[1].value.trim(), email: emailField ? emailField.value.trim() : "", topic: topic.value,
        message: document.getElementById("contactMessage").value.trim(), website: document.getElementById("contactWebsite").value,
        elapsed: Date.now() - loadedAt, lang, page: location.pathname
      };
      let outcome = "failed";
      try {
        const res = await fetch("/api/contact", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
        const data = await res.json().catch(() => ({}));
        if (res.ok && data.ok) outcome = "sent";
        else if (res.status === 429) outcome = "busy";
        else if (data.error === "too_fast") outcome = "too_fast";
        else if (res.status === 400 && data.error === "invalid") {
          outcome = "check";
          const map = { name: "contactName", phone: "contactPhone" };
          Object.keys(data.fields || {}).forEach((k) => {
            const el = map[k] && document.getElementById(map[k]); if (!el) return;
            el.setAttribute("aria-invalid", "true"); document.getElementById("err-" + el.id).textContent = t(k === "phone" ? "error_phone" : "error_required");
          });
        }
      } catch (err) { outcome = "failed"; }
      sendBtn.disabled = false;
      if (outcome === "sent") { document.dispatchEvent(new CustomEvent("pdg:track", { detail: { name: "generate_lead", params: { form: "consultation", topic: topic.value || "general" } } })); form.reset(); if (Array.from(topic.options).some((o) => o.value === requestedTopic)) topic.value = requestedTopic; }
      status.textContent = t({ sent: "form_sent", busy: "form_busy", too_fast: "form_too_fast", check: "form_check", failed: "form_failed" }[outcome]);
      status.classList.add(outcome === "sent" ? "is-ok" : "is-error");
    });
  }
})();

/* P150 MAX package pages: thumbnails switch the main picture (the first one shows exactly the package contents). */
(function () {
  "use strict";
  var main = document.getElementById("pkMain");
  if (!main) return;
  document.addEventListener("click", function (e) {
    var b = e.target.closest ? e.target.closest(".pk-thumb") : null;
    if (!b) return;
    main.src = b.getAttribute("data-full");
    main.alt = b.getAttribute("aria-label") || "";
    Array.prototype.forEach.call(document.querySelectorAll(".pk-thumb"), function (x) {
      var on = x === b; x.classList.toggle("is-on", on);
      if (on) x.setAttribute("aria-current", "true"); else x.removeAttribute("aria-current");
    });
  });
})();
/* P150 MAX media (owner, 6 Nov 2026): XAG videos play silently only while on screen; reduced motion keeps the still picture. */
(function () {
  var vids = document.querySelectorAll("video.pm-video");
  if (!vids.length) return;
  var big = window.matchMedia("(min-width: 1000px)").matches;
  vids.forEach(function (v) { if (big && v.dataset.posterLg) v.poster = v.dataset.posterLg; });
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) return;
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) {
      var v = e.target;
      if (e.isIntersecting) { if (v.preload !== "auto") { v.preload = "auto"; } var p = v.play(); if (p && p.catch) p.catch(function () {}); }
      else if (!v.paused) v.pause();
    });
  }, { threshold: 0.35 });
  vids.forEach(function (v) { io.observe(v); });
})();
