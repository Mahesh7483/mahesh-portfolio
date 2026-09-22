/* Mahesh R — portfolio: motion switch, mobile nav, active section, reveal,
   and the pointer-driven light (aurora parallax, glass specular + tilt).
   Everything here is progressive enhancement; the page reads fine without it. */

(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  /* ---------- motion switch ----------
     data-motion is set before first paint by the inline script in <head>.
     It defaults to "on"; the control below turns it off and remembers that. */

  var MOTION_KEY = "mr-motion";
  var motionToggle = document.querySelector(".motion-toggle");

  function motionOn() {
    return root.dataset.motion !== "off";
  }

  function syncToggle() {
    if (!motionToggle) return;
    var on = motionOn();
    motionToggle.setAttribute("aria-pressed", String(on));
    motionToggle.setAttribute("aria-label", on ? "Turn motion off" : "Turn motion on");
  }

  function setMotion(on) {
    root.dataset.motion = on ? "on" : "off";
    try { localStorage.setItem(MOTION_KEY, on ? "on" : "off"); } catch (e) { /* private mode */ }
    syncToggle();
    document.dispatchEvent(new CustomEvent("motionchange", { detail: { on: on } }));
  }

  syncToggle();
  if (motionToggle) {
    motionToggle.addEventListener("click", function () { setMotion(!motionOn()); });
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

  function revealAll() {
    reveals.forEach(function (el) { el.classList.add("in"); });
  }

  if (motionOn() && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    reveals.forEach(function (el) { io.observe(el); });
  } else {
    revealAll();
  }

  // turning motion off mid-scroll must not leave anything hidden
  document.addEventListener("motionchange", function (e) {
    if (!e.detail.on) revealAll();
  });

  /* ---------- pointer-driven light ----------
     Fine pointers only. One requestAnimationFrame per pointer burst, writing
     CSS variables; the compositor does the rest. */

  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  if (finePointer) {
    var aurora = document.querySelector(".aurora");
    var glassEls = Array.prototype.slice.call(document.querySelectorAll(".glass"));
    var TILT_MAX = 2.5;      // degrees
    var PARALLAX_MAX = 30;   // px at the viewport edge
    var pending = false;
    var px = 0, py = 0;
    var hovered = null, hx = 0, hy = 0;

    function noTilt(el) {
      return el.classList.contains("card-featured") || el.classList.contains("facts-strip");
    }

    function clearLight() {
      if (aurora) {
        aurora.style.removeProperty("--px");
        aurora.style.removeProperty("--py");
      }
      root.style.removeProperty("--hx");
      root.style.removeProperty("--hy");
      glassEls.forEach(function (el) {
        el.style.removeProperty("--rx");
        el.style.removeProperty("--ry");
      });
    }

    function flush() {
      pending = false;
      if (!motionOn()) return;

      if (aurora) {
        aurora.style.setProperty("--px", px.toFixed(1) + "px");
        aurora.style.setProperty("--py", py.toFixed(1) + "px");
      }
      // normalised pointer position (-1..1) drives the 3-D scene tilt and layer parallax
      root.style.setProperty("--hx", (px / PARALLAX_MAX).toFixed(3));
      root.style.setProperty("--hy", (py / PARALLAX_MAX).toFixed(3));

      if (hovered) {
        var r = hovered.getBoundingClientRect();
        var nx = (hx - r.left) / r.width;   // 0..1 across the surface
        var ny = (hy - r.top) / r.height;
        hovered.style.setProperty("--mx", (nx * 100).toFixed(1) + "%");
        hovered.style.setProperty("--my", (ny * 100).toFixed(1) + "%");
        if (!noTilt(hovered)) {
          hovered.style.setProperty("--ry", ((nx - 0.5) * 2 * TILT_MAX).toFixed(2) + "deg");
          hovered.style.setProperty("--rx", ((0.5 - ny) * 2 * TILT_MAX).toFixed(2) + "deg");
        }
      }
    }

    function schedule() {
      if (!pending) { pending = true; requestAnimationFrame(flush); }
    }

    document.addEventListener("pointermove", function (e) {
      px = ((e.clientX / window.innerWidth) - 0.5) * 2 * PARALLAX_MAX;
      py = ((e.clientY / window.innerHeight) - 0.5) * 2 * PARALLAX_MAX;
      hx = e.clientX; hy = e.clientY;
      schedule();
    }, { passive: true });

    // ease everything back to rest when the pointer leaves the window
    document.addEventListener("pointerleave", function () {
      px = 0; py = 0; hovered = null;
      schedule();
    });

    glassEls.forEach(function (el) {
      el.addEventListener("pointerenter", function () { hovered = el; schedule(); });
      el.addEventListener("pointerleave", function () {
        if (hovered === el) hovered = null;
        el.style.removeProperty("--rx");
        el.style.removeProperty("--ry");
      });
    });

    document.addEventListener("motionchange", function (e) {
      if (!e.detail.on) clearLight();
    });
  }
})();
