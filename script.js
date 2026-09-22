/* Mahesh R — portfolio: theme toggle, mobile nav, active section, reveal.
   Everything here is progressive enhancement; the page reads fine without it. */

(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  /* ---------- theme ---------- */

  var THEME_KEY = "mr-theme";
  var toggle = document.querySelector(".theme-toggle");
  var mql = window.matchMedia("(prefers-color-scheme: dark)");

  function storedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }

  function currentTheme() {
    var explicit = root.getAttribute("data-theme");
    if (explicit) return explicit;
    return mql.matches ? "dark" : "light";
  }

  function applyTheme(theme, persist) {
    if (theme) root.setAttribute("data-theme", theme);
    else root.removeAttribute("data-theme");
    if (persist) {
      try {
        if (theme) localStorage.setItem(THEME_KEY, theme);
        else localStorage.removeItem(THEME_KEY);
      } catch (e) { /* storage unavailable: theme still applies for this view */ }
    }
    if (toggle) {
      var next = currentTheme() === "dark" ? "light" : "dark";
      toggle.setAttribute("aria-label", "Switch to " + next + " theme");
    }
  }

  applyTheme(storedTheme(), false);

  if (toggle) {
    toggle.addEventListener("click", function () {
      applyTheme(currentTheme() === "dark" ? "light" : "dark", true);
    });
  }

  // Follow the OS again if the user never chose explicitly.
  if (mql.addEventListener) {
    mql.addEventListener("change", function () {
      if (!storedTheme()) applyTheme(null, false);
    });
  }

  /* ---------- mobile nav ---------- */

  var header = document.querySelector(".site-header");
  var navToggle = document.querySelector(".nav-toggle");
  var navLinks = document.querySelectorAll(".nav-links a");

  function setNav(open) {
    if (!header || !navToggle) return;
    header.classList.toggle("nav-open", open);
    navToggle.setAttribute("aria-expanded", String(open));
    navToggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
  }

  if (navToggle) {
    navToggle.addEventListener("click", function () {
      setNav(!header.classList.contains("nav-open"));
    });
    navLinks.forEach(function (a) { a.addEventListener("click", function () { setNav(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setNav(false); });
    document.addEventListener("click", function (e) {
      if (header.classList.contains("nav-open") && !header.contains(e.target)) setNav(false);
    });
  }

  /* ---------- active section in nav ---------- */

  var sections = Array.prototype.slice.call(document.querySelectorAll("main section[id]"));
  var linkFor = {};
  navLinks.forEach(function (a) {
    var id = (a.getAttribute("href") || "").replace("#", "");
    if (id) linkFor[id] = a;
  });

  function setActive(id) {
    navLinks.forEach(function (a) { a.classList.remove("is-active"); });
    if (id && linkFor[id]) linkFor[id].classList.add("is-active");
  }

  if ("IntersectionObserver" in window && sections.length) {
    var visible = {};
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting ? en.intersectionRatio : 0; });
      var best = null, bestRatio = 0;
      sections.forEach(function (s) {
        if ((visible[s.id] || 0) > bestRatio) { best = s.id; bestRatio = visible[s.id]; }
      });
      setActive(best);
    }, { rootMargin: "-40% 0px -50% 0px", threshold: [0, .1, .25, .5, .75, 1] });
    sections.forEach(function (s) { spy.observe(s); });
  }

  /* ---------- reveal on scroll ---------- */

  var reveals = document.querySelectorAll(".reveal");
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (!reduce && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }
})();
