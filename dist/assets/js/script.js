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
  setTheme(storage.get("pdge-theme"));
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
  const desktop = window.matchMedia("(min-width: 901px)");
  desktop.addEventListener?.("change", (event) => { if (event.matches) closeNav(); });

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
  const calc = document.getElementById("calcForm");
  if (calc) {
    const area = document.getElementById("calcArea");
    const rate = document.getElementById("calcRate");
    const throughput = document.getElementById("calcThroughput");
    const number = (input) => {
      const value = Number(input.value);
      return input.value !== "" && Number.isFinite(value) && value > 0 && input.validity.valid ? value : null;
    };
    const formatter = new Intl.NumberFormat(lang === "ka" ? "ka-GE" : lang === "ru" ? "ru-RU" : "en-GB", { maximumFractionDigits: 2 });
    function calculate() {
      const a = number(area), r = number(rate), h = number(throughput);
      document.getElementById("calcVolume").textContent = a && r ? formatter.format(a * r) + " " + t("unit_liter") : "—";
      document.getElementById("calcTime").textContent = a && h ? formatter.format(a / h) + " " + t("unit_hour") : "—";
    }
    calc.addEventListener("input", calculate);
    calc.addEventListener("change", calculate);
    calc.addEventListener("submit", (event) => event.preventDefault());
    calculate();
  }
})();
