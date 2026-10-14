(function () {
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
  document.querySelectorAll("[data-lang]").forEach((link) => {
    const targetLanguage = link.dataset.lang;
    const relativePath = location.pathname.replace(/^\/(en|ru)(?=\/|$)/, "");
    const path = relativePath === "/index.html" || relativePath === "" ? "/" : relativePath;
    const prefix = targetLanguage === "ka" ? "" : "/" + targetLanguage;
    link.href = prefix + path + location.search + location.hash;
    if (targetLanguage === lang) link.setAttribute("aria-current", "page");
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
  }
  const header = document.querySelector(".site-header");
  if (header) {
    const onScroll = () => header.classList.toggle("is-scrolled", window.scrollY > 8);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
  const nav = document.getElementById("site-nav");
  const navToggle = document.getElementById("navToggle");
  function closeNav() {
    nav?.classList.remove("is-open");
    navToggle?.setAttribute("aria-expanded", "false");
  }
  navToggle?.addEventListener("click", () => {
    const open = nav.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(open));
  });
  nav?.addEventListener("click", (event) => { if (event.target.closest("a")) closeNav(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeNav(); });
  /* Products / Services submenus: click or keyboard opens, outside click or Escape closes. */
  const groups = Array.from(document.querySelectorAll(".nav-group-btn"));
  function closeGroups(except) { groups.forEach((b) => { if (b !== except) b.setAttribute("aria-expanded", "false"); }); }
  groups.forEach((b) => b.addEventListener("click", () => {
    const open = b.getAttribute("aria-expanded") !== "true";
    closeGroups(b); b.setAttribute("aria-expanded", String(open));
  }));
  document.addEventListener("click", (event) => { if (!event.target.closest(".nav-group")) closeGroups(); });
  document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeGroups(); });
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
      const prods = index.products.map((p) => [score(p), p]).filter((a) => a[0]).sort((a, b) => b[0] - a[0]).slice(0, 8).map((a) => a[1]);
      const pages = index.pages.map((p) => [score(p), p]).filter((a) => a[0]).sort((a, b) => b[0] - a[0]).slice(0, 6).map((a) => a[1]);
      if (!prods.length && !pages.length) { none.hidden = false; return; }
      let out = "";
      if (prods.length) out += '<p class="search-group">' + esc(txt("lbSearchProducts")) + "</p><ul>" + prods.map((p) =>
        '<li><a class="search-product" href="' + esc(p.u) + '"><span class="sp-name">' + esc(p.n) + '</span><span class="sp-meta">' + (p.o ? esc(p.o) + " · " : "") + esc(p.s) + " · " + esc(p.c) + '</span><span class="sp-price">₾' + Number(p.p).toLocaleString("en-US") + "</span></a></li>").join("") + "</ul>";
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
    document.getElementById("searchClose").addEventListener("click", () => searchDlg.close());
    searchDlg.addEventListener("click", (e) => { if (e.target === searchDlg) searchDlg.close(); });
    searchDlg.addEventListener("close", () => document.body.classList.remove("modal-open"));
    input.addEventListener("input", () => (index ? run() : load().then(run)));
    input.addEventListener("keydown", (e) => { if (e.key === "Escape") { e.preventDefault(); searchDlg.close(); } });
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
    fields.forEach((field) => field.addEventListener("blur", () => validate(field)));
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const invalid = fields.map((field) => ({ field, error: validate(field) })).find((result) => result.error);
      const status = document.getElementById("formStatus");
      if (invalid) { status.textContent = invalid.error; invalid.field.focus(); return; }
      const name = fields[0].value.trim();
      const phone = fields[1].value.trim();
      const message = document.getElementById("contactMessage").value.trim();
      const body = [t("form_name") + ": " + name, t("form_phone") + ": " + phone, t("form_topic") + ": " + topic.options[topic.selectedIndex].text, "", message].join("\n");
      const subject = "Premium Drones Georgia — " + name;
      const mailto = "mailto:info@premium-drones.ge?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      const draftLink = document.createElement("a");
      draftLink.href = mailto;
      draftLink.click();
      status.textContent = t("email_ready");
      /* Keep the form values if no mail application is configured. Never claim delivery. */
    });
  }
})();
