/* DexLab website behaviour. Everything here is progressive: the page is complete without it. */
(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* Hero entrance */
  if (!reduce) root.classList.add("play");
  var motif = $(".motif");
  if (motif) {
    motif.addEventListener("click", function () {
      if (reduce) return;
      root.classList.remove("play");
      void motif.offsetWidth;
      root.classList.add("play");
    });
    if (!reduce && window.matchMedia("(pointer: fine)").matches) {
      var hero = $(".hero"), raf = 0, tx = 0, ty = 0;
      hero.addEventListener("pointermove", function (e) {
        var r = motif.getBoundingClientRect();
        tx = Math.max(-1, Math.min(1, (e.clientX - (r.left + r.width / 2)) / (r.width / 1.2)));
        ty = Math.max(-1, Math.min(1, (e.clientY - (r.top + r.height / 2)) / (r.height / 1.2)));
        if (!raf) raf = requestAnimationFrame(function () {
          motif.style.setProperty("--px", tx.toFixed(3));
          motif.style.setProperty("--py", ty.toFixed(3));
          raf = 0;
        });
      });
      hero.addEventListener("pointerleave", function () {
        motif.style.setProperty("--px", 0);
        motif.style.setProperty("--py", 0);
      });
    }
  }

  /* Sticky header border + scroll progress */
  var head = $(".site-head"), bar = $(".progress span"), ticking = false;
  function onScroll() {
    var y = window.scrollY || 0;
    if (head) head.classList.toggle("scrolled", y > 8);
    if (bar) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = "scaleX(" + (max > 0 ? Math.min(1, y / max) : 0).toFixed(4) + ")";
    }
    ticking = false;
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* Section reveal, once, 20% in view */
  var revealables = $$(".rv");
  var groups = $$(".ba");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add(en.target.classList.contains("ba") ? "aligned" : "in"); io.unobserve(en.target); }
      });
    }, { threshold: 0.2, rootMargin: "0px 0px -5% 0px" });
    revealables.forEach(function (el) { io.observe(el); });
    groups.forEach(function (el) { io.observe(el); });
    /* safety net: never leave content hidden */
    setTimeout(function () { revealables.forEach(function (el) { el.classList.add("in"); }); }, 6000);
  } else {
    revealables.forEach(function (el) { el.classList.add("in"); });
    groups.forEach(function (el) { el.classList.add("aligned"); });
  }

  /* Active nav link */
  var links = $$(".nav a");
  if ("IntersectionObserver" in window && links.length) {
    var map = {};
    links.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        var a = map[en.target.id];
        if (a && en.isIntersecting) { links.forEach(function (l) { l.removeAttribute("aria-current"); }); a.setAttribute("aria-current", "true"); }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) spy.observe(s); });
  }

  /* Language dropdown */
  var langBtn = $(".lang-btn"), langList = $(".lang-list");
  function closeLang(focus) { if (!langBtn) return; langBtn.setAttribute("aria-expanded", "false"); langList.classList.remove("open"); if (focus) langBtn.focus(); }
  if (langBtn) {
    langBtn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = langBtn.getAttribute("aria-expanded") !== "true";
      langBtn.setAttribute("aria-expanded", String(open));
      langList.classList.toggle("open", open);
      if (open) { var cur = $("a[aria-current=true]", langList) || $("a", langList); cur.focus(); }
    });
    langList.addEventListener("keydown", function (e) {
      var items = $$("a", langList), i = items.indexOf(document.activeElement);
      if (e.key === "ArrowDown") { e.preventDefault(); items[(i + 1) % items.length].focus(); }
      if (e.key === "ArrowUp") { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); }
      if (e.key === "Escape") closeLang(true);
    });
    document.addEventListener("click", function (e) { if (!langList.contains(e.target)) closeLang(false); });
  }
  $$("a[data-lang]").forEach(function (a) {
    a.addEventListener("click", function () { try { localStorage.setItem("dexlab-lang", a.getAttribute("data-lang")); } catch (x) {} });
  });

  /* Mobile menu */
  var menuBtn = $(".menu-btn"), menu = $("#mobile-menu");
  function setMenu(open, focusBack) {
    menuBtn.setAttribute("aria-expanded", String(open));
    menuBtn.setAttribute("aria-label", open ? menuBtn.dataset.close : menuBtn.dataset.open);
    menu.classList.toggle("open", open);
    if (open) { var first = $("a", menu); if (first) first.focus(); }
    else if (focusBack) menuBtn.focus();
  }
  if (menuBtn && menu) {
    menuBtn.addEventListener("click", function () { setMenu(menuBtn.getAttribute("aria-expanded") !== "true"); });
    menu.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false, true); });
    $$("a.m-link, a.btn-pri", menu).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    window.addEventListener("resize", function () { if (window.innerWidth >= 1100 && menu.classList.contains("open")) setMenu(false); });
  }
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closeLang(false); });

  /* Clinic screen: tap a status to move it forward */
  $$(".stbtn").forEach(function (b) {
    b.addEventListener("click", function () {
      var labels = JSON.parse(b.dataset.labels), s = (parseInt(b.dataset.s, 10) + 1) % labels.length;
      b.dataset.s = s;
      b.className = "stbtn s" + s;
      b.textContent = labels[s];
      if (!reduce) { void b.offsetWidth; b.classList.add("pop"); }
    });
  });

  /* Contact form: compose an email (no server needed on GitHub Pages) */
  var form = $("form.cform");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = $("#f-name").value.trim(), reach = $("#f-reach").value.trim(), msg = $("#f-msg").value.trim();
      var typeEl = $("input[name=type]:checked", form), type = typeEl ? typeEl.parentNode.textContent.trim() : "";
      var ok = $(".msg.ok", form), err = $(".msg.err", form);
      $("#f-name").setAttribute("aria-invalid", String(!name));
      $("#f-msg").setAttribute("aria-invalid", String(!msg));
      if (!name || !msg) { err.hidden = false; ok.hidden = true; (name ? $("#f-msg") : $("#f-name")).focus(); return; }
      err.hidden = true;
      var subject = form.dataset.subject + (type ? " · " + type : "") + " · " + name;
      var body = msg + "\n\n— " + name + (reach ? "\n" + reach : "") + (type ? "\n" + type : "");
      window.location.href = "mailto:" + form.dataset.to + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(body);
      ok.hidden = false;
    });
  }

  /* Year */
  $$("[data-year]").forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
